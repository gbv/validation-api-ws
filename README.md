# Validation API (demo)

[![Docker image](https://github.com/gbv/validation-api-ws/actions/workflows/docker.yml/badge.svg)](https://github.com/orgs/gbv/packages/container/package/validation-api-ws)
[![Test](https://github.com/gbv/validation-api-ws/actions/workflows/test.yml/badge.svg)](https://github.com/gbv/validation-api-ws/actions/workflows/test.yml)

> Demo of a simple Web API to validate data against predefined criteria

This web service implements a **[Data Validation API](#API)** being specified as part of project AQinDA. The API helps allows to check data against defined application profiles and to integrate such checks into data processing workflows. The API is not meant to define quality criteria of application profiles.

## Table of Contents

- [Installation](#installation)
  - [From sources](#from-sources)
  - [With Docker](#with-docker)
- [Configuration](#configuration)
  - [Service settings](#service-settings)
  - [Profiles](#profiles)
  - [Checks](#checks)
- [API](#api)
  - [GET /profiles](#get-profiles)
  - [GET /{profile}/validate](#get-profilevalidate)
  - [POST /{profile}/validate](#get-profilevalidate)
- [Maintainers](#maintainers)
- [Contributing](#contributing)
- [License](#license)

## Installation

The web application is started on <http://localhost:7007> by default.

### From sources

Requires basic development toolchain (`sudo apt install build-essential`) and Python 3 with module venv to be installed.

1. clone repository: `git clone https://github.com/gbv/validation-api-ws.git && cd validation-api-ws`
2. run `make deps` to install dependencies
3. optionally [Configure](#configuration) the instance
3. `make start` 

### Via Docker

A Docker image is automatically build [and published](https://github.com/orgs/gbv/packages/container/package/validation-api-ws) on GitHub. To run a one-shot instance of the application from the most recent Docker image:

~~~sh
docker run --rm -p 7007:7007 ghcr.io/gbv/validation-api-ws:main
~~~

A [configuration](#configuration) directory or file must exist and be mounted:

~~~sh
test -f data/config.json && docker run --rm -p 7007:7007 --volume config:/app/config ghcr.io/gbv/validation-api-ws:main
test -f config.json && docker run --rm -p 7007:7007 --volume ./config.json:/app/config.json ghcr.io/gbv/validation-api-ws:main
~~~

## Configuration

The [default configuration](config.default.json) contains some base formats. To defined application profiles to be checked against, create a configuration file in JSON format at `config.json` in the current directory or in the local subdirectory `config`. It is also possible to pass the location of config file or directory with argument `--config` at startup. The configuration file must contain field `profiles` with a list of [profile objects](#profiles) and it can contain additional service settings.

### Service settings

- `title` (title of the webservice) is set to "Validation Service" by default.
- `port` (numeric port to run the webservice) is set to 7007 by default.
- `stage` (stage directory for data files at the server) is set to `false` (disabled) by default.
- `reports` (reports directory to store reports in) is set to `false` (disabled) by default.
- `downloads` (cache directory for data retrieved via URL) is set to `false` (disabled) by default.

### Profiles

Each application profile is configured with a JSON object having a unique `id`, a list of `checks`, and additional metadata. See [profiles configuration JSON Schema](lib/validate/profiles-schema.json) for details.

### Checks

Each check is either a string, referencing another profile or a base format, or a JSON object for a more complex check.

### Base formats

- `json` - validate JSON syntax
- `xml` - validate XML syntax (document must be well-formed XML)

### Schema checks

A check with two fields:

- `language` - schema language: `jsonschema` (JSON Schema) or `xsd` (XML Schema)
- `schema` - schema file or ULR

## API

The webservice provides one endpoint to [list application profiles](#get-profiles) and one **Data Validation API** endpoint for each profile to validate data.

Details of Data Validation API are still being specified, so details may change. The core response format is being specified as **[Data Validation Error Format]**.

### GET /profiles

Return a list of application profiles configured at this instance of the validation service. The information is a subset of [profiles configuration](#profiles) limited to the public fields `id` (required), `title`, `description`, and `url`. Internal information about checks is not included.

### GET /{profile}/validate

Validate data against an application profile and return a list of errors in [Data Validation Error Format]. Data must be passed via one of these query parameters:

- `data` as string
- `url` to be downloaded from an URL (if the service is configured with `downloads` directory)
- `file` to be read from a local file in the stage directory of the server (if the service is configured with `stage` directory)

Status code is always 200 if validation could be executed, no matter whether errors have been found or not. For example validating the string `[1,2` at default profile `json` results in the following validation response. The error position (after the fourth character on line 1) is referenced with multiple dimensions. Dimension values are always strings.

~~~sh
curl http://localhost:7007/json/validate -d '[1,2'
~~~

~~~json
[
  {
    "message": "Expecting ',' delimiter",
    "position": {
      "line": "1",
      "linecol": "1:5",
      "offset": "4"
    }
  }
]
~~~

### POST /{profile}/validate

The validation endpoint can also be queried via HTTP POST: data can be passed as request body or as file upload (content type `multipart/form-data`). Additional query parameters are not supported.

### GET /reports/{id}

Return a validation report. *This endpoint has not been specified nor implemented yet.*

### DELETE /reports/{id}

Delete a validation report. *This endpoint has not been specified nor implemented yet.*

## Maintainers

- [@nichtich](https://github.com/nichtich)

## Contributing

- `make deps` installs Python dependencies in a virtual environment in directory `.venv`. You may want to call `. .venv/bin/activate` to active the environment.
- `make test` runs unit tests
- `make all` runs unit tests and integration test. Also puts coverage report into directory `htmlcov`
- `make lint` checks coding style
- `make fix` cleans up some coding style violations

To locally build and run the image Docker for testing:

~~~sh
docker image build -t validator .
docker run --rm -p 7007:7007 validator  # default config, or:
test -f config.json && docker run --rm -p 7007:7007 --volume ./config.json:/app/config.json validator
~~~

See also <https://github.com/gbv/validation-server> for a previous implementation in NodeJS. Both implementations may converge

## License

MIT © 2025- Verbundzentrale des GBV (VZG)

This work has been [funded by DFG in project *AQinDa*](https://gepris.dfg.de/gepris/projekt/521659096)

[Data Validation Error Format]: https://gbv.github.io/validation-error-format/
