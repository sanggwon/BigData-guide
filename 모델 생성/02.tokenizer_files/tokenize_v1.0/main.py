import multiprocessing
from tokenizer import Tokenizer
from hbaseUtils import HbaseUtils

def start(scanner) :
    try :
        multiprocessing.freeze_support()
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        pool.map(Tokenizer.tokenizer, scanner)
        pool.close()
        pool.join()
    except:
        pass

if __name__ == '__main__':
    hbase_utils = HbaseUtils(host="192.168.0.144", port=9090, size=5)
    scanner = hbase_utils.read_scan('bigdata_collection_list', filter="SingleColumnValueFilter ('naver_news','collection_token',=,'regexstring:None') OR SingleColumnValueFilter ('naver_blog','collection_token',=,'regexstring:None')")
    start(scanner)
    print('tokenizer done.')