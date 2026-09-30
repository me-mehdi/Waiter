# The Waiter - UK Market Digital Hospitality Platform

> Enterprise-grade, hardware-agnostic digital ecosystem enabling seamless **"Scan to Invoice"** workflows for UK pubs, cafes, fast-casual venues, and hotels.

[![UK Strategy Document](https://img.shields.io/badge/Docs-UK%20Market%20Strategy-blue)](docs/UK_MARKET_STRATEGY.md)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-brightgreen)](https://python.org)

---

## 🌟 Executive Overview

**The Waiter** resolves SaaS sprawl and labor shortages across the UK hospitality landscape by consolidating point-of-sale, table-side ordering, kitchen management, customer feedback, and financial invoicing into a single unified cloud ecosystem.

Read the full executive blueprint: [UK Market Strategy & Operational Blueprint](file:///Users/elmehdinidazi/Downloads/Waiter/docs/UK_MARKET_STRATEGY.md).

---

## 🚀 Core Functional Modules

1. **QR Code Ordering & Digital Menus** (`src/modules/qr_ordering.py`)
   - Dynamic, photo-rich catalogues with smart upsell recommendations.
   - Built-in multi-language translation support (`EN`, `FR`, `AR`).
2. **Kitchen Display System (KDS) & TV Tracking** (`src/modules/kds.py`)
   - Real-time order line digitalization (`New` ➔ `Preparing` ➔ `Ready`).
   - Zero lost tickets; live queue tracking for kitchen and service staff.
3. **Targeted Promo Codes** (`src/modules/promos.py`)
   - Targeted discounts with usage limits to boost off-peak demand.
4. **Private Customer Reviews ("Avis clients")** (`src/modules/reviews.py`)
   - Internal guest feedback collection to mitigate public negative reviews.
5. **Automated Finance & Analytics** (`src/modules/finance.py`)
   - Automated PDF invoicing with sequential invoice numbers.
   - Real-time RevPASH analytics, peak-hour heatmaps, and dish sales ranking.

---

## 🛠️ Architecture & Setup

### Repository Structure

```
Waiter/
├── docs/
│   └── UK_MARKET_STRATEGY.md
├── src/
│   ├── core/
│   │   ├── config.py
│   │   ├── db.py
│   │   └── translation.py
│   ├── modules/
│   │   ├── qr_ordering.py
│   │   ├── kds.py
│   │   ├── promos.py
│   │   ├── reviews.py
│   │   └── finance.py
│   └── app.py
├── tests/
│   └── test_modules.py
├── requirements.txt
└── README.md
```

### Installation & Execution

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run unit tests
python -m unittest discover -s tests

# 3. Start the application
python src/app.py
```

---

## 📞 Contact Information

- **Website**: [waiter.com](https://waiter.com/)
- **Phone**: +44 7594 560831
- **Email**: nidaazzielmehdi@gmail.com
