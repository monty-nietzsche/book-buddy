# BOOKBUDDY - Sales platform for old books

*Bookbuddy*is an online platform (market) for sales of good old books. Its main features are:
- Visitors can browse the books advertised on the platform by category and by language.
- Logged-in users can add, edit and delete books.
- Logged-in users can add, edit and delete packages. A package is a collection of books to be sold all together at a single price.
- To add a book, a user needs the ISBN of the book, the suggest price and the condition of the book (torn, new, etc.). The details of the book are fetched using Google Books API.
- Two restrictions: [1] No user can advertise two books with the same ISBN [2] A package must contain at least two books.
- An empty package or a package with one book are automatically deleted.
- BookBuddy automatically creates two dummy users: 'Jacob Svensson' and 'John Smith'. Users can login as any of these dummy users to test the different functionalities of the BookBuddy platform.
- In the current version of BookBuddy, users can only use google third-party sign-in utility.
- Bookbuddy is written in Python and uses sqlalachemy orm to interact with SQLite database. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Before running the code, please make sure that the following programs are installed on your machine:
- Vagrant
- VirtualBox
- Git Bash

If you do not have them already installed on your machine, please download them here: 

[Download Vagrant](https://www.vagrantup.com/downloads.html) | [Download VirtualBox](https://www.virtualbox.org/wiki/Downloads) | [Download Git Bash](https://github.com/git-for-windows/git/releases/download/v2.13.3.windows.1/Git-2.13.3-64-bit.exe)

### Installing

Once all requirements are met, proceed with the following steps:

1. _Create bookbuddy folder_ : Create a folder called `bookbuddy` in the location of your preference. For illustration purposes, assume you create the `bookbuddy` report under the root folder `c:\`. 

2. _Download installation files_ : Download [installation.zip](https://github.com/monty-nietzsche/log-analysis-reporting/raw/master/files/installation.zip) and unzip its contents in the bookbuddy folder. The `installation.zip` contains two folders `templates` and `static` as well as six files `Vagrantfile`, `client_secrets.json`,`functions.py`, `database_setup.py`, `database_fill.py` and `application.py`. Before proceeding, make sure that your bookbuddy folder contains all of the above. To check this, `cd` to the bookbuddy folder and type `ls`.

![alt text][screen1]

3. _Setup virtual machine_: On Git Bash (if you are a Windows user) or your default terminal, `cd` to the bookbuddy folder and type `vagrant up`. Wait until the virtual machine is set up, it can take few minutes.

![alt text][screen2]

4. _Connect to the virtual machine_ : Type `vagrant ssh` to connect to the virtual machine. 

![alt text][screen3]

5. _Access bookbuddy folder_ : Type `cd /vagrant` which brings you to the bookbuddy folder. 

![alt text][screen4]

6. _Setup and fill data into database_:
To set up the database, type `python database_setup.py`. Once the script has been executed, type `python database_fill.py`. This script will fill the database with sample date
# BOOKBUDDY - Sales platform for old books
<p align="left">
  <img src="https://github.com/monty-nietzsche/bookbuddy/blob/master/images/0.jpg">
</p>

**BOOKBUDDY** is an online platform (market) for sales of good old books. Its main features are:
- Visitors can browse the books advertised on the platform by category and by language.
- Logged-in users can add, edit and delete books.
- Logged-in users can add, edit and delete packages. A package is a collection of books to be sold all together at a single price.
- To add a book, a user needs the ISBN of the book, the suggested price and the condition of the book (torn, new, etc.). The details of the book are fetched using Google Books API.
- Two restrictions: [1] No user can advertise two books with the same ISBN [2] A package must contain at least two books.
- An empty package or a package with one book are automatically deleted.
- BookBuddy automatically creates two dummy users: 'Jacob Svensson' and 'John Smith'. Users can login as any of these dummy users to test the different functionalities of the BookBuddy platform.
- In the current version of BookBuddy, users can only use google third-party sign-in utility.
- Bookbuddy is written in Python and uses sqlalachemy orm to interact with SQLite database. 
- It provides API endpoints where users can get a list in json format of all books, all packages as well as books per category.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

Before running the code, please make sure that the following programs are installed on your machine:
- Vagrant
- VirtualBox
- Git Bash

If you do not have them already installed on your machine, please download them here: 

[Download Vagrant](https://www.vagrantup.com/downloads.html) | [Download VirtualBox](https://www.virtualbox.org/wiki/Downloads) | [Download Git Bash](https://github.com/git-for-windows/git/releases/download/v2.13.3.windows.1/Git-2.13.3-64-bit.exe)

### Installing

Once all requirements are met, proceed with the following steps:

1. _Create bookbuddy folder_ : Create a folder called `bookbuddy` in the location of your preference. For illustration purposes, assume you create the `bookbuddy` report under the root folder `c:\`. 

2. _Download installation files_ : Download [installation.zip](https://github.com/monty-nietzsche/bookbuddy/blob/master/files/installation.zip) and unzip its contents in the bookbuddy folder. The `installation.zip` contains two folders `templates` and `static` as well as six files `Vagrantfile`, `client_secrets.json`,`functions.py`, `database_setup.py`, `database_fill.py` and `application.py`. Before proceeding, make sure that your bookbuddy folder contains all of the above. To check this, `cd` to the bookbuddy folder and type `ls`.
<p align="center">
  <img src="https://github.com/monty-nietzsche/bookbuddy/blob/master/images/1.jpg">
</p>

3. _Setup virtual machine_: On Git Bash (if you are a Windows user) or your default terminal, `cd` to the bookbuddy folder and type `vagrant up`. Wait until the virtual machine is set up, it can take few minutes.

<p align="center">
  <img src="https://github.com/monty-nietzsche/bookbuddy/blob/master/images/2.jpg">
</p>

4. _Connect to the virtual machine_ : Type `vagrant ssh` to connect to the virtual machine. 

<p align="center">
  <img src="https://github.com/monty-nietzsche/bookbuddy/blob/master/images/3.jpg">
</p>

5. _Access bookbuddy folder_ : Type `cd /vagrant` which brings you to the bookbuddy folder. 

<p align="center">
  <img src="https://github.com/monty-nietzsche/bookbuddy/blob/master/images/4.jpg">
</p>

6. _Setup database and fill it with sample data_:
To set up the database and fill it with sample data, type `python database_fill.py`. 

<p align="center">
  <img src="https://github.com/monty-nietzsche/bookbuddy/blob/master/images/6.jpg">
</p>

7. _Run the application_: 
Type `python application.py`

<p align="center">
  <img src="https://github.com/monty-nietzsche/bookbuddy/blob/master/images/7.jpg">
</p>

8. _Use the application_ : 
Open your favorite web browser and type `http://localhost:8000/` in the address bar to use bookbuddy.

<p align="center">
  <img src="https://github.com/monty-nietzsche/bookbuddy/blob/master/images/8.jpg">
</p>

## Running the tests

The functionalities to be tested are:

- Browse the books per category and per language
- Login using a dummy user `Jacob Svensson`or `John Smith`
- Login using Google Sign-In Utility
- Add a book / Edit a book / Delete a book
- Add a package / Edit a package / Delete a package
- API end points:
  - Get all books in json format
  ```/books/json/```
  - Get all packages in json format
  ```/packages/json/```
  - Get all books per category
    ```/category/<int:category_id>/books/json/```
  

### Author

Montasser Ghachem | Udacity Full Stack Nanodegree 2018

![alt text][screen5]

7. _Run the application_: Type `python application.py`

![alt text][screen6]

8. _Use the application_ : Open your favorite web browser and type `http://localhost:8000/` to use bookbuddy.

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc





# bookbuddy


## Requirements
Before running the code, please make sure that the following programs are installed on your machine:
- Vagrant
- VirtualBox
- Git Bash

If you do not have them already installed on your machine, please download them here: 

[Download Vagrant](https://www.vagrantup.com/downloads.html) | [Download VirtualBox](https://www.virtualbox.org/wiki/Downloads) | [Download Git Bash](https://github.com/git-for-windows/git/releases/download/v2.13.3.windows.1/Git-2.13.3-64-bit.exe)

## Installation and Running



The pupose of this project is to create a plain-text reporting tool about the user activity and preferences on a newspaper website. The backend database `news` stores information about articles, authors and site visitors' activity in three tables: _authors_, _articles_ and _log_. The table _authors_ stores a name and a short bio of every author. The table _articles_ stores articles' title and body text as well as creation date and slug. Finally, The table _log_ records details about the different requests directed at the newspaper site namely the landing page and requests' HTTP status code. The structure of the database is as follows:

![alt text][diagram]

While _articles.author_ is foreign key in table _articles_ referencing _authors_id_; _log.path_ is not a foreign key. It is, however, closely related to _articles.slug_ since the path to an article having a slug `bad-things-gone` is `/article/bag-things-gone`. These two relationships enable us to combine data cross tables (join operations) and therefore allow answering a fairly large set of questions. However, we want to focus in this project on answering three questions:
- Which articles are most popular i.e. most viewed?
- Which authors are most popular?
- Which days have had an error rate of more than 1%? The error rate is defined as the ratio between erronous requests and total requests. The erronous requests are the requests whose status code is not `200 OK`.

The Python script (`report.py`) uses `psycopg2`to query a mock PostgreSQL database and produces a report that answers these questions. [See a preview of the report](#report-preview)




## Structure of the Python script(report.py)
The script consists of four major parts:
- Importing psycopg2: `import psycopg2` 
- Declaring and initializing parameters: `DBNAME, TOP, THRESHOLD, ETOP`
- Extracting data from the database through 3 functions: [1] `Popular_articles()` [2] `Popular_authors()` [3] `Error_days()`
- Printing the report: `Print_report()`

## Parameters of the Python script(report.py)

- `TOP`: The number of popular articles that the user would like to show in the report. If `TOP=4`, the report show the 4 most popular articles of all time. The default value is 3.
- `THRESHOLD`: This is the error rate threshold. The report shows the days that have an error rate (errors/requests) higher than this threshold. For instance, if `THRESHOLD=2`, then the report will show all days that have an error rate higher than 2%. The default value is `THRESHOLD=1`.
- `ETOP`: This parameter specify the maximum number of days shown in the report. In case the threshold is very low (take `0.01%` for example), the report might contain a large number of days having an error rate higher than this threshold. `ETOP` limits the number of the days shown in the report. If `THRESHOLD=0.5` and `ETOP=3`, the report shows the top three days with error rates higher than 0.5%. The default value is `ETOP=3`.

## Data functions
- `Popular_articles (TOP)`

    This function takes as argument the parameter `TOP (=3)` to return the list of the most popular articles and their number of views.     The list has at most TOP rows. The function calls DB-API, executes the following `SQL`query, and returns the result.

    ```sql
    select a.title, b.views from
     (select title, slug from articles) a 
     left join 
      (select path, count(*) as views from log where status LIKE '2%' and path!='/' group by path order by views desc) b
    on concat('/article/',a.slug)=b.path
  limit 3;"
    ``` 
    The number of views is obtained from the table _log_ and is equal to all successful requests i.e. where `status=2xx`. Joining the     table _articles_ and the table _log_ is done through linking _articles.slug_ to _log.path_.

- `Popular_authors()`

  The function takes no argument and returns the list of the most popular authors and their number of views. The function calls DB-API,   executes the following `SQL`query, and returns the result.
  
  ```sql
  select c.name, sum(b.views) as total_views
  from 
    (select name, id from authors) c
    left join 
      (select author, title, slug from articles) a
      left join 
      (select path, count(*) as views from log where status LIKE '2%' and path!='/' group by path order by views desc) b
      on concat('/article/',a.slug)=b.path
    on a.author=c.id group by c.name 
  order by total_views desc; 
  ``` 
  The number of views for each other is obtained by summing the views of all articles he has written. Joining the tables _articles_ and    _log_ is done through linking _articles.slug_ and _log.path_. Joining _authors_ and _articles_ is done through  _articles.author_ referencing _authors.id_. 

- `Error_days(THRESHOLD, ETOP)`

  The function takes two arguments `THRESHOLD` and `ETOP` and returns the list of all days in which the ratio of failed requests to total requests (error rate) is higher that `THRESHOLD`. The list returned cannot have a length higher than `ETOP`. The function calls DB-API, executes the following `SQL`query, and returns the result. Here `THRESHOLD=1`and `ETOP=3`.
  
  ```sql
  select a.day, a.requests, b.errors, b.errors*1./a.requests as error_rate
  from 
    (select date(time) as day, count(*) as requests from log group by day) a
    left join 
    (select date(time) as day, count(*) as errors from log where status NOT LIKE (%s) group by day) b
    on a.day=b.day 
  where b.errors*1./a.requests>0.01 
  order by error_rate desc 
  limit 3"
  ``` 
  The number of requests per day is obtained from the table _log_ by grouping entries per day. The number of errors per day is the number of requests where `status!=2xx`. For each single day, dividing _errors_ by _requests_ gives the daily error rate `error_rate`. The days are then sorted by decreasing error rates. Finally, the first `ETOP` days with `rate>THRESHOLD` are selected and returned by the function.

## Report preview
```text
--------------------------------------- ----------------------------------------
------------------- Log Analysis Report By Montasser Ghachem -------------------
--------------------------------------- ----------------------------------------


The 3 most popular articles of all time:
 + Candidate is jerk, alleges rival - 338647 views
 + Bears love berries, alleges bear - 253801 views
 + Bad things gone, say good people - 170098 views


The most popular article authors of all time:
 + Ursula La Multa - 507594 views
 + Rudolf von Treppenwitz - 423457 views
 + Anonymous Contributor - 170098 views
 + Markoff Chaney - 84557 views


Days with 1 % or more failed requests:
 + Jul 17, 2016 - 2.3%  errs
  (1265 out of 55907 requests failed)


--------------------------------- End of Report---------------------------------
```
[diagram]:https://github.com/monty-nietzsche/log-analysis-reporting/raw/master/files/diagram.jpg "database diagram"
[screen1]:https://github.com/monty-nietzsche/log-analysis-reporting/raw/master/files/screen1.jpg "list files in report folder"
[screen2]:https://github.com/monty-nietzsche/log-analysis-reporting/raw/master/files/screen2.jpg "setup the virtual machine"
[screen3]:https://github.com/monty-nietzsche/log-analysis-reporting/raw/master/files/screen3.jpg "connect to the virtual machine"
[screen4]:https://github.com/monty-nietzsche/log-analysis-reporting/raw/master/files/screen4.jpg "`cd` to the report folder"
[screen5]:https://github.com/monty-nietzsche/log-analysis-reporting/raw/master/files/screen5.jpg "load data into the news database"
[screen6]:https://github.com/monty-nietzsche/log-analysis-reporting/raw/master/files/screen6.jpg "run the Python script"
