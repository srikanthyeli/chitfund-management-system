# Chit Fund Management System

## Overview

A premium digital platform tailored for managing rural and semi-urban chit funds efficiently, ensuring transparency, legal compliance (under the Chit Funds Act, 1982), and automated calculations.

### Features

- **Chit Creation:** Easy group initialization, duration setting, member assignment, and security deposit management.
- **Member Management:** Secure onboarding, KYC details tracking, and individual member profile management.
- **Monthly Auctions:** Automated digital bidding room, real-time bid tracking, and instant winner determination.
- **Bonus & Dividend Calculation:** Accurate distribution of auction discount among subscribers, automatically adjusting subsequent installments.
- **Collection Tracking:** Payment logs, receipt generation, pending installment alerts, and automated penalties.
- **Digital Passbook:** Real-time visibility for subscribers into paid installments, received dividends, and outstanding balances.
- **Reports & Analytics:** Dashboard insights for the foreman on collection efficiency, group health, and profitability.

### Tech Stack

*   **Frontend:** Angular 17 (PWA enabled for offline-first support in rural areas)
*   **Backend:** FastAPI (Python 3.10+)
*   **Database:** PostgreSQL (v15+)
*   **Authentication:** Mobile OTP-based authentication (secure, passwordless entry)

---

## Project Structure

```text
chitfund-management-system/
│
├── frontend/                  # Angular Web App (PWA)
│   └── angular-app/
│
├── backend/                   # FastAPI REST API
│   └── fastapi-app/
│
├── database/                  # Schema, migrations, and seed scripts
│   ├── schema/
│   ├── migrations/
│   └── seed/
│
├── docs/                      # Foundational system documentation
│   ├── business-flow.md       # Operational workflow and lifecycles
│   ├── business-rules.md      # Formulas, penalties, commissions
│   ├── entities.md            # Data models and attributes
│   ├── er-diagram.md          # Database schema relationships
│   └── api-design.md          # REST API OpenAPI specifications
│
├── docker/                    # Infrastructure / Dockerfiles
│
├── .gitignore
├── README.md
└── docker-compose.yml
```

---

## Getting Started

Detailed running instructions will be added as implementation progresses.
