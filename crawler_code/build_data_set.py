import os
import urllib.request

import PyPDF2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords  # Import the stop word list
import re
import pandas as pd
import string
import ssl



# Method to build the overall dataset for storage of the training sets' data
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


# gets all the text from each link in the links list
def get_text_from_links(links):
	translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
	i = 0
	text_list = []
	for link in links:
		i += 1
		got_content = get_content_from_page(link, i)
		print("type" + str(type(got_content)))
		if got_content is not False:
			# break into lines and remove leading and trailing space on each
			lines = (line.strip() for line in got_content.splitlines())
			# break multi-headlines into a line each
			chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
			# drop blank lines
			text = ' '.join(chunk for chunk in chunks if chunk)
			text = text.translate(translator)
			text = trim_words(text)
			if len(text) > 100:
				text_list.append(text)
	return text_list

# returns the content from a page
def get_content_from_page(link, count):
	context = ssl._create_unverified_context()
	errors = []
	content = ''
	if '.pdf' in link:
		try:
			response = urllib.request.urlopen(link)
			print(str(count) + ". " + link)
		except Exception as e:  # requests.exceptions.ConnectionError:
			# logging.error(traceback.format_exc())
			errors.append(link)
			print("erronous pages: " + str(len(errors)))
			print(errors)
			return False

		with open('..\\temp_files\\pdf_' + str(count) + '.pdf', 'wb') as out_file:
			print("hereer")
			out_file.write(response.read())

		with open("..\\temp_files\\pdf_" + str(count) + '.pdf', 'rb') as pdf_obj:
			try:
				read_pdf = PyPDF2.PdfFileReader(pdf_obj)
			except:
				print("failed to read: " + link)
				return False

			if read_pdf.numPages < 12:
				if read_pdf.isEncrypted:
					read_pdf.decrypt("")
					for i in range (0, read_pdf.numPages):
						content = content + ' ' + read_pdf.getPage(0).extractText()
				else:
					content = content + ' ' + read_pdf.getPage(0).extractText()
			else:
				print("too long: " + link)

		print(content)
		os.remove("..\\temp_files\\pdf_" + str(count) + '.pdf')
	else:
		try:
			# req = urllib.request.Request(line, headers={'User-Agent': 'Mozilla/5.0'})
			response = urllib.request.urlopen(link, context=context)
			html = response.read()
			print(str(count) + ". " + link)

		except OSError:
			print("***** " + str(link))
			print(OSError.strerror)
			return False

		soup = BeautifulSoup(html, 'lxml')

		for script in soup(["script", "style"]):
			script.decompose()  # rip it out

		# get text
		content = soup.get_text()

	return content

def get_links_from_file(path):
	file = open(path, "r")
	links = []
	for line in file:
		links.append(line)
	return links

# preprocesses text for the feature generation step
def trim_words(content):
	lower_case = content.lower()  # Convert to lower case
	letters_only = re.sub("[^a-zA-Z]", " ", lower_case)
	words = letters_only.split()  # Split into words

	# Remove stop words from "words"
	stops = set(stopwords.words("english"))
	words = [w for w in words if not w in stops]
	return (" ".join(words))

# build_set(POSITIVE_URLS, NEGATIVE_URLS)


