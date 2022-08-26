from efficient_apriori import apriori
import tkinter as tk
from tkinter import *
import csv
from csv import DictReader
import codecs
import random
types_of_encoding = ["utf8", "cp1252"]

class user:

    def __init__(self, id):
        self.user_id = id
        self.all_books = [] #list of all books to
        self.liked_books = []  # Books rated 4 or 5
        self.disliked_books = []  # Books rated 3 or below
        self.recommended_books = [] #Just a list of book ids with no ratings

    def add_book (self, book):
        self.all_books.append(book)
        if(int(book.rating) > 3):
            self.liked_books.append(book)
        if(int(book.rating) <=3):
            self.disliked_books.append(book)
    def __str__(self):
        x = str(self.user_id) + str(self.liked_books) + str(self.disliked_books)
        return x

class book:

    def __init__(self, id, other, name):
        self.book_id = id
        self.good_id = other
        self.rating = -1
        self.title = name
        self.tags = [""]
    def __int__(self):
        return self.id
    def __ge__(self, other):
        if(self.book_id > other.book_id):
            return True
        else:
            return False
    def __gt__(self, other):
        if(self.book_id < other.book_id):
            return True
        else:
            return False

#Global Variables
rules = open("output/rules1.csv")
user_list = []
book_dict = dict()
#titles = dict()
tags = dict()
reverse_tags = dict()
good_id_to_id = dict()

def findUser():
    x = int(userID.get())
    if(tagField.get()!= ""):
        tag = tagField.get()
    else:
        tag = ""
    readBooks.delete(0,END)
    reccomendedBooks.delete(0,END)
    gen_reccomendatrions()

    for a in range(len(user_list[x].all_books)):
        readBooks.insert(0,user_list[x].all_books[a].title)

    for a in range(len(user_list[x].recommended_books)):
        #print(user_list[x].recommended_books[a].tags)
        for b in user_list[x].recommended_books[a].tags:
            if (b == tag):
                reccomendedBooks.insert(0,user_list[x].recommended_books[a].title)

def read_data():
    test_data = open("Test_Data/ratings.csv", "r", encoding = "UTF8")
    test_data.seek(0)
    csvreader = csv.reader(test_data)
    next(csvreader)

    book_data = open("../mySQL_Scripts/books.csv", "r", encoding = "UTF8")
    bookreader = csv.reader(book_data)
    next(bookreader)

    for row in bookreader:
        book_dict[int(row[0])] = book(row[0], row[1], row[10])
        good_id_to_id[int(row[1])] = int(row[0])

    for x in range(53425):
        user_list.append(user(x))

    a = 0
    for row in csvreader:
        user_list[int(row[0])].add_book(book_dict[int(row[1])])
        a += 1

    tags_reader_file = open("../mySQL_Scripts/newtags.csv", "r",  encoding = "UTF8")
    tag_association_reader = csv.reader(tags_reader_file)

    for row in tag_association_reader:
        tags[row[0]] = row[1]
        reverse_tags[row[1]] = row[0]

    tags_file = open("../mySQL_Scripts/book_tags_500.csv", "r",  encoding = "UTF8")
    tagreader = csv.reader(tags_file)
    next(tagreader)

    for row in tagreader:
        book_dict[good_id_to_id[int(row[0])]].tags.append(row[1])


def find_trends():
    input = []
    for x in user_list:
        temp = []
        for y in x.all_books:
            temp.append(int(y.book_id))
        input.append(temp)
        """
        for y in user_list[x.user_id].liked_books:
            input.append(y.book_id)
        """

    itemsets, rulesData = apriori(input, min_support=float(minSup.get()), min_confidence=float(minConf.get()))
    f1 = open("output/itemset.txt", 'w')
    if ruleFile.get() != "":
        f2 = open("output/" + ruleFile.get(), "w")
    else:
        f2 = open("output/rules.csv", "w")
    header= ["lhs", "rhs", "confidence"]
    writer = csv.writer(f2, lineterminator= '\n')
    writer.writerow(header)
    for x in itemsets:
        temp = itemsets.get(x)
        f1.write(str(temp))
        f1.write('\n')
    for x in rulesData:
        data = [x.lhs, x.rhs, x.confidence]
        writer.writerow(data)

def gen_reccomendatrions():
    if ruleFile.get() != "":
        rules = open("output/" + ruleFile.get())
    else:
        rules = open("output/rules.csv")
    csvreader = csv.reader(rules)
    next(csvreader)
    x = int(userID.get())
    rec = []
    books = []
    for a in user_list[x].all_books:
        books.append(a.book_id)
    for y in csvreader:
        y[0] = y[0].replace("(","")
        y[0] = y[0].replace(")", "")
        y[0] = y[0].replace(",","")
        #print(y[0])
        y[1] = y[1].replace("(", "")
        y[1] = y[1].replace(")", "")
        y[1] = y[1].replace(",", "")
        left = y[0].split(" ")
        right = y[1].split(" ")
        #print(left)
        """
        for l in left:
            if all(elem in l for elem in y[0]):
                for r in right:
                    if (r not in rec):
                        user_list[x].recommended_books.append(book_dict[r])
                        rec.append(r)
        """
        if any(elem in books for elem in left):
            for r in right:
                if (r not in rec):
                    if (r not in books):
                        user_list[x].recommended_books.append(book_dict[int(r)])
                        rec.append(r)
    user_list[x].recommended_books = sorted(set(user_list[x].recommended_books))
    #random.shuffle(user_list[x].recommended_books)

    for a in user_list[x].recommended_books:
        for b in user_list[x].recommended_books:
            if(a.book_id == b.book_id):
                user_list[x].recommended_books.remove(b)





#Basic UI to show users
root = Tk()

root.title("Algorithm UI")

root.minsize(width= 350, height= 350)
root.maxsize(width= 500, height= 500)

frame1 = tk.Frame(root, borderwidth= 2, relief= 'ridge')
frame1.grid(column= 0, row= 1, sticky='nsew')

frame2 = tk.Frame(root, borderwidth= 2, relief= 'ridge')
frame2.grid(column= 0, row= 2)

frame3 = tk.Frame(root, borderwidth= 2, relief= 'ridge')
frame3.grid(column= 0, row= 0)

#Row 1 Labels for parameter

suppLabel = Label(frame1, text = "Minimmum Support")
suppLabel.grid(column= 0, row= 0)

confLabel = Label(frame1, text = "Minimmum Confidence")
confLabel.grid(column= 1, row= 0)

#Row 2 parameter entry

minSup = Entry(frame1, bd= 2)
minSup.grid(column= 0, row= 1)

minConf = Entry(frame1, bd= 2)
minConf.grid(column= 1, row= 1)

aprioriB = tk.Button(frame1, text= "Apriori", command=lambda:find_trends())
aprioriB.grid(column=2, row= 1)

#Row 3 Label for user display

userLabel = Label(frame2, text= "Find user:")
userLabel.grid(column= 0, row= 1)

userID = Entry(frame2, bd= 2)
userID.grid(column= 1, row= 1, sticky='nsew')

runSearch = tk.Button(frame2, text= "Search", command=lambda:findUser())
runSearch.grid(column= 2, row= 1)

tagLabel = Label(frame2, text="Tag to search")
tagLabel.grid(column= 0, row= 0)

tagField = Entry(frame2, bd = 2)
tagField.grid(column= 1, row= 0)

#Row 4 Listboxes for user book lists

readLabel = Label(frame2, text="Read Books")
readLabel.grid(column= 0, row= 2)

readBooks = tk.Listbox(frame2)
readBooks.grid(column= 0, row= 3)

recLabel = Label(frame2, text="Recommended Books")
recLabel.grid(column= 1, row= 2)

reccomendedBooks = tk.Listbox(frame2)
reccomendedBooks.grid(column= 1, row= 3)

#Row 5 Read Data button
ruleFile = Entry(frame3, bd= 2)
ruleFile.grid(column=0, row=0)

runB = tk.Button(frame3, text= "Read in Data", command=lambda:read_data())
runB.grid(column=1, row= 0)

root.mainloop()