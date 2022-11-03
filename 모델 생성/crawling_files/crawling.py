import multiprocessing
import os, sys, csv
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

# 언론사
newspaper = {'경향신문':'032','국민일보':'005','동아일보':'020','문화일보':'021','서울신문':'081','세계일보':'022','조선일보':'023', '중앙일보':'025', '한겨레':'028', '한국일보':'469'}
# 카테고리
theme_list = ['정치','경제','사회','생활/문화','세계','IT/과학','오피니언']
# 데이터 저장 경로
file_path = os.getcwd() + '/crawling_files/datas/'

def page_crawling(news):
    # 시작일,종료일 설정
    last = datetime.now()
    start = last - relativedelta(months=1)
    link = {}
    # 언론사
    checked = newspaper[news]
    while start <= last:
        dates = start.strftime("%Y%m%d")
        # 하루 더하기
        start += timedelta(days=1)
        # 10페이지
        for i in range(1, 10):
            webpage = urlopen('https://news.naver.com/main/list.naver?mode=LPOD&mid=sec&oid='+checked+'&date='+dates+'&page='+str(i))
            soup = BeautifulSoup(webpage,"html.parser",from_encoding="utf-8-sig")
            ul_list = soup.find('div', {'class': 'list_body newsflash_body'}).findAll('ul')
            for ul in ul_list:
                for li in ul.findAll('li'):
                    href = li.find('dt').find('a').attrs['href']
                    ym = datetime.strptime(dates, "%Y%m%d").strftime("%Y%m")
                    if ym not in link:
                        link.update({ym : []})
                    link[ym].append(href)
    # 월별로 반복문
    for ym in link:
        title, date_list, content, category = ['제목'], ['날짜'], ['내용'], ['카테고리']
        # 저장 경로
        ym_file_path = file_path + ym
        # 폴더 만들기
        if not os.path.exists(ym_file_path):
            os.mkdir(ym_file_path)
        # 반복문 soup
        for url in tqdm(link[ym]):
            try:
                webpage = urlopen(url)
                soup = BeautifulSoup(webpage,"html.parser",from_encoding="utf-8-sig")
                title_ = soup.find('h2', {'class': 'media_end_head_headline'}).text.strip()
                content_ = soup.find('div', {'id': 'dic_area'}).text.strip()
                date_ = soup.find('span', {'class': 'media_end_head_info_datestamp_time'}).text.strip()
                theme = soup.find('li', {'class': 'is_active'}).find('span', {'class':'Nitem_link_menu'}).text
                idx = theme_list.index(theme)

                #테마별
                title.append(title_)
                content.append(content_)
                date_list.append(date_)
                category.append(str(idx))
            except:
                continue

        with open(ym_file_path + '/' + news + '.csv', 'w+', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            for cnt, i in enumerate(title):
                title_ = title[cnt]
                date_ = date_list[cnt]
                content_ = content[cnt]
                category_ = category[cnt]
                writer.writerow((title_, date_, content_, category_))
            f.truncate()
            f.close()

if __name__ == "__main__":
    if not os.path.exists(file_path):
        os.mkdir(file_path)

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    # pool = multiprocessing.Pool(5)
    pool.map(page_crawling,newspaper)
    pool.close()
    pool.join()

    sys.exit()