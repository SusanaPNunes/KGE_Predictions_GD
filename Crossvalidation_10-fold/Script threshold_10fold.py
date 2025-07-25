# -*- coding: utf-8 -*-
'''
    File name: Script threshold_10fold.py
    Authors: Susana Nunes, Rita T. Sousa, Catia Pesquita
    Python Version: 3.7
'''
import numpy as np
from sklearn import metrics
from operator import itemgetter


################################################
##        MEASURE FILE MANIPULATION           ##
################################################

# CSV file reading function
def process_measure_file(file_measure_path):
    dataset = open(file_measure_path, 'r')
    data = dataset.readlines()
    csmeasure = []
    labels = []
    labels_list = []
    pairs = []
    cs = []

    for line in data[1:]:
        gene, disease, cosine_measure, label = line.strip(";\n").split(";")
        csmeasure.append(float(cosine_measure))
        labels.append(int(label))
        labels_list.append([(gene, disease), int(label)])
        pairs.append((gene, disease))
        cs.append([(gene, disease), csmeasure])

    dataset.close()
    return labels_list, pairs, labels, csmeasure, cs


################################################
##         TEST AND TRAINING CREATION         ##
################################################

# Creates X train/test and Y train/test:
def create_X_and_Y_lists(file_measure_path, file_indexes_path):
    index_file = open(file_indexes_path, 'r')
    indexes = index_file.readlines()
    labels_list, pairs, labels, csmeasure, cs = process_measure_file(file_measure_path)
    indexesList = []

    for index in indexes:
        ind = index.strip("\n")
        indexesList.append(int(ind))
    final_Xlist = [csmeasure[index] for index in indexesList]
    final_Ylist = [labels[index] for index in indexesList]

    index_file.close()
    return final_Xlist, final_Ylist


################################################
##                PREDICTION                  ##
################################################

def labels_prediction_with_cuttof_baselines(list_SS, cuttof):
    predicted_labels = []
    ssm_values = []
    for SS in list_SS:
        ssm_values.append(SS)
        if SS >= cuttof:
            prediction = 1
        else:
            prediction = 0
        predicted_labels.append(prediction)
    return predicted_labels, ssm_values


def predictions(predicted_labels, list_labels, ssm_values):
    waf_measure = metrics.f1_score(list_labels, predicted_labels, average='weighted')
    Fmeasure_noninteract, Fmeasure_interact = metrics.f1_score(list_labels, predicted_labels, average=None)
    Auc = metrics.roc_auc_score(list_labels, ssm_values, average='weighted')
    Precision = metrics.precision_score(list_labels, predicted_labels)
    Recall = metrics.recall_score(list_labels, predicted_labels)
    Accuracy = metrics.accuracy_score(list_labels, predicted_labels)
    return waf_measure, Fmeasure_noninteract, Fmeasure_interact, Precision, Recall, Accuracy, Auc

def writePredictions(predictions, ytest_or_train, path_output):
    print('WRITING PREDICTIONS!!!!!!!!!!!!!!!!!')
    file_predictions = open(path_output, 'w')
    file_predictions.write('Predicted_output' + '\t' + 'Expected_Output' + '\n')

    for i in range(len(ytest_or_train)):
        file_predictions.write(str(predictions[i]) + '\t' + str(ytest_or_train[i]) + '\n')

    file_predictions.close()


################################################
##         BASELINE PERFORMANCES              ##
################################################

# Function that calls predictions and labels_prediction_with_cuttof_baselines
def performance_baseline(X_train, X_test, y_train, y_test):
    cutoffs = list(np.arange(0, 1, 0.01))
    WAFs_TrainingSet = {}
    for cutoff in cutoffs:
        WAFs_TrainingSet[cutoff] = metrics.f1_score(y_train,
                                                    labels_prediction_with_cuttof_baselines(X_train,
                                                                                            cutoff)[0],
                                                    average='weighted')

    max_cutoff_TrainingSet, max_waf_TrainingSet = max(WAFs_TrainingSet.items(), key=itemgetter(1))

    predicted_labels, predicted_values = labels_prediction_with_cuttof_baselines(X_test, max_cutoff_TrainingSet)

    waf_measure, Fmeasure_noninteract, Fmeasure_interact, \
        Precision, Recall, Accuracy, Auc = predictions(predicted_labels, y_test, predicted_values)
    x = X_train + X_test
    y = y_train + y_test
    writePredictions(x, y,'CS_predictions_prob.txt')

    print('Maximum cutoff value: ' + str(max_cutoff_TrainingSet))
    print('WAF: ' + str(waf_measure))
    print('fmeasure noninteract: ' + str(Fmeasure_noninteract))
    print('fmeasure interact: ' + str(Fmeasure_interact))
    print('Precision: ' + str(Precision))
    print('Recall: ' + str(Recall))
    print('Accuracy: ' + str(Accuracy))
    print('Auc: ' + str(Auc))

    return max_cutoff_TrainingSet, waf_measure, Fmeasure_noninteract, \
        Fmeasure_interact, Precision, Recall, Accuracy, Auc


################################################
##             RUN PERFORMANCES               ##
################################################

# Creation of the partitions and performance files for each measure
for i in range(1, 11):  # Partition
    Xtrain, Ytrain = create_X_and_Y_lists('Data_Cosine_Similarity.csv',
                                          '_10Fold_indexes/10Fold_indexes__crossvalidationTrain_Run_' + str(i) + '.txt')
    Xtest, Ytest = create_X_and_Y_lists('Data_Cosine_Similarity.csv',
                                        '_10Fold_indexes/10Fold_indexes__crossvalidationTest_Run_' + str(i) + '.txt')
    max_c, waf, fmeasure_noninteract, fmeasure_interact, precision, recall, accuracy, auc = performance_baseline(
        Xtrain, Xtest, Ytrain, Ytest)

    file_cuttof = open(
        'Performance_Baseline_Measure_Cosine_Similarity.txt', 'a')

    file_cuttof.write('PARTITION ' + str(i) + '\n')
    file_cuttof.write('Maximum cutoff value: ' + str(max_c) + '\n')
    file_cuttof.write('WAF: ' + str(waf) + '\n')
    file_cuttof.write('fmeasure noninteract: ' + str(fmeasure_noninteract) + '\n')
    file_cuttof.write('fmeasure interact: ' + str(fmeasure_interact) + '\n')
    file_cuttof.write('Precision: ' + str(precision) + '\n')
    file_cuttof.write('Recall: ' + str(recall) + '\n')
    file_cuttof.write('Accuracy: ' + str(accuracy) + '\n')
    file_cuttof.write('Auc: ' + str(auc) + '\n')

    file_cuttof.close()
