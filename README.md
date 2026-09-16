# API Testing with Playwright

An API test suite for the [GoRest](https://gorest.co.in/) public REST API, built with Python, pytest, and Playwright's synchronous API testing client. This project was built to demonstrate API test automation and SDET fundamentals: request chaining, auth handling, negative/edge-case testing, schema validation, data-driven tests, and a CI pipeline with a published test report.

**Live test report:** https://sivaranjani19.github.io/api-testing-playwright/
(auto-published on every push to `main` and every nightly run)

## Tech Stack

- **Python** + **pytest** — test runner and assertions
- **Playwright (sync API)** — HTTP client, used purely for API requests (not browser automation; `pytest-playwright` is deliberately not used, since that plugin is built for browser testing)
- **Faker** — generates unique test data per run
- **jsonschema** — response schema/contract validation
- **python-dotenv** — loads secrets from a local `.env` file
- **pytest-html** — generates the HTML test report
- **GitHub Actions** — CI, running on push and a nightly schedule

## Architecture

### Fixtures (`conftest.py`)

Three session-scoped fixtures:

- **`playwright_instance`** — the only place `sync_playwright()` is invoked. Playwright's sync API only allows one active `sync_playwright()` context manager per thread; having two independent fixtures each call it directly caused a real `asyncio` event-loop conflict during development. Centralizing it here means every other fixture depends on this one instead of creating its own.
- **`api_request_context`** — an authenticated `APIRequestContext`, built from `playwright_instance`, carrying a bearer token (`GOREST_TOKEN`) in its headers. Used by every test that needs a valid, logged-in client.
- **`unauthenticated_request_context`** — the same shape, but with no `Authorization` header. Exists specifically to test that GoRest correctly rejects unauthenticated requests, without having to strip headers per-request inside individual tests.

Both context fixtures share the one `playwright_instance`, so there's exactly one Playwright driver process per test session no matter how many request contexts are built from it.

### Secrets

`GOREST_TOKEN` is read via `os.getenv()` in both environments:
- **Locally**, it comes from a `.env` file (gitignored, never committed) loaded by `python-dotenv`.
- **In CI**, it's injected directly as a GitHub Actions repository secret — `load_dotenv()` simply finds no `.env` file and does nothing, and `os.getenv()` picks up the value from the environment either way. No code branches on which environment it's running in.

### Data factory (`tests/factories.py`)

`build_user_payload()` returns a **fresh dict on every call**, using `Faker` to generate a unique email each time. This was a deliberate fix, not the starting design — GoRest rejects duplicate emails, and an earlier version of this suite used a single shared payload dict that got mutated in place across tests, causing failures that leaked between unrelated test cases. A factory function that returns new data per call keeps every test's data independent and re-runnable.

It started out living inside `test_users.py`, then moved into its own module once `test_posts.py` needed the same "create a valid user" step — posts and comments both require a real, pre-existing user to attach to, so the factory is now shared across both test files instead of duplicated.

### Schema validation

`user_schema` (a JSON Schema dict, validated via `jsonschema.validate()`) checks the *shape* of a GoRest user object — types and required fields — which catches things manual `assert "id" in response` checks wouldn't, like a field coming back as the wrong type.

## Test Coverage

### Users (`tests/test_users.py`)
- **CRUD lifecycle with request chaining** — `test_user_lifecycle` creates a user, reads it back, updates it, deletes it, then verifies the delete by confirming a subsequent GET returns `404`. Each step uses the ID returned by the previous one.
- **Auth flow** — token loaded once via fixture, reused across every authenticated test.
- **Negative tests** — missing required fields and invalid field values (parametrized, `test_create_user_invalid_payload`) assert `422` and check the error response body names the specific broken field; unauthenticated requests (`test_create_user_unauthorized`) assert `401`.
- **Schema/contract assertions** — response shape validated against a JSON Schema, not just spot-checked fields.

### Posts & comments (`tests/test_posts.py`)
- **Cross-resource chaining** — `test_create_post_comment_for_user` creates a user, then a post attached to that user's real `id`, then a comment attached to that post's real `id` — each step depends on the previous one's actual response, not hardcoded IDs.
- **CRUD lifecycle for posts** — `test_post_lifecycle` mirrors the user lifecycle test: create → read → update → delete → verify gone.
- **Negative tests** — missing required fields (`test_create_post_with_invalid_payload`, parametrized over `title`/`body`) assert `422`; an invalid/nonexistent `user_id` (`test_create_post_with_invalid_userId`) also asserts `422`, with the error body checked against GoRest's actual response shape rather than an assumed one — the error names the related resource (`"field": "user"`), not the literal payload key (`user_id`), which only became clear by inspecting a real response first.

### Across both
- **Data-driven tests** — invalid-payload tests run multiple cases through one parametrized test function instead of duplicated near-identical tests.
- **Parallel-safe design** — every test builds its own unique data via the shared factory and doesn't depend on state left behind by other tests.

## Running Locally

```bash
git clone https://github.com/sivaranjani19/api-testing-playwright.git
cd api-testing-playwright
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root with your own [GoRest](https://gorest.co.in/) token:
```
GOREST_TOKEN=your_token_here
```

Run the tests:
```bash
pytest tests/ -v
```

Generate an HTML report:
```bash
pytest tests/ --html=report.html --self-contained-html
```

## CI/CD

`.github/workflows/tests.yml` runs the full suite:
- On every push to `main`
- On a nightly schedule (3 AM UTC)

Each run installs dependencies, executes the tests against the live GoRest API, and publishes the resulting HTML report to GitHub Pages — so the latest test results are always viewable at the link above, pass or fail.

## Possible Next Steps

- Migrate reporting from pytest-html to Allure for richer test history/trends
- Extend coverage further (e.g. pagination, GoRest's `todos` endpoint)
