from MyPriorityQueue import MyPriorityQueue
from urllib.request import Request, urlopen
import requests
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urldefrag
import ssl
import re

MAX_RETRIES = 20
MAX_LINKS = 10
MAX_PAGES = 50

context = ssl._create_unverified_context()


'''
    GENERAL CRAWLER NOTES:
Need to handle pdfs, do I just ignore them for now
'''

regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

keywords = {
        '.edu': 100,
        'computer': 450,
        'computing': 250,
        'science': 50,
        'programming': 400,
        'algorithm': 300,
        'syllabus': 300,
        'module': 150,
        'course': 150,
        'intro': 100,
        'school': 100,
        'c++': 100,
        'java': 100,
        'scheme': 100,
        'python': 100,
        'functional': 200,
        'coding': 300,
        'engineering': 50,
        'software': 150,
        'data': 100,
        'undergraduate': 1300,
        'major': 150
    }

negative_identifiers = [
        'visitor',
        'tour',
        'services',
        'story',
        'graduate',
        'campus',
        'fellowship',
        'scholarship',
        'stories',
        'facilities',
        'life',
        'earth',
        'geo',
        'bio',
        'public',
        'laboratory',
        'chem',
        'medicine',
        'vet',
        'research',
        'accounting',
        'cognitive',
        'political',
        'psych',
        'genetics',
        'criminal',
        'justice',
        'environment',
        'law',
        'history',
        'literature',
        'economics',
        'english',
        'linguistics',
        'wikipedia',
        'art',
        'liberal',
        'leader',
        'theatre',
        'dance',
        'archaeology',
        'classic',
        'faq',
        'business',
        'dental',
        'computer-labs',
        'health',
        'news',
        'neuro',
        'linkedin',
        'pinterest',
        'coursera',
        'blog',
        'google',
        'gradschool',
        'twitter',
        'youtube',
        'gmail',
        'facebook',
        'shop',
        'instagram',
        'profile',
        'vision',
        'github'
    ]

#initial crawl function, takes seed page as input
def crawl_site(seed):
    crawlSession = requests.Session()
    crawlAdapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
    session.mount('https://', crawlAdapter)
    session.mount('http://', crawlAdapter)

    uni_key_words = get_home_words(seed, crawlSession);

    tocrawl = MyPriorityQueue()
    tocrawl.put(1, seed)
    crawled = []
    syllabi = MyPriorityQueue()
    errors = []
    temp_best = MyPriorityQueue()      #temporary track of highest ranking links, will delete when ML implemented

    while not tocrawl.is_empty() and len(crawled) < MAX_PAGES:
        popped = tocrawl.pop()
        page = popped[1]
        valid_type = True
        for type in ['.pdf', '.ashx', '.doc', '.jpg', '.JPG', '.xlsx', '.ods', '.ppt', '.png']:
            if type in page:
                valid_type = False
                break

        if page not in crawled and valid_type:     #can check for pdf and skip here
            try:
                response = crawlSession.get(page, headers={'User-Agent': 'Mozilla/5.0'})
            except Exception as e:  # requests.exceptions.ConnectionError:
                # logging.error(traceback.format_exc())
                errors.append(page)
                print("erronous pages: " + str(len(errors)))
                print(errors)
                continue
            html = response.content
            soup = BeautifulSoup(html, 'lxml')

            if (popped[0] > temp_best.lowest_rank()) and popped[1] not in temp_best.list():
                temp_best.put(popped[0], popped[1])
                if temp_best.length() > 10:
                    temp_best.chop()

            outlinks = get_ranked_links(soup, page, uni_key_words)

            if popped[0] >= syllabi.lowest_rank():
                syllabi.put(popped[0], popped[1])

                if syllabi.length() > 50:
                    syllabi.chop()

            union(tocrawl, outlinks)  # deal with union of outlinks and tocrawl
            crawled.append(page)

    return syllabi

def union(toCrawl, outlinks):
    addresses_to_crawl = toCrawl.values()
    for e in outlinks:
        if e[1] not in addresses_to_crawl:
            toCrawl.put(e[0], e[1])

def get_ranked_links(html_soup, page, uni_keys):
    links = MyPriorityQueue()
    for link in html_soup.findAll('a'):
        rank = 0
        if link.has_attr('href'):
            address = link.get('href')
            if not is_absolute(address):
                address = urljoin(page, address)
            address = urldefrag(address)
            address = address[0]
            if regex.search(address):
                rank += gen_priority(address, uni_keys)
                links.put(rank, address)
    return links.top_N(MAX_LINKS)


def is_absolute(url):
    return bool(urlparse(url).netloc)


def gen_priority(link, unikeys):
    priority = 0

    low_link = link.lower()

    # if seed.lower() in low_link:
    #     priority = priority + 500

    if unikeys:
        for word in unikeys:
            if word.lower() in low_link:
                priority = priority + 200

    for word in keywords.keys():
        if word.lower() in low_link:
            priority = priority + keywords[word]

    for word in negative_identifiers:
        if word.lower() in low_link:
            priority = priority - 1000
    return priority


def get_home_words(home_page, crawlSession):
    # print("home page is : " + str(home_page))
    s = set(stopwords.words('english'))
    common_words = ["university", "college", "institute", "technology", "home", "the", "science"]
    try:
        response = crawlSession.get(home_page, headers={'User-Agent': 'Mozilla/5.0'})
    except:
        print("couldn't access page")
        return None, None

    html = response.content
    html_soup = BeautifulSoup(html, 'html.parser')

    if not html_soup.title:
        print("No title")
        return None, None

    title = html_soup.title.string.lower()
    # print(title)
    title_words = list(filter(lambda w: not w in s, title.split()))
    title_words = list(filter(str.isalpha, title_words))

    for word in common_words:
        if word in title_words:
            title_words.remove(word)

    # parsed_url = urlparse(home_page)
    print(title_words)
    return title_words


file = open("seeds_for_false_cases")           #links.txt", "r")
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
session.mount('https://', adapter)
session.mount('http://', adapter)

count = 0
for line in file:
    if count > 228:
        print(line)
        l = line.rstrip('\n')
        l = 'http://' + l
        # req = Request(l, headers={'User-Agent': 'Mozilla/5.0'})
        # html = urlopen(req).read()
        crawl_site(l)
    count += 1



    # for link in soup.findAll('a'):
    #     if count == 5:
    #         break
    #     rank = 0
    #     if link.has_attr('href'):
    #         address = link.get('href')
    #         if not is_absolute(address):
    #             address = urljoin(l, address)
    #         address = urldefrag(address)
    #         address = address[0]
    #         print("defragged: " + str(address))
    #         if regex.search(address):
    #             try:
    #                 response = session.get(address, headers={'User-Agent': 'Mozilla/5.0'})
    #                 count += 1
    #             except Exception as e:  # requests.exceptions.ConnectionError:
    #                 logging.error(traceback.format_exc())
    #                 print("eeeror")
    #             # req = Request(address, headers={'User-Agent': 'Mozilla/5.0'})
    #             html = response.content  # urlopen(req).read()
    #             print(html)



