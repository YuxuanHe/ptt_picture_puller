import requests
import os
from bs4 import BeautifulSoup
import itchat
import time
from hanziconv import HanziConv

BASE_PTT_URL = 'https://www.ptt.cc'

class ArticleInfo:
    def __init__(self,title, url, likes):
        self.title = title
        self.url = url
        self.likes = likes
    def __str__(self):
        return 'Likes:' + self.likes + ' ' + self.title + '\n\t' + self.url

def Simplified2Traditional(sentence):
    sentence = HanziConv.toTraditional(sentence)
    return sentence

def getHtmlPage(url):
    response = requests.get(
                    url = url, cookies={'over18': '1'}, verify=True, timeout=3
                )
    if response.status_code != 200:
        raise Exception('Invalid url:' + url)
    return response

def getArticles(url, count):
    if count == 0:
        return []
    response = getHtmlPage(url)
    soup = BeautifulSoup(response.text, 'lxml')
    previousPageUrl = BASE_PTT_URL + soup.find_all('a', 'btn wide')[1]['href']
    divs = soup.find_all("div", "r-ent")

    articles = []
    for div in divs:
        try:
            title = str(div.find('div','title').find('a').string)
            href = str(div.find('a')['href'])
            nrec = str(div.find('div','nrec').string)
            articles.append(ArticleInfo(title, BASE_PTT_URL + href, nrec))
        except:
            pass
    return articles + getArticles(previousPageUrl, count-1)

def isPopular(likes, likes_count):
    if likes_count == 0:
        return True
    return likes == '爆' or (likes != 'None'and not likes.startswith('X') and int(likes) > likes_count)

def doesKeyWordExist(keyword, title):
    return (not keyword or keyword in title) and not '[公告]' in title

def getAllArticles(index_count, likes_count, board, keyword):
    latestPageUrl = BASE_PTT_URL + '/bbs/' + board + '/index' + '.html'
    articles = getArticles(latestPageUrl, int(index_count))
    filtered_articles = []
    for article in articles:
        if not doesKeyWordExist(Simplified2Traditional(keyword), article.title) or not isPopular(article.likes, int(likes_count)):
            continue
        filtered_articles.append(str(article))
    # TODO -- Add images here
    return filtered_articles

def get_ptt_response(msg):
    if msg['ToUserName'] == 'filehelper':
        args = msg['Text'].split()
        if len(args) == 4:
            return getAllArticles(args[0], args[1], args[2], args[3])
        elif len(args) == 3:
            return getAllArticles(args[0], args[1], args[2], '')
        elif len(args) == 2:
            return getAllArticles(args[0], 20, args[1], '')
        elif len(args) == 1:
            return getAllArticles(1, 0, args[0], '')
        else:
            raise Exception('Invalid input args count')

def get_ptt_reponse_with_error_handling(msg):
    try:
        return get_ptt_response(msg)
    except Exception as e:
        return [str(e)]

@itchat.msg_register(itchat.content.TEXT)
def ptt_wechat_reply(msg):
    replies = get_ptt_reponse_with_error_handling(msg)
    for reply in replies or []: 
        itchat.send(reply, 'filehelper')
        time.sleep(3)

itchat.auto_login(hotReload=True, enableCmdQR=2)
itchat.run()

