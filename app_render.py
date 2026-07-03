"""Deployment del CRM a Render."""
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(__file__), 'data', 'crm.db'))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, email TEXT, phone TEXT,
        wedding_date TEXT, venue TEXT, package TEXT,
        status TEXT DEFAULT 'nuevo', source TEXT, notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER, name TEXT NOT NULL, partner_name TEXT,
        email TEXT, phone TEXT, wedding_date TEXT, venue TEXT,
        package TEXT, package_price REAL, deposit REAL, paid REAL DEFAULT 0,
        status TEXT DEFAULT 'confirmado', notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL, wedding_date TEXT, ceremony_time TEXT,
        venue TEXT, package TEXT, photographers TEXT, videographers TEXT,
        status TEXT DEFAULT 'pendiente', notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL, amount REAL NOT NULL,
        concept TEXT, method TEXT, status TEXT DEFAULT 'pendiente',
        due_date TEXT, paid_date TEXT, recurrente_link TEXT,
        notes TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    conn.commit()
    c.execute('SELECT COUNT(*) c FROM clients')
    if c.fetchone()['c'] == 0:
        clients = [
            ('Carlos Zelaya', 'Ana López', 'carlos@z.com', '+502 5555-0001', '2026-07-04', 'Antigua Guatemala', 'Mix Platinum', 29500, 14750, 14750, 'confirmado'),
            ('Geraldine Barberena', 'Juan Manuel', 'geraldine@g.com', '+502 5555-0002', '2026-07-18', 'Hotel Atitlán, Panajachel', 'Mix Gold', 20500, 10250, 10250, 'confirmado'),
            ('Cindy Cerezo', '', 'cindy@c.com', '+502 5555-0003', '2026-07-25', 'Sanarate', 'Foto Gold', 13500, 6750, 6750, 'confirmado'),
            ('Karen Sandoval', '', 'karen@k.com', '+502 5555-0004', '2026-08-01', 'Antigua Guatemala', 'Mix Platinum', 29500, 14750, 0, 'confirmado'),
            ('Daniel Dubuc', '', 'daniel@d.com', '+502 5555-0005', '2026-08-15', 'Ciudad Guatemala', 'Mix Platinum', 29500, 14750, 14750, 'confirmado'),
            ('Hector y Katia', '', 'hector@h.com', '+502 5555-0006', '2026-08-22', 'Por confirmar', 'Mix Gold', 20500, 10250, 5000, 'confirmado'),
            ('Anna Beatriz Cermeño', '', 'anna@a.com', '+502 5555-0007', '2026-11-21', 'Guatemala', 'Mix Gold', 20500, 10250, 0, 'confirmado'),
            ('Jefferson y Karen', '', 'j@k.com', '+502 5555-0008', '2026-11-14', 'San Cristóbal Mixco', 'Foto Gold', 13500, 6750, 0, 'confirmado'),
            ('Wilson Zapeta', '', 'wilson@w.com', '+502 5555-0009', '2027-01-16', 'Guatemala', 'Foto Gold', 13500, 6750, 0, 'confirmado'),
            ('Kéller Zapote', '', 'keller@k.com', '+502 5555-0010', '2027-01-23', 'Santo Domingo Xenacoj', 'Mix Gold', 20500, 10250, 0, 'confirmado'),
            ('Jessica Estrada', '', 'jess@e.com', '+502 5555-0011', '2027-01-30', 'San Gregorio Hotel', 'Mix Gold', 20500, 10250, 0, 'confirmado'),
            ('Javier Cordon', 'Alejandra Morales', 'javier@jc.com', '+502 5555-0012', '2027-04-17', 'Jardín El Cerro, Fraijanes', 'Mix Gold', 20500, 10250, 0, 'confirmado'),
        ]
        for cl in clients:
            c.execute('''INSERT INTO clients (name, partner_name, email, phone, wedding_date, venue, package, package_price, deposit, paid, status) VALUES (?,?,?,?,?,?,?,?,?,?,?)''', cl)
        leads = [
            ('María González', 'maria@g.com', '+502 5555-1001', '2026-12-15', 'Antigua', 'Foto Gold', 'nuevo', 'WhatsApp'),
            ('Luis Pérez', 'luis@p.com', '+502 5555-1002', '2027-02-20', 'Ciudad Guatemala', 'Mix Gold', 'contactado', 'Instagram'),
            ('Ana Rodríguez', 'ana@r.com', '+502 5555-1003', '2026-09-10', 'Antigua', 'Mix Platinum', 'consulta', 'Referido'),
        ]
        for l in leads:
            c.execute('''INSERT INTO leads (name, email, phone, wedding_date, venue, package, status, source) VALUES (?,?,?,?,?,?,?,?)''', l)
        c.execute('SELECT id FROM clients WHERE paid < deposit')
        for row in c.fetchall()[:5]:
            c.execute('''INSERT INTO payments (client_id, amount, concept, status, due_date) VALUES (?,?,?,?,?)''', (row[0], 5000, 'Anticipo', 'pendiente', '2026-07-15'))
        conn.commit()
    conn.close()

@app.context_processor
def inject_globals():
    conn = get_db()
    leads_count = conn.execute("SELECT COUNT(*) c FROM leads WHERE status='nuevo'").fetchone()['c']
    total_pending = conn.execute("SELECT SUM(amount) s FROM payments WHERE status='pendiente'").fetchone()['s'] or 0
    conn.close()
    return dict(leads_count=leads_count, total_pending=total_pending)

@app.route('/')
def calendar():
    conn = get_db()
    clients = conn.execute('SELECT * FROM clients WHERE wedding_date IS NOT NULL ORDER BY wedding_date').fetchall()
    conn.close()
    events = [{'id': c['id'], 'title': f"{c['name']} ({c['package']})", 'date': c['wedding_date'], 'venue': c['venue'], 'package': c['package'], 'status': c['status']} for c in clients]
    return render_template('calendar.html', events=events, clients=clients)

@app.route('/leads')
def leads():
    conn = get_db()
    leads = conn.execute('SELECT * FROM leads ORDER BY created_at DESC').fetchall()
    counts = {s: conn.execute(f"SELECT COUNT(*) c FROM leads WHERE status='{s}'").fetchone()['c'] for s in ['nuevo','contactado','consulta','cerrado']}
    conn.close()
    return render_template('leads.html', leads=leads, counts=counts)

@app.route('/clients')
def clients():
    conn = get_db()
    clients = conn.execute('SELECT * FROM clients ORDER BY wedding_date').fetchall()
    conn.close()
    return render_template('clients.html', clients=clients)

@app.route('/jobs')
def jobs():
    conn = get_db()
    jobs = conn.execute('''SELECT j.*, c.name as client_name, c.partner_name FROM jobs j JOIN clients c ON j.client_id = c.id ORDER BY j.wedding_date''').fetchall()
    clients_no_job = conn.execute('''SELECT * FROM clients WHERE id NOT IN (SELECT client_id FROM jobs)''').fetchall()
    conn.close()
    return render_template('jobs.html', jobs=jobs, clients=clients_no_job)

@app.route('/payments')
def payments():
    conn = get_db()
    payments = conn.execute('''SELECT p.*, c.name as client_name FROM payments p JOIN clients c ON p.client_id = c.id ORDER BY p.due_date''').fetchall()
    pending = [p for p in payments if p['status'] == 'pendiente']
    paid = [p for p in payments if p['status'] == 'pagado']
    total_pending = sum(p['amount'] for p in pending)
    total_paid = sum(p['amount'] for p in paid)
    conn.close()
    return render_template('payments.html', pending=pending, paid=paid, total_pending=total_pending, total_paid=total_paid)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/api/payments/<int:payment_id>/pay', methods=['POST'])
def api_mark_paid(payment_id):
    conn = get_db()
    p = conn.execute('SELECT * FROM payments WHERE id=?', (payment_id,)).fetchone()
    if p:
        conn.execute('UPDATE payments SET status="pagado", paid_date=CURRENT_TIMESTAMP WHERE id=?', (payment_id,))
        conn.execute('UPDATE clients SET paid = paid + ? WHERE id=?', (p['amount'], p['client_id']))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8765))
    app.run(debug=False, host='0.0.0.0', port=port)