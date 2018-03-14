import requests
import urllib.parse
from bs4 import BeautifulSoup
import json
import sys


URL = "https://www.ptt.cc/bbs/Beauty/index2000.html"
NOT_EXIST = BeautifulSoup('<a>本文已被刪除</a>', 'lxml').a
open('all_article.txt', 'w').close()
open('all_popular.txt', 'w').close()
def get_posts_on_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    posts = list()
    for article in soup.find_all('div', 'r-ent'):
        meta = article.find('div', 'title').find('a') or NOT_EXIST
        #print(meta)
        if meta==NOT_EXIST:
            continue
        link = meta.get('href')
        link = urllib.parse.urljoin(URL, link)
        title = meta.getText().strip()

        if title.find('[公告]')>-1:
            print("$$$$$$$$$$$$",title.find('[公告]'), meta)
            continue
        if not check(link, '2017'):
            continue
            #break

        posts.append({
            'title': meta.getText(),
            'link': link,#meta.get('href'),
            'push': article.find('div', 'nrec').getText(),
            'date': article.find('div', 'date').getText().strip().replace('/',""),
            'author': article.find('div', 'author').getText(),
        })
        with open('all_article.txt','a', encoding='UTF-8') as article_f:
            info = posts[-1]['date'] + ',' + posts[-1]['title'] + ',' + posts[-1]['link'] + '\n'
            #print(info)
            article_f.write(info)
            if posts[-1]['push'] =='爆':
                with open('all_popular.txt', 'a', encoding='UTF-8') as article_f:
                    article_f.write(info)
        #exit(1)
    next_link = soup.find('div', 'btn-group-paging').find_all('a', 'btn')[2].get('href')

    return posts, next_link


def get_pages(num):
    page_url = URL
    all_posts = list()
    for i in range(num):
        print ("////////////////////////////////////////////////////////////////////////////PAGE:",i)
        posts, link = get_posts_on_page(page_url)
        all_posts += posts
        page_url = urllib.parse.urljoin(URL, link)
    json.dump(all_posts, open("mydict.txt",'w'))
    return all_posts

def check(link, year):
    #article_url = urllib.parse.urljoin(URL, link)
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    #print("#########################################")
   # print(soup.find_all('div', 'article-metaline'))
    if not soup.find_all('div', 'article-metaline'):
        return True
    time = soup.find_all('div', 'article-metaline')[-1].find('span', 'article-meta-value').getText()
    print(time)
    my_year = time.split(' ')[-1]

    print(my_year)
    if my_year=='2018' or my_year=='2016':
        return False
    else:
        return True
    '''
    if my_year == year:
        print('yes')
        return True
    else:
        print('no')
        return False
    '''
def push(start, end):
    print("push...")
    all_posts = json.load(open("mydict.txt"))
    print((all_posts))




if __name__ == '__main__':
    pages = 355#2000~2352
    if sys.argv[1]=='crawl':
        for post in get_pages(pages):
            print(post['push'], post['title'], post['date'], post['author'])
    if sys.argv[1] == 'push':
        push(sys.argv[2], sys.argv[3])



