# AuctionHub — Commerce

A Django auction site (CS50 "Commerce") where users can create listings, bid,
comment, and keep a watchlist — with a clean, responsive Bootstrap 5 interface.

## Features

- **Active Listings** — uniform, responsive card grid with a fixed 200px
  `object-fit: cover` thumbnail and action buttons aligned on one line.
- **Categories** — icon cards in a responsive grid (2 / 3 / 4 columns).
- **Create Listing** — centered, compact form with image upload *or* image URL
  and a live preview.
- **Watchlist** — quick remove (corner `×` button and a footer `Remove` button).
- **Listing detail** — bidding, auction close, comments, watch toggle.
- Login / register with Django's built-in auth.

## Requirements

- Python 3.10+
- Django 3.x or 4.x, Pillow (for image uploads)

```bash
pip install django pillow
```

## Run locally

```bash
git clone <this-repo-url>
cd commerce
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install django pillow

python manage.py migrate
python manage.py createsuperuser   # optional: manage categories in /admin
python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

Add categories from the admin panel at `/admin/` — the icon on the categories
page is picked automatically from the category name (see
`auctions/templatetags/auction_extras.py`).

## Project layout

```
commerce/
├── manage.py
├── commerce/               # project settings & urls
└── auctions/
    ├── models.py           # Category, Listing, Bid, Comment
    ├── views.py
    ├── urls.py
    ├── static/auctions/styles.css
    ├── templatetags/       # category_emoji filter
    └── templates/auctions/ # layout, index, categories, watchlist, create, listing
```

## Notes

- `db.sqlite3` and `media/` are intentionally git-ignored. The app recreates
  the database with `python manage.py migrate`, and users seed their own data.
- **Not deployed here.** GitHub Pages can only serve static sites, so it cannot
  host Django. To publish it live, use a Python host such as
  [PythonAnywhere](https://www.pythonanywhere.com/),
  [Railway](https://railway.app/) or [Render](https://render.com/) — remember
  to set `DEBUG = False`, a secret `SECRET_KEY` from an env var, and your
  `ALLOWED_HOSTS` before going public.
