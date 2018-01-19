from nltk.corpus import stopwords  # Import the stop word list
import re


def trim_words(content):
	lower_case = content.lower()  # Convert to lower case
	letters_only = re.sub("[^a-zA-Z]", " ", lower_case)
	words = letters_only.split()  # Split into words

	# Remove stop words from "words"
	stops = set(stopwords.words("english"))
	words = [w for w in words if not w in stops]
	return (" ".join(words))