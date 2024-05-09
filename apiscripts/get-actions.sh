turbohost=$(cat turbohost| grep -v '#')
echo $turbohost
JSESSIONID=$(curl \
--silent \
--cookie-jar - \
--insecure \
https:/$turbohost/vmturbo/rest/login \
--data "username=Administrator&password=ta5t1c!" \
| awk '/JSESSIONID/{print $7}')

echo $JSESSIONID


#"https://$turbohost/api/v3/search?types=action" \
(curl \
"https://$turbohost/api/v3/entities" \
--insecure \
--compressed \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header "cookie: JSESSIONID=$JSESSIONID" \
--request GET)
# | tail -1 | jq '.'

#(curl \
#"https://10.188.161.53/api/v3/entities/$1" \
#--insecure \
#--compressed \
#--header 'Accept: application/json' \
#--header 'Content-Type: application/json' \
#--header "cookie: JSESSIONID=$JSESSIONID" \
#--request POST) | tail -1 | jq '.'
