# Sensay AI's Core backend Service

## FastAPI nano
This repo is created from the boilerplate FastAPI nano
please refer to this document about how this project 
is structure [a link](./FASTAPINANO_README.md)

## How to add new dependency
First of all, this project's will follow [PEP 505](https://peps.python.org/pep-0508/)
please refer to the link, and we will use Poetry to manage our packaging versioning (You can think it will like Pip with lock version of Nodejs).

Set to install:
1. Install "Poetry" in your local development please follow the guide here [Poetry](https://python-poetry.org/docs/)
2. To add new dependency please add in the [pyproject.toml](./pyproject.toml) file 
   - 2.1.1) If that dependency is essential in the production env please add that in the [tool.poetry.dependencies] section
or you can run the command:
    ```bash
        poetry add black
    ```
   - 2.1.2) If that dependency is only need for development env please add it
in the production env please add that in the [tool.poetry.group.dev.dependencies] section or you can run the command:
    ```bash
        poetry add black -D
    ```

3. Next step

    For the installation in local you can do the following </br>
    Set up a venv in your local like this for example
    ```bash
        python3.11 -m venv .venv
    ```
    and then run
    ```bash
        poetry config virtualenvs.in-project true --local
    ```
       to install core dependencies you run:
    ```shell
    poetry install --no-root 
    ```
    or run this if you don't want the dev dependencies
    ```shell
    poetry install --no-root --no-dev
    ```
    to run the application, test, or make lint you you can do like this
    ```shell
    poetry run pytest
    ```
    ```shell
    poetry run make lint-check
    ```
    ```shell
    poetry run uvicorn app.main:app --port 5000 --reload
    ```