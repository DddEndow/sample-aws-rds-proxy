import sys
import os
import boto3
import pymysql
import logging

logger = logging.getLogger(__name__)

RDS_PROXY_ENDPOINT = os.environ['RDS_PROXY_ENDPOINT']
RDS_PROXY_PORT = os.environ['RDS_PROXY_PORT']
RDS_USER = os.environ['RDS_USER']
REGION = os.environ['AWS_REGION']
DB_NAME = os.environ['DB_NAME']

rds = boto3.client('rds')


def lambda_handler(event, context):
    """ IAM認証でRDS Proxy経由でRDSからデータを取得する。
    https://docs.aws.amazon.com/ja_jp/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.Connecting.Python.html

    TLS/SSLに関しては以下のURLを参照
    https://docs.aws.amazon.com/ja_jp/AmazonRDS/latest/UserGuide/rds-proxy.html#rds-proxy-security.tls
    """
    password = rds.generate_db_auth_token(
        DBHostname=RDS_PROXY_ENDPOINT,
        Port=RDS_PROXY_PORT,
        DBUsername=RDS_USER,
        Region=REGION
    )

    try:
        conn = pymysql.connect(
            host=RDS_PROXY_ENDPOINT,
            user=RDS_USER,
            passwd=password,
            db=DB_NAME,
            connect_timeout=5,
            cursorclass=pymysql.cursors.DictCursor,
            ssl={'ca': 'AmazonRootCA1.pem'}
        )
    except Exception as e:
        logger.error("不明なエラーが発生しました。")
        logger.error(e)
        sys.exit()

    with conn.cursor() as cur:
        cur.execute('SELECT id, name FROM users;')
        results = cur.fetchall()

    return results
