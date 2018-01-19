import tidy_data
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import sklearn.metrics as metric

def train_model():
	train = pd.read_csv("..\\urls_and_prep\\data_set.csv", header=0, delimiter=",", quoting=3)
	clean_contents = []

	for i in range(0, train["content"].size):
		clean_contents.append(tidy_data.trim_words(train["content"][i]))

	vectorizer = CountVectorizer(analyzer="word", tokenizer=None, preprocessor=None,
								 stop_words=None, max_features=5000)

	data_features = vectorizer.fit_transform(clean_contents)

	data_features = data_features.toarray()

	forest = RandomForestClassifier(n_estimators=100)
	forest = forest.fit(data_features["content"], data_features["syllabus"])

	return forest


train = pd.read_csv("..\\urls_and_prep\\data_set.csv", header=0, delimiter=",", quoting=3)

print(train.shape)
print(train.columns.values)

clean_contents = []

for i in range(0, train["content"].size):
	clean_contents.append(tidy_data.trim_words(train["content"][i]))

vectorizer = CountVectorizer(analyzer="word", tokenizer=None, preprocessor=None,
							 stop_words=None, max_features=5000)

data_features = vectorizer.fit_transform(clean_contents)

data_features = data_features.toarray()

print(data_features.shape)

c_train, c_test, s_train, s_test = train_test_split(data_features, train["syllabus"],
													test_size=0.2, random_state=0)

print(c_train.shape, s_train.shape)
print(c_test.shape, s_test.shape)

print("Testing:")
print(c_test.shape, s_test.shape)

forest = RandomForestClassifier(n_estimators = 100)
forest = forest.fit(c_train, s_train)

scores = cross_val_score(forest, c_train, s_train, cv=10)
print("scores:")
print(scores)

print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

result = forest.predict(c_test)

print("\nAfter training on training set, test set evaluation: ")
print("accuracy: " + str(metric.accuracy_score(s_test, result)))
print(list(zip(['prec', 'rec', 'fscor', 'supp'], metric.precision_recall_fscore_support(s_test, result))))
print("confusion matrix:\n" + str(metric.confusion_matrix(s_test, result)))

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


