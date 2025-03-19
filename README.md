# Serverless-observability
# Demo - MusicQA: AI-Powered Music Question Answering System - AWS Native Observability

MusicQA is an AI-powered system that answers questions about music using AWS services and the CDK (Cloud Development Kit) for infrastructure deployment.

This project implements a serverless architecture to process user queries about music, leveraging natural language processing and a knowledge base to provide accurate and informative responses. The system is designed to scale automatically and handle a wide range of music-related questions efficiently.

## Repository Structureß

The repository is organized as follows:

- `app.py`: The main entry point for the CDK application.
- `cdk.json`: Configuration file for the CDK project.
- `requirements.txt`: Python dependencies for the project.
- `musicqa/`: Directory containing the main application code.
  - `musicqa_stack.py`: Defines the AWS resources using CDK constructs.
- `source.bat`: Windows batch script for activating the Python virtual environment.

## Usage Instructions

### Installation

1. Ensure you have Python 3.7 or later installed.
2. Install the AWS CDK CLI:
   ```
   npm install -g aws-cdk
   ```
3. Clone this repository:
   ```
   git clone https://github.com/caylent/serverless-observability.git
   cd musicqa
   ```
4. Create and activate a virtual environment:
   ```
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```
5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Deployment

1. Configure your AWS credentials:
   ```
   aws configure
   ```
2. Synthesize the CloudFormation template:
   ```
   cdk synth
   ```
3. Deploy the stack:
   ```
   cdk deploy
   ```

### Using the MusicQA System

After deployment, you can interact with the MusicQA system through the provided API Gateway endpoint. Send POST requests to the endpoint with your music-related questions in the request body.

Example:
```
curl -X POST https://your-api-gateway-url/prod/ask -d '{"question": "Who wrote Bohemian Rhapsody?"}'
```

## Data Flow

1. User submits a question through the API Gateway.
2. The request is routed to a Lambda function.
3. The Lambda function processes the question using natural language processing.
4. The processed question is used to query a knowledge base (e.g., DynamoDB or Amazon Kendra).
5. The retrieved information is formatted into a response.
6. The response is sent back through the API Gateway to the user.

```
[User] -> [API Gateway] -> [Lambda] -> [NLP Processing]
                                   -> [Knowledge Base Query]
                                   -> [Response Formatting]
         [API Gateway] <- [Lambda] <- [Final Response]
[User] <-
```

## Infrastructure

The project uses AWS CDK to define and deploy the following resources:

- Lambda: Processes questions and generates responses.
- API Gateway: Provides the HTTP endpoint for user interactions.
- CloudWatch: Monitors and logs system activities.
- IAM: Manages permissions for the various components.

The exact resources and their configurations are defined in the `musicqa_stack.py` file.

## Observability with AWS Services

This project leverages AWS-native observability services to monitor and analyze the performance of the serverless functions:

- Amazon CloudWatch: Logs function invocations, errors, and custom metrics.
- AWS X-Ray: Provides tracing and debugging insights for Lambda executions.
- Amazon CloudWatch Alarms: Alerts on anomalous behavior and potential issues.

## Enabling Observability

1. Ensure that CloudWatch logs and X-Ray tracing are enabled for all Lambda functions in the musicqa_stack.py file.

2. Access CloudWatch logs to monitor function execution:
```
aws logs tail /aws/lambda/musicqa-function --follow
```
3. Use the AWS X-Ray console to visualize traces and detect performance bottlenecks.

By integrating AWS observability tools, the system gains visibility into execution performance, error handling, and latency analysis, ensuring a robust and scalable serverless solution.