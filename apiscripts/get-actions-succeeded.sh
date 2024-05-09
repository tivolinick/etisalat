JSESSIONID=$(curl \
--silent \
--cookie-jar - \
--insecure \
https:/10.188.161.53/vmturbo/rest/login \
--data "username=Administrator&password=ta5t1c!" \
| awk '/JSESSIONID/{print $7}')

echo $JSESSIONID


curl \
"https://10.188.161.53/api/v3/actions" \
--insecure \
--compressed \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header "cookie: JSESSIONID=$JSESSIONID" \
--request POST \
--data '
{
  "actionInput":{
    "actionStateList":[
      "PENDING_ACCEPT"
    ],
    "environmentType":"ONPREM",
    "groupBy":[
      "actionModes"
    ]
  },
  "relatedType":"VirtualMachine"
}
'
#"template": "{ \"text\":\"My Webhook Template -- DATA: Action Details: $action\" }",
#"template": "{ \"name\":\"test\", \"action\":\" $action.details\" }",

