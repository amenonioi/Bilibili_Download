import requests
import json
import subprocess
import os


def get_id(url_input, id_type):
    start = 0
    end = len(url_input)
    for i in range(len(url_input)):
        if start == 0:
            if url_input[i:i + len(id_type)] == id_type:
                start = i + len(id_type)
        else:
            if i < start:
                continue
            if not (url_input[i].isalpha() or url_input[i].isnumeric()):
                end = i
                break
    url_id = url_input[start:end]
    return url_id


def get_bv_info(bv):
    url = 'https://api.bilibili.com/x/web-interface/wbi/view?'
    data = {
        'bvid': bv
    }
    request = requests.get(url, params=data, headers=headers, cookies=cookies)
    info = request.json()
    title = info['data']['title']
    cover = info['data']['pic']
    # keywords 是会在创建文件夹或合并视频时产生bug的字符
    keywords = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for i in range(len(keywords)):
        title = title.replace(keywords[i], '')

    pages = info['data']['pages']
    datas = []
    subtitles = []
    for i in range(len(pages)):
        cid = pages[i]['cid']
        data = {
            'bvid': bv,
            'cid': cid,
            'fnval': '16',
            'fnver': '0',
            'fourk': '1'
        }
        datas.append(data)
        subtitle = pages[i]['part']
        for j in range(len(keywords)):
            subtitle = subtitle.replace(keywords[j], '')
        subtitles.append(subtitle)

    return datas, title, cover, subtitles


def get_fav_info(media_id):
    data = {
        'media_id': media_id
    }
    url = 'https://api.bilibili.com/x/v3/fav/folder/info'
    request = requests.get(url=url, params=data, headers=headers, cookies=cookies)
    info = request.json()
    media_count = info['data']['media_count']

    bvs = []
    for i in range(1, media_count // 20 + 2):
        data = {
            'media_id': media_id,
            'pn': str(i),
            'ps': '20'
        }
        url = 'https://api.bilibili.com/x/v3/fav/resource/list'
        request = requests.get(url=url, params=data, headers=headers, cookies=cookies)
        info = request.json()
        content = info['data']['medias']
        for j in range(len(content)):
            bvs.append(content[j]['bv_id'])
    return bvs


def get_collection_info(season_id):
    url = 'https://api.bilibili.com/x/space/fav/season/list?'
    data = {
        'season_id': season_id
    }
    request = requests.get(url=url, params=data, headers=headers, cookies=cookies)
    info = request.json()
    medias = info['data']['medias']

    bvs = []
    for i in range(len(medias)):
        bvs.append(medias[i]['bvid'])
    return bvs


def get_video_stream_info(data):
    url = 'https://api.bilibili.com/x/player/playurl?'
    request = requests.get(url, params=data, headers=headers, cookies=cookies)
    info = request.json()
    accept_quality = info['data']['accept_quality']
    video_info = info['data']['dash']['video']
    audio_info = info['data']['dash']['audio']

    _accept_quality = []
    for i in range(len(accept_quality)):
        if accept_quality[i] in vip_accept:
            _accept_quality.append(video_resolutions_decode[str(accept_quality[i])])

    video_resolutions = {}
    bandwidth = 0
    for i in range(len(video_info)):
        if video_info[i]['id'] not in video_resolutions:
            video_resolutions[video_info[i]['id']] = video_info[i]["baseUrl"]
            bandwidth = video_info[i]['bandwidth']
        elif video_info[i]['bandwidth'] > bandwidth:
            video_resolutions[video_info[i]['id']] = video_info[i]["baseUrl"]
            bandwidth = video_info[i]['bandwidth']

    audio_url = None
    for i in range(len(audio_resolutions_sort)):
        for j in range(len(audio_info)):
            if audio_info[j]['id'] == audio_resolutions_sort[i]:
                audio_url = audio_info[j]["baseUrl"]
                break
        if audio_url:
            break

    return _accept_quality, video_resolutions, audio_url


def get_bangumi_info(id_type, the_id):
    url = 'https://api.bilibili.com/pgc/view/web/season?'
    if id_type == 'ss':
        data = {'season_id': the_id}
    elif id_type == 'ep':
        data = {'ep_id': the_id}
    request = requests.get(url, params=data, headers=headers, cookies=cookies)
    info = request.json()
    title = info['result']['season_title']
    cover = info['result']['cover']
    episodes = info['result']['episodes']
    ep_ids = []
    subtitles = []
    for ep in episodes:
        ep_ids.append(ep['id'])
        subtitles.append(ep['show_title'])

    url = 'https://api.bilibili.com/pgc/player/web/playurl?'
    data = {'ep_id': ep_ids[0], 'fnval': '16'}
    request = requests.get(url, params=data, headers=headers, cookies=cookies)
    info = request.json()
    accept_quality = info['result']['accept_quality']
    _accept_quality = []
    for i in range(len(accept_quality)):
        if accept_quality[i] in vip_accept:
            _accept_quality.append(video_resolutions_decode[str(accept_quality[i])])

    return ep_ids, cover, title, subtitles, _accept_quality


def get_bangumi_stream_info(ep_id, video_resolution):
    url = 'https://api.bilibili.com/pgc/player/web/playurl'
    data = {'ep_id': ep_id, 'fnval': '16'}
    request = requests.get(url, params=data, headers=headers, cookies=cookies)
    info = request.json()
    video_info = info['result']['dash']['video']
    audio_info = info['result']['dash']['audio']
    bangumi_video_url = None
    size = 0
    for i in range(len(video_info)):
        if video_resolution == video_info[i]['id'] and int(video_info[i]['size']) > size:
            size = int(video_info[i]['size'])
            bangumi_video_url = video_info[i]['baseUrl']
    bangumi_audio_url = None
    for i in range(len(audio_resolutions_sort)):
        for j in range(len(audio_info)):
            if audio_info[j]['id'] == audio_resolutions_sort[i]:
                bangumi_audio_url = audio_info[j]["baseUrl"]
                break
        if bangumi_audio_url:
            break
    return bangumi_video_url, bangumi_audio_url


def get_video_stream(title, cover, video_url, audio_url, page, subtitle):
    if not page or page == 1:
        os.mkdir(title)
    os.chdir('./' + title)

    if cover_download:
        request = requests.get(cover, headers=headers)
        content = request.content
        with open('./' + title + '.jpg', 'wb') as filename:
            filename.write(content)

    title_info = title
    if page:
        # os.mkdir(subtitle)
        # os.chdir('./' + subtitle)
        title_info = subtitle

    if video:
        path = './video.mp4'
        download_in_chunk(video_url, 1024 * 1024 * 5, path, title_info, '视频')
    if audio:
        path = './audio.mp3'
        download_in_chunk(audio_url, 1024 * 1024 * 5, path, title_info, "音频")

    if video and audio:
        subprocess.run('ffmpeg -loglevel quiet -i video.mp4 -i audio.mp3 -c:v copy -c:a copy -f mp4 converge_video.mp4')
        os.remove("video.mp4")
        os.remove("audio.mp3")
        os.rename("converge_video.mp4", title_info + '.mp4')
    elif video:
        os.rename("video.mp4", title_info + '.mp4')
    elif audio:
        os.rename("audio.mp3", title_info + '.mp3')

    if page:
        pass
        # os.chdir('..')

    os.chdir('..')


def download_in_chunk(url, chunk_size, path, title, download_type):
    print('正在下载：', title, '-', download_type)
    with open(path, 'wb') as file:
        downloaded_size = 0
        while True:
            end = downloaded_size + chunk_size
            this_header = headers
            this_header['Range'] = f'bytes={downloaded_size}-{end}'
            response = requests.get(url, headers=this_header, stream=True)
            if not response:
                break
            file.write(response.content)

            downloaded_size = end + 1

            download_range = response.headers['Content-Range']
            for i in range(len(download_range)):
                if download_range[i] == '-':
                    start = i
                if download_range[i] == '/':
                    downloaded = download_range[start+1:i]
                    total = download_range[i+1:]
            print('下载进度：', round((int(downloaded)+1)/int(total)*100, 1), '%', end='    ')
            print(round(int(downloaded)/1048576, 1), 'MB', '/', round(int(total)/1048576, 1), 'MB')


def video_download(url_input, id_type):
    bv = 'BV' + get_id(url_input, id_type)
    datas, title, cover, subtitles = get_bv_info(bv)
    if os.path.exists(title):
        x = 1
        while os.path.exists(title + str(x)):
            x += 1
        title = title + str(x)
    for i in range(len(datas)):
        data = datas[i]
        subtitle = subtitles[i]
        accept_quality, video_resolutions, audio_url = get_video_stream_info(data)

        if video:
            video_quality = None
            if len(datas) == 1:
                print(accept_quality)
                while video_quality not in accept_quality:
                    video_quality = input('请选择视频分辨率')
            elif i == 0:
                quality_accept = []
                for key in video_resolutions_encode.keys():
                    if video_resolutions_encode[key] in vip_accept:
                        quality_accept.append(key)
                quality_accept.reverse()
                print(quality_accept)
                while video_quality not in video_resolutions_encode:
                    video_quality = input('这是一个分p视频，请选择视频默认分辨率')

            if video_quality in accept_quality:
                video_url = video_resolutions[video_resolutions_encode[video_quality]]
            else:
                video_url = video_resolutions[video_resolutions_encode[accept_quality[0]]]

        else:
            video_url = None

        if len(datas) == 1:
            get_video_stream(title, cover, video_url, audio_url, None, None)
        else:
            get_video_stream(title, cover, video_url, audio_url, i+1, 'P' + str(i+1) + ' ' + subtitle)


def fav_download(url_input, id_type, mode):
    if mode == 'fav':
        media_id = get_id(url_input, id_type)
        bvs = get_fav_info(media_id)
    elif mode == 'collection':
        season_id = get_id(url_input, id_type)
        bvs = get_collection_info(season_id)

    video_quality = None
    if video:
        quality_accept = []
        for key in video_resolutions_encode.keys():
            if video_resolutions_encode[key] in vip_accept:
                quality_accept.append(key)
        quality_accept.reverse()
        print(quality_accept)
        if mode == 'fav':
            print('这是一个收藏夹,', end='')
        elif mode == 'collection':
            print('这是一个合集,', end='')
        while video_quality not in video_resolutions_encode:
            video_quality = input('请选择视频默认分辨率')

    for i in range(len(bvs)):
        bv = bvs[i]
        datas, title, cover, subtitles = get_bv_info(bv)
        if os.path.exists(title):
            x = 1
            while os.path.exists(title + str(x)):
                x += 1
            title = title + str(x)
        for j in range(len(datas)):
            data = datas[j]
            subtitle = subtitles[j]
            accept_quality, video_resolutions, audio_url = get_video_stream_info(data)
            if video:
                if video_quality in accept_quality:
                    video_url = video_resolutions[video_resolutions_encode[video_quality]]
                else:
                    video_url = video_resolutions[video_resolutions_encode[accept_quality[0]]]
            else:
                video_url = None

            if len(datas) == 1:
                get_video_stream(title, cover, video_url, audio_url, None, None)
            else:
                get_video_stream(title, cover, video_url, audio_url, j + 1, 'P' + str(j + 1) + ' ' + subtitle)


def bangumi_download(url_input, id_type, mode):
    the_id = get_id(url_input, id_type)
    ep_ids, cover, title, subtitles, accept_quality = get_bangumi_info(id_type, the_id)

    if mode == '单集':
        print('请选择要下载的单集（阿拉伯数字）', end='')
        correct_input = False
        while not correct_input:
            index = input('请选择要下载的单集（阿拉伯数字）')
            if index.isnumeric() and int(index) - 1 < len(ep_ids):
                index = int(index) - 1
                correct_input = True
            else:
                print('请输入正确的集数')

    if os.path.exists(title):
        x = 1
        while os.path.exists(title + str(x)):
            x += 1
        title = title + str(x)
    video_quality = None
    print(accept_quality)
    while video_quality not in accept_quality:
        video_quality = input('选择视频分辨率')
    video_resolution = video_resolutions_encode[video_quality]

    if mode == '单集':
        bangumi_video_url, bangumi_audio_url = get_bangumi_stream_info(ep_ids[index], video_resolution)
        get_video_stream(title, cover, bangumi_video_url, bangumi_audio_url, 1, subtitles[index])
    else:
        for i in range(len(ep_ids)):
            bangumi_video_url, bangumi_audio_url = get_bangumi_stream_info(ep_ids[i], video_resolution)
            get_video_stream(title, cover, bangumi_video_url, bangumi_audio_url, i+1, subtitles[i])


if __name__ == "__main__":
    with open('default_data.json', 'r', encoding='utf-8') as default_data:
        default_info = json.load(default_data)
    video_resolutions_encode = default_info['video_resolutions_encode']
    video_resolutions_decode = default_info['video_resolutions_decode']
    audio_resolutions_sort = default_info['audio_resolutions_sort']
    vip = default_info['vip']

    with open('user_data.json', 'r', encoding='utf-8') as user_data:
        user_info = json.load(user_data)
    headers = {
        'referer': 'https://www.bilibili.com',
        'user-agent': user_info['User-Agent']
    }
    cookies = {'SESSDATA': user_info['SESSDATA']}
    store_path = user_info['path']

    input_url = input('请输入网址')

    video = None
    while video != 'yes' and video != 'no':
        video = input('下载视频(yes/no)')
    if video == 'yes':
        video = True
    else:
        video = False
    audio = None
    while audio != 'yes' and audio != 'no':
        audio = input('下载音频(yes/no)')
    if audio == 'yes':
        audio = True
    else:
        audio = False
    cover_download = None
    while cover_download != 'yes' and cover_download != 'no':
        cover_download = input('下载封面(yes/no)')
    if cover_download == 'yes':
        cover_download = True
    else:
        cover_download = False

    the_url = 'https://api.bilibili.com/x/web-interface/nav'
    the_request = requests.get(the_url, headers=headers, cookies=cookies)
    the_info = the_request.json()
    if the_info['code'] == -101:
        vip_accept = vip['-1']
    else:
        vipType = the_info['data']['vipType']
        if vipType == 0:
            vip_accept = vip['0']
        elif vipType == 1:
            vip_accept = vip['1']
        elif vipType == 2:
            vip_accept = vip['2']
    os.chdir(store_path)

    # 下载视频
    if 'BV' in input_url:
        video_download(input_url, 'BV')
    # 下载收藏夹
    elif 'ftype=create' in input_url:
        fav_download(input_url, 'fid=', 'fav')
    # 下载合集
    elif 'type=season' in input_url or 'ftype=collect' in input_url:
        if 'fid' in input_url:
            fav_download(input_url, 'fid=', 'collection')
        elif 'lists/' in input_url:
            fav_download(input_url, 'lists/', 'collection')
    elif 'sid' in input_url:
        fav_download(input_url, 'sid=', 'collection')
    # 下载动漫
    elif 'ss' in input_url:
        cover_download = False
        print('这是一部动漫，请选择下载内容')
        mode = input('下载（全部/单集）')
        while mode != '全部' and mode != '单集':
            mode = input('下载（全部/单集）')
        bangumi_download(input_url, 'ss', mode)
    elif 'ep' in input_url:
        cover_download = False
        print('这是一部动漫，请选择下载内容')
        mode = input('下载（全部/单集）')
        while mode != '全部' and mode != '单集':
            mode = input('下载（全部/单集）')
        bangumi_download(input_url, 'ep', mode)

    else:
        print('无效的视频链接')
