# Final Project

![App CI/CD](https://github.com/software-students-spring2025/5-final-fizzbuzz/actions/workflows/frontend-ci.yml/badge.svg)
![Database CI/CD](https://github.com/software-students-spring2025/5-final-fizzbuzz/actions/workflows/database-ci.yml/badge.svg)
![Deploy Status](https://github.com/software-students-spring2025/5-final-fizzbuzz/actions/workflows/deploy.yml/badge.svg)

# Student Finance Tracker
## Overview 
Student Finance Tracker is a containerized web application designed to help students manage and track their personal finances. Users can log their spending across categories (transportation, books, food, etc) in interactive charts that visualize their spending habits over time. The objective of this project is to encourage financial literacy and provide students with a simple tool to budget and analyze their expenses.


## Team 
- [Aaqila Patel](https://github.com/aaqilap)

- [Isha Gopal](https://github.com/ishy04)

- [Chris Leu](https://github.com/cl3880)

- [Cyryl Zhang](https://github.com/nstraightbeam)

## System Architecture 
The system consists of three main components:
1. **Web Application**: Built with Flask, providing user authentication, expense tracking, and data visualization.
2. **MongoDB Database**: Stores user accounts, transactions, categories, and budgets.
3. **DockerHub and Docker Compose Setup**: Uses Docker Compose to run everything, and DockerHub to store data for the app and database, keeping deployment much faster. 

## Docker Images
Our containerized applications are available on Docker Hub:
- Frontend Application: [finance-tracker-frontend](https://hub.docker.com/repository/docker/cl3880/finance-tracker-frontend/general)
- Backend Database: [finance-tracker-backend](https://hub.docker.com/repository/docker/cl3880/finance-tracker-backend/general)

## Setup Instructions
Follow these steps to get your development environment up and running:

### 1. Install Python 3.8 (using `pyenv` if needed)

### 2. Setup pipenv with Python 3.8  
Ensure that pipenv is using Python 3.8. If it is not, reinitialize it: 

```bash
pipenv --rm
pipenv --python 3.8
pipenv --py  # This will show a Python 3.8 path
```

We can verify that it works by running: 
```bash
pipenv --py # This will show a Python 3.8 path 
```

### 3. Navigate to the root project directory 
```bash
cd path-to-5-final-fizzbuzz
``` 

### 4. Install Dependencies from Pipfile
```bash
pipenv install
```

### 5. Activate the Pipenv Shell 
```bash
pipenv shell
```

### 6. Run the Project with Docker Compose 
```bash
docker compose up --build
```

### 7. Access the Application 
Once the Docker build is complete, open your browser and go to: 
http://localhost:8000


## MongoDB Setup
MongoDB is automatically started by Docker Compose. Database details:
- Database Name: finance_tracker<br>
- Collection: users, transactions, categories, budgets<br>
- Port: 27017

### Database Initialization
The database is automatically initialized with default categories when the application starts. The initialization script (`database/init_db.py`) performs the following tasks:
- Creates necessary indexes for better query performance
- Loads default expense/income categories

If you need to manually initialize the database, you can run:
```bash
cd database
python init_db.py
```

## Environment Configuration
Create a '.env' file at the project root as these variables are required for the application to connect to MongoDB and manage session security. 
Example: 
```bash
MONGO_URI=mongodb://localhost:27017/finance_tracker
FLASK_SECRET_KEY=your_secret_key
```

## Development Workflow
1. Create a feature branch for your changes
2. Make your changes and commit them
3. Create a pull request
4. Get code review from at least one team member
5. Merge after approval

## Testing
All unit tests must pass before merging any changes:
```bash
# Run backend tests.  
cd app
pytest --cov=app tests/ --cov-report=term-missing --cov-fail-under=80

# Run database tests
cd database
pytest --cov=database tests/ --cov-report=term-missing --cov-fail-under=80
```