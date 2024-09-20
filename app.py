from flask import Flask, request, jsonify, abort
from collections import deque
from datetime import datetime
import threading

app = Flask(__name__)

lock = threading.Lock()

balances = {}
transactions = deque()


@app.route('/add', methods=['POST'])
def add_points():
    data = request.get_json()
    fields = {'payer', 'points', 'timestamp'}
    if not data or not fields.issubset(data.keys()):
        abort(400, 'Request must contain payer, points, and timestamp fields')
    
    payer = data['payer']
    points = data['points']
    timestamp_str = data['timestamp']
    
    try:
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ') # convert to datetime object
    except ValueError:
        abort(400, 'Timestamp must be in format YYYY-MM-DDTHH:MM:SSZ')
        
    with lock:
        # update balances
        balances[payer] = balances.get(payer, 0) + points

        # check for negative balance
        if balances[payer] < 0:
            abort(400, f'Payer {payer} cannot have negative balance.')

        # insert transaction in sorted order
        transaction = {
            'payer': payer,
            'points': points,
            'timestamp': timestamp
        }
        # insert transaction, while maintaining sorted order
        inserted = False
        for idx, existing_txn in enumerate(transactions):
            if transaction['timestamp'] < existing_txn['timestamp']:
                transactions.insert(idx, transaction)
                inserted = True
                break
        if not inserted:
            transactions.append(transaction)

    return '', 200

@app.route('/spend', methods=['POST'])
def spend_points():
    pass

@app.route('/balance', methods=['GET'])
def get_balance():
    pass


if __name__ == '__main__':
    app.run(port=8000)