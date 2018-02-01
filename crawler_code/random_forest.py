import pandas as pd
import numpy as np
import math
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import cross_val_score
import sklearn.metrics as metric

DATA_SET_PATH = "..\\data\\model_1\\data_set(1).csv"

def train_model(data_set_path):
	train = pd.read_csv(data_set_path, header=0, delimiter=",", quoting=3)

	vectorizer = CountVectorizer(analyzer="word", tokenizer=None, preprocessor=None,
								 stop_words=None, max_features=5000)

	data_features = vectorizer.fit_transform(train["content"])

	data_features = data_features.toarray()

	c_train, c_test, s_train, s_test = train_test_split(data_features, train["syllabus"],
														test_size=0.2, random_state=0)
	# models = []
	# scores = []
	# k = 5
	# l = len(s_train)
	# for i in range(0, k):
	# 	first = math.ceil((i / k) * l)
	# 	second = math.ceil(((i + 1) / k) * l)
	# 	model = RandomForestClassifier(n_estimators=100)
	# 	examples = np.concatenate((c_train[:first], c_train[second:]), axis=0)
	# 	targets = np.concatenate((s_train[:first], s_train[second:]), axis=0)
	# 	model = model.fit(examples, targets)
	# 	models.append(model)
	#
	# 	result = model.predict(c_train[first:second])
	# 	acc = metric.accuracy_score(s_train[first:second], result)
	# 	scores.append(acc)

	# forest = VotingClassifier(estimators=[('one', models[0]), ('two', models[1]), ('three', models[2]),
	# 									('four', models[3]), ('five', models[4])])
	forest = RandomForestClassifier(n_estimators=100)
	forest = forest.fit(c_train, s_train)
	# forest = RandomForestClassifier(n_estimators=400)
	# forest = forest.fit(data_features, train["syllabus"])

	return forest, vectorizer

def test_model(data_set_path):
	train = pd.read_csv(data_set_path, header=0, delimiter=",", quoting=3)

	vectorizer = CountVectorizer(analyzer="word", tokenizer=None, preprocessor=None,
								 stop_words=None, max_features=5000)

	data_features = vectorizer.fit_transform(train["content"])
	# print(data_features)
	data_features = data_features.toarray()


	c_train, c_test, s_train, s_test = train_test_split(data_features, train["syllabus"],
														test_size=0.2, random_state=0)


	# models = []
	# scores = []
	# k = 5
	# l = len(s_train)
	# for i in range(0, k):
	# 	first = math.ceil((i/k)*l)
	# 	second = math.ceil(((i + 1)/k)*l)
	# 	model = RandomForestClassifier(n_estimators=100)
	# 	examples = np.concatenate((c_train[:first], c_train[second:]), axis=0)
	# 	targets = np.concatenate((s_train[:first], s_train[second:]), axis=0)
	# 	model = model.fit(examples, targets)
	# 	models.append(model)
	#
	# 	result = model.predict(c_train[first:second])
	# 	acc = metric.accuracy_score(s_train[first:second], result)
	# 	scores.append(acc)

	# eclf = VotingClassifier(estimators=[('one', models[0]), ('two', models[1]), ('three', models[2]),
	# 									('four', models[3]), ('five', models[4])])

	eclf = RandomForestClassifier(n_estimators=400)

	ensemble_score = cross_val_score(eclf, c_train, s_train, cv=5, scoring='accuracy') # waah change to train? getting confused with sets

	print("Accuracy: %0.2f (+/- %0.2f) [%s]" % (ensemble_score.mean(), ensemble_score.std(), 'ensemble'))


	# clf1 = RandomForestClassifier(random_state=1)
	# clf2 = RandomForestClassifier(random_state=2)
	# clf3 = RandomForestClassifier(random_state=3)
	#
	# eclf = VotingClassifier(estimators=[('lr', clf1), ('rf', clf2), ('gnb', clf3)], voting='hard')
	#
	# for clf, label in zip([clf1, clf2, clf3, eclf], ['1', '2', '3', 'Ensemble']):
	# 	scores = cross_val_score(clf, c_train, s_train, cv=5, scoring='accuracy')
	# 	print("Accuracy: %0.2f (+/- %0.2f) [%s]" % (scores.mean(), scores.std(), label))

	# print("scores: " + str(scores))

	print("\nTesting:")
	eclf = eclf.fit(c_train, s_train)
	result = eclf.predict(c_test)
	print("\nAfter training on training set, test set evaluation: ")
	print("accuracy: " + str(metric.accuracy_score(s_test, result)))
	print(list(zip(['prec', 'rec', 'fscor', 'supp'], metric.precision_recall_fscore_support(s_test, result))))
	print("confusion matrix:\n" + str(metric.confusion_matrix(s_test, result)))



###################################################################################

# output = pd.DataFrame(data={"syllabus":result, "actual": s_test})
#
# output.to_csv("random_forest_output_1.csv", index=False, quoting=3)

# vocab = vectorizer.get_feature_names()
# print("\nVocab: ")
# print(vocab)
# dist = np.sum(train_data_features, axis=0)
# For each, print the vocabulary word and the number of times it
# appears in the training set
# print("\nCount")
# for tag, count in zip(vocab, dist):
# 	print(count, tag)

# forest = RandomForestClassifier(n_estimators = 100)
# forest = forest.fit(train_data_features, train["syllabus"])
