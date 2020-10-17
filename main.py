import requests
from requests.exceptions import Timeout
import datetime
import atexit
import time
import re
import os
import textwrap

webhook_keys = os.environ["WEBHOOK_KEY"]

p = re.compile(r"<[^>]*?>")

target_url = "http://61.205.203.82/i"
trigger_url = "https://maker.ifttt.com/trigger/tweet/with/key/{}".format(webhook_keys)
error_url = "https://maker.ifttt.com/trigger/error/with/key/{}".format(webhook_keys)

dt_now_jst_aware = datetime.datetime.now(
    datetime.timezone(datetime.timedelta(hours=9))
)


def on_error():
    requests.post(error_url)


atexit.register(on_error)

prev_page = requests.get(target_url)
print('Current Page\n{}'.format(p.sub("", prev_page.text)))

prev_etag = prev_page.headers["ETag"]

while True:
    time.sleep(30)
    try:
        current_page = requests.get(target_url, headers={"If-None-Match": prev_etag})
    except Timeout:
        print(str(dt_now_jst_aware) + ' Timeout Error!')
        continue

    if current_page.status_code == 200:
        print("Page Modified!")
        prev_etag = current_page.headers['ETag']

        if 'お知らせはありません' in current_page.text:
            print("Back to Normal")
        else:
            print("An Incident Occurred")
            value1 = '{0}...'.format(textwrap.wrap('登校情報が更新されました。\n' + p.sub("", current_page.text), 130)[0])
            print(value1)
            payload = {'value1': value1}
            requests.post(trigger_url, params=payload)
