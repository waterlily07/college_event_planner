# College Event Planner

A simple Python command-line mini-project for managing college events and student registrations.

## Features

- Add college events with date, venue, organizer, audience, category, and seat capacity.
- Register students for an event.
- Track seats left automatically.
- Search events by name, venue, organizer, or category.
- Show all events and a dashboard with total registrations.
- Show the most popular event based on registration count.

## Run

```bash
python event_planner.py
```

## Screenshots

The CLI supports event creation, student registration, event search, dashboard summaries, and registration tracking.

### Add Events and Register Students

![Add an event and register a student](docs/screenshots/menu-and-event.png)

### Browse and Search Events

![Browse and search events](docs/screenshots/events-and-search.png)

### Event Dashboard

![Event dashboard](docs/screenshots/dashboard.png)

### Registration Records

![Registration records](docs/screenshots/registrations.png)

## Project Data

The project automatically stores data in:

- `data/events.json`
- `data/registrations.json`
