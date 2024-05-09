JSESSIONID=$(curl \
--silent \
--cookie-jar - \
--insecure \
https:/10.188.161.53/vmturbo/rest/login \
--data "username=Administrator&password=ta5t1c!" \
| awk '/JSESSIONID/{print $7}')

echo $JSESSIONID
#curl -X 'GET' \
  #'https://10.188.161.53/vmturbo/rest/targets?target_category=Hypervisor&target_type=ACTION_SCRIPT&order_by=validation_status&ascending=true&query_method=regex' \
  #-H 'accept: application/json'

(curl \
"https://10.188.161.53/api/v3/targets/$1" \
--insecure \
--compressed \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header "cookie: JSESSIONID=$JSESSIONID" \
--request GET) | tail -1 | jq '.'
