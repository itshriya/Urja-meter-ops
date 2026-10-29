# Urja Meter Ops API

A FastAPI wrapper around Flock Energy's legacy Urja Meter Ops portal, providing a structured API for retrieving electricity meter information, geographic coordinates, energy readings, and transformer data.

The goal is to make portal data accessible to applications and data teams through a documented API without requiring them to interact with the original web interface.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Running the API](#running-the-api)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Example Requests](#example-requests)
- [API Documentation](#api-documentation)
- [Portal Investigation](#portal-investigation)
- [Assumptions and Design Decisions](#assumptions-and-design-decisions)
- [Limitations and Intentionally Skipped Work](#limitations-and-intentionally-skipped-work)
- [Future Improvements](#future-improvements)
- [Testing](#testing)
- [Reflection](#reflection)

## Overview

Urja Meter Ops is a legacy web portal used to look up smart-meter information. Since the portal does not provide a convenient API for programmatic access, this project adds a FastAPI service between API consumers and the existing portal.

The service uses an authenticated HTTP client to communicate with the portal, transforms portal responses into structured API responses, and protects its own endpoints with API-key authentication.

The portal is treated as a **read-only data source**. This service does not attempt to modify portal records.

## Features

- Search for electricity meters using a query and page number.
- Retrieve geographic coordinates for a meter.
- Retrieve energy readings for a meter.
- Retrieve paginated transformer data.
- Validate and structure responses using Pydantic models.
- Protect API endpoints with an API key.
- Reuse an HTTP client and portal session.
- Handle common upstream errors, including timeouts and connection failures.
- Expose an OpenAPI specification and interactive API documentation.
- Include automated tests for API behavior, validation, security, and error handling.

## Technology Stack

- **Python 3.11**
- **FastAPI** — API framework
- **HTTPX** — asynchronous HTTP requests to the legacy portal
- **Pydantic** — configuration and response validation
- **Pytest** — automated testing
- **Uvicorn** — ASGI development server

## Project Structure

urja meter ops/
├── .DS_Store
├── .env
├── .env.example
├── .git/
├── .gitignore
├── .pytest_cache/
├── __pycache__/
├── PROTOCOL.md
├── README.md
├── openapi.json
├── pytest.ini
├── requirements.txt
├── venv/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   ├── errors.py
│   │   ├── http_client.py
│   │   ├── lifespan.py
│   │   └── security.py
│   ├── integrations/
│   │   └── urja/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── details.py
│   │       ├── meters.py
│   │       └── transformers.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── meter_details.py
│   │   ├── meter.py
│   │   └── transformer.py
│   └── routes/
│       ├── meters.py
│       └── transformers.py
└── tests/
    ├── test_auth_recovery.py
    ├── test_auth.py
    ├── test_errors.py
    ├── test_meter_validation.py
    ├── test_meters.py
    ├── test_security.py
    └── test_transformers.py


### Architecture

The application is organized by responsibility:

- **Routes:** Define the public API endpoints, validate request parameters, and return responses.
- **Models:** Define the expected structure of API responses.
- **Integrations:** Contain the HTTP interactions with the Urja Meter Ops portal.
- **Core:** Handle configuration, HTTP client setup, authentication, application lifecycle, and error translation.
- **Tests:** Verify important behavior without requiring every test to make a live request to the portal.

This separation keeps portal-specific details out of the public API layer and makes the integration easier to test and maintain.

## Prerequisites

- Python 3.11 or compatible
- Git```
- Access to the Urja Meter Ops portal
- Portal credentials supplied for the assignment

## Installation and Setup

### 1. Clone the repository

bash
git clone <YOUR_PUBLIC_GITHUB_REPOSITORY_URL>
cd <YOUR_REPOSITORY_DIRECTORY>


Replace the placeholders with your actual repository URL and directory name.

### 2. Create and activate a virtual environment

On macOS or Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using the example:

```bash
cp .env.example .env
```

Update `.env` with your portal credentials and a strong API key.

Example `.env.example`:

```dotenv
PORTAL_BASE_URL=https://urja-ops.flockenergy.tech
PORTAL_USERNAME=your-portal-username
PORTAL_PASSWORD=your-portal-password
API_KEY=replace-with-a-strong-random-secret
PORTAL_TIMEOUT_SECONDS=15
```

Ensure these names match the application's configuration in `app/core/config.py`.

Generate a random API key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the generated value into `API_KEY` in your local `.env` file.

**Security:** Never commit `.env`, real portal credentials, session cookies, or actual API keys. Commit `.env.example` with placeholders only.

## Running the API

Start the development server from the project root:

```bash
uvicorn app.main:app --reload
```

The API should be available at:

- Base URL: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health endpoint: `http://127.0.0.1:8000/health`

The health endpoint reports whether the application considers the portal session ready. It is not necessarily a full end-to-end check of every portal operation.

## Authentication

The service has two authentication layers:

1. **Client-to-API authentication:** Consumers provide the API key using the `X-API-Key` request header.
2. **API-to-portal authentication:** The backend uses configured portal credentials to establish a portal session and makes subsequent requests through its HTTP client.

API consumers do not need to know the portal credentials or manage the portal session themselves.

Example header:

```http
X-API-Key: your-api-key
```

In production, store credentials and API keys in a secrets manager or protected deployment configuration. Use HTTPS, rotate secrets when necessary, and avoid logging sensitive values.

## API Endpoints

The following endpoints are implemented by the service. Confirm their response schemas and query parameters in the generated OpenAPI documentation before submission.

| Method | Endpoint                          |     Purpose                                         | 
| ------ | --------------------------------- |---------------------------------------------- |
| GET    | `/health`                         | Report application and portal-session readiness |
| GET    | `/meters/search?q=J100000&page=1` | Search for meters                               |
| GET    | `/meters/{meter_id}/geo`          | Retrieve a meter's coordinates                  |
| GET    | `/meters/{meter_id}/energy`       | Retrieve energy readings                        |
| GET    | `/transformers?page=1`            | Retrieve paginated transformer data             |

Except for `/health`, the endpoints are intended to require a valid `X-API-Key` header.

### Meter search

Accepts a search query and page number. The response includes meter records and pagination metadata, such as the total number of matches, current page, and page size, where supplied by the portal.

### Meter geographic information

Returns the latitude and longitude associated with a meter, where available in the portal.

### Meter energy readings

Returns the energy readings available for a meter. The response may include timestamps and measurements such as kWh, kVAh, and voltage.

### Transformer listing

Returns transformer records, including fields such as transformer code, name, feeder code, and capacity where available.

## Example Requests

Set your API key in the shell:

```bash
export API_KEY='your-local-api-key'
```

### Check service health

```bash
curl http://127.0.0.1:8000/health
```

### Search for a meter

```bash
curl -G 'http://127.0.0.1:8000/meters/search' \
  -H "X-API-Key: $API_KEY" \
  --data-urlencode 'q=J100000' \
  --data-urlencode 'page=1'
```

### Retrieve geographic coordinates

```bash
curl 'http://127.0.0.1:8000/meters/J100000/geo' \
  -H "X-API-Key: $API_KEY"
```

### Retrieve energy readings

```bash
curl 'http://127.0.0.1:8000/meters/J100000/energy' \
  -H "X-API-Key: $API_KEY"
```

### Retrieve transformers

```bash
curl 'http://127.0.0.1:8000/transformers?page=1' \
  -H "X-API-Key: $API_KEY"
```

Replace the sample meter ID with another valid ID as needed. The examples assume the API is running locally and the environment is configured correctly.

## API Documentation

The API exposes an OpenAPI specification describing the wrapper service, rather than the original portal.

- **OpenAPI JSON:** [`openapi.json`](openapi.json)
- **Interactive Swagger UI:** [`/docs`](http://127.0.0.1:8000/docs) when running locally
- **ReDoc:** [`/redoc`](http://127.0.0.1:8000/redoc) when running locally
- **Portal investigation notes:** [`PROTOCOL.md`](PROTOCOL.md)

If `openapi.json` is generated from FastAPI, regenerate it after changing endpoint definitions, request parameters, response models, or security configuration.

## Portal Investigation

The portal was investigated through normal browser and HTTP interactions to understand how its data could be accessed programmatically.

The observations are documented separately in [`PROTOCOL.md`](PROTOCOL.md), including:

- Login flow and session behavior.
- Portal endpoints and response structures.
- Meter search, geographic information, energy readings, and transformer data.
- Observed authentication requirements and request quirks.
- Assumptions and limitations discovered during investigation.

The portal is treated as an upstream dependency, not as part of the public API contract. Its response format may change independently of this service.

## Assumptions and Design Decisions

### Assumptions

- The portal is the source of truth for the meter and transformer data exposed by this service.
- The assignment requires read-only access; write operations are outside scope.
- Portal credentials are provided through environment configuration rather than hard-coded in source files.
- The service's API key is intended to restrict access to its own endpoints.
- Portal data may be incomplete or inconsistent, so response validation and error handling are useful.
- Pagination is exposed where supported by the upstream portal.

### Design decisions and trade-offs

- **FastAPI:** Provides request validation, asynchronous endpoints, and automatic OpenAPI generation with relatively little boilerplate.
- **HTTPX:** Allows asynchronous HTTP communication and reuse of a client and its session cookies.
- **Pydantic response models:** Make the public response structure explicit and help detect unexpected upstream data.
- **Separate integration and route layers:** Keep upstream HTTP details separate from the public API.
- **API-key authentication:** Provides a simple access-control mechanism suitable for this take-home project. A production service with multiple customers would likely need more complete identity, authorization, and key-management capabilities.
- **No caching by default:** Avoids introducing cache invalidation and stale-data behavior before the portal's data freshness requirements are understood.
- **Explicit error translation:** Avoids returning raw upstream errors or internal exception details directly to consumers.

## Limitations and Intentionally Skipped Work

This implementation focuses on the core API wrapper and its documentation rather than optional extensions.

The following are intentionally outside the initial scope unless implemented separately:

- Reconstructing the complete meter-to-transformer-to-feeder network hierarchy.
- Building a local index for cross-field filtering or geographic proximity queries.
- Bulk extraction and storage of the full portal dataset.
- Caching and cache invalidation.
- A web-based dashboard or map.
- Multi-tenant API-key management, per-client quotas, and a key-revocation interface.
- Production deployment infrastructure and monitoring.

These items require additional investigation or introduce complexity that is not essential to demonstrate the basic API integration.

## Future Improvements

With additional time, I would prioritize:

1. **Improve integration resilience:** Test expired sessions, re-authentication, upstream rate limits, and transient failures against realistic scenarios.
2. **Expand test coverage:** Add more isolated tests for portal response parsing, API-key failures, pagination, timeouts, and malformed upstream responses.
3. **Strengthen security:** Use constant-time API-key comparison, external secret storage, rotation, and a more complete client authorization model.
4. **Improve observability:** Add structured logs, request correlation IDs, and metrics for latency and upstream failures without logging secrets.
5. **Clarify freshness guarantees:** Investigate how frequently portal data changes before introducing caching.
6. **Explore network hierarchy:** Determine how meters relate to transformers and feeders, then expose a useful read-only representation.
7. **Improve data discovery:** Evaluate a local index if users need filtering or location-based queries that the portal does not support.
8. **Automate documentation and delivery:** Regenerate and validate `openapi.json` in CI and run the test suite on every change.

## Testing

Run the automated test suite from the project root:

```bash
pytest -v
```

Tests should cover the behavior of API endpoints, request validation, authentication, error handling, and portal-session recovery.

Where possible, tests should use mocks or HTTPX mock transports instead of relying on a live portal. This makes them more repeatable and avoids unnecessary requests to the upstream service.

The test suite should be run before submission. Report the actual result from your latest run rather than a previously observed test count.

## Reflection

### 1. What assumptions did you make?

I treated the existing portal as the source of truth and kept the service read-only. I assumed that exposing the portal's useful data through a small set of predictable endpoints would be more valuable than recreating the entire portal. I also assumed that credentials and API keys should be configurable outside the source code.

### 2. Which part was the most difficult, and how did you get unstuck?

The most challenging part was understanding how the portal's authentication and session behavior worked. A normal browser login does more than send a username and password, so reproducing it required examining the HTTP requests and responses. I used the observed login flow and response behavior to guide the integration rather than guessing how the portal worked.

### 3. If you had another day, what would you improve?

I would expand tests around expired portal sessions, upstream failures, and unexpected response formats. I would also investigate the portal's network hierarchy and evaluate whether caching or a local index would improve common queries without returning stale data.

### 4. What mistake did you make while solving this?

During development, I initially encountered an authentication failure because the portal rejected a login POST that did not include the expected same-origin request headers. I investigated the response, adjusted the request to match the observed login flow, and retested the integration. This reinforced the importance of observing the actual protocol rather than assuming a login endpoint behaves like a generic form submission.

### 5. If you were reviewing your own submission, what would you criticise?

I would look closely at how the service handles long-running sessions and changes in the upstream portal. The API-key mechanism is intentionally simple and does not provide full client lifecycle management. I would also want broader integration tests, clearer operational monitoring, and a more explicit data-freshness strategy before treating the service as production-ready.

---

## Submission Checklist

Before making the repository public, verify that:

- [ ] The source code and tests are committed.
- [ ] `README.md` describes installation, configuration, endpoints, decisions, limitations, and reflection.
- [ ] `PROTOCOL.md` contains observations from your actual portal investigation.
- [ ] `openapi.json` is valid and describes the wrapper API.
- [ ] `.env.example` contains placeholders matching the application configuration.
- [ ] `.env`, credentials, API keys, and session cookies are not committed.
- [ ] `pytest -v` passes in a clean environment.
- [ ] The documented commands work when starting from a fresh clone.
- [ ] The GitHub repository is public and its URL is ready to email to the recruiter.