# python-project-template
This is a template for ML application projects

## Table of Contents

- [Tech we use](#tech-we-use)
- [Get started](#get-started)
- [Usage](#usage)

## Tech we use
- API modularization: PyNest
- API: FastAPI
- Frontend Framework: Streamlit
- Storage: Atlas MongoDB

## Get started

1. Create venv.
    ```bash
    python3.12 -m venv .venv
    ```

2. Source venv

    Using Windows:
    ```bash
    .venv/Scripts/activate
    ```

    Using macOS and Linux:
    ```bash
    source .venv/bin/activate
    ```

3. Install the dependencies.
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

## Usage

1. Run the application.

    Run frontend.
    ```bash
    streamlit run src.streamlit_app.py
    ```

    Run backend Swagger UI using uvicorn.
    ```bash
    uvicorn "app:app" --host "0.0.0.0" --port "80" --reload
    ```
    To send requests: Go to the fastapi docs and use your api endpoints - http://127.0.0.1/docs