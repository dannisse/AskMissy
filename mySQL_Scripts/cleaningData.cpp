#include <fstream>
#include <string>
#include <vector>
#include <iostream>
#include <sstream>
#include <algorithm>
#include <iomanip>


using namespace std;

vector<int> readBookList(string filename)
{
    ifstream file;

    file.open(filename);

    vector<int> bookIDList;

    //header line exempt
    string line = "";
    getline(file, line);
    line = "";

    while(getline(file, line))
    {
        //vars
        int bookID;
        string otherFields;
        string transferString;

        stringstream inputString(line);

        //bookID saved
        getline(inputString, transferString, ',');
        bookID = atoi(transferString.c_str());
        //un-needed fields for comparison
        getline(inputString, otherFields, '\n');

        bookIDList.push_back(bookID);
    }//end while
    file.close();
    return bookIDList;
}//end readBookList

void updateBookTagsList(string filename, vector<int> bookIDList)
{
    ifstream file;
    file.open(filename);

    string newFilename = "new" + filename;
    ofstream newFile(newFilename);

    //header line exempt
    string line = "";
    getline(file,line);
    line = "";

    while(getline(file, line))
    {
        //vars
        int bookID;
        string otherFields;
        string transferString;

        stringstream inputString(line);

        //bookID saved
        getline(inputString, transferString, ',');
        bookID = atoi(transferString.c_str());
        //un-needed fields for comparison
        getline(inputString, otherFields, '\n');

        if(binary_search(bookIDList.begin(), bookIDList.end(), bookID))
        {
            newFile << line << "\n";
        }
    }//end while
    file.close();
    newFile.close();
}//end updateBookTagsList

void updateTagsList(string filename, string updatedBookTagsList)
{
    ifstream bookTagsFile;
    bookTagsFile.open(updatedBookTagsList);

    vector<int> usedTagsList;

    string line = "";

    while(getline(bookTagsFile, line))
    {
        //vars
        int bookID;
        int tagID;
        int count;
        string transferString;

        stringstream inputString(line);

        //get bookID
        getline(inputString, transferString, ',');
        bookID = atoi(transferString.c_str());
        transferString = "";
        //get tagID
        getline(inputString, transferString, ',');
        tagID = atoi(transferString.c_str());
        transferString = "";
         //get count
        getline(inputString, transferString, '\n');
        count = atoi(transferString.c_str());
        transferString = "";

        usedTagsList.push_back(tagID);
    }//end while

    sort(usedTagsList.begin(), usedTagsList.end());
    bookTagsFile.close();


    ifstream file;
    file.open(filename);

    string newFilename = "new" + filename;
    ofstream newFile(newFilename);

    //header line exempt
    line = "";
    getline(file,line);
    line = "";

    while(getline(file, line))
    {
        //vars
        int tagID;
        string tagName;
        string transferString;

        stringstream inputString(line);

        //get tagID
        getline(inputString, transferString, ',');
        tagID = atoi(transferString.c_str());
        //get tagName
        getline(inputString, tagName, '\n');

        if(binary_search(usedTagsList.begin(),usedTagsList.end(),tagID))
            newFile << line << "\n";
    }//end while
    file.close();
    newFile.close();
}//end updateBookTagsList

int main()
{
    string bookListFilename = "GoodReads150.csv";
    vector<int> bookIDList = readBookList(bookListFilename);

    //sort vector for faster search
    sort(bookIDList.begin(), bookIDList.end());

    string bookTagsFilename = "book_tags.csv";
    updateBookTagsList(bookTagsFilename, bookIDList);
    string updatedBookTagsFilename = "new" + bookTagsFilename;

    string tagsFilename = "tags.csv";
    updateTagsList(tagsFilename, updatedBookTagsFilename);

}//end main