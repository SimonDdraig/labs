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
        "bucket": "event" if "BUCKET_NAME" in event else "environment",
        "filekey": "event" if "FILE_KEY" in event else "environment",
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

    return row.get("line_item_operation", "").lower() == "gp3"


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


def create_response(bucket_name, file_name, parameter_source, gp3_rows, gp3_count):
    """
    Create the formatted response object.

    Args:
        bucket_name (str): Name of the S3 bucket
        file_name (str): Name of the processed file
        parameter_source (dict): Source of parameters
        gp3_rows (list): List of matching rows
        gp3_count (int): Total count of matches

    Returns:
        dict: Formatted response with status code and body
    """

    return {
        "statusCode": 200,
        "body": {
            "bucket": bucket_name,
            "filekey": file_name,
            "parameter_source": parameter_source,
            "total_gp3_operations": gp3_count,
            "message": f"Found {gp3_count} rows with gp3 operations",
            "matched_rows": gp3_rows[:10],  # Limiting to first 10 matches
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

        # Process the CSV content
        gp3_rows, gp3_count = process_csv_content(csv_file)

        # Create and return response
        return create_response(
            bucket_name, file_name, parameter_source, gp3_rows, gp3_count
        )

    except s3_client.exceptions.NoSuchKey:
        return {
            "statusCode": 404,
            "body": f"File {file_name} not found in bucket {bucket_name}",
        }
    except s3_client.exceptions.NoSuchBucket:
        return {"statusCode": 404, "body": f"Bucket {bucket_name} does not exist"}
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": f"Error processing file: {str(e)}"}
