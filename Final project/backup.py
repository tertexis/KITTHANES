import nltk
import calendar
import matplotlib
#nltk.download('wordnet')
#nltk.download('omw-1.4')
#nltk.download("punkt")
from nltk import word_tokenize, WordNetLemmatizer, RegexpTokenizer
from nltk.corpus import stopwords
from newspaper import Article
from googlesearch import search
from newspaper import Config
from itertools import chain
from urllib.parse import urlparse
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

def findfreq(text, n = 3):
    """Machine learning purpose""" #extracting top freq from each sites
    en_stopws = stopwords.words('english')  #  loads the default stopwords list
    #en_stopws.append('spam')  # add custom words to the list
    text = [token for token in text if token not in en_stopws]  # filter stopwords
    frequency = nltk.FreqDist(text)
    return frequency.most_common(n)

def lemmatization(text):
    """Change verbs to its neutural form"""
    excludedwords = []
    return [WordNetLemmatizer().lemmatize(t, "v") for t in text] 

def printchange(words):
    """Testing lemmatizing modules"""
    for word in words:
        print (word + "-->"+ WordNetLemmatizer().lemmatize(word,'v'))

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
    config = Config()
    config.browser_user_agent = user_agent
    article = Article(localurl, config=config)
    article.download()
    try:
        article.parse()
    except:
        pass
    article.nlp()
    localtext = article.summary #basic summarization of texts (remove neutral words)
    return localtext

def processeverything(text):
    processedtoken = textprocessing(text)
    processedtexts = lemmatization(processedtoken)
    topfreq = findfreq(processedtexts)
    try:
        topfreqlst.append(topfreq)
    except:
        pass
    return processedtexts

def processdict(textfilename):
    with open(textfilename, "r") as f:
        text = f.read()
    words = text.split()
    word_list = []
    for word in words:
        word_list.append(word)
    return word_list

def findexclude():
    with open("faultyurl.txt", "r") as file:
        lines = file.readlines()
        result = []
        for line in lines:
            line = line.strip()
            result.append(" -site:" + line)
        result_string = "".join(result)
        return result_string

def processexclude():
    file = open("excluded.txt", "r")
    word_counts = {}
    for line in file:
        word, count = line.split(":")
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
        dict = word_counts
        items = dict.items()
        for key, value in items:
            f.write(key + ': ' + str(value) + '\n')

def findintersects(diction):
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
    bearwords = processdict("bearish.txt")
    bullwords = processdict("bullish.txt")
    redindices = findintersects(bearwords)[0]
    greenindices = findintersects(bullwords)[0]
    commonexcluded = findintersects(bearwords + bullwords)[1]
    #print(commonexcluded, type(commonexcluded))
    file = open("excluded.txt", "a")
    for item in commonexcluded:
        file.write("{} : {}\n".format(item[0], item[1]))
    file.close()

    print("The program found: ", redindices, "bearish words")
    print("The program found: ", greenindices, "bullish words")
    percentile = 100 / (redindices + greenindices)
    stvl = -(percentile * redindices) + (percentile * greenindices)
    return stvl

def machinelearnstop():
    with open('excluded.txt', 'r') as infile:
        data = infile.read()

    lines = data.split('\n')

    with open('stopwords.txt', 'a') as outfile:
        for line in lines:
            word, count = line.split(':')

            word = word.strip()
            count = count.strip()

            if int(count) >= 2000:
                outfile.write(word + " ")
                data = data.replace(line, '') #remove original strings

    lines = data.split('\n')

    lines = [line for line in lines if line.strip() != '']

    data = '\n'.join(lines)

    with open('excluded.txt', 'w') as infile:
        infile.write(data) #rewrite

d = input("Enter date(1-31): ")
m = int(input("Enter month(1-12): "))
y = input("Enter year(20xx): ")
sr = int(input("enter search range(5-10 recommended): "))
day = d
month = m
year = y
#searchrange = 5
totalword = []
topfreqlst = []

date = calendar.month_abbr[month] + " " + day + " " + year
toexclude = findexclude()
searchqueue = ("NASDAQ news " + date)
print((searchqueue + toexclude))
googlesearch(searchqueue + " " + toexclude, sr)

f = open("linklist.txt", "r")
nextlink = f.readline()
uselesslink = []
urlcount = 1
while nextlink != "":
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

with open("faultyurl.txt", "a") as file: #collect faulty result
    for string in uselesslink:
        parsed_url = urlparse(string)
        domain = parsed_url.netloc
        parts = domain.split(".")
        second_level_domain = parts[-2]
        top_level_domain = parts[-1]
        result = second_level_domain + "." + top_level_domain
        file.write(result + "\n")

print("Cleaning and neutralizing process completes")
processedtotalword = list(chain.from_iterable(totalword))
print(sr, "sites processed, words found: ", len(processedtotalword))
sentimentvalue = sentimize()

print("Sentiment values processed(-100 to 100): ", sentimentvalue)

processexclude()

#print("Bear:", a)
#print("Bull: ", b)

#print(topfreqlst)
#print(processedtotalword)
#print(len(processedtotalword))

