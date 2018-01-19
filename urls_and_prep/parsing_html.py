import urllib.request
from bs4 import BeautifulSoup
import ssl


def make_text_files(file, out_folder):
    context = ssl._create_unverified_context()
    i = 0
    for line in file:
        i += 1
        try:
            # req = urllib.request.Request(line, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(line, context=context)
            html = response.read()
            print(str(i) + ". " + line)

        except OSError:
            print("***** " + str(line) + " ************************")
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

        f = open(out_folder + str(i) + ".txt", "wb")
        t = text.encode('utf-8')
        f.write(t)
        f.close()

make_text_files(open("positive_urls.txt", "r"), "syllabi_text_files/")
make_text_files(open("false_crawled_b10_d50.txt", "r"), "false_text_files/")