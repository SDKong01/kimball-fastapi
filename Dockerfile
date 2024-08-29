FROM python:3.11-bullseye

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install --no-cache-dir -r requirements/requirements.txt
RUN pip install langchain-google-genai==1.0.8

# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app.main:app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--reload", "--log-level", "info"]