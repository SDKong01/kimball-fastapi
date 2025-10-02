FROM python:3.11-bullseye

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Environment variables for the application
ENV PYTHONPATH=.
ENV DEBUG=False
ENV GENERAL_DB_NAME=813dcf27-3de3-4c07-bfb0-140977739ee8
ENV GENERAL_DB_URL=mongodb+srv://generic-user:pZJ0t5nQPwkOJ7BK@dev.kj6fy.mongodb.net/
ENV MONGO_HOST=dev.kj6fy.mongodb.net
ENV MONGO_PORT=27017
ENV MONGO_DB=kimball
ENV MONGO_USER=generic-user
ENV MONGO_PASS=pZJ0t5nQPwkOJ7BK
ENV MONGO_IS_ATLAS_CLUSTER=True
ENV REDIS_HOST=localhost
ENV REDIS_PORT=6379
ENV REDIS_PASS=
ENV REDIS_DB=0
ENV CLICKHOUSE_HOST=3.150.3.160
ENV CLICKHOUSE_PORT=8123
ENV CLICKHOUSE_USER=default
ENV CLICKHOUSE_PASSWORD=Kainam2023
ENV CLICKHOUSE_DB=default
ENV AIRFLOW_URL=http://3.144.122.44:8088
ENV AIRFLOW_USER=kainam
ENV AIRFLOW_PASSWORD=Kainam2023
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV ALLOWED_ORIGINS=*

RUN pip install --no-cache-dir -r requirements/requirements.txt
RUN pip install langchain-google-genai==1.0.8

# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app.main:app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]