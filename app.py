#!/usr/bin/env python3
"""Web front-end for the College Event Planner (Flask + the same SQLite DB as the CLI)."""
import os
import secrets
from datetime import date

from flask import Flask, abort, flash, redirect, render_template, request, url_for

from event_planner import EventPlanner

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
planner = EventPlanner()

CATEGORIES = ['Technical', 'Cultural', 'Sports', 'Workshop']


def event_cards(where='', params=()):
    """Events with organizers, seats left and rating summary, ready for templates."""
    with planner.get_connection() as conn:
        rows = conn.execute(
            f'''
            SELECT e.*, COUNT(DISTINCT r.registration_id) AS registered,
                   (SELECT GROUP_CONCAT(o.name, ', ')
                      FROM event_organizers eo
                      JOIN organizers o ON o.organizer_id = eo.organizer_id
                     WHERE eo.event_id = e.event_id) AS organizers
            FROM events e
            LEFT JOIN registrations r ON r.event_id = e.event_id
            {where}
            GROUP BY e.event_id
            ORDER BY e.event_date
            ''', params).fetchall()
    cards = []
    for row in rows:
        card = dict(row)
        card['seats_left'] = card['total_seats'] - card['registered']
        card['rating'] = planner.get_rating_summary(card['event_id'])
        card['is_past'] = card['event_date'] < date.today().isoformat()
        cards.append(card)
    return cards


@app.route('/')
def index():
    q = request.args.get('q', '').strip().lower()
    category = request.args.get('category', '').strip()
    where, params = [], []
    if q:
        like = f'%{q}%'
        where.append('''(LOWER(e.event_name) LIKE ? OR LOWER(e.venue) LIKE ? OR LOWER(e.category) LIKE ?
                        OR e.event_id IN (SELECT eo.event_id FROM event_organizers eo
                                          JOIN organizers o ON o.organizer_id = eo.organizer_id
                                          WHERE LOWER(o.name) LIKE ?))''')
        params += [like] * 4
    if category in CATEGORIES:
        where.append('e.category = ?')
        params.append(category)
    clause = ('WHERE ' + ' AND '.join(where)) if where else ''
    with planner.get_connection() as conn:
        totals = conn.execute(
            'SELECT (SELECT COUNT(*) FROM events) AS events, (SELECT COUNT(*) FROM registrations) AS regs,'
            ' (SELECT AVG(rating) FROM feedback) AS avg_rating').fetchone()
    stats = {'events': totals['events'], 'regs': totals['regs'],
             'avg': round(totals['avg_rating'], 1) if totals['avg_rating'] else None}
    return render_template('index.html', events=event_cards(clause, tuple(params)), stats=stats,
                           q=request.args.get('q', ''), category=category, categories=CATEGORIES)


@app.route('/event/<event_id>')
def event_detail(event_id):
    cards = event_cards('WHERE e.event_id = ?', (event_id,))
    if not cards:
        abort(404)
    with planner.get_connection() as conn:
        reviews = conn.execute(
            '''
            SELECT s.student_name, f.rating, f.comment, f.created_at
            FROM feedback f
            JOIN registrations r ON r.registration_id = f.registration_id
            JOIN students s ON s.student_id = r.student_id
            WHERE r.event_id = ?
            ORDER BY f.feedback_id DESC
            ''', (cards[0]['event_id'],)).fetchall()
    return render_template('event.html', event=cards[0], reviews=reviews)


@app.route('/event/<event_id>/register', methods=['POST'])
def register(event_id):
    f = {k: request.form.get(k, '').strip() for k in ('student_name', 'roll_number', 'department', 'phone')}
    if not f['student_name'] or not f['roll_number'] or not f['phone']:
        flash('Name, roll number and phone are required.', 'error')
        return redirect(url_for('event_detail', event_id=event_id) + '#register')

    conn = planner.get_connection()
    try:
        conn.execute('BEGIN IMMEDIATE')  # lock so two people cannot take the last seat
        event = conn.execute('SELECT * FROM events WHERE event_id = ?', (event_id,)).fetchone()
        if not event:
            abort(404)
        taken = conn.execute('SELECT COUNT(*) FROM registrations WHERE event_id = ?', (event_id,)).fetchone()[0]
        if taken >= event['total_seats']:
            flash('Sorry, this event is full.', 'error')
        else:
            student = conn.execute('SELECT * FROM students WHERE LOWER(roll_number) = LOWER(?)',
                                   (f['roll_number'],)).fetchone()
            if student:
                if student['phone'] and student['phone'] != f['phone']:
                    # Stops someone re-registering with another student's roll number and changing their details.
                    flash('This roll number is already on file with a different phone number.', 'error')
                    conn.rollback()
                    return redirect(url_for('event_detail', event_id=event_id) + '#register')
                student_id = student['student_id']
                conn.execute('UPDATE students SET student_name=?, department=?, phone=? WHERE student_id=?',
                             (f['student_name'], f['department'], f['phone'], student_id))
            else:
                student_id = conn.execute(
                    'INSERT INTO students (student_name, roll_number, department, phone) VALUES (?,?,?,?)',
                    (f['student_name'], f['roll_number'], f['department'], f['phone'])).lastrowid
            if conn.execute('SELECT 1 FROM registrations WHERE event_id=? AND student_id=?',
                            (event_id, student_id)).fetchone():
                flash('You are already registered for this event.', 'error')
            else:
                reg_id = planner.generate_registration_id(conn)
                conn.execute('INSERT INTO registrations (registration_id, event_id, student_id) VALUES (?,?,?)',
                             (reg_id, event_id, student_id))
                flash(f'You are registered! Your registration ID is {reg_id}.', 'success')
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for('event_detail', event_id=event_id) + '#register')


@app.route('/event/<event_id>/feedback', methods=['POST'])
def feedback(event_id):
    if not planner.get_event_by_id(event_id):
        abort(404)
    ok, message = planner.submit_feedback(
        event_id, request.form.get('roll_number', ''), request.form.get('phone', ''),
        request.form.get('rating'), request.form.get('comment', ''))
    flash(message, 'success' if ok else 'error')
    return redirect(url_for('event_detail', event_id=event_id) + '#feedback')


@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        f = {k: request.form.get(k, '').strip() for k in
             ('event_name', 'event_date', 'venue', 'organizers', 'audience', 'category', 'description')}
        try:
            seats = int(request.form.get('total_seats', ''))
            date.fromisoformat(f['event_date'])
        except ValueError:
            flash('Please enter a valid date and a whole number of seats.', 'error')
            return render_template('add_event.html', form=request.form, categories=CATEGORIES)
        if not f['event_name'] or seats < 1:
            flash('Event name is required and seats must be at least 1.', 'error')
            return render_template('add_event.html', form=request.form, categories=CATEGORIES)
        with planner.get_connection() as conn:
            event_id = planner.generate_event_id(conn)
            conn.execute(
                'INSERT INTO events (event_id, event_name, event_date, venue, audience, category, total_seats, description)'
                ' VALUES (?,?,?,?,?,?,?,?)',
                (event_id, f['event_name'], f['event_date'], f['venue'], f['audience'],
                 f['category'], seats, f['description']))
            names = [n.strip() for n in f['organizers'].split(',') if n.strip()] or ['College Team']
            for name in names:
                oid = planner.ensure_organizer(conn, name)
                conn.execute('INSERT OR IGNORE INTO event_organizers VALUES (?,?)', (event_id, oid))
        flash(f'Event created: {event_id}', 'success')
        return redirect(url_for('event_detail', event_id=event_id))
    return render_template('add_event.html', form={}, categories=CATEGORIES)


@app.route('/dashboard')
def dashboard():
    events = event_cards()
    total_regs = sum(e['registered'] for e in events)
    popular = max(events, key=lambda e: e['registered'], default=None)
    rated = [e for e in events if e['rating']['average']]
    top_rated = max(rated, key=lambda e: (e['rating']['average'], e['rating']['total']), default=None)
    return render_template('dashboard.html', events=events, total_regs=total_regs,
                           popular=popular if popular and popular['registered'] else None, top_rated=top_rated)


@app.errorhandler(404)
def not_found(_):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
