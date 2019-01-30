import io
import json
import random
import sys
import time
import xlwt

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, encoding='utf-8')  # 改变标准输出的默认编码


class Craw:
    def __init__(self, browser, url, keyword):
        self.__browser = browser
        self.__url = url
        browser.get(self.__url)  # 工作页面
        self.keyword = keyword

    def __prepare(self):
        browser = self.__browser
        WebDriverWait(browser, 10).until(
            lambda browser: browser.find_element_by_id("code_suggest"))
        browser.find_element_by_id("code_suggest").send_keys(
            self.keyword, Keys.ENTER)
        # print("handles ",str(browser.window_handles))
        # print(browser.title)
        browser.switch_to.window(browser.window_handles[-1])
        # print(browser.title)
        WebDriverWait(browser, 20).until(
            lambda browser: browser.find_element_by_css_selector("div.module.module-share-list > div > table > tbody > tr:nth-child(1)")
        )
        browser.find_element_by_css_selector(
            "div.module.module-share-list > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > a"
        ).click()
        browser.switch_to.window(browser.window_handles[-1])
        WebDriverWait(browser, 10).until(
            lambda browser: browser.find_element_by_css_selector("body > div:nth-child(13) > div.hqrls > div:nth-child(1) > a:nth-child(9)")
        )  #等财务分析
        browser.find_element_by_css_selector(
            "body > div:nth-child(13) > div.hqrls > div:nth-child(1) > a:nth-child(9)"
        ).click()  #点财务分析
        browser.switch_to.window(browser.window_handles[-1])

    def crawTheBalanceSheet(self):
        browser = self.__browser
        excel = xlwt.Workbook(encoding='utf-8', style_compression=0)

        sheet1 = excel.add_sheet('reportPeriod ', cell_overwrite_ok=True)
        page = 0
        #第一格
        WebDriverWait(browser, 10).until(
            lambda browser: browser.find_element_by_css_selector("#report_zcfzb > tbody > tr:nth-child(1) > th:nth-child(1)")
        )  #等
        sheet1.write(
            0, 0,
            browser.find_element_by_css_selector(
                "#report_zcfzb > tbody > tr:nth-child(1) > th:nth-child(1)").
            text)

        browser.execute_script(r'$("#report_zcfzb > tbody > tr").show()')
        trs = browser.find_elements_by_css_selector(
            "#report_zcfzb > tbody > tr")
        #第一列[1:]
        for i, tr in enumerate(trs[1:], 1):
            head = tr.find_element_by_tag_name("td")
            sheet1.write(i, 0, head.text)

        while page<100:
            trs = browser.find_elements_by_css_selector(
                "#report_zcfzb > tbody > tr")
            judgeAjax = browser.find_element_by_css_selector(
                "#report_zcfzb > tbody > tr:nth-child(1) > th:nth-child(2)"
            ).text
            #第一行[1:]
            line = 1 + page * 5
            for th in trs[0].find_elements_by_tag_name("th")[1:]:
                sheet1.write(0, line, th.text)
                line += 1
            row = 1

            #其他行[1:]
            for tr in trs[1:]:
                line = 1 + page * 5
                for td in tr.find_elements_by_tag_name("td")[1:]:
                    sheet1.write(row, line, td.text)
                    line += 1
                row += 1

            if "none" in browser.find_element_by_css_selector(
                    "#zcfzb_next").get_attribute("style"):
                break
            WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable( (By.CSS_SELECTOR,"#zcfzb_next") )
            )  #等可被点击
            browser.find_element_by_css_selector("#zcfzb_next").click()
            WebDriverWait(browser, 10).until(
                lambda browser: judgeAjax != browser.find_element_by_css_selector("#report_zcfzb > tbody > tr:nth-child(1) > th:nth-child(2)").text
            )  #等加载
            browser.execute_script(r'$("#report_zcfzb > tbody > tr").show()')
            page += 1

        excel.save(r'd:\theBalanceSheet.xls')

    def runCraw(self):
        try:
            self.__prepare()
        except:
            print(self.keyword + " except")
        finally:
            time.sleep(random.uniform(1.11, 4.11))

    def __test__(self):
        self.__prepare()
        self.crawTheBalanceSheet()
        print("test done")


browser = webdriver.Chrome()
craw = Craw(browser, "http://www.eastmoney.com/", "万科")
# craw.runCraw()
craw.__test__()
