import requests
import os
from bs4 import BeautifulSoup
import itchat
import time

BASE_PTT_URL = 'https://www.ptt.cc'

class ArticleInfo:
    def __init__(self, url, likes):
        self.url = url
        self.likes = likes

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
            href = str(div.find('a')['href'])
            nrec = str(div.find('div','nrec').string)
            articles.append(ArticleInfo(BASE_PTT_URL + href, nrec))
        except:
            pass
    return articles + getArticles(previousPageUrl, count-1)

def isPopular(likes):
    return likes == '爆' or (likes != 'None'and not likes.startswith('X') and int(likes) > 20)

def getTitlesFromBoard(board, keyword):
    latestPageUrl = BASE_PTT_URL + '/bbs/' + board + '/index' + '.html'
    articles = getArticles(latestPageUrl, 5)
    titles = []
    for article in articles:
        response = getHtmlPage(article.url)
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.title.string
        if keyword not in title or not isPopular(article.likes):
            continue
        titles.append('Likes:' + article.likes + ' ' + title + '\n\t' + article.url)
    # TODO -- Add images here
    return titles


def get_ptt_response(msg):
    if msg['ToUserName'] == 'filehelper' and msg['Text'] == '正妹':
        return getTitlesFromBoard('Beauty', '正妹')
    else:
        return []


@itchat.msg_register(itchat.content.TEXT)
def ptt_wechat_reply(msg):
    replies = get_ptt_response(msg)
    for reply in replies: 
        itchat.send(reply, 'filehelper')
        time.sleep(3)

# itchat.auto_login(hotReload=True, enableCmdQR=True)
itchat.auto_login(enableCmdQR=2)
itchat.run()

