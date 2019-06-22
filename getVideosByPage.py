# -*- coding: utf-8 -*-
# ! /usr/bin/env python3

import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'
}

'''
提取专辑内的音频列表
参数：albumId 专辑ID
参数：pageNum 页号
'''
def get_track_list(albumId, pageNum):
    trackList = []
    # 音频列表地址
    url = 'https://www.ximalaya.com/revision/album/getTracksList?sort=1&albumId=' + str(albumId) + '&pageNum=' + str(pageNum)
    print(url)
    resp = requests.get(url, headers=headers)
    result = resp.json()
    print(result)
    if result['ret'] == 200:
        tracks = result['data']['tracks']
        for track in tracks:
            trackList.append({'trackId': track['trackId'], 'title': track['title']})
    return trackList


'''
获取音频下载地址

'''
def get_track_url(trackId):
    url = 'https://www.ximalaya.com/revision/play/tracks?trackIds=' + str(trackId)
    resp = requests.get(url, headers=headers)
    result = resp.json()
    if result['ret'] == 200:
        tracksForAudioPlay = result['data']['tracksForAudioPlay']
        if len(tracksForAudioPlay) > 0:
            return tracksForAudioPlay[0]['src']
    return ""


'''
下载音频文件

'''
def download_track(url, file):
    resp = requests.get(url, headers=headers, stream=True)
    with open(file, 'wb') as f:
        for data in resp.iter_content(chunk_size=1024):
            if data:
                f.write(data)


if __name__ == '__main__':
    albumId = 3977741
    pageNum = 1
    # 下载目录
    dir = 'C:/ximalaya/'
    trackList = get_track_list(albumId, pageNum)
    print('trackList ',trackList)
    for track in trackList:
        trackUrl = get_track_url(track['trackId'])
        if trackUrl:
            # 获取拓展名
            ext = trackUrl[trackUrl.rindex('.')]
            # 构建文件路径
            filePath = dir + track['title']+'.' + ext
            print('正在下载 ' + trackUrl)
            download_track(trackUrl, filePath)
