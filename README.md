# Quasimodo

---

## Description

Quasimodo is a web-based management interface for school bell scheduling systems. It is being developed as a service project to provide administrators with a modern, intuitive alternative to the default scheduling interface while maintaining compatibility with existing hardware.

---

## Goals

* Simplify bell schedule creation and editing
* Provide a clean, responsive user interface
* Reduce scheduling errors through validation and conflict detection
* Support deployment on low-power hardware such as a Raspberry Pi
* Maintain compatibility with existing scheduling hardware

---

## Technology

* Python
* Django
* DaisyUI + Tailwind CSS
* Gunicorn
* Nginx (deployment)
* Raspberry Pi OS

---

# Development

---

## Setting up Development Environment

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

## Working With AI

As seen elsewhere in the documentation, use of AI is not discouraged, but there should _never_ be extensive amounts of code that no human understands.
Preferably, a human would write code while advised by an LLM for efficiency and debugging. Directly pasting AI-generated code is not acceptable for a long-term code base.
Suggested uses:

- LLM explains a concept, human writes code.
- LLM suggests an approach to a problem, human implements.
- LLM generates code, human rewrites in their own words.

Notice what they have in common? 
If the code is not _yours_, don't submit it.

There are a few cases where AI-generated content is acceptable, mainly as a short-term patch so that development can continue in other areas.
At the time of writing this, there are a few examples of AI-generated content:

- Documentation of Allsync IQ Connection Protocol
- Documentation of logging.
- Documentation of Client and Server responsibilities.
- Bit-wise Encoding/Decoding logic.

This is not optimal. These files need to eventually be replaced or rewritten by human hands.

---
