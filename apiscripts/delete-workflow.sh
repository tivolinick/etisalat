JSESSIONID=$(curl \
--silent \
--cookie-jar - \
--insecure \
https:/10.188.161.53/vmturbo/rest/login \
--data "username=Administrator&password=ta5t1c!" \
| awk '/JSESSIONID/{print $7}')

echo $JSESSIONID


curl \
"https://10.188.161.53/api/v3/workflows/$1" \
--insecure \
--compressed \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header "cookie: JSESSIONID=$JSESSIONID" \
--request DELETE
