# Translating https://learn.hashicorp.com/terraform/aws/lambda-api-gateway

import os
import mimetypes

from pulumi import export, FileAsset, ResourceOptions, Output
from pulumi_aws import s3, lambda_, apigateway
import iam

LAMBDA_SOURCE = 'lambda.py'
LAMBDA_PACKAGE = 'lambda.zip'
LAMBDA_VERSION = '1.0.0'
os.system('zip %s %s' % (LAMBDA_PACKAGE, LAMBDA_SOURCE))

# Create an AWS resource (S3 Bucket)
bucket = s3.Bucket('lambda-api-gateway-example')

mime_type, _ = mimetypes.guess_type(LAMBDA_PACKAGE)
obj = s3.BucketObject(
            LAMBDA_VERSION+'/'+LAMBDA_PACKAGE,
            bucket=bucket.id,
            source=FileAsset(LAMBDA_PACKAGE),
            content_type=mime_type
            )

example_fn = lambda_.Function(
    'ServerlessExample',
    s3_bucket=bucket.id,
    s3_key=LAMBDA_VERSION+'/'+LAMBDA_PACKAGE,
    handler="lambda.handler",
    runtime="python3.7",
    role=iam.lambda_role.arn,
)

example_api = apigateway.RestApi(
    'ServerlessExample',
    description='Pulumi Lambda API Gateway Example'
)

proxy_res = apigateway.Resource(
    'proxy',
    rest_api=example_api,
    parent_id=example_api.root_resource_id,
    path_part='{proxy+}'
)

proxy_met = apigateway.Method(
    'proxy',
    rest_api=example_api,
    resource_id=proxy_res.id,
    http_method='ANY',
    authorization='NONE'
)

example_int = apigateway.Integration(
    'lambda',
    rest_api=example_api,
    resource_id=proxy_met.resource_id,
    http_method=proxy_met.http_method,
    integration_http_method='POST',
    type='AWS_PROXY',
    uri=example_fn.invoke_arn
)

proxy_root_met = apigateway.Method(
    'proxy_root',
    rest_api=example_api,
    resource_id=example_api.root_resource_id,
    http_method='ANY',
    authorization='NONE'
)

example_root_int = apigateway.Integration(
    'lambda_root',
    rest_api=example_api,
    resource_id=proxy_root_met.resource_id,
    http_method=proxy_root_met.http_method,
    integration_http_method='POST',
    type='AWS_PROXY',
    uri=example_fn.invoke_arn
)

example_dep = apigateway.Deployment(
    'example',
    rest_api=example_api,
    stage_name="example-test",
    __opts__=ResourceOptions(depends_on=[example_int, example_root_int])
)

example_perm = lambda_.Permission(
    "apigw",
    statement_id="AllowAPIGatewayInvoke",
    action="lambda:InvokeFunction",
    function=example_fn,
    principal="apigateway.amazonaws.com",
    source_arn=example_dep.execution_arn.apply(lambda x:f"{x}/*/*")
)

# Export the name of the bucket with lambda code
# List bucket with:
# aws s3 ls --recursive `pulumi stack output bucket_name`
export('bucket_name',  bucket.id)
# Export the name of the lambda
# Test with:
# aws lambda invoke --region=eu-west-1 --function-name=`pulumi stack output lambda_name` output.txt
export('lambda_name',  example_fn.id)
# Export the name of the API endpoint
export('base_url', example_dep.invoke_url)
