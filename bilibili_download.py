import requests
import json
import subprocess
import os

with open('user_data.json', 'r', encoding='utf-8') as user_data:
    user_info = json.load(user_data)
headers = {
    'referer': 'https://www.bilibili.com',
    'user-agent': user_info['User-Agent']
}
cookies = {'SESSDATA': user_info['SESSDATA']}
store_path = user_info['path']

print('当前的下载路径为', store_path)
url = 'https://api.bilibili.com/x/web-interface/nav'
request = requests.get(url, headers=headers, cookies=cookies)
info = request.json()
print('用户状态：', end='')
if info['code'] == -101:
    print('游客状态')
else:
    vip = info['data']['vipType']
    if vip == 0:
        print('普通用户')
    elif vip == 1:
        print('大会员')
    elif vip == 2:
        print('年度大会员')

print('-输入 help 以获得帮助-')
while True:
    instruction = input('<bilibili_download>')
    if instruction == 'exit':
        break
    elif instruction == 'help':
        print(' download -- 进行下载')
        print(' filepath -- 改变保存位置')
        print(' login -- 登录b站账号（使用sessdata）')
        print(' exit -- 退出程序')
    elif instruction == 'download':
        subprocess.run('python core.py')
    elif instruction == 'filepath':
        filepath = input('请输入文件夹路径')
        if os.path.exists(filepath):
            store_path = filepath
            user_info['path'] = store_path
            with open('user_data.json', 'w', encoding='utf-8') as user_data:
                user_data.write(json.dumps(user_info))
        print('下载路径已修改至', filepath)
    elif instruction == 'login':
        sessdata = input('请输入sessdata')
        cookies = {'SESSDATA': sessdata}
        user_info['SESSDATA'] = sessdata
        with open('user_data.json', 'w', encoding='utf-8') as user_data:
            user_data.write(json.dumps(user_info))

        url = 'https://api.bilibili.com/x/web-interface/nav'
        request = requests.get(url, headers=headers, cookies=cookies)
        info = request.json()
        print('用户状态：', end='')
        if info['code'] == -101:
            print('游客状态')
        else:
            vip = info['data']['vipType']
            if vip == 0:
                print('普通用户')
            elif vip == 1:
                print('大会员')
            elif vip == 2:
                print('年度大会员')

