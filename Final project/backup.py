import nltk
import calendar
import matplotlib as plt
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
    global excludedlst
    return [WordNetLemmatizer().lemmatize(t, "v") for t in text if t not in excludedlst] 

def googlesearch(query, sr):
    """Google searchs module"""
    print("Searching US markets news for:", date)
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
        #some website couldn't be passed and would result in 0 words analyzed which would then get excluded the next times
        pass
    article.nlp()
    localtext = article.summary #basic summarization of texts (remove neutral words)
    return localtext

def processeverything(text):
    """The functions which connect everything to works together"""
    processedtoken = textprocessing(text)
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
    bearwords = processdict("bearish.txt")
    bullwords = processdict("bullish.txt")
    redindices = findintersects(bearwords)[0]
    greenindices = findintersects(bullwords)[0]
    commonexcluded = findintersects(bearwords + bullwords)[1] #this code find top 4 words that are not included in both bear and bullwords
    file = open("excluded.txt", "a")
    for item in commonexcluded:
        file.write("{} : {}\n".format(item[0], item[1]))
        #append the top 4 common words to excluded.txt 
    file.close()
    percentile = 100 / (redindices + greenindices)
    stvl = -(percentile * redindices) + (percentile * greenindices)
    return stvl, greenindices, redindices

def machinelearnstop():
    """Semi-machine learning, by appending the words that get excluded for above 500 times to stopwords.txt where it wouldn't get analyzed anymore, also removes orignal world from excluded.txt"""
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

#print("Hello, welcome everyone to")

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

statistics.append(date)
toexclude = findexclude()
searchqueue = ("NASDAQ news " + date)
googlesearch(searchqueue + " " + toexclude, sr)

f = open("linklist.txt", "r")
nextlink = f.readline()
uselesslink = []
urlcount = 1
while nextlink != "":
    """Main loops of computing every functions together"""
    usablelink = nextlink.strip()
    url = usablelink
    try:
        text = processurl(url)
    except:
        pass
    cleantext = processeverything(text)
    if len(cleantext) == 0:
        print("Faulty url found. At url No.", urlcount, "which returns 0 words.")
        uselesslink.append(url)
        print("This specific url will be ignored the next time this program runs")
    else:
        print("URL No.", urlcount, "Analyzed: ", len(cleantext), "words found")
    totalword.append(cleantext)
    nextlink = f.readline()
    urlcount += 1
f.close()

with open("faultyurl.txt", "a") as file: #collect faulty website result in faultyurl.txt
    for string in uselesslink:
        parsed_url = urlparse(string)
        domain = parsed_url.netloc
        parts = domain.split(".") #www.youtube.com/sdasfasfas
        second_level_domain = parts[-2]
        top_level_domain = parts[-1]
        result = second_level_domain + "." + top_level_domain
        file.write(result + "\n")

print("Cleaning and neutralizing process completes")
processedtotalword = list(chain.from_iterable(totalword))
print(sr, "sites processed, words found: ", len(processedtotalword))
sentimentvalue, greenbulls, redbears = sentimize()
sentimentvalue = round(sentimentvalue, 2)
greenpercent = round(((greenbulls / (greenbulls + redbears)) * 100),2)
redpercent = round(((redbears / (greenbulls + redbears)) * 100), 2)

print("The following were the results after computations")
print("Out of the total number of words that intersected with the algorithm, ...")
print("The algorithm determined that", str(greenpercent) + "%" ,"of the total number of words were indicative of a bullish situation.")
print("On the other hand...")
print("The algorithm determined that", str(redpercent) + "%" ,"of the total number of words were indicative of a bearish situation.")

print("Sentiment values processed(-100 to 100): ", sentimentvalue)
print("Based on the results of the computation, the program predicts that...")

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

part2 = input("Would you like to assess the statistics? (Y/N) ")

if part2 == "Y":
    statistics.append(sentimentvalue) #2
    statistics.append(greenpercent) #3
    statistics.append(redpercent) #4
    statistics.append(greenbulls) #5
    statistics.append(redbears) #6
    statistics.append(len(processedtotalword)) #7
    statistics.append(len(excludedlst)) #8
    statistics.append(len(toexclude.split())) #9
    statistics.append(greenbulls + redbears) #10
    print("\n", "The concluding computed result for the date:", statistics[0], "is that the market will closes in", statistics[1], "\n")
    print(statistics[7], "words analyzed,", statistics[8], "amount of machine ignored words,", statistics[9], "machine excluded links", "\n")
    print("The program computed: ", statistics[10], "words that contributed toward the calculation", statistics[3], "%", "of which were bullish words and", statistics[4], "%", "of which were bearish words", "\n")
    print("The final sentiment value were: ", statistics[2])
    pass
else:
    print("Program Terminating...")
    pass

print("Confirming result with past database,...", "\n")

nasdaqmovement = pd.read_csv("NDX Data.csv")
nasdaqmovement = nasdaqmovement.values
indices = np.argwhere(nasdaqmovement[:,0] == dateformat).ravel()
movement = nasdaqmovement[indices[0], 4] - nasdaqmovement[indices[0], 1]
movement = round(movement, 2)
percentage = (movement / nasdaqmovement[indices[0], 1]) * 100
percentage = round(percentage, 2)
print("The market on", dateformat, "ended with", movement, "movement. Which is a total of", str(percentage) + "%", "change")
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

print(regresslst)

processexclude()
machinelearnstop()