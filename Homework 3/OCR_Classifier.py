# Code (c) Andrew Balaschak, 2023
import os
import numpy as np
import pandas as pd
import random

ROOT_DIR = os.path.dirname(__file__)

'''
You will build a optical character recognition (OCR) classifier: given an image of handwritten character, we need to predict whether the corresponding letter is vowel (a, e, i, o, u) or consonant.
You are provided with a training and testing set.
Data format: Each non-empty line corresponds to one input-output pair.
128 binary values after “im” correspond to the input features (pixel values of a binary image).
The letter immediately afterwards is the corresponding output label.
'''

####################################################################################################
# Preprocessing

# Read training data
traindata_file = open(os.path.join(ROOT_DIR, 'OCR-data', 'ocr_train.txt'), 'r')
traindata = traindata_file.read().splitlines()

# Read testing data
testdata_file = open(os.path.join(ROOT_DIR, 'OCR-data', 'ocr_test.txt'), 'r')
testdata = testdata_file.read().splitlines()

# Convert the training data into a set of features
training_features = []
for line in traindata:
    # If the line is not empty
    if (line.strip()):
        line_split = line.split()
        label = 0 # This label will be changed to 1 if the letter is a vowel, otherwise it stays 0

        # Covert bitmap into feature vector
        features = []
        for char in line_split[1][2:]:
            features.append(int(char))
        
        # Check if the letter is a vowel, if it is then set the label to 1
        if (line_split[2] == 'a' or line_split[2] == 'e' or line_split[2] == 'i' or 
            line_split[2] == 'o' or line_split[2] == 'u'):
            label = 1

        training_features.append([features, label])

# Convert the testing data into a set of features
testing_features = []
for line in testdata:
    # If the line is not empty
    if (line.strip()):
        line_split = line.split()
        label = 0 # This label will be changed to 1 if the letter is a vowel, otherwise it stays 0

        # Covert bitmap into feature vector
        features = []
        for char in line_split[1][2:]:
            features.append(int(char))
        
        # Check if the letter is a vowel, if it is then set the label to 1
        if (line_split[2] == 'a' or line_split[2] == 'e' or line_split[2] == 'i' or 
            line_split[2] == 'o' or line_split[2] == 'u'):
            label = 1

        testing_features.append([features, label])

####################################################################################################
# Model Training & Testing
output = open(os.path.join(ROOT_DIR, 'output.txt'), 'a')
tempstring = ""

weights = [0] * len(training_features[0][0])
averaged_weights = [0] * len(training_features[0][0])
weight_survival_time = np.array([0] * len(training_features[0][0]))
iterations = 20
learning_rate = 1
for i in range(iterations):
    train_mistakes = 0
    test_mistakes = 0
    averaged_train_mistakes = 0
    averaged_test_mistakes = 0
    
    '''
    # This was just for fun, shuffling the data doesn't seem to do much
    random.shuffle(training_features)
    random.shuffle(testing_features)
    '''

    # Train this iteration
    for example in training_features:
        #########################################
        # Make prediction for standard perceptron
        prediction = np.sign(np.sum(np.fromiter(example[0], dtype=int) * weights))
        if (prediction < 0):
            prediction = 0
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
        weight_survival_time = weight_survival_time + 1
        if (averaged_prediction < 0):
            averaged_prediction = 0
        # If weighted prediction is wrong
        if averaged_prediction != example[1]:
            averaged_train_mistakes = averaged_train_mistakes + 1
            
            if(averaged_prediction > example[1]):
                averaged_weights = averaged_weights - np.fromiter(example[0], dtype=int) * learning_rate
                weight_survival_time = weight_survival_time - (weight_survival_time * np.fromiter(example[0], dtype=int))
            else:
                averaged_weights = averaged_weights + np.fromiter(example[0], dtype=int) * learning_rate
                weight_survival_time = weight_survival_time - (weight_survival_time * np.fromiter(example[0], dtype=int))

    # Calculate test accuracy
    for example in testing_features:
        prediction = np.sign(np.sum(np.fromiter(example[0], dtype=int) * weights))
        averaged_prediction = np.sign(np.sum(np.fromiter(example[0], dtype=int) * averaged_weights * weight_survival_time))
        if (prediction < 0):
            prediction = 0
        if (averaged_prediction < 0):
            averaged_prediction = 0
        # If prediction is wrong
        if prediction != example[1]:
            test_mistakes = test_mistakes + 1
        if averaged_prediction != example[1]:
            averaged_test_mistakes = averaged_test_mistakes + 1

    # Accuracy calculations
    training_accuracy = (len(training_features)-train_mistakes)/len(training_features)
    testing_accuracy = (len(testing_features)-test_mistakes)/len(testing_features)
    averaged_training_accuracy = (len(training_features)-averaged_train_mistakes)/len(training_features)
    averaged_testing_accuracy = (len(testing_features)-averaged_test_mistakes)/len(testing_features)

    # File output
    output.write("iteration-{} {}\n".format(i+1, train_mistakes))
    tempstring = tempstring + "iteration-{} training_accuracy {} testing-accuracy {}\n".format(i+1, training_accuracy, testing_accuracy)

    # Console output
    print("Iteration %d:\n\tStandard perceptron training mistakes: %d\n\tStandard perceptron training accuracy: %f\n\tStandard perceptron testing mistakes: %d\n\tStandard perceptron testing accuracy: %f" % (i+1, train_mistakes, training_accuracy, test_mistakes, testing_accuracy))
    print()
    print("\tAveraged perceptron training mistakes: %d\n\tAveraged perceptron training accuracy: %f\n\tAveraged perceptron testing mistakes: %d\n\tAveraged perceptron testing accuracy: %f" % (averaged_train_mistakes, averaged_training_accuracy, averaged_test_mistakes, averaged_testing_accuracy))
    print()

    if(i+1 == iterations):
        tempstring = tempstring + "\ntraining-accuracy- standard-perceptron {} averaged-perceptron {}\n\n".format(training_accuracy, averaged_testing_accuracy)
        tempstring = tempstring + "testing-accuracy- standard-perceptron {} averaged-perceptron {}".format(testing_accuracy, averaged_testing_accuracy)

output.write("\n")
output.write(tempstring)

output.close()