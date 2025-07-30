import requests
import json
import subprocess
import os
import questionary

with open('user_data.json', 'r', encoding='utf-8') as user_data:
    user_info = json.load(user_data)
headers = {
    'referer': 'https://www.bilibili.com',
    'user-agent': user_info['User-Agent']
}
cookies = {'SESSDATA': user_info['SESSDATA']}
store_path = user_info['path']

PINK = "\033[38;5;213m"
BLUE = "\033[1;34m"
RESET = "\033[0m"
print(f'{PINK}', end='')
print('当前的下载路径为:', store_path)
url = 'https://api.bilibili.com/x/web-interface/nav'
request = requests.get(url, headers=headers, cookies=cookies)
info = request.json()
print('用户状态：', end='')
if info['code'] == -101:
    print('游客状态')
else:
    vip = info['data']['vipType']
    if info['data']['vipStatus'] == 0:
        print('普通用户')
    elif vip == 1:
        print('大会员')
    elif vip == 2:
        print('年度大会员')
print(f'{RESET}')

while True:
    instruction = questionary.select(
        "请选择指令 (箭头切换，ENTER确认):",
        choices=["进行下载", "改变保存位置", "登录b站账号（使用sessdata，获取方法详见https://github.com/amenonioi/Bilibili_Download）", "更改默认设置", "退出程序"],
        default="进行下载"
    ).ask()
    if instruction == '退出程序':
        print(f'{BLUE}已退出程序\n{RESET}')
        break
    elif instruction == '进行下载':
        subprocess.run('python core.py')
    elif instruction == '改变保存位置':
        filepath = questionary.text("请输入文件夹路径:").ask()
        print(f'{PINK}', end='')
        if os.path.exists(filepath):
            store_path = filepath
            user_info['path'] = store_path
            with open('user_data.json', 'w', encoding='utf-8') as user_data:
                user_data.write(json.dumps(user_info))
            print('下载路径已修改至:', filepath)
        else:
            print('无效的路径')
        print(f'\n{RESET}', end='')
    elif instruction == '登录b站账号（使用sessdata，获取方法详见https://github.com/amenonioi/Bilibili_Download）':
        sessdata = questionary.text("请输入sessdata:").ask()
        cookies = {'SESSDATA': sessdata}
        user_info['SESSDATA'] = sessdata
        with open('user_data.json', 'w', encoding='utf-8') as user_data:
            user_data.write(json.dumps(user_info))

        url = 'https://api.bilibili.com/x/web-interface/nav'
        request = requests.get(url, headers=headers, cookies=cookies)
        info = request.json()

        print(f'{PINK}', end='')
        print('用户状态已变更为：', end='')
        if info['code'] == -101:
            print('游客状态')
        else:
            vip = info['data']['vipType']
            if info['data']['vipStatus'] == 0:
                print('普通用户')
            elif vip == 1:
                print('大会员')
            elif vip == 2:
                print('年度大会员')
        print(f'\n{RESET}', end='')
    elif instruction == '更改默认设置':
        choices = ["是否下载重名文件", "是否将所有视频相关文件存储于文件夹中"]
        if user_info['download_duplicate_file']:
            choices[0] += " （当前选择为【是】）"
        else:
            choices[0] += " （当前选择为【否】）"
        if user_info['save_in_file']:
            choices[1] += " （当前选择为【是】）"
        else:
            choices[1] += " （当前选择为【否】）"

        instruction = questionary.select(
            "请选择更改内容 (箭头切换，ENTER确认):",
            choices=choices
        ).ask()
        if instruction == choices[0]:
            instruction = questionary.select(
                "是否下载重名文件 (箭头切换，ENTER确认):",
                choices=["是", "否"]
            ).ask()
            if instruction == "是":
                user_info['download_duplicate_file'] = True
            else:
                user_info['download_duplicate_file'] = False
        if instruction == choices[1]:
            instruction = questionary.select(
                "是否下载重名文件 (箭头切换，ENTER确认):",
                choices=["是", "否"]
            ).ask()
            if instruction == "是":
                user_info['save_in_file'] = True
            else:
                user_info['save_in_file'] = False
        with open('user_data.json', 'w', encoding='utf-8') as user_data:
            user_data.write(json.dumps(user_info))

