import nltk
import calendar
import matplotlib.pyplot as plt
#nltk.download('wordnet')
#nltk.download('omw-1.4')
#nltk.download("punkt")
from nltk import word_tokenize, WordNetLemmatizer
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

def textprocessing(lst):
    """Clean texts, remove all punctuations"""
    def remove_punc(string):
        """Main module for removing punctuation"""
        punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''
        for ele in string:  
            if ele in punc:  
                string = string.replace(ele, "") 
        return string
    tokens = word_tokenize(lst)
    cleanedtokens = [remove_punc(i).lower() for i in tokens] #remove whitespaces from previous line
    return list(filter(None, cleanedtokens))  #removes remaining punctuations

def lemmatization(text):
    """Change verbs to its neutural form"""
    global excludedlst #Machine-Learning list
    return [WordNetLemmatizer().lemmatize(t, "v") for t in text if t not in excludedlst] 

def googlesearch(query, sr):
    """Google searchs module"""
    print("Searching NDX markets news for:", date)
    searchlst = []
    for j in search(query, tld="co.in", num=sr, stop=sr, pause=1):
        searchlst.append(j)
    with open('linklist.txt', 'w') as f:
        for link in searchlst:
            f.write(link + "\n")
    print("Search completes!.... Recording urls")

def processurl(localurl, user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"):
    """This functions cooporate with article plugin to turn website's texts to string"""
    config = Config()
    config.browser_user_agent = user_agent
    article = Article(localurl, config=config)
    article.download()
    try:
        article.parse()
    except:
        #some website couldn't be passed and would result in 0 words analyzed which would then get excluded the next time this run
        pass
    article.nlp()
    localtext = article.summary #First filtering of the text
    return localtext

def processeverything(text):
    """The functions which connect everything to works together"""
    processedtoken = textprocessing(text) #Remove punctuations, blank spaces
    processedtexts = lemmatization(processedtoken)
    return processedtexts

def processdict(textfilename):
    """This function basically process bearish and bullish word"""
    with open(textfilename, "r") as f:
        text = f.read()
    words = text.split()
    word_list = []
    for word in words:
        word_list.append(word)
    return word_list

def findexclude():
    """This functions does the automatic exclusion of faulty websites"""
    with open("faultyurl.txt", "r") as file:
        lines = file.readlines()
        result = []
        for line in lines:
            line = line.strip()
            result.append(" -site:" + line)
        result_string = "".join(result)
        return result_string

def processexclude():
    """This functions fully updates excluded.txt by doing arithmetic of the same words when new common words get appended"""
    file = open("excluded.txt", "r")
    word_counts = {}
    for line in file:
        if line != "":
            try:
                word, count = line.split(":")
            except:
                #error will happen occasionally when this code is trying to format excluded.txt, so this will handle everything after formatting correctly
                continue
        else:
            pass
        count = int(count)
        if word in word_counts:
            word_counts[word] += count
        else:
            word_counts[word] = count
    total_count = 0
    for word, count in word_counts.items():
        total_count += count
    file.close()
    with open('excluded.txt', 'w') as f:
        dict_count = word_counts
        items = dict_count.items()
        for key, value in items:
            f.write(key + ': ' + str(value) + '\n')

def findintersects(diction):
    """This is the main function for language processing"""
    global processedtotalword
    count = 0
    excludedword = []
    for scanning in processedtotalword:
        if scanning in diction:
            count += 1
        else:
            excludedword.append(scanning)
    frequency = nltk.FreqDist(excludedword)
    return count, frequency.most_common(4)

def sentimize():
    """The main function for computing sentiment value"""
    bearwords = processdict("bearish.txt") #Process dictionaries
    bullwords = processdict("bullish.txt")
    redindices = findintersects(bearwords)[0] #Simple intersecting code
    greenindices = findintersects(bullwords)[0]
    commonexcluded = findintersects(bearwords + bullwords)[1] #this line return top 4 words that are not included in both bear and bullwords
    file = open("excluded.txt", "a")
    for item in commonexcluded:
        file.write("{} : {}\n".format(item[0], item[1]))
        #append the top 4 common words to excluded.txt 
    file.close()
    percentile = 100 / (redindices + greenindices)
    stvl = -(percentile * redindices) + (percentile * greenindices)
    return stvl, greenindices, redindices

def machinelearnstop():
    """Semi-machine learning, by appending the words that get excluded for above 800 times to stopwords.txt where it wouldn't get analyzed anymore, also removes orignal world from excluded.txt"""
    with open('excluded.txt', 'r') as infile:
        data = infile.read()
    lines = data.split('\n')

    with open('stopwords.txt', 'a') as outfile:
        for line in lines:
            if line != "":
                try:
                    word, count = line.split(':')
                except:
                    print("error occured while machine learning at line:", line, "exception already handled")
                    continue
            else:
                pass
            word = word.strip()
            count = count.strip()
            if int(count) >= 800:
                outfile.write(word + " ")
                data = data.replace(line, '') #remove original strings
    lines = data.split('\n')

    lines = [line for line in lines if line.strip() != '']

    data = '\n'.join(lines)

    with open('excluded.txt', 'w') as infile:
        infile.write(data) #rewrite

def findregresseddate(year, m, day):
    k = ""
    l = ""
    if len(str(m)) == 1:
        l = "0" + str(m)
    else:
        l = str(m)
    if len(str(day)) == 1:
        k = "0" + str(day)
    else:
        k = str(day)
    regresseddate = year + "-" + l + "-" + k
    return regresseddate

def printsentiment(sentimentvalue):
    global statistics
    if sentimentvalue <= -20:
        print("The market will likely be red for the day")
        statistics.append("red")
    elif sentimentvalue <= -5 and sentimentvalue > -20:
        print("The market will likely be mild red for the day")
        statistics.append("red")
    elif sentimentvalue <= 5 and sentimentvalue > -5:
        print("The market will likely be sideway for the day")
        statistics.append("side")
    elif sentimentvalue >= 5 and sentimentvalue < 20:
        print("The market will likely be mild green for the day")
        statistics.append("green")
    elif sentimentvalue >= 20:
        print("The market will likely be green for the day")
        statistics.append("green")

print("\n" +"Hello, I'm a semi-machine learning natural language processor. This particular model was developed for using sentiment analysis to forecast market movement." + "\n" + "With each time the program is ran, it develops more and more efficient.")
print("I have been trained to examine historical market indices, more precisely, this model has been trained to examine historical news of the NASDAQ 100 index, although I could realistically be used with any shares model.", "\n")
print("After the natural language processing is done, the data result will get saved for statistics purpose", "\n")
print("To get started, pick the day you want to examine the sentimentality of the Nasdaq.", "\n")

d = input("Enter date(1-31): ")
m = int(input("Enter month(1-12): "))
y = input("Enter year(20xx): ")
sr = int(input("enter search range(5-10 recommended): "))
day = d
month = m
year = y
totalword = []
statistics = []

k = open("stopwords.txt", "r")
str1 = k.read()
excludedlst = str1.split()
k.close()

date = calendar.month_abbr[month] + " " + day + " " + year
dateformat = findregresseddate(year, month, day)
toexclude = findexclude() #call ine 79
searchqueue = ("NASDAQ Futures news " + date)
googlesearch(searchqueue + " " + toexclude, sr)

f = open("linklist.txt", "r")
nextlink = f.readline() #run through textt files of linklist
uselesslink = []
urlcount = 1
while nextlink != "":
    """Main loops of computing every functions together"""
    usablelink = nextlink.strip()
    url = usablelink
    try:
        text = processurl(url) #Main module for filtering-converting url to texts call line 48
    except:
        pass
    cleantext = processeverything(text) #Main module for processing links, call 63
    if len(cleantext) == 0:
        print("Faulty url found. At url No.", urlcount, "which returns 0 words.")
        uselesslink.append(url)
        print("This specific url will be ignored the next time this program runs")
    else:
        print("URL No.", urlcount, "Analyzed: ", len(cleantext), "words found")
    totalword.append(cleantext) #append list of processed words to another list
    nextlink = f.readline()
    urlcount += 1
f.close()

with open("faultyurl.txt", "a") as file: #Automatically collect faulty urls
    for string in uselesslink:
        parsed_url = urlparse(string)
        domain = parsed_url.netloc
        parts = domain.split(".") 
        second_level_domain = parts[-2]
        top_level_domain = parts[-1] #www.youtube.com/sdasfasfas---> youtube.com
        result = second_level_domain + "." + top_level_domain 
        file.write(result + "\n")

print("\n", "Cleaning and neutralizing process completes")
processedtotalword = list(chain.from_iterable(totalword)) #flatten 2d list
print(sr, "sites processed, words found: ", len(processedtotalword), "\n")
sentimentvalue, greenbulls, redbears = sentimize() #calculation of sentiments line 131
sentimentvalue = round(sentimentvalue, 2)
greenpercent = round(((greenbulls / (greenbulls + redbears)) * 100),2)
redpercent = round(((redbears / (greenbulls + redbears)) * 100), 2)

print("The following were the results after computations")
print("Out of the total number of words that intersected with the algorithm, ...", "\n")
print("The algorithm determined that", str(greenpercent) + "%" ,"of the total number of words were indicative of a bullish situation.", "\n")
print("On the other hand...", "\n")
print("The algorithm determined that", str(redpercent) + "%" ,"of the total number of words were indicative of a bearish situation.", "\n")

print("Sentiment values processed(-100 to 100): ", sentimentvalue)
print("Based on the results of the computation, the program predicts that...")

printsentiment(sentimentvalue)

#Main natural language processes end here.

part2 = input("\n" + "Would you like to assess the statistics? (Y/N) " + "\n")

if part2 == "Y":
    statistics.extend([date, sentimentvalue, greenpercent, redpercent, greenbulls, redbears, len(processedtotalword), len(excludedlst), len(toexclude.split()), (greenbulls + redbears)])
    print("The market will close in the", statistics[1], "on", statistics[0], "according to the final computed result.", "\n")
    print(statistics[7], "words analyzed,", statistics[8], "machine-excluded words and", statistics[9], "machine-excluded links", "\n")
    print(statistics[10], "words were used in the calculation", str(statistics[3]) + "%" + " of which were bullish words and", str(statistics[4]) + "%" + " of which were bearish ones.", "\n")
    print("The Final Sentiment Value is: ", statistics[2], "\n")
else:
    print("Understood, statistics model not initiated")
    pass

part3 = input("Do you agree to let us save your results for future uses? (Y/N) " + "\n")

if part3 == "Y":
    print("Thank you, the data will be analyzed upon completion", "\n")
    print("Confirming result with past database,...", "\n")
    nasdaqmovement = pd.read_csv("NDX Data.csv")
    nasdaqmovement = nasdaqmovement.values
    try:
        indices = np.argwhere(nasdaqmovement[:,0] == dateformat).ravel()
        movement = nasdaqmovement[indices[0], 4] - nasdaqmovement[indices[0], 1]
        movement = round(movement, 2)
        percentage = (movement / nasdaqmovement[indices[0], 1]) * 100
        percentage = round(percentage, 2)
        print("The market on", dateformat, "ended with", movement, "movement. Which is a total of", str(percentage) + "%", "change", "\n")
        regresslst = []
        regresslst.extend([sentimentvalue, percentage, dateformat])
        forregress = input("Save your result for regression model? (Y/N) " + "\n")
        if forregress == "Y":
            with open("RegressionModel.txt", "r+") as f:
                lines = list(f)
                f.seek(0)
                for i in range(min(len(lines), len(regresslst))):
                    f.write(lines[i].rstrip('\n'))
                    f.write(' ')
                    f.write(str(regresslst[i]))
                    f.write('\n')
                f.truncate() #incase shrinking happens
        else:
            print("Understood, the program wont append datas for regression model")
    except:
        print("Error while trying to acess past market data on", dateformat, "was it Saturday/Sunday or a holiday?")
    finally:
        print("Updating the libaries..")
        processexclude() #Second machine learning module, this one process excluded words
        machinelearnstop() #This one updates exclu
        print("Natural processer Terminated")
else:
    print("Understood, the program will not record any result")
    print("Natural processer Terminated")

part4 = input("Would you like to initiate the current regression model? (Y/N) ")

if part4 == "Y":
    regressmodel = open("RegressionModel.txt", "r")
    sentmodel = regressmodel.readline().split()
    percentmodel = regressmodel.readline().split()
    sentmodel = [float(x) for x in sentmodel]
    percentmodel = [float(x) for x in percentmodel]
    slope, intercept, r, p, std_err = stats.linregress(sentmodel, percentmodel)
    def myfunc(sentmodel):
        return slope * sentmodel + intercept
    mymodel = list(map(myfunc, sentmodel))
    plt.title("The Relationship of Sentimentality: Market Movement")
    plt.xlabel("Setimental Value (-100 to 100)")
    plt.ylabel("Market Movement (In percentage)")
    plt.scatter(sentmodel, percentmodel)
    plt.plot(sentmodel, mymodel)
    plt.show()
    print("Current relationship rate: ", r)
    print("Terminating the regression Model.")
else:
    print("Understood, See you later !")