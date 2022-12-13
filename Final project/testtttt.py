import nltk
import calendar
import matplotlib.pyplot as plt
#nltk.download('wordnet')
#nltk.download('omw-1.4')
#nltk.download("punkt")
from nltk import word_tokenize, WordNetLemmatizer, RegexpTokenizer
#from nltk.corpus import stopwords
from newspaper import Article
from googlesearch import search
from newspaper import Config
from itertools import chain
from urllib.parse import urlparse
import pandas as pd
import numpy as np
from scipy import stats
#nltk.download('stopwords')

regresseddate = "2022-12-09"
"""
nasdaqmovement = pd.read_csv("NDX Data.csv")
nasdaqmovement = nasdaqmovement.values
#print(nasdaqmovement)
indices = np.argwhere(nasdaqmovement[:,0] == regresseddate).ravel()
print(indices)
john = nasdaqmovement[indices[0], 4] - nasdaqmovement[indices[0], 1]
print(john)
"""
"""
nasdaqmovement = pd.read_csv("NDX Data.csv")
nasdaqmovement = nasdaqmovement.values
indices = np.argwhere(nasdaqmovement[:,0] == regresseddate).ravel()
movement = nasdaqmovement[indices[0], 4] - nasdaqmovement[indices[0], 1]
percentage = (movement / nasdaqmovement[indices[0], 1]) * 100
print(movement, percentage)
"""
"""
regresslst = [1,2, "3"]

with open("RegressionModel.txt", "r+") as f:
    lines = list(f)
    f.seek(0)
    for i in range(min(len(lines), len(regresslst))):
        f.write(lines[i].rstrip('\n'))
        f.write(' ')
        f.write(str(regresslst[i]))
        f.write('\n')
    f.truncate()
"""

regressmodel = open("RegressionModel.txt", "r")
sentmodel = regressmodel.readline().split()
percentmodel = regressmodel.readline().split()
sentmodel = [float(x) for x in sentmodel]
percentmodel = [float(x) for x in percentmodel]
slope, intercept, r, p, std_err = stats.linregress(sentmodel, percentmodel)

def myfunc(sentmodel):
    return slope * sentmodel + intercept

mymodel = list(map(myfunc, sentmodel))

plt.scatter(sentmodel, percentmodel)
plt.plot(sentmodel, mymodel)
plt.show()