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

## Development guidelines

### Tests

- Every module must include unit tests
- Tests should consider success and failure scenarios
- During the first development phase, code coverage should be at least of 80% per module, it should eventually be expanded to 100%

### Architecture

- Apps should be isolated
  - Each layer can only include direct calls to functions in lower layers (Interface > Application > Domain > Infrastructure)
  - The application layer is the main point of integration of domain APIs
  - Interactions should be modelled as API/function calls.
  - Avoid direct calls from one domain module to another.
  - When modules depend on each other directly use dependency inversion.


## License

This project is licensed under the [Proprietary Software](LICENSE).