#!/usr/bin/env bash
# Get page access and price information and record to log
# Intended as analytic resource for investment decisions

FILENAME='/home/hobs/Notes/notes_repo/bitcoin popularity trend.txt'
COOKIEFILE='/home/hobs/tmp/wget_cookies.txt'
REFERRERURL='http://google.com'
USERAGENT='Mozilla'
echo -n `date --rfc-3339=seconds` >> "$FILENAME"
echo -n '	' >> "$FILENAME"
wget --output-document=- --tries=6 --no-http-keep-alive --no-check-certificate --user-agent="$USERAGENT"--referer="$REFERRERURL" --ignore-length --save-cookies="$COOKIEFILE" --load-cookies="$COOKIEFILE" --wait=6 --random-wait https://en.bitcoin.it/wiki/Trade | grep -P -o '(?<=accessed\s)\s*([0-9],)?[0-9]{3},[0-9]{3}' >> "$FILENAME"
echo -n '	' >> "$FILENAME"
wget --output-document=- --tries=6 --no-http-keep-alive --no-check-certificate --user-agent="$USERAGENT"--referer="$REFERRERURL" --ignore-length --save-cookies="$COOKIEFILE" --load-cookies="$COOKIEFILE" --wait=9 --random-wait https://mtgox.com | grep -P -o '(?<=Weighted Avg:<span>)\s*\$[0-9]{1,2}[.][0-9]{5}' >> "$FILENAME"
echo ' ' >> "$FILENAME"


