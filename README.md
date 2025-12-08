# Validation API (demo)

[![Docker image](https://github.com/gbv/validation-api-ws/actions/workflows/docker.yml/badge.svg)](https://github.com/orgs/gbv/packages/container/package/validation-api-ws)
[![Test](https://github.com/gbv/validation-api-ws/actions/workflows/test.yml/badge.svg)](https://github.com/gbv/validation-api-ws/actions/workflows/test.yml)

> Demo of a simple Web API to validate data against predefined criteria

This web service implements a **[Data Validation API](#API)** being specified as part of project AQinDA. The API helps allows to check data against defined application profiles and to integrate such checks into data processing workflows. The API is not meant to define quality criteria of application profiles, this is another part of the project.

## Table of Contents

- [Installation](#installation)
  - [From sources](#from-sources)
  - [With Docker](#with-docker)
- [Configuration](#configuration)
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
3. optionally [Configure](#configuration] the instance with 
3. `make start` 

### Via Docker

A Docker image is automatically build on GitHub.

Run from recent Docker image:

~~~sh
docker run --rm -p 7007:7007 ghcr.io/gbv/validation-api-ws:main
~~~

Same but with local config file (which must exist):

~~~sh
test -f config.json && docker run --rm -p 7007:7007 --volume ./config.json:/app/config.json ghcr.io/gbv/validation-api-ws:main
~~~

Run from locally built Docker image:

~~~sh
docker run --rm -p 7007:7007 validator
~~~

## Configuration

The [default configuration](config.default.json) contains some base formats. To defined the application profiles to be checked against, create a configuration file in JSON format at `config.json` in the current directory or in the local subdirectory `config`. It is also possible to pass the location of config file or directory with argument `--config` at startup.

The configuration file must contain field `profiles` with a list of profile objects, each having a unique `id` and a list of `checks`. See [profiles configuration JSON Schema](lib/validate/profiles-schema.json) for details. Additional config fields include:

- `title` (title of the webservice) is set to "Validation Service" by default.
- `port` (numeric port to run the webservice) is set to 7007 by default.
- `stage` (stage directory for data files at the server). Set to `false` (disabled) by default.
- `reports` (reports directory to store reports in). Set to `false` (disabled) by default.
- `downloads` (cache directory for data retrieved via URL). Set to `false` (disabled) by default.

## API

The webservice provides one endpoint to [list application profiles](#get-profiles) and one **Data Validation API** endpoint for each profile to validate data (with either HTTP GET or HTTP POST, listed as two endpoints below).

Details of Data Validation API are still being specified, so details may change. The core response format is being specified as **[Data Validation Error Format]**.

#### GET /profiles

Return a list of application profiles configured at this instance of the validation service. The information is a subset of configuration limited to the fields `id` (required`, `title`, `description`, and `url`.

#### GET /{profile}/validate

Validate data against an application profile and return a list of errors in [Data Validation Error Format]. Data must be passed via one of these query parameters:

- `data` as string
- `url` to be downloaded from an URL (if the service is configured with `downloads` directory)
- `file` to be read from a local file in the stage directory of the server (if the service is configured with `stage` directory)

Status code is always 200 if validation could be executed, no matter whether errors have been found or not.

For example validating the string `[1,2` at default profile `json` (`curl http://localhost:7007/json/validate -d '[1,2'`) results in this validation response:

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

#### POST /{profile}/validate

Same as GET request but data is passed as request body or as file upload (content type `multipart/form-data`).

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
test -f config.json && docker run --rm -p 7007:7007 --volume ./config.json:/app/configt.json validator
~~~

See also <https://github.com/gbv/validation-server> for a previous implementation in NodeJS. Both implementations may converge

This work is [funded by DFG (project "AQinDa")](https://gepris.dfg.de/gepris/projekt/521659096)

## License

MIT © 2025- Verbundzentrale des GBV (VZG)

[Data Validation Error Format]: https://gbv.github.io/validation-error-format/
