from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
)
from constructs import Construct

class MusicQAStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Lambda function
        music_qa_lambda = _lambda.Function(
            self, 'MusicQAFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='music_qa.handler',
            code=_lambda.Code.from_asset('musicqa/lambda'),
            timeout=Duration.seconds(30),
            memory_size=512,
            tracing=_lambda.Tracing.ACTIVE  # Enable X-Ray tracing,
        )
        
        # Grant Bedrock permissions to Lambda
        music_qa_lambda.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=['bedrock:InvokeModel'],
            resources=['*']  # You might want to restrict this to specific model ARNs
        ))

        # Create API Gateway with X-Ray tracing enabled
        api = apigw.RestApi(
            self, 'MusicQAApi',
            rest_api_name='Music Q&A API',
            deploy_options=apigw.StageOptions(
                tracing_enabled=True,  # Enable X-Ray tracing
                logging_level=apigw.MethodLoggingLevel.INFO,
                metrics_enabled=True,
                data_trace_enabled=True,
            )
        )

        # Create API endpoint
        questions = api.root.add_resource('questions')
        questions.add_method(
            'POST', 
            apigw.LambdaIntegration(music_qa_lambda),
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Content-Type': True,
                }
            }]
        )

        # Nothing more to add here - stack is complete
