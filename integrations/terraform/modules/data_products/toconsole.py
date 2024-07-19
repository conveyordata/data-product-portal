import urllib, json, sys
import os
import logging
import requests # 'pip install requests'
import boto3 # AWS SDK for Python (Boto3) 'pip install boto3'

# Step 1: Authenticate user in your own identity system.

# Step 2: Using the access keys for an IAM user in your AWS account,
# call "AssumeRole" to get temporary access keys for the federated user

# Note: Calls to AWS STS AssumeRole must be signed using the access key ID
# and secret access key of an IAM user or using existing temporary credentials.
# The credentials can be in Amazon EC2 instance metadata, in environment variables,
# or in a configuration file, and will be discovered automatically by the
# client('sts') function. For more information, see the Python SDK docs:
# http://boto3.readthedocs.io/en/latest/reference/services/sts.html
# http://boto3.readthedocs.io/en/latest/reference/services/sts.html#STS.Client.assume_role
sts_connection = boto3.client('sts')

if 'AWS_WEB_IDENTITY_TOKEN_FILE' in os.environ:
    role = os.environ["AWS_ROLE_ARN"]
    token = open(os.environ['AWS_WEB_IDENTITY_TOKEN_FILE'], 'r').readline()
    assumed_role_object = sts_connection.assume_role_with_web_identity(
        RoleArn=role,
        RoleSessionName="AssumeRoleSession",
        WebIdentityToken=token,
        #ProviderId='www.amazon.com',
        #PolicyArns=[{'arn': 'string'}],
        #Policy='string',
        DurationSeconds=3600
    )
else:
    assumed_role_object = sts_connection.assume_role(
        RoleArn=os.environ["AWS_ROLE_ARN"],
        RoleSessionName="AssumeRoleSession",
    )

# Step 3: Format resulting temporary credentials into JSON
url_credentials = {}
url_credentials['sessionId'] = assumed_role_object.get('Credentials').get('AccessKeyId')
url_credentials['sessionKey'] = assumed_role_object.get('Credentials').get('SecretAccessKey')
url_credentials['sessionToken'] = assumed_role_object.get('Credentials').get('SessionToken')

json_string_with_temp_credentials = json.dumps(url_credentials)

# Step 4. Make request to AWS federation endpoint to get sign-in token. Construct the parameter string with
# the sign-in action request, a 12-hour session duration, and the JSON document with temporary credentials
# as parameters.
request_parameters = "?Action=getSigninToken"
if False: # not to be included when you got the temporary credentials with GetFederationToke
    request_parameters += "&SessionDuration=43200"
if sys.version_info[0] < 3:
    def quote_plus_function(s):
        return urllib.quote_plus(s)
else:
    def quote_plus_function(s):
        return urllib.parse.quote_plus(s)
request_parameters += "&Session=" + quote_plus_function(json_string_with_temp_credentials)
#request_url = "https://signin.aws.amazon.com/federation" + request_parameters
request_url = "https://eu-west-1.signin.aws.amazon.com/federation" + request_parameters
r = requests.get(request_url)

# Returns a JSON document with a single element named SigninToken.
try:
    signin_token = json.loads(r.text)
except json.decoder.JSONDecodeError as e:
    logging.error(type(r.text))
    logging.error(r.text)
    raise e

# Step 5: Create URL where users can use the sign-in token to sign in to
# the console. This URL must be used within 15 minutes after the
# sign-in token was issued.
request_parameters = "?Action=login"
request_parameters += "&Issuer=Example.org"
request_parameters += "&Destination=" + quote_plus_function("https://console.aws.amazon.com/")
request_parameters += "&SigninToken=" + signin_token["SigninToken"]
request_url = "https://signin.aws.amazon.com/federation" + request_parameters

# Send final URL to stdout
print (request_url)
