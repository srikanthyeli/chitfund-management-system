# Backend Coding Guidelines

All backend development for the **Chit Fund Management System** must strictly adhere to the following standards, architectural patterns, and quality rules.

---

## 1. Directory & Layered Architecture
We follow a separation of concerns layout inside the FastAPI application:
*   **Routers / Views (Thin Layer):** Handles HTTP requests, path parameters, query parameters, dependency injections, and returns HTTP responses. No business logic or database queries should live here.
*   **Services / Business Logic (Core Layer):** Orchestrates transactions, executes calculations, and applies business rules.
*   **Repositories / Queries / Repos (Data Access Layer):** Direct database interactions via SQLAlchemy. No business logic or calculations should reside here.
*   **DB Setup:** Centralized connection configuration, engines, and session tracking.

---

## 2. Code Quality & Performance Rules
*   **Thin Controllers/Routers:** Route handlers should only call service methods and validate inputs/outputs.
*   **No DB Queries inside Loops (N+1 Prevention):** Always batch fetch (`IN` clause, eager loads, joins) instead of querying inside a loop.
*   **Dynamic Queries:** Use filter-building helpers for dynamic query configurations.
*   **Database Transactions:** Wrap multi-step mutating operations in transaction blocks (using `with db.begin():` or similar) to ensure all financial operations are atomic.

---

## 3. Input Validation & Serialization
*   Use **Pydantic v2** schemas for request body parsing, query validation, and response serialization.
*   All endpoints must declare explicit response schemas (`response_model`).

---

## 4. Error Handling & API Contracts
*   **Centralized Error Strategy:** Use defined error message files or utilities (`ErrorMsgs`, `MsgUtils`) instead of raw text inline.
*   **HTTP Exceptions:** Map internal service errors to appropriate HTTP status codes in the routers layer.
*   **API Versioning:** Prefix all endpoints with version identifiers (e.g., `/api/v1/`, `/api/v2/`) to prevent breaking change conflicts with the frontend.
*   **Interactive Docs:** Auto-generate Swagger/OpenAPI specifications to maintain clear API contracts with the frontend.

---

## 5. Logging, Utils & Constants
*   **Day-wise Rotational Logging:** Set up file-based rotational logging (rotating daily) to track transactions and errors.
*   **No Hardcoding:** Centralize strings, statuses, configuration limits, and parameters in a `constants.py` or `.env` configuration file.
*   **Helper Utils:** Move generic calculations (like simple interest or commission) to modular utility files.

---

## 6. Schedulers & Readmes
*   **Documentation:** Maintain readable `README.md` files at the root of the project, inside the API folders, and inside any background Schedulers/Cron directories.
*   **GitHub Actions:** Set up GitHub workflows for running unit tests, linting check tasks, and deployments.
