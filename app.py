from datetime import date, datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///smartscan.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    sku = db.Column(db.String(32), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    brand = db.Column(db.String(80), nullable=False, default="")
    qty = db.Column(db.Integer, nullable=False, default=0)
    min_qty = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False, default=0)
    cost = db.Column(db.Float, nullable=False, default=0)
    size = db.Column(db.String(40), default="")
    supplier = db.Column(db.String(120), default="")
    expiry = db.Column(db.Date, nullable=True)
    barcode = db.Column(db.String(80), unique=True, nullable=True)

    __table_args__ = (
        CheckConstraint("qty >= 0", name="ck_product_qty_nonnegative"),
        CheckConstraint("min_qty >= 0", name="ck_product_min_nonnegative"),
        CheckConstraint("price >= 0 AND cost >= 0", name="ck_product_prices_nonnegative"),
    )

    def as_dict(self):
        return {
            "id": self.id, "sku": self.sku, "name": self.name,
            "cat": self.category, "brand": self.brand, "qty": self.qty,
            "min": self.min_qty, "price": self.price, "cost": self.cost,
            "size": self.size, "supplier": self.supplier,
            "exp": self.expiry.isoformat() if self.expiry else "",
            "barcode": self.barcode or ""
        }


class Delivery(db.Model):
    id = db.Column(db.String(24), primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    supplier = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Awaiting verification")
    items = db.relationship("DeliveryItem", backref="delivery", cascade="all, delete-orphan")


class DeliveryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.String(24), db.ForeignKey("delivery.id"), nullable=False)
    product_id = db.Column(db.String(16), db.ForeignKey("product.id"), nullable=False)
    expected_qty = db.Column(db.Integer, nullable=False)
    detected_qty = db.Column(db.Integer, nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    accepted = db.Column(db.Boolean, nullable=False, default=False)
    product = db.relationship("Product")

    __table_args__ = (
        CheckConstraint("expected_qty >= 0", name="ck_expected_qty_nonnegative"),
        CheckConstraint("detected_qty IS NULL OR detected_qty >= 0", name="ck_detected_qty_nonnegative"),
    )


class StockMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    product_id = db.Column(db.String(16), db.ForeignKey("product.id"), nullable=False)
    change = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    reference = db.Column(db.String(40), nullable=True)
    product = db.relationship("Product")


def delivery_dict(d):
    return {
        "id": d.id, "date": d.date.isoformat(), "sup": d.supplier,
        "status": d.status,
        "items": [{
            "product_id": i.product_id,
            "expected": i.expected_qty,
            "detected": i.detected_qty,
            "confidence": i.confidence,
            "accepted": i.accepted
        } for i in d.items]
    }


def seed_demo_data():
    if Product.query.first():
        return
    rows = [
        ("P01","OC-001","Oman Chips","Snacks","Oman Chips",0,0,0,0,"","","",""),
        ("P02","OR-001","Oreo","Biscuits","Oreo",0,0,0,0,"","","",""),
        ("P03","WB-001","Water Bottle","Drinks","",0,0,0,0,"","","",""),
    ]
    for r in rows:
        expiry = date.fromisoformat(r[11]) if r[11] else None
        db.session.add(Product(id=r[0], sku=r[1], name=r[2], category=r[3], brand=r[4],
            qty=r[5], min_qty=r[6], price=r[7], cost=r[8], size=r[9], supplier=r[10],
            expiry=expiry, barcode=r[12] or None))
    deliveries = [
        Delivery(id="DEL-1042", date=date(2026,10,20), supplier="Snackline Ltd", status="Awaiting verification"),
    ]
    db.session.add_all(deliveries)
    db.session.flush()
    for pid, exp, det, conf in [("P01",100,94,.93),("P02",60,60,.91),("P03",40,40,.72)]:
        db.session.add(DeliveryItem(delivery_id="DEL-1042", product_id=pid,
            expected_qty=exp, detected_qty=det, confidence=conf))
    db.session.commit()


@app.get("/")
def dashboard():
    return send_from_directory(
        app.root_path, "AI SmartScan — Inventory Dashboard (Demo).html"
    )


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/state")
def state():
    products = Product.query.order_by(Product.name).all()
    movements = StockMovement.query.order_by(StockMovement.created_at.desc()).limit(100).all()
    deliveries = Delivery.query.order_by(Delivery.date.desc()).all()
    pending = Delivery.query.filter(Delivery.status.like("Awaiting%")).first()
    scan = []
    if pending:
        scan = [{
            "pid": i.product_id, "exp": i.expected_qty,
            "det": i.detected_qty if i.detected_qty is not None else i.expected_qty,
            "conf": i.confidence if i.confidence is not None else 0,
            "ok": i.accepted
        } for i in pending.items]
    return jsonify({
        "products": [p.as_dict() for p in products],
        "movements": [[m.created_at.date().isoformat(), m.product_id, f"{m.change:+d}",
                       f"{m.reason}" + (f" {m.reference}" if m.reference else "")]
                      for m in movements],
        "deliveries": [{"id": d.id, "date": d.date.isoformat(), "sup": d.supplier,
                        "status": d.status} for d in deliveries],
        "scan": scan,
        "confirmed": bool(pending and pending.status.startswith("Verified"))
    })


@app.get("/api/products")
def list_products():
    query = Product.query
    category = request.args.get("category")
    search = request.args.get("q", "").strip()
    if category:
        query = query.filter_by(category=category)
    if search:
        pattern = f"%{search}%"
        query = query.filter(db.or_(Product.name.ilike(pattern), Product.sku.ilike(pattern),
                                    Product.brand.ilike(pattern), Product.barcode.ilike(pattern)))
    return jsonify([p.as_dict() for p in query.order_by(Product.name).all()])


@app.post("/api/products")
def create_product():
    data = request.get_json(silent=True) or {}
    required = ("id", "sku", "name", "category")
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400
    try:
        p = Product(
            id=data["id"], sku=data["sku"], name=data["name"], category=data["category"],
            brand=data.get("brand", ""), qty=int(data.get("qty", 0)),
            min_qty=int(data.get("min", 0)), price=float(data.get("price", 0)),
            cost=float(data.get("cost", 0)), size=data.get("size", ""),
            supplier=data.get("supplier", ""), barcode=data.get("barcode") or None,
            expiry=date.fromisoformat(data["exp"]) if data.get("exp") else None
        )
        db.session.add(p)
        db.session.commit()
        return jsonify(p.as_dict()), 201
    except (ValueError, TypeError):
        db.session.rollback()
        return jsonify({"error": "Invalid numeric value or date"}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Product ID, SKU, or barcode already exists"}), 409


@app.patch("/api/products/<product_id>")
def update_product(product_id):
    p = db.session.get(Product, product_id)
    if not p:
        return jsonify({"error": "Product not found"}), 404
    data = request.get_json(silent=True) or {}
    fields = {"sku":"sku", "name":"name", "category":"category", "cat":"category",
              "brand":"brand", "qty":"qty", "min":"min_qty", "price":"price",
              "cost":"cost", "size":"size", "supplier":"supplier", "barcode":"barcode"}
    try:
        for key, attr in fields.items():
            if key in data:
                value = data[key]
                if attr in ("qty", "min_qty"):
                    value = int(value)
                elif attr in ("price", "cost"):
                    value = float(value)
                elif attr == "barcode":
                    value = value or None
                setattr(p, attr, value)
        if "exp" in data:
            p.expiry = date.fromisoformat(data["exp"]) if data["exp"] else None
        db.session.commit()
        return jsonify(p.as_dict())
    except (ValueError, TypeError):
        db.session.rollback()
        return jsonify({"error": "Invalid field value"}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "SKU or barcode already exists"}), 409


@app.post("/api/stock-adjustments")
def stock_adjustment():
    data = request.get_json(silent=True) or {}
    p = db.session.get(Product, data.get("product_id", ""))
    if not p:
        return jsonify({"error": "Product not found"}), 404
    try:
        change = int(data["change"])
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "'change' must be an integer"}), 400
    if change == 0 or p.qty + change < 0:
        return jsonify({"error": "Change must be non-zero and stock cannot become negative"}), 400
    p.qty += change
    db.session.add(StockMovement(product_id=p.id, change=change,
        reason=(data.get("reason") or "Manual adjustment")[:200],
        reference=(data.get("reference") or "")[:40] or None))
    db.session.commit()
    return jsonify({"product": p.as_dict(), "new_qty": p.qty})


@app.get("/api/deliveries")
def list_deliveries():
    return jsonify([delivery_dict(d) for d in Delivery.query.order_by(Delivery.date.desc()).all()])


@app.post("/api/deliveries/<delivery_id>/scan-results")
def save_scan_results(delivery_id):
    d = db.session.get(Delivery, delivery_id)
    if not d:
        return jsonify({"error": "Delivery not found"}), 404
    if d.status.startswith("Verified"):
        return jsonify({"error": "Verified deliveries cannot be edited"}), 409
    data = request.get_json(silent=True) or {}
    items = data.get("items")
    if not isinstance(items, list):
        return jsonify({"error": "'items' must be a list"}), 400
    by_product = {i.product_id: i for i in d.items}
    try:
        for row in items:
            item = by_product.get(row.get("product_id"))
            if not item:
                return jsonify({"error": f"Product {row.get('product_id')} is not on this delivery"}), 400
            detected = int(row["detected_qty"])
            confidence = float(row.get("confidence", item.confidence or 0))
            if detected < 0 or not 0 <= confidence <= 1:
                return jsonify({"error": "Detected quantity must be >= 0 and confidence between 0 and 1"}), 400
            item.detected_qty = detected
            item.confidence = confidence
            if "accepted" in row:
                item.accepted = bool(row["accepted"])
        db.session.commit()
        return jsonify(delivery_dict(d))
    except (ValueError, TypeError, KeyError):
        db.session.rollback()
        return jsonify({"error": "Invalid scan result values"}), 400


@app.post("/api/confirm")
def confirm_delivery():
    data = request.get_json(silent=True) or {}
    delivery_id = data.get("delivery_id", "DEL-1042")
    d = db.session.get(Delivery, delivery_id)
    if not d:
        return jsonify({"error": "Delivery not found"}), 404
    if d.status.startswith("Verified"):
        return jsonify({"error": "Delivery has already been confirmed"}), 409
    if not d.items:
        return jsonify({"error": "Delivery has no items"}), 400

    discrepancies = []
    uncertain = []
    for item in d.items:
        detected = item.detected_qty
        if detected is None:
            return jsonify({"error": f"Missing detected quantity for {item.product_id}"}), 400
        if item.confidence is not None and item.confidence < 0.8 and not item.accepted:
            uncertain.append(item.product_id)
        if detected != item.expected_qty:
            discrepancies.append(item.product_id)
    if uncertain:
        return jsonify({"error": "Low-confidence scan results must be reviewed",
                        "products": uncertain}), 409
    if discrepancies and not data.get("acknowledge_discrepancies", False):
        return jsonify({"error": "Manual acknowledgement required for discrepancies",
                        "products": discrepancies}), 409

    # Apply all inventory changes atomically, exactly once.
    try:
        for item in d.items:
            item.product.qty += item.detected_qty
            db.session.add(StockMovement(
                product_id=item.product_id, change=item.detected_qty,
                reason="Delivery received", reference=d.id
            ))
        d.status = "Verified (discrepancy)" if discrepancies else "Verified"
        db.session.commit()
    except Exception:
        db.session.rollback()
        app.logger.exception("Could not confirm delivery")
        return jsonify({"error": "Delivery confirmation failed; no changes were saved"}), 500
    return jsonify({"message": "Delivery confirmed", "delivery": delivery_dict(d)})


@app.get("/api/alerts")
def alerts():
    today = date.today()
    products = Product.query.all()
    low = [p.as_dict() for p in products if 0 < p.qty <= p.min_qty]
    out = [p.as_dict() for p in products if p.qty == 0]
    missing_barcode = [p.as_dict() for p in products if not p.barcode]
    expiring = [p.as_dict() for p in products if p.expiry and 0 <= (p.expiry - today).days <= 30]
    pending = [{"id": d.id, "supplier": d.supplier, "status": d.status}
               for d in Delivery.query.filter(Delivery.status.like("Awaiting%")).all()]
    return jsonify({"low_stock": low, "out_of_stock": out,
                    "missing_barcode": missing_barcode, "expiring_soon": expiring,
                    "unverified_deliveries": pending})


@app.get("/api/reports/summary")
def report_summary():
    products = Product.query.all()
    categories = {}
    for p in products:
        row = categories.setdefault(p.category, {
            "category": p.category, "products": 0, "units": 0,
            "cost_value": 0.0, "retail_value": 0.0
        })
        row["products"] += 1
        row["units"] += p.qty
        row["cost_value"] += p.qty * p.cost
        row["retail_value"] += p.qty * p.price
    return jsonify({
        "categories": list(categories.values()),
        "total_products": len(products),
        "total_units": sum(p.qty for p in products),
        "retail_value": round(sum(p.qty * p.price for p in products), 2),
        "cost_value": round(sum(p.qty * p.cost for p in products), 2)
    })


with app.app_context():
    db.create_all()
    seed_demo_data()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
