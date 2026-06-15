# Claws & Crystals

Django e-commerce site for handcrafted Indian jewellery.

## Setup

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
python3 manage.py migrate
python3 manage.py seed_homepage
python3 manage.py runserver
```

### Frontend CSS (Tailwind)

Tailwind is built locally (not loaded from CDN). After changing templates or `tailwind.config.js`:

```bash
npm install && npm run build:css
```

Output is written to `static/css/tailwind.css`.

## Razorpay payment setup (test mode)

1. Copy your test API keys from [Razorpay Dashboard → API Keys](https://dashboard.razorpay.com/app/keys) into `.env`:

```
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...
```

2. Start the dev server:

```bash
python3 manage.py runserver
```

3. Expose localhost for webhooks (required for `payment.captured`):

```bash
ngrok http 8000
```

4. In Razorpay Dashboard → Webhooks, create a webhook:
   - URL: `https://<your-ngrok-subdomain>.ngrok.io/orders/webhook/razorpay/`
   - Event: `payment.captured`
   - Copy the webhook secret into `RAZORPAY_WEBHOOK_SECRET` in `.env`

5. Test the checkout flow:
   - Register / log in
   - Add a published product to cart
   - Go to checkout → fill shipping details → **Continue to Payment**
   - Click **Pay** and use Razorpay test card: `4111 1111 1111 1111` (any future expiry, any CVV)
   - Confirm redirect to order success page
   - Verify in admin: order `payment_status` = Paid, cart cleared

6. Check webhook delivery in Razorpay Dashboard → Webhooks → Logs.

## Payment flow

1. Checkout creates an unpaid order (cart is kept until payment succeeds).
2. Payment page opens Razorpay Standard Checkout modal.
3. On success, the browser POSTs to `/orders/payment/verify/` for signature verification.
4. Razorpay also sends `payment.captured` to `/orders/webhook/razorpay/` (idempotent backup).
5. Unpaid orders can be completed from **My Orders** via **Complete Payment** or **Retry Payment**.

## User profile

Logged-in users can manage their account at `/accounts/profile/`:

- **Overview** — stats, recent orders, saved addresses
- **Edit Profile** — name and email
- **Addresses** — add, edit, delete, set default
- **Change Password** — secure password update (session preserved)
- **Preferences** — phone number and notification settings

Click your username in the navbar to open your profile.

## Email setup

**Development (no SMTP):** Leave `EMAIL_HOST` unset in `.env`. Django prints all emails to the terminal console automatically.

**Production SMTP** — add to `.env` (see `.env.example`):

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Claws & Crystals <noreply@clawsandcrystals.in>
ADMIN_ORDER_EMAIL=admin@example.com
SITE_URL=https://yourdomain.com
SITE_NAME=Claws & Crystals
```

For Gmail, use an [App Password](https://myaccount.google.com/apppasswords) (not your regular Gmail password). You need 2-Step Verification enabled on the Google account first. The app password is a 16-character code like `abcd efgh ijkl mnop` — paste it without spaces in `EMAIL_HOST_PASSWORD`.

**macOS SSL note:** If you see `CERTIFICATE_VERIFY_FAILED`, the project uses a certifi-backed SMTP backend automatically when `EMAIL_HOST` is set. Restart the dev server after pulling that change.

### Troubleshooting

| Error | Fix |
|-------|-----|
| `CERTIFICATE_VERIFY_FAILED` | Restart server after update; or run `/Applications/Python 3.14/Install Certificates.command` |
| `Username and Password not accepted` | Use a Gmail **App Password**, not your login password |
| Emails print to terminal | Remove or comment out `EMAIL_HOST` in `.env` for console mode |

### What sends email

| Trigger | Recipient |
|---------|-----------|
| Payment confirmed | Customer + admin |
| Order shipped / delivered / cancelled | Customer (if opted in) |
| Customer cancels order | Customer + admin |
| Contact form submitted | Admin |
| Password reset requested | User |
| Stock drops to 5 or below | Admin |

Customers can disable order emails in **Profile → Preferences** (`receive_order_updates`).

### Maintenance

Cancel abandoned unpaid orders (default: older than 48 hours):

```bash
python3 manage.py cancel_unpaid_orders
python3 manage.py cancel_unpaid_orders --hours 24
```

## Design system

All brand colors and fonts are defined in one file:

[`static/css/design-tokens.css`](static/css/design-tokens.css)

Edit the `:root` variables there to retheme the site. Tailwind utilities (`bg-gold`, `text-brown`, etc.) and component styles (`btn-primary`, `glass-card`, forms) all read from the same tokens.

If you change font families, also update the Google Fonts link in [`templates/base.html`](templates/base.html).

## Tests

```bash
python3 manage.py test
```
