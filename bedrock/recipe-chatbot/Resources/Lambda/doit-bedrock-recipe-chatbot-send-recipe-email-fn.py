# Simon Davies @ DoiT International
# doit-bedrock-recipe-chatbot-send-recipe-email-fn.py
# doit-bedrock-recipe-chatbot-send-recipe-email-fn
# sends an email from details passed in via the bedrock agent event
# note for the workshop, the ses account is in the aws sandbox with very limited functionality

# aws api libraries
import boto3
import json

# other
import os

# logging libraries
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

####################################################################################
# controlling function
####################################################################################
def lambda_handler(event, context):
    logger.info('doit-bedrock-recipe-chatbot-send-recipe-email-fn lambda has been called')
    logger.info('event passed in: {}'.format(event))

    # send the email
    recipientEmail, emailContent = getProperties(event)
    sendEmail(recipientEmail, emailContent)

    # build the response to send back to the agent
    response = buildResponse(event)

    # return
    return response

####################################################################################
# get all the meta data we need
####################################################################################
def getProperties(event):
    properties = event.get("requestBody", {}).get("content", {}).get("application/json", {}).get("properties", [])

    # prepare vars
    subjectP = 'NOT FOUND subjectP'
    bodyIngredientsP = 'NOT FOUND bodyIngredientsP'
    bodyInstructionsP = 'NOT FOUND bodyInstructionsP'
    salutationP = 'NOT FOUND salutationP'

    for prop in properties:
        if prop.get("name") == "firstname":
            salutationP = prop.get("value")
            break
    for prop in properties:
        if prop.get("name") == "ingredients":
            bodyIngredientsP = prop.get("value")
            break
    for prop in properties:
        if prop.get("name") == "instructions":
            bodyInstructionsP = prop.get("value")
            break
    for prop in properties:
        if prop.get("name") == "emailAddress":
            recipientEmail = prop.get("value")
            break

    subjectP = "Recipe from {}".format(event['agent']['name'])
    if bodyIngredientsP == 'NOT FOUND bodyIngredientsP': bodyIngredientsP = ""
    if bodyInstructionsP == 'NOT FOUND bodyInstructionsP': bodyInstructionsP = ""

    logger.info('Will send to email: {}'.format(recipientEmail))

    class emailContent:
        subject = subjectP
        bodyIngredients = bodyIngredientsP
        bodyInstructions = bodyInstructionsP
        salutation = 'Hi {},'.format(salutationP)
    logger.info('Emailing subject: {} with body: {}\n{}'.format(emailContent.subject, emailContent.bodyIngredients, emailContent.bodyInstructions))

    return recipientEmail, emailContent

####################################################################################
# send an email
####################################################################################
def sendEmail(recipientEmail, emailContent):
    # get the ses client
    ses = boto3.client('ses')

    # send the email
    response = ses.send_email(
        Destination={
            'ToAddresses': [
                recipientEmail,
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': '{}<br><br>Here is your recipe:<br><br>{}<br>{}<br><br>Enjoy your meal and happy cooking!'.format(emailContent.salutation, emailContent.bodyIngredients, emailContent.bodyInstructions),
                },
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': '{}\n\nHere is your recipe:\n\n{}\n{}\n\nEnjoy your meal and happy cooking!'.format(emailContent.salutation, emailContent.bodyIngredients, emailContent.bodyInstructions),
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': emailContent.subject,
            },
        },
        # this is your verified email/domain
        Source=os.environ['SES_SENDER_EMAIL'],
    )

    logger.info('Email sent: {}'.format(response))

####################################################################################
# response back to bedrock agent
####################################################################################
def buildResponse(event):
    response_json = {"sendEmailStatus": "successful"}
    response_body = {
        'application/json': {
            'body':  {"application/json": {"body": json.dumps(response_json)}}
        }
    }
    
    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }
    
    session_attributes = event['sessionAttributes']
    prompt_session_attributes = event['promptSessionAttributes']
    
    api_response = {
        'messageVersion': '1.0', 
        'response': action_response,
        'sessionAttributes': session_attributes,
        'promptSessionAttributes': prompt_session_attributes
    }
        
    return api_response