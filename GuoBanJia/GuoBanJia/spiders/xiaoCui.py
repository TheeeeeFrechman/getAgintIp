#!/bin/user/python
#encoding:utf-8

import os
import sys
from lxml import etree
import re
import datetime
import requests
import bs4
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf-8')


class Cui():
    name = "cui"
    def __init__(self):
        self.stat = 1
    def startUrl(self):
        now = datetime.datetime.now()
        now_str = datetime.datetime.strftime(now, '%Y/%m/%d %H:%M:%S')
        web = requests.get(url='http://www.infobidding.com/listAction.do?type=4&count=25',
                            headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'},
                            ).content
        
        return self.bsWeb(web)

    def bsWeb(self, web):
        html_list = {}
        web_b = BeautifulSoup(web, "lxml") #//*[@id="lxwm_td"]/table/tbody/tr[2]/td[2]/table[3]/tbody
        html = web_b.find_all(align="left")
        for key in html:
            bu = key.span
            buk = key.find(width="11%")
            plase = buk.font
            bukk = key.find(width="10%")
            time = bukk.font
            if None == bu:
                print "bu is none"
            else:
                base = "时间：" + time.text + "    区域：" + plase.text
                html_list[base] = bu.text 
        self.stat =self.stat + 1      
        return html_list

    def getNext(self):
        sta = []
        while 1:
            if 2 == self.stat:
                web = requests.get(url='http://www.infobidding.com/listAction.do?count=25&type=0&freeflg=&tradeid=',
                            headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'},
                            ).content
                sta.append(self.bsWeb(web))
                if 100 == self.stat:
                    break
            else:
                sta.append(self.startUrl())
                pass



tect = Cui()
#buff = tect.getNext()
buff = tect.startUrl()
fp = open("./cui.txt", 'w+')
#print buff
#fp.write(str(buff))
for key in buff:
    ll = key + buff[key]
    print ll
    fp.write(ll)
    fp.write('\n')
#print eval(buff)






