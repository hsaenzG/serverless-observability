import json
import os
import boto3
import time
from aws_xray_sdk.core import patch_all, xray_recorder
from aws_xray_sdk.core import patch
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
cloudwatch = boto3.client('cloudwatch')

# Configure X-Ray
patch_all()
patch(['boto3'])


@xray_recorder.capture('handler')
def handler(event, context):
    try:
        logger.info(f'Event received: {event}')

        # Start measuring request duration
        start_time = time.time()

        # Extract question from the request
        body = event.get('body', '{}')
        if isinstance(body, str):  
            body = json.loads(body)  # Only parse if it's a string

        question = body.get('question', '').strip()

        logger.info(f'Processing question: {question}')

        if not question:
            logger.warning('Empty question received')
            cloudwatch.put_metric_data(
                Namespace='MusicQA',
                MetricData=[{
                    'MetricName': 'InvalidRequests',
                    'Value': 1,
                    'Unit': 'Count'
                }]
            )
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Question is required'})
            }

        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {"role": "user", "content": question}
            ],
            "max_tokens": 300,
            "temperature": 0.7
        }

        logger.debug(f'Bedrock payload: {json.dumps(payload, indent=2)}')

        # Create X-Ray subsegment for Bedrock API call
        subsegment = xray_recorder.begin_subsegment('bedrock_invoke_model')

        try:
            response = bedrock.invoke_model(
                modelId="anthropic.claude-v2",
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload)
            )

            # Read and parse the response properly
            response_body = json.loads(response['body'].read().decode("utf-8"))
            logger.info(f"Raw Bedrock Response: {json.dumps(response_body, indent=2)}")

            # Extract answer safely
            answer = "Sorry, I could not generate an answer."
            if "content" in response_body and isinstance(response_body["content"], list):
                # Extract text from the first content block
                answer = response_body["content"][0].get("text", answer)

            subsegment.put_annotation('BedrockResponse', json.dumps(response_body))

        except Exception as e:
            subsegment.add_exception(e)
            logger.error(f"Error invoking Bedrock model: {str(e)}", exc_info=True)
            raise e  # Ensure the error propagates properly

        finally:
            xray_recorder.end_subsegment()  # Manually close the subsegment

        # Calculate request duration and record metrics
        duration = time.time() - start_time
        logger.info(f'Request processed in {duration:.2f} seconds')

        # Record CloudWatch metrics
        cloudwatch.put_metric_data(
            Namespace='MusicQA',
            MetricData=[
                {
                    'MetricName': 'RequestLatency',
                    'Value': duration,
                    'Unit': 'Seconds'
                },
                {
                    'MetricName': 'SuccessfulRequests',
                    'Value': 1,
                    'Unit': 'Count'
                }
            ]
        )

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'question': question,
                'answer': answer
            })
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)  # Improved error logging
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }
