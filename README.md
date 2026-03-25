# Stock Trend Scanner Modernization

> Placeholder: add dashboard screenshot or short GIF here later.

This repository is a modernization case study of an older Python desktop stock scanner. The original project centered on local scanner logic and a PySide6 interface; this version keeps the scanning logic, moves it behind a FastAPI backend, and adds a Next.js frontend that is easier to review, extend, and demo locally.

It is intentionally presented as a repo-first portfolio project, not as a polished production trading product.

## Overview

The app scans a stock universe for trend and candlestick setups, ranks matching symbols, and displays the results in a browser-based dashboard. The main value of the project is not "live deployment"; it is the technical transition from a legacy-style desktop app to a clearer frontend/backend architecture with better separation of concerns.

## Why This Project Exists

This project started as a desktop scanner with useful signal logic but a dated delivery model. I wanted to turn it into a stronger portfolio piece by:

- preserving the scanner and signal rules instead of rewriting them from scratch
- moving business logic behind an API boundary
- creating a frontend that is easier for other developers to inspect and understand
- making the project easier to evolve than the original desktop-first structure

The result is a technical refactor and product-thinking exercise: keep the core behavior, improve the architecture, and make the system easier to reason about.

## Modernization Highlights

- Reframed the project from a PySide6 desktop app into a web-first system with `api/` and `web/`
- Preserved the scanner engine in Python instead of discarding working domain logic
- Wrapped scanner operations in FastAPI endpoints for health checks, universe loading, scan execution, and CSV export
- Added a typed Next.js frontend for scan controls, result display, loading/error states, and detail views
- Kept the legacy desktop UI isolated in `legacy/desktop_app.py` for comparison and reference
- Retained an offline-friendly demo path through bundled sample universes and sample market data

## Tech Stack

- Backend: FastAPI, Uvicorn, pandas, numpy, yfinance, PyYAML
- Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS
- UI/data handling: TanStack Table, Lucide icons
- Legacy reference: PySide6 desktop app

## Project Structure

```text
.
|- api/
|  |- main.py                # FastAPI app entry point
|  |- routes/                # HTTP endpoints
|  |- schemas/               # Request/response models
|  |- services/              # API orchestration layer
|  `- scanner/               # Preserved scanner logic and config loading
|- web/
|  |- app/                   # Next.js app router
|  |- components/            # Dashboard UI
|  |- lib/                   # API client helpers
|  `- types/                 # Shared frontend types
|- legacy/
|  `- desktop_app.py         # Old desktop UI kept for reference
|- sample_data/              # Bundled sample OHLCV data for offline demos
|- universes/                # CSV watchlists and demo universes
|- config.yaml               # Scanner configuration
`- app.py                    # Root helper that points to the new architecture
```

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 20+

### 1. Install backend dependencies

From the repo root:

```bash
python -m pip install -r api/requirements.txt
```

### 2. Start the FastAPI backend

From the repo root:

```bash
python -m uvicorn api.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

### 3. Install frontend dependencies

In a second terminal:

```bash
cd web
npm install
```

### 4. Set the frontend API base URL if needed

The frontend defaults to `http://127.0.0.1:8000`, so this is optional for local development.

PowerShell:

```powershell
$env:NEXT_PUBLIC_API_BASE_URL="http://127.0.0.1:8000"
```

Bash:

```bash
export NEXT_PUBLIC_API_BASE_URL="http://127.0.0.1:8000"
```

### 5. Start the Next.js frontend

From `web/`:

```bash
npm run dev
```

Frontend URL:

```text
http://127.0.0.1:3000
```

## Environment Variables

### Frontend

- `NEXT_PUBLIC_API_BASE_URL`
  - Optional for local development
  - Defaults to `http://127.0.0.1:8000`

### Backend

- No required environment variables for the standard local sample-mode demo

## Best Demo Flow

For the most reliable local review:

1. Start the backend with `python -m uvicorn api.main:app --reload`
2. Start the frontend with `npm run dev` inside `web/`
3. Open `http://127.0.0.1:3000`
4. Leave the mode set to `sample`
5. Choose `demo_sample.csv`
6. Run a scan
7. Review the ranked results table, row detail panel, and CSV export flow

Why this flow is recommended:

- it avoids dependence on external market-data availability
- it highlights the architecture and UI improvements instead of network variability
- it gives reviewers a predictable way to evaluate the project locally

## Current Scope

What this repo is good at:

- showing the transition from legacy desktop code to a web-first architecture
- demonstrating API design around existing business logic
- showing a practical frontend for running scans and reviewing results
- serving as a technical portfolio piece and refactor case study

What this repo is not:

- a brokerage integration
- a live trading system
- a fully polished public product
- a claim of production readiness

## Limitations

- Live mode depends on `yfinance`, so data quality, latency, and availability are outside the app's control
- Dynamic universes such as S&P 500 and NASDAQ 100 fall back to curated ticker lists if upstream helpers fail
- The default demo experience uses a small bundled dataset rather than a broad historical data pipeline
- There is no authentication, persistence layer, user management, or saved scan history
- The UI is significantly cleaner than the original desktop version, but it is still a portfolio demo rather than a finished product
- There is no deployment configuration here intended to represent a polished public release

## Future Improvements

- Add tests around the scanner engine, API contracts, and key frontend flows
- Introduce stronger validation and more structured error handling across scan modes
- Improve observability with logging around scan execution and data-source failures
- Add saved scan history or lightweight persistence for repeatable comparisons
- Expand the demo workflow with screenshots, seeded examples, or short recorded walkthroughs
- Refine frontend polish and interaction details before considering a public deployment
- Add containerized local setup for faster onboarding

## Notes for Reviewers

- The legacy desktop entry point still exists at `legacy/desktop_app.py`, but it is no longer the primary interface
- The root `app.py` does not launch the old GUI; it points developers toward the FastAPI and Next.js setup instead
- The most representative code paths for this version are in `api/` and `web/`
