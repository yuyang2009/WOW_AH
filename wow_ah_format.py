#-*- coding: UTF-8 -*-
import urllib
import os
import sys
import json
import time
import datetime
import winsound
import pandas as pd
from collections import namedtuple

auc_url = "http://auction-api-cn.worldofwarcraft.com/auction-data/d9f2775ea6440077e5de6749fc37d81e/auctions.json"
snap_url = "https://wowtoken.info/snapshot.json"
report_list = [u"物品名称", u"最低价格", u"数量", u"我的价格"]
item = namedtuple('item', ['id', 'name', 'low', 'high'])
row_format = u"{:<20}" * (len(report_list))
bn_id = u"道亦有盗"

app_path = sys.path[0]
file_name = "item_list.txt"
file_path = os.path.join(app_path, file_name)
alter_flag = False
report_flag = True

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
            print u"拍卖行API不可用"

    except:
        pass

def get_snapshot():
    try:
        resp = urllib.urlopen(snap_url)
        if resp.code == 200:
            #resp_json = json.load(resp)
            resp_json = json.loads(resp.read())
            snap_cn_json = resp_json.get('CN').get('formatted')
            return snap_cn_json['buy'], snap_cn_json['updated']
        else:
            print u"时光徽章API不可用"
    except:
        pass

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

def report(item, df):
    name = item.name.decode("utf8")
    df.loc[:, 'unit_price'] = df.loc[:, 'buyout'] / df.loc[:, 'quantity'] / 10000
    low = df['unit_price'].min()
    quantity = df.loc[df['unit_price'] == low]['quantity'].sum()
    my_price = df.loc[df['owner'] == bn_id]['unit_price'].mean()
    alter_low = item.low
    alter_high = item.high
    if alter_low.strip() and low<int(alter_low) or alter_high.strip() and low>int(alter_high):
        print '\033[32m', row_format.format(name, low, quantity, my_price), '\033[0m'
        global alter_flag
        alter_flag = True
    else:
        print row_format.format(name, low, quantity, my_price)


if __name__ == '__main__':
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    items = get_items()
    if len(items) == 0:
        print u"监视列表为空！"
    pd.options.mode.chained_assignment = None

    snap_updated = ''
    auc_lenth = 0
    while True:
        alter_flag = False
        report_flag = True
        snap_cn_buy, time_updated = get_snapshot()
        time_now = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        auc_df = get_auc()
        #Comparisons to singletons like None should always be done with is or is not, never the equality operators.
        #用 is 或者 is not 来判断对象是否为空
        if not snap_updated or time_updated is not None and snap_updated!=time_updated:
            print u"当前时间: %s" %time_now
            print '\033[32m', u"时光徽章: %s\t" %snap_cn_buy, u"更新时间: %s " %time_updated, '\033[0m'

        #循环中存在auc_df为 NoneType 错误，可能为resp.read()读取失败，也可能是urlopen失败
        elif auc_lenth==0 or auc_df is not None and auc_lenth!=len(auc_df):
            print u"当前时间: %s" %time_now
            print u"时光徽章: %s\t" %snap_cn_buy, u"更新时间: %s " %time_updated
        else:
            report_flag = False
            continue
        auc_lenth = len(auc_df)
        snap_updated = time_updated

        print "* " *40
        report_df = pd.DataFrame(columns = report_list)
        print row_format.format(*report_list)
        for item in items:
            if item.id:
                df = auc_df.loc[auc_df['item'] == int(item.id)]
                report(item, df)
        print "* " *40, "\n"
        if alter_flag:
            winsound.Beep(300,2000)
        time.sleep(20)
