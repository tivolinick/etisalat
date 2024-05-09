#!/usr/bin/python3
import psycopg2
import csv
import re
#==================================================================
#                             FUNCTIONS
#==================================================================

# function to build start and stop order lists for each application
def build_list(orderObj,order,id,application,environment):
    theKey=f'{application}@{environment}'
    try:
        if orderObj[theKey]:
            pass
    except KeyError:
        orderObj[theKey]=[]
    print(f'ORDER: {orderObj}')
    if len(orderObj[theKey]) <= int(order):
        orderObj[theKey].extend([''] * (int(order) - len(orderObj[theKey]) +1))
    if orderObj[theKey][int(order)] == '':
        orderObj[theKey][int(order)]=str(id)
    else:
        orderObj[theKey][int(order)] += f',{str(id)}'

# function to insert VM entries
def insertvm(vms,cursor,displayname,startcmd,stopcmd,statuscmd):
    for i in range(len(vms)) :
        if vms[i][1]== displayname:
            print('NAME')
            if vms[i][2] != startcmd or vms[i][3] != stopcmd or vms[i][4] != statuscmd:
                print('NO MATCH')
                print(f"UPDATE vms SET startcmd = '{startcmd}', stopcmd = '{stopcmd}', statuscmd = '{statuscmd}' WHERE id = {vms[i][0]}")
                cursor.execute(f"UPDATE vms SET startcmd = '{startcmd}', stopcmd = '{stopcmd}', statuscmd = '{statuscmd}' WHERE id = {vms[i][0]}")
            return vms[i][0]
    print('NEW')
    print(f"INSERT INTO vms (displayname, startcmd, stopcmd, statuscmd) VALUES ('{displayname}','{startcmd}','{stopcmd}','{statuscmd}');" )
    cursor.execute(f"INSERT INTO vms (displayname, startcmd, stopcmd, statuscmd) VALUES ('{displayname}','{startcmd}','{stopcmd}','{statuscmd}');" )
    cursor.execute(f"SELECT id, displayname FROM vms where (displayname = '{displayname}');" )
    newvm=cursor.fetchone()
    newrow=(newvm[0],displayname, startcmd, stopcmd, statuscmd)
    vms.append(newrow)
    return newvm[0]

# function to insert App entries
def insertapp(apps,cursor,start,stop):
    for theKey in start.keys():
        match=False
        print(theKey)
        # remove empty 
        startorder=' '.join([item for item in start[theKey] if item != ''])
        stoporder=' '.join([item for item in stop[theKey] if item != ''])
        # startorder=' '.join(start[theKey]).strip()
        # stoporder=' '.join(stop[theKey]).strip()
        print(f'{startorder}  {stoporder}')
        print(re.split(' +',startorder))
        print(re.split(' +',stoporder))
        for i in range(len(apps)):
            if f'{apps[i][1]}@{apps[i][2]}'==theKey :
                match=True
                print('NAME')
                if apps[i][3] != startorder or apps[i][4] != stoporder:
                    print('NO MATCH')
                    print(f"UPDATE apps SET startorder = '{startorder}', stoporder = '{stoporder}' WHERE id = {apps[i][0]}")
                    cursor.execute(f"UPDATE apps SET startorder = '{startorder}', stoporder = '{stoporder}' WHERE id = {apps[i][0]}")
                    conn.commit() 
                break
        if not match:
            uniqname=theKey.split('@')
            print(f"INSERT INTO apps (appname, environment, startorder, stoporder) VALUES ('{uniqname[0]}','{uniqname[1]}','{startorder}','{stoporder}');" )
            cursor.execute(f"INSERT INTO apps (appname, environment, startorder, stoporder) VALUES ('{uniqname[0]}','{uniqname[1]}','{startorder}','{stoporder}');" )
            conn.commit() 

#==================================================================
#                               MAIN
#==================================================================

db_name='apps'
db_host='ndf-db.cluster.local'
db_user='admin'
db_pass='adm1nPa55'
db_port=5432
conn = psycopg2.connect(database=db_name,
                        host=db_host,
                        user=db_user,
                        password=db_pass,
                        port=db_port)

cursor = conn.cursor()
cursor.execute("SELECT * FROM apps")
apps=cursor.fetchall()
cursor.execute("SELECT * FROM vms")
vms=cursor.fetchall()

start={}
stop={}
with open('dbinput.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(f'row {row}')
        id=insertvm(vms,cursor,row['displayname'],row['start cmd'],row['stop cmd'],row['status cmd'])
        print(f'ID: {id}')
        build_list(start,row['start order'],id,row['application'],row['environment'])
        build_list(stop,row['stop order'],id,row['application'],row['environment'])
    print(f'start {start}')
    print(f'stop {stop}')

print(f'APPS: {apps}')
print(f'VMS:  {vms}')

insertapp(apps,cursor,start,stop)

print(f'APPS: {apps}')
print(f'VMS:  {vms}')


conn.commit() 
conn.close()
