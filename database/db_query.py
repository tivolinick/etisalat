#!/usr/local/bin/python3
import requests
import json
import psycopg2
import sys
import os

# db user and password will come from a secret
db_name = 'apps'
db_host = 'ndf-db.cluster.local'
db_user = 'turbo'
db_pass = 'ta5tic!'
db_port = 5432

# turbo user and password will come from a secret
turbo_host = '10.188.161.53'
turbo_user = 'Administrator'
turbo_pass = 'ta5t1c!'

'''
===================================================================
                            CLASSES
===================================================================
'''


class DatabaseAppVM:
    def __init__(self, database, host, port, username, password) -> None:
        self.database = database
        self.host = host
        self.port = port
        self.conn = psycopg2.connect(database=self.database,
                                     host=self.host,
                                     user=username,
                                     password=password,
                                     port=self.port)
        self.cursor = self.conn.cursor()

    def __str__(self) -> str:
        return f'Database: {self.database} on {self.host}:{self.port}'

    def __del__(self) -> None:
        self.close_connection()

    def close_connection(self) -> None:
        self.conn.close()

    def execute(self, sql) -> list:
        self.cursor.execute(sql)
        return self.cursor.fetchall()


class TurboApi:
    def __init__(self, host, username, password) -> None:
        self.host = host
        url = f'https://{self.host}/vmturbo/rest/login'
        data = {'username': username, 'password': password}
        r = requests.post(url, data=data, verify=False)
        self.cookie = r.headers['Set-Cookie'].split(';')[0]

    def __str__(self) -> str:
        return f'API: https://{self.host}/api/v3/'

    # get  data from a query
    def get_turbo_data(self, api, payload) -> json:
        url = f'https://{self.host}/api/v3/{api}'
        headers = {'Content-Type': 'application/json', 'cookie': self.cookie}
        t = requests.get(url, headers=headers, verify=False, params=payload)
        print(t)
        # print(t.text)
        return json.loads(t.text)

    def search_turbo_data(self, server) -> json:
        turbo_payload = {f'types': 'VirtualMachine', 'detail_type': 'aspects', 'q': server}
        return self.get_turbo_data('search', turbo_payload)


'''
===================================================================
                           FUNCTIONS
===================================================================
'''


# Function to map forward and backwards dependencies on start or stop order
def mapper(list, target, forwards, backwards):
    prev = 0
    for str_item in list:
        item = int(str_item)
        print(f'item: {item}, prev: {prev}, (matching {target})')
        print(type(item))
        print(type(target))
        if prev == 0:
            prev = item
            continue
        # print ('ONWARDS')
        if prev in forwards.keys():
            print(f'CONTAINS {prev} - {forwards[prev]}')
            forwards[prev].append(item)
        else:
            forwards[prev] = [item]
        if item in backwards.keys():
            print(f'CONTAINS {item} - {backwards[item]}')
            backwards[item].append(prev)
        else:
            backwards[item] = [prev]
        # depended[item]=prev
        prev = item
        print(f'so far: {forwards} - {backwards}')


# Iterative function to sort the startup and shutdown orders
def order_maps(back, front, order, id):
    index = -1
    if id not in order:
        if id in front.keys():
            for parent in front[id]:
                if parent in order:
                    i = order.index(parent)
                    # print(f'id: {id}, parent: {parent}, index: {i}')
                    if index < 0 or i < index:
                        index = i
        if index < 0:
            index = 0
        order.insert(index, id)
        if id in back.keys():
            for child in back[id]:
                order_maps(back, front, order, child)


def build_vm_entry(id, db_data, turbo_data):
    host_line = {}
    print(f'DB_DATA: {db_data}')
    print(db_data[0][1])
    print(f'ID: {id}')
    print(f'TURBO: {turbo_data}')
    host_line['displayName'] = turbo_data[0]['displayName']
    host_line['uuid'] = turbo_data[0]['uuid']
    host_line['vmhost'] = turbo_data[0]['discoveredBy']['displayName']
    host_line['ip'] = turbo_data[0]['aspects']['virtualMachineAspect']['ip']
    host_line['startcmd'] = db_data[0][2]
    host_line['stopcmd'] = db_data[0][3]
    host_line['statuscmd'] = db_data[0][4]
    print(f'host_line: {host_line}')
    return host_line


def read_envs(dir_name, envs_obj):
    dir_name = f'//users//nickfreer{dir_name}'
    d = os.listdir(dir_name)
    for filename in os.listdir(dir_name):
        if 'key' not in filename:
            f = open(f'{dir_name}/{filename}', 'r')
            envs[filename] = f.readline().splitlines()[0]


'''
===================================================================
                             MAIN
===================================================================
'''
# Read in all the env values from secrets and configmaps
envs = {}
for dir in ['//actionscriptcreds', '//actionscriptrefs', '//externalhosts', '//sshkeys']:
    read_envs(dir, envs)
print(envs)

sys.exit('bye bye')

# Read in the data about the action
action_data = json.loads(sys.stdin.read())
server = action_data[0]['targetSE']['displayName']
print(server)

# open a DB connection and return a cursor
vm_db = DatabaseAppVM(db_name, db_host, db_port, db_user, db_pass)

# get the vm info from the DB
host_info = vm_db.execute(f"SELECT * FROM vms WHERE displayname = '{server}'")
print(f'HOST_INFO: {host_info}')

# get all the apps in the DB
apps = vm_db.execute("SELECT * FROM apps")
print('fserver: {host_info[0][0]}')
print(f'START ORDER: {apps[0][3]}')
print(f'STOP ORDER:  {apps[0][4]}')

# map the start and stop dependencies
start_front = {}
start_back = {}
stop_front = {}
stop_back = {}

for app in apps:
    print(app[1])
    mapper(app[4].split(' '), host_info[0][0], start_front, start_back)
    mapper(app[3].split(' '), host_info[0][0], stop_front, stop_back)
print('RESULTS')
print(host_info[0][0])
for app in apps:
    print(app[3].split(' '))
    print(app[4].split(' '))
print('============START=============')
print(start_front)
print(start_back)
print(start_front.keys())
print(start_back.keys())
print('============STOP==============')
print(stop_front)
print(stop_back)
print(stop_front.keys())
print(stop_back.keys())

# use the maps to work out the start and stop orders
start_order = []
stop_order = []
# return orders
order_maps(start_back, start_front, start_order, host_info[0][0])
order_maps(stop_front, stop_back, stop_order, host_info[0][0])
start_order.reverse()
print("START")
print(start_order)

print("STOP")
print(stop_order)

# get vm data from the DB for those in the list
vms = vm_db.execute(f"SELECT * FROM vms WHERE id IN ({','.join(map(str, stop_order))})")
print(vms)

# get log in to the turbo API
turbo = TurboApi('10.188.161.53', turbo_user, turbo_pass)
# build the payload
ansible_payload = {'inventory': '', 'order': []}
for id in stop_order:
    db_data = [host_line for host_line in vms if host_line[0] == id]
    turbo_data = turbo.search_turbo_data(db_data[0][1])
    ansible_payload['order'].append(build_vm_entry(id, db_data, turbo_data))
    for ip in turbo_data[0]['aspects']['virtualMachineAspect']['ip']:
        ansible_payload['inventory'] += f' {ip}'
print('FINAL ANSWER:-')
ansible_payload['inventory'] = ansible_payload['inventory'].strip()
# print(ansible_payload)

del vm_db
print('for the ansible call')

# url = "https://www.example.com/api/v2/job_templates/%7Bid%7D/launch/"
# payload = { "extra_vars": { "survey_var": 7 } }
# headers = {"Content-Type": "application/json"}
# response = requests.post(url, json=payload, headers=headers)
# print(response.json())

url = "https://controller-1-aap.mycluster-dal10-b3-971261-853ee6c705a11146d16c0fa7df8df22d-0000.us-south.containers.appdomain.cloud/api/v2/job_templates/7/launch/"
payload = {"extra_vars": json.dumps(ansible_payload)}
auth = ("admin", "zYywgoOWA4ywG9lb5C59AHA0FudLVb3C")
# payload = { "extra_vars": { "survey_var": 7 } }
print(payload)
headers = {"Content-Type": "application/json"}
# response = requests.post(url, json=payload, headers=headers, auth=auth)
# print(response)
# print(response.text)


# payload = { "extra_vars": { "survey_var": 7 } }
