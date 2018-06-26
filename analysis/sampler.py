import pandas as pd
import numpy as np
import json
import re

regex = re.compile(
	r'^(?:http|ftp)s?://'  # http:// or https://
	r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
	r'localhost|'  # localhost...
	r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
	r'(?::\d+)?'  # optional port
	r'(?:/?|[/?]\S+)$', re.IGNORECASE)

MODEL_3 = "..//data//model_3//found_json_model3.json"				#628
MODEL_4 = "..//data//model_4_pdfs//found_json_model4.json"			#3117
MODEL_5 = "..//data//model_5_mixed//found_json_model5.json"			#5449
MODEL_6 = "..//data//model_6_improved_basic//found_json_model6.json"#7962
MODEL_7 = "..//data//model_7_svm_mixed//found_json_model7.json" 	#2774 results
MODEL_8 = "..//data//model_8_svm_basic//found_json_model8.json"		#3140
MODEL_9 = "..//data//model_9_svm_improved_basic//found_json_model9.json"#5434
MODEL_10= "..//data//model_10_svm_basic_tfidf//found_json_model10.json"
MODEL_11= "..//data//model_11_svm_html_larger_tfidf//found_json_model11.json"
MODEL_12= "..//data//model_12_RF_html_larger_tfidf//found_json_model12.json"#1584
MODEL_13= "..//data//model_13_RF_basic_tfidf//found_json_model13.json" #660
grab_model="..//data//Grabbing_all_urls//found_urls.json"


with open(grab_model) as f:
	data = json.load(f)


RF = pd.DataFrame(data)


all_results = []
for uni in RF.columns.tolist():
	for syl in RF[uni]:
		if regex.search(str(syl)):
			all_results.append(syl)

print(len(all_results))

sample = np.random.choice(all_results, size=150, replace=False)
print(sample)

text_file = open("url_grab_sample", "w")

for l in sample:
	try:
		text_file.write(str(l) + '\n')
	except:
		print(l)

text_file.close()