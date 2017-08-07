import re
import datetime
import traceback
from lxml import etree
from bs4 import BeautifulSoup
from scrapy.spiders import Spider
from scrapy.http import FormRequest


class GouBanJia(Spider):
    name = 'GouBanJia'

    def start_requests(self):
        now = datetime.datetime.now()
        now_str = datetime.datetime.strftime(now, '%Y/%m/%d %H:%M:%S')

        return [FormRequest(url='http://www.goubanjia.com/',
                            callback=self.parseDetail,
                            errback=self.errorParse,
                            headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'},
                            formdata={'URL':'http://www.goubanjia.com/',
                                  'Server':'iz28nzqrukyz',
                                  'Date':now_str})]

    def parseDetail(self, response):
        print "Enter parse"

        main_tags_list =[{'tag_name':'td', 'kwarg':{'class_':'ip'}}]
        save_tags_list = [{'tag_name':'div', 'kwarg':{'style':False}},
                          {'tag_name': 'p', 'kwarg': {'style': False}},
                          {'tag_name':'span', 'kwarg':{'style':False}}]

        html, status, msg = self.removeTags(response.text, main_tags_list, save_tags_list)

        raw_html = etree.HTML(html)
        
        ip_list = raw_html.xpath(".//td[@class='ip']")
        _ip_list = [''.join(e.xpath(".//text()")) for e in ip_list]
        _ip_list = [re.sub('\r|\n|\s|:', '', x) for x in _ip_list]
     
        next_pages_list = response.xpath(".//div[@class='wp-pagenavi']/a/@href").extract()
        _next_pages_list = [response.urljoin(x) for x in next_pages_list]

        for index, next_page_href in enumerate(_next_pages_list):
            now = datetime.datetime.now()
            now_str = datetime.datetime.strftime(now, '%Y/%m/%d %H:%M:%S')
            return [FormRequest(url=next_page_href,
                        callback=self.parseDetail,
                        errback=self.errorParse,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'},
                        formdata={'URL': 'http://www.goubanjia.com/',
                                  'Server': 'iz28nzqrukyz',
                                  'Date': now_str})]

    def errorParse(self, response):
        print 'error'

    def removeTags(self, html, main_tags_list, remove_tags_list):
        res_html = html
        status = True
        msg = 'done'
        try:
            html_bs = BeautifulSoup(html, 'lxml')
            _main_tags_list = self.handleTagsList(main_tags_list, html_bs)
            for main_tag in _main_tags_list:
                remove_tags = self.handleTagsList(remove_tags_list, main_tag)
                if remove_tags:
                    [tag.decompose() for tag in remove_tags]
            res_html = html_bs.prettify()
        except Exception as e:
            msg = 'err:{}, e:{}'.format(traceback.format_exc(), e)
            status = False
        finally:
            return res_html, status, msg

    def filterTags(self, html, main_tags_list, keep_tags_list):
        res_html = html
        status = True
        msg = 'done'
        try:
            html_bs = BeautifulSoup(html, 'lxml')
            _main_tags_list = self.handleTagsList(main_tags_list, html_bs)
            for main_tag in _main_tags_list:
                keep_tags = self.handleTagsList(keep_tags_list, main_tag)
                if keep_tags:
                    [tag.decompose() for tag in main_tag.find_all_next() if tag not in keep_tags]
            res_html = html_bs.prettify()
        except Exception as e:
            msg = 'err:{}, e:{}'.format(traceback.format_exc(), e)
            status = False
        finally:
            return res_html, status, msg

    def handleTagsList(self, tag_list, main_tag):
        try:
            res_list = []
            for tag in tag_list:
                kwarg = tag.get('kwarg', {})
                tag_pos = tag.get('tag_pos', '')
                tag_name = tag.get('tag_name', '')
                if not tag_name:
                    continue

                if tag_pos:
                    if kwarg:
                        find_res = main_tag.find_all(tag_name, **kwarg)[tag_pos]
                    else:
                        find_res = main_tag.find_all(tag_name)[tag_pos]
                    res_list.append(find_res)
                else:
                    if kwarg:
                        find_res = main_tag.find_all(tag_name, **kwarg)
                    else:
                        find_res = main_tag.find_all(tag_name)
                    res_list.extend(find_res) 
            return res_list
        except Exception as e:
            err_msg = traceback.format_exc()
            raise Exception(err_msg)