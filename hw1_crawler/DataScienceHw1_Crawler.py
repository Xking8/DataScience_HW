import requests
import urllib.parse
from bs4 import BeautifulSoup
import json
import sys


URL = "https://www.ptt.cc/bbs/Beauty/index2000.html"
NOT_EXIST = BeautifulSoup('<a>本文已被刪除</a>', 'lxml').a
IGNORE = ["https://www.ptt.cc/bbs/Beauty/M.1490936972.A.60D.html",
        "https://www.ptt.cc/bbs/Beauty/M.1494776135.A.50A.html",
        "https://www.ptt.cc/bbs/Beauty/M.1503194519.A.F4C.html",
        "https://www.ptt.cc/bbs/Beauty/M.1504936945.A.313.html",
        "https://www.ptt.cc/bbs/Beauty/M.1505973115.A.732.html",
        "https://www.ptt.cc/bbs/Beauty/M.1507620395.A.27E.html",
        "https://www.ptt.cc/bbs/Beauty/M.1510829546.A.D83.html",
        "https://www.ptt.cc/bbs/Beauty/M.1512141143.A.D31.html"]
def get_posts_on_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    posts = list()
    populars = list()
    for article in soup.find_all('div', 'r-ent'):
        meta = article.find('div', 'title').find('a') or NOT_EXIST
        #print(meta)
        if meta==NOT_EXIST:
            continue
        link = meta.get('href')
        link = urllib.parse.urljoin(URL, link)
        if link in IGNORE:
            continue
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
                populars.append({
                    'title': meta.getText(),
                    'link': link,  # meta.get('href'),
                    'push': article.find('div', 'nrec').getText(),
                    'date': article.find('div', 'date').getText().strip().replace('/', ""),
                    'author': article.find('div', 'author').getText(),
                })
                with open('all_popular.txt', 'a', encoding='UTF-8') as popular_f:
                    popular_f.write(info)
        #exit(1)
    next_link = soup.find('div', 'btn-group-paging').find_all('a', 'btn')[2].get('href')

    return posts, populars, next_link


def get_pages(num):
    page_url = URL
    all_posts = list()
    all_populars = list()
    for i in range(num):
        print ("////////////////////////////////////////////////////////////////////////////PAGE:",i)
        posts, populars, link = get_posts_on_page(page_url)
        all_posts += posts
        all_populars += populars
        page_url = urllib.parse.urljoin(URL, link)
    json.dump(all_posts, open("all_article_list.txt",'w'))
    json.dump(all_populars, open("all_popular_list.txt", 'w'))
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
def push_rank(start, end, push_file):
    print("ranking push...")
    all_posts = json.load(open("all_article_list.txt"))

    #print((all_posts))
    push_rank = {}
    boo_rank = {}
    push_count = 0
    boo_count = 0
    for post in all_posts:
        if int(post['date']) < int(start):
            continue
        elif int(post['date']) > int(end):
            break
        print(post['link'])
        response = requests.get(post['link'])
        #response = requests.get('https://www.ptt.cc/bbs/Beauty/M.1492519470.A.B6E.html')
        soup = BeautifulSoup(response.text, 'html.parser')
        pushes = soup.find_all('div', 'push')
        #print(pushes)
        for push in pushes:
            #print(push)
            pushtag = push.find('span', 'push-tag')
            pushid = push.find('span', 'push-userid')
            if not pushtag:
                continue
            pushtag = pushtag.getText()
            pushid = pushid.getText()
            #print(pushtag)
            if pushtag.find('推')>-1:
                push_count += 1
                if pushid not in push_rank:
                    push_rank[pushid] = 0
                push_rank[pushid] += 1

            elif pushtag.find('噓')>-1:
                boo_count += 1
                if pushid not in boo_rank:
                    boo_rank[pushid] = 0
                boo_rank[pushid] += 1
        #print (push_rank)

        #break
    push_rank = sorted(push_rank.items(), key= lambda l:l[1], reverse=True)
    boo_rank = sorted(boo_rank.items(), key=lambda l: l[1], reverse=True)
    print(push_rank)
    rank_string = ""
    for i in range(10):
        rank_string = rank_string + "like #"+ str(i+1) + ": " +  push_rank[i][0] + " " + str(push_rank[i][1]) +"\n"
    for i in range(10):
        rank_string = rank_string + "boo #" + str(i + 1) + ": " + boo_rank[i][0] + " " + str(boo_rank[i][1]) + "\n"
        #rank_string = rank_string + "like #"+ str(i+1) + ": " +  list(boo_rank)[i] + " " + str(boo_rank.get(list(boo_rank)[i])) +"\n"

    with open(push_file, 'a', encoding='UTF-8') as push_f:
        push_f.write("all like: " + str(push_count) + "\n")
        push_f.write("all boo: " + str(boo_count) + "\n")
        push_f.write(rank_string)
    print("push_count", push_count)
    print("boo_count", boo_count)
def popular(start, end, popular_file):
    all_populars = json.load(open("all_popular_list.txt"))
    popular_count = 0
    img_urls = ""
    for popular in all_populars:

        if int(popular['date']) < int(start):
            continue
        elif int(popular['date']) > int(end):
            break
        popular_count += 1
        response = requests.get(popular['link'])
        print(popular['link'])
        soup = BeautifulSoup(response.text, 'html.parser')
        for img_cand in soup.find_all('a'):
            img_cand = img_cand.get('href')
            #print(img_cand)
            imgtype = ['.jpg', '.jpeg', '.png', '.gif', '.JPG', '.JPEG', '.PNG', '.GIF']
            if any(ty in img_cand[-5:] for ty in imgtype): #結尾
                img_urls = img_urls + img_cand +"\n"
                print(img_cand)
    with open(popular_file, "a", encoding='UTF-8') as popular_f:
        popular_f.write("number of popoular articles: " + str(popular_count) + "\n")
        popular_f.write(img_urls)
    print(img_urls)



if __name__ == '__main__':
    pages = 355#2000~2352
    if sys.argv[1]=='crawl':
        open('all_article.txt', 'w').close()
        open('all_popular.txt', 'w').close()
        for post in get_pages(pages):
            print(post['push'], post['title'], post['date'], post['author'])
    if sys.argv[1] == 'push':
        push_file = "push[" + sys.argv[2] + "-" + sys.argv[3] + "].txt"
        open(push_file, 'w').close()
        push_rank(sys.argv[2], sys.argv[3], push_file)
    if sys.argv[1] == "popular":
        popular_file = "popular[" + sys.argv[2] + "-" + sys.argv[3] + "].txt"
        open(popular_file, 'w').close()
        popular(sys.argv[2], sys.argv[3], popular_file)




