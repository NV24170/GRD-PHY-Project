# GRD-PHY-Project

## Project Title
AI SmartScan — Inventory Dashboard (Demo)

## Overview
This project is a front-end prototype for a smart inventory management dashboard designed to simulate stock monitoring, delivery verification, and AI-assisted scan review in a retail or warehouse environment.

The application presents a clean dashboard interface with product inventory tracking, low-stock alerts, recent movement history, and a simulated AI scan workflow for checking incoming deliveries. The data is demo-only and intentionally not connected to a real AI model or live backend.

## Purpose
The app demonstrates how a business could:
- Monitor inventory across multiple product categories
- Identify low-stock and out-of-stock items quickly
- Review simulated scan results before confirming deliveries
- Track supplier delivery status and discrepancies
- Visualize product movement and stock alerts
- Generate a simple reporting view for operational oversight

## Key Features
- Overview dashboard with summary metrics
- Product inventory table with search, sort, and filtering
- Product detail modal with stock information and recent movements
- AI Scan review area with confidence percentages and simulated detections
- Delivery verification workflow for discrepancy checks
- Alerts for low stock, expired items, missing barcodes, and unverified deliveries
- Reporting view for category summaries and movement history
- Responsive layout for desktop and smaller screens

## Application Structure
The project currently contains the following main files:

- README.md — project documentation and setup guide
- AI SmartScan — Inventory Dashboard (Demo).html — complete dashboard UI, embedded styles, simulated data, and application logic

## Tech Stack
This project is built using:
- HTML5
- CSS3
- JavaScript (vanilla ES6)
- No external dependencies required for the demo UI

## How It Works
The app is implemented as a single-page dashboard in one HTML file. It contains:
- Embedded product catalog data
- Simulated inventory and movement records
- Delivery and scan result arrays
- Front-end logic for navigation, filtering, sorting, and modal details
- Demo status updates for stock and verification actions

The "AI Scan" and "Verification" flows are not connected to a real model. They simulate an AI-assisted quality check so the workflow can be demonstrated without production infrastructure.

## Project Flow
1. Open the dashboard
2. View the summary metrics on the Overview page
3. Browse or search products in the Inventory page
4. Use the AI Scans page to review scan confidence and discrepancies
5. Verify or reject the simulated delivery on the Verification page
6. Review stock alerts and reports for operational insights

## Running the Project
Because this is a static HTML demo, there are two simple ways to run it:

### Option 1: Open directly in a browser
- Open the file named "AI SmartScan — Inventory Dashboard (Demo).html" in any modern browser.
- The dashboard should load and run without additional setup.

### Option 2: Serve locally
From the project folder, run:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/
```

## Demo Data Notes
The project uses simulated inventory values and fake supplier records. Examples include:
- Product quantities and stock thresholds
- Inventory movement history
- Delivery statuses
- AI scan confidence values
- Expiration and low-stock alerts

These values are intended for demonstration only and reset with the browser session unless connected to a real backend later.

## Functional Areas

### Overview
Displays key stock metrics such as:
- Total products
- Units in stock
- Low or out-of-stock items
- Awaiting verification deliveries
- Inventory value estimate

### Inventory
Provides a searchable and filterable catalog of products including:
- Product name
- SKU
- Category
- Brand
- Quantity
- Minimum threshold
- Price and value
- Current stock status

### AI Scans
Simulates a review page for incoming scanned items where:
- Expected counts are compared with detected quantities
- Confidence values are displayed
- Items below a threshold are highlighted for manual review
- Results can be accepted before final verification

### Verification
Allows the user to confirm whether a delivery should be added to stock. This page checks:
- Whether scan discrepancies were reviewed
- Whether uncertain results remain unresolved
- Whether confirmation is allowed before updating inventory

### Alerts
Shows items that require attention such as:
- Low stock
- Out-of-stock products
- Unverified deliveries
- Missing barcodes
- Items nearing expiry

### Reports
Summarizes data by category and provides a movement report for operational reviews.

## Limitations
This demo has several intentional limitations:
- No real AI model integration
- No persistent database or authentication
- No backend API for saving inventory state
- No production-grade validation or security controls
- Data is embedded directly in the browser

## Future Enhancements
Potential next steps for turning this prototype into a production-ready application include:
- Connect to a real database and REST API
- Add barcode or OCR scanning integration
- Implement live inventory sync across devices
- Add user authentication and role-based permissions
- Support CSV/Excel import and export
- Add notifications and email/SMS alerts
- Generate more detailed PDF or Excel reports
- Add audit logs and delivery history tracking

## Suggested Roadmap
### Phase 1: Prototype polish
- Improve dashboard UX and accessibility
- Refine metrics, filters, and reporting layout
- Add more realistic inventory workflows

### Phase 2: Real backend
- Build API endpoints for products, stock movements, and deliveries
- Persist data in a database
- Add validation and transaction-safe updates

### Phase 3: AI integration
- Connect scanning to an OCR / image recognition model
- Add confidence-based decision rules
- Enforce review workflow for uncertain matches

### Phase 4: Production readiness
- Add user accounts, permissions, and audit trails
- Deploy to a hosting environment
- Add testing and CI/CD pipelines

## Contribution Guidelines
This project is currently structured as a prototype/demo. If you plan to extend it:
- Keep the UI and logic easy to understand
- Maintain the demo-friendly data structure
- Document any new features or workflows
- Prefer simple, modular JavaScript patterns where possible

## License
This project does not currently include a formal license file. If the project is intended for public or team use, add a license such as MIT or Apache 2.0 before distribution.

## Summary
GRD-PHY-Project is a demo inventory intelligence dashboard that showcases how a business could review stock health, verify deliveries, and process AI-assisted scanning workflows in a single, visually clear interface. It serves as a strong prototype foundation for future development into a real inventory management platform.
