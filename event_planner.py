#!/usr/bin/env python3
<<<<<<< HEAD
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), 'event_planner.db')
=======
import json
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
EVENTS_FILE = os.path.join(DATA_DIR, 'events.json')
REGISTRATIONS_FILE = os.path.join(DATA_DIR, 'registrations.json')


def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'w') as f:
            json.dump([], f)

    if not os.path.exists(REGISTRATIONS_FILE):
        with open(REGISTRATIONS_FILE, 'w') as f:
            json.dump([], f)
>>>>>>> feffcf6a718c68e105a5b96ef23f469a584969d4


class EventPlanner:
    def __init__(self):
<<<<<<< HEAD
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS organizers (
                    organizer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    event_name TEXT NOT NULL,
                    event_date TEXT NOT NULL,
                    venue TEXT,
                    audience TEXT,
                    category TEXT,
                    total_seats INTEGER NOT NULL,
                    description TEXT
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS event_organizers (
                    event_id TEXT NOT NULL,
                    organizer_id INTEGER NOT NULL,
                    PRIMARY KEY (event_id, organizer_id),
                    FOREIGN KEY (event_id) REFERENCES events(event_id),
                    FOREIGN KEY (organizer_id) REFERENCES organizers(organizer_id)
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    roll_number TEXT NOT NULL UNIQUE,
                    department TEXT,
                    phone TEXT
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS registrations (
                    registration_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    student_id INTEGER NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES events(event_id),
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    registration_id TEXT NOT NULL UNIQUE,
                    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                    comment TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (registration_id) REFERENCES registrations(registration_id)
                )
            ''')

    def generate_event_id(self, conn):
        row = conn.execute(
            "SELECT COALESCE(MAX(CAST(SUBSTR(event_id, 3) AS INTEGER)), 1000) AS last_id FROM events WHERE event_id LIKE 'EV%'"
        ).fetchone()
        return f"EV{int(row['last_id']) + 1}"

    def generate_registration_id(self, conn):
        row = conn.execute(
            "SELECT COALESCE(MAX(CAST(SUBSTR(registration_id, 4) AS INTEGER)), 1000) AS last_id FROM registrations WHERE registration_id LIKE 'REG%'"
        ).fetchone()
        return f"REG{int(row['last_id']) + 1}"

    # ---------- shared helpers (also used by the web app) ----------
    def find_registration(self, conn, event_id, roll_number, phone):
        """Return the registration row only if this student (roll number + the
        phone number used at registration) is registered for the event."""
        return conn.execute(
            '''
            SELECT r.registration_id, s.student_name
            FROM registrations r
            INNER JOIN students s ON s.student_id = r.student_id
            WHERE LOWER(r.event_id) = LOWER(?)
              AND LOWER(s.roll_number) = LOWER(?)
              AND s.phone = ?
            ''',
            (event_id, roll_number.strip(), phone.strip())
        ).fetchone()

    def submit_feedback(self, event_id, roll_number, phone, rating, comment):
        """Save a rating. Returns (ok, message). Registered students only,
        one rating per registration."""
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            return False, 'Rating must be a number from 1 to 5.'
        if not 1 <= rating <= 5:
            return False, 'Rating must be between 1 and 5.'

        with self.get_connection() as conn:
            reg = self.find_registration(conn, event_id, roll_number, phone)
            if not reg:
                return False, 'Only students registered for this event can leave feedback (check roll number and phone).'
            exists = conn.execute(
                'SELECT 1 FROM feedback WHERE registration_id = ?', (reg['registration_id'],)
            ).fetchone()
            if exists:
                return False, 'You have already submitted feedback for this event.'
            conn.execute(
                'INSERT INTO feedback (registration_id, rating, comment) VALUES (?, ?, ?)',
                (reg['registration_id'], rating, comment.strip())
            )
        return True, 'Thank you! Your feedback was saved.'

    def get_rating_summary(self, event_id):
        with self.get_connection() as conn:
            row = conn.execute(
                '''
                SELECT COUNT(f.feedback_id) AS total, AVG(f.rating) AS average
                FROM feedback f
                INNER JOIN registrations r ON r.registration_id = f.registration_id
                WHERE r.event_id = ?
                ''',
                (event_id,)
            ).fetchone()
        return {'total': row['total'], 'average': round(row['average'], 1) if row['average'] else None}
=======
        ensure_data_files()
        self.events = self.load_events()
        self.registrations = self.load_registrations()

    def load_events(self):
        try:
            with open(EVENTS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def load_registrations(self):
        try:
            with open(REGISTRATIONS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def save_events(self):
        with open(EVENTS_FILE, 'w') as f:
            json.dump(self.events, f, indent=4)

    def save_registrations(self):
        with open(REGISTRATIONS_FILE, 'w') as f:
            json.dump(self.registrations, f, indent=4)
>>>>>>> feffcf6a718c68e105a5b96ef23f469a584969d4

    def display_menu(self):
        print('\n' + '=' * 60)
        print('COLLEGE EVENT PLANNER')
        print('=' * 60)
        print('1. Add Event')
        print('2. Register Student')
        print('3. Show All Events')
        print('4. Search Events')
        print('5. Show Event Dashboard')
        print('6. Show Registrations')
<<<<<<< HEAD
        print('7. Give Feedback / Rating')
        print('8. Show Feedback')
        print('9. Exit')
        print('=' * 60)

    def ensure_organizer(self, conn, organizer_name):
        organizer_name = organizer_name.strip()
        if not organizer_name:
            return None

        row = conn.execute(
            'SELECT organizer_id FROM organizers WHERE LOWER(name) = LOWER(?)',
            (organizer_name,)
        ).fetchone()

        if row:
            return row['organizer_id']

        cursor = conn.execute(
            'INSERT INTO organizers (name) VALUES (?)',
            (organizer_name,)
        )
        return cursor.lastrowid

    def get_organizer_names_for_event(self, event_id):
        with self.get_connection() as conn:
            rows = conn.execute(
                '''
                SELECT o.name
                FROM organizers o
                INNER JOIN event_organizers eo ON eo.organizer_id = o.organizer_id
                WHERE eo.event_id = ?
                ORDER BY o.name
                ''',
                (event_id,)
            ).fetchall()
            return [row['name'] for row in rows]

=======
        print('7. Exit')
        print('=' * 60)

>>>>>>> feffcf6a718c68e105a5b96ef23f469a584969d4
    def add_event(self):
        print('\nADD NEW EVENT')
        event_name = input('Event Name: ').strip()
        event_date = input('Event Date (YYYY-MM-DD): ').strip()
        venue = input('Venue: ').strip()
<<<<<<< HEAD
        organizer_input = input('Organizer Name(s) (comma separated): ').strip()
        audience = input('Audience (e.g. BCA Students): ').strip()
        category = input('Category (Technical/Cultural/Sports/Workshop): ').strip()
        try:
            total_seats = int(input('Total Seats: ').strip())
        except ValueError:
            print('Total seats must be a whole number.')
            return
        if total_seats <= 0:
            print('Total seats must be at least 1.')
            return
=======
        organizer = input('Organizer: ').strip()
        audience = input('Audience (e.g. BCA Students): ').strip()
        category = input('Category (Technical/Cultural/Sports/Workshop): ').strip()
        total_seats = int(input('Total Seats: ').strip())
>>>>>>> feffcf6a718c68e105a5b96ef23f469a584969d4
        description = input('Description: ').strip()

        if not event_name or not event_date:
            print('Event name and date are required.')
            return

<<<<<<< HEAD
        with self.get_connection() as conn:
            event_id = self.generate_event_id(conn)
            conn.execute(
                '''
                INSERT INTO events (event_id, event_name, event_date, venue, audience, category, total_seats, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (event_id, event_name, event_date, venue, audience, category, total_seats, description)
            )

            organizer_names = [name.strip() for name in organizer_input.split(',') if name.strip()]
            if not organizer_names:
                organizer_names = ['College Team']

            for organizer_name in organizer_names:
                organizer_id = self.ensure_organizer(conn, organizer_name)
                if organizer_id is not None:
                    conn.execute(
                        'INSERT OR IGNORE INTO event_organizers (event_id, organizer_id) VALUES (?, ?)',
                        (event_id, organizer_id)
                    )

        print(f'Event added successfully: {event_id}')

    def get_event_by_id(self, event_id):
        with self.get_connection() as conn:
            row = conn.execute('SELECT * FROM events WHERE LOWER(event_id) = LOWER(?)', (event_id,)).fetchone()
            return dict(row) if row else None

    def get_seats_left(self, event_id):
        with self.get_connection() as conn:
            event = conn.execute('SELECT total_seats FROM events WHERE LOWER(event_id) = LOWER(?)', (event_id,)).fetchone()
            if not event:
                return 0

            registered_count = conn.execute(
                'SELECT COUNT(*) AS total FROM registrations WHERE LOWER(event_id) = LOWER(?)',
                (event_id,)
            ).fetchone()['total']
            return int(event['total_seats']) - int(registered_count)

    def show_all_events_for_choice(self):
        with self.get_connection() as conn:
            rows = conn.execute('SELECT * FROM events ORDER BY event_date').fetchall()

        if not rows:
            print('No events exist yet.')
            return

        print('\nAvailable Events:')
        for event in rows:
            event_id = event['event_id']
            seats_left = self.get_seats_left(event_id)
            organizers = ', '.join(self.get_organizer_names_for_event(event_id)) or 'Not assigned'
            print(f"{event_id} | {event['event_name']} | {event['event_date']} | {event['venue']} | Organizers: {organizers} | Seats Left: {seats_left}/{event['total_seats']}")

    def show_all_events(self):
        with self.get_connection() as conn:
            rows = conn.execute('SELECT * FROM events ORDER BY event_date').fetchall()

        if not rows:
            print('No events found.')
            return

        print('\nALL EVENTS')
        for event in rows:
            event_id = event['event_id']
            seats_left = self.get_seats_left(event_id)
            organizers = ', '.join(self.get_organizer_names_for_event(event_id)) or 'Not assigned'
            print(f"\n{event_id} - {event['event_name']}")
            print(f"Date: {event['event_date']} | Venue: {event['venue']} | Organizer(s): {organizers}")
            print(f"Category: {event['category']} | Audience: {event['audience']}")
            print(f"Seats: {seats_left}/{event['total_seats']} left")
            print(f"Description: {event['description']}")

    def search_events(self):
        keyword = input('Search events by name, venue, organizer, or category: ').strip().lower()
        with self.get_connection() as conn:
            rows = conn.execute(
                '''
                SELECT DISTINCT e.*
                FROM events e
                LEFT JOIN event_organizers eo ON eo.event_id = e.event_id
                LEFT JOIN organizers o ON o.organizer_id = eo.organizer_id
                WHERE LOWER(e.event_name) LIKE ?
                   OR LOWER(e.venue) LIKE ?
                   OR LOWER(e.category) LIKE ?
                   OR LOWER(COALESCE(o.name, '')) LIKE ?
                ORDER BY e.event_date
                ''',
                (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')
            ).fetchall()

        if not rows:
            print('No matching events found.')
            return

        print('\nSEARCH RESULTS')
        for event in rows:
            event_id = event['event_id']
            seats_left = self.get_seats_left(event_id)
            organizers = ', '.join(self.get_organizer_names_for_event(event_id)) or 'Not assigned'
            print(f"{event_id} | {event['event_name']} | {event['event_date']} | {event['venue']} | {event['category']} | Organizer(s): {organizers} | Seats Left: {seats_left}/{event['total_seats']}")

=======
        event_id = 'EV' + str(1000 + len(self.events) + 1)

        event = {
            'event_id': event_id,
            'event_name': event_name,
            'event_date': event_date,
            'venue': venue,
            'organizer': organizer,
            'audience': audience,
            'category': category,
            'total_seats': total_seats,
            'description': description
        }

        self.events.append(event)
        self.save_events()
        print(f'Event added successfully: {event_id}')

>>>>>>> feffcf6a718c68e105a5b96ef23f469a584969d4
    def register_student(self):
        print('\nREGISTER STUDENT FOR EVENT')
        self.show_all_events_for_choice()

        event_id = input('\nEnter Event ID: ').strip()
        event = self.get_event_by_id(event_id)

        if not event:
            print('Event not found.')
            return

        if self.get_seats_left(event_id) <= 0:
            print('This event is already full.')
            return

        student_name = input('Student Name: ').strip()
        roll_number = input('Roll Number: ').strip()
        department = input('Department: ').strip()
        phone = input('Phone Number: ').strip()

        if not student_name or not roll_number:
            print('Student name and roll number are required.')
            return

<<<<<<< HEAD
        with self.get_connection() as conn:
            student_row = conn.execute(
                'SELECT student_id FROM students WHERE LOWER(roll_number) = LOWER(?)',
                (roll_number,)
            ).fetchone()

            if student_row:
                student_id = student_row['student_id']
                conn.execute(
                    'UPDATE students SET student_name = ?, department = ?, phone = ? WHERE student_id = ?',
                    (student_name, department, phone, student_id)
                )
            else:
                cursor = conn.execute(
                    'INSERT INTO students (student_name, roll_number, department, phone) VALUES (?, ?, ?, ?)',
                    (student_name, roll_number, department, phone)
                )
                student_id = cursor.lastrowid

            existing = conn.execute(
                'SELECT 1 FROM registrations WHERE event_id = ? AND student_id = ? LIMIT 1',
                (event_id, student_id)
            ).fetchone()

            if existing:
                print('This student is already registered for this event.')
                return

            registration_id = self.generate_registration_id(conn)
            conn.execute(
                'INSERT INTO registrations (registration_id, event_id, student_id) VALUES (?, ?, ?)',
                (registration_id, event_id, student_id)
            )

        print(f'Registration successful: {registration_id}')

    def show_dashboard(self):
        print('\nEVENT DASHBOARD')

        with self.get_connection() as conn:
            rows = conn.execute(
                '''
                SELECT e.event_id, e.event_name, e.total_seats,
                       COUNT(r.registration_id) AS registration_count
                FROM events e
                LEFT JOIN registrations r ON r.event_id = e.event_id
                GROUP BY e.event_id, e.event_name, e.total_seats
                ORDER BY e.event_date
                '''
            ).fetchall()

        if not rows:
            print('No events available.')
            return

        for row in rows:
            seats_left = int(row['total_seats']) - int(row['registration_count'])
            print(f"{row['event_id']} | {row['event_name']} | Registrations: {row['registration_count']} | Seats Left: {seats_left}")
=======
        registration_id = 'REG' + str(1000 + len(self.registrations) + 1)

        registration = {
            'registration_id': registration_id,
            'event_id': event_id,
            'student_name': student_name,
            'roll_number': roll_number,
            'department': department,
            'phone': phone
        }

        self.registrations.append(registration)
        self.save_registrations()
        print(f'Registration successful: {registration_id}')

    def get_event_by_id(self, event_id):
        for event in self.events:
            if event['event_id'].lower() == event_id.lower():
                return event
        return None

    def get_seats_left(self, event_id):
        event = self.get_event_by_id(event_id)
        if not event:
            return 0

        total_seats = event['total_seats']
        registered = 0

        for reg in self.registrations:
            if reg['event_id'].lower() == event_id.lower():
                registered += 1

        return total_seats - registered

    def show_all_events_for_choice(self):
        if not self.events:
            print('No events exist yet.')
            return

        print('\nAvailable Events:')
        for event in self.events:
            seats_left = self.get_seats_left(event['event_id'])
            print(f"{event['event_id']} | {event['event_name']} | {event['event_date']} | {event['venue']} | Seats Left: {seats_left}/{event['total_seats']}")

    def show_all_events(self):
        if not self.events:
            print('No events found.')
            return

        print('\nALL EVENTS')
        for event in self.events:
            seats_left = self.get_seats_left(event['event_id'])
            print(f"\n{event['event_id']} - {event['event_name']}")
            print(f"Date: {event['event_date']} | Venue: {event['venue']} | Organizer: {event['organizer']}")
            print(f"Category: {event['category']} | Audience: {event['audience']}")
            print(f"Seats: {seats_left}/{event['total_seats']} left")
            print(f"Description: {event['description']}")

    def search_events(self):
        keyword = input('Search events by name, venue, organizer, or category: ').strip().lower()
        found = []

        for event in self.events:
            fields = f"{event['event_name']} {event['venue']} {event['organizer']} {event['category']}".lower()
            if keyword in fields:
                found.append(event)

        if not found:
            print('No matching events found.')
            return

        print('\nSEARCH RESULTS')
        for event in found:
            seats_left = self.get_seats_left(event['event_id'])
            print(f"{event['event_id']} | {event['event_name']} | {event['event_date']} | {event['venue']} | {event['category']} | Seats Left: {seats_left}/{event['total_seats']}")

    def show_dashboard(self):
        print('\nEVENT DASHBOARD')

        if not self.events:
            print('No events available.')
            return

        for event in self.events:
            reg_count = 0
            for reg in self.registrations:
                if reg['event_id'].lower() == event['event_id'].lower():
                    reg_count += 1

            seats_left = event['total_seats'] - reg_count
            print(f"{event['event_id']} | {event['event_name']} | Registrations: {reg_count} | Seats Left: {seats_left}")
>>>>>>> feffcf6a718c68e105a5b96ef23f469a584969d4

        popular = self.get_most_popular_event()
        if popular:
            print('\nMost Popular Event:')
            print(f"{popular['event_name']} ({popular['event_id']}) with {popular['registrations']} registrations")
        else:
            print('\nMost Popular Event: No registrations yet')

    def get_most_popular_event(self):
<<<<<<< HEAD
        with self.get_connection() as conn:
            row = conn.execute(
                '''
                SELECT e.event_id, e.event_name, COUNT(r.registration_id) AS registrations
                FROM events e
                LEFT JOIN registrations r ON r.event_id = e.event_id
                GROUP BY e.event_id, e.event_name
                ORDER BY registrations DESC, e.event_name ASC
                LIMIT 1
                '''
            ).fetchone()

        if not row:
            return None

        return {
            'event_id': row['event_id'],
            'event_name': row['event_name'],
            'registrations': row['registrations']
        }

    def show_registrations(self):
        with self.get_connection() as conn:
            rows = conn.execute(
                '''
                SELECT r.registration_id, e.event_name, s.student_name, s.roll_number, s.department, s.phone
                FROM registrations r
                INNER JOIN events e ON e.event_id = r.event_id
                INNER JOIN students s ON s.student_id = r.student_id
                ORDER BY r.registration_id
                '''
            ).fetchall()

        if not rows:
=======
        if not self.events:
            return None

        results = []
        for event in self.events:
            reg_count = sum(1 for reg in self.registrations if reg['event_id'].lower() == event['event_id'].lower())
            results.append({'event_name': event['event_name'], 'event_id': event['event_id'], 'registrations': reg_count})

        if not results:
            return None

        results.sort(key=lambda item: item['registrations'], reverse=True)
        return results[0]

    def show_registrations(self):
        if not self.registrations:
>>>>>>> feffcf6a718c68e105a5b96ef23f469a584969d4
            print('\nNo registrations yet.')
            return

        print('\nALL REGISTRATIONS')
<<<<<<< HEAD
        for row in rows:
            print(f"{row['registration_id']} | {row['event_name']} | {row['student_name']} | {row['roll_number']} | {row['department']} | {row['phone']}")

    def give_feedback(self):
        print('\nGIVE FEEDBACK (registered students only)')
        self.show_all_events_for_choice()
        event_id = input('\nEnter Event ID: ').strip()
        if not self.get_event_by_id(event_id):
            print('Event not found.')
            return
        roll_number = input('Roll Number: ').strip()
        phone = input('Phone Number used at registration: ').strip()
        rating = input('Rating (1-5): ').strip()
        comment = input('Comment (optional): ').strip()
        ok, message = self.submit_feedback(event_id, roll_number, phone, rating, comment)
        print(message)

    def show_feedback(self):
        with self.get_connection() as conn:
            rows = conn.execute(
                '''
                SELECT e.event_id, e.event_name, s.student_name, f.rating, f.comment
                FROM feedback f
                INNER JOIN registrations r ON r.registration_id = f.registration_id
                INNER JOIN events e ON e.event_id = r.event_id
                INNER JOIN students s ON s.student_id = r.student_id
                ORDER BY e.event_date, f.feedback_id
                '''
            ).fetchall()
        if not rows:
            print('\nNo feedback yet.')
            return
        print('\nALL FEEDBACK')
        for row in rows:
            print(f"{row['event_id']} | {row['event_name']} | {row['student_name']} | {row['rating']}/5 | {row['comment'] or '-'}")
=======
        for reg in self.registrations:
            event = self.get_event_by_id(reg['event_id'])
            event_name = event['event_name'] if event else 'Unknown Event'
            print(f"{reg['registration_id']} | {event_name} | {reg['student_name']} | {reg['roll_number']} | {reg['department']} | {reg['phone']}")
>>>>>>> feffcf6a718c68e105a5b96ef23f469a584969d4

    def run(self):
        while True:
            self.display_menu()
<<<<<<< HEAD
            choice = input('Choose an option (1-9): ').strip()
=======
            choice = input('Choose an option (1-7): ').strip()
>>>>>>> feffcf6a718c68e105a5b96ef23f469a584969d4

            if choice == '1':
                self.add_event()
            elif choice == '2':
                self.register_student()
            elif choice == '3':
                self.show_all_events()
            elif choice == '4':
                self.search_events()
            elif choice == '5':
                self.show_dashboard()
            elif choice == '6':
                self.show_registrations()
            elif choice == '7':
<<<<<<< HEAD
                self.give_feedback()
            elif choice == '8':
                self.show_feedback()
            elif choice == '9':
                print('Goodbye!')
                break
            else:
                print('Invalid option. Please choose from 1 to 9.')
=======
                print('Goodbye!')
                break
            else:
                print('Invalid option. Please choose from 1 to 7.')
>>>>>>> feffcf6a718c68e105a5b96ef23f469a584969d4

            input('\nPress Enter to continue...')


if __name__ == '__main__':
    planner = EventPlanner()
    planner.run()
