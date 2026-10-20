# GRD-PHY-Project

## AI SmartScan — Inventory Dashboard

This project contains a browser-based inventory dashboard demo and a Flask API starter. The dashboard shows stock levels, movements, delivery verification, alerts, and category reports. The API adds SQLite-backed product and delivery data; its scan confidence values are sample data, not output from a real AI model.

## Features

- Overview metrics, searchable inventory, and product details
- Simulated scan review and delivery discrepancy workflow
- Low-stock, out-of-stock, expiry, barcode, and pending-delivery alerts
- Category reports and inventory valuation
- Flask endpoints for products, stock adjustments, delivery review and confirmation
- SQLite persistence and sample data for Oman Chips, Oreo, and Water Bottle

The three initial products use zero-valued quantity and price placeholders. Update them in the API or replace the sample seed values before using the data for real inventory.

## Project files

- `AI SmartScan — Inventory Dashboard (Demo).html` — single-page dashboard with embedded styles and JavaScript
- `app.py` — Flask API, SQLite models, and demo seed data
- `requirements.txt` — Python dependencies
- `README.md` — setup and project documentation

## Run the dashboard

Open the HTML file directly in a modern browser, or serve the project folder:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000/`.

## Run the API

1. Install Python 3.10 or newer and create/activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the API:
   ```bash
   python app.py
   ```
4. Check `http://127.0.0.1:5000/api/health`.

SQLite data is stored in `instance/smartscan.db`.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/state` | Dashboard bootstrap payload |
| GET | `/api/products?q=chips&category=Snacks` | Search/filter products |
| POST | `/api/products` | Create product |
| PATCH | `/api/products/P01` | Update product fields |
| POST | `/api/stock-adjustments` | Adjust stock and record a movement |
| GET | `/api/deliveries` | List deliveries and line items |
| POST | `/api/deliveries/DEL-1042/scan-results` | Save reviewed scan values |
| POST | `/api/confirm` | Confirm a delivery transactionally |
| GET | `/api/alerts` | Stock, expiry, barcode, and delivery alerts |
| GET | `/api/reports/summary` | Category and valuation summary |

Example: create a product.

```bash
curl -X POST http://127.0.0.1:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{"id":"P04","sku":"TE-001","name":"Green Tea","category":"Drinks","qty":20,"min":10,"price":1.5,"cost":0.8}'
```

Example: confirm a delivery after reviewing discrepancies.

```bash
curl -X POST http://127.0.0.1:5000/api/confirm \
  -H "Content-Type: application/json" \
  -d '{"delivery_id":"DEL-1042","acknowledge_discrepancies":true}'
```

Confirmation rejects low-confidence items until accepted, requires acknowledgement when detected and expected quantities differ, and prevents a delivery from being applied twice.

## Dashboard/API integration

When served from the same origin as the API, the dashboard requests `GET /api/state` on startup. For other deployments, configure a deliberate same-origin proxy or CORS policy. The current dashboard confirmation handler still updates browser memory before it receives the API result; check the response and refresh `/api/state` before relying on it for live inventory.

## Demo limitations and next steps

- No real AI model, authentication, or role-based permissions
- Sample inventory and supplier records are for demonstration only
- Add production database configuration, migrations, HTTPS, rate limits, structured logs, backups, and monitoring before deployment
- Validate and limit image uploads and store files outside the web root
- Add automated tests and an audit trail for inventory changes
- Add barcode/OCR integration and live inventory synchronization when required
