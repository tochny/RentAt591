import requests
import json
import time
from bs4 import BeautifulSoup as Soup

class UrlGenerator:
    BaseUrl = "https://rent.591.com.tw/"
    HouseListUrl = "home/search/rsList"
    PhotoListUrl = "home/business/getPhotoList"
    LineNotifyUrl = "https://notify-api.line.me/api/notify"

    def GetHouseListApiUrl():
        returnParams = []
        for queryString in QueryStringBuilder():
            returnParams.append(HouseListUrl + queryString)
        return returnParams

    def QueryStringBuilder():
        returnParams = []

    def ValidateFilterCondition():

class HouseEntity:
    title = ""
    address = ""
    addr_number_name = ""
    


if __name__ == '__main__':
    url = "https://rent.591.com.tw/"
    queryString = "?kind=0&region=1&section=7&rentprice=4&pattern=2"
    searchApi = "home/search/rsList?is_new_list=1&type=1&searchtype=1&"
    houseDetail = "rent-detail-10774640.html"
    
    session = requests.Session()
    headers = {"X-CSRF-TOKEN": "", "X-Requested-With" : "XMLHttpRequest"}
    
    while 1:
        r = session.get(url + queryString).text  # Cookie initial & get whole page
        headers["X-CSRF-TOKEN"] = str(Soup(r, features="html.parser").find('meta',  {"name": "csrf-token"})["content"]) # Get token
        
        r = (session.get(searchApi + queryString, headers=headers).json())
        
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
    exit()