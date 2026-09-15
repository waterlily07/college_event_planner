#!/usr/bin/env python3
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


class EventPlanner:
    def __init__(self):
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
        print('7. Exit')
        print('=' * 60)

    def add_event(self):
        print('\nADD NEW EVENT')
        event_name = input('Event Name: ').strip()
        event_date = input('Event Date (YYYY-MM-DD): ').strip()
        venue = input('Venue: ').strip()
        organizer = input('Organizer: ').strip()
        audience = input('Audience (e.g. BCA Students): ').strip()
        category = input('Category (Technical/Cultural/Sports/Workshop): ').strip()
        total_seats = int(input('Total Seats: ').strip())
        description = input('Description: ').strip()

        if not event_name or not event_date:
            print('Event name and date are required.')
            return

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

        popular = self.get_most_popular_event()
        if popular:
            print('\nMost Popular Event:')
            print(f"{popular['event_name']} ({popular['event_id']}) with {popular['registrations']} registrations")
        else:
            print('\nMost Popular Event: No registrations yet')

    def get_most_popular_event(self):
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
            print('\nNo registrations yet.')
            return

        print('\nALL REGISTRATIONS')
        for reg in self.registrations:
            event = self.get_event_by_id(reg['event_id'])
            event_name = event['event_name'] if event else 'Unknown Event'
            print(f"{reg['registration_id']} | {event_name} | {reg['student_name']} | {reg['roll_number']} | {reg['department']} | {reg['phone']}")

    def run(self):
        while True:
            self.display_menu()
            choice = input('Choose an option (1-7): ').strip()

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
                print('Goodbye!')
                break
            else:
                print('Invalid option. Please choose from 1 to 7.')

            input('\nPress Enter to continue...')


if __name__ == '__main__':
    planner = EventPlanner()
    planner.run()
