# Application Name

BC Registries Manufactured Home Registry API

## Background

## Technology Stack Used
* Python, Flask
* Postgres -  SQLAlchemy, psycopg2-binary & alembic

## Third-Party Products/Libraries used and the the License they are covert by

## Project Status

## Documnentation

GitHub Pages (https://guides.github.com/features/pages/) are a neat way to document you application/project.

## Security


## Files in this repository

## Environment Variables
The set of environment variables used by this API includes:

| Variable Name | Description |
|---------------|-------------|

## Development Environment
Follow the instructions of the [Development Readme](https://github.com/bcgov/entity/blob/master/docs/development.md)
to setup your local development environment.

### Mock pay-api environment variable.
To use the mock pay-api service for local testing, set the .env variable:
   PAYMENT_SVC_URL="https://bcregistry-bcregistry-mock.apigee.net/pay/api/v1"

### Development Setup
1. Open the mhr-api directory in VS Code to treat it as a project (or WSL projec). To prevent version clashes, set up a virtual environment to install the Python packages used by this project.
1. Run `make setup`
1. Run `pip install .`
1. Update the .env file to add your local environment variables including the database configuration. A sample .env file is provided.
1. Run a local instance of the Postgres PPR database.
    1. From your project root run: `docker-compose up -d`
    1. In your `venv` environment run: `python manage.py db upgrade`


### Running the PPR-API
Start the flask server with `(python -m flask run -p 5000)`

### Running Linting
Run `make pylint`

### Running Unit Tests
- For all tests run `pytest -v -s` 
- For an individual file run `pytest -v -s ./tests/unit/api/filename.py` or `pytest -v -s ./tests/unit/models/filename.py`
- For an individual test case run `pytest -v -s ./tests/unit/api/filename.py::test-case-name`
  
## Deployment (OpenShift)

See (openshift/Readme.md)

## Getting Help or Reporting an Issue

To report bugs/issues/feature requests, please file an [issue](../../issues).

## How to Contribute

If you would like to contribute, please see our [CONTRIBUTING](./CONTRIBUTING.md) guidelines.

Please note that this project is released with a [Contributor Code of Conduct](./CODE_OF_CONDUCT.md).
By participating in this project you agree to abide by its terms.

## License

    Copyright 2021 Province of British Columbia

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

