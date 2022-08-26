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

    def __init__(self, id, other, name, a):
        self.book_id = id
        self.good_id = other
        self.rating = -1
        self.title = name
        self.tags = [""]
        self.author = a
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
rules = open("rules1.csv")
user_list = []
book_dict = dict()
#titles = dict()
tags = dict()
reverse_tags = dict()
good_id_to_id = dict()


def read_data():
    test_data = open("AskMissy_Test/Test_Data/englishratings.csv", "r", encoding = "UTF8")
    test_data.seek(0)
    csvreader = csv.reader(test_data)
    #next(csvreader)

    book_data = open("mySQL_Scripts/books.csv", "r", encoding = "UTF8")
    book_data.seek(0)
    bookreader = csv.reader(book_data)
    next(bookreader)

    for row in bookreader:
        book_dict[int(row[0])] = book(row[0], row[1], row[10], row[7])
        good_id_to_id[row[1]] = row[0]


    for x in range(53425):
        user_list.append(user(x))

    a = 0
    for row in csvreader:
        user_list[int(row[0])].add_book(book_dict[int(row[1])])
        a += 1

    tags_reader_file = open("mySQL_Scripts/newtags.csv", "r",  encoding = "UTF8")
    tag_association_reader = csv.reader(tags_reader_file)

    for row in tag_association_reader:
        tags[row[0]] = row[1]
        reverse_tags[row[1]] = row[0]

    tags_file = open("mySQL_Scripts/book_tags_500.csv", "r",  encoding = "UTF8")
    tagreader = csv.reader(tags_file)
    next(tagreader)

    for row in tagreader:
        book_dict[int(good_id_to_id[row[0]])].tags.append(row[1])


#For website use functions
#user id is x
#tag to be sorted is tag
#If all reccomendations are to be displayed tag should be ""
def findUser_website(x, tag):
    read_data()
    gen_reccomendatrions_website(x)
    rec_books = []

    for a in range(len(user_list[x].recommended_books)):
        for b in user_list[x].recommended_books[a].tags:
            if (b == ''):
                random123 = 2
            elif(int(b) == int(tag)):
                rec_books.append(int(a))
    #print(rec_books)
    return rec_books

def gen_reccomendatrions_website(x):
    rules = open("rules1.csv")
    csvreader = csv.reader(rules)
    next(csvreader)
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
        if any(elem in books for elem in left):
            for r in right:
                if (r not in rec):
                    if(r not in books):
                        user_list[x].recommended_books.append(book_dict[int(r)])
                        rec.append(r)
    #user_list[x].recommended_books = sorted(set(user_list[x].recommended_books))

    for a in user_list[x].all_books:
        if (a in user_list[x].recommended_books):
            print("removed")
            user_list[x].recommended_books.remove(a)

def book_recommendation(book_id):
    rules = open("rules1.csv")
    csvreader = csv.reader(rules)
    next(csvreader)
    rec_book = ""
    top_conf = 0.01

    for y in csvreader:
        y[0] = y[0].replace("(","")
        y[0] = y[0].replace(")", "")
        y[0] = y[0].replace(",","")
        y[1] = y[1].replace("(", "")
        y[1] = y[1].replace(")", "")
        y[1] = y[1].replace(",", "")
        left = y[0].split(" ")
        right = y[1].split(" ")
        if(len(left) == 1):
            if(book_id in right):
                if(top_conf < float(y[2])):
                    top_conf = float(y[2])
                    rec_book = left[0]
        if(len(right) == 1):
            if(book_id in left):
                if (top_conf < float(y[2])):
                    top_conf = float(y[2])
                    rec_book = right[0]
    #print(rec_book)
    if(rec_book != ""):
        return int(rec_book)
    else:
        return -1

read_data()