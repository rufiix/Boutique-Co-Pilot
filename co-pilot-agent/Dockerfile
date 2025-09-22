# Krok 1: Wybierz oficjalny, lekki obraz Pythona jako bazę
FROM python:3.11-slim

# Krok 2: Ustaw katalog roboczy wewnątrz kontenera
WORKDIR /app

# Krok 3: Skopiuj i zainstaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Krok 4: Skopiuj kod źródłowy naszej aplikacji
COPY main.py .

# Krok 5: Ustaw domyślne zmienne środowiskowe
ENV GCP_REGION=europe-west1

# Krok 6: Zdefiniuj komendę, która uruchomi aplikację
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]