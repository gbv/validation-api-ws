# Validation API (demo)

[![Docker image](https://github.com/gbv/validation-api-demo/actions/workflows/docker.yml/badge.svg)](https://github.com/orgs/gbv/packages/container/package/validation-api-demo)
[![Test](https://github.com/gbv/validation-api-demo/actions/workflows/test.yml/badge.svg)](https://github.com/gbv/validation-api-demo/actions/workflows/test.yml)

> Demo of a simple Web API to validate data against predefined criteria

## Table of Contents

- [Usage](#usage)
  - [From sources](#from-sources)
  - [With Docker](#with-docker)
- [Configuration](#configuration)

## Usage

Start the the web application with default [configuration](#configuration) on port 7007.

### From sources

- Clone repository
- `make deps`
- `make start` 

### Via Docker

A Docker image is automatically build on GitHub.


Run from recent Docker image:

~~~sh
docker run --rm -p 7007:7007 ghcr.io/nfdi4objects/validation-api-demo
~~~

Same but with local config file (which must exist):

~~~sh
test -f config.json && docker run --rm -p 7007:7007 --volume ./config.json:/app/config.json ghcr.io/nfdi4objects/validation-api-demo
~~~

Run from locally built Docker image:

~~~sh
~~~

## Configuration

If local file `config.json` exist, it is used for configuration, otherwise [default configuration](config.default.json).

## Development

To locally build and run the image Docker for testing:

~~~sh
docker image build -t validator .
docker run --rm -p 7007:7007 validator  # default config, or:
test -f config.json && docker run --rm -p 7007:7007 --volume ./config.json:/app/configt.json validator
~~~

