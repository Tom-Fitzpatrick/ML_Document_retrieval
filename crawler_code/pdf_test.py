import PyPDF2
import ssl
import requests
import urllib.request
import os

context = ssl._create_unverified_context()

session = requests.Session()
crawlAdapter = requests.adapters.HTTPAdapter(max_retries=30)
session.mount('https://', crawlAdapter)
session.mount('http://', crawlAdapter)

errors = []
file = open("..\\data\\pdf_pos_urls.txt", "r")
count = 0
for line in file:
	count += 1
	print(line)
	try:
		response = urllib.request.urlopen(line)
	except Exception as e:  # requests.exceptions.ConnectionError:
		# logging.error(traceback.format_exc())
		errors.append(line)
		print("erronous pages: " + str(len(errors)))
		print(errors)
		continue

	with open('..\\data\\model_2\\pdf_' + str(count) + '.pdf', 'wb') as out_file:
		print("hereer")
		out_file.write(response.read())

	with open("..\\data\\model_2\\pdf_" + str(count) + '.pdf', 'rb') as pdf_obj:
		try:
			read_pdf = PyPDF2.PdfFileReader(pdf_obj)
		except:
			print("failed to read: " + line)
			continue
		if read_pdf.numPages < 6:
			if read_pdf.isEncrypted:
				read_pdf.decrypt("")
				print(read_pdf.getPage(0).extractText())
			else:
				print(read_pdf.getPage(0).extractText())
		else:
			print("too long: " + line)

	os.remove("..\\data\\model_2\\pdf_" + str(count) + '.pdf')