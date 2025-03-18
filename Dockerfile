# Pobieramy obraz Pythona
FROM python:3.9

# Ustawiamy katalog roboczy
WORKDIR /app

# Kopiujemy pliki do kontenera
COPY requirements.txt requirements.txt
COPY scraper.py scraper.py

# Instalujemy zależności
RUN pip install -r requirements.txt

# Otwieramy port 10000 (Render.com wymaga tego)
EXPOSE 10000

# Uruchamiamy aplikację Flask przez Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:10000", "scraper:app"]
