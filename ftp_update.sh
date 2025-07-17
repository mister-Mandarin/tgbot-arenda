#!/bin/bash
set -a
source .env
set +a

rm -f "$LOCAL_PATH"/*

ftp -inv $FTP_HOST <<EOF
user $FTP_USER $FTP_PASS
cd $SERVER_PATH
lcd $LOCAL_PATH
mget *.json
bye
EOF

uv run python -m services.sync
