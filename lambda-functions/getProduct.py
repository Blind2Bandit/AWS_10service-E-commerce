import boto3
import json
from decimal import Decimal # <-- 1. Import the Decimal library

# --- This is the FIX ---
# Create a custom helper class to convert Decimal to int or float
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 == 0:
                return int(o)  # Convert whole numbers to int
            else:
                return float(o) # Convert numbers with decimals to float
        return super(DecimalEncoder, self).default(o)
# ------------------------

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Products')

def lambda_handler(event, context):
    # Get productId from the API Gateway path parameters
    try:
        product_id = event.get('pathParameters', {}).get('productId')
    except Exception as e:
        # Handle cases where pathParameters might be missing/None
        product_id = None
        
    if not product_id:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Missing productId in path'})}
    
    try:
        # Fetch the specific item from DynamoDB
        response = table.get_item(Key={'productId': product_id})
        item = response.get('Item')
        
        if item:
            # --- This is the CHANGE ---
            # Tell json.dumps() to use your new DecimalEncoder helper
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*', # Add CORS headers
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET'
                },
                'body': json.dumps(item, cls=DecimalEncoder)
            }
            # ------------------------
        else:
            return {
                'statusCode': 404, 
                'body': json.dumps({'error': 'Product not found'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500, 
            'body': json.dumps({'error': str(e)})
        }