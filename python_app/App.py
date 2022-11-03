import os
import logging.config
import sys
import asyncio
from datetime import datetime
from flask import Flask, request
from flask_cors import CORS
from Service import Service

app = Flask(__name__)
CORS(app)

@app.route('/favicon.ico')
def favicon():
    return ''

@app.route('/keyword/<keyword>', methods=['GET'])
def keyword(keyword):
    Service.init()
    return Service.keyword(keyword)

@app.route('/news', methods=['POST'])
def news():
    text = str(request.get_data(), encoding="cp949")
    return Service.text(text)

if  __name__ == '__main__':

    current_dir = os.path.dirname(os.path.realpath(__file__))
    log_dir = '{}/logs'.format(current_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%m-%d-%Y %H:%M:%S')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler('./logs/{:%Y-%m-%d}.log'.format(datetime.now()), encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    app.run(host='0.0.0.0', port=8084, debug=True) 