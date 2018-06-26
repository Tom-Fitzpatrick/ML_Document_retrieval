from Crawler import Crawler
from build_data_set import build_set
import random_forest
import svm_classifier
import requests
import pandas as pd
import numpy as np
import json

MAX_RETRIES = 10
MAX_LINKS = 10
MAX_PAGES = 100
MAX_SYLLABI = 30

POSITIVE_URLS = "positive_urls.txt"
NEGATIVE_URLS = "false_crawled_b10_d50.txt"
DATASET_PATH = "dataset3.csv"
OUTPUT = "found_syllabi_model3.csv"
JSON = "found_json_model3.json"
CRAWL_PDFS = False
BUILD_SET = False
FIRST_RUN = False
TEST_CLASSIFIER = True
SVM_OVER_FOREST = False

if BUILD_SET: build_set(POSITIVE_URLS, NEGATIVE_URLS, DATASET_PATH)

file = open("..\\links2.txt", "r")
# file = open("..\\data\\model_1\\found_syl.txt")
print("testing")

if SVM_OVER_FOREST:
	if TEST_CLASSIFIER:
		print(svm_classifier.test_model(DATASET_PATH))
	model, vectorizer = svm_classifier.train_model(DATASET_PATH)
else:
	if TEST_CLASSIFIER:
		print(random_forest.test_model(DATASET_PATH, False))
	model, vectorizer = random_forest.train_model(DATASET_PATH, False)

print("Model Trained")


crawler = Crawler(MAX_LINKS, MAX_PAGES, MAX_RETRIES, model, vectorizer)


count = 0
syllabi = []

if FIRST_RUN:
	df = pd.DataFrame()
else:
	df = pd.read_csv(OUTPUT)


count = 0
for line in file:
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
