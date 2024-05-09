#!/usr/bin/python3

# JSESSIONID=$(curl \
# --silent \
# --cookie-jar - \
# --insecure \
# https:/10.188.161.53/vmturbo/rest/login \
# --data "username=Administrator&password=ta5t1c!" \
# | awk '/JSESSIONID/{print $7}')

# echo $JSESSIONID


# (curl \
# "https://10.188.161.53/api/v3/search?types=VirtualMachine&entity_types=VirtualMachines&order_by=NAME&ascending=true" \
# --insecure \
# --compressed \
# --header 'Accept: application/json' \
# --header 'Content-Type: application/json' \
# --header "cookie: JSESSIONID=$JSESSIONID" \
# --request GET) | tail -1 | jq '.'
import sys
import json
import requests
from requests.auth import HTTPBasicAuth
# LOGIN
url='https://10.188.161.53/vmturbo/rest/login'
basic=HTTPBasicAuth('Administrator','ta5t1c!')
data={'username': 'Administrator', 'password': 'ta5t1c!'} 

r=requests.post(url,data=data,verify=False)
# head=json.loads(r.headers)
# print(head)
cookie=r.headers['Set-Cookie'].split(';')[0]

# ########### Function me up ################
# url='https://10.188.161.53/api/v3/search'
# headers={'Content-Type': 'application/json', 'cookie': cookie }
# cursor=0
# data=[]
# while cursor != '':
#     payload={'types': 'VirtualMachine', 'entity_types': 'VirtualMachines','order_by': 'NAME','ascending': 'true','cursor': cursor}
#     v=requests.get(url, headers=headers, params=payload, verify=False)
#     data=data + json.loads(v.text)
#     print (v.headers['X-Next-Cursor'])
#     cursor=v.headers['X-Next-Cursor']

# # print(v.status_code)
# # # print(v.content)
# # # print(v.json)
# # # print(v.headers)
# # # print(v.text)
# # data=json.loads(v.text)
# print(len(data))
# # print(f'{data[1]}\n')
# # hostdata=[{'displayName': hostline['displayName']} for hostline in data ]
# # print (f'{hostdata}\n')



# hostinfo= [ hostline for hostline in data if hostline['displayName'] == 'ndf-target3' ]
# print(hostinfo)
# print(f"{hostinfo[0]['displayName']},{hostinfo[0]['discoveredBy']['displayName']}")

# url='https://10.188.161.53/api/v3/entities/75303889872592/aspects/virtualMachineAspect'
# a=json.loads(requests.get(url, headers=headers, verify=False).text)
# # print(a['virtualMachineAspect']['ip'])
# # print(a['ip'])
# print(a)


url='https://10.188.161.53/api/v3/search'
headers={'Content-Type': 'application/json', 'cookie': cookie }
# payload={'types': 'VirtualMachine', 'entity_types': 'VirtualMachines','displayName': 'ndf-target1'}
payload={'types': 'VirtualMachine','detail_type' : 'aspects', 'q': 'ndf-target1'}
t=requests.get(url, headers=headers,  verify=False, params=payload)
print(t.text)
# print (t.headers['X-Next-Cursor'])
# cursor=v.headers['X-Next-Cursor']

