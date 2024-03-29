# -*- coding: utf-8 -*-
# ! /usr/bin/env python3

import json
import os
import re
import urllib.request
from bs4 import BeautifulSoup
import urljoin
from math import log10
import socket

LocalDir = "C:\\ximalaya\\"

socket.setdefaulttimeout(100)


def bsObjForm(url):
    print("Request url:" + url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ' 'Chrome/51.0.2704.63 Safari/537.36'}
    req = urllib.request.Request(url=url, headers=headers)
    html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')  # , 'ignore'
    bsObj1 = BeautifulSoup(html, "html.parser")
    return bsObj1


def getTrackLocalPath(albumTitle, trackTitle, trackIndex, fileExt):
    albumTitle = re.sub('[\/:*?"<>|]', '_', albumTitle)
    trackTitle = re.sub('[\/:*?"<>|]', '_', trackTitle)
    if fileExt == "":
        fileExt = ".m4a"
    # article_path = LocalDir + albumTitle + '/' + trackTitle + fileExt
    article_path = LocalDir + albumTitle+'/' + trackIndex + "-" + trackTitle+ fileExt
    return article_path


def isTrackExist(albumTitle, trackTitle, trackIndex, fileExt):
    articalPath = getTrackLocalPath(albumTitle, trackTitle, trackIndex, fileExt)
    if os.path.exists(articalPath):
        print('%s 文件已经存在' % articalPath)
        return True
    else:
        return False


def Schedule(a, b, c):
    '''
    a:已经下载的数据块
    b:数据块的大小
    c:远程文件的大小
   '''
    per = 100.0 * a * b / c
    if per > 100:
        per = 100
    # print ('%.2f%%' % per,'已下载的大小:',a*b,'文件大小:',c)
    # print '已经下载的数据块:',a#,'\n'
    # print '数据块的大小:',b#,'\n'
    # print '远程文件大小:',c,'\n'
    # print '已下载的大小:',a*b,'文件大小:',c


def auto_down(url, filename):
    try:
        urllib.request.urlretrieve(url, filename, Schedule)
    except urllib.ContentTooShortError:
        print('Network conditions is not good.Reloading.')
        auto_down(url, filename)


# 获得专辑信息，分析音频文件名称，所属专辑，下载地址，并将文件保存在本地
def getM4a(url, trackIndex):
    print("Get track file url:" + url + " index:" + trackIndex)
    bsObj = bsObjForm(url)
    soundInfo = bsObj.text
    try:
        jsonStr = json.loads(soundInfo)
    except:
        print("load json fail! str:" + soundInfo + " url:" + url)
        return
    album_title = jsonStr['album_title']
    play_path = jsonStr["play_path"]
    title = jsonStr["title"]

    fileExt = os.path.splitext(play_path)[1]
    if (fileExt == ""):
        fileExt = ".m4a"

    # 由于title里面可能包含不能作文件名称的字符，所以将这些字符去掉
    title = re.sub('[\/:*?"<>|]', '_', title)
    album_title = re.sub('[\/:*?"<>|]', '_', album_title)
    print(album_title, play_path, title)
    # 将单曲写入文件
    # 判断文件夹是否存在，如果不存在，则新建文件夹
    if os.path.exists(LocalDir + album_title + '/') == False:
        os.makedirs(LocalDir + album_title + '/')

    article_path = getTrackLocalPath(album_title, title, trackIndex, fileExt)

    print("m4a url:" + play_path + "\tlocal path:" + article_path)

    # 判断文件是否存在，如果存在，则不进行下载
    if os.path.exists(article_path):
        print('%s 文件已经存在' % title)
    else:
        # auto_down(play_path, article_path)
        urllib.request.urlretrieve(play_path,article_path,Schedule)


def getAlbumPages(soap, urlSetFinishedPages, urlSetPages):
    pageArray = soap.select(".e-3793817119 .page-link");
    for pageObj in pageArray:
        pageUrl = pageObj.attrs['href']
        urlSetPages.add(pageUrl)
        urlSetPages -= urlSetFinishedPages


def getTrackSoundUrl(trackId, trackIndex):
    trackInfoUrl = path_url = 'http://www.ximalaya.com/tracks/' + trackId + '.json'  # "http://www.ximalaya.com/revision/play/tracks?trackIds=" + trackId;
    getM4a(trackInfoUrl, trackIndex)


# 分析所属专辑内各文件地址
def getAlbumPageInfo(bsObj):
    scriptList = bsObj.select('html > body > script')
    for scriptObj in scriptList:
        if (scriptObj.text.find("window.__INITIAL_STATE__ = ") != -1):
            albumJsonStr = re.findall("{.*}}", scriptObj.text)[0]
            albumJson = json.loads(albumJsonStr)
            return albumJson
    return


baseUrl = "http://www.ximalaya.com"
# beginUrl = "/yinyue/5742865/"  # "/youshengshu/3977741"
beginUrl = "/renwen/7778088/"
pageCount = 2

urlSetFinishedPages = set()
urlSetUnfinishedPages = set()
urlSetErrorPages = set()

for i in range(1, pageCount + 1):
    urlSetUnfinishedPages.add(beginUrl + 'p' + str(i))

# urlSetUnfinishedPages.add( beginUrl )
# urlSetUnfinishedPages.add( "/youshengshu/6062943/")
# urlSetUnfinishedPages.add( "/renwen/6655240/" )
# urlSetUnfinishedPages.add( "/youshengshu/3757698/")
# urlSetUnfinishedPages.add( "/renwen/7651313/")

while (len(urlSetUnfinishedPages) > 0):
    print("unfinished pages:" + str(urlSetUnfinishedPages))
    unfinishedUrl = urlSetUnfinishedPages.pop()
    fullUrl = unfinishedUrl
    if (unfinishedUrl.find("http://") != 0):
        fullUrl = baseUrl + unfinishedUrl  # urljoin.url_path_join( baseUrl, unfinishedUrl )
    bsObj = bsObjForm(fullUrl)
    if bsObj:
        urlSetFinishedPages.add(unfinishedUrl)
    else:
        urlSetErrorPages.add(unfinishedUrl)
        continue
    getAlbumPages(bsObj, urlSetFinishedPages, urlSetUnfinishedPages)
    albumJson = getAlbumPageInfo(bsObj)
    if (albumJson == None):
        urlSetErrorPages.add(unfinishedUrl)
        continue

    albumInfoJson = albumJson["AlbumDetailPage"]["albumInfo"]
    albumId = albumInfoJson["albumId"]
    albumCoverImgUrl = albumInfoJson["mainInfo"]["cover"]
    albumTitle = albumInfoJson["mainInfo"]["albumTitle"]
    albumPlayCount = albumInfoJson["mainInfo"]["playCount"]
    albumIsFinished = albumInfoJson["mainInfo"]["isFinished"]
    print("album id:" + str(albumId) + " Cover:" + albumCoverImgUrl + " Title:" + albumTitle + " PlayCount:" + str(
        albumPlayCount) + " IsFinished:" + str(albumIsFinished))

    allTrackNum = int(albumJson["AlbumDetailTrackList"]["tracksInfo"]["trackTotalCount"])
    print("All track num:" + str(allTrackNum))
    tracksInfoArray = albumJson["AlbumDetailTrackList"]["tracksInfo"]["tracks"]

    indexWidth = int(0.5 + log10(allTrackNum)) + 1
    indexFormatStr = "%0" + str(indexWidth) + "d"

    for tracksInfo in tracksInfoArray:
        trackId = str(tracksInfo["trackId"])
        trackIndex = indexFormatStr % int(tracksInfo["index"])
        trackName = tracksInfo["title"]
        isPaid = str(tracksInfo["isPaid"])
        print("track index:" + trackIndex + " id:" + trackId + " title:" + trackName + " isPaid:" + isPaid)
        if (isTrackExist(albumTitle, trackName, trackIndex, "")):
            continue
        else:
            getTrackSoundUrl(trackId, trackIndex)

print("Finished urls:" + str(urlSetFinishedPages))
print("Error urls:" + str(urlSetErrorPages))
