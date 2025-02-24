import boto3
import json
import csv
import io
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_parameters(event):
    """Extract parameters from event or environment variables.
    
    Args:
        event (dict): Lambda event object containing potential parameters
        
    Returns:
        tuple: (bucket_name, file_name, parameter_source)
    """

    bucket_name = event.get("BUCKET_NAME") or os.environ.get("BUCKET_NAME")
    file_name = event.get("FILE_KEY") or os.environ.get("FILE_KEY")

    parameter_source = {
        "bucket": "event" if "BUCKET_NAME" in event else "lambda environment vars",
        "filekey": "event" if "FILE_KEY" in event else "lambda environment vars",
    }

    return bucket_name, file_name, parameter_source


def validate_parameters(bucket_name, file_name):
    """
    Validate that required parameters are present and not empty.

    Args:
        bucket_name (str): Name of the S3 bucket
        file_name (str): Name of the file to process

    Returns:
        dict or None: Error response dictionary if validation fails, None if successful
    """
    
    if not bucket_name or not file_name:
        return {
            "statusCode": 400,
            "body": "Missing required parameters: bucket and filekey. "
            "Please provide them either in the event or as environment variables "
            "BUCKET_NAME and FILE_KEY",
        }
    return None


def process_csv_row(row):
    """
    Process a single CSV row and determine if it matches criteria.

    Args:
        row (dict): Dictionary containing CSV row data with 'line_item_operation' key

    Returns:
        bool: True if row contains 'gp3' operation, False otherwise
    """

    operation = row.get("line_item_operation", "").lower()
    return "gp3" in operation


def read_csv_from_s3(s3_client, bucket_name, file_name):
    """
    Read and process CSV file from S3 bucket.

    Args:
        s3_client (boto3.client): Initialized boto3 S3 client
        bucket_name (str): Name of the S3 bucket
        file_name (str): Path to the file in the bucket

    Returns:
        io.StringIO: File content as a string buffer

    Raises:
        botocore.exceptions.ClientError: If file or bucket not found
    """

    response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
    file_content = response["Body"].read().decode("utf-8")
    return io.StringIO(file_content)


def process_csv_content(csv_file):
    """
    Process CSV content and collect matching rows.

    Args:
        csv_file (io.StringIO): CSV file content as string buffer

    Returns:
        tuple: Contains:
            - list: Matching rows from CSV
            - int: Count of matching rows
    """

    csv_reader = csv.DictReader(csv_file)
    gp3_rows = []
    gp3_count = 0

    for row in csv_reader:
        if process_csv_row(row):
            gp3_count += 1
            gp3_rows.append(row)

    return gp3_rows, gp3_count


def create_response(s3_client, bucket_name, file_name, parameter_source, md_content):
    """
    Create the formatted response object.

    Args:
        bucket_name (str): Name of the S3 bucket
        file_name (str): Name of the processed file
        parameter_source (dict): Source of parameters
        md_content (str): Markdown content to write as a file back to the S3 bucket

    Returns:
        dict: Formatted response with status code and body
    """

    # Write markdown content to a file in the S3 bucket
    # Convert string content to bytes
    encoded_content = md_content.encode('utf-8')
    
    # Upload the file to S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=encoded_content,
        ContentType='text/plain'
    )
    
    logger.info(
        f"Successfully wrote markdown file '{file_name}' to bucket '{bucket_name}'"
    )

    return {
        "statusCode": 200,
        "body": {
            "bucket": bucket_name,
            "filekey": file_name,
            "parameter_source": parameter_source
        },
    }


def lambda_handler(event, context):
    """
    Main Lambda handler function that processes S3 CSV files.

    Args:
        event (dict): Lambda event containing 'bucket' and 'filename' parameters
        context (LambdaContext): Lambda context object

    Returns:
        dict: Response containing processing results or error message

    Raises:
        Various exceptions handled with appropriate error responses
    """

    try:
        # Get and validate parameters
        bucket_name, file_name, parameter_source = get_parameters(event)
        validation_error = validate_parameters(bucket_name, file_name)
        if validation_error:
            return validation_error

        # Log parameter sources
        logger.info(f"Using bucket: {bucket_name} (from {parameter_source['bucket']})")
        logger.info(f"Using file: {file_name} (from {parameter_source['filekey']})")

        # Initialize S3 client and read file
        s3_client = boto3.client("s3")
        csv_file = read_csv_from_s3(s3_client, bucket_name, file_name)

    except s3_client.exceptions.NoSuchKey:
        return {
            "statusCode": 404,
            "body": f"Data export file {file_name} not found in bucket {bucket_name}",
        }
    except s3_client.exceptions.NoSuchBucket:
        return {"statusCode": 404, "body": f"Bucket {bucket_name} does not exist"}
    except Exception as e:
        logger.error(f"Error processing data export source file: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": f"Error processing data export source file: {str(e)}"}

    try:
        # Process the CSV content
        md_content = process_csv_content(csv_file)

        # Create and return response
        return create_response(
            s3_client, bucket_name, file_name, parameter_source, md_content
        )
    except s3_client.exceptions.NoSuchBucket:
        return {"statusCode": 404, "body": f"Bucket {bucket_name} does not exist"}
    except Exception as e:
        logger.error(f"Error processing markdown target file: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": f"Error processing markdown target file: {str(e)}"}