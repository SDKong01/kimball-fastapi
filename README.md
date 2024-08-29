# Kimball Backend
This is the FastAPI API Layer for the Kimball application modularized with PyNest.

## Table of Contents

- [Tech we use](#tech-we-use)
- [Get started](#get-started)
- [Usage](#usage)
- [Send requests](#sendrequests)
- [License](#license)

## Tech we use
- Cloud microservice: Cloud Run
- API modularization: PyNest
- API: FastAPI
- Storage: Atlas MongoDB

## Get started

1. Create venv.
    ```bash
    python3.12 -m venv myenv
    ```

2. Source venv.

    Using Windows:
    ```bash
    myenv\Scripts\activate
    ```

    Using macOS and Linux:
    ```bash
    source myenv/bin/activate
    ```

3. Install the dependencies.
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

## Usage

1. Run the application.

    Run service using main module.
    ```bash
    python main.py
    ```

    Run service using uvicorn.
    ```bash
    uvicorn "app:app" --host "0.0.0.0" --port "80" --reload
    ```

    Run service on Docker.
    ```bash
    docker build -t ezml-api .
    docker run -p 80:80 ezml-api
    ```

## Send requests

Go to the fastapi docs and use your api endpoints - http://127.0.0.1/docs

## License

This project is licensed under the [Proprietary Software](LICENSE).