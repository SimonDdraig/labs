# Simon Davies @ DoiT International
# doit-bedrock-recipe-chatbot-order-delivery-fn.py
# doit-bedrock-recipe-chatbot-order-delivery-fn
# orders ingredients from details passed in via the bedrock agent event
# note for the workshop, the lambda simulates this functionality

# aws api libraries
import boto3
import json

# logging libraries
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

####################################################################################
# controlling function
####################################################################################
def lambda_handler(event, context):
    logger.info('doit-bedrock-recipe-chatbot-order-delivery-fn lambda has been called')
    logger.info('event passed in: {}'.format(event))

    # NOTE you could check the apiPath value here, and call an appropriate method if required.
    # this would allow you to use a single lambda for multiple action groups if preferred.
    # we just use /order so we don't bother checking it.

    # place the order
    orderContent = getProperties(event)
    orderRef = placeOrder(orderContent)

    # build the response to send back to the agent
    response = buildResponse(orderRef, event)

    # return
    return response

####################################################################################
# get all the meta data we need
####################################################################################
def getProperties(event):
    properties = event.get("requestBody", {}).get("content", {}).get("application/json", {}).get("properties", [])

    # prepare vars
    firstnameP = 'NOT FOUND firstnameP'
    ingredientsP = 'NOT FOUND ingredientsP'
    deliveryAddressP = 'NOT FOUND deliveryAddressP'

    for prop in properties:
        if prop.get("name") == "firstname":
            firstnameP = prop.get("value")
            break
    for prop in properties:
        if prop.get("name") == "ingredients":
            ingredientsP = prop.get("value")
            break
    for prop in properties:
        if prop.get("name") == "deliveryAddress":
            deliveryAddressP = prop.get("value")
            break

    class orderContent:
        ingredients = ingredientsP
        deliveryAddress = deliveryAddressP
        firstname = firstnameP

    logger.info('Ordering ingredients: {} for delivery to: {} for: {}'.format(orderContent.ingredients, orderContent.deliveryAddress, orderContent.firstname))

    return orderContent

####################################################################################
# place the order
####################################################################################
def placeOrder(orderContent):
    # simulate the order
    
    # 1. write order to dynamodb
    # 2. call a 3rd party api - could be a store that delivers immediately
    # 3. receive an order reference from the store
    orderRef = '123ABC'

    logger.info('Order placed, reference: {}'.format(orderRef))
    return orderRef

####################################################################################
# response back to bedrock agent
####################################################################################
def buildResponse(orderRef, event):
    response_json = {"placeOrderStatus": "successful", "orderRef": orderRef}
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