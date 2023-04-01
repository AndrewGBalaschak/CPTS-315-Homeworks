# Code (c) Andrew Balaschak, 2023
import os
import numpy as np
import pandas as pd
import random

ROOT_DIR = os.path.dirname(__file__)

'''
You will build a binary fortune cookie classifier.
This classifier will be used to classify fortune cookie messages into two classes: messages that predict what will happen in the future (class 1) and messages that just contain a wise saying (class 0).
For example, “Never go in against a Sicilian when death is on the line” would be a message in class 0.
“You will get an A in Machine learning class” would be a message in class 1.

Files Provided There are three sets of files. All words in these files are lower case and punctuation has been removed.
1)	The training data: traindata.txt: This is the training data consisting of fortune cookie messages. trainlabels.txt: This file contains the class labels for the training data.
2)	The testing data: testdata.txt: This is the testing data consisting of fortune cookie messages. testlabels.txt: This file contains the class labels for the testing data.
3)	A list of stopwords: stoplist.txt

There are two steps: the pre-processing step and the classification step.
In the preprocessing step, you will convert fortune cookie messages into features to be used by your classifier. You will be using a bag of words representation.

The following steps outline the process involved:
Form the vocabulary. The vocabulary consists of the set of all the words that are in the training data with stop words removed (stop words are common, uninformative words such as “a” and “the” that are listed in the file stoplist.txt).
The vocabulary will now be the features of your training data. Keep the vocabulary in alphabetical order to help you with debugging.

Now, convert the training data into a set of features. Let M be the size of your vocabulary. For each fortune cookie message, you will convert it into a feature vector of size M.
Each slot in that feature vector takes the value of 0 or 1. For these M slots, if the ith slot is 1, it means that the ith word in the vocabulary is present in the fortune cookie message; otherwise, if it is 0, then the ith word is not present in the message.
Most of these feature vector slots will be 0. Since you are keeping the vocabulary in alphabetical order, the first feature will be the first word alphabetically in the vocabulary.

Implement a binary classifier with perceptron weight update as shown below. Use learning rate η=1.

'''


####################################################################################################
# Preprocessing

# Read training data
traindata_file = open(os.path.join(ROOT_DIR, 'fortune-cookie-data', 'traindata.txt'), 'r')
traindata = traindata_file.read().splitlines()

trainlabels_file = open(os.path.join(ROOT_DIR, 'fortune-cookie-data', 'trainlabels.txt'), 'r')
trainlabels = trainlabels_file.read().splitlines()
trainlabels = [int(num) for num in trainlabels]

# Read testing data
testdata_file = open(os.path.join(ROOT_DIR, 'fortune-cookie-data', 'testdata.txt'), 'r')
testdata = testdata_file.read().splitlines()

testlabels_file = open(os.path.join(ROOT_DIR, 'fortune-cookie-data', 'testlabels.txt'), 'r')
testlabels = testlabels_file.read().splitlines()
testlabels = [int(num) for num in testlabels]

# Read stop list
stoplist_file = open(os.path.join(ROOT_DIR, 'fortune-cookie-data', 'stoplist.txt'), 'r')
stoplist = stoplist_file.read().splitlines()

# Form the vocabulary, alphabetical list of all words that appear that are not stop words
vocabulary = set()
for line in traindata:
    line_split = line.split()
    for word in line_split:
        if word not in stoplist:
            vocabulary.add(word)
vocabulary = sorted(vocabulary)

# Convert the training data into a set of features
feature_set = []
for message in traindata:
    message_split = message.split()
    features = dict.fromkeys(vocabulary, 0)

    for word in message_split:
        if word in features:
            features[word] = 1
    feature_set.append(features.values())

merged_training_data_labels = np.array(list(zip(feature_set, trainlabels)))

# Convert the testing data into a set of features
feature_set = []
for message in testdata:
    message_split = message.split()
    features = dict.fromkeys(vocabulary, 0)

    for word in message_split:
        if word in features:
            features[word] = 1
    feature_set.append(features.values())

merged_testing_data_labels = np.array(list(zip(feature_set, testlabels)))

####################################################################################################
# Model Training & Testing

'''
# This was just for fun, shuffling the data produces much better results for both classifiers
random.shuffle(merged_training_data_labels)
random.shuffle(merged_testing_data_labels)
'''

weights = [0] * len(vocabulary)
averaged_weights = [0] * len(vocabulary)
weight_survival_time = np.array([0] * len(vocabulary))
iterations = 20
learning_rate = 1
for i in range(iterations):
    train_mistakes = 0
    test_mistakes = 0
    averaged_test_mistakes = 0
    averaged_train_mistakes = 0

    # Train this iteration
    for example in merged_training_data_labels:
        #########################################
        # Make prediction for standard perceptron
        prediction = np.sign(np.sum(np.fromiter(example[0], dtype=int) * weights))
        # If prediction is wrong
        if prediction != example[1]:
            train_mistakes = train_mistakes + 1
            if(prediction > example[1]):
                weights = weights - np.fromiter(example[0], dtype=int) * learning_rate
            else:
                weights = weights + np.fromiter(example[0], dtype=int) * learning_rate

        #########################################
        # Make prediction for averaged perceptron
        averaged_prediction = np.sign(np.sum(np.fromiter(example[0], dtype=int) * averaged_weights * weight_survival_time))
        # If weighted prediction is wrong
        if averaged_prediction != example[1]:
            averaged_train_mistakes = averaged_train_mistakes + 1
            weight_survival_time = weight_survival_time + 1
            if(averaged_prediction > example[1]):
                averaged_weights = averaged_weights - np.fromiter(example[0], dtype=int) * learning_rate
                weight_survival_time = weight_survival_time - (weight_survival_time * np.fromiter(example[0], dtype=int))
            else:
                averaged_weights = averaged_weights + np.fromiter(example[0], dtype=int) * learning_rate
                weight_survival_time = weight_survival_time - (weight_survival_time * np.fromiter(example[0], dtype=int))

    # Calculate test accuracy
    for example in merged_testing_data_labels:
        prediction = np.sign(np.sum(np.fromiter(example[0], dtype=int) * weights))
        averaged_prediction = np.sign(np.sum(np.fromiter(example[0], dtype=int) * averaged_weights * weight_survival_time))
        # If prediction is wrong
        if prediction != example[1]:
            test_mistakes = test_mistakes + 1
        if averaged_prediction != example[1]:
            averaged_test_mistakes = averaged_test_mistakes + 1

    # Console output
    training_accuracy = (len(merged_training_data_labels)-train_mistakes)/len(merged_training_data_labels)
    testing_accuracy = (len(merged_testing_data_labels)-test_mistakes)/len(merged_testing_data_labels)
    averaged_training_accuracy = (len(merged_training_data_labels)-averaged_train_mistakes)/len(merged_training_data_labels)
    averaged_testing_accuracy = (len(merged_testing_data_labels)-averaged_test_mistakes)/len(merged_testing_data_labels)
    print("Iteration %d:\n\tStandard training mistakes: %d\n\tStandard training accuracy: %f\n\tStandard testing mistakes: %d\n\tStandard testing accuracy: %f" % (i+1, train_mistakes, training_accuracy, test_mistakes, testing_accuracy))
    print()
    print("\tAveraged training mistakes: %d\n\tAveraged training accuracy: %f\n\tAveraged testing mistakes: %d\n\tAveraged testing accuracy: %f" % (averaged_train_mistakes, averaged_training_accuracy, averaged_test_mistakes, averaged_testing_accuracy))
    print()