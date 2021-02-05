# Application Name

BC Registries Personal Property Registry API

## Background
For API usage documentation see [PPR API](https://yfthig-test.web.app/ppr-api) 
For BC Registries Gateway API configuration see [Gateway PPR Proxy](https://github.com/bcregistry/apigw/blob/master/proxy/README-ppr.md)

## Technology Stack Used
* Python, Flask
* Postgres -  SQLAlchemy, psycopg2-binary & alembic

## Third-Party Products/Libraries used and the the License they are covert by

## Project Status

## Documnentation

GitHub Pages (https://guides.github.com/features/pages/) are a neat way to document you application/project.

## Security


## Files in this repository


## Development Environment
Follow the instructions of the [Development Readme](https://github.com/bcgov/entity/blob/master/docs/development.md)
to setup your local development environment.

### Development Setup
1. Open the ppr-api directory in VS Code to treat it as a project (or WSL projec). To prevent version clashes, set up avirtual environment to install the Python packages used by this project.
1. Run `make setup`
1. Run `pip install .`
1. See [Oracle DB README](./oracle-db/README.md) on running a local Docker Oracle PPR database.
1. Update the .env file to add your local environment variables including the database configuration. A sample .env file is provided.
1. See [test data README](./test_data/README.md) for instructions to set up unit test data.

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

