import PyPDF2
import os
from PriorityQueue import PriorityQueue
import string
import urllib.request
import requests
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urldefrag
from langdetect import detect
import ssl
import re


# context = ssl._create_unverified_context()
TIMEOUT = 10
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

class Crawler:
    def __init__(self, max_links, max_pages, max_retries, model, vectorizer):
        self.max_links = max_links
        self.max_pages = max_pages
        self.model = model
        self.vectorizer = vectorizer

        context = ssl._create_unverified_context()
        self.session = requests.Session()
        crawlAdapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
        self.session.mount('https://', crawlAdapter)
        self.session.mount('http://', crawlAdapter)

    #initial crawl function, takes seed page as input, returns the list of found documents
    def crawl_site(self, seed, max_found, crawl_pdfs):
        uni_key_words = self.get_home_words(seed);

        tocrawl = PriorityQueue()
        tocrawl.put(1, seed)
        crawled = []
        # syllabi = PriorityQueue()
        found_syllabi = []
        count = 0

        uni_content, outlinks = self.get_content(seed, uni_key_words, count)

        count += 1
        try:
            lang = str(detect(uni_content))
        except:
            lang = 'not_detected'

        # print("language: " + lang)
        if lang == "en":
            print("crawled_uni")
            while not tocrawl.is_empty() and len(crawled) < self.max_pages and len(found_syllabi) < max_found:
                popped = tocrawl.pop()
                page = popped[1]
                valid_type = True
                invalid_types = ['.ashx', '.doc', '.jpg', '.JPG', '.xlsx',
                             '.ods', '.ppt', '.png', '.zip', '.mp3', '.ics', '.jpeg']
                if not crawl_pdfs:
                    invalid_types.append('.pdf')

                for type in invalid_types:
                    if type in page:
                        valid_type = False
                        break

                if page not in crawled and valid_type:     #can check for pdf and skip here
                    count += 1
                    content, outlinks = self.get_content(page, uni_key_words, count)

                    page_features = self.prepare_page(content)

                    prediction = self.model.predict(page_features)
                    print(page)
                    print(prediction)
                    if prediction == 'yes':
                        found_syllabi.append(page)

                    # if popped[0] >= syllabi.lowest_rank():
                    #     syllabi.put(popped[0], popped[1])
					#
                    #     if syllabi.length() > 50:
                    #         syllabi.chop()

                    self.union(tocrawl, outlinks)
                    crawled.append(page)

        return found_syllabi

    def union(self, toCrawl, outlinks):
        addresses_to_crawl = toCrawl.values()
        for e in outlinks:
            if e[1] not in addresses_to_crawl:
                toCrawl.put(e[0], e[1])

    # gets the links from the content of a page and generates their priorities
    def get_ranked_links(self, html_soup, page, uni_keys):
        links = PriorityQueue()
        for link in html_soup.findAll('a'):
            rank = 0
            if link.has_attr('href'):
                address = link.get('href')
                if not self.is_absolute(address):
                    address = urljoin(page, address)
                address = urldefrag(address)
                address = address[0]
                if regex.search(address):
                    rank += self.gen_priority(address, uni_keys)
                    links.put(rank, address)
        return links.top_N(self.max_links)


    def is_absolute(self, url):
        return bool(urlparse(url).netloc)

    # generates a priority for a link based off keywords which are specific to the type of document being searched for
    def gen_priority(self, link, unikeys):
        priority = 0

        low_link = link.lower()

        for word in unikeys:
            if type(word) is str:
                if word.lower() in low_link:
                    priority = priority + 200

        for word in keywords.keys():
            if word.lower() in low_link:
                priority = priority + keywords[word]

        for word in negative_identifiers:
            if word.lower() in low_link:
                priority = priority - 1000
        return priority

    # pulls keywords from the title of a page, used for setting priorities based off university name etc.
    def get_home_words(self, home_page):
        # print("home page is : " + str(home_page))
        s = set(stopwords.words('english'))
        common_words = ["university", "college", "institute", "technology", "home", "the", "science"]
        try:
            response = self.session.get(home_page, headers={'User-Agent': 'Mozilla/5.0'}, timeout=TIMEOUT)
        except:
            print("couldn't access page")
            return None, None

        html = response.content
        html_soup = BeautifulSoup(html, 'html.parser')

        if not html_soup.title:
            print("No title")
            return None, None

        title_words = []
        if type(html_soup.title.stringg) is str:
            title = html_soup.title.string.lower()
            title_words = list(filter(lambda w: not w in s, title.split()))
            title_words = list(filter(str.isalpha, title_words))

        for word in common_words:
            if word in title_words:
                title_words.remove(word)

        # parsed_url = urlparse(home_page)
        # print(title_words)
        return title_words

    # returns the text content of the document which the link points to
    def get_content(self, link, uni_key_words, count):
        content = ''

        if '.pdf' in link:
            try:
                response = urllib.request.urlopen(link)
            except Exception as e:  # requests.exceptions.ConnectionError:
                # logging.error(traceback.format_exc())
                # print("erronous page: " + str(link))                                                                      %%%%%%%%%%%%%%%%%
                return '', []

            with open('..\\temp_files\\pdf_' + str(count) + '.pdf', 'wb') as out_file:

                out_file.write(response.read())

            with open("..\\temp_files\\pdf_" + str(count) + '.pdf', 'rb') as pdf_obj:
                try:
                    read_pdf = PyPDF2.PdfFileReader(pdf_obj)
                except:
                    print("failed to read: " + link)
                    return '', []
                try:                                            # just added this try except to deal witha weird error about accessing num pages, may need to delete
                    if read_pdf.numPages < 12:
                        if read_pdf.isEncrypted:
                            read_pdf.decrypt("")
                            for i in range(0, read_pdf.numPages):
                                content = content + ' ' + read_pdf.getPage(0).extractText()
                        else:
                            content = content + ' ' + read_pdf.getPage(0).extractText()
                    else:
                        print("too long: " + link)
                except:
                    return '', []
            outlinks = []
            os.remove("..\\temp_files\\pdf_" + str(count) + '.pdf')
        else:
            try:
                response = self.session.get(link, headers={'User-Agent': 'Mozilla/5.0'}, timeout=TIMEOUT)
            except Exception as e:  # requests.exceptions.ConnectionError:
                # logging.error(traceback.format_exc())
                print("erronous page: " + str(link))
                return '', []
            html = response.content
            soup = BeautifulSoup(html, 'lxml')

            outlinks = self.get_ranked_links(soup, link, uni_key_words)

            for script in soup(["script", "style"]):
                script.decompose()  # rip it out

            # get text
            content = soup.get_text()

        return content, outlinks

    # converts text of a page to the representation being used by the classifier
    def prepare_page(self, text):
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))



        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = ' '.join(chunk for chunk in chunks if chunk)

        text = text.translate(translator)

        lower_case = text.lower()  # Convert to lower case
        letters_only = re.sub("[^a-zA-Z]", " ", lower_case)
        words = letters_only.split()  # Split into words

        # Remove stop words from "words"
        stops = set(stopwords.words("english"))
        words = [w for w in words if not w in stops]
        words =  " ".join(words)
        data_features = self.vectorizer.transform([words])
        data_features = data_features.toarray()
        return data_features

