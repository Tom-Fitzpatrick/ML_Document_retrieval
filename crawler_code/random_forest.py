import pandas as pd
import numpy as np
import math
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import cross_val_score
import sklearn.metrics as metric
from sklearn import preprocessing

DATA_SET_PATH = "..\\data\\model_1\\data_set(1).csv"

# trains a model on the dataset specified, using the feature generation method specified.
# returns a model capable of making predictions and a vectorizer for representation of documents for classification
def train_model(data_set_path, tfidf):
	train = pd.read_csv(data_set_path, header=0, delimiter=",", quoting=3)

	if tfidf:
		vectorizer = TfidfVectorizer(analyzer="word", tokenizer=None, preprocessor=None,
									 stop_words=None, max_features=5000)
	else:
		vectorizer = CountVectorizer(analyzer="word", tokenizer=None, preprocessor=None,
								 stop_words=None, max_features=5000)

	data_features = vectorizer.fit_transform(train["content"].values.astype('U'))

	data_features = data_features.toarray()

	print("forest trained with " + str(len(data_features)) + " samples and " + str(len(train["syllabus"])) + " tags.")

	forest = RandomForestClassifier(n_estimators=100)
	forest = forest.fit(data_features, train["syllabus"])


	return forest, vectorizer

# performs testing on the training set using the classifier, outputs results to a stats.txt file
def test_model(data_set_path, tfidf):
	output = ""

	train = pd.read_csv(data_set_path, header=0, delimiter=",", quoting=3)

	if tfidf:
		vectorizer = TfidfVectorizer(analyzer="word", tokenizer=None, preprocessor=None,
									 stop_words=None, max_features=5000)
	else:
		vectorizer = CountVectorizer(analyzer="word", tokenizer=None, preprocessor=None,
								 stop_words=None, max_features=5000)

	data_features = vectorizer.fit_transform(train["content"].values.astype('U'))
	print(data_features)
	data_features = data_features.toarray()

	c_train, c_test, s_train, s_test = train_test_split(data_features, train["syllabus"],
														test_size=0.2, random_state=0)


	forest = RandomForestClassifier(n_estimators=400)

	ensemble_score = cross_val_score(forest, c_train, s_train, cv=5, scoring='accuracy')

	print("Accuracy: %0.2f (+/- %0.2f) [%s]" % (ensemble_score.mean(), ensemble_score.std(), 'ensemble'))
	output += ("Accuracy: %0.2f (+/- %0.2f) [%s]" % (ensemble_score.mean(), ensemble_score.std(), 'ensemble'))

	output += "\nTesting:"
	output += "\nAfter training on training set, test set evaluation: "
	forest = forest.fit(c_train, s_train)
	result = forest.predict(c_test)
	output += "accuracy: " + str(metric.accuracy_score(s_test, result))  + "\n"
	output += str(list(zip(['prec', 'rec', 'fscor', 'supp'], metric.precision_recall_fscore_support(s_test, result))))
	output += "confusion matrix:\n" + str(metric.confusion_matrix(s_test, result))

	forest = RandomForestClassifier(n_estimators=400)
	lb = preprocessing.LabelBinarizer()
	labels = np.array([number[0] for number in lb.fit_transform(train["syllabus"])])

	ensemble_full_set_prec = cross_val_score(forest, data_features, labels, cv=5, scoring="precision")
	ensemble_full_set_rec = cross_val_score(forest, data_features, labels, cv=5, scoring="recall")

	output += "\n\nCross_validation avg precision: " + str(
		ensemble_full_set_prec.mean()) + "(+/- " + str(ensemble_full_set_prec.std()) + ")"
	output += "\n\nCross_validation avg recall: " + str(
		ensemble_full_set_rec.mean()) + "(+/- " + str(ensemble_full_set_rec.std()) + ")"

	file = open('stats.txt', 'w')
	file.write(output)
	file.close()

