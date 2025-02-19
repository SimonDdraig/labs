import boto3
import csv
import io

#the data source for this lambda must be a csv file
#if parquet is preferred, rewrite this lambda to use pandas instead of the cdv library
#but for csv, the csv library is much more efficient as it streams rather than holds in memory
#and is a simplistic module to use, and very small in library size vs pandas
def lambda_handler(event, context):
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    # S3 bucket and file details
    bucket_name = 'XXXXXXXXXXXXXXXXXXX'
    file_key = 'monthly-00001.csv'
    
    try:
        # Get the object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        
        # Read the CSV content
        file_content = response['Body'].read().decode('utf-8')
        csv_file = io.StringIO(file_content)
        
        # Create CSV reader
        csv_reader = csv.DictReader(csv_file)
        
        # Initialize variables
        gp3_rows = []
        gp3_count = 0
        
        # Process each row
        for row in csv_reader:
            if row.get('line_item_operation', '').lower() == 'gp3':
                gp3_count += 1
                gp3_rows.append(row)
        
        # Prepare the response
        response = {
            'statusCode': 200,
            'body': {
                'total_gp3_operations': gp3_count,
                'message': f'Found {gp3_count} rows with gp3 operations',
                'matched_rows': gp3_rows[:10]  # Limiting to first 10 matches in response
            }
        }
        
    except s3_client.exceptions.NoSuchKey:
        response = {
            'statusCode': 404,
            'body': f'File {file_key} not found in bucket {bucket_name}'
        }
    except Exception as e:
        response = {
            'statusCode': 500,
            'body': f'Error processing file: {str(e)}'
        }
    
    return response
