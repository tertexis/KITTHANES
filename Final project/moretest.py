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

f = open("ex1.txt", "r")
content = f.readline()
g = open("excluded.txt", "r")
content1 = g.readline()

lst = []
lst.append(content1)
lst.append(content)
if str(content1) == str(content):
    print("true")
else:
    print("false")
print(lst)