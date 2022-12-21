import makeKeras
import os
from hbaseUtils import HbaseUtils

if __name__ == '__main__':
    if not os.path.exists('./datas'):
        os.mkdir('./datas')

    hbase_utils = HbaseUtils(host="192.168.0.144", port=9090, size=5)
    scanner = hbase_utils.read_scan('bigdata_collection_list', filter="SingleColumnValueFilter ('naver_news','collection_token',!=,'regexstring:None') OR SingleColumnValueFilter ('naver_blog','collection_token',!=,'regexstring:None')")
    makeKeras.start(scanner)
    print('keras done.')