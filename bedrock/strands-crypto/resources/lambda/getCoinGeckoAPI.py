import json
import urllib3
import os

def lambda_handler(event, context):
    """
    Lambda function to exchange access token with Salesforce REST API
    """
    
    # Salesforce token endpoint
    token_url = os.environ.get('SALESFORCE_TOKEN_URL', 'https://login.salesforce.com/services/oauth2/token')
    
    # Required parameters from environment variables
    client_id = os.environ['SALESFORCE_CLIENT_ID']
    client_secret = os.environ['SALESFORCE_CLIENT_SECRET']
    username = os.environ['SALESFORCE_USERNAME']
    password = os.environ['SALESFORCE_PASSWORD']
    
    # Prepare request data
    data = {
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password
    }
    
    # Make HTTP request
    http = urllib3.PoolManager()
    encoded_data = urllib3.request.urlencode(data)
    
    try:
        response = http.request(
            'POST',
            token_url,
            body=encoded_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        response_data = json.loads(response.data.decode('utf-8'))
        
        if response.status == 200:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'access_token': response_data['access_token'],
                    'instance_url': response_data['instance_url'],
                    'token_type': response_data.get('token_type', 'Bearer')
                })
            }
        else:
            return {
                'statusCode': response.status,
                'body': json.dumps({'error': response_data})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }