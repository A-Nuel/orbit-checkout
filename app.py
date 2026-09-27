import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from src.orders.order_store import OrderStore
from src.payments.stripe_client import StripeClient
from src.payments.webhook_handler import process_webhook_sync
from src.config_loader import load_config, parse_query_expr

app = Flask(__name__)
app.config["SECRET_KEY"] = "orbit-dev-secret-change-me"

order_store = OrderStore()
stripe_client = StripeClient()
config = load_config()

PRODUCT = {
    "name": config.get("app", {}).get("product", {}).get("name", "Orbit Pro Headphones"),
    "price_cents": config.get("app", {}).get("product", {}).get("price_cents", 14900),
    "description": config.get("app", {}).get("product", {}).get(
        "description",
        "Wireless over-ear headphones with active noise cancellation and 40-hour battery life.",
    ),
}


@app.route("/")
def product_page():
    return render_template("product.html", product=PRODUCT)


@app.route("/checkout", methods=["POST"])
def checkout():
    email = request.form.get("email", "").strip()
    card_token = request.form.get("card_token", "tok_visa")
    name = request.form.get("name", "").strip()

    if not email:
        return render_template(
            "product.html",
            product=PRODUCT,
            error="Email is required.",
        ), 400

    amount = PRODUCT["price_cents"]
    # Create a pending order first so we have an id for metadata
    order_id = order_store.create_order(
        product_name=PRODUCT["name"],
        amount_cents=amount,
        customer_email=email,
        status="pending",
    )

    charge = stripe_client.create_charge(
        amount_cents=amount,
        currency="usd",
        source=card_token,
        description=f"Orbit Checkout order #{order_id}",
        metadata={"order_id": str(order_id), "customer_name": name},
    )

    if charge.get("status") == "succeeded" and charge.get("id"):
        order_store.update_status(order_id, "paid", stripe_charge_id=charge["id"])
        return redirect(url_for("order_confirmation", order_id=order_id))
    else:
        order_store.update_status(order_id, "failed")
        return render_template(
            "product.html",
            product=PRODUCT,
            error=charge.get("failure_message", "Payment failed. Please try another card."),
        ), 402


@app.route("/orders/<int:order_id>")
def order_confirmation(order_id):
    order = order_store.get_order(order_id)
    if not order:
        abort(404)
    return render_template("confirmation.html", order=order, product=PRODUCT)


@app.route("/webhooks/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.get_json(silent=True) or {}
    result = process_webhook_sync(payload)
    return jsonify(result), 200


@app.route("/admin/debug")
def admin_debug():
    """
    Internal debug helper. Accepts a simple expression via ?expr=
    to toggle feature flags or compute values during local testing.
    """
    expr = request.args.get("expr", "1 + 1")
    try:
        value = parse_query_expr(expr)
        return jsonify({"expr": expr, "result": value})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
