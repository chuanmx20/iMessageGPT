import sqlite3
import json
import yaml
import asyncio
import os
from openai_utils import get_answer_simple, openai

cfg = yaml.safe_load(open("config.yml"))
proxy_url = cfg["proxy_uri"]
db_path = cfg["db_path"]
api_key = cfg["api_key"]
white_list = cfg["white_list"]
print(','.join(white_list))
async def refresh_cfg(sleep):
    while True:
        global cfg
        cfg = yaml.safe_load(open("config.yml"))
        global db_path
        db_path = cfg["db_path"]
        global api_key
        api_key = cfg["api_key"]
        global white_list
        white_list = cfg["white_list"]
        await asyncio.sleep(sleep)

def read_messages_after(earliest_date):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    query = f"""SELECT guid, account, text, date FROM message
        JOIN handle ON message.handle_id = handle.ROWID
        WHERE handle.id IN ({','.join(['?']*len(white_list))}) AND is_from_me = 1 AND date > {earliest_date};
    """
    c.execute(query, white_list)
    rows = c.fetchall()

    conn.close()
    return rows

def update_db(func):
    def wrapper(*args, **kwargs):

        row = kwargs["row"]
        guid, account, text, date = row
        message = kwargs["message"]
        db = kwargs["db"]
        conn = sqlite3.connect(db)
        c = conn.cursor()
        query = "INSERT INTO message (guid, account, date, message, reply) VALUES (?, ?, ?, ?, ?)"
        c.execute(query, (guid, account, date, text, message))
        conn.commit()
        conn.close()

        func(*args, **kwargs)
    return wrapper

@update_db
def reply(**kwargs):
    _, account, _, _ = kwargs["row"]
    account = account.split(':')[-1]
    message = kwargs["message"]
    os.system(f'osascript send-message.applescript {account} "{message}"')

def get_latest_reply_date(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    query = "SELECT MAX(date) FROM message"
    c.execute(query)
    row = c.fetchone()
    conn.close()
    return row[0]

async def run_bot():
    openai.api_key = api_key
    while True:
        latest_date = get_latest_reply_date('./chat.sqlite')
        rows = read_messages_after(latest_date if latest_date else 0)
        for row in rows:
            guid, account, text, date = row
            if text == None:
                continue
            print(f"New message from {account}: {text}")
            answer = await get_answer_simple(text, True, url=proxy_url)
            reply(row=row, message=answer, db='./chat.sqlite')
        await asyncio.sleep(10)

async def main():
    asyncio.create_task(refresh_cfg(10))
    asyncio.create_task(run_bot())

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()