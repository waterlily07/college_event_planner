"""Optional: fill the database with a few sample events and students for testing."""
from event_planner import EventPlanner

planner = EventPlanner()
with planner.get_connection() as conn:
    if conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]:
        print('Database already has events - nothing added.')
        raise SystemExit

    events = [
        ('Hackathon 2026', '2026-11-12', 'Main Auditorium', 'BCA Students', 'Technical', 60, 'Build something in 24 hours.', ['Coding Club']),
        ('Cultural Night', '2026-11-20', 'Open Air Theatre', 'All Students', 'Cultural', 200, 'Music, dance and drama.', ['Cultural Committee', 'Student Council']),
        ('Inter-School Cricket', '2026-10-05', 'College Ground', 'All Students', 'Sports', 40, 'Knockout tournament.', ['Sports Club']),
        ('Web Dev Workshop', '2026-11-03', 'Lab 4', 'BCA Students', 'Workshop', 30, 'Hands-on HTML, CSS and JS.', ['Coding Club']),
    ]
    for name, d, venue, aud, cat, seats, desc, orgs in events:
        eid = planner.generate_event_id(conn)
        conn.execute('INSERT INTO events VALUES (?,?,?,?,?,?,?,?)', (eid, name, d, venue, aud, cat, seats, desc))
        for o in orgs:
            conn.execute('INSERT OR IGNORE INTO event_organizers VALUES (?,?)', (eid, planner.ensure_organizer(conn, o)))
print('Sample events added. Register students from the web page or the CLI.')
