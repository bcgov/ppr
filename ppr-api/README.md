# Application Name

BC Registries PPR API

## Background


## Technology Stack Used
* Python, Flask, GCP Cloud Storage
* Postgres -  SQLAlchemy, psycopg2-binary

## Third-Party Products/Libraries used and the the License they are covert by

## Project Status

## Documnentation

GitHub Pages (https://guides.github.com/features/pages/) are a neat way to document you application/project.

## Security

## Files in this repository

## Environment Variables
Copy '.env.sample' to '.env' and replace the values

### Development Setup
Run `poetry install`

Run `poetry shell`

See the src/database README for the database instance set up.

To load/reload unit test data run python manage.py create_test_data

### Bump version
Run `poetry version (patch, minor, major, prepatch, preminor, premajor, prerelease)`

### Running the db migration
If modifying the database definition run `poetry run flask db migrate -m "xxx"`
Note: PPR API and MHR API share the same database so the migration scripts need to be synchronized. 
Run `poetry run flask db upgrade`
Run `poetry run flask db downgrade`

### Running the Doc-API
Run `poetry run flask run`

### Running Linting
Run `poetry run isort . --check`
Run `poetry run black . --check`
Run `poetry run pylint src`
Run `poetry run flake8 src`

### Running Unit Tests
- For all tests run `poetry run pytest -v -s`
- For an individual file run `poetry run pytest -v -s ./tests/unit/api/filename.py`
- For an individual test case run `poetry run pytest -v -s ./tests/unit/api/filename.py::test-case-name`

## Deployment

See https://github.com/bcgov/bcregistry-sre/blob/main/.github/workflows/doc-api-cd-gcp.yaml

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