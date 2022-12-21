# -*- coding: utf-8 -*-

from newspaper import Article
import newspaper
import multiprocessing
from urllib.error import HTTPError, URLError
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from functools import wraps
from urllib.request import Request
from urllib.request import urlopen
import logging
import time
import traceback

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    logging.error(traceback.format_exc())
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry

@retry((TimeoutError, URLError, HTTPError), tries=4, delay=60, backoff=2)
def get_link(url) :
    ua=UserAgent()
    rxn_req = Request(url, headers={'User-Agent': ua.chrome})
    return urlopen(rxn_req)

webpage = get_link('https://section.blog.naver.com/BlogHome.naver?directoryNo=0&currentPage=1&groupId=0')
soup = BeautifulSoup(webpage,"html.parser",from_encoding="utf-8-sig")
addr_list = soup.select('div.list_post_article a.desc_inner')