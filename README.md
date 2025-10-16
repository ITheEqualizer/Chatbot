# Chatbot: A Lightweight and Flexible Question & Answer Chatbot

## Description

This repository contains a lightweight and flexible Question & Answer (Q&A) chatbot built using Django and powered by FastText embeddings for semantic similarity search. The chatbot is designed to handle user queries by matching them against a database of predefined FAQs, providing quick and relevant responses. It is ideal for applications such as customer support, knowledge bases, trivia bots, or any scenario requiring automated responses based on natural language understanding.

The system supports both English and Persian languages through separate pretrained models. The core logic uses cosine similarity with a configurable threshold (default: 0.7) to determine the best matching answer. If no match is found above the threshold, a fallback response is provided.

The repository includes all necessary code for the Django application, templates, static files, and configuration details. Note that the pretrained model files must be downloaded separately and placed in the root directory.

## Key Features

- **Fast Response Times**: Leverages FastText embeddings for efficient semantic search.
- **Django Integration**: Seamlessly integrates with Django for web-based deployment and admin management.
- **Semantic Matching**: Uses cosine similarity to find the most relevant FAQ entry.
- **Customizable**: Easily adjust similarity thresholds, model paths, and other settings.
- **Minimalist Interface**: Clean web-based chat UI with real-time updates via JavaScript.
- **Language Support**: Compatible with English and Persian via dedicated pretrained models.
- **No Bloat**: Lightweight design with minimal dependencies.
- **Logging**: Includes debug logging for development and troubleshooting.
- **Admin Panel**: Manage FAQs through Django's built-in admin interface.
- **Test Suite**: Basic unit tests for core functionality.

## Tech Stack

| Component      | Version/Description                          |
|----------------|----------------------------------------------|
| Django        | 4.2.7 - Web framework for backend logic.    |
| FastText      | 0.9.2 (via fasttext-wheel) - For embeddings and semantic similarity. |
| NumPy         | 1.24.3 - Numerical computations.            |
| scikit-learn  | 1.3.0 - Cosine similarity calculations.     |
| Python        | 3.8+ - Core programming language.           |
| Database      | SQLite (default) or PostgreSQL for production. |
| Frontend      | HTML, CSS, JavaScript - Minimalist chat interface. |

## Getting Started

### Prerequisites

- Python 3.8 or higher installed.
- A virtual environment is recommended to isolate dependencies.
- Access to the Django admin requires creating a superuser (via `python manage.py createsuperuser`).

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/ITheEqualizer/Chatbot.git
   cd Chatbot
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Download the pretrained model:
   - **English Version**: Download from [this link](https://drive.google.com/file/d/1u17AHiicxmfeDbvTyuew60SjXCr19UCu/view?usp=drive_link), rename the file to `ChatBot.bin`, and place it in the root directory of the project.
   - **Persian Version**: Download from [this link](https://drive.google.com/file/d/1jIMJC03SYYBqsH5YjZ84w-T2J-kRRGTp/view?usp=drive_link), rename the file to `ChatBot_Persian.bin`, and place it in the root directory of the project.
   
   Note: For Persian support, ensure your FAQ entries in the database are in Persian for optimal performance.

5. Apply database migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Collect static files:
   ```
   python manage.py collectstatic --noinput
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```
   Access the chatbot at `http://127.0.0.1:8000/`. Add FAQs via the admin panel at `http://127.0.0.1:8000/admin/` (login required).

### Troubleshooting

- If the model fails to load, verify the file path and permissions.
- Ensure no typos in questions/answers when adding via admin.
- For production, set `DEBUG = False` and configure a proper database.

## Project Structure

The repository follows a standard Django project structure with the project named `chatbot`. Below is a detailed breakdown of every file and directory, including their purposes:

- **`manage.py`**: Django's command-line utility for administrative tasks like running the server, migrations, and tests.
- **`requirements.txt`**: Lists all Python dependencies with exact versions (Django==4.2.7, fasttext-wheel==0.9.2, numpy==1.24.3, scikit-learn==1.3.0).
- **`ChatBot.bin`** or **`ChatBot_Persian.bin`**: Pretrained FastText model file (downloaded separately). Provides vector embeddings for questions.
- **`chatbot/`**: Core project directory containing settings, models, views, and other configurations.
  - **`__init__.py`**: Initializes the directory as a Python package.
  - **`admin.py`**: Registers the FAQ model in the Django admin interface for easy management.
  - **`apps.py`**: Application configuration class (e.g., `ChatbotConfig` with default auto field set to `BigAutoField`).
  - **`models.py`**: Defines the `FAQ` model with fields: `question` (text), `answer` (text), `embedding_vector` (binary field for storing vectorized embeddings). Includes a `save()` override to automatically compute and store embeddings using the loaded FastText model.
  - **`views.py`**: Contains the `chat_view` function (or class-based view) that handles user queries. Loads the FastText model, vectorizes the input question, computes cosine similarity against all FAQ embeddings, and returns the best match if above the threshold (default 0.7). Falls back to a default message if no match.
  - **`urls.py`**: Defines URL patterns, mapping the root path (`''`) to the chat view (named 'chatbot').
  - **`tests.py`**: Unit tests for models and views, including tests for embedding generation, similarity calculations, and edge cases like empty queries.
  - **`settings.py`**: Project settings file, including database configuration, installed apps, middleware, templates, static files, SECRET_KEY, DEBUG mode, MODEL_PATH='ChatBot.bin' (configurable for Persian), and SIMILARITY_THRESHOLD=0.7.
  - **`wsgi.py`** and **`asgi.py`**: Entry points for WSGI/ASGI-compatible web servers (standard for deployment).
- **`templates/chatbot/`**: Directory for HTML templates.
  - **`base.html`**: Base template providing the overall HTML structure, including headers, footers, and links to CSS/JS.
  - **`index.html`**: Main chat interface template with message bubbles, input form, and loading spinner.
  - **`style.css`**: CSS file for styling the chat UI (minimalist design with bubbles, colors, and responsive layout).
- **`static/js/`**: Directory for static JavaScript files.
  - **`chat.js`**: Handles client-side logic, including AJAX (fetch) requests to the server, updating the chat UI in real-time, displaying typing indicators, and handling errors.
- **`.gitignore`**: Standard ignore file for virtual environments, pyc files, __pycache__, databases, and other temporary files.
- **`LICENSE`**: MIT License file granting permissions for use, modification, and distribution.
- **`README.md`**: This documentation file.

## Configuration

Customize the project via `chatbot/settings.py`:

- **SECRET_KEY**: Generate a secure key and set via environment variables for security.
- **DEBUG**: Set to `True` for development; `False` for production.
- **MODEL_PATH**: Defaults to `'ChatBot.bin'`. Change to `'ChatBot_Persian.bin'` for Persian support.
- **SIMILARITY_THRESHOLD**: Float value (0.7 default) for matching queries to FAQs.
- **DATABASES**: Configured for SQLite by default; update for PostgreSQL or other backends.
- Use environment variables (e.g., via `os.environ`) for sensitive settings.

## Testing

Run the test suite:
```
python manage.py test chatbot.tests
```
Tests cover model saving, view responses, similarity logic, and edge cases. Aim for at least 80% coverage using tools like coverage.py.

## Deployment

- **Heroku**: Add a `Procfile` with `web: gunicorn chatbot.wsgi` and configure environment variables.
- **Docker**: Create a `Dockerfile` for containerization (e.g., base on python:3.12, install dependencies, expose port 8000).
- **AWS/Vercel/Other**: Use gunicorn or uWSGI for production server; enable HTTPS; sanitize inputs to prevent injections.
- Ensure the model file is included in the deployment bundle.

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/new-feature`.
3. Commit changes: `git commit -m "Add new feature"`.
4. Push to the branch: `git push origin feature/new-feature`.
5. Open a Pull Request with descriptive title, details, and screenshots if applicable.

Report bugs, suggest features, or ask questions via GitHub Issues. Follow the code of conduct for respectful contributions.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- Thanks to the Django team for the robust framework.
- Credit to Facebook's FastText for embedding technology.
- Appreciation to contributors and users for feedback.

Updated: October 16, 2025

---

# چت‌بات: یک چت‌بات سبک و انعطاف‌پذیر سوال و جواب

## توضیحات

این مخزن شامل یک چت‌بات سبک و انعطاف‌پذیر سوال و جواب (Q&A) است که با استفاده از جنگو ساخته شده و توسط جاسازی‌های فست‌تکست برای جستجوی معنایی مشابهت قدرت‌گرفته است. چت‌بات برای مدیریت پرسش‌های کاربر با تطبیق آنها با پایگاه داده‌ای از سوالات متداول از پیش تعریف‌شده طراحی شده و پاسخ‌های سریع و مرتبط ارائه می‌دهد. این سیستم ایده‌آل برای کاربردهایی مانند پشتیبانی مشتری، پایگاه‌های دانش، ربات‌های trivia یا هر سناریویی که نیاز به پاسخ‌های خودکار مبتنی بر درک زبان طبیعی دارد.

سیستم از هر دو زبان انگلیسی و فارسی از طریق مدل‌های پیش‌آموزش‌دیده جداگانه پشتیبانی می‌کند. منطق اصلی از مشابهت کسینوسی با آستانه قابل تنظیم (پیش‌فرض: 0.7) برای تعیین بهترین پاسخ تطبیقی استفاده می‌کند. اگر هیچ تطبیقی بالای آستانه پیدا نشود، یک پاسخ fallback ارائه می‌شود.

مخزن شامل تمام کدهای لازم برای برنامه جنگو، قالب‌ها، فایل‌های استاتیک و جزئیات پیکربندی است. توجه کنید که فایل‌های مدل پیش‌آموزش‌دیده باید جداگانه دانلود شده و در دایرکتوری ریشه قرار گیرند.

## ویژگی‌های کلیدی

- **زمان پاسخ‌دهی سریع**: از جاسازی‌های فست‌تکست برای جستجوی معنایی کارآمد استفاده می‌کند.
- **یکپارچگی با جنگو**: به طور seamless با جنگو برای استقرار مبتنی بر وب و مدیریت ادمین ادغام می‌شود.
- **تطبیق معنایی**: از مشابهت کسینوسی برای یافتن مرتبط‌ترین ورودی FAQ استفاده می‌کند.
- **قابل تنظیم**: به راحتی آستانه مشابهت، مسیر مدل و سایر تنظیمات را تنظیم کنید.
- **رابط کاربری minimalist**: رابط چت مبتنی بر وب تمیز با به‌روزرسانی‌های واقعی‌زمان از طریق جاوااسکریپت.
- **پشتیبانی از زبان**: سازگار با انگلیسی و فارسی از طریق مدل‌های پیش‌آموزش‌دیده اختصاصی.
- **بدون bloat**: طراحی سبک با وابستگی‌های minimal.
- **لاگینگ**: شامل لاگینگ debug برای توسعه و عیب‌یابی.
- **پنل ادمین**: مدیریت FAQها از طریق رابط ادمین内置 جنگو.
- **مجموعه تست**: تست‌های واحد پایه برای عملکرد اصلی.

## پشته فناوری

| جزء           | نسخه/توضیحات                               |
|---------------|---------------------------------------------|
| Django       | 4.2.7 - چارچوب وب برای منطق backend.      |
| FastText     | 0.9.2 (از طریق fasttext-wheel) - برای جاسازی‌ها و مشابهت معنایی. |
| NumPy        | 1.24.3 - محاسبات عددی.                    |
| scikit-learn | 1.3.0 - محاسبات مشابهت کسینوسی.           |
| Python       | 3.8+ - زبان برنامه‌نویسی اصلی.           |
| پایگاه داده | SQLite (پیش‌فرض) یا PostgreSQL برای تولید. |
| Frontend     | HTML، CSS، JavaScript - رابط چت minimalist. |

## شروع به کار

### پیش‌نیازها

- پایتون 3.8 یا بالاتر نصب شده.
- محیط مجازی توصیه می‌شود برای جداسازی وابستگی‌ها.
- دسترسی به ادمین جنگو نیاز به ایجاد superuser دارد (از طریق `python manage.py createsuperuser`).

### نصب

1. کلون کردن مخزن:
   ```
   git clone https://github.com/ITheEqualizer/Chatbot.git
   cd Chatbot
   ```

2. ایجاد و فعال‌سازی محیط مجازی:
   ```
   python -m venv venv
   source venv/bin/activate  # در ویندوز: venv\Scripts\activate
   ```

3. نصب وابستگی‌ها:
   ```
   pip install -r requirements.txt
   ```

4. دانلود مدل پیش‌آموزش‌دیده:
   - **نسخه انگلیسی**: دانلود از [این لینک](https://drive.google.com/file/d/1u17AHiicxmfeDbvTyuew60SjXCr19UCu/view?usp=drive_link)، نام فایل را به `ChatBot.bin` تغییر دهید و در دایرکتوری ریشه پروژه قرار دهید.
   - **نسخه فارسی**: دانلود از [این لینک](https://drive.google.com/file/d/1jIMJC03SYYBqsH5YjZ84w-T2J-kRRGTp/view?usp=drive_link)، نام فایل را به `ChatBot_Persian.bin` تغییر دهید و در دایرکتوری ریشه پروژه قرار دهید.
   
   توجه: برای پشتیبانی فارسی، اطمینان حاصل کنید که ورودی‌های FAQ در پایگاه داده به زبان فارسی هستند برای عملکرد بهینه.

5. اعمال مهاجرت‌های پایگاه داده:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

6. جمع‌آوری فایل‌های استاتیک:
   ```
   python manage.py collectstatic --noinput
   ```

7. اجرای سرور توسعه:
   ```
   python manage.py runserver
   ```
   دسترسی به چت‌بات در `http://127.0.0.1:8000/`. افزودن FAQها از طریق پنل ادمین در `http://127.0.0.1:8000/admin/` (ورود لازم است).

### عیب‌یابی

- اگر بارگذاری مدل شکست خورد، مسیر فایل و مجوزها را بررسی کنید.
- اطمینان حاصل کنید که هیچ اشتباهی در سوالات/پاسخ‌ها هنگام افزودن از طریق ادمین وجود ندارد.
- برای تولید، `DEBUG = False`を設定 کنید و یک پایگاه داده مناسب پیکربندی کنید.

## ساختار پروژه

مخزن از ساختار استاندارد پروژه جنگو پیروی می‌کند با نام پروژه `chatbot`. در زیر شکستن دقیق هر فایل و دایرکتوری، شامل اهداف آنها آورده شده است:

- **`manage.py`**: ابزار خط فرمان جنگو برای وظایف اداری مانند اجرای سرور، مهاجرت‌ها و تست‌ها.
- **`requirements.txt`**: لیست تمام وابستگی‌های پایتون با نسخه‌های دقیق (Django==4.2.7, fasttext-wheel==0.9.2, numpy==1.24.3, scikit-learn==1.3.0).
- **`ChatBot.bin`** یا **`ChatBot_Persian.bin`**: فایل مدل فست‌تکست پیش‌آموزش‌دیده (دانلود جداگانه). جاسازی‌های وکتور برای سوالات فراهم می‌کند.
- **`chatbot/`**: دایرکتوری اصلی پروژه شامل تنظیمات، مدل‌ها، ویوها و سایر پیکربندی‌ها.
  - **`__init__.py`**: دایرکتوری را به عنوان بسته پایتون اولیه‌سازی می‌کند.
  - **`admin.py`**: مدل FAQ را در رابط ادمین جنگو ثبت می‌کند برای مدیریت آسان.
  - **`apps.py`**: کلاس پیکربندی برنامه (مانند `ChatbotConfig` با فیلد خودکار پیش‌فرض تنظیم‌شده به `BigAutoField`).
  - **`models.py`**: مدل `FAQ` را تعریف می‌کند با فیلدها: `question` (متن)، `answer` (متن)، `embedding_vector` (فیلد باینری برای ذخیره جاسازی‌های وکتور). شامل override `save()` برای محاسبه و ذخیره خودکار جاسازی‌ها با استفاده از مدل فست‌تکست بارگذاری‌شده.
  - **`views.py`**: شامل تابع `chat_view` (یا ویو مبتنی بر کلاس) که پرسش‌های کاربر را مدیریت می‌کند. مدل فست‌تکست را بارگذاری می‌کند، سوال ورودی را وکتور می‌کند، مشابهت کسینوسی را در برابر تمام جاسازی‌های FAQ محاسبه می‌کند و بهترین تطبیق را اگر بالای آستانه (پیش‌فرض 0.7) باشد برمی‌گرداند. اگر هیچ تطبیقی نباشد، به پیام پیش‌فرض برمی‌گردد.
  - **`urls.py`**: الگوهای URL را تعریف می‌کند، مسیر ریشه (`''`) را به ویو چت (نام 'chatbot') نقشه می‌زند.
  - **`tests.py`**: تست‌های واحد برای مدل‌ها و ویوها، شامل تست‌های تولید جاسازی، محاسبات مشابهت و موارد لبه مانند پرسش‌های خالی.
  - **`settings.py`**: فایل تنظیمات پروژه، شامل پیکربندی پایگاه داده، برنامه‌های نصب‌شده، middleware، قالب‌ها، فایل‌های استاتیک، SECRET_KEY، حالت DEBUG، MODEL_PATH='ChatBot.bin' (قابل تنظیم برای فارسی) و SIMILARITY_THRESHOLD=0.7.
  - **`wsgi.py`** و **`asgi.py`**: نقاط ورودی برای سرورهای وب سازگار با WSGI/ASGI (استاندارد برای استقرار).
- **`templates/chatbot/`**: دایرکتوری برای قالب‌های HTML.
  - **`base.html`**: قالب پایه که ساختار کلی HTML را فراهم می‌کند، شامل هدرها، فوترها و لینک‌ها به CSS/JS.
  - **`index.html`**: قالب رابط چت اصلی با bubbles پیام، فرم ورودی و spinner بارگذاری.
  - **`style.css`**: فایل CSS برای استایل رابط چت (طراحی minimalist با bubbles، رنگ‌ها و layout responsive).
- **`static/js/`**: دایرکتوری برای فایل‌های جاوااسکریپت استاتیک.
  - **`chat.js`**: منطق سمت مشتری را مدیریت می‌کند، شامل درخواست‌های AJAX (fetch) به سرور، به‌روزرسانی رابط چت در زمان واقعی، نمایش نشانگرهای typing و مدیریت خطاها.
- **`.gitignore`**: فایل ignore استاندارد برای محیط‌های مجازی، فایل‌های pyc، __pycache__، پایگاه‌های داده و سایر فایل‌های موقت.
- **`LICENSE`**: فایل مجوز MIT که مجوزهای استفاده، اصلاح و توزیع را اعطا می‌کند.
- **`README.md`**: این فایل مستندسازی.

## پیکربندی

پروژه را از طریق `chatbot/settings.py` سفارشی کنید:

- **SECRET_KEY**: یک کلید امن تولید کنید و از طریق متغیرهای محیطی برای امنیت تنظیم کنید.
- **DEBUG**: برای توسعه به `True` تنظیم کنید؛ برای تولید `False`.
- **MODEL_PATH**: پیش‌فرض `'ChatBot.bin'`. برای پشتیبانی فارسی به `'ChatBot_Persian.bin'` تغییر دهید.
- **SIMILARITY_THRESHOLD**: مقدار float (پیش‌فرض 0.7) برای تطبیق پرسش‌ها با FAQها.
- **DATABASES**: پیش‌فرض برای SQLite پیکربندی شده؛ برای PostgreSQL یا backendهای دیگر به‌روزرسانی کنید.
- از متغیرهای محیطی (مانند `os.environ`) برای تنظیمات حساس استفاده کنید.

## تستینگ

مجموعه تست را اجرا کنید:
```
python manage.py test chatbot.tests
```
تست‌ها پوشش مدل ذخیره‌سازی، پاسخ‌های ویو، منطق مشابهت و موارد لبه را می‌دهند. هدف حداقل 80% پوشش با ابزارهایی مانند coverage.py.

## استقرار

- **Heroku**: یک `Procfile` با `web: gunicorn chatbot.wsgi` اضافه کنید و متغیرهای محیطی را پیکربندی کنید.
- **Docker**: یک `Dockerfile` برای containerization ایجاد کنید (مانند پایه روی python:3.12، نصب وابستگی‌ها، expose پورت 8000).
- **AWS/Vercel/سایر**: از gunicorn یا uWSGI برای سرور تولید استفاده کنید؛ HTTPS را فعال کنید؛ ورودی‌ها را برای جلوگیری از injections sanitize کنید.
- اطمینان حاصل کنید که فایل مدل در bundle استقرار گنجانده شده است.

## مشارکت

1. مخزن را fork کنید.
2. یک شاخه feature ایجاد کنید: `git checkout -b feature/new-feature`.
3. تغییرات را commit کنید: `git commit -m "Add new feature"`.
4. به شاخه push کنید: `git push origin feature/new-feature`.
5. یک Pull Request با عنوان توصیفی، جزئیات و اسکرین‌شات‌ها اگر適用 باز کنید.

باگ‌ها را گزارش دهید، ویژگی‌ها پیشنهاد دهید یا سوالات بپرسید از طریق Issues GitHub. کد رفتار را برای مشارکت‌های respectful پیروی کنید.

## مجوز

این پروژه تحت مجوز MIT مجوز داده شده است. جزئیات را در فایل `LICENSE` ببینید.

## قدردانی‌ها

- تشکر از تیم جنگو برای چارچوب robust.
- اعتبار به فست‌تکست فیسبوک برای فناوری جاسازی.
- قدردانی از مشارکت‌کنندگان و کاربران برای بازخورد.

به‌روزرسانی‌شده: ۱۶ اکتبر ۲۰۲۵
