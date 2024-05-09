UUID=$1

JSESSIONID=$(curl \
--silent \
--cookie-jar - \
--insecure \
https:/10.188.161.53/vmturbo/rest/login \
--data "username=Administrator&password=ta5t1c!" \
| awk '/JSESSIONID/{print $7}')

echo $JSESSIONID


(curl -v \
"https://10.188.161.53/api/v3/entities/$UUID" \
--insecure \
--compressed \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header "cookie: JSESSIONID=$JSESSIONID" \
--request GET) 
# | tail -1 | jq '.' | grep state | wc -l

# --request GET) | tail -1 | jq '.[0].uuid'
