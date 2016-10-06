#-*- coding: UTF-8 -*-
import urllib
from os import path
import sys
import json
import time
import winsound
import unicodedata
import pandas as pd
from collections import namedtuple

auc_url = "http://auction-api-cn.worldofwarcraft.com/auction-data/d9f2775ea6440077e5de6749fc37d81e/auctions.json"
snap_url = "https://wowtoken.info/snapshot.json"

report_list = [u"物品名称", u"最低价格", u"数量", u"我的价格"]
item = namedtuple('item', ['id', 'name', 'low', 'high'])
row_format = u"{:<{}}" * (len(report_list))
cutoff_line = u"* "*30
ft_color = ['37', '36']
width = 15

bn_id = u"道亦有盗"
app_path = path.abspath(sys.path[0])
#app_path = path.abspath(path)
file_name = "item_list.txt"
file_path = path.join(app_path, file_name)

def calc_width(target, text):
    return target - sum(unicodedata.east_asian_width(c) in 'WF' for c in text)

def insert_width(list, width):
    ret_list = []
    for s in list:
        ret_list.append(s)
        ret_list.append(calc_width(width, s))
    return ret_list

def get_auc():
    try:
        resp = urllib.urlopen(auc_url)
        if resp.code == 200:
            #resp_json = json.load(resp)
            resp_json = json.loads(resp.read())
            auc_json = resp_json.get('auctions')
            auc_df = pd.DataFrame(auc_json)
            return auc_df
        else:
            print '\033[31m', u"%s: 拍卖行API不可用" %time.ctime(), '\033[0m'
            return None

    except:
        # print u"当前时间：%s" %time.ctime()
        # print '\033[31m', u"拍卖行API异常", '\033[0m'
        # print cutoff_line, "\n"
        print '\033[31m', u"%s: 拍卖行API异常" %time.ctime(), '\033[0m'
        return None

def get_snapshot():
    try:
        resp = urllib.urlopen(snap_url)
        if resp.code == 200:
            #resp_json = json.load(resp)
            resp_json = json.loads(resp.read())
            snap_cn_json = resp_json.get('CN').get('formatted')
            return snap_cn_json['buy'], snap_cn_json['updated']
        else:
            print '\033[31m', u"%s: 时光徽章API不可用" %time.ctime(), '\033[0m'
            return None, None
    except:
        print '\033[31m', u"%s: 时光徽章API异常" %time.ctime(), '\033[0m'

        return None, None


def get_items():
    items = []
    with open(file_path, 'r') as f_items:
        for line in f_items:
            if not line.isspace():
                splitted_line = line.strip('\n').split(',')
                temp = item._make(splitted_line)
                items.append(temp)
    f_items.close()
    return items

def report(items, auc_df):
    print u"当前时间：%s" %time.ctime()
    print u"时光徽章: %s\t" %snap_cn_buy, u"更新时间: %s " %time_updated
    print cutoff_line
    print '\033[37m', row_format.format(*insert_width(report_list, width)), '\033[0m'
    alter_flag = False
    color_flag = 1
    for item in items:
        if item.id:
            df = auc_df.loc[auc_df['item'] == int(item.id)]
            name = item.name.decode("utf8")
            df.loc[:, 'unit_price'] = df.loc[:, 'buyout'] / df.loc[:, 'quantity'] / 10000
            low = df['unit_price'].min()
            quantity = df.loc[df['unit_price'] == low]['quantity'].sum()
            my_price = df.loc[df['owner'] == bn_id]['unit_price'].mean()
            alter_low = item.low
            alter_high = item.high
            data_list = [name, str(low).decode('utf8'), str(quantity).decode('utf8'), str(my_price).decode('utf8')]
            if alter_low.strip() and low<int(alter_low) or alter_high.strip() and low>int(alter_high):
                print '\033[31m', row_format.format(*insert_width(data_list, width)), '\033[0m'
                alter_flag = True
            else:
                print '\033[%sm' %ft_color[color_flag], row_format.format(*insert_width(data_list, width)), '\033[0m'
            color_flag = (color_flag+1)%2
    print cutoff_line, "\n"
    if alter_flag:
        winsound.Beep(300,2000)

if __name__ == '__main__':
    items = get_items()
    if len(items) == 0:
        print u"监视列表为空！\n"
    pd.options.mode.chained_assignment = None

    snap_updated = ''
    auc_lenth = 0
    print '\033[32m', u"查询中……\n", '\033[0m'
    while True:
        #start = time.clock()

        snap_cn_buy, time_updated = get_snapshot()
        auc_df = get_auc()


        # now = time.ctime()
        # if auc_df is not None:
        #     print u'%s: 拍卖行物品数量为 %d \n' %(now, len(auc_df))
        # else:
        #     print u'拍卖行API异常\n'

        #Comparisons to singletons like None should always be done with is or is not, never the equality operators.
        #用 is 或者 is not 来判断对象是否为空
        if auc_df is not None and not snap_updated and auc_lenth==0:
            report(items, auc_df)
            auc_lenth = len(auc_df)
            snap_updated = time_updated
        #循环中存在auc_df为 NoneType 错误，可能为resp.read()读取失败，也可能是urlopen失败
        elif auc_df is not None and auc_lenth!=len(auc_df):
            report(items, auc_df)
            auc_lenth = len(auc_df)
        elif time_updated is not None and snap_updated!=time_updated:
            print u"当前时间：%s" %time.ctime()
            print '\033[32m', u"时光徽章: %s\t" %snap_cn_buy, u"更新时间: %s " %time_updated, '\033[0m'
            print cutoff_line, "\n"
            snap_updated = time_updated
        else:
            time.sleep(5)
            continue

        #auc_lenth = len(auc_df)
        #snap_updated = time_updated

        # end = time.clock()
        # print u'%s: 运行时间了 %d 秒\n' %(now, (end-start))
        time.sleep(5)
