JSESSIONID=$(curl \
--silent \
--cookie-jar - \
--insecure \
https:/10.188.161.53/vmturbo/rest/login \
--data "username=Administrator&password=ta5t1c!" \
| awk '/JSESSIONID/{print $7}')

echo $JSESSIONID

for url in $(grep 'this.baseUrl +' website.js | grep entities | cut -d'"' -f2 | sed 's/{entity_Uuid}/75303889872592/g'); do
    echo $url >> js.log
    echo $url 
    

    (curl -v \
    "https://10.188.161.53/api/v3/$url" \
    --insecure \
    --compressed \
    --header 'Accept: application/json' \
    --header 'Content-Type: application/json' \
    --header "cookie: JSESSIONID=$JSESSIONID" \
    --request GET) | tail -1 | grep '10.188.174.41' | tee -a js.log

done

# 