import aws_cdk as core
import aws_cdk.assertions as assertions

from musicqa.musicqa_stack import MusicQAStack

# example tests. To run these tests, uncomment this file along with the example
# resource in demo01/demo01_stack.py
def test_music_qa_stack():
    app = core.App()
    stack = MusicQAStack(app, "musicqa")
    template = assertions.Template.from_stack(stack)

    # Test Lambda Function
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "music_qa.handler",
        "Runtime": "python3.9",
        "Timeout": 30,
        "MemorySize": 512,
        "TracingConfig": {"Mode": "Active"}
    })

    # Test API Gateway
    template.has_resource_properties("AWS::ApiGateway::RestApi", {
        "Name": "Music Q&A API"
    })
