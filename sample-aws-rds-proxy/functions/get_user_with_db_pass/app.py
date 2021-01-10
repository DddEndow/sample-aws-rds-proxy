import sys
import os
import boto3
from botocore.client import Config
import json
import pymysql
import logging

logger = logging.getLogger(__name__)

RDS_SECRET_NAME = os.environ['RDS_SECRET_NAME']
RDS_PROXY_ENDPOINT = os.environ['RDS_PROXY_ENDPOINT']
DB_NAME = os.environ['DB_NAME']


def lambda_handler(event, context):
    """ SecretsManagerに保存されたDBの認証情報を使用してRDSからデータを取得する。
    """
    try:
        config = Config(connect_timeout=5, retries={'max_attempts': 0})
        client = boto3.client(service_name='secretsmanager',
                              config=config)

        get_secret_value_response = client.get_secret_value(SecretId=RDS_SECRET_NAME)
    except Exception:
        logger.error("不明なエラーが発生しました。")
        raise

    rds_secret = json.loads(get_secret_value_response['SecretString'])


    try:
        conn = pymysql.connect(
            host=RDS_PROXY_ENDPOINT,
            user=rds_secret['username'],
            passwd=rds_secret['password'],
            db=DB_NAME,
            connect_timeout=5,
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        logger.error("不明なエラーが発生しました。")
        logger.error(e)
        sys.exit()

    with conn.cursor() as cur:
        cur.execute('SELECT id, name FROM users;')
        results = cur.fetchall()

    return results
