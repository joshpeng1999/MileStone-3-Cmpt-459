import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, classification_report,precision_recall_fscore_support, confusion_matrix
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import make_scorer
import seaborn as sns
import pickle
import matplotlib.pyplot as plt

filename = '../models/rf_classifier.pkl'

def f1Deceased(val, predict):
    ans = precision_recall_fscore_support(val,predict, labels=['deceased'])
    return ans[2]

def recallDeceased(val, predict):
    ans = precision_recall_fscore_support(val,predict, labels=['deceased'])
    return ans[1]

def rf_train(train_attr, train_outcomes, param_grid):

    scoring = {
            'f1_deceased': make_scorer(f1Deceased),
            'recall_deceased': make_scorer(recallDeceased),
            'accuracy': make_scorer(accuracy_score),
            'recall': make_scorer(recall_score, average = 'micro')}


    clf = RandomForestClassifier(random_state=42)

    random_search = RandomizedSearchCV(clf, param_grid, n_iter=15,
                                        scoring=scoring, refit='accuracy', verbose=10, cv=5,
                                        n_jobs=-1, random_state=42)
    print("\n--------------CHECKING MODEL STATS--------------\n")
    # Randomized search
    random_search.fit(train_attr, train_outcomes)
    all_results = random_search.cv_results_
    results_df = []
    for i in range(0,len(all_results['params'])):
        combination = all_results['params'][i]
        f1_deceased = all_results['mean_test_f1_deceased'][i]
        recall_deceased = all_results['mean_test_recall_deceased'][i]
        overall_accuracy = all_results['mean_test_accuracy'][i]
        overall_recall = all_results['mean_test_recall'][i]
        results_df.append([combination, f1_deceased, recall_deceased, overall_accuracy, overall_recall])

    results_df = pd.DataFrame(results_df, columns=['combination', 'f1_deceased', 'recall_deceased', 'overall_accuracy', 'overal_recall'])
    print("Best parameters:", random_search.best_params_)
    print("Best score:", random_search.best_score_)
    results_df.to_csv("randomsearch_results.csv")
    pickle.dump(random_search, open(filename, 'wb'))


def overfit_rf_train(train_attr, train_outcomes, estimators):
    clf = RandomForestClassifier(n_estimators=estimators)
    # Train model and write to file
    clf.fit(train_attr, train_outcomes)
    return clf

def overfit_eval(data,outcomes, clf):
    predictions = clf.predict(data)
    value = accuracy_score(outcomes, predictions)
    return value

def rf_eval(data, outcomes, name):
    clf_load = pickle.load(open(filename, 'rb'))
    predictions = clf_load.predict(data)
    value = accuracy_score(outcomes, predictions)
    print("Accuracy Score: ", end=" ")
    print(value)


    # Confusion Matrix
    # Modified from https://medium.com/analytics-vidhya/evaluating-a-random-forest-model-9d165595ad56
    matrix = confusion_matrix(outcomes, predictions)
    matrix = matrix.astype('float') / matrix.sum(axis=1)[:, np.newaxis]

    plt.figure(figsize=(16,7))
    sns.set(font_scale=1.4)
    sns.heatmap(matrix, annot=True, annot_kws={'size':10},
                cmap=plt.cm.Blues, linewidths=0.2)

    class_names = np.unique(outcomes)
    tick_marks = np.arange(len(class_names))
    tick_marks2 = tick_marks + 0.5
    plt.xticks(tick_marks, class_names, rotation=25)
    plt.yticks(tick_marks2, class_names, rotation=0)
    plt.xlabel('Predicted label')
    plt.ylabel('True label')
    plt.title('Confusion Matrix for Random Forest Model')
    if(name):
        plt.title('Confusion Matrix for Random Forest Model - Train Data')
        plt.savefig("../plots/confusion_matrix_train_rf.png", bbox_inches = "tight")
    else:
        plt.title('Confusion Matrix for Random Forest Model - Validation Data')
        plt.savefig("../plots/confusion_matrix_val_rf.png", bbox_inches = "tight")
    #

    # F1-scores
    print(classification_report(outcomes, predictions))



