import csv
import paramiko
import time
import multiprocessing


with open('oui.txt', 'r') as file:
    lines_oui = file.readlines()


def oui_search(mac):
    if mac[0:6] + '\n' in lines_oui:
        return True
    return False


def start_scan(host):

    user = 'root'
    passw = '1'
    port = 22
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=passw, look_for_keys=False, allow_agent=False)
    client.exec_command('ifconfig wlan0 down')
    client.exec_command('iwconfig wlan0 mode monitor')
    client.exec_command('ifconfig wlan0 up')
    stdin, stdout, stderr = client.exec_command('airodump-ng wlan0 -w out --output-format csv > /dev/null 2>&1 &')
    data = stdout.read() + stderr.read()

def last_file(host):

    user = 'root'
    passw = '1'
    port = 22
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=passw, look_for_keys=False, allow_agent=False)
    stdin, stdout, stderr = client.exec_command('ls | grep -e .csv')
    data = stdout.read()
    lst = [d for d in data.decode().split('\n')]
    return lst[-2]


def get_file(host):
    port = 22
    transport = paramiko.Transport((host, port))
    transport.connect(username='root', password='1')
    sftp = paramiko.SFTPClient.from_transport(transport)

    file = last_file(host)
    remotepath = f'/root/{file}'
    localpath = 'out.csv'

    sftp.get(remotepath, localpath)

    sftp.close()
    transport.close()


def csv_reader(file_obj):
    reader = csv.reader(file_obj)
    bssid = []
    w = False
    for row in reader:
        try:
            if row[0] == 'Station MAC':
                w = True
                continue
        except: pass

        if w:
           try:
            bssid.append(row[0])
           except: pass

    print('MAC FOUND: ', len(bssid))

    return bssid

def seva_mac(bssids):
    out_bssid = set()
    file_name = str(input('Введи название файла'))

    for bssid in bssids:
        mac = bssid.replace(':','') + '\n'
        if oui_search(mac):
            out_bssid.add(mac)


    try:
        with open(f'{file_name}.txt', 'r') as file_read:
            read_bssid = file_read.readlines()

        for rbssid in read_bssid:
            out_bssid.add(rbssid)
    except:
        print('error read')

    print('mac write: ', len(out_bssid))
    with open(f'{file_name}.txt', 'w') as file:
        file.writelines(out_bssid)



if __name__ == "__main__":
    host = str(input('ip host: '))
    host = '192.168.1.1' if host == '' else host
    multiprocessing.Process(target=start_scan, args=(host,)).start()
    while True:
        get_file(host)
        with open("out.csv", "r", encoding="utf-8", errors='replace') as f_obj:
            bssids = csv_reader(f_obj)

        seva_mac(bssids)
        time.sleep(60)

