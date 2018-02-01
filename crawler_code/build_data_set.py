import urllib.request
from bs4 import BeautifulSoup
from nltk.corpus import stopwords  # Import the stop word list
import re
import pandas as pd
import string
import ssl

LOCAL_PATH = "..\\data\\"
POSITIVE_URLS = "positive_urls.txt"
NEGATIVE_URLS = "model_1\\false_crawled_b10_d50.txt"


def build_set(positive_path, negative_path, output_file):
	links = []
	print("Getting links from file..")
	positive_links = links + get_links_from_file(positive_path)
	negative_links = links + get_links_from_file(negative_path)

	print("Getting text from links...")
	positive_strings = get_text_from_links(positive_links)
	negative_strings = get_text_from_links(negative_links)

	output = pd.DataFrame(data={"syllabus": ["yes"] * len(positive_strings) + ["no"] * len(negative_strings), "content": positive_strings + negative_strings})

	output.to_csv(output_file, index=False, quoting=3)


def get_text_from_links(links):
	context = ssl._create_unverified_context()
	translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
	i = 0
	text_list = []
	for link in links:
		i += 1
		try:
			# req = urllib.request.Request(line, headers={'User-Agent': 'Mozilla/5.0'})
			response = urllib.request.urlopen(link, context=context)
			html = response.read()
			print(str(i) + ". " + link)

		except OSError:
			print("***** " + str(link))
			print(OSError.strerror)
			continue
		soup = BeautifulSoup(html, 'lxml')

		for script in soup(["script", "style"]):
			script.decompose()  # rip it out

		# get text
		text = soup.get_text()

		# break into lines and remove leading and trailing space on each
		lines = (line.strip() for line in text.splitlines())
		# break multi-headlines into a line each
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
		# drop blank lines
		text = ' '.join(chunk for chunk in chunks if chunk)
		text = text.translate(translator)
		text = trim_words(text)
		text_list.append(text)
	return text_list

def get_links_from_file(path):
	file = open(LOCAL_PATH + path, "r")
	links = []
	for line in file:
		links.append(line)
	return links

def trim_words(content):
	lower_case = content.lower()  # Convert to lower case
	letters_only = re.sub("[^a-zA-Z]", " ", lower_case)
	words = letters_only.split()  # Split into words

	# Remove stop words from "words"
	stops = set(stopwords.words("english"))
	words = [w for w in words if not w in stops]
	return (" ".join(words))

# build_set(POSITIVE_URLS, NEGATIVE_URLS)


