LOAD DATA LOCAL INFILE 'C:/Users/tbuch/OneDrive/Desktop/School/Year 4 - Senior/Spring 2022/CS 411W/Workspace/Spring22-AskMissy/mySQL Scripts/tags.csv'
INTO TABLE tags
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(tag_id, tag_name);