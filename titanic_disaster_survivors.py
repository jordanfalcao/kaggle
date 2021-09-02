# -*- coding: utf-8 -*-
"""titanic-disaster-survivors.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Jd_Tg4dZcsn8RM-nzu-IDU5deqC9UArL
"""

# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session

"""- Survived: 0 = no, 1 = yes
- Pclass (Class):1 = 1º, 2 = 2º, 3 = 3º
- Sex: passenger sex
- Age: age in years
- Sibsp: Siblings / Spouses on board
- Parch: Quantidade de pais / crianças a bordo do Titanic
- Ticket: ticket number
- Fare: Fare paid by the passenger
- Cabin: cabin number
- Embarked: departure port (C = Cherbourg, Q = Queenstown, S = Southampton)
"""

import numpy as np 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# %matplotlib inline

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier

import tensorflow as tf

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout

from sklearn.metrics import confusion_matrix

"""# Data"""

train_df = pd.read_csv('train.csv')
test_df = pd.read_csv('test.csv')
combine = [train_df, test_df]

# train_df = pd.read_csv('../input/titanic/train.csv')

# test_df = pd.read_csv('../input/titanic/test.csv')

train_df.head()

test_df.head()

train_df.shape

"""## Features"""

train_df.columns.values

train_df.info()

test_df.info()

train_df['Survived'].value_counts()

train_df['Survived'].value_counts().plot.pie(colors=('tab:red', 'tab:blue'), shadow=True,
                                             labels=('Not survived','Survived'),
                                            figsize=(8,5), startangle=90, autopct='%1.1f%%',
                                            title='Porcentage of survivors', fontsize=18).set_ylabel=('')
plt.show()

"""### Correlations:"""

plt.figure(figsize=(7,7))
sns.heatmap(train_df.corr(), cmap='coolwarm')
plt.show()

"""### 'Pclass': Percentage of survivors in each class:"""

train_df[['Pclass', 'Survived']].groupby(['Pclass'], as_index=False).mean().sort_values(by='Survived', ascending=False)

ax = train_df.pivot_table(index='Pclass',values='Name',aggfunc='count').plot(kind='bar', rot=0, legend=None,
                                                                        label='index', figsize=(8,5))

ax.set_xlabel('Class', fontsize = 14)
ax.set_title('People per class', fontsize = 20, pad=10)
plt.show()

ax = train_df[train_df['Survived'] == 1].groupby('Pclass').sum()['Survived'].plot(kind='bar', rot=0, legend=None,
                                                                        label='index',figsize=(8,5))
ax.set_xlabel('Class', fontsize = 14)
ax.set_title('Survivors per class', fontsize = 20, pad=10)
plt.show()

"""- Despite having more people in class-3, class-1 had more survivors."""

ax = train_df[['Pclass', 'Survived']].groupby(['Pclass'], as_index=False).mean().set_index('Pclass').plot(kind='bar',
                                                                                                    rot=0,
                                                                                                    legend=None,
                                                                                                    figsize=(8,5))
ax.set_title('Survivors Percentage in each class', fontsize=20)
ax.set_xlabel('Class', fontsize=14)
ax.annotate('62.9%', xy = (-0.15, 0.16), fontsize = 16)
ax.annotate('47.3%', xy = (0.82, 0.16), fontsize = 16)
ax.annotate('24.2%', xy = (1.83, 0.16), fontsize = 16)
plt.show()

"""### 'Sex': Percentage of survived women and men:"""

# male and female percentage
train_df['Sex'].value_counts(normalize=True) * 100

train_df[["Sex", "Survived"]].groupby(['Sex'], as_index=False).mean().set_index('Sex') * 100

train_df.pivot_table('PassengerId', ['Sex'], 'Pclass', aggfunc='count')

"""- We note there is a huge difference between male and female percentage survivors.

### Converting 'Sex' to categorical feature:
"""

for dataset in combine:
    dataset['Sex'] = dataset['Sex'].map( {'female': 0, 'male': 1} ).astype(int)

"""### 'SibSp': Survivors according the amount of siblings/spouses on board:"""

train_df[["SibSp", "Survived"]].groupby(['SibSp'], as_index=False).mean().sort_values(by='Survived', ascending=False)

"""### 'Parch': Survivors according the amount of parents/children on board:"""

train_df[["Parch", "Survived"]].groupby(['Parch'], as_index=False).mean().sort_values(by='Survived', ascending=False)

"""## 'IsAlone': Lets create a new feature if a person is alone or not:

### First we combine 'Parch' and 'SibSp':
"""

for dataset in combine:
    dataset['FamilySize'] = dataset['SibSp'] + dataset['Parch'] + 1 # plus 1

train_df[['FamilySize', 'Survived']].groupby(['FamilySize'], as_index=False).mean().sort_values(by='Survived', ascending=False)

"""### Now we create the new feature and drop the useless:"""

for dataset in combine:
    dataset['IsAlone'] = 0
    dataset.loc[dataset['FamilySize'] == 1, 'IsAlone'] = 1

train_df[['IsAlone', 'Survived']].groupby(['IsAlone'], as_index=False).mean()

"""- Drop useless features:"""

train_df = train_df.drop(['Parch', 'SibSp', 'FamilySize'], axis=1)
test_df = test_df.drop(['Parch', 'SibSp', 'FamilySize'], axis=1)
combine = [train_df, test_df]

train_df.head()

"""## 'Age': Suvivors by age:"""

g = sns.FacetGrid(train_df, col='Survived', height=5)
g.map(plt.hist, 'Age', bins=32)
plt.show()

"""- Most passengers are between 15-35 age;
- Infants - age <=4 - had high survival rate;
- Oldest passengers - age = 80 - survived;
- Large number of 15-25 year olds did not survive.

-------------------------------
Completing a numerical continuous feature.

Now we should start estimating and completing missing or null values.
"""

guess_ages = np.zeros((2,3))
guess_ages

for dataset in combine:
    for i in range(0, 2):
        for j in range(0, 3):
            guess_df = dataset[(dataset['Sex'] == i) & \
                                  (dataset['Pclass'] == j+1)]['Age'].dropna()

            age_guess = guess_df.median()

            # Convert random age float to nearest .5 age
            guess_ages[i,j] = int( age_guess/0.5 + 0.5 ) * 0.5
            
    for i in range(0, 2):
        for j in range(0, 3):
            dataset.loc[ (dataset.Age.isnull()) & (dataset.Sex == i) & (dataset.Pclass == j+1),\
                    'Age'] = guess_ages[i,j]

    dataset['Age'] = dataset['Age'].astype(int)

train_df.head(2)

"""---------------------------
- Age bands to determine correlations with Survived:
"""

train_df['AgeBand'] = pd.cut(train_df['Age'], 10)
train_df[['AgeBand', 'Survived']].groupby(['AgeBand'], as_index=False).mean()

for dataset in combine:    
    dataset.loc[ dataset['Age'] <= 8, 'Age'] = 0
    dataset.loc[(dataset['Age'] > 8) & (dataset['Age'] <= 16), 'Age'] = 1
    dataset.loc[(dataset['Age'] > 16) & (dataset['Age'] <= 24), 'Age'] = 2
    dataset.loc[(dataset['Age'] > 24) & (dataset['Age'] <= 32), 'Age'] = 3
    dataset.loc[(dataset['Age'] > 32) & (dataset['Age'] <= 40), 'Age'] = 4
    dataset.loc[(dataset['Age'] > 40) & (dataset['Age'] <= 48), 'Age'] = 5
    dataset.loc[(dataset['Age'] > 48) & (dataset['Age'] <= 56), 'Age'] = 6
    dataset.loc[(dataset['Age'] > 56) & (dataset['Age'] <= 64), 'Age'] = 7
    dataset.loc[(dataset['Age'] > 64) & (dataset['Age'] <= 72), 'Age'] = 8
    dataset.loc[ dataset['Age'] > 72, 'Age'] = 9

np.sort(train_df['Age'].unique())

#drop the useless column
train_df = train_df.drop(['AgeBand'], axis=1)
combine = [train_df, test_df]
train_df.head(1)

"""## Creating new feature 'Title' extracting from existing 'Name':"""

# extracting 'Title' from the 'Name'
for dataset in combine:
    dataset['Title'] = dataset.Name.str.extract(' ([A-Za-z]+)\.', expand=False)

pd.crosstab(train_df['Title'], train_df['Sex'])

"""- We can replace many titles with a more common name or classify them as 'Rare'."""

for dataset in combine:
    dataset['Title'] = dataset['Title'].replace(['Lady', 'Countess','Capt', 'Col',\
 	'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')

    dataset['Title'] = dataset['Title'].replace('Mlle', 'Miss')
    dataset['Title'] = dataset['Title'].replace('Ms', 'Miss')
    dataset['Title'] = dataset['Title'].replace('Mme', 'Mrs')

train_df[['Title', 'Survived']].groupby(['Title'], as_index=False).mean()

"""### Converting the categorical titles to ordinal:"""

title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Rare": 5}
for dataset in combine:
    dataset['Title'] = dataset['Title'].map(title_mapping)
    dataset['Title'] = dataset['Title'].fillna(0)

train_df.head()

"""## Dropping useless features:"""

train_df = train_df.drop(['Ticket', 'Cabin', 'Name', 'PassengerId'], axis=1)
test_df = test_df.drop(['Ticket', 'Cabin', 'Name'], axis=1)

combine = [train_df, test_df]

"""## Survivors according embarked port:"""

train_df['Embarked'].unique()

train_df[["Embarked", "Survived"]].groupby(['Embarked'], as_index=False).mean()

"""- There are 2 null value."""

train_df["Embarked"].value_counts()

# most common
train_df["Embarked"].mode()

# Filling missing values with most common occurance
for dataset in combine:
    dataset['Embarked'] = dataset['Embarked'].fillna(train_df["Embarked"].mode()[0])

for data in combine:
  data["Embarked"] = data["Embarked"].map({'C': 0, 'Q': 1, 'S':2}).astype(int)

train_df[["Embarked", "Survived"]].groupby(['Embarked'], as_index=False).mean()

train_df.info()

train_df.head()

"""## 'Fare': """

# filling missing value
test_df['Fare'].fillna(test_df['Fare'].dropna().median(), inplace=True)

train_df['Fare'].nunique()

train_df[['Fare']].describe().T

train_df['Fare'].mode()

# intervals based on quantile: 25%, 50%, 75%
pd.qcut(train_df['Fare'], 4)[0:4]

"""- Convert the Fare feature to ordinal values based on quantiles:"""

for dataset in combine:
    dataset.loc[ dataset['Fare'] <= 7.91, 'Fare'] = 0
    dataset.loc[(dataset['Fare'] > 7.91) & (dataset['Fare'] <= 14.454), 'Fare'] = 1
    dataset.loc[(dataset['Fare'] > 14.454) & (dataset['Fare'] <= 31), 'Fare']   = 2
    dataset.loc[ dataset['Fare'] > 31, 'Fare'] = 3
    # dataset['Fare'] = dataset['Fare'].astype(int)

combine = [train_df, test_df]

train_df.head(3)

train_df.info()

test_df.info()

"""# Models and Predictions:

## Train Test split
"""

X_train = train_df.drop("Survived", axis=1)
Y_train = train_df["Survived"]
X_test  = test_df.drop("PassengerId", axis=1).copy()
X_train.shape, Y_train.shape, X_test.shape

"""### Logistic Regression:"""

# initializing

logreg = LogisticRegression()

# training
logreg.fit(X_train, Y_train)

Y_pred = logreg.predict(X_test)

# simulated score
logreg.score(X_train, Y_train) * 100

# Y_pred

"""### Random Forest:"""

random_forest = RandomForestClassifier(n_estimators=100)

random_forest.fit(X_train, Y_train)

Y_pred_RF = random_forest.predict(X_test)

random_forest.score(X_train, Y_train) * 100

"""### Decision Tree:"""

# Decision Tree

decision_tree = DecisionTreeClassifier()

decision_tree.fit(X_train, Y_train)

Y_pred_DT = decision_tree.predict(X_test)

round(decision_tree.score(X_train, Y_train) * 100, 2)

"""### Artificial Neural Network:"""

model = Sequential()

model.add(Dense(units = 7, activation='relu'))
model.add(Dense(units = 2, activation='relu'))

# output layer with sigmoid activate fuction, better to classification problem
model.add(Dense(units = 1, activation='sigmoid'))

# For a binary classification problem
model.compile(loss='binary_crossentropy', optimizer='adam')

model.fit(x=X_train, y=Y_train, epochs=4, verbose = 1)

model.history.history

# testing predictions in another way
Y_pred_ANN = (model.predict(X_test) > 0.5).astype("int32")

# testing predictions in another way
Y_pred_TEST = (model.predict(X_train) > 0.5).astype("int32")

# we only get 1 False Negative and 3 False Positive
print(confusion_matrix(Y_train,Y_pred_TEST))

