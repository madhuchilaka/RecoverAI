import json
import os
import sqlite3
import urllib.request

DB_PATH = os.path.join(os.getcwd(), 'data', 'recoverai.db')
BASE_URL = 'http://127.0.0.1:8002'

print('DB_EXISTS=' + str(os.path.exists(DB_PATH)))
conn = sqlite3.connect(DB_PATH)
print('TABLES=' + str([row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]))
print('CUSTOMER_COUNT=' + str(conn.execute('SELECT COUNT(*) FROM customers').fetchone()[0]))
print('TRANSACTION_COUNT=' + str(conn.execute('SELECT COUNT(*) FROM transactions').fetchone()[0]))
print('SUCCESSFUL_TRANSACTION_COUNT=' + str(conn.execute("SELECT COUNT(*) FROM transactions WHERE status='SUCCESS'").fetchone()[0]))
print('FAILED_TRANSACTION_COUNT=' + str(conn.execute("SELECT COUNT(*) FROM transactions WHERE status='FAILED'").fetchone()[0]))
print('ABANDONED_TRANSACTION_COUNT=' + str(conn.execute("SELECT COUNT(*) FROM transactions WHERE status='ABANDONED'").fetchone()[0]))
print('PENDING_TRANSACTION_COUNT=' + str(conn.execute("SELECT COUNT(*) FROM transactions WHERE status='PENDING'").fetchone()[0]))
print('TOTAL_TRANSACTION_VALUE=' + str(conn.execute('SELECT COALESCE(SUM(amount), 0) FROM transactions').fetchone()[0]))
print('FAILED_TRANSACTION_VALUE=' + str(conn.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE status='FAILED'").fetchone()[0]))
conn.close()

with urllib.request.urlopen(BASE_URL + '/health') as resp:
    print('HEALTH=' + json.dumps(json.loads(resp.read().decode('utf-8'))))

for path in [
    '/api/transactions?limit=3&offset=0',
    '/api/transactions/1',
    '/api/customers?limit=2&offset=0',
    '/api/customers/1',
    '/api/recovery-attempts?limit=2&offset=0',
    '/api/audit-logs?limit=2&offset=0',
]:
    with urllib.request.urlopen(BASE_URL + path) as resp:
        payload = json.loads(resp.read().decode('utf-8'))
        print(path + '=' + json.dumps(payload[:1] if isinstance(payload, list) else payload))

with urllib.request.urlopen(BASE_URL + '/api/transactions?limit=2&offset=0') as resp:
    first_page = json.loads(resp.read().decode('utf-8'))
with urllib.request.urlopen(BASE_URL + '/api/transactions?limit=2&offset=2') as resp:
    second_page = json.loads(resp.read().decode('utf-8'))
print('PAGINATION=' + json.dumps({'page1_len': len(first_page), 'page2_len': len(second_page), 'page1_ids': [item['id'] for item in first_page], 'page2_ids': [item['id'] for item in second_page]}))
