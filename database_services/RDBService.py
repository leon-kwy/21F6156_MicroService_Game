from typing import KeysView, ValuesView
import pymysql
import json
import logging

import middleware.context as context

import boto3
import json
import decimal
import time
import os

import botocore
from boto3.dynamodb.conditions import Key, Attr, And
from botocore.exceptions import ClientError



dynamodb = boto3.resource(
    service_name='dynamodb',
    region_name='us-east-2',
    aws_access_key_id=os.environ['aws_access_key_id'],
    aws_secret_access_key=os.environ['aws_secret_access_key']
)
table = dynamodb.Table('6156_game')

class RDBService:

    def __init__(self):
        pass

    @classmethod
    def find_by_template(cls, template, limit, offset):
        res = []
        try:
            if template is None:
                res = table.scan()['Items']
            else:
                for k,v in template.items():
                    if k == 'id':
                        response = table.scan(
                            FilterExpression=Attr(k).eq(int(v))
                        )
                    elif k == 'G_Type':
                        if len(template['G_Type']) > 1:
                            response = table.scan(
                                FilterExpression=And(*[(Attr('G_Type').contains(value)) for value in template['G_Type']])
                            )
                        else:
                            response = table.scan(
                                FilterExpression=Attr(k).contains(template['G_Type'][0])
                            )
                    else:
                        response = table.scan(
                            FilterExpression=Attr(k).contains(v)
                        )
                    res += response['Items']
            if offset < len(res):
                # if offset == 0:
                #     res = table.scan(
                #         Limit=limit
                #     )['Items']
                # else:
                #     res = table.scan(
                #         ExclusiveStartKey={'id': res[offset-1]["id"]},
                #         Limit=limit
                #     )['Items']
                if offset + limit <= len(res):
                    res = res[offset:offset + limit]
                else:
                    res = res[offset:]
            else:
                res = []

        except ClientError as e:
            raise
        else:
            return res


    @classmethod
    def create(cls, create_data):
        item = create_data
        item['version'] = 0
        try:
            table.put_item(Item=item, ConditionExpression='attribute_not_exists(Game_name)')
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise
        else:
            return 1


    @classmethod
    def update(cls, ID, update_data):

        current_version = update_data['version']
        update_data["version"] += 1
        keys = list(update_data.keys())
        values = list(update_data.values())
        attrs = [':a', ':b', ':c', ':d', ':e']
        set_clause = "set "
        expression_attr = {}
        for i in range(len(keys)):
            set_clause += keys[i] + "=" + attrs[i] + ","
        set_clause = set_clause[:-1]
        for i in range(len(values)):
            expression_attr[attrs[i]] = values[i]
        try:
            response = table.update_item(
                Key={'id': ID},
                UpdateExpression=set_clause,
                ExpressionAttributeValues=expression_attr,
                ConditionExpression=Attr('version').eq(current_version),
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            raise
        else:
            return response['Attributes']
    
    @classmethod
    def insert(cls,  select_data, update_data):
        try:
            response = table.update_item(
                Key=select_data,
                UpdateExpression="SET G_Type = list_append( G_Type, :i)",
                ExpressionAttributeValues={':i': update_data},
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            raise
        else:
            return response['Attributes']

    @classmethod
    def delete(cls, template):
        try:
            response = table.delete_item(
                Key=template,
            )
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                print(e.response['Error']['Message'])
            else:
                raise
        else:
            return response
