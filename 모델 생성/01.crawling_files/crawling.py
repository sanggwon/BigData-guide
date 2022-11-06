import multiprocessing
import os, csv
from boilerpipe.extract import Extractor
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from urllib.request import Request
from urllib.request import urlopen
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from functools import partial
from functools import wraps
from fake_useragent import UserAgent
import time
import logging

logger = logging.getLogger('ftpuploader')

# 언론사
newspaper = {'경향신문':'032','국민일보':'005','동아일보':'020','문화일보':'021','서울신문':'081','세계일보':'022','조선일보':'023', '중앙일보':'025', '한겨레':'028', '한국일보':'469'}
# 카테고리
theme_list = ['정치','경제','사회','생활/문화','세계','IT/과학','오피니언', '연예', '스포츠', '기타']
# 데이터 저장 경로
file_path = os.getcwd() + '/datas/'

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
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

# @retry((TimeoutError, URLError, HTTPError), tries=4, delay=15, backoff=2)
# def get_extractor(url) :
#     return Extractor(extractor='ArticleExtractor', url=url)

def page_crawling(news, idx):
    # 시작일,종료일 설정
    last = datetime.now()
    start = last - relativedelta(days=idx)
    link = {}
    # 언론사
    checked = newspaper[news]
    # while start < last:

    dates = start.strftime("%Y%m%d")
    # 하루 더하기
    start += timedelta(days=1)
    # 10페이지
    for i in range(1, 10):
        try :
            url = 'https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid='+checked+'&date='+dates+'&page='+str(i)
            webpage = get_link(url)
            soup = BeautifulSoup(webpage,"html.parser",from_encoding="utf-8-sig")
            ul_list = soup.find('div', {'class': 'list_body newsflash_body'}).findAll('ul')
            for ul in ul_list:
                for li in ul.findAll('li'):
                    href = li.find('dt').find('a').attrs['href']
                    ymd = datetime.strptime(dates, "%Y%m%d").strftime("%Y%m%d")
                    if ymd not in link:
                        link.update({ymd : []})
                    link[ymd].append(href)
            webpage.close()
        except :
            continue

    # 월별로 반복문
    for ymd in link:
        title, date_list, content, category, url_txt = ['제목'], ['날짜'], ['내용'], ['카테고리'], ['URL']
        # # 저장 경로
        ym_file_path = file_path + ymd[:-2]
        # 저장 경로
        ymd_file_path = ym_file_path + "/" + ymd

        try :
            # 폴더 만들기
            if not os.path.exists(ym_file_path):
                os.mkdir(ym_file_path)
                # time.sleep(180)
        except :
            pass
        try :
            if not os.path.exists(ymd_file_path):
                os.mkdir(ymd_file_path)
        except :
            pass

        # 반복문 soup
        for url in tqdm(link[ymd]):
            try:
                webpage = get_link(url)
                soup = BeautifulSoup(webpage,"html.parser",from_encoding="utf-8-sig")
                if soup is not None :
                    site = soup.find('meta', {'name': 'twitter:site'})
                    if site is not None :
                        content_attr = site.get_attribute_list('content')[0]
                        if '연예' in content_attr :
                            theme = '연예'
                        elif '스포츠' in content_attr :
                            theme = '스포츠'
                        elif '뉴스' in content_attr :
                            if soup.find('li', {'class': 'is_active'}) is not None :
                                theme = soup.find('li', {'class': 'is_active'}).find('span', {'class':'Nitem_link_menu'}).text
                            else :
                                theme = '기타'
                        else :
                            theme = '기타'
                    else :
                        site = soup.find('meta', {'property': 'og:article:author'})
                        if site is not None :
                            content_attr = site.get_attribute_list('content')[0]
                            if '스포츠' in content_attr :
                                theme = '스포츠'
                            else :
                                theme = '기타'
                        else :
                            theme = '기타'

                    extractor = Extractor(extractor='ArticleExtractor', html=str(soup.find('body')))

                    title_ = soup.find('title').text
                    content_ = str(extractor.getText())
                    date_ = ymd
                    idx = theme_list.index(theme)

                    #테마별
                    title.append(title_)
                    content.append(content_)
                    date_list.append(date_)
                    category.append(str(idx))
                    url_txt.append(url)

                else :
                    print(url)
                webpage.close()
            except Exception as e: # work on python 3.x
                continue

        with open(ymd_file_path + '/' + news + '.csv', 'w+', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            for cnt, i in enumerate(title):
                title_ = title[cnt]
                date_ = date_list[cnt]
                content_ = content[cnt]
                category_ = category[cnt]
                url_ = url_txt[cnt]
                writer.writerow((title_, date_, content_, category_, url_))
            f.truncate()
            f.close()
        
        # with open('count.txt', 'w+', encoding='cp949') as f:
        #     f.write(ymd)
        #     f.truncate()
        #     f.close()



def start(idx) :
    try :
        multiprocessing.freeze_support()
        pool = multiprocessing.Pool(10)
        pool.map(partial(page_crawling, idx=idx), newspaper)
        pool.close()
        pool.join()
    except:
        pass    

if __name__ == "__main__":

    if not os.path.exists(file_path):
        os.mkdir(file_path)

    while True :
        ymd = ''
        file = 'count.txt'
        if os.path.isfile(file):
            with open(file, 'r+', encoding='utf-8-sig') as f: 
                ymd = f.readlines()[0]

        num = 0
        if ymd != '' :
            now  = datetime.now()
            date_to_compare = datetime.strptime(ymd, "%Y%m%d")
            date_diff = now - date_to_compare
            num = date_diff.days

        for i in range(num, num+30) :
            ymd = datetime.now() - relativedelta(days=i)
            ymd = ymd.strftime("%Y%m%d")
            with open('count.txt', 'w+', encoding='utf-8-sig') as f:
                f.write(ymd)
                f.truncate()
                f.close()
            start(i)