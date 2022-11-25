from typing import Counter
from bs4 import BeautifulSoup
from bs4.element import Tag
from feedparser.api import parse
import sqlite3
import sys,os,time,re,requests
import csv,json
import xmltodict
import feedparser
import tweepy
import discord
from discord.ext import tasks
from selenium import webdriver
import chromedriver_binary
import time, selenium.webdriver
from discordwebhook import Discord
import datetime
import subprocess


def wgetc(url):
    subprocess.run(["wget","-N",url],cwd=r"/Users/自身のファイル名")

def e_xml(url):
    response = requests.get(url,headers={'Cache-Control': 'no-cache'})
    #成功200

    if response.status_code== 200:

        response.encoding = response.apparent_encoding
        xml = response.text
        
        file = open('data/new.xml', 'w')
        file.write(xml)
        file.close()
        print("new.xml complete!")


def getRssFeedData():
    url = 'http://localhost:7001/data/e.xml'#'https://www.data.jma.go.jp/developer/xml/feed/eqvol_l.xml'
    wgetc(url)
    # アクセスするrdfのURLを記載
    RSS_URL = 'data/e.xml'#'data/eqvol_l.xml'#'http://www.data.jma.go.jp/developer/xml/feed/eqvol.xml'
    #RSS_URL='http://www.data.jma.go.jp/developer/xml/feed/eqvol_l.xml'
    xml = feedparser.parse(RSS_URL)
    for entry in xml.entries:
        if (entry.title == '震度速報'):
            eid=entry.id
            #print(entry.title)
            break

        if (entry.title == '震源・震度に関する情報'):
            eid=entry.id
            #print(entry.title)
            break

        eid=None
    return eid

# URLが更新されたかチェック
def check():
    rss_url = getRssFeedData()
    #print(rss_url)
    #rss_url='https://www.data.jma.go.jp/developer/xml/data/20220316143844_0_VXSE51_270000.xml'
    path = 'data/latest_url.txt'
    #print(rss_url)
    if (rss_url == None):
        print('新着情報はありませんでした 1')
    else:
        # latest_url.txtがなければ新規作成
        if not os.path.isfile(path):
            string = 'new file'
            with open(path, mode='w') as file:
                file.write(string)

        local_url = ''
        with open(path, mode='r') as file:
            local_url = file.read()
        #print(local_url)
        # 新着情報があるかチェック
        if (local_url == rss_url):
            print('新着情報はありませんでした 2')
            #pass
        #情報が更新されていない場合はここで処理が終わります。
        else:
        
            #lineNotify(rss_url)
            with open(path, mode='w') as file:
                string = rss_url
                file.write(string)
            print('新着情報があったので通知しました')
            #print(rss_url)
            e_xml(rss_url)
            return True

   
def screen_shot():
    driver = webdriver.Chrome()

    driver.set_window_size(1920, 1080)

    driver.get('http://localhost:8095/')
    time.sleep(5)
    driver.save_screenshot('data/images/screenshot.png')
    driver.quit()

def perse():
    z=check()
    if z==True:
        savename = 'data/new.xml'
        xml = open(savename, "r", encoding="utf-8").read()#XMLよみこみ
        soup = BeautifulSoup(xml, 'xml')

        # sqlite3にcsvを都度展開する
        connection = sqlite3.connect(":memory:")
        terminal = connection.cursor()


        #sqlite memory area
        terminal.execute("create table area(id integer primary key,area_name text,latitude real,longitude real);")
        with open('jma_area.csv','rt')as f:
            b = csv.reader(f)
            for t in b:
                terminal.execute('insert into area values (?,?,?,?);', t)
            #参考：https://www.teamxeppet.com/python-sqlite3-intro/#toc4
            #.mode csv は使えない　らしい...。

        #print(terminal.fetchall)

        #sqlite memory city
        terminal.execute("create table city(id integer primary key,city_name text,latitude real,longitude real);")
        with open('data/jma_city.csv','rt')as f:
            b = csv.reader(f)
            for t in b:
                terminal.execute('insert into city values (?,?,?,?);', t)
                #参考：https://www.teamxeppet.com/python-sqlite3-intro/#toc4
                #.mode csv は使えない　らしい...。
        connection.commit()
        terminal.execute('select * from area;')

        # 震源の座標を取得
        if soup.find('jmx_eb:Coordinate') is not None:
            epicenterStr = soup.find('jmx_eb:Coordinate').string

            # 分割
            epicenterCoord = re.split(r'(\-|\+|\/)', epicenterStr)
            # epicenterに入れる
            epicenter = {"type":"Feature",
                        "properties": {"class":"epicenter"},
                        "geometry":{
                            "type":"Point",
                            "coordinates":[float(epicenterCoord[3] + epicenterCoord[4]), float(epicenterCoord[1] + epicenterCoord[2])]
                            }
                        }
            epc=epicenter
            areaLevelFeatures = [epicenter]
            cityLevelFeatures = [epicenter]
    
        else:
            epicenter = {"type":"Feature",
                        "properties": {"class":"epicenter"},
                        "geometry":{
                            "type":"Point",
                            "coordinates":''
                            }
                        }
            epc=epicenter
            areaLevelFeatures = [epicenter]
            cityLevelFeatures = [epicenter]


        list_area=[]
        list_city=[]
        list_area.append(epc)
        list_city.append(epc)


        for p in soup.find_all('Pref'):
            #県をしゅとく
            #for a in p.find_all('Area'):
            for a in p.find_all('Area'):
                #print(a.text)            

                for city in a.find_all('City'):
                    #print(city)
                    for m in city.find_all('MaxInt'):
                        if m is not None:
                            maxint = m.text
                        else:
                            maxint = ""
                            print('error')
                    try:
                        for ccode in city.find_all('Code'):
                            #print(maxint)
                            terminal.execute("select latitude,longitude,city_name,id from city where id=" + ccode.text)
                            row = terminal.fetchone()
                            cityLevelFeatures={"type":"Feature","properties":{"class": maxint, "code": int(str(row[3])[:-2]), "name": row[2]},"geometry":{"type":"Point","coordinates": [row[1],row[0]]}}

                            list_city.append(cityLevelFeatures)
                        #print(list_city)
                    except TypeError:
                        code=city.find('Code')
                        #print(code)
                        terminal.execute("select latitude,longitude,city_name,id from city where id=" + code.text)
                        row = terminal.fetchone()
                        cityLevelFeatures={"type":"Feature","properties":{"class": maxint, "code": int(str(row[3])[:-2]), "name": row[2]},"geometry":{"type":"Point","coordinates": [row[1],row[0]]}}
                        list_city.append(cityLevelFeatures)

                #-----area がcity分のmaxint をとってきてしまうことを防ぐ。
                for tag in a.findAll("City"):
                    #tag.decompose()
                    for t in city.find_all(['Code','MaxInt']):
                        t.decompose()
                    tag.decompose()
                #print("-"*10)
                #---------------
                for m in a.find_all('MaxInt'):
            
                    if m is not None:
                        maxint = m.text
                        #print(maxint)
                    else:
                        maxint = ""
                        print('error')
             #print(cnt_area)
                try:
                    for c in a.find_all('Code'):
                        #print(c.text)
                        terminal.execute("select latitude,longitude,area_name,id from area where id=" + c.text)
                        row = terminal.fetchone()
                        #print(type(areaLevelFeatures))
                        #print(type(row[3]))
                        areaLevelFeatures={"type":"Feature","properties":{"class": maxint, "code": row[3], "name": row[2]},"geometry":{"type":"Point","coordinates": [row[1],row[0]]}}
                        #print(areaLevelFeatures)
                        list_area.append(areaLevelFeatures)
                        #list_area.append(epc)
                        #print(list_area)
                except TypeError:
                    code=a.find('Code')
            
                    terminal.execute("select latitude,longitude,area_name,id from area where id=" + code.text)
                    row = terminal.fetchone()
                    #print(type(row[3]))
                    areaLevelFeatures={"type":"Feature","properties":{"class": maxint, "code": row[3], "name": row[2]},"geometry":{"type":"Point","coordinates": [row[1],row[0]]}}

                
                
        colec='FeatureCollection'
        #print(row)
        areaLevelFeatureCollection = {"type":colec,"features":list_area}
        cityLevelFeatureCollection = {"type":colec,"features":list_city}             
        #print(areaLevelFeatureCollection)

        file = open('data/jma_area.json', 'w')
        json.dump(areaLevelFeatureCollection, file, ensure_ascii=False, indent=4, sort_keys=True, separators=(',',':'))
        
        file = open('data/jma_city.json', 'w')
        json.dump(cityLevelFeatureCollection, file, ensure_ascii=False, indent=4, sort_keys=True, separators=(',',':'))
        
        
        try:
            h=soup.find('Hypocenter')
            a=h.find("Area") 
        
            name=(a.find("Name")).text      
            #print(name)
            magunitude=(soup.find('jmx_eb:Magnitude')).text
            head=soup.find("Head")
            headline=head.find("Headline")
            text=(headline.find("Text")).text
            #print(text)
            h=soup.find('Intensity')
            a=h.find("Observation") 
            maxint=(a.find("MaxInt")).text  

            h=soup.find('Control')
            a=h.find('Title').text
            title=a

            jma_text={
            "title":title,
            "magunitude":magunitude,
            "name":name,
            "text":text,
            "maxint":maxint
            }
        except:
            h=soup.find('Headline')
            a=h.find('Text')
            text=(a).text
            h=soup.find('Control')
            a=h.find('Title').text
            title=a
            h=soup.find('Observation')
            a=h.find('MaxInt').text
            maxint=a
            
            
            jma_text={
                "title":title,
                "text":text,
                "maxint":maxint,
                "magunitude":"調査中",
                "name":"調査中",
            }
        

    
        file = open('data/jma_text.json', 'w')
        json.dump(jma_text, file, ensure_ascii=True, indent=4, sort_keys=True)

        # 後処理
        file.close()
        terminal.close()
        connection.close()
        print('perce complete!')

        screen_shot()
        print('screen shot...')
        #tweet()
        #print('tw posts ...')
        #new_msg()
        print('ds posts ...!')
        return 0
    else:
        return 1

import sizecheck
szl=[]
sumszl=0
while True:
    start = time.time()
    sum(range(50000000))
    dt_now = datetime.datetime.now()
    print(dt_now.strftime('%H:%M:%S'))
    #perse()
    path = 'data/eqvol_l.xml'
    path2= 'data/new.xml'
    #byte->
    sz=os.path.getsize(path)+os.path.getsize(path2)

    s=perse()
    if s==0:
        szl.append(sz)
    else:
        szl.append(0)
    if 2880<len(szl):
        del(szl[0])
    for i in szl:
        sumszl+=i
    print(len(szl))
    print('[一回あたり:'+sizecheck.convert_size(sz)+']')
    print('[24時間あたり:'+sizecheck.convert_size(sumszl)+']')


    # チェック※適宜変更
    elapsed = time.time() - start
    print(f"[処理時間:{elapsed:.3f}s]")  # 秒
    #print(f"{elapsed * 1000:.0f}ms")  # ミリ秒

    print("-"*30)
    time.sleep(5)
