#-*- coding: UTF-8 -*-
import asyncio
import cgi
from collections import namedtuple
import logging
import re
import time

try:
    # Python 3.4.
    from asyncio import JoinableQueue as Queue
except ImportError:
    # Python 3.5.
    from asyncio import Queue

import aiohttp  # Install with "pip install aiohttp".

LOGGER = logging.getLogger(__name__)

def getRealmUrl(RealmUrlPath):
    app_log.info("start")
    RealmUrls = list()
    with open(RealmUrlPath) as realm_file:
        for line in realm_file:
            Url_dic = line.decode("utf8").split()
            RealmUrls.append(Url_dic[1])
        return RealmUrls
    print '\033[31m', u"%s: 服务器API文件不存在。\n" %time.ctime(), '\033[0m'
    exit()

class AuctionHouse:
    def __init__(self, RealmUrlPath, max_task, max_tries, *, loop=None):
        self.RealmUrl = RealmUrl
        self.max_task = max_task
        self.max_tries = max_tries
        self.loop = loop or asyncio.get_event_loop()
        self.q = Queue(loop=self.loop)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.RealmUrls = getRealmUrl(RealmUrlPath)
        for Url in RealmUrls:
            self.q.put_nowait(Url)
    
@asyncio.coroutine
    def work(self):
        """Process queue items forever."""
        try:
            while True:
                url = yield from self.q.get()
                yield from self.fetch(url)
                self.q.task_done()
                self.q.put_nowait(url)
        except asyncio.CancelledError:
            pass


    @asyncio.coroutine
    def Auction(self):
        workers = [asyncio.Task(self.work(), loop=self.loop)
                   for _ in range(self.max_tasks)]
        yield from self.q.join()
        for w in workers:
            w.cancel()






