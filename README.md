# New is always better: A cinema prediction tool

<p align="center">
  <img height="800" alt="Image" src="https://github.com/user-attachments/assets/b54dce82-629c-439e-8635-5f5fdc8637fb" />
</p>

## Project Overview
**New Is Always Better** is a decision-making tool designed for a cinema manager aiming to optimize the selection of films to screen. This cinema follows a unique policy: only screening new releases during their first week, with weekly updates every Wednesday. The cinema has two screening rooms (with capacities of 120 and 80 seats), and the tool's goal is to predict the potential audience for upcoming films to maximize revenue.

---

## Global Architecture

The project is organized into microservices:

- **Prediction API (FastAPI):** Exposes the machine learning model.
- **Web Application (Django):** Provides a user interface for the cinema manager.
- **Transactional Database:** Stores application data (SQLite).
- **Analytical Database:** Stores data for the ML model (Azure Blob Storage).

---

## Directory Structure

The project files are structured as follows:

```
new-is-always-better/
├── api/
│   ├── requirements.txt
├── BDD/
│   ├── analytic_database.db
├── django/
│   ├── azure_blob_getter.py
│   ├── deploy.sh
│   ├── django_readme.md
│   ├── Dockerfile
│   ├── dummy_model_utils.py
│   ├── dummy_pipeline.joblib
│   ├── first_model_preparation.ipynb
│   ├── first_predictor.py
│   ├── manage.py
│   ├── package.json
│   ├── requirements.txt
│   ├── tailwind.config.js
│   ├── test_load_model.ipynb
│   ├── filmprediction/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   ├── films/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── data_importer.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   ├── views.py
│   │   ├── business/
│   │   │   ├── __init__.py
│   │   │   ├── broadcast_utils.py
│   │   │   ├── movie_list_utils.py
│   │   │   ├── prediction_utils.py
│   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_alter_movie_first_week_actual_entries_france.py
│   │   │   ├── 0003_boadcast_remove_movie_room_recette.py
│   │   │   ├── 0004_rename_boadcast_broadcast_recette_broadcast.py
│   │   │   ├── 0005_remove_recette_broadcast_recette_broadcast_id.py
│   │   ├── templates/
│   │   ├── views_fold/
│   ├── static/
│   │   ├── salle_de_cinema_vide.png
│   │   ├── css/
│   ├── templates/
│   │   ├── base.html
├── DOC/
│   ├── Cahier des charges fonctionnels.pdf
├── machine_learning/
│   ├── allocine_analysis.ipynb
│   ├── requirements.txt
├── MLFlow/
│   ├── MLFlow_Readme.md
│   ├── requirements.txt
│   ├── leo_is_there/
│   │   ├── cleaningleo.ipynb
│   │   ├── eda.ipynb
│   │   ├── films_cleaned.csv
│   │   ├── films_nettoyes.csv
│   │   ├── fusion.ipynb
│   │   ├── resultfilm.csv
│   │   ├── modelisations/
│   ├── mlruns/
│   │   ├── 0/
│   │   │   ├── 692666111458774218/
│   ├── nico_is_here/
│   │   ├── blostorage_connection.ipynb
│   │   ├── chat_gpt_sample.ipynb
│   │   ├── in_azure_created_notebook.ipynb
│   │   ├── titanic_data_cleaned.csv
│   ├── wael_is_here/
│   │   ├── ML_firstNB.ipynb
├── movie_prediction_api/
│   ├── Dockerfile
│   ├── README.md
│   ├── requirements.txt
│   ├── test_model.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── preprocessing/
│   │   ├── schema/
│   │   ├── utils/
├── model/
│   ├── catboost_model.cbm
├── scraping/
│   ├── allocinescraper/
│   │   ├── cleaner.ipynb
│   │   ├── create-azure-function.ps1
│   │   ├── deploy_airflow.sh
│   │   ├── deploy_func_app.ps1
│   │   ├── deploy.ps1
│   │   ├── docker-compose.yml
│   │   ├── Dockerfile
│   │   ├── entrypoint.sh
│   │   ├── host.json
│   │   ├── local.settings.json
│   │   ├── profile.ps1
│   │   ├── profile.ps1.bak
│   │   ├── requirements.psd1
│   │   ├── requirements.txt
│   │   ├── run.ps1
│   │   ├── scrapy.cfg
│   │   ├── upload_blob.py
│   │   ├── allocinescraper/
│   │   ├── dags/
│   │   ├── TimerTriggerScraper/
```

This structure provides an overview of the organization of the project files and directories.

---

## Part 1: Prediction API (FastAPI)

This API predicts the audience for films during their first week of release.

### Features

- **Individual Prediction:** Predicts the audience for a single film.
- **Batch Prediction:** Analyzes multiple films simultaneously.
- **Feature Engineering:** Transforms raw film data into usable features.
- **ML Model:** Utilizes CatBoost for accurate predictions.

### Installation

#### Prerequisites
- Python 3.8+
- pip (Python package manager)

#### Installation Steps
```bash
# Clone the repository
git clone https://github.com/your-repo/new-is-always-better.git
cd new-is-always-better/api

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Using the API

#### Start the API
```bash
# In the api/ directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
The API will be accessible at: `http://localhost:8000`

#### API Documentation
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

#### Key Endpoints

1. **Predict for a Single Film**
   - **POST /predict**
   - Example Request:
     ```json
     {
       "film_title": "Avatar 3",
       "release_date": "2025-12-25",
       "duration": "2h 45min",
       "age_classification": "All audiences",
       "producers": "James Cameron, Jon Landau",
       "director": "James Cameron",
       "top_stars": "Sam Worthington, Zoe Saldana",
       "languages": "English",
       "distributor": "20th Century Studios",
       "year_of_production": "2025",
       "film_nationality": "United States",
       "filming_secrets": "15 anecdotes",
       "awards": "",
       "associated_genres": "Science Fiction, Adventure",
       "broadcast_category": "in theaters",
       "trailer_views": "5000000 views",
       "synopsis": "Jake Sully and Neytiri return for another epic adventure on Pandora."
     }
     ```
   - Example Response:
     ```json
     {
       "film_title": "Avatar 3",
       "predicted_fr_entries": 1250000
     }
     ```

2. **Predict for Multiple Films**
   - **POST /predict-batch**
   - Request Body: List of films in JSON format.

#### Prediction Model

- **Algorithm:** CatBoostRegressor, optimized for categorical features.
- **Key Features:**
  - **Film Metadata:** Duration, synopsis (length, sentiment), awards, trailer views, release date.
  - **Production Team:** Director, main actors, producers.
  - **Distribution and Franchise:** Distributor, franchise affiliation, cinematic universe.
  - **Binary Features:** Presence of specific stars, film nationalities, languages, studio type.

#### Deployment with Docker
```bash
# Build the Docker image
docker build -t film-prediction-api .

# Run the container
docker run -d -p 8000:8000 film-prediction-api
```

---

## Part 2: Web Application (Django)

The web application provides a user interface for the cinema manager to visualize predictions, manage screening schedules, and track financial performance.

### Features

- **Dashboard:** Overview of selected and upcoming films.
- **Top Ten:** List of films with the highest predicted audience.
- **Revenue Tracking:** Monitor actual entries and revenue per room and day.
- **Financial Analysis:** Analyze revenue, costs, and profitability.
- **Settings:** Import and update film data.

### Installation

#### Prerequisites
- Python 3.8+
- pip (Python package manager)

#### Installation Steps
```bash
# Navigate to the Django application directory
cd new-is-always-better/django_app

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```
The application will be accessible at: `http://localhost:8000`

### Data Models

1. **Movie:** Stores information about each film.
   - Fields: Title, image URL, synopsis, genre, cast, release date, first-week entries.

2. **PredictionHistory:** Records prediction history for each film.
   - Fields: Film, predicted entries, prediction error, model version, date.

3. **Broadcast:** Represents a week of programming.
   - Fields: Start date, end date, films for each room.

4. **Revenue:** Tracks daily entries and revenue.
   - Fields: Date, ticket price, broadcast ID, films, actual entries, additional revenue.

### Key Views

- **Dashboard:** Displays currently screened and upcoming films with predictions.
- **Top Ten:** Lists the top 10 films with the highest predictions.
- **Revenue:** Interface for tracking and updating daily entries.
- **Financial Analysis:** Weekly revenue, fixed costs, net profit, occupancy rate.
- **Settings:** Import film data via CSV or Azure Blob Storage.

### Deployment with Docker
```bash
# Build the Docker image
docker build -t new-is-always-better-django .

# Run the container
docker run -d -p 8000:8000 new-is-always-better-django
```

---

## Full Project Deployment with Docker Compose

To deploy the entire application (API and Web Interface):
```yaml
version: '3'

services:
  api:
    build: ./api
    ports:
      - "8001:8000"
    volumes:
      - ./api:/app
    environment:
      - MODEL_PATH=/app/model/catboost_model.cbm
    restart: always

  web:
    build: ./django_app
    ports:
      - "8000:8000"
    volumes:
      - ./django_app:/app
    environment:
      - FASTAPI_URL=http://api:8000
      - SECRET_KEY=your_secret_key
      - DEBUG=0
      - ACCOUNT_URL=your_azure_account
      - CONTAINER_NAME=your_container
      - BLOB_NAME=your_blob
    depends_on:
      - api
    restart: always
```

---

## Usage

1. Access the application at `http://localhost:8000`.
2. View the dashboard for currently screened films.
3. Explore the "Top Ten" tab for predictions of upcoming releases.
4. Update actual entries in the "Revenue" tab.
5. Analyze financial performance in the "Financial Analysis" tab.
6. Import new data via the "Settings" tab.

---

## Maintenance and Updates

- **Model Updates:** Regularly update the prediction model.
- **Data Updates:** Use the "Settings" tab to update data manually or via Azure Blob Storage.

---

## About the Project
This project was developed as part of a mission for an IT consulting firm, following the agile SCRUM methodology with a team of four AI developers. It aims to help cinema managers optimize film selection to maximize revenue.

## Authors
- Michael Adebayo ([@MichAdebayo](https://github.com/MichAdebayo))
- Nicolas Cassonne ([@NicoCasso](https://github.com/NicoCasso))
- Wael Bensoltana ([@wbensolt](https://github.com/wbensolt))
- Leo Gallus ([@Leozmee](https://github.com/Leozmee))