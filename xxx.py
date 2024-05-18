import tqdm as tqdm
from matplotlib.lines import Line2D
from nltk import FreqDist
from sklearn.metrics import accuracy_score, silhouette_score, \
    davies_bouldin_score, pairwise_distances  ## for evaluation of the model using accuracy metric
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, RandomizedSearchCV, GridSearchCV, KFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import roc_auc_score, confusion_matrix
from sklearn.decomposition import PCA
from tqdm import tqdm
import matplotlib.pyplot as plt
from pyclustering.cluster.kmedoids import kmedoids
from sklearn.svm import SVC
import openpyxl

#upload worksheet!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Load the workbook

df = pd.read_excel('C:/Users/yaels/Downloads/השתתפות במחקר בנושא עיבוד תמונה לבחינת הרווחה הנפשית (תגובות).xlsx')
column_names = ['תעודת זהות', 'images']

selected_columns = df[column_names]

selected_columns['images'] = selected_columns['images'].str.replace(' ', '')

result_dict = {}

for index, row in selected_columns.iterrows():
    # Get the ID and the string from the current row
    id_value = row['תעודת זהות']
    string_value = row['images']

    # Split the string by comma and create a list
    split_strings = string_value.split(',')

    # Update the dictionary with ID as key and list of split strings as value
    result_dict[id_value] = split_strings

print()





