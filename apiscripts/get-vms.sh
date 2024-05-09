turbohost=$(cat turbohost| grep -v '#')
JSESSIONID=$(curl \
--silent \
--cookie-jar - \
--insecure \
https:/$turbohost/vmturbo/rest/login \
--data "username=Administrator&password=ta5t1c!" \
| awk '/JSESSIONID/{print $7}')

echo $JSESSIONID


#"https://$turbohost/api/v3/search?types=VirtualMachine&entity_types=VirtualMachines&cursor=0&q=$1" \
result=$((curl -v \
"https://$turbohost/api/v3/search?types=VirtualMachine&entity_types=VirtualMachines" \
--insecure \
--compressed \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header "cookie: JSESSIONID=$JSESSIONID" \
--request GET) | tail -1 )

#curl -v \
#"https://$turbohost/api/v3/search?types=VirtualMachine&entity_types=VirtualMachines" \
#--insecure \
#--compressed \
#--header 'Accept: application/json' \
#--header 'Content-Type: application/json' \
#--header "cookie: JSESSIONID=$JSESSIONID" \
#--request GET


echo $result 
echo $result | jq '.' 

uuid=$(echo $result | jq '.[].uuid' | sed 's/"//g')

echo UUID
echo $uuid
echo ASPECT
aspect=$((curl -v \
"https://$turbohost/api/entities/$uuid/actions" \
--insecure \
--compressed \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header "cookie: JSESSIONID=$JSESSIONID" \
--request GET 2> /dev/null) | tail -1 )

echo $aspect | jq '.' 
echo
echo $aspect | jq '.virtualMachineAspect.ip' 

# | grep cursor

# --request GET) | tail -1 | jq '.[0].uuid'
