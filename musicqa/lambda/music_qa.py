import json
import os
import boto3
import aws_xray_sdk.core
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Initialize X-Ray
patch_all()

# Initialize Bedrock client
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def handler(event, context):
    try:
        print(f'Event: {event}')  # Debugging log

        # Extract question from the request
        body = json.loads(event.get('body', '{}'))
        question = body.get('question', '').strip()

        print(f'Question: {question}')  # Debugging log
        
        if not question:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Question is required'})
            }

        # ✅ Corrected Claude v2 request format
        payload = {
            "anthropic_version": "bedrock-2023-05-31",  # Required field
            "messages": [
                {"role": "user", "content": question}  # Claude requires "user" as the first message
            ],
            "max_tokens": 300,
            "temperature": 0.7
        }

        print(f'Payload: {json.dumps(payload, indent=2)}')  # Debugging log
        
        # Call Bedrock
        response = bedrock.invoke_model(
            modelId="anthropic.claude-v2",  # Using Claude v2 model
            contentType="application/json",  # ✅ Explicitly set content type
            accept="application/json",
            body=json.dumps(payload)
        )
        
        # Parse Bedrock response
        response_body = json.loads(response['body'].read().decode("utf-8"))
        answer = response_body.get("content", "Sorry, I could not generate an answer.")

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'question': question,
                'answer': answer
            })
        }

    except Exception as e:
        print(f'Error: {str(e)}')  # Debugging log
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
