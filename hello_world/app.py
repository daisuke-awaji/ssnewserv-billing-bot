# coding:utf-8
import json

import boto3
import logging
import datetime

import requests

SLACK_CHANNEL = 'robots'
# Slack Incoming Webhook URLを指定。
CHANNEL_URL  = "https://hooks.slack.com/services/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"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cost_exploler = boto3.client('ce')

def lambda_handler(event, context):
    start_time = datetime.date.today() - datetime.timedelta(days=1)
    end_time   = datetime.date.today()

    day_cost = get_cost(str(start_time), str(end_time))
    day_cost_msg = '本日の課金金額: ' + day_cost + ' USD'
    logger.info(day_cost_msg)

    dt = datetime.datetime.utcnow()
    first_day_of_the_month = dt.date() - datetime.timedelta(days=dt.day - 1)
    monthly_cost = get_cost(str(first_day_of_the_month), str(end_time))
    monthly_cost_msg = '今月の課金金額: ' + monthly_cost + ' USD'
    logger.info(monthly_cost_msg)

    requests.post(CHANNEL_URL, data=json.dumps({
        'text': day_cost_msg + '\n' + monthly_cost_msg,  # 通知内容
        'username': u'billing-bot'  # ユーザー名
    }))


def get_cost(start_time, end_time):
    response = cost_exploler.get_cost_and_usage(
        TimePeriod={
            'Start': start_time,
            'End': end_time
        },
        Granularity='MONTHLY',
        Metrics=[
            'UnblendedCost',
        ]
    )
    logger.info(response)
    results = response['ResultsByTime'][0]
    return results['Total']['UnblendedCost']['Amount']
