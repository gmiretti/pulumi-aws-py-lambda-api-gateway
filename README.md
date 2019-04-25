# lambda-apigateway

This [Pulumi](https://github.com/pulumi/pulumi) example use Python to deploy a serverless app using AWS Lambda and API Gateway as it's show in https://learn.hashicorp.com/terraform/aws/lambda-api-gateway

This example doesn't feature any of the higher-level abstractions of Pulumi, unavailable for Python at the moment ex. `python-awsx`, but it highlitghts the ability to manage existing application code in a Pulumi application.

```bash
# Create and configure a new stack
$ pulumi stack init lambda-api-gateway-dev
$ pulumi config set aws:region eu-wast-1

# Install dependencies
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt

# Preview and run the deployment
$ pulumi up
Previewing changes:
...
Performing changes:
...
info: 14 changes performed:
    + 14 resources created
Update duration: 25.017340162s

# Test it out
$ curl $(pulumi stack output base_url)
<p>Hello world!</p>

# See the logs
$ pulumi logs -f

# Remove the app
$ pulumi destroy
```
