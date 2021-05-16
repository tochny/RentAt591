import requests
import json
import time
from bs4 import BeautifulSoup as Soup

class Entity:
    HouseEntityList = []
    HouseEntity = {
        "title": "",
        "address": "",
        "addr_number_name": "",
        "houseUrl": "",
        "street_name": "",
        "alley_name": "",
        "lane_name": "",
        "coverUrl": "",
        "album": [],
        "distance": 0,
        "floor": "",
        "kind_name": "",
        "post_id": "",
        "price": "",
        "layout": "",
        "area" : "",
        "regionName": "",
        "sectionName": "",
        "updateTime": "",
        "isNew": True
    }

    def Convert(self, houseList):
        for house in houseList:
            for obj in house['data']['data']:
                self.HouseEntity = {
                    "title": obj["address_img"],
                    "address": obj["regionname"] + obj["sectionname"] + obj["street_name"] + obj["alley_name"] + obj["lane_name"] + obj["addr_number_name"],
                    "houseUrl": f"https://rent.591.com.tw/rent-detail-{obj['post_id']}.html",
                    "coverUrl": obj["cover"],
                    "album": obj["house_img"].split(','),
                    "street_name": obj["street_name"],
                    "alley_name": obj["alley_name"],
                    "lane_name": obj["lane_name"],
                    "addr_number_name": obj["addr_number_name"],
                    "floor": obj["floorInfo"],
                    "kind_name": obj["kind_name"],
                    "post_id": obj["post_id"],
                    "price": obj["price"],
                    "layout": obj["layout"],
                    "area" : obj["area"],
                    "regionName": obj["regionname"],
                    "sectionName": obj["sectionname"],
                    "updateTime": obj["refreshtime"]
                }
                self.HouseEntityList.append(self.HouseEntity)
        
        return self.HouseEntityList

class UrlGenerator:
    BaseUrl = "https://rent.591.com.tw/"
    HouseListRoute = "home/search/rsList"
    PhotoListRoute = "home/business/getPhotoList"
    LineNotifyUrl = "https://notify-api.line.me/api/notify"
    # 就是加上 rslist 好像有點無用
    def GetHouseListApiRoute(self):
        returnParams = []
        for queryString in self.QueryStringBuilder():
            returnParams.append(self.HouseListRoute + queryString)
        return returnParams

    # todo implement
    # 預計要接上 Line API 來選擇要什麼條件
    def QueryStringBuilder(self):
        returnParams = []
        with open("searchConfig.json") as jsonfile:
            searchConfig = json.load(jsonfile)
        returnParams.append("?is_new_list=1&type=1&kind=0&searchtype=1&region=1&section=7&rentprice=4&pattern=2")
        return returnParams

# 取得所有條件的房子，對新來的物件進行推送通知
def Craw591():
    houseEntity = Entity()
    houseList = houseEntity.Convert(GetHouseList())
    return houseList
    
# 從 API List 中列出所有的房子
def GetHouseList():
    session = requests.session()
    returnParams = []
    genUrl = UrlGenerator()

    token = GetCSRFTokenFromHtml(Get591Response(session))
    urls = genUrl.GetHouseListApiRoute()
        
    for url in urls:
        returnParams.append(Get591Response(session, url, token))

    return returnParams

# 取得 591 的回應，如果不是拿 CSRF 偷啃的話一定要帶其他參數
def Get591Response(session, route=None, csrfToken=None): #一定要同一個 session
    url = UrlGenerator.BaseUrl + route if route else UrlGenerator.BaseUrl

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
    pass

if __name__ == '__main__':

    print((Craw591()))

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
    exit()