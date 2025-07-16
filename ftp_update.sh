#!/bin/bash
set -a
source .env
set +a

rm -f "$LOCAL_PATH"/*

ftp -inv $FTP_HOST <<EOF
user $FTP_USER $FTP_PASS
cd $SERVER_PATH
lcd $LOCAL_PATH
mget *
bye
EOF

#python -m services.sync
