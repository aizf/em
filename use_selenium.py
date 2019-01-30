import io
import json
import random
import re
import sys
import time

import pymysql
import redis
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, encoding='utf-8')  #改变标准输出的默认编码


class crawCnRank:
    def __init__(self, browser, matchId):
        self.__browser = browser
        self.__initId = matchId  #初始ID
        self.__url = "http://dotamax.com/match/detail/"

        self.__Id = str(matchId)  #char
        browser.get(self.__url + self.__Id)  #工作页面
        self.alter = 1   #偏移量
        self.addOrSub = True
        # self.__Id= browser.find_element_by_css_selector(
        #     "body > div.maxtopbar > div.main-shadow-box > div.main-container > div.container.xuning-box > table.match-detail-info.new-box > tbody > tr:nth-child(2) > td:nth-child(1)"
        # ).text
        # print(self.__Id)

    def __judgeWinner(self, str):
        if "天辉" in str:
            return "radiant"
        elif "夜魇" in str:
            return "dire"
        else:
            return "none"

    def __eqListToJson(self, obj):
        # print(1)
        eq = []
        pattern = re.compile(r"detail/(\w+)")
        divs = obj.find_elements_by_tag_name("div")
        for i in divs:
            ii = i.find_elements_by_tag_name("a")
            for j in ii:
                for jj in pattern.findall(j.get_attribute('href')):
                    eq.append(jj)
        # print(json.dumps(eq))
        return json.dumps(eq)

    def crawlCnRank_head(self):
        browser = self.__browser
        mode = browser.find_element_by_css_selector(
            "body > div.maxtopbar > div.main-shadow-box > div.main-container > div.container.xuning-box > table.match-detail-info.new-box > tbody > tr:nth-child(2) > td:nth-child(7)"
        ).text
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="123456",
            database="cnrank",
            charset="utf8")
        cursor = db.cursor()
        sql =   """REPLACE INTO HEAD(Id,winner, duration, region, FBtime, skill, pattern)
                    VALUES ("""+"\'"+self.__Id+"\'"+','+\
        "\'"+self.__judgeWinner(browser.find_element_by_css_selector("body > div.maxtopbar > div.maxtopmainbar > div:nth-child(2) > div > div.new-box > table > tbody > tr > td > span > font").text)+"\'"+','+\
        "\'"+browser.find_element_by_css_selector("body > div.maxtopbar > div.main-shadow-box > div.main-container > div.container.xuning-box > table.match-detail-info.new-box > tbody > tr:nth-child(2) > td:nth-child(3)").text+"\'"+','+\
        "\'"+browser.find_element_by_css_selector("body > div.maxtopbar > div.main-shadow-box > div.main-container > div.container.xuning-box > table.match-detail-info.new-box > tbody > tr:nth-child(2) > td:nth-child(4)").text+"\'"+','+\
        "\'"+browser.find_element_by_css_selector("body > div.maxtopbar > div.main-shadow-box > div.main-container > div.container.xuning-box > table.match-detail-info.new-box > tbody > tr:nth-child(2) > td:nth-child(5)").text+"\'"+','+\
        "\'"+browser.find_element_by_css_selector("body > div.maxtopbar > div.main-shadow-box > div.main-container > div.container.xuning-box > table.match-detail-info.new-box > tbody > tr:nth-child(2) > td:nth-child(6) > font").text+"\'"+','+\
        "\'"+mode+"\'"+')'
        try:
            cursor.execute(sql)  # 执行sql语句
            db.commit()  # 提交到数据库执行
        except:
            db.rollback()  # 如果发生错误则回滚
        db.close()  # 关闭数据库连接

    def crawlCnRank_gen(self):
        browser = self.__browser
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="123456",
            database="cnrank",
            charset="utf8")
        cursor = db.cursor()
        table = browser.find_element_by_css_selector(
            "body > div.maxtopbar > div.main-shadow-box > div.main-container > div.container.xuning-box > div:nth-child(2)"
        ).find_elements_by_tag_name("table")
        anonym = 0
        pattern1 = re.compile(r"detail/(\w+)")
        pattern2 = re.compile(r"hphover/(\w+)_hphover.png")
        for i in range(1, 11):
            if i < 6:
                camp = "radiant"
                tableNum = 0
            else:
                camp = "dire"
                tableNum = 1
                i -= 5
            ggamer = table[tableNum].find_element_by_css_selector(
                "tbody > tr:nth-child(" + str(i) +
                ") > td:nth-child(2) > a").text
            if "匿名玩家" in ggamer:
                gamer = 'anonym' + str(anonym)
                gamerId = 'none' + str(anonym)
                anonym += 1
            else:
                gamer = ggamer
                gamerId = pattern1.findall(
                    table[tableNum].find_element_by_css_selector(
                        "tbody > tr:nth-child(" + str(i) +
                        ") > td:nth-child(2) > a").get_attribute('href'))[0]
                #                                      3    4      5        6        7       8       9        10          11          12    13
            sql =   """REPLACE INTO GEN(Id, camp, gamerid, gamer, IdAndGamer, hero, KDA, frate, perdamage, damage, lastHit, expMin , goldMin, buildingDamage, heal, goods)
                        VALUES ("""+"\'"+self.__Id+"\'"+','+"\'"+camp+"\'"+','+\
            "\'"+gamerId+"\'"+','+\
            "\'"+gamer+"\'"+','+\
            "\'"+self.__Id+"+"+gamerId+"\'"+','+\
            "\'"+pattern2.findall(table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(3) > a > img").get_attribute('src'))[0]+"\'"+','+\
            "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(4)").text+"\'"+','+\
            "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(5)").text+"\'"+','+\
            "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(6)").text+"\'"+','+\
            "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(7)").text+"\'"+','+\
            "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(8)").text+"\'"+','+\
            "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(9)").text+"\'"+','+\
            "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(10)").text+"\'"+','+\
            "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(11)").text+"\'"+','+\
            "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(12)").text+"\'"+','+\
            "\'"+self.__eqListToJson(table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(13)"))+"\'"+")"
            # print(sql)
            try:
                cursor.execute(sql)  # 执行sql语句
                db.commit()  # 提交到数据库执行
            except:
                db.rollback()  # 如果发生错误则回滚
        db.close()  # 关闭数据库连接

    def __details(self):
        browser = self.__browser
        browser.find_elements_by_css_selector(
            "body > div.maxtopbar > div.main-shadow-box > div.main-container > div.rep_nav > ul > a"
            )
        # for i in detailsLinks:
        #     print(i.get_attribute("href"))
        # return

        browser.find_elements_by_css_selector(
            "body > div.maxtopbar > div.main-shadow-box > div.main-container > div.rep_nav > ul > a"
            )[1].click()     # 出装顺序
        db = pymysql.connect(
            host="localhost",
            user="root",
            password="123456",
            database="cnrank",
            charset="utf8")
        cursor = db.cursor()
        pattern = re.compile(r"detail/(\w+)/")
        pattern1 = re.compile(r"detail/(\w+)")
        divList = browser.find_elements_by_css_selector(
            "body > div.maxtopbar > div.main-shadow-box > div.main-container > div.main-container > div.rep-build-box > div"
        )
        anonym = 0
        for i in divList:   #遍历每个玩家
            eqDict = {}
            # print(i.get_attribute("id"))
            try:
                gamerId=pattern1.findall(
                    i.find_element_by_tag_name("div"
                    ).find_element_by_css_selector("div.build-eqid"
                    ).find_element_by_css_selector("a"
                    ).get_attribute("href")
                    )[0]
            except TypeError:
                gamerId = 'none' + str(anonym)
                anonym += 1
            # print(gamerId)
            j = i.find_elements_by_css_selector(
                "div.equipment > div"
                )
                # .find_elements_by_css_selector("div")
            for k in j:     #遍历出装
                eqTime = k.find_element_by_css_selector(".item-equipment-time").text
                eq = pattern.findall(k.find_element_by_css_selector("a").get_attribute('href'))[0]
                if eqTime not in eqDict:
                    eqDict[eqTime]=[eq]
                else:
                    eqDict[eqTime].append(eq)
                # print(json.dumps(eqDict))
            sql =   """REPLACE INTO GOODSDETAILS(IdAndGamer,goodsOrder)
                        VALUES ("""+"\'"+self.__Id+"+"+gamerId+"\'"+','+\
            "\'"+json.dumps(eqDict)+"\'"+')'
            # print(sql)
            try:
                cursor.execute(sql)  # 执行sql语句
                db.commit()  # 提交到数据库执行
            except:
                db.rollback()  # 如果发生错误则回滚

        browser.find_elements_by_css_selector(
            "body > div.maxtopbar > div.main-shadow-box > div.main-container > div.rep_nav > ul > a"
            )[6].click()     # 操作
        tables=browser.find_elements_by_css_selector(
            "body > div.maxtopbar > div.main-shadow-box > div.main-container > div.maxtopbar1 > div > div > div:nth-child(1) > table"
            )
        anonym = 0
        for tbody in tables:
            trs=tbody.find_elements_by_css_selector("tbody > tr")
            for tr in trs:   #遍历每个玩家
                tds=tr.find_elements_by_css_selector("tr > td")
                opDs=[]
                try:
                    gamerId=pattern1.findall(tds[0].find_element_by_css_selector(
                    "td > a"
                    ).get_attribute("href"))[0]
                except TypeError:
                    gamerId = 'none' + str(anonym)
                    anonym += 1
                for td in tds[3:]:
                    opDs.append(td.text)
                sql =   """REPLACE INTO OPDETAILS(IdAndGamer,operation)
                            VALUES ("""+"\'"+self.__Id+"+"+gamerId+"\'"+','+\
                "\'"+json.dumps(opDs)+"\'"+')'
                # print(sql)
                try:
                    cursor.execute(sql)  # 执行sql语句
                    db.commit()  # 提交到数据库执行
                except:
                    db.rollback()  # 如果发生错误则回滚

        # 物品使用次数        
        tbodyEqFq=browser.find_elements_by_css_selector("#List1 > div > table > tbody > tr") 
        anonym = 0
        for tr in tbodyEqFq:   #遍历每个玩家
            fqDivs=tr.find_elements_by_css_selector("tr > td.reprunes-border > div > div")
            eqFqDict={}
            try:
                gamerId=pattern1.findall(tr.find_element_by_css_selector(
                "tr > td:nth-child(2) > div > a"
                ).get_attribute("href"))[0]
            except TypeError:
                gamerId = 'none' + str(anonym)
                anonym += 1
            for fqDiv in fqDivs:
                eq=pattern1.findall(fqDiv.find_element_by_css_selector("div > div:nth-child(1) > a").get_attribute("href"))[0]
                eqFq=fqDiv.find_element_by_css_selector("div > div:nth-child(2)").text
                eqFqDict[eq]=eqFq
            sql =   "UPDATE GOODSDETAILS SET goodsTimes="+\
            "\'"+json.dumps(eqFqDict)+"\'"+\
            " WHERE IdAndGamer="+\
            "\'"+self.__Id+"+"+gamerId+"\'"
            # print(sql)
            try:
                cursor.execute(sql)  # 执行sql语句
                db.commit()  # 提交到数据库执行
            except:
                db.rollback()  # 如果发生错误则回滚

        db.close()  # 关闭数据库连接

    def __jump(self):
        browser = self.__browser
        if self.addOrSub:
            self.__Id = str(self.__initId + self.alter)
        else:
            self.__Id = str(self.__initId - self.alter)
            self.alter += 1
        browser.get(self.__url + self.__Id)
        # print(self.__Id)
        self.addOrSub = not self.addOrSub

    def runCraw(self):
        for _ in range(0, 20000):
            if random.randint(0, 200)==125:
                time.sleep(random.uniform(12.12, 20.11))
            try:
                mode = self.__browser.find_element_by_css_selector(
                    "body > div.maxtopbar > div.main-shadow-box > div.main-container > div.container.xuning-box > table.match-detail-info.new-box > tbody > tr:nth-child(2) > td:nth-child(7)"
                ).text
                if ("solo" in mode) or ("Solo" in mode) or ("单排" in mode):
                    print(self.__Id + " mode pass")
                else:
                    self.crawlCnRank_head()
                    self.crawlCnRank_gen()
                    try:
                        self.__details()
                    except:
                        print("no details")
                    print(self.__Id + " done")
            except:
                print(self.__Id + " except")
            finally:
                self.__jump()
                time.sleep(random.uniform(1.11, 4.11))

    def __test__(self):
        self.__details()
        print("test done")

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

# cookies_num = random.randint(0, len(r.keys()) - 1)  #随机选个cookies
cookies_num = 0  #选指定cookies
cookies = eval(r[r.keys()[cookies_num]])

browser.get("http://dotamax.com/")
for i in cookies:
    browser.add_cookie(cookie_dict=i)
time.sleep(3)
# url="http://dotamax.com/match/detail/3797013964"
# url="http://dotamax.com/match/detail/4210022726"
# url="http://dotamax.com/match/detail/4212872401"
# url="http://dotamax.com/match/detail/4216654992"  #details匿名
# url="http://dotamax.com/match/detail/1654973853"  #solo
# craw = crawCnRank(browser, 4210022726)
craw = crawCnRank(browser, 3797013964)
craw.runCraw()
# craw.__test__()

#

# input=browser.find_element_by_id('kw')
# input.send_keys('python')
# input.send_keys(Keys.ENTER)
# wait=WebDriverWait(browser,10)
# wait.until(EC.presence_of_all_elements_located((By.ID,'content_left')))
# print(browser.current_url)

# time.sleep(100)
# browser.close()
