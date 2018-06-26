from Crawler import Crawler
from build_data_set import build_set
import random_forest
import svm_classifier
import requests
import pandas as pd
import numpy as np
import json

MAX_RETRIES = 10	# number of times to retry downloading a page before moving on
MAX_LINKS = 10		# max links leading out of a page to extract and add to URL Frontier
MAX_PAGES = 100		# max number of pages to be crawled from a given seed
MAX_SYLLABI = 30	# max number of documents identified as a syllabus to return

POSITIVE_URLS = "positive_urls.txt"
NEGATIVE_URLS = "false_crawled_b10_d50.txt"
DATASET_PATH = "dataset13.csv"
OUTPUT = "found_syllabi_modell3.csv"
JSON = "found_json_model13.json"
CRAWL_PDFS = False				# Determines whether to crawl or skip found PDF files
BUILD_SET = False				# Whether the dataset needs to be built or if it already exists
FIRST_RUN = True				# Whether this is the first run or this is a continuation and a previous state must be loaded
TEST_CLASSIFIER = True			# Whether to test the classifier and generate a stats file
SVM_OVER_FOREST = False			# Whether to use the SVM or Random Forest classifier
TFIDF_OVER_BOW = True			# Whether to use tf-idf or Bow for feature generation


if BUILD_SET: build_set(POSITIVE_URLS, NEGATIVE_URLS, DATASET_PATH)

file = open("..\\links2.txt", "r")
# file = open("..\\data\\model_1\\found_syl.txt"
print("testing")

if SVM_OVER_FOREST:
	if TEST_CLASSIFIER:
		print(svm_classifier.test_model(DATASET_PATH, TFIDF_OVER_BOW))
	model, vectorizer = svm_classifier.train_model(DATASET_PATH, TFIDF_OVER_BOW)
else:
	if TEST_CLASSIFIER:
		print(random_forest.test_model(DATASET_PATH, TFIDF_OVER_BOW))
	model, vectorizer = random_forest.train_model(DATASET_PATH, TFIDF_OVER_BOW)

print("Model Trained")


crawler = Crawler(MAX_LINKS, MAX_PAGES, MAX_RETRIES, model, vectorizer)

count = 0
syllabi = []

if FIRST_RUN:
	df = pd.DataFrame()
else:
	df = pd.read_csv(OUTPUT)


count = 0
for line in file: 	# simple loop over all seed pages, calling the crawler on each
	print(line)
	stripped = line.rstrip('\n')

	if stripped not in df.columns.tolist():
		l = 'http://' + stripped
		found = crawler.crawl_site(l, MAX_SYLLABI, CRAWL_PDFS)  # crawler.crawl_site(l)
		df[stripped] = pd.Series(found + ['']*(MAX_SYLLABI - len(found)))
		if count%3 == 0:
			print("outputting: " )
			df.to_csv(OUTPUT, index=False, quoting=3, escapechar='\\')
			df.to_json(JSON)
		count += 1
