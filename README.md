# Todo Flask App
- A simple Todo List web application built using Flask and SQLite. It allows users to register, log in, and manage their daily tasks.

## Features
- User registration and login system  
- Add new tasks  
- Edit existing tasks  
- Delete tasks  
- Mark tasks as done or undone  
- Filter tasks (All, Active, Done)  
- Session-based authentication  
- Dark mode support

## Tech Stack
- Flask (Python)  
- SQLite (Database)  
- HTML  
- CSS  

## Project Structure
- app.py
- db/
  - database.db
- templates/
  - login.html
  - register.html
  - home.html
  - edit.html
  - about.html
- static/
  - css/

## How to Run
- To run the application, first make sure Python is installed on your system. Install Flask by running `pip install flask` in your terminal. After installing the required dependency, start the application by running `python app.py`. Once the server is running, open your browser and go to `http://localhost:5000` to access the web app.
