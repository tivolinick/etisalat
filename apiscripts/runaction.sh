turbohost=$(cat turbohost| grep -v '#')
JSESSIONID=$(curl \
--silent \
--cookie-jar - \
--insecure \
https:/$turbohost/vmturbo/rest/login \
--data "username=Administrator&password=ta5t1c!" \
| awk '/JSESSIONID/{print $7}')

echo $JSESSIONID

#action_UUID=638413893855923
action_UUID=$1
curl -v \
"https://$turbohost/api/v3/actions/${action_UUID}?accept=true" \
--insecure \
--compressed \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header "cookie: JSESSIONID=$JSESSIONID" \
--request POST
echo
echo ================================================================
