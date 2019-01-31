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
    def __init__(self, drive, url, keyword):
        self.__drive = drive
        self.__url = url
        drive.get(self.__url)  # 工作页面
        self.keyword = keyword

    def __prepare(self):
        drive = self.__drive
        WebDriverWait(
            drive,
            10).until(lambda drive: drive.find_element_by_id("code_suggest"))
        drive.find_element_by_id("code_suggest").send_keys(
            self.keyword, Keys.ENTER)
        # print("handles ",str(drive.window_handles))
        # print(drive.title)
        drive.switch_to.window(drive.window_handles[-1])
        # print(drive.title)
        WebDriverWait(drive, 20).until(
            lambda drive: drive.find_element_by_css_selector("div.module.module-share-list > div > table > tbody > tr:nth-child(1)")
        )
        drive.find_element_by_css_selector(
            "div.module.module-share-list > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > a"
        ).click()
        drive.switch_to.window(drive.window_handles[-1])
        WebDriverWait(drive, 10).until(
            lambda drive: drive.find_element_by_css_selector("body > div:nth-child(13) > div.hqrls > div:nth-child(1) > a:nth-child(9)")
        )  #等财务分析
        drive.find_element_by_css_selector(
            "body > div:nth-child(13) > div.hqrls > div:nth-child(1) > a:nth-child(9)"
        ).click()  #点财务分析
        drive.switch_to.window(drive.window_handles[-1])

    def crawSheet(self, excel, sheet, sheetId, nextId):
        drive = self.__drive
        page = 0
        #第一格
        WebDriverWait(drive, 10).until(
            lambda drive: drive.find_element_by_css_selector("#" + sheetId + " > tbody > tr:nth-child(1) > th:nth-child(1)")
        )  #等
        sheet.write(
            0, 0,
            drive.find_element_by_css_selector(
                "#" + sheetId +
                " > tbody > tr:nth-child(1) > th:nth-child(1)").text)

        drive.execute_script(r'$("#' + sheetId + r' > tbody > tr").show()')
        trs = drive.find_elements_by_css_selector("#" + sheetId +
                                                  " > tbody > tr")
        #第一列[1:]
        for i, tr in enumerate(trs[1:], 1):
            head = tr.find_element_by_tag_name("td")
            sheet.write(i, 0, head.text)

        while page < 100:
            trs = drive.find_elements_by_css_selector("#" + sheetId +
                                                      " > tbody > tr")
            judgeAjax = drive.find_element_by_css_selector(
                "#" + sheetId +
                " > tbody > tr:nth-child(1) > th:nth-child(2)").text
            #第一行[1:]
            line = 1 + page * 5
            for th in trs[0].find_elements_by_tag_name("th")[1:]:
                sheet.write(0, line, th.text)
                line += 1
            row = 1

            #其他行[1:]
            for tr in trs[1:]:
                line = 1 + page * 5
                for td in tr.find_elements_by_tag_name("td")[1:]:
                    sheet.write(row, line, td.text)
                    line += 1
                row += 1

            if "none" in drive.find_element_by_css_selector(
                    "#" + nextId).get_attribute("style"):
                break
            WebDriverWait(drive, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "#" + nextId)))  #等可被点击
            drive.find_element_by_css_selector("#" + nextId).click()
            try:
                WebDriverWait(drive, 15).until(
                    lambda drive: judgeAjax != drive.find_element_by_css_selector("#" + sheetId + " > tbody > tr:nth-child(1) > th:nth-child(2)").text
                )  #等加载
            except:
                print(judgeAjax)
                print(drive.find_element_by_css_selector("#" + sheetId + " > tbody > tr:nth-child(1) > th:nth-child(2)").text)
                sys.exit()
            drive.execute_script(r'$("#' + sheetId + r' > tbody > tr").show()')
            page += 1

    def crawTheBalanceSheet(self):
        try:
            drive = self.__drive
            excel = xlwt.Workbook(encoding='utf-8', style_compression=0)
            sheetId = "report_zcfzb"
            nextId = "zcfzb_next"
            lis = drive.find_elements_by_css_selector("#zcfzb_ul > li")

            for li in lis:
                if "none" in li.get_attribute("style"):
                    continue
                WebDriverWait(drive, 10).until( EC.element_to_be_clickable((By.CSS_SELECTOR,"#zcfzb_ul > li")) )  #等可被点击
                li.click()
                sheet = excel.add_sheet(li.text, cell_overwrite_ok=True)
                time.sleep(0.5)  #等加载
                self.crawSheet(excel, sheet, sheetId, nextId)
        except:
            print("except")
        finally:
            excel.save(r'd:\theBalanceSheet.xls')

    def crawProfitStatement(self):
        pass

    def crawCashFlowStatement(self):
        pass

    def runCraw(self):
        try:
            # self.__prepare()
            # i=input("哪个？\t")
            i = input(r'Press "y" to start.')
        except:
            # print(self.keyword + " except")
            print("except")
        finally:
            # if i=0:
            #     pass
            # elif expression:
            #     pass
            if i == "y":
                self.crawTheBalanceSheet()
                self.crawProfitStatement()
                self.crawCashFlowStatement()

            drive.execute_script(r'alert("Done.")')
            time.sleep(random.uniform(1.11, 4.11))

    def __test__(self):
        # self.__prepare()
        self.crawTheBalanceSheet()
        self.crawProfitStatement()
        self.crawCashFlowStatement()
        print("test done")


webdriver.Chrome().get("http://www.eastmoney.com/")
drive = webdriver.Chrome()
# http://f10.eastmoney.com/f10_v2/FinanceAnalysis.aspx?code=sz000002
craw = Craw(drive, input("粘贴网址："), "")
# craw.runCraw()
craw.__test__()
