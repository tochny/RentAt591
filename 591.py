import json
import csv
import time
import boto3
import base64
import requests
from io import BytesIO, StringIO

from Utility import UrlGenerator
from Entity.Entity import Entity, CryptoEntity
from bs4 import BeautifulSoup as Soup
from io import BytesIO, StringIO

# 取得所有條件的房子，對新來的物件進行推送通知
def Craw591():
    
     # 轉成好讀版
    # alert = FilterHouse(user, houseList, ) # 找誰需要通知
    
    return houseList
    
# 從 API List 中列出所有的房子
def GetHouseList():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table("UserID")
    session = requests.session()
    houseEntity = Entity()
    
    returnParams = []
    genUrl = UrlGenerator()
    

    token = GetCSRFTokenFromHtml(Get591Response(session))
    urls = list(GetHouseListFromDB())
    
    print("Done Get From DB")

    for user, condition, queryString in urls:
        c = CryptoEntity(user)
        encrypted_data = c.encrypt(json.dumps(houseEntity.Convert([Get591Response(session, queryString, token)])))
        s3_url = S3_write("alex-archive-tokyo", user + "/" + base64.b64encode(condition.value).decode('ascii'), encrypted_data)
        table.update_item(
            Key={
                'user': user,
                'condition': condition
            },
            # UpdateExpression='set assemble=:d, updateTime=:t',
            UpdateExpression='set s3_url=:d, updateTime=:t',
            ExpressionAttributeValues={
                ':d': s3_url.encode('utf-8'),
                ':t': int(time.time())
            },
            ReturnValues="NONE")
        returnParams.append(encrypted_data)
        
    print(returnParams)
    return returnParams
    
def GetHouseListFromDB():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table("UserID")

    done = False
    start_key = None
    ret = []
    while not done:
        response = table.scan()
        ret = response.get('Items', [])
        start_key = response.get('LastEvaluatedKey', None)
        done = start_key is None
    print("Done reading")
    for data in ret:
        c = CryptoEntity(data['user'])
        yield ([data['user'], data['condition'], c.decrypt(data['condition'].value)])


# 取得 591 的回應，如果不是拿 CSRF 偷啃的話一定要帶其他參數
def Get591Response(session, route=None, csrfToken=None): #一定要同一個 session
    url = UrlGenerator.BaseUrl + ("home/search/rsList" + route) if route else UrlGenerator.BaseUrl

    if(csrfToken):
        headers = {"X-CSRF-TOKEN": csrfToken, "X-Requested-With" : "XMLHttpRequest"}
        r = (session.get(url=url, headers=headers).json())
    else:
        r = session.get(url=url).text
    
    return r

# 討厭的 CSRF 偷啃
def GetCSRFTokenFromHtml(html):
    token = str(Soup(html, features="html.parser").find('meta',  {"name": "csrf-token"})["content"]) # Get token
    return token

# 揪出新來的菜逼八
def FilterHouse(houseList):
    returnParams = []
    for house in houseList:
        if(house['isNew']):
            returnParams.append(house)
            house['isNew'] = False
    return returnParams

def lambda_handler(event, context):
    # c = CryptoEntity('外面來的ID')
    
    
    print((GetHouseList()))
    
    return
    
    exit()


    url = "https://rent.591.com.tw/"
    queryString = "kind=0&region=1&section=7&rentprice=4&pattern=2"
    searchApi = "home/search/rsList?is_new_list=1&type=1&searchtype=1&"
    houseDetail = "rent-detail-10774640.html"
    
    session = requests.Session()
    
    
    while 1:
        r = session.get(url + '?' +  queryString).text  # Cookie initial & get whole page
        
        headers = {"X-CSRF-TOKEN": "", "X-Requested-With" : "XMLHttpRequest"}
        headers["X-CSRF-TOKEN"] = str(Soup(r, features="html.parser").find('meta',  {"name": "csrf-token"})["content"]) # Get token
        
        r = (session.get("https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region=1&section=7&rentprice=4&pattern=2", headers=headers).json())
        print(r)
        exit()

        count = r["records"]
        tophouses = r["data"]["topData"]
        houses = r["data"]["data"]
        index = []
        
        for house in houses:
         index.append(house["post_id"])
        
        print(len(house))
        print(len(tophouses))
        print(count)

        break

    print("Done")


def S3_write(bucket, name, object):
    csvfile = to_csv(object)
    temp = BytesIO(csvfile.read().encode('utf8'))
    s3 = boto3.client('s3')
    response = s3.upload_fileobj(temp, bucket, 
        name + ".csv")
        
    return 'https://{}.s3.ap-northeast-1.amazonaws.com/{}'.format(bucket, name)
    
def to_csv(object):
    fields = ['encrypted_data']
    csvfile = StringIO()
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    writer.writerow({"encrypted_data": base64.b64encode(object).decode('ascii')})
    csvfile.seek(0)
    return csvfile

def create_presigned_post(bucket_name, object_name,
                          fields=None, conditions=None, expiration=600):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3', region_name = 'ap-northeast-1')
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None
    
    # The response contains the presigned URL and required fields
    return response
    
def create_presigned_url(bucket_name, object_name, expiration=600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response