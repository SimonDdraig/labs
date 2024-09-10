import json
import boto3
import logging
import os

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    rekognition = boto3.client('rekognition')
    
    try:
        response = rekognition.create_face_liveness_session(
            Settings={
                'OutputConfig': {
                    'S3Bucket': os.environ['S3'],
                    'S3KeyPrefix': 'images'
                },
                'AuditImagesLimit': 4  # Optional: Set the number of audit images to store (0-4)
            }
        )
        session_id = response['SessionId']
        
        # Log the session ID
        logger.info(f"Face liveness session created with SessionId: {session_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Enable CORS for all origins
            },
            'body': json.dumps({'sessionId': session_id})
        }
    except Exception as e:
        # Log the error
        logger.error(f"Error creating face liveness session: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Enable CORS for all origins
            },
            'body': json.dumps({'error': str(e)})
        }
