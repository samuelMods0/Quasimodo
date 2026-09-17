# Quasimodo

Quasimodo is a web-based management interface for school bell scheduling systems. It is being developed as a service project to provide administrators with a modern, intuitive alternative to the default scheduling interface while maintaining compatibility with existing hardware.

---

# Goals

* Simplify bell schedule creation and editing
* Provide a clean, responsive user interface
* Reduce scheduling errors through validation and conflict detection
* Support deployment on low-power hardware such as a Raspberry Pi
* Maintain compatibility with existing scheduling hardware

---

# Technology

* Python
* Django
* DaisyUI + Tailwind CSS
* Gunicorn
* Nginx (deployment)
* Raspberry Pi OS

---

# Project Status

This project is currently in early development.

---

# Dev Notes

Assuming that you have git, python, and pip already installed, from the project root:

`python -m venv .venv`

`source .venv/bin/activate`

`pip install -r requirements.txt`

Create `.env` with the variables from `.env.example`.
Generate a Django secret key with the Django module:

`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

or with the secrets module:

`python -c "import secrets; print(secrets.token_urlsafe(50))"`

For development, usually just set `DEBUG` to True.

Give `CLOCK_IP` a blank string for now, there is nothing that actually communicates with it yet.

To run the project from its root:

`python manage.py runserver <port>`

---

# License

This project is licensed under the MIT License.

---

# Disclaimer

Much of the documentation was created by AI. However, very little code was produced by AI.