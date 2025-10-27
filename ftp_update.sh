#!/bin/bash
set -a
source .env
set +a

rm -f "$LOCAL_PATH/data"/*

ftp -inv $FTP_HOST <<EOF
user $FTP_USER $FTP_PASS
cd $SERVER_PATH
lcd "$LOCAL_PATH/data"
mget *.json
bye
EOF

cd $LOCAL_PATH || exit 1
"$LOCAL_PATH/.venv/bin/python" -m services.sync
