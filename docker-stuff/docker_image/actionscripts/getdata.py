import requests
import json
import psycopg2
import sys
import os
import time
import oracledb


'''
===================================================================
                            CLASSES
===================================================================
'''

# en = 'hr'
# cs = '192.168.253.27/freepdp1' W= getpass.getpass(f'Enter password for {un}@{cs}: ')
# vith oracledb.connect(user=un, password=pw, dsn=cs) as connection:
# with connection.cursor as cursor:
# sql = """select

class DatabaseAppVM:
    def __init__(self, database, host, port, username, password) -> None:
        self.database = database
        self.host = host
        self.port = port
        self.conn = oracledb.connect(database=self.database,
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

    def execute(self, sql: str) -> list:
        self.cursor.execute(sql)
        return self.cursor.fetchall()

class DatabaseAppVMpostgres:
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

    def execute(self, sql: str) -> list:
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


class AnsibleApi:
    def __init__(self, host, username, password, interval_secs=5, timeout_mins=10) -> None:
        self.url = f'https://{host}/api/v2'
        self.auth = (username, password)
        self.headers = {"Content-Type": "application/json"}
        self.interval_secs = interval_secs
        self.max_count = timeout_mins * 60 / interval_secs

    def __str__(self) -> str:
        return f'API: {self.url}'

    def launch_job(self, template_id, payload) -> str:
        url = f'{self.url}/job_templates/{template_id}/launch/'
        print(url)
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth, verify=False)
        print(response)
        print(response.text)
        return json.loads(response.text)['job']

    def get_job_status(self, job_id) -> str:
        url = f'{self.url}/jobs/{job_id}/'
        # print(url)
        r = requests.get(url, auth=self.auth, verify=False)
        # print(json.loads(r.text))
        return json.loads(r.text)['status']

    def get_event_status(self, job_id) -> str:
        # Make sure page size is always bigger than number of records
        url = f'{self.url}/jobs/{job_id}/job_events/?page_size=1'
        r = requests.get(url, auth=self.auth, verify=False)
        page_size = json.loads(r.text)['count']
        page_size += 1
        url = f'{self.url}/jobs/{job_id}/job_events/?page_size={page_size}'
        # print(url)
        r = requests.get(url, auth=self.auth, verify=False)
        print(f"RESULTS: {r.text}")
        stat = json.loads(r.text)
        for theLine in [line['stdout'] for line in stat['results'] if 'STATUS:' in line['stdout']]:
            print(f'LINE: {theLine}')
            if 'Success' not in theLine:
                return theLine
        return 'success'

    def wait_for_job(self, job_id) -> str:
        status = self.get_job_status(job_id)
        print(status)
        count = 0
        while status == 'running' and count < self.max_count:
            print(status)
            time.sleep(self.interval_secs)
            status = self.get_job_status(job_id)
            count += 1
        print(f'FINAL:STATUS: {status}')
        if status == 'running':
            sys.exit('Ansible job timed out')
        if status != 'successful':
            sys.exit('Ansible job failed')
        status = self.get_event_status(job_id)
        if status != 'success':
            sys.exit(f'Ansible job failed with this message - {status}')
        return status


'''
===================================================================
                           FUNCTIONS
===================================================================
'''


def order_dependency(order, target, forwards, backwards):
    print('order dependency')
    print(order)
    print(target)
    print(forwards)
    print(backwards)


# Function to map forward and backwards dependencies on start or stop order
def mapper(order, target, forwards, backwards):
    prev = 0
    for item in order:
        if item == '':
            continue
        # item = int(str_item)
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


# Iterative function to get the startup and shutdown orders from the map
def order_maps(back, front, order, vm_id):
    index = -1
    if vm_id not in order:
        if vm_id in back.keys():
            # print(f'in there: {back[vm_id]}')
            for parent in back[vm_id]:
                if parent in order:
                    i = order.index(parent)
                    if index < 0 or i < index:
                        index = i
        if index < 0:
            index = 0
        order.insert(index, vm_id)
        if vm_id in front.keys():
            # print(f'In the back: {vm_id}')
            for child in front[vm_id]:
                order_maps(back, front, order, child)

# return all the required info for a specifc VM
def build_vm_entry(vm_id, db_data, turbo_data):
    host_line = {}
    print(f'DB_DATA: {db_data}')
    print(db_data[0][1])
    print(f'ID: {vm_id}')
    print(f'TURBO: {turbo_data}')
    host_line['displayName'] = turbo_data[0]['displayName']
    host_line['uuid'] = turbo_data[0]['uuid']
    host_line['vmhost'] = turbo_data[0]['discoveredBy']['displayName']
    # Need to check if IP is defined
    try:
        host_line['ip'] = turbo_data[0]['aspects']['virtualMachineAspect']['ip']
    except KeyError:
        sys.exit(f"No IP Address found for {host_line['displayName']}. VM may be powered off")
    host_line['startcmd'] = db_data[0][2]
    host_line['stopcmd'] = db_data[0][3]
    host_line['statuscmd'] = db_data[0][4]
    print(f'host_line: {host_line}')
    return host_line

# read the environment vars from files created by secrets and config maps
def read_envs(dir_name, envs_obj):
    for filename in os.listdir(dir_name):
        if 'key' not in filename and '..' not in filename:
            f = open(f'{dir_name}/{filename}', 'r')
            envs_obj[filename] = f.readline().splitlines()[0]
