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
    try:
        response = table.scan()
        products = response['Items']
        
        # --- This is the CHANGE ---
        # Tell json.dumps() to use your new DecimalEncoder helper
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                # Add CORS headers for your frontend
                'Access-Control-Allow-Origin': '*', 
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            'body': json.dumps(products, cls=DecimalEncoder) 
        }
        # ------------------------

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }