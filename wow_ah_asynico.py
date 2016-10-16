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
    RealmUrls = list()
    with open(RealmUrlPath, 'r', encoding="utf8") as realm_file:
        for line in realm_file:
            Url_dic = line.decode("utf8").split()
            RealmUrls.append(Url_dic[1])
        return RealmUrls
    #print('\033[31m', u"%s: 服务器API文件不存在。\n" time.ctime(), '\033[0m')
    exit()

class AuctionHouse:
    def __init__(self, RealmUrlPath, max_tasks, max_tries, *, loop=None):
        self.RealmUrl = RealmUrlPath
        self.max_tasks = max_tasks
        self.max_tries = max_tries
        self.loop = loop or asyncio.get_event_loop()
        self.q = Queue(loop=self.loop)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.RealmUrls = getRealmUrl(RealmUrlPath)
        for Url in self.RealmUrls:
            self.q.put_nowait(Url)

    def close(self):
        """Close resources."""
        self.session.close()

    @asyncio.coroutine
    def fetch(self, url):
        """Fetch one URL."""
        tries = 0
        exception = None
        while tries < self.max_tries:
            try:
                response = yield from self.session.get(
                    url, allow_redirects=False)

                if tries > 1:
                    LOGGER.info('try %r for %r success', tries, url)

                break
            except aiohttp.ClientError as client_error:
                LOGGER.info('try %r for %r raised %r', tries, url, client_error)
                exception = client_error

            tries += 1
        else:
            # We never broke out of the loop: all tries failed.
            LOGGER.error('%r failed after %r tries',
                         url, self.max_tries)
            return

        try:
            #stat, links = yield from self.parse_links(response)
            resp_json = yield from response.json()
            auc_json = resp_json.get("auction")
            realm_json = resp_json.get("realms")
            LOGGER.info('服务器 %r 的拍卖行数据获取成功', realm_json)
        finally:
            yield from response.release()


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
