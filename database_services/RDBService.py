from typing import KeysView, ValuesView
import pymysql
import json
import logging

import middleware.context as context

import boto3
import json
import decimal
import time

import botocore
from boto3.dynamodb.conditions import Key, Attr, And
from botocore.exceptions import ClientError


dynamodb = boto3.resource(
    service_name='dynamodb',
    region_name='us-east-2',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
table = dynamodb.Table('6156_game')

class RDBService:

    def __init__(self):
        pass

    # @classmethod
    # def _get_db_connection(cls):

        # db_connect_info = context.get_db_info()
        #
        # logger.info("RDBService._get_db_connection:")
        # logger.info("\t HOST = " + db_connect_info['host'])
        #
        # db_info = context.get_db_info()
        #
        # db_connection = pymysql.connect(
        #    **db_info,
        #     autocommit=True
        # )
        # return db_connection

    # @classmethod
    # def run_sql(cls, sql_statement, args, fetch=False):

    #     conn = RDBService._get_db_connection()

    #     try:
    #         cur = conn.cursor()
    #         res = cur.execute(sql_statement, args=args)
    #         if fetch:
    #             res = cur.fetchall()
    #     except Exception as e:
    #         conn.close()
    #         raise e

    #     return res

    # @classmethod
    # def get_by_prefix(cls, db_schema, table_name, column_name, value_prefix):

    #     conn = RDBService._get_db_connection()
    #     cur = conn.cursor()

    #     sql = "select * from " + db_schema + "." + table_name + " where " + \
    #         column_name + " like " + "'" + value_prefix + "%'"
    #     print("SQL Statement = " + cur.mogrify(sql, None))

    #     res = cur.execute(sql)
    #     res = cur.fetchall()

    #     conn.close()

    #     return res

    # @classmethod
    # def _get_where_clause_args(cls, template):

    #     terms = []
    #     args = []
    #     clause = None

    #     if template is None or template == {}:
    #         clause = ""
    #         args = None
    #     else:
    #         for k,v in template.items():
    #             terms.append(k + "=%s")
    #             args.append(v)

    #         clause = " where " +  " AND ".join(terms)


    #     return clause, args

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
                            FilterExpression=Attr(k).eq(v)
                        )
                    res += response['Items']
        except ClientError as e:
            raise
        else:
            return res


    @classmethod
    def create(cls, db_schema, table_name, create_data):
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
    def update(cls, db_schema, table_name, select_data, update_data):

        # select_clause, select_args = RDBService._get_where_clause_args(select_data)

        # cols = []
        # args = []

        # for k, v in update_data.items():
        #     cols.append(k + "=%s")
        #     args.append(v)
        # clause = "set " + ", ".join(cols)
        # args = args + select_args

        # sql_stmt = "update " + db_schema + "." + table_name + " " + clause + \
        #            " " + select_clause

        # res = RDBService.run_sql(sql_stmt, args)
        # return res

        item = update_data
        item["version"] += 1
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
                Key=select_data,
                UpdateExpression=set_clause,
                ExpressionAttributeValues=expression_attr,
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            raise
        else:
            return response['Attributes']
    
    @classmethod
    def insert(cls, db_schema, table_name, select_data, update_data):
        item = update_data
        item["version"] += 1
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
    def delete(cls, db_schema, table_name, template):
        # clause, args = RDBService._get_where_clause_args(template)
        # sql_stmt = "delete from " + db_schema + "." + table_name + " " + clause
        # res = RDBService.run_sql(sql_stmt, args)
        # return res

        try:
            print(template)
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
