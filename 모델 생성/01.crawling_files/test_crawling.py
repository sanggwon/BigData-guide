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
from newspaper import Article
import time
import logging

logger = logging.getLogger('ftpuploader')
# 데이터 저장 경로
file_path = os.getcwd() + '/datas/'

# 카테고리
theme_list = {
    '정치' : '100',
    '경제' : '101',
    '사회' : '102',
    '생활_문화' : '103',
    'IT_과학' : '105',
    '세계' : '104',
    '연예' : 'entertain',
    # '스포츠' : 'sports',
    # 'e소프츠' : 'game'
}
sub_theme_list = {
    '100' : {
        '대통령실' : '264',
        '국회_정당' : '265',
        '북한' : '268',
        '행정' : '266',
        '국방_외교' : '267',
        '정치일반' : '269'
    },
    '101' : {
        '금융' : '259',
        '증권' : '258',
        '산업_재계' : '261',
        '중기_벤처' : '771',
        '부동산' : '260',
        '글로벌경제' : '262',
        '생활경제' : '310',
        '경제 일반' : '263'
    },
    '102' : {
        '사건사고' : '249',
        '교육' : '250',
        '노동' : '251',
        '언론' : '254',
        '환경' : '252',
        '인권_복지' : '59b',
        '식품_의료' : '255',
        '지역' : '256',
        '인물' : '276',
        '사회 일반' : '257'
    },
    '103' : {
        '건강정보' : '241',
        '자동차_시승기' : '239',
        '도로_교통' : '240',
        '여행_레저' : '237',
        '음식_맛집' : '238',
        '패션_뷰티' : '376',
        '공연_전시' : '242',
        '책' : '243',
        '종교' : '244',
        '날씨' : '248',
        '생활_문화 일반' : '245'
    },
    '105' : {
        '모바일' : '731',
        '인터넷_SNS' : '226',
        '통신_뉴미디어' : '227',
        'IT 일반' : '230',
        '보안_해킹' : '732',
        '컴퓨터' : '283',
        '게임_리뷰' : '229',
        '과학 일반' : '228'
    },
    '104' : {
        '아시아_호주' : '231',
        '미국_중남미' : '232',
        '유럽' : '233',
        '중동_아프리카' : '234',
        '세계 일반' : '322'
    },
    'entertain' : {
        '연예가화제' : '221',
        '방송_TV' : '224',
        '드라마' : '225',
        '뮤직' : '7a5',
        '해외연예' : '309',
    },
    'sports' : {
        '야구' : 'kbaseball',
        '해외야구' : 'wbaseball',
        '축구' : 'kfootball',
        '해외축구' : 'wfootball',
        '농구' : 'basketball',
        '배구' : 'volleyball',
        '골프' : 'golf',
        '일반' : 'general',
    },
    'game' : {
        'lol' : 'League_of_Legends',
        'pubg' : 'Player_Unknowns_Battle_Grounds',
        'starcraft2' : 'Starcraft_II_Legacy_of_the_Void',
        'esports_general' : 'general'
    }
}

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

def get_page_url_list(url, date, class_name) :
    link = []
    for i in range(1, 10):
        try :
            _url = url + '&date=' + date + '&page=' + str(i)
            webpage = get_link(_url)
            soup = BeautifulSoup(webpage,"html.parser",from_encoding="utf-8-sig")
            addr_list = soup.select(class_name)
            for addr in addr_list:
                link.append(addr.attrs['href'])
            webpage.close()
        except Exception as e: # work on python 3.x
            print(e)
            continue
    return link
    
def get_url_list(url, date, class_name) :
    link = []
    try :
        _url = url + '&date=' + date
        webpage = get_link(_url)
        soup = BeautifulSoup(webpage,"html.parser",from_encoding="utf-8-sig")
        addr_list = soup.select(class_name)
        for addr in addr_list:
            link.append(addr.attrs['href'])
        webpage.close()
    except Exception as e: # work on python 3.x
        print(e)

    return link

def create_file(path, sub_theme, sub, date, links) : 
    # 폴더 만들기
    sub_theme_file_path = path + "/" + sub
    try :
        if not os.path.exists(sub_theme_file_path):
            os.mkdir(sub_theme_file_path)
    except Exception as e: # work on python 3.x
        print(e)
        pass

    ym_file_path = sub_theme_file_path + "/" + date[:-2]
    try :
        if not os.path.exists(ym_file_path):
            os.mkdir(ym_file_path)
    except Exception as e: # work on python 3.x
        print(e)
        pass

    _date, _content, _keywords, _summary, _category, _url = ['날짜'], ['본문'], ['키워드'], ['요약'], ['카테고리'], ['URL']

    for link in tqdm(links) :
        article = Article(link)
        article.download()
        article.html
        article.parse()
        article.nlp()

        #테마별
        _date.append(article.publish_date)
        _content.append(article.text)
        _keywords.append(article.keywords)
        _summary.append(article.summary)
        _category.append(sub_theme[sub])
        _url.append(link)

    with open(ym_file_path + '/' + date + '.csv', 'w+', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        for cnt, i in enumerate(_date):
            date_txt = _date[cnt]
            content_txt = _content[cnt]
            keywords_txt = _keywords[cnt]
            summary_txt = _summary[cnt]
            category_txt = _category[cnt]
            url_txt = _url[cnt]
            writer.writerow((date_txt, content_txt, keywords_txt, summary_txt, category_txt, url_txt))
        f.truncate()
        f.close()

def page_crawling(theme_name, idx):
    # 시작일,종료일 설정
    last = datetime.now()
    start = last - relativedelta(days=idx)

    # 카테고리
    theme = theme_list[theme_name]

    # 폴더 만들기
    theme_file_path = file_path + "/" + theme_name
    try :
        if not os.path.exists(theme_file_path):
            os.mkdir(theme_file_path)
    except Exception as e: # work on python 3.x
        print(e)
        pass

    sub_theme = sub_theme_list[theme]

    # 연예
    if theme.isalpha() :
        ori_url = 'https://' + theme + '.naver.com/'
        if theme == 'entertain' :
            for sub in sub_theme :
                url = ori_url + 'now?sid=' + sub_theme[sub]
                date = start.strftime("%Y-%m-%d")
                class_name = 'div.left_cont ul li div.tit_area a'
                links = get_page_url_list(url, date, class_name)
                create_file(theme_file_path, sub_theme, sub, date, links)
        elif theme == 'sports' :
            for sub in sub_theme :
                url = ori_url + sub_theme[sub] + '/news/index?isphoto=N'
                date = start.strftime("%Y%m%d")
                class_name = 'div.content ul li div.text a'
                links = get_page_url_list(url, date, class_name)
                create_file(theme_file_path, sub_theme, sub, date, links)
        elif theme == 'game' :
            for sub in sub_theme :
                url = url + 'esports/' + sub_theme[sub] + '/news/' + sub
                date = start.strftime("%Y-%m-%d")
                class_name = 'div.news_list_container__1L7tH ul li.news_card_item__2lh4o a'
                links = get_url_list(url, date, class_name)
                create_file(theme_file_path, sub_theme, sub, date, links)
    else :
        for sub in sub_theme :
            url = 'https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1='+ theme + '&sid2=' + sub_theme[sub]
            date = start.strftime("%Y%m%d")
            class_name = 'div.content ul li dt:not(.photo) a'
            links = get_page_url_list(url, date, class_name)
            create_file(theme_file_path, sub_theme, sub, date, links)
        
    ymd = datetime.now() - relativedelta(days=idx+1)
    ymd = ymd.strftime("%Y%m%d")
    with open('count.txt', 'w+', encoding='cp949') as f:
        f.write(ymd)
        f.truncate()
        f.close()

def start(idx) :
    try :
        multiprocessing.freeze_support()
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        pool.map(partial(page_crawling, idx=idx), theme_list)
        pool.close()
        pool.join()
    except Exception as e: # work on python 3.x
        print(e)
        pass    

if __name__ == "__main__":

    if not os.path.exists(file_path):
        os.mkdir(file_path)

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

    while True :
        start(num)
        num += 1