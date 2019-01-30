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
    sys.stdout.buffer, encoding='utf-8')  # 改变标准输出的默认编码


class Craw:
    def __init__(self, browser, url):
        self.__browser = browser
        self.__url = url
        browser.get(self.__url)  # 工作页面
        self.keyWord="万科"

    def __prepare(self):
        self.__browser.find_element_by_id("code_suggest").send_keys(self.keyWord,Keys.ENTER)
        # print("handles ",str(self.__browser.window_handles))
        # print(self.__browser.title)
        self.__browser.switch_to.window(self.__browser.window_handles[-1])
        # print(self.__browser.title)
        self.__browser.find_element_by_css_selector(
            "div.module.module-share-list > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > a"
            ).click()
        self.__browser.switch_to.window(self.__browser.window_handles[-1])
        self.__browser.find_element_by_css_selector(
            "body > div:nth-child(13) > div.hqrls > div:nth-child(1) > a:nth-child(9)"
            ).click()
        self.__browser.switch_to.window(self.__browser.window_handles[-1])

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
            sql = """INSERT IGNORE INTO GEN(Id, camp, gamerid, gamer, IdAndGamer, hero, KDA, frate, perdamage, damage, lastHit, expMin , goldMin, buildingDamage, heal, goods)
                        VALUES ("""+"\'"+self.__Id+"\'"+','+"\'"+camp+"\'"+',' +\
                "\'"+gamerId+"\'"+',' +\
                "\'"+gamer+"\'"+',' +\
                "\'"+self.__Id+"+"+gamerId+"\'"+',' +\
                "\'"+pattern2.findall(table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(3) > a > img").get_attribute('src'))[0]+"\'"+',' +\
                "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(4)").text+"\'"+',' +\
                "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(5)").text+"\'"+',' +\
                "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(6)").text+"\'"+',' +\
                "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(7)").text+"\'"+',' +\
                "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(8)").text+"\'"+',' +\
                "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(9)").text+"\'"+',' +\
                "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(10)").text+"\'"+',' +\
                "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(11)").text+"\'"+',' +\
                "\'"+table[tableNum].find_element_by_css_selector("tbody > tr:nth-child("+str(i)+") > td:nth-child(12)").text+"\'"+',' +\
                "\'"+self.__eqListToJson(table[tableNum].find_element_by_css_selector(
                    "tbody > tr:nth-child("+str(i)+") > td:nth-child(13)"))+"\'"+")"
            # print(sql)
            try:
                cursor.execute(sql)  # 执行sql语句
                db.commit()  # 提交到数据库执行
            except:
                db.rollback()  # 如果发生错误则回滚
        db.close()  # 关闭数据库连接

    def runCraw(self):
        try:
            self.__prepare()
        except:
            print(self.keyWord + " except")
        finally:
            time.sleep(random.uniform(1.11, 4.11))

    def __test__(self):
        self.__prepare()
        print("test done")


browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)
craw = Craw(browser, "http://www.eastmoney.com/")
# craw.runCraw()
craw.__test__()

