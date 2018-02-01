from Crawler import Crawler
from build_data_set import build_set
import random_forest
import requests
import pandas as pd
import numpy as np

PATH = "..\\data\\"
POSITIVE_URLS = PATH + "positive_urls.txt"
NEGATIVE_URLS_1 = PATH + "model_1\\false_crawled_b10_d502.txt"
NEGATIVE_URLS_2 = PATH + "model_2\\negative_eg_from_crawl.txt"

MAX_RETRIES = 20
MAX_LINKS = 15
MAX_PAGES = 100
DATA_SET_PATH_1 = PATH + "model_1\\data_set(1).csv"
DATA_SET_PATH_2 = PATH + "model_2\\data_set_2.csv"

# build_data_set_from_links.build_set(POSITIVE_URLS, NEGATIVE_URLS_1, DATA_SET_PATH_1)
# build_set(POSITIVE_URLS, NEGATIVE_URLS_2, DATA_SET_PATH_2)

file = open("..\\data\\links.txt", "r")
# file = open("..\\data\\model_1\\found_syl.txt")


# random_forest.test_model(DATA_SET_PATH_2)
model, vectorizer = random_forest.train_model(DATA_SET_PATH_1)
random_forest.test_model(DATA_SET_PATH_1)
# model_2, vectorizer_2 = random_forest.train_model(DATA_SET_PATH_2)
print("Model Trained")
crawler = Crawler(MAX_LINKS, MAX_PAGES, MAX_RETRIES, model, vectorizer)
# crawler_2 = Crawler(0, 1, MAX_RETRIES, model_2, vectorizer_2)

count = 0
syllabi = []
for line in file:
	print(line)
	l = line.rstrip('\n')
	l = 'http://' + l
	# layer_1
	syllabi = syllabi + crawler.crawl_site(l)  # crawler.crawl_site(l)
	print("layer_1 done: " + str(syllabi))


	# for syl in layer_1:
	# 	print("layer 2")
	# 	layer_2 = crawler_2.crawl_site(syl)
	# 	syllabi = syllabi + layer_2
	# 	print("found syllabi:")
	# 	print(syllabi)

	output = pd.DataFrame(data={"address": syllabi})
	output.to_csv("..\\data\\model_2\\found_syllabi.csv", index=False, quoting=3)
