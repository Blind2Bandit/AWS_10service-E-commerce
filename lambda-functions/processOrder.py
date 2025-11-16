import boto3
import json
from decimal import Decimal

# --- CONFIGURATION ---
# Change this to the email you verified in SES (Step 7B)
FROM_EMAIL = "kpbehara10@gmail.com" 
# Change this to match your table's key (it was 'OrderId' with a capital O)
TABLE_KEY = "OrderId"
# ---------------------

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
table = dynamodb.Table('Orders')

# Helper class for JSON (you'll need it if you print the order)
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    
    for record in event['Records']:
        try:
            # 1. Parse the message from SQS
            message_body = json.loads(record['body'])
            order_id = message_body['orderId']
            user_email = message_body['userEmail']
            
            print(f"Processing order {order_id} for {user_email}...")
            
            # 2. (In a real app, process payment here)
            
            # 3. Update DynamoDB status from PENDING to CONFIRMED
            response = table.update_item(
                Key={ TABLE_KEY: order_id },
                UpdateExpression="set #s = :s",
                ExpressionAttributeNames={
                    '#s': 'status'
                },
                ExpressionAttributeValues={
                    ':s': 'CONFIRMED'
                },
                ReturnValues="UPDATED_NEW"
            )
            print(f"DynamoDB update response: {response}")

            # 4. Send confirmation email via SES
            ses_response = ses.send_email(
                Source=FROM_EMAIL,
                Destination={
                    'ToAddresses': [ user_email ]
                },
                Message={
                    'Subject': {
                        'Data': f"Order Confirmed: {order_id}"
                    },
                    'Body': {
                        'Text': {
                            'Data': f"Your order {order_id} has been confirmed and is being processed. Thank you for your purchase!"
                        }
                    }
                }
            )
            print(f"SES response: {ses_response['MessageId']}")

        except Exception as e:
            print(f"Error processing record: {e}")
            # Even if one message fails, continue to the next
            continue
            
    return {'statusCode': 200, 'body': json.dumps('Processing complete.')}