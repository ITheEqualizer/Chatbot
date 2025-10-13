# Chatbot: A Lightweight and Flexible Q&A Chatbot

Welcome to **Chatbot**, a lightweight, flexible, and powerful Question & Answer chatbot built with **Django** and powered by **FastText embeddings**. This project is designed to provide an efficient and customizable solution for creating conversational agents that can understand and respond to user queries with high accuracy. Whether you're building a customer support bot, a knowledge base assistant, or an interactive Q&A system, this chatbot is a great starting point.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Step-by-Step Setup](#step-by-step-setup)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Running the Chatbot](#running-the-chatbot)
  - [Interacting with the Chatbot](#interacting-with-the-chatbot)
- [Using the Pre-trained Model](#using-the-pre-trained-model)
- [Project Structure](#project-structure)
- [Customization](#customization)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

## Features

- **Natural Language Understanding**: Utilizes **FastText embeddings** for robust and efficient text processing, enabling the chatbot to understand user queries effectively.
- **Django Backend**: Built on the Django framework for a scalable and secure web-based interface.
- **Lightweight Design**: Optimized for performance, making it suitable for deployment on resource-constrained environments.
- **Customizable Responses**: Easily extend the chatbot’s knowledge base by adding new question-answer pairs or integrating with external data sources.
- **RESTful API**: Provides an API for seamless integration with other applications or frontends.
- **Responsive Web Interface**: Includes a user-friendly web interface for interacting with the chatbot.
- **Modular Architecture**: Designed for easy customization and extension, allowing developers to add new features or modify existing ones.
- **Pre-trained Model Support**: Leverages a pre-trained FastText model for quick setup and improved performance.

## Technologies Used

- **Django**: A high-level Python web framework for rapid development and clean design.
- **FastText**: A library for efficient text classification and word embeddings by Facebook AI Research.
- **Python**: The primary programming language used for the project (Python 3.8+ recommended).
- **HTML/CSS/JavaScript**: For the web-based user interface.
- **SQLite**: Default database for development (configurable to use PostgreSQL, MySQL, etc.).
- **Gunicorn**: WSGI HTTP server for serving the Django application in production.
- **Nginx** (optional): Recommended for production deployment as a reverse proxy.
- **Pipenv**: For dependency management and virtual environment setup.

## Installation

Follow these steps to set up the Chatbot project on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+**: Download and install from [python.org](https://www.python.org/downloads/).
- **Pipenv**: Install using `pip install pipenv`.
- **Git**: For cloning the repository. Install from [git-scm.com](https://git-scm.com/).
- **FastText**: Install the FastText Python library (see installation steps below).
- **Django**: Included in the project dependencies.
- A modern web browser for accessing the web interface.

### Step-by-Step Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ITheEqualizer/Chatbot.git
   cd Chatbot
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   pipenv install
   pipenv shell
   ```

3. **Install FastText**:
   Install the FastText Python library:
   ```bash
   pip install fasttext
   ```

4. **Download the Pre-trained Model**:
   Download the pre-trained FastText model from the following link:
   [Download Pre-trained Model](https://drive.google.com/file/d/1u17AHiicxmfeDbvTyuew60SjXCr19UCu/view?usp=drive_link)

   Place the downloaded `ChatBot.bin` file in the root directory of the project (`Chatbot/`).

5. **Apply Database Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser (Optional)**:
   If you want to access the Django admin panel:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

   The chatbot will be accessible at `http://localhost:8000`.

## Configuration

The chatbot can be configured via the `settings.py` file in the Django project directory. Key configurations include:

- **Database**: By default, SQLite is used. To use PostgreSQL or MySQL, update the `DATABASES` setting.
- **FastText Model Path**: Specify the path to the FastText model in the `settings.py` file:
  ```python
  FASTTEXT_MODEL_PATH = 'ChatBot.bin'
  ```
- **Static Files**: Ensure static files are collected for production:
  ```bash
  python manage.py collectstatic
  ```

## Usage

### Running the Chatbot

1. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

2. Open your browser and navigate to `http://localhost:8000` to access the web interface.

3. For production, use Gunicorn and Nginx:
   ```bash
   gunicorn --workers 3 chatbot.wsgi:application
   ```

### Interacting with the Chatbot

- **Web Interface**: Type your question in the input field and receive responses instantly.
- **API**: Send POST requests to the `/api/chat/` endpoint with a JSON payload:
  ```json
  {
    "question": "What is the capital of France?"
  }
  ```
  Example using `curl`:
  ```bash
  curl -X POST http://localhost:8000/api/chat/ -H "Content-Type: application/json" -d '{"question": "What is the capital of France?"}'
  ```

## Using the Pre-trained Model

The chatbot uses a pre-trained FastText model for efficient and accurate responses. To use the provided model:

1. Ensure the `ChatBot.bin` file is placed in the root directory of the project (`Chatbot/`).
2. Verify that the `FASTTEXT_MODEL_PATH` in `settings.py` points to `model.bin`.
3. No additional training is required to start using the chatbot with the pre-trained model.

If you wish to train a custom model, you can prepare a dataset and follow the FastText training documentation, but the pre-trained model is recommended for quick setup.

## Project Structure

```
Chatbot/
├── chatbot/                 # Django project directory
│   ├── __init__.py
│   ├── settings.py         # Configuration settings
│   ├── urls.py             # URL routing
│   ├── wsgi.py             # WSGI entry point
├── chat/                    # Main Django app
│   ├── migrations/         # Database migrations
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── templates/          # HTML templates
│   ├── static/             # CSS, JS, and other static files
├── data/                    # Training data for FastText (optional)
├── ChatBot.bin                # Pre-trained FastText model
├── manage.py                # Django management script
├── Pipfile                  # Dependency management
├── README.md                # This file
```

## Customization

- **Adding New Responses**: Update the dataset in `data/train.txt` (if training a custom model) and retrain the FastText model.
- **Customizing the UI**: Modify the templates in `chat/templates/` and static files in `chat/static/`.
- **Extending the API**: Add new endpoints in `chat/urls.py` and corresponding views in `chat/views.py`.
- **Integrating External APIs**: Modify `chat/views.py` to fetch data from external sources for dynamic responses.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -m "Add new feature"`).
4. Push to your branch (`git push origin feature-branch`).
5. Create a pull request.

Please ensure your code follows the project’s coding standards and includes tests where applicable.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, reach out to the project maintainer:

- **GitHub**: [ITheEqualizer](https://github.com/ITheEqualizer)
- **Email**: ali.zakaee.1997@gmail.com

## Acknowledgements

- **Django**: For providing a robust web framework.
- **FastText**: For efficient text processing and embeddings.
- **GitHub Community**: For inspiration and support.
- **Open Source Contributors**: For making awesome tools available to everyone.

Thank you for using **Chatbot**! We hope it powers your next great project. 🚀
