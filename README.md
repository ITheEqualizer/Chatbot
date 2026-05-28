# Chatbot: A Lightweight Q&A Chatbot

A lightweight Django Q&A chatbot powered by FastText embeddings and cosine-similarity search.
It matches a user's message against a database of question/answer pairs and returns the closest
answer, or a fallback message when nothing is similar enough. It supports English and Persian
through separate pretrained models, selectable at runtime.

## How it works

1. Each `QAPair` (question + answer) stores a **precomputed** FastText embedding of its question,
   generated automatically on save and held in the database as raw `float32` bytes.
2. On startup the app lazily builds a single **pre-normalized in-memory matrix** of all question
   embeddings. A chat request then costs **one** embedding (the incoming message) plus **one**
   matrix-vector product — not one embedding per stored question per request.
3. The in-memory matrix is rebuilt automatically (via `post_save`/`post_delete` signals) whenever
   a `QAPair` is added, edited, or deleted, so it stays consistent without restarting the server.
4. If the best cosine similarity is below `SIMILARITY_THRESHOLD`, a fallback reply is returned.

> **Why this matters:** the matching cost is independent of corpus size in embedding terms — adding
> more FAQs does not multiply the per-request embedding work.

## Tech stack

| Component     | Version / role                                              |
|---------------|-------------------------------------------------------------|
| Python        | 3.11+                                                       |
| Django        | 5.2.7 — web framework, admin, ORM                          |
| FastText      | `fasttext-wheel` 0.9.2 — word embeddings (prebuilt wheel)  |
| NumPy         | 1.24.3 — vectorized similarity search                      |
| hazm          | 0.10.0 — Persian text normalization/tokenization (optional)|
| Database      | SQLite (default); any Django-supported DB for production   |
| Frontend      | HTML + Bulma (CDN) + vanilla JS (`fetch`)                  |

## Getting started

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/ITheEqualizer/Chatbot.git
cd Chatbot
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Download a pretrained model

Place the `.bin` file in the project root (model files are gitignored — they are large):

- **English** → save as `ChatBot.bin`:
  [download](https://drive.google.com/file/d/1u17AHiicxmfeDbvTyuew60SjXCr19UCu/view)
- **Persian** → save as `ChatBot_Persian.bin`:
  [download](https://drive.google.com/file/d/1jIMJC03SYYBqsH5YjZ84w-T2J-kRRGTp/view)

### 3. Configure environment (optional for local dev)

Copy `.env.example` and export the variables (or set them in your shell / process manager):

```bash
cp .env.example .env
```

Sensible local defaults are built in, so you can skip this for development.

### 4. Migrate, create an admin user, and run

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Chat UI: http://127.0.0.1:8000/
- Admin (add FAQs): http://127.0.0.1:8000/admin/

After adding FAQ entries in the admin, their embeddings are computed automatically on save. If you
imported rows in bulk or changed the model, run `python manage.py rebuild_embeddings` once.

## Configuration

All settings are read from environment variables in [`chatbot/settings.py`](chatbot/settings.py):

| Variable                | Default                 | Purpose                                                        |
|-------------------------|-------------------------|----------------------------------------------------------------|
| `DJANGO_SECRET_KEY`     | insecure dev key        | **Set a real secret in production.**                           |
| `DJANGO_DEBUG`          | `True`                  | Set `False` in production.                                     |
| `DJANGO_ALLOWED_HOSTS`  | `localhost,127.0.0.1`   | Comma-separated allowed hostnames.                             |
| `CHATBOT_LANGUAGE`      | `en`                    | `en` or `fa` — picks the default model and preprocessor.       |
| `MODEL_PATH`            | follows `CHATBOT_LANGUAGE` | Override the FastText model file path.                      |
| `SIMILARITY_THRESHOLD`  | `0.85`                  | Minimum cosine similarity (0–1) to return an answer.           |
| `BOT_LOG_LEVEL`         | `INFO`                  | Log level for the `bot` logger.                                |

## Persian support

Set `CHATBOT_LANGUAGE=fa` (with `ChatBot_Persian.bin` present). This selects both the Persian model
and the hazm-based preprocessor in [`bot/persian_process.py`](bot/persian_process.py), and the
English/Persian content of your `QAPair` entries should match the selected language. Embeddings are
tied to the active model, so after switching languages run:

```bash
python manage.py rebuild_embeddings
```

## Testing

```bash
python manage.py test bot
```

The suite mocks FastText, so it runs **without** the model file or the `fasttext` package installed.
It covers preprocessing, cosine math, embedding storage, cache invalidation, the chat endpoint
(matching, threshold fallback, `400`/`405` handling), and CSRF enforcement.

## Project structure

```text
chatbot/            Django project (settings, urls, wsgi/asgi)
bot/
  models.py         QAPair model (question, answer, embedding_vector) + save() override
  embedding.py      Lazy model loading, language-aware preprocessing, (de)serialization
  cache.py          EmbeddingCache: normalized in-memory matrix + vectorized search
  views.py          index page + chat_api endpoint
  apps.py           Connects cache-invalidation signals on startup
  persian_process.py  Persian preprocessing (hazm)
  management/commands/rebuild_embeddings.py   Recompute/store all embeddings
  migrations/       Committed schema + embedding backfill
  templates/bot/index.html   Chat UI
  static/bot/chat.js         Frontend logic (sends CSRF token)
  tests.py          Test suite
manage.py
requirements.txt
.env.example        Documented environment variables
```

## Deployment notes

- Set `DJANGO_DEBUG=False`, a real `DJANGO_SECRET_KEY`, and `DJANGO_ALLOWED_HOSTS`.
- Run `python manage.py collectstatic` (output goes to `staticfiles/`, which is gitignored).
- Ship the FastText `.bin` model with your deployment (bake into the image or fetch on boot).
- Serve with gunicorn/uWSGI behind HTTPS, e.g. `gunicorn chatbot.wsgi`.
- **Upgrading an older clone** that already had a `db.sqlite3` (created before migrations were
  committed): run `python manage.py migrate --fake-initial`, then `python manage.py rebuild_embeddings`.

## License

MIT — see [`LICENSE`](LICENSE).

## Acknowledgments

- Django, for the framework and admin.
- Facebook Research, for FastText.
- The hazm project, for Persian NLP tooling.

---

# چت‌بات سبک پرسش و پاسخ

یک چت‌بات سبک مبتنی بر Django که با استفاده از جاسازی‌های FastText و شباهت کسینوسی کار می‌کند.
پیام کاربر را با مجموعه‌ای از جفت‌های پرسش/پاسخ مطابقت می‌دهد و نزدیک‌ترین پاسخ را برمی‌گرداند؛ اگر
شباهت کافی نباشد، یک پاسخ پیش‌فرض داده می‌شود. از انگلیسی و فارسی پشتیبانی می‌کند.

## نحوه کار

برای هر `QAPair`، جاسازی پرسش **یک بار** هنگام ذخیره محاسبه و در پایگاه‌داده نگه‌داری می‌شود. هنگام
اجرا، همهٔ این جاسازی‌ها در یک ماتریس نرمال‌شده در حافظه بارگذاری می‌شوند، بنابراین هر درخواست فقط
**یک** جاسازی (برای پیام ورودی) و **یک** ضرب ماتریسی هزینه دارد — نه یک جاسازی به ازای هر پرسش
در هر درخواست. این ماتریس هنگام افزودن/ویرایش/حذف `QAPair` به‌صورت خودکار به‌روزرسانی می‌شود.

## راه‌اندازی

```bash
git clone https://github.com/ITheEqualizer/Chatbot.git
cd Chatbot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# مدل فارسی را دانلود کرده و با نام ChatBot_Persian.bin در ریشهٔ پروژه قرار دهید
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## فعال‌سازی فارسی

متغیر محیطی `CHATBOT_LANGUAGE=fa` را تنظیم کنید (و فایل `ChatBot_Persian.bin` را قرار دهید). این
کار هم مدل فارسی و هم پیش‌پردازندهٔ مبتنی بر hazm را انتخاب می‌کند. پس از تغییر زبان یا مدل، دستور
زیر را اجرا کنید تا جاسازی‌ها بازسازی شوند:

```bash
python manage.py rebuild_embeddings
```

## پیکربندی

تنظیمات از متغیرهای محیطی خوانده می‌شوند (به `.env.example` مراجعه کنید): `DJANGO_SECRET_KEY`،
`DJANGO_DEBUG`، `DJANGO_ALLOWED_HOSTS`، `CHATBOT_LANGUAGE`، `MODEL_PATH`، `SIMILARITY_THRESHOLD`.

## آزمون

```bash
python manage.py test bot
```

آزمون‌ها مدل FastText را شبیه‌سازی می‌کنند و بدون نیاز به فایل مدل اجرا می‌شوند.

## مجوز

تحت مجوز MIT منتشر شده است — فایل [`LICENSE`](LICENSE) را ببینید.
