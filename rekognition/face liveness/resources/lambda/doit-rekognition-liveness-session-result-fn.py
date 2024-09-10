import json
import boto3
from botocore.exceptions import ClientError
import logging

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Initialize the Rekognition client
    rekognition = boto3.client('rekognition')
    
    # Extract the sessionId from the event body
    query_params = event.get('queryStringParameters', {})
    if query_params is None:
        query_params = {}
    
    session_id = query_params.get('SessionId')
    
    if not session_id:
        return {
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin":"*",
            },
            'statusCode': 400,
            'body': json.dumps('Invalid request: SessionId is required')
        }
    logger.info(f"Getting resuts for SessionId: {session_id}")

    try:
        # Call the get_face_liveness_session_results operation
        response = rekognition.get_face_liveness_session_results(SessionId=session_id)
        
        # Extract relevant information from the response
        result = {
            'Confidence': response.get('Confidence'),
            'Status': response.get('Status')
        }
        
        logger.info(f"Resuts for SessionId: {result}")

        return {
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin":"*",
            },
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except ClientError as e:
        error_message = e.response['Error']['Message']
        return {
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin":"*",
            },
            'statusCode': 500,
            'body': json.dumps(f'Error: {error_message}')
        }
