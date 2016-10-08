#-*- coding: UTF-8 -*-
import urllib
import contextlib
import sys
import json
import time
#import winsound
import logging
import unicodedata
import pandas as pd
from os import path
from collections import namedtuple

#auc_url = "http://auction-api-cn.worldofwarcraft.com/auction-data/d9f2775ea6440077e5de6749fc37d81e/auctions.json"
snap_url = "https://wowtoken.info/snapshot.json"
report_list = [u"物品名称", u"最低价格", u"数量", u"我的价格"]
item = namedtuple('item', ['id', 'name', 'low', 'high'])
row_format = u"{:<{}}" * (len(report_list))
cutoff_line = u"* "*30
ft_color = ['37', '36']
width = 15
timeout = 10
chunk_size = 1024
#RealmName = u"影牙要塞"
#bn_id = u"盗亦有道"

app_path = path.abspath(sys.path[0])
#app_path = path.abspath(path)
file_name = "item_list.txt"
file_path = path.join(app_path, file_name)
realmurls_name = "RealmUrl.txt"
realmurls_path = path.join(app_path, realmurls_name)
player_info_name = "Player_info.txt"
player_info_path = path.join(app_path, player_info_name)

def get_Player_info():
    logging.info("get_Player_info start")
    with open(player_info_path) as player_info_file:
        player_info_line = player_info_file.read()
        if player_info_line:
            player_info = player_info_line.decode('utf8').split(',')
            if len(player_info)==2:
                logging.info("get_Player_info end")
                return player_info[0].strip(), player_info[1].strip()
            else:
                print '\033[31m', u"%s: 玩家信息描述文件格式错误，请确认分隔符为英文逗号。\n" %time.ctime(), '\033[0m'
                exit()
        else:
            print '\033[31m', u"%s: 玩家信息描述文件不可用！\n" %time.ctime(), '\033[0m'
            exit()

def get_RealmAPI(RealmName):
    logging.info("RealmName start")
    with open(realmurls_path) as realm_file:
        for line in realm_file:
            API_dic = line.decode("utf8").split()
            if API_dic[0] == RealmName:
                logging.info("RealmName end")
                return API_dic[1]
            else:
                pass
        print '\033[31m', u"%s: 找不到对应服务器，请确认服务器名称（以合并后主服务器名称为准）。\n" %time.ctime(), '\033[0m'
        exit()

def get_items():
    logging.info("get_items start")
    items = []
    with open(file_path, 'r') as f_items:
        for line in f_items:
            if not line.isspace():
                splitted_line = line.decode("utf8").strip('\n').split(',')
                temp = item._make(splitted_line)
                items.append(temp)
    f_items.close()
    if items is not None and len(items) != 0:
        logging.info("get_items end")
        return items
    else:
        print '\033[31m', u"%s: 监视列表为空！\n" %time.ctime(), '\033[0m'
        exit()

def calc_width(target, text):
    return target - sum(unicodedata.east_asian_width(c) in 'WF' for c in text)

def insert_width(list, width):
    ret_list = []
    for s in list:
        ret_list.append(s)
        ret_list.append(calc_width(width, s))
    return ret_list

def get_auc():
    logging.info("get_auc start")
    with contextlib.closing(urllib.urlopen(auc_url)) as resp:
        logging.info(resp.code)
        try:
            resp_json = json.loads(resp.read())
            auc_json = resp_json.get('auctions')
            auc_df = pd.DataFrame(auc_json)
            logging.info("get_auc end")
            return auc_df
        except:
            #print '\033[31m', u"%s: 拍卖行数据读取失败\n" %time.ctime(), '\033[0m'
            logging.info('urllib error')
            return None

    # try:
    #     resp = urllib.urlopen(auc_url)
    #     #resp_json = json.load(resp)
    #     resp_json = json.loads(resp.read())
    #     auc_json = resp_json.get('auctions')
    #     auc_df = pd.DataFrame(auc_json)
    #     logging.info("get_auc end")
    #     resp.close()
    #     return auc_df

    # except:
    #     # print u"当前时间：%s" %time.ctime()
    #     # print '\033[31m', u"拍卖行API异常", '\033[0m'
    #     # print cutoff_line, "\n"
    #     print '\033[31m', u"%s: 拍卖行API异常\n" %time.ctime(), '\033[0m'
    #     logging.info("get_auc error")
    #     resp.close()
    #     return None

def get_snapshot():
    logging.info("get_snapshot start")
    with contextlib.closing(urllib.urlopen(snap_url)) as resp:
        logging.info(resp.code)
        try:
            resp_json = json.loads(resp.read())
            snap_cn_json = resp_json.get('CN').get('formatted')
            logging.info("get_snapshot end")
            return snap_cn_json['buy'], snap_cn_json['updated']
        except:
            #print '\033[31m', u"%s: 时光徽章读取失败\n" %time.ctime(), '\033[0m'
            logging.info('urllib error')
            return None, None
    # try:
    #     resp = urllib.urlopen(snap_url)
    #     #resp_json = json.load(resp)
    #     resp_json = json.loads(resp.read())
    #     snap_cn_json = resp_json.get('CN').get('formatted')
    #     logging.info("get_snapshot end")
    #     #return snap_cn_json['buy'], snap_cn_json['get_snapshot updated']
    #     #JSON api 修改
    #     if snap_cn_json['buy'] is None or snap_cn_json['updated'] is None:
    #         print '\033[31m', u"%s: 时光徽章API格式修改\n" %time.ctime(), '\033[0m'
    #         logging.info("snapshot format error")
    #     resp.close()
    #     return snap_cn_json['buy'], snap_cn_json['updated']
    # except:
    #     resp.close()
    #     print '\033[31m', u"%s: 时光徽章API异常\n" %time.ctime(), '\033[0m'
    #     logging.info("get_snapshot error")
    #     return None, None

def report(items, auc_df):
    logging.info("report start")
    print u"当前时间：%s" %time.ctime()
    print u"服务器名称：%s\t玩家ID：%s" %(RealmName, bn_id)
    print u"时光徽章: %s\t" %snap_cn_buy, u"更新时间: %s " %time_updated
    print cutoff_line
    print '\033[37m', row_format.format(*insert_width(report_list, width)), '\033[0m'
    alter_flag = False
    color_flag = 1
    for item in items:
        if item.id:
            df = auc_df.loc[auc_df['item'] == int(item.id)]
            #删除无一口价的物品
            df = df.loc[df['buyout'] != 0]
            name = item.name
            if name is not None and len(name)>7:
                name = name[:6] + u"..."
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
        #winsound.Beep(300,2000)
        pass
    logging.info("report end")

if __name__ == '__main__':
    #global RealmName, bn_id
    logging.basicConfig(filename='wow_ah.log', filemode='w', filemaxBytes=5 * 1024, level=logging.DEBUG, format='%(asctime)s - (%(lineno)d) - %(funcName)s - %(message)s')

    RealmName, bn_id = get_Player_info()
    auc_url = get_RealmAPI(RealmName)
    items = get_items()
    pd.options.mode.chained_assignment = None

    snap_updated = ''
    auc_lenth = 0
    print '\033[32m', u"查询中……\n", '\033[0m'
    while True:
        logging.info("查询开始")
        snap_cn_buy, time_updated = get_snapshot()
        auc_df = get_auc()

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
            pass

        #auc_lenth = len(auc_df)
        #snap_updated = time_updated

        # end = time.clock()
        # print u'%s: 运行时间了 %d 秒\n' %(now, (end-start))
        logging.info("查询结束")
        time.sleep(5)
