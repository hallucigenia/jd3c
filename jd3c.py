import json
import argparse
import time
import re
import requests
import pymongo
import numpy
import pandas
from lxml import etree
from wordcloud import WordCloud
import matplotlib.pyplot

DB = "notebook"

def fix_url(string):
    if re.match(r"http://", string):
        return string
    if re.match(r"//", string):
        return "http" + string

def get_page_num():
    url = "https://list.jd.com/list.html?cat=670,671,672"
    r = requests.get(url, verify=False)
    content = r.content
    root = etree.HTML(content)
    page_nodes = root.xpath('.//span[@class="p-num"]/a')
    for node in page_nodes:
        if node.attrib["class"] == "":
            page_num = int(node.text)
            return page_num

def get_price(skuid):
    url = "https://c0.3.cn/stock?skuId=" + str(skuid) +  "&area=1_72_4137_0&venderId=1000004123&cat=9987,653,655&buyNum=1&choseSuitSkuIds=&extraParam={%22originid%22:%221%22}&ch=1&fqsp=0&pduid=15379228074621272760279&pdpin=&detailedAdd=null&callback=jQuery3285040"
    r = requests.get(url, verify=False)
    content = r.content.decode('GBK')
    matched = re.search(r'jQuery\d+\((.*)\)', content, re.M)
    if matched:
        data = json.loads(matched.group(1))
        price = float(data["stock"]["jdPrice"]["p"])
        return price
    return 0

def get_item(skuid, url):
    price = get_price(skuid)
    r = requests.get(url, verify=False)
    content = r.content
    root = etree.HTML(content)
    nodes = root.xpath('.//div[@class="Ptable"]/div[@class="Ptable-item"')
    params = {"price": price, "skuid": skuid}
    for node in nodes:
        text_nodes = node.xpath('./dl')[0]
        k = ""
        v = ""
        for text_node in text_nodes:
            if text_node.tag == "dt":
                k = text_node.text
            elif text_node.tag == "dd" and "class" not in text_node.attrib:
                v = text_node.text
                params[k] = v
    return params

def get_laptop(page):
    url = "https://list.jd.com/list.html?cat=9987,653,655&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0&ms=4#J_main".format(page)
    r = requests.get(url, verify=False)
    content = r.content.decode("utf-8")
    root = etree.HTML(content)
    cell_nodes = root.xpath('.//div[@class="-
