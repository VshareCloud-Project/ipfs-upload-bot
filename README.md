# ipfs-upload-bot

A telegram bot to upload files to IPFS.

## Requirements

-  [Python 3.7+](https://www.python.org/downloads/)
-  [pip](https://pip.pypa.io/en/stable/installing/)


## Installation

    mkdir -p /opt
    cd /opt
    git clone https://github.com/VshareCloud-Project/ipfs-upload-bot.git
    mv ipfs-upload-bot ipfs-upload-bot
    cd ipfs-upload-bot
    python3 -m pip install -r requirements.txt
    python3 migration.py

## Configuration

Edit the `config.json` file.

```json
{
    "secret_key": "1145141919810",
    "telegram_api_token": "",
    "telegram_bot_username": "",
    "telegram_bot_server":null,
    "telegram_bot_server_file":null,
    "maxium_size": 10485760,
    "ipfs_api_host":"http://127.0.0.1:5010",
    "log_level":"DEBUG",
    "log_file":"/var/log/ipfs-upload-bot.log",
    "log_file_size":10485760,
    "log_file_backup_count":5,
    "log_file_encoding":"utf-8",
    "log_error_level":"ERROR",
    "log_error_file":"/var/log/ipfs-upload-bot-error.log",
    "tmp_path":"/tmp/uploadbot",
    "chunk_size": 2000000,
    "timeout":3600,
    "welcome_message":"Welcome to IPFS Upload Bot",
    "file_message":"File uploaded to IPFS, cid is {cid}"
}
```

## Run

    python3 main.py

## Make as a service

    cp ipfs-upload-bot.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable ipfs-upload-bot
    systemctl start ipfs-upload-bot

## License

[MIT](LICENSE)