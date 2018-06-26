from Crawler import Crawler
from build_data_set import build_set
import random_forest
import requests
import pandas as pd
import numpy as np
import json

MAX_RETRIES = 10
MAX_LINKS = 10
MAX_PAGES = 100
MAX_SYLLABI = 30

POSITIVE_URLS = "positive_urls.txt";
NEGATIVE_URLS = "false_crawled_b10_d50.txt"
DATASET_PATH = "dataset3.csv"
OUTPUT = "found_syllabi_model3.csv"
JSON = "found_json_model3.json"

# build_set(POSITIVE_URLS, NEGATIVE_URLS, DATASET_PATH)

file = open("..\\links.txt", "r")
# file = open("..\\data\\model_1\\found_syl.txt")
print("testing")

random_forest.test_model(DATASET_PATH)
model, vectorizer = random_forest.train_model(DATASET_PATH)
# model_2, vectorizer_2 = random_forest.train_model(DATA_SET_PATH_2)
print("Model Trained")
crawler = Crawler(MAX_LINKS, MAX_PAGES, MAX_RETRIES, model, vectorizer)
# crawler_2 = Crawler(0, 1, MAX_RETRIES, model_2, vectorizer_2)

count = 0
syllabi = []

# Need to decide whether I get 50 links from a crawl and take a random sample or take
# 10 links and add them all. also I can't just search till I get 50 links as it may never happen

df = pd.read_csv(OUTPUT)
count = 0
for line in file:
	print(line)
	stripped = line.rstrip('\n')

	if stripped not in df.columns.tolist():
		l = 'http://' + stripped
		found = crawler.crawl_site(l, MAX_SYLLABI, False)  # crawler.crawl_site(l)
		df = df.assign(stripped=pd.Series(found + ['']*(MAX_SYLLABI - len(found))).values)
		if count%3 == 0:
			df.to_csv(OUTPUT, index=False, quoting=3, escapechar='\\')
			df.to_json(JSON)
		count += 1
