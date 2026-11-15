# Library Reservation System

A small Flask web app for booking time slots at university libraries. Students pick a library, a date and a time, and the app refuses bookings that clash with an existing one or fall in the past.

Built as a group project for CMPE331 (Software Engineering) at Istanbul Bilgi University. The project's requirements, UML diagrams and final report are included as PDFs.

## Features

- List, create and delete reservations
- University email check: only addresses ending in `.edu.tr` can book (for example `name@bilgi.edu.tr`)
- No bookings in the past, and no double booking of the same slot at the same library
- Clear error messages, with the form keeping what you typed
- Reservations are saved to a JSON file, so they survive a restart

## Tech stack

Python 3.10+, Flask, Jinja templates, Bootstrap 5, pytest.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000.

Optional settings (environment variables):

| Variable | What it does | Default |
|----------|--------------|---------|
| `PORT` | Port to listen on | `5000` |
| `DATA_FILE` | Where reservations are stored | `data/reservations.json` |
| `SECRET_KEY` | Signs the session that carries flash messages | a random key per start |

## Tests

```bash
pytest
```

The tests cover the email rule, past dates, double booking, invalid dates and times, deleting, and saving across restarts.

## Project documents

| File | Contents |
|------|----------|
| `Library_Reservation_SRS.pdf` | Software requirements specification |
| `Library_Reservation_UML_Diagrams.pdf` | Use case, class, activity and sequence diagrams |
| `Library_Reservation_Final_Report.pdf` | Final report with screenshots |

## Team

Cem Akçiçek, Ece Doğa Gül, Berkay Özdelice, Muhammed Ali Akdoğan and Emirhan İnan.
