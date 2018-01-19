import csv
import string
import pandas as pd

def to_csv():
	with open('data_set.csv', 'w', newline='', encoding='utf-8') as csvfile:
		# translator = str.maketrans('', '', string.punctuation)
		translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
		writer = csv.writer(csvfile, delimiter=',')
		rows = []
		writer.writerow(['syllabus', 'content'])

		for i in range(1, 190):
			try:
				file = open("false_text_files/" + str(i) + ".txt", "rb")
				text = file.read().decode('utf-8').translate(translator)	#need to make it replace punc with spaces
			except:
				continue
			row = ['no', text]
			rows.append(row)
		for u in rows:
			print(u[1])
			writer.writerow(u)

		rows = []
		for i in range(1, 190):
			try:
				file = open("syllabi_text_files/" + str(i) + ".txt", "rb")
				text = file.read().decode('utf-8').translate(translator)
			except:
				continue
			row = ['yes', text]
			rows.append(row)
		for u in rows:
			print(u[1])
			writer.writerow(u)

to_csv()
