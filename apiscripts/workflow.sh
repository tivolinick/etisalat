JSESSIONID=$(curl \
--silent \
--cookie-jar - \
--insecure \
https:/10.188.161.53/vmturbo/rest/login \
--data "username=Administrator&password=ta5t1c!" \
| awk '/JSESSIONID/{print $7}')

echo $JSESSIONID


curl \
"https://10.188.161.53/api/v3/workflows" \
--insecure \
--compressed \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header "cookie: JSESSIONID=$JSESSIONID" \
--request POST \
--data '
{
"displayName": "URLTest_Webhook1",
"className": "Workflow",
"description": "First webhook attempt.",
"discoveredBy":
{
"readonly": false
},
"type": "WEBHOOK",
"typeSpecificDetails": {
"template": "{ \"name\":\"test\", \"action\":\" $action.details\" }",
"url": "https://eo5tpbp6fxdjwit.m.pipedream.net",
"method": "POST",
"type": "WebhookApiDTO"
}
}
'
#"template": "$converter.toJson($action)",
#"template": "{ \"name\":\"test\", \"action\":\" $converter.toJson($action)\"}",
#"template": "{ \"name\":\"test\", \"action\":\" $action.details\", \"actionImapctID\":\" $action.actionImpactID\", \"marketID\":\" $action.marketID\", \"createTime\":\" $action.createTime\", \"actionType\":\" $action.actionType\", \"actionState\":\" $action.actionState\", \"actionMode\":\" $action.actionMode\", \"importance\":\" $action.importance\", \"target\":\" $action.target\", \"currentValue\":\" $action.currentValue\", \"newValue\":\" $action.newValue\", \"valueUnits\":\" $action.valueUnits\", \"risk\":\" $action.risk \"}",
#"template": "$converter.toJson($action)",
#"template": "{ \"name\":\"test\", \"action\":\" $action.details\", \"target\":\" $action.target\", \"uuid\":\" $action.actionType\"}",
#"template": "{ \"text\":\"My Webhook Template -- DATA: Action Details: $action\" }",
#"template": "{ \"name\":\"test\", \"action\":\" $action.details\" }",

