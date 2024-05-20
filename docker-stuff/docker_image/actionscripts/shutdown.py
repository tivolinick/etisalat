#!/usr/local/bin/python

# from get_data import getdata
import getdata
import requests
import json
# import psycopg2
import sys
# import os
import socket

'''
===================================================================
                             MAIN
===================================================================
'''
# Read in all the env values from secrets and configmaps
envs = {}
for dir in ['//actionscriptcreds', '//actionscriptrefs', '//externalhosts', '//sshkeys']:
    if socket.gethostname() == 'Nicks-MacBook-Pro.local':
        dir = f'/users/nickfreer{dir}'
    getdata.read_envs(dir, envs)
print(envs)

# Read in the data about the action
# action_data = json.loads(sys.stdin.read())
# FOR DEBUG PURPOSES
stdin_data = sys.stdin.read()
requests.post('https://eo5tpbp6fxdjwit.m.pipedream.net/', stdin_data)
action_data = json.loads(stdin_data)
server = action_data['actionItem'][0]['targetSE']['displayName']
print(server)

# open a DB connection and return a cursor
# vm_db - tuple: (id, name, startup cmd, shutdown cmd, status cmd)
vm_db = getdata.DatabaseAppVM(envs['db_name'], envs['db_host'], envs['db_port'], envs['db_user'], envs['db_pass'])

# get the vm info from the DB
host_info = vm_db.execute(f"SELECT * FROM vms WHERE displayname = '{server}'")
if len(host_info) == 0:
    sys.exit(f'ERROR: VM {server} not found in database')
print(f'HOST_INFO: {host_info}')

# get all the apps in the DB
# apps - tuple: (id, app, environment, startup order, shutdown order)
apps = vm_db.execute("SELECT * FROM apps")

# map the start and stop dependencies
# start_front = {}
# start_back = {}
stop_front = {}
stop_back = {}

for app in apps:
    getdata.mapper(app[4].split(' '), host_info[0][0], stop_front, stop_back)
    getdata.order_dependency(app[3].split(' '), host_info[0][0], stop_front, stop_back)
print('RESULTS')
print('============STOP==============')
print(stop_front)
print(stop_back)
print(stop_front.keys())
print(stop_back.keys())

# use the maps to work out the start and stop orders
stop_order = []
stop_list = []
# return orders
getdata.order_maps(stop_front, stop_back, stop_list, str(host_info[0][0]))
print("STOP")
print(stop_list)
# flatten out lists of servers that are grouped by depndency
[stop_order.extend(item.split(',')) if ',' in item else stop_order.append(item) for item in stop_list]
print(stop_order)

# get vm data from the DB for those in the list
vms = vm_db.execute(f"SELECT * FROM vms WHERE id IN ({','.join(map(str, stop_order))})")
del vm_db
if len(vms) != len(stop_order):
    print(f'VMS from DB: {vms}')
    sys.exit(f'Not all the VMs were found in database for ids: {stop_order}')

# log in to the turbo API
turbo = getdata.TurboApi('10.188.161.53', envs['turbouser'], envs['turbopass'])
# build the payload
ansible_payload = {'inventory': '', 'order': []}
for id in stop_order:
    db_data = [host_line for host_line in vms if host_line[0] == id]
    turbo_data = turbo.search_turbo_data(db_data[0][1])
    ansible_payload['order'].append(getdata.build_vm_entry(id, db_data, turbo_data))
    for ip in turbo_data[0]['aspects']['virtualMachineAspect']['ip']:
        ansible_payload['inventory'] += f' {ip}'
ansible_payload['inventory'] = ansible_payload['inventory'].strip()

ansible_api = getdata.AnsibleApi(envs['ansible_host'], envs['ansible_user'], envs['ansible_pass'], 3, 1)
payload = {"extra_vars": json.dumps(ansible_payload)}
print(f'PAYLOAD- {payload}')
job = ansible_api.launch_job(envs['shutdown'], payload)
status = ansible_api.wait_for_job(job)
print(status)