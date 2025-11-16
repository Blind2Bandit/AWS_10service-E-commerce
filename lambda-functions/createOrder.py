import boto3
import json
import uuid
from datetime import datetime

# --- CONFIGURATION ---
# Change this to the Queue URL you saved in Step 7A
QUEUE_URL = "https://sqs.eu-north-1.amazonaws.com/464037860606/OrderQueue"
# Change this to match your table's key
TABLE_KEY = "OrderId" 
# ---------------------

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs') # <-- NEW: SQS client
table = dynamodb.Table('Orders')

def lambda_handler(event, context):
    try:
        # Get data from the event
        # Note: The body from API Gateway is now a JSON object
        # (This is handled by your v6 Amplify config: body: { ... })
        body = json.loads(event.get('body', '{}'))
        
        # Get user email from the Cognito authorizer token
        user_email = event['requestContext']['authorizer']['claims']['email']
        
        order_id = str(uuid.uuid4())
        items = body.get('items', [])
        
        order = {
            TABLE_KEY: order_id, # Use the correct key
            'userId': user_email, # Use the email from the token
            'items': items,
            'status': 'PENDING', # Set initial status
            'createdAt': datetime.utcnow().isoformat()
        }
        
        # 1. Put the item in DynamoDB (same as before)
        table.put_item(Item=order)
        
        # 2. --- NEW: Send a message to SQS ---
        message_body = {
            'orderId': order_id,
            'userEmail': user_email
        }
        
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message_body)
        )
        
        # 3. Return a fast response (same as before)
        return {
            'statusCode': 201, 
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            # Return the key that matches your table
            'body': json.dumps({'message': 'Order received', TABLE_KEY: order_id})
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500, 
            'body': json.dumps({'error': str(e)})
        }