#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib.request
import time
from bs4 import BeautifulSoup
import itertools
import time
import requests

from line_notify import LineNotify

## สำหรับทำ Progress Bar
import time
import progressbar


tag_value = "สถานที่ท่องเที่ยวต่างประเทศ"
last_id = 0
n_page = 100

ACCESS_TOKEN = "xFxSCXHfq1LUBW6eYGUNzeX4KrCv1IAfNFFEuc4aLll"

notify = LineNotify(ACCESS_TOKEN)


def getTopicByTag(tag_value, last_id, n_page):

    
    with progressbar.ProgressBar(max_value=n_page) as bar:
        my_data = {} # Topic and TID
        tag_list = {} # Tag Topic ID

        for p in range(n_page):
            json_search = "https://pantip.com/forum/topic/ajax_json_all_topic_tag"

            post_data = {'last_id_current_page': last_id , 
                'dataSend[tag]' : urllib.parse.quote(tag_value),
                'dataSend[topic_type][type]' : 0, 
                'dataSend[topic_type][default_type]' : 1, 
                'thumbnailview': False, 'current_page' : p+1
            }

            query_string = urllib.parse.urlencode(post_data)   
            data = query_string.encode("utf-8") 
            header = {'X-Requested-With': 'XMLHttpRequest'}

            req = urllib.request.Request(json_search,headers=header)
            search_response = urllib.request.urlopen(req,data)
            the_page = search_response.read().decode('utf-8-sig')
            y = json.loads(the_page)

            for i in y['item']['topic']:
                if 'disp_topic' in i:
                    topic_name = i['disp_topic']
    #                 if 'scb' in topic_name.lower():
                    last_id = i['_id']
                    my_data.setdefault(topic_name,[])
                    my_data[topic_name].append(last_id)
                    for t in i['tags']:
                        tag_name = t['tag']
                        tag_list.setdefault(last_id,[])
                        tag_list[last_id].append(tag_name)

            time.sleep(1.5)
#             print("crawl page ", p+1)
            bar.update(p)
        
    return my_data, tag_list

def getTitleAndDescriptionTopic(tag_list):
    
    
    tid_list = list(tag_list.keys())
    titles = []
    descriptions = []
    i = 1
    with progressbar.ProgressBar(max_value=len(tid_list)) as bar:
        for tid in tid_list:
            """
            path for getiing data
            title and description
            """
            response = urllib.request.urlopen("https://pantip.com/topic/{}".format(tid))
            raw_html = response.read()
            html = raw_html.decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')

            title = soup.title.get_text(strip=True)
            description = soup.find(class_='display-post-story').get_text(strip=True)
            titles.append(title)
            descriptions.append(description)
            bar.update(i)
            i += 1

    return titles, descriptions

def saveTitleAndDescriptionTopic(titles, descriptions, tag_list):
    """
    path saving data in text files
    title and description
    """

    pantip_data = ""

    # Filter by 'scb' key words
    for i, j, k in zip(titles, descriptions, list(tag_list.values())):
        pantip_data += (i + "|" + j + "|" + ','.join(k) + "\n")

    # ส่วน Save Text files            
    with open('output-data/travel_topic_des_22102018/travel_and_des.txt', 'a', encoding='utf-8') as out:
        out.write(pantip_data)
    out.close()

    return notify.send("Your data has been saved Completely!!", sticker_id=132, package_id=1)




if __name__ == '__main__':
    _, tag_list = getTopicByTag(tag_value, last_id, n_page)
    print("Check Length tid: ",len(tag_list))
    titles, descriptions = getTitleAndDescriptionTopic(tag_list)
    print("Check Length title: ",len(titles))
    print("Check Length description: ",len(descriptions))
    saveTitleAndDescriptionTopic(titles, descriptions, tag_list)