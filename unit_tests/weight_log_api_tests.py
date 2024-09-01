from moto import mock_aws
import boto3
import sys
import pytest
from fastapi.testclient import TestClient
import os
#will work only if you run the test from the root folder
sys.path.append('./src')
from first_api import app
client = TestClient(app)

def create_log_table(dynamodb):
    """Helper function to create the Log table."""
    dynamodb.create_table(
        TableName='Log',
        KeySchema=[
            {'AttributeName': 'log_id', 'KeyType': 'HASH'},
            {'AttributeName': 'log_datetime', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'log_id', 'AttributeType': 'S'},
            {'AttributeName': 'log_datetime', 'AttributeType': 'N'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welocme to the log API"}

@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "ap-south-1"
    os.environ["ENVIRONMENT"] = "test"

@mock_aws
def test_add_weight(aws_credentials,mocker):
    dynamodb=boto3.resource('dynamodb')
    create_log_table(dynamodb)
    mocker.patch('first_api.id_token.verify_oauth2_token',return_value={"email": "user"})
    response = client.post("/v1/weight?weight=170", headers={"Authorization": "Bearer 123456"})
    assert response.json() == {"weight": 170}

@mock_aws
def test_get_weight(aws_credentials,mocker):
    dynamodb=boto3.resource('dynamodb')
    create_log_table(dynamodb)
    mocker.patch('first_api.id_token.verify_oauth2_token',return_value={"email": "user"})
    client.post("/v1/weight?weight=170", headers={"Authorization": "Bearer 123456"})
    response = client.get("/v1/weight", headers={"Authorization": "Bearer  123456"})
    response_json = response.json()
    assert response_json[0]['weight'] == 170

