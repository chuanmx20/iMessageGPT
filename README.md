# iMessageGPT

This repo is to set up a iMessage bot with openai's api.
I've no idea which OSX version will be supported, but works just well for me (Ventura 13.3.1, x86_64).

## Usage
1. Fill a `config.yml` according to `example.config.yml`
2. Create db and run
```shell
git clone https://github.com/chuanmx20/iMessageGPT.git
cd iMessageGPT

touch chat.sqlite
sqlite3 chat.sqlite

# on connection to chat.sqlite now
>> CREATE TABLE message
    (guid TEXT NOT NULL,
    account TEXT NOT NULL,
    date INTEGER NOT NULL,
    message TEXT NOT NULL,
    reply TEXT NOT NULL);
>> .quit
# now the connection to chat.sqlite is closed

pip install -r requirement.txt

python bot.py
```

## Implementation summary
In conclusion, this bot can be classified into three parts, new message check, generate reply and send back respectively.
The first part, new message check is done by reading ~/Library/Messages/chat.db.
The second part is supported by openai lib.
And the last part is defined in `send-message.applescript`, which is a simple applescript function to send certain message to a certain contact.

## TBD
I can't tell from the ~/Library/Messages/chat.db the sender of each message. Hence if you are running this bot, **DONT** send message to others with your iphone, or it will be wierd to find that you are replying your own message in the chat with other people.
