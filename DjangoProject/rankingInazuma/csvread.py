import csv


with open('inazuma.csv', newline='', encoding='utf8') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        print(row[0])
        print(row[1])
        print(row[2])

