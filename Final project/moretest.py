import pandas as pd
import numpy as np

dateformat = "2007-11-14"
nasdaqmovement = pd.read_csv("NDX Data.csv")
nasdaqmovement = nasdaqmovement.values
print("DATE:", dateformat)
indices = np.argwhere(nasdaqmovement[:,0] == dateformat).ravel()
print(indices)
movement = nasdaqmovement[indices[0], 4] - nasdaqmovement[indices[0], 1]
movement = round(movement, 2)
percentage = (movement / nasdaqmovement[indices[0], 1]) * 100
percentage = round(percentage, 2)
print("The market on", dateformat, "ended with", movement, "movement. Which is a total of", str(percentage) + "%", "change")

"""
regresslst = []
regresslst.extend([sentimentvalue, percentage, dateformat])
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