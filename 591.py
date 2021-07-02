import json
import csv
import boto3
from boto3.dynamodb.conditions import Key
import os
from io import BytesIO, StringIO
import time, datetime

def printLog(logger):
    print("{time} : {message}".format(time = (datetime.datetime.now() + datetime.timedelta(hours = 8)).strftime("%Y-%m-%d %H:%M:%S"), message = logger))

def lambda_handler(event, context):
    # 預期在晚上00:00執行，讀取前一天的表格
    print('\r')
    printLog('Lambda execute initial.')
    
    queryTime = (datetime.datetime.now() + datetime.timedelta(hours=7)).strftime("%Y-%m-%d")
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DB_TABLE_CHECKOUT'])
    response = table.scan()
    printLog('Read datas from DynamoDB...')
    
    printLog('Data Count : {dataCount}'.format(dataCount = response['Count']))
    
    if(response['Count'] != 0):
        printLog('Searching datas at {time} in DynamoDB...'.format(time = queryTime))
        response = [i for i in response['Items'] if queryTime in i['time']]
        
        if(response):
            fields = ['Name', 'time', 'ontime', 's3_link']
        
            # writing rows in to the CSV file
            printLog('Writing rows in to the CSV file.')
            csvfile = StringIO()
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            writer.writerows(response)
            csvfile.seek(0)
            temp = BytesIO(csvfile.read().encode('utf8'))
            
            
            printLog('Sending CSV to S3.')
            s3 = boto3.client('s3')
            response = s3.upload_fileobj(temp, os.environ['BUCKET'], 
                queryTime.replace('-', '/')[:8] + "Daily_Records_" + queryTime.replace('-', '') + ".csv")
            
            # with open('/tmp/testtest.csv', 'w', newline='') as csvfile:
            #     writer = csv.DictWriter(csvfile, fieldnames=fields)
            #     writer.writeheader()
            #     writer.writerows(response['Items'])
            #     s3.upload_file('/tmp/testtest.csv', os.environ['BUCKET'], 'testtest.csv')
            # return response['Items']
            printLog('Data saved to S3 success.')
        else:
            printLog('No data to process, exiting.')
    else:
        printLog('No data to process, exiting.')
    
    table.delete()
    printLog('Attempting to delete DynamoDB table...')
    table.wait_until_not_exists()
    printLog('DynamoDB delete complete.')
    
    table = dynamodb.create_table(
        TableName = os.environ['DB_TABLE_CHECKOUT'],
        KeySchema = [
            {'AttributeName' : 'Name', 'KeyType' : 'HASH'},  # Partition key
            {'AttributeName' : 'time', 'KeyType' : 'RANGE'}  # Sort key
        ],
        AttributeDefinitions = [
            {'AttributeName': 'Name', 'AttributeType' : 'S'},
            {'AttributeName': 'time', 'AttributeType' : 'S'},
            {'AttributeName': 's3_link', 'AttributeType' : 'S'}
        ],
        BillingMode = 'PAY_PER_REQUEST',
        GlobalSecondaryIndexes = [
            {
                'IndexName': 's3_link_index',
                'KeySchema': [{'AttributeName' : 's3_link', 'KeyType' : 'HASH'}],
                'Projection': {
                    'ProjectionType': 'KEYS_ONLY',
                }
            }
        ],
        Tags = [{'Key': 'Retain', 'Value': 'True'}]
    )
    
    printLog("Attempting to create DynamoDB table...")
    table.wait_until_exists()
    printLog('DynamoDB table recreation complete.')
    printLog(table)
    print('\r')