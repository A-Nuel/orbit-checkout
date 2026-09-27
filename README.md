# Orbit Checkout

A small single-product checkout demo built with Flask. It shows a product page, accepts a demo card token, creates an order in SQLite, and displays a confirmation page. Webhook handling for charge events is also stubbed in.

## Features

- Product page with checkout form
- Server-side order creation and status updates
- Mocked Stripe-like payment client (no real network calls or API keys required)
- Webhook receiver for `charge.succeeded` / `charge.failed`
- SQLite order store with a few seed records

## Requirements

- Python 3.11+
- Dependencies listed in `requirements.txt`

## Quick start

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

Then open http://127.0.0.1:5000/

Demo card tokens on the product page:

- `tok_visa` / `tok_mastercard` — succeed
- `tok_chargeDeclined` / `tok_insufficient_funds` — fail

## Project layout

```
app.py                      # Flask entry point and routes
seed.py                     # Seed sample orders into SQLite
config.yaml                 # Simple app config
requirements.txt
src/
  config_loader.py          # Loads YAML config
  orders/
    order_store.py          # SQLite order persistence
  payments/
    stripe_client.py        # Mock payment client
    webhook_handler.py      # Webhook event processing
templates/
  base.html
  product.html
  confirmation.html
static/
  styles.css
```

## Routes

| Method | Path                 | Description                |
|--------|----------------------|----------------------------|
| GET    | `/`                  | Product / checkout page    |
| POST   | `/checkout`          | Create charge + order      |
| GET    | `/orders/<id>`       | Order confirmation         |
| POST   | `/webhooks/stripe`   | Incoming webhook handler   |

## Notes

This is a demo application intended for local exploration. Payment processing is fully mocked and does not contact any external service.
