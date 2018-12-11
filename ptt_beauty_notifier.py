import requests
import os
from bs4 import BeautifulSoup

BASE_PTT_URL = 'https://www.ptt.cc'

def download_image(image_url, dir_name):
    response = requests.get(image_url)
    with open(dir_name + '/' + image_url.split('/')[-1], 'wb') as f:
        f.write(response.content)
    f.close()

def getHtmlPage(url):
    response = requests.get(
                    url = url, cookies={'over18': '1'}, verify=True, timeout=3
                )
    if response.status_code != 200:
        raise Exception('Invalid url:' + url)
    return response

def getArticlesInLatestPage(board):
    latestPageUrl = BASE_PTT_URL + '/bbs/' + board + '/index' + '.html'
    response = getHtmlPage(latestPageUrl)
    soup = BeautifulSoup(response.text, 'lxml')
    divs = soup.find_all("div", "r-ent")
    articles = []
    for div in divs:
        try:
            href = div.find('a')['href']
            articles.append(BASE_PTT_URL + href)
        except:
            pass
    return articles

def main():
    articles = getArticlesInLatestPage('Beauty')
    for article in articles:
        response = getHtmlPage(article)
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.title.string
        if '正妹' not in title: 
            continue
        dir_name = './ptt_photos/' + title
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        else:
            print('已经存在， 跳过')
        for picture in soup.findAll('a', href = True):
            if '.jpg' in str(picture.string):
                download_image(picture.string, dir_name)


if __name__ == '__main__':
    main()


