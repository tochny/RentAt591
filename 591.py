import requests
import json
import time
from bs4 import BeautifulSoup as Soup

class UrlGenerator:
    BaseUrl = "https://rent.591.com.tw/"
    HouseListRoute = "home/search/rsList"
    PhotoListRoute = "home/business/getPhotoList"
    LineNotifyUrl = "https://notify-api.line.me/api/notify"

    def GetHouseListApiRoute(self):
        returnParams = []
        for queryString in self.QueryStringBuilder():
            returnParams.append(self.HouseListRoute + queryString)
        return returnParams

    def QueryStringBuilder(self):
        returnParams = []
        with open("searchConfig.json") as jsonfile:
            searchConfig = json.load(jsonfile)
        returnParams.append("?is_new_list=1&type=1&kind=0&searchtype=1&region=1&section=7&rentprice=4&pattern=2")
        return returnParams

def Craw591():
    return GetHouseList()
    

def GetHouseList():
    session = requests.session()
    returnParams = ''
    genUrl = UrlGenerator()

    token = GetCSRFTokenFromHtml(Get591Response(session))
    urls = genUrl.GetHouseListApiRoute()
    print(urls)

    returnParams = (Get591Response(session, urls[0], token))
    
    # for url in urls:
    #     returnParams = (Get591Response(session, url, token))
    
    return returnParams


    
def Get591Response(session, route=None, csrfToken=None):
    
    url = UrlGenerator.BaseUrl + route if route else UrlGenerator.BaseUrl

    print(url)
    print(csrfToken)
    if(csrfToken):
        headers = {"X-CSRF-TOKEN": csrfToken, "X-Requested-With" : "XMLHttpRequest"}
        r = (session.get(url=url, headers=headers).json())
    else:
        r = session.get(url=url).text
    
    return r


def  GetCSRFTokenFromHtml(html):
    token = str(Soup(html, features="html.parser").find('meta',  {"name": "csrf-token"})["content"]) # Get token
    return token

if __name__ == '__main__':
    # print((Craw591()))

    # exit()


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
    exit()