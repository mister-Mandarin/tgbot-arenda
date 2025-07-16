#!/bin/bash
set -a
source .env
set +a

LOCAL_PATH="/home/mandarin/tgbot-arenda/data"
SERVER_PATH="/home/c/ca70594/google_calendar_to_sheets/data"

ftp -inv $FTP_HOST <<EOF
user $FTP_USER $FTP_PASS
cd $SERVER_PATH
lcd $LOCAL_PATH
mget *
bye
EOF

#python -m services.sync
