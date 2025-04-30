FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Créez le dossier model s'il n'existe pas
RUN mkdir -p /app/model

# Copiez le modèle CatBoost
COPY model/catboost_model.cbm /app/model/

# Expose the port
EXPOSE 8000

# Set the entrypoint
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]