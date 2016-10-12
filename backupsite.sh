#!/bin/sh
# args:
# $1 backup path
# $2 sites path
# $3 site name
# $4 config path
# $5 rm
# $6 scripts path

mkdir -p $1
cd $2
if [ -n "$5" ]; then
    zip -qruo $1/$3.zip $3/mysite $3/site $3/assets $3.sql $3/composer.json $3/humans.txt $3/robots.txt $3/favicon.ico
else
    zip -qrmuo $1/$3.zip $3/mysite $3/site $3/assets $3.sql $3/composer.json $3/humans.txt $3/robots.txt $3/favicon.ico
fi

cd $4
if [ -n "$5" ]; then
    zip -qruo $1/$3.zip ./example_config
else
    zip -qrmuo $1/$3.zip ./example_config
fi

cd $2
rm $3.sql
# Upload to dropbox
$6/Dropbox-Uploader/dropbox_uploader.sh upload $1/$3.zip

rm $1/$3.zip