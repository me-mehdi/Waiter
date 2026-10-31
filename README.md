# The Waiter — UK Hospitality Operating System

> One system for every table, ticket and till. Built for how the UK trades.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-c8a86b?style=for-the-badge&logo=github)](https://me-mehdi.github.io/Waiter/)
[![CI/CD](https://img.shields.io/github/actions/workflow/status/me-mehdi/Waiter/ci.yml?branch=master&style=for-the-badge&label=Tests)](https://github.com/me-mehdi/Waiter/actions)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-0f1520?style=for-the-badge&logo=python)](https://python.org)
[![Deploy to Render](https://img.shields.io/badge/Deploy%20to-Render-46E3B7?style=for-the-badge&logo=render)](https://render.com/deploy?repo=https://github.com/me-mehdi/Waiter)

---

## 🌐 Live Deployments & URLs

- **Live Web App (GitHub Pages)**: [https://me-mehdi.github.io/Waiter/](https://me-mehdi.github.io/Waiter/)
- **GitHub Repository**: [https://github.com/me-mehdi/Waiter](https://github.com/me-mehdi/Waiter)
- **1-Click Render Deploy**: Ready with `render.yaml` and `Dockerfile`

---

## 🎨 Design System: Navy & Brass

The Waiter runs on a flat, high-contrast, accessible design system tailored for British hospitality:
- **Palette**: Deep Navy (`#0f1520`, `#141c28`), Warm Brass (`#c8a86b`, `#6b5b3e`), Cream (`#f3ebd8`), Crisp White (`#f8fafc`).
- **Typography**: Display serif `Fraunces` and high-legibility body sans `Inter`.
- **Principles**: Zero gradients, zero emoji, flat colour blocks, accessible $\ge 44\text{px}$ touch targets, and text status indicators alongside colour cues.
- **Placeholders**: 1-click toggle between `[X]` / `£[PRICE]` presentation placeholders and live UK venue figures.

---

## 🧭 Dedicated Screen Routes

Every screen in the ecosystem runs on its own dedicated URL path:

| Path | Screen | Description |
|:---|:---|:---|
| `/` or `/landing` | **1. Landing Page** | Flow overview (Order $\rightarrow$ Prepare $\rightarrow$ Settle), UK statutory grid, The Old Way vs Waiter, and 6-device cloud hub. |
| `/menu` | **2. Guest QR Menu** | Phone-frame ($390\times 844$) or full viewport with multi-currency, 5 languages (EN/FR/AR/PL/UR), Natasha's Law tags, Challenge 25 notices, and Pay at Table. |
| `/kitchen` | **3. Kitchen KDS** | Real-time 3-column ticket pass (NEW, PREPARING, READY), allergy alerts, delivery aggregator tabs, and Chef SOP recipes. |
| `/today` | **4. Owner Today** | 4 primary KPI tiles, covers, floor plan & bar stools, statutory EHO compliance panel, hourly sales chart, VAT invoice, and daily Z-report. |
| `/till` | **5. Till / POS** | Pre-auth bar tabs, 1-tap *"Same again!"* round reorders, and quick-tap counter register. |
| `/reservations`| **6. Reservations** | Tonight's covers roster, £10/guest deposit card pre-auth hold, and Sunday Roast pre-order counter. |
| `/stock` | **7. Stock & Cellar** | Live recipe gross profit % (target 70%+), keg cellar levels, 7-day line cleaning logs, and Booker/Bidfood/Brakes ordering. |
| `/staff` | **8. Staff Rota** | 4-digit PIN clock-in/out, live labour cost % vs sales, and October 2024 Tips Act 100% tronc distribution policy. |
| `/settings` | **9. Settings** | Certified Epson TM-T88 and Star TSP143 ESC/POS test printing, store-and-forward offline queue sync, and UK GDPR hosting. |

---

## 🚀 Quickstart & Local Execution

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/me-mehdi/Waiter.git
cd Waiter

# Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Test Suite (100% Pass)

```bash
pytest tests/test_modules.py -v
```

### 3. Launch Development Server

```bash
python src/app.py
```
Open [http://127.0.0.1:5050](http://127.0.0.1:5050) in your browser.

---

## 🐳 Docker Deployment

Build and run the production container:

```bash
docker build -t waiter-os:latest .
docker run -d -p 5050:5050 --name waiter-container waiter-os:latest
```

---

## ☁️ Cloud PaaS Deployment (Render / Railway / Fly)

The repository includes pre-configured deployment manifests:
- **Render**: `render.yaml` sets up the Python web service with Gunicorn automatically.
- **Heroku / Railway / Fly.io**: `Procfile` configured for `gunicorn -c gunicorn.conf.py src.app:app`.
- **GitHub Pages**: Automatically deployed via GitHub Actions on every commit to `master`.

---

## 📞 UK Hospitality Enquiries

- **UK Team Phone**: +44 7594 560831
- **Email**: nidaazzielmehdi@gmail.com
- **Website**: [waiter.com](https://waiter.com/)
