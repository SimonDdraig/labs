import boto3
import json
import csv
import io
import os
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# using STREAM, the data export CSV file is retrieved from S3, and passed back as a stream, it is then fetched and used, and fetched again for each 
# array item in recommendations.json - use if the file is > available memory - can be slower though due to S3 fetch
# using MEMORY, the data export CSV file is retrieved from S3, and passed back as a stream, however it is then stored as a list in memory - faster 
# than above to iterate through as it does not have to repeatedly fetch from S3
csvFile='STREAM'
#csvFile='MEMORY'

def get_parameters(event):
    """Extract parameters from event or environment variables.
    
    Args:
        event (dict): Lambda event object containing potential parameters
        
    Returns:
        tuple: (bucket_name, file_name, parameter_source)
    """

    bucket_name = event.get("BUCKET_NAME") or os.environ.get("BUCKET_NAME")
    file_name = event.get("FILE_KEY") or os.environ.get("FILE_KEY")
    github_raw_url = event.get("GITHUB") or os.environ.get("GITHUB")

    parameter_source = {
        "bucket": "event" if "BUCKET_NAME" in event else "lambda environment vars",
        "filekey": "event" if "FILE_KEY" in event else "lambda environment vars",
        "github": "event" if "GITHUB" in event else "lambda environment vars",
    }

    return bucket_name, file_name, github_raw_url, parameter_source


def validate_parameters(bucket_name, file_name, github_raw_url):
    """
    Validate that required parameters are present and not empty.

    Args:
        bucket_name (str): Name of the S3 bucket
        file_name (str): Name of the file to process

    Returns:
        dict or None: Error response dictionary if validation fails, None if successful
    """
    
    if not bucket_name or not file_name or not github_raw_url:
        return {
            "statusCode": 400,
            "body": "Missing required parameters: bucket, filekey and github. "
            "Please provide them either in the event or as environment variables "
            "BUCKET_NAME, FILE_KEY and GITHUB",
        }
    return None


def read_github_json(github_raw_url):
    """
    Read and parse JSON file from GitHub raw content.
    
    Args:
        github_raw_url (str): Raw content URL for the GitHub JSON file
    
    Returns:
        dict: Parsed JSON data if successful, None if failed
    """

    logger.info("Will read JSON file from GitHub: {}".format(github_raw_url))

    try:
        response = requests.get(github_raw_url)
        response.raise_for_status()

        data = response.json()
        logger.info("Will use JSON recommendations: {}".format(data))
        return data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching JSON from GitHub: {str(e)}", exc_info=True)
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON content: {str(e)}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return None


def read_github_md(github_raw_url):
    """
    Read markdown from GitHub raw content.
    
    Args:
        github_raw_url (str): Raw content URL for the GitHub file
    
    Returns:
        dict: markdown if successful, None if failed
    """

    logger.info('Processing recommendation for {}'.format(github_raw_url))
    try:
        response = requests.get(github_raw_url)
        response.raise_for_status()
        
        data = response.text
        logger.info("Successfully read md file from GitHub")
        return data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching markdown from GitHub: {str(e)}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return None


def process_csv_row(row, keywords, columns):
    """
    Process a single CSV row and determine if it matches criteria.
    We keywords and columns are lists, so it checks if the keyword is present in its corresponding column

    Args:
        row (dict): Dictionary containing CSV row data with 'line_item_operation' key
        keywords (list): Keywords to search for
        columns (list): Columns to search in 

    Returns:
        bool: True if row contains keyword(2) in relevant column(s), False otherwise
    """

    # Check if each keyword appears only in its corresponding column
    for i in range(len(columns)):  
        column = columns[i]
        keyword = keywords[i].lower()
        column_value = row.get(column, "").lower()
        
        if keyword not in column_value:  
            return False
        logger.info('FOUND: keyword:{} in column:{} containing:{}'.format(keyword, column, column_value))

    return True


def read_csv_from_s3(s3_client, bucket_name, file_name):
    """
    Read and process data export CUR2.0 CSV file from S3 bucket
    Returns a list held in memory so we don't have to fetch from S3 multiple times each time we iterate through it
    If the file is > available memory, then return as a stream instead and fetch it for each iteration - see hardcoded var above to switch
    If files are > very large, refactor code to replace csv with pandas

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


def process_csv_content(csv_file, github_raw_url):
    """
    Process CSV content and collect matching rows.

    Args:
        csv_file (io.StringIO): CSV file content as string buffer

    Returns:
        tuple: Contains:
            - list: Matching rows from CSV
            - int: Count of matching rows
    """

    # get the json that contains the collection of markdown recommendations we should consider
    recommendationsJson = read_github_json('{}recommendations.json'.format(github_raw_url))
    markdownContent = []
    foundEntry = False

    # iterate through the collection to process the requirements for each markdown recommendation
    files = recommendationsJson.get('Files', [])

    # how are we handling the CSV file
    if csvFile=='MEMORY':
        csv_reader = list(csv.DictReader(csv_file))

    # iterate through recommendations.json
    for file_entry in files:
        file_name = file_entry.get('File', '')
        parent = file_entry.get('Parent', '')
        service = file_entry.get('Service', '')
        columns = file_entry.get('Columns', '').split('|')
        keywords = file_entry.get('Keywords', '').split('|')
        logger.info('Looking for keywords: {} in columns: {}'.format(keywords, columns))

        if keywords[0] == 'GENERAL':
            # just grab the markdown as we dont need to do any searching
            markdown = read_github_md('{}{}.md'.format(github_raw_url,file_name))
            markdownContent.append(markdown)
        else:
            # how are we handling the CSV file - if from an S3 stream we need to refetch it for each iteration through recomendations
            if csvFile=='STREAM':
                csv_file.seek(0)
                csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                if process_csv_row(row, keywords, columns):
                    # grab the markdown appropriate for the keyword just found
                    markdown = read_github_md('{}{}.md'.format(github_raw_url,file_name))
                    markdownContent.append(markdown)
                    # we've found one, so lets jump out otherwise we might repeat advice
                    foundEntry=True
                    break

        # lets check if we either continue processing the file, or abandon it if the service is not present in the csv_file but its mandatory
        if file_name == 'mandatory-header' and not foundEntry:
            logger.info('Service {} not found in CSV file, skipping this recommendations file'.format(service))
            break

    return markdownContent


def create_response(s3_client, bucket_name, file_name, parameter_source, md_content, md_file_name):
    """
    Create the formatted response object.

    Args:
        bucket_name (str): Name of the S3 bucket
        file_name (str): Name of the processed file
        parameter_source (dict): Source of parameters
        md_content (str): Markdown content to write as a file back to the S3 bucket
        md_file_name (str): Name of the markdown file

    Returns:
        dict: Formatted response with status code and body
    """

    # Write markdown content to a file in the S3 bucket
    # Convert string content to bytes
    md_content_str = "\n\n".join(md_content)  # Join list into a string
    encoded_content = md_content_str.encode('utf-8')  # Encode as UTF-8

    # Upload the file to S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key=md_file_name,
        Body=encoded_content,
        ContentType='text/markdown'
    )
    
    logger.info(
        f"Successfully wrote markdown file '{md_file_name}' to bucket '{bucket_name}'"
    )

    return {
        "statusCode": 200,
        "body": {
            "bucket": bucket_name,
            "filekey": md_file_name,
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
        bucket_name, file_name, github_raw_url, parameter_source = get_parameters(event)
        validation_error = validate_parameters(bucket_name, file_name, github_raw_url)
        if validation_error:
            return validation_error

        # Log parameter sources
        logger.info(f"Using bucket: {bucket_name} (from {parameter_source['bucket']})")
        logger.info(f"Using file: {file_name} (from {parameter_source['filekey']})")
        logger.info(f"Using github: {github_raw_url} (from {parameter_source['github']})")

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
        md_content = process_csv_content(csv_file, github_raw_url)

        # Create and return response
        md_file_name = file_name.replace(".csv", ".md")
        return create_response(
            s3_client, bucket_name, file_name, parameter_source, md_content, md_file_name
        )
    except s3_client.exceptions.NoSuchBucket:
        return {"statusCode": 404, "body": f"Bucket {bucket_name} does not exist"}
    except Exception as e:
        logger.error(f"Error processing markdown target file: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": f"Error processing markdown target file: {str(e)}"}