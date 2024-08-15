import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
from log_type import LogType
from log_datetime import LogDateTime
import os

class LogTable:
    def __init__(self):
        if os.getenv("ENVIRONMENT") == 'development':
            boto3.setup_default_session(profile_name=os.getenv("PROFILE_NAME"))
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('Log')
    
    def GetID(self,user_name:str,log_type:LogType):
        return user_name + '_' + log_type.value
    
    def AddWeight(self,user_name:str,weight: float):
        response = self.table.put_item(
            Item={
                'log_id': self.GetID(user_name, LogType.WEIGHT),
                'log_datetime': LogDateTime.TimeInMilliseconds(),
                'user_name': user_name,
                'weight': Decimal(str(weight)),
                'type': LogType.WEIGHT.value,
                'datetime': LogDateTime.TimeInMilliseconds()
            }
        )
        return response['ResponseMetadata']['HTTPStatusCode'] == 200
    
    def GetWeight(self,user_name:str):
        response = self.table.query(
            KeyConditionExpression=Key('log_id').eq(self.GetID(user_name, LogType.WEIGHT))
            )
        return response['Items']

