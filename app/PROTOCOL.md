# Urja Meter Ops Portal — Protocol Notes

## 1. Purpose

This document records the observed behavior of the Urja Meter Ops legacy portal during investigation for the Flock Energy engineering take-home assignment.

The objective is to understand how the portal exposes meter and transformer data over HTTP and document the behavior needed to build a separate, read-only API service.

**Portal base URL:** `https://urja-ops.flockenergy.tech`

The observations below describe the requests and responses observed during development. They are not a guarantee that every endpoint, field, or behavior will remain unchanged.

## 2. Authentication and Session Management

### Login flow

The portal uses a login form at:

```http
GET /login
POST /login
```

The observed login flow is:

1. Send a GET request to `/login`.
2. Submit a POST request to `/login` containing the form fields `email` and `password`.
3. Include the expected same-origin headers, including `Origin` and `Referer`.
4. Retain the session cookies returned by the server.
5. Reuse the authenticated session when making subsequent portal requests.

### Login request

The login POST uses form-encoded data with these fields:

| Field | Purpose |
|---|---|
| `email` | Portal account email |
| `password` | Portal account password |

The request also needs headers identifying the portal origin and login page as the referrer.

### Observed login response

A successful login attempt returned HTTP status `200` with a JSON response similar to:

```json
{
  "type": "redirect",
  "status": 303,
  "location": "/meters"
}
```

The response describes a redirect to `/meters`. In the observed flow, the HTTP response itself was `200`, while the JSON body contained the redirect status `303`.

The authenticated session is maintained using cookies. The API service therefore needs to preserve cookies across requests rather than independently sending credentials with every data request.

### Authentication quirk

An initial login attempt without the expected `Origin` and `Referer` headers returned:

```http
403 Forbidden
```

with a response body indicating that cross-site POST form submissions were forbidden.

Adding the expected same-origin headers allowed the login flow to proceed. This demonstrates that reproducing the browser's login behavior requires more than sending the username and password alone.

### Session validation and recovery

The wrapper checks whether the existing portal session can access a protected meter-search endpoint. If the session is rejected, it attempts to log in again and rechecks access.

This is intended to reduce failures caused by expired or invalid sessions. The behavior should also be tested against other upstream failures, including timeouts and server errors, to ensure they are not incorrectly treated as authentication failures.

Credentials must be loaded from environment configuration. Passwords, session cookies, and other secrets must not be written to logs or committed to source control.

## 3. Observed Data Endpoints

The following endpoints were observed during portal investigation.

### 3.1 Meter search

**Request**

```http
GET /portal/meters/search?q=J100000&page=1
```

**Query parameters**

| Parameter | Purpose |
|---|---|
| `q` | Meter search query |
| `page` | Requested result page |

**Observed response structure**

```json
{
  "data": [
    {
      "meterId": "J100000",
      "serialNo": "SE33962",
      "make": "HPL",
      "phaseType": "single",
      "installStatus": "Decommissioned",
      "dtCode": "DT-001"
    }
  ],
  "total": 1,
  "page": 1,
  "pageSize": 10
}
```

The values above illustrate the observed field names and an example record. The `total` and `pageSize` values are illustrative and may differ for a real query.

**Observed fields**

- `meterId`: Meter identifier.
- `serialNo`: Meter serial number.
- `make`: Meter manufacturer.
- `phaseType`: Phase classification.
- `installStatus`: Installation status.
- `dtCode`: Associated distribution transformer code.
- `total`, `page`, `pageSize`: Pagination metadata.

The response uses a `data` array for records and separate pagination metadata.

### 3.2 Meter geographic information

The portal exposes meter geographic information under a meter-specific route within `/portal/meters/`.

The observed response has the following structure:

```json
{
  "data": {
    "latitude": "26.938961002479868",
    "longitude": "75.83095696146852"
  }
}
```

Coordinates were returned as strings in the observed response. The wrapper should validate and document its own chosen representation and handle missing or invalid coordinate values appropriately.

### 3.3 Meter energy readings

Energy readings are available from a meter-specific endpoint under `/portal/meters/`.

The observed response has a `data` array:

```json
{
  "data": [
    {
      "timestamp": "23/06/2026 23:30",
      "kwh": "48438.74",
      "kvah": "52313.84",
      "voltR": "226"
    }
  ]
}
```

The example illustrates the observed field names and value formats.

**Observed fields**

- `timestamp`: Reading timestamp, represented as a formatted string.
- `kwh`: Energy measurement in kWh.
- `kvah`: Energy measurement in kVAh.
- `voltR`: Voltage reading for the R phase.

The measurements were represented as strings in the observed response. Timestamp parsing, numeric conversion, units, and handling of missing readings should be explicit in the wrapper's models and documentation.

The timestamp format observed in the sample was `DD/MM/YYYY HH:mm`. The timezone and the full interpretation of the timestamp were not established during the initial investigation.

### 3.4 Transformer listing

**Request**

```http
GET /portal/dts?page=1
```

**Query parameters**

| Parameter | Purpose |
|---|---|
| `page` | Requested result page |

**Observed response structure**

```json
{
  "data": [
    {
      "code": "DT-001",
      "name": "Malviya Nagar DT 1",
      "feederCode": "F-001",
      "capacityKva": 100
    }
  ]
}
```

**Observed fields**

- `code`: Transformer identifier.
- `name`: Transformer name.
- `feederCode`: Associated feeder identifier.
- `capacityKva`: Transformer capacity in kVA.

The portal response included transformer records inside a `data` array. The full pagination behavior and all optional fields should be verified before making stronger assumptions about the dataset.

## 4. Relationship Between Meters and Transformers

Meter search records include a `dtCode` field, while transformer records include a `code` field.

These fields suggest a relationship between meters and distribution transformers. Matching them may allow the wrapper to associate a meter with a transformer.

However, a complete network hierarchy was not established during the initial investigation. Additional exploration would be needed to determine whether the portal exposes feeder, transformer, and meter relationships consistently and whether the data contains missing or inconsistent references.

The current API should not claim to provide a complete network hierarchy unless that behavior is implemented and verified.

## 5. Wrapper API Versus Portal API

The wrapper exposes a separate API intended for application and data-team consumption.

| Wrapper endpoint | Purpose |
|---|---|
| `GET /health` | Report application and portal-session readiness |
| `GET /meters/search` | Search for meters |
| `GET /meters/{meter_id}/geo` | Retrieve geographic coordinates |
| `GET /meters/{meter_id}/energy` | Retrieve energy readings |
| `GET /transformers` | Retrieve transformer data |

The wrapper's endpoint names, response models, validation, and authentication are separate from the legacy portal's HTTP interface.

The wrapper uses its own API-key authentication for clients. The backend separately handles portal authentication and session cookies. Clients should not need direct access to the portal credentials.

The wrapper's OpenAPI specification is maintained in [`openapi.json`](openapi.json).

## 6. Error Handling and Reliability

The portal is an upstream dependency and may return errors or become temporarily unavailable.

The wrapper translates common HTTP-client failures into API errors rather than exposing raw exception details to callers.

The current implementation is intended to distinguish between:

- **Timeouts:** The upstream portal did not respond within the configured timeout.
- **Connection failures:** The wrapper could not connect to the portal.
- **Upstream HTTP errors:** The portal returned an unsuccessful HTTP status.
- **Unexpected failures:** An unanticipated error occurred while processing a request.

The wrapper uses HTTP `502 Bad Gateway` for common upstream failures and `504 Gateway Timeout` for upstream timeouts.

These mappings should be tested to confirm that each failure type is handled consistently and that sensitive upstream response details are not exposed.

Session recovery also needs careful handling: a rejected session can justify re-authentication, but an unrelated server error or network timeout should not automatically be interpreted as an expired session.

## 7. Data Freshness and Caching

The current approach retrieves data from the portal when API requests are made rather than maintaining a separate local dataset.

No caching policy has been established. This avoids introducing stale-data behavior before the portal's update frequency and the consumers' freshness requirements are understood.

If caching is added later, the implementation should document:

- Cache lifetime and invalidation rules.
- Whether different endpoint types need different expiration periods.
- How updates in the portal become visible to API consumers.
- How errors are handled when cached data exists but the portal is unavailable.

## 8. Security Considerations

- Store portal credentials in environment variables or a secrets manager.
- Do not commit `.env` files, credentials, session cookies, or real API keys.
- Require the wrapper's API key on protected endpoints.
- Use HTTPS in deployed environments.
- Avoid logging sensitive headers, passwords, or cookies.
- Consider key rotation, revocation, and per-client access controls for production use.
- Treat portal response data as untrusted input and validate it before returning it from the wrapper.

The wrapper is intended for read-only use and does not attempt to bypass access controls or modify portal data.

## 9. Known Limitations and Open Questions

The initial investigation did not fully establish:

- The complete network hierarchy between meters, transformers, and feeders.
- The full set of optional fields and edge cases in every response.
- Whether every endpoint uses identical pagination conventions.
- The timezone associated with energy-reading timestamps.
- The portal's rate limits and maximum result sizes.
- The portal's expected session lifetime and all session-expiration behaviors.
- Whether a supported bulk-data retrieval path exists.
- The freshness requirements for each data type.

These are potential areas for further investigation rather than confirmed portal capabilities.

## 10. Follow-up Investigation

With additional time, I would:

1. Verify response schemas against multiple meter and transformer records.
2. Test empty search results, invalid identifiers, missing fields, and malformed values.
3. Confirm pagination behavior and maximum page sizes.
4. Test session expiration and recovery in a controlled way.
5. Investigate meter-to-transformer-to-feeder relationships.
6. Determine timestamp timezone semantics and whether energy readings are ordered consistently.
7. Evaluate whether a bulk retrieval path exists and whether caching would be useful.

## 11. Summary

The investigation established a working HTTP-based login flow, cookie-backed portal sessions, and read access to meter search, geographic information, energy readings, and transformer records.

The wrapper builds on these observations to provide a separate, validated, documented API with API-key protection and upstream error handling.

This document records observed behavior and known uncertainties so that future developers can understand the integration without having to rediscover the entire portal protocol.