# Client and Server Responsibilities

## Philosophy

Quasimodo follows a **client-driven architecture**. The browser is responsible for the user interface and editing schedules, while the Django server is responsible for validating, storing, and serving schedule data. This separation keeps the backend simple, makes the interface responsive, and allows future clients (such as a mobile app or desktop application) to interact with the same API.

The canonical representation of every schedule is a JSON document.

---

# Server Responsibilities

The Django server has a deliberately small set of responsibilities.

## Templates

The server must be able to:

* Create a new day, week, or month template from a JSON document.
* Read a day, week, or month template and return it as JSON.
* Delete a template.

The server validates incoming data before storing it in the database.

---

## Active Schedule

The server must also be able to:

* Replace the active schedule with a JSON document received from the client.

The server does **not** edit schedules event-by-event. Instead, it stores the completed schedule submitted by the client.

---

## Validation

The server is responsible for ensuring that submitted schedules are valid before committing them to the database.

Examples include:

* Required fields are present.
* Times are valid.
* Events are in chronological order.
* No invalid references exist.

The client should attempt to prevent invalid input, but the server is always the final authority.

---

## API Design

The server should expose a small REST-style API.

Example endpoints:

```text
GET    /api/templates/day/<id>/
POST   /api/templates/day/
PUT    /api/templates/day/<id>/
DELETE /api/templates/day/<id>/

GET    /api/templates/week/<id>/
POST   /api/templates/week/
PUT    /api/templates/week/<id>/
DELETE /api/templates/week/<id>/

GET    /api/templates/month/<id>/
POST   /api/templates/month/
PUT    /api/templates/month/<id>/
DELETE /api/templates/month/<id>/

POST   /api/active/day/
POST   /api/active/week/
POST   /api/active/month/
```

Application state should be communicated through URLs and JSON payloads rather than custom HTTP headers. Standard HTTP headers remain reserved for authentication, CSRF protection, and content negotiation.

---

# Client Responsibilities

The browser is responsible for nearly all user interaction.

## User Interface

The client renders:

* Dashboard
* Schedule pages
* Editors
* Dialogs
* Forms
* Notifications

The server should never need to know how these are implemented.

---

## Editing

All schedule editing occurs entirely within the browser.

Users should be able to:

* Create templates
* Edit templates
* Duplicate templates
* Delete events
* Add events
* Reorder events
* Modify event times
* Load templates into the active schedule

None of these operations require communication with the server until the user selects **Apply** or **Save**.

---

## Temporary State

The client maintains all temporary editing state.

Examples include:

* Unsaved changes
* Drag-and-drop ordering
* Selected template
* Undo history (future)
* Validation warnings

This allows the editor to remain fast and responsive without unnecessary network requests.

---

## Saving

When the administrator chooses to save or apply changes, the client sends the **entire completed schedule** to the server as a single JSON document.

The server validates the document and stores it if it is valid.

This approach greatly simplifies the backend by eliminating the need to process dozens of individual editing operations.

---

# Design Principles

Quasimodo follows these architectural principles:

* The browser owns the editing experience.
* The server owns data integrity.
* Schedules are exchanged as JSON.
* Templates are reusable.
* Active schedules are independent instances derived from templates.
* The backend should remain simple enough that another client (mobile app, desktop app, or command-line tool) could use the same API without modification.

Maintaining this separation keeps the project easier to extend, test, and maintain as new features are added.
