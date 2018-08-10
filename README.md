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
