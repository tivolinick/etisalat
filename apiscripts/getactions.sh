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

uuids=$(echo $result | jq '.[].uuid' | sed 's/"//g')
uuids=75463853292783

echo UUID
echo $uuids
echo ACTION
for uuid in $uuids ; do
echo $uuid
echo
(curl -v \
"https://$turbohost/api/entities/$uuid/actions" \
--insecure \
--compressed \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header "cookie: JSESSIONID=$JSESSIONID" \
--request GET 2> /dev/null) | tail -1 
echo
echo ================================================================
done
