from flask import Flask, request, jsonify, abort
from collections import deque
from datetime import datetime
import threading

app = Flask(__name__)

lock = threading.Lock()

# for scalability, we can use a database to store balances and transactions, but for the purposes of this exercise, we will use in-memory data structures
# i don't want to overcomplicate the assignment
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
    data = request.get_json()
    if not data or 'points' not in data:
        abort(400, 'Request must contain points to spend.')

    points_to_spend = data['points']
    if points_to_spend < 0:
        abort(400, 'Points to spend must be positive.')

    with lock:
        total_balance = sum(balances.values())
        if points_to_spend > total_balance:
            abort(400, 'Not enough points to spend.')
            
        temp_transactions = deque()
        points_deducted = {}

        while points_to_spend > 0 and transactions:
            txn = transactions.popleft()
            payer = txn['payer']
            points = txn['points']

            available_points = min(points, points_to_spend)
            if available_points == 0:
                temp_transactions.append(txn)
                continue

            # deduct points
            deduction = min(available_points, points_to_spend)
            balances[payer] -= deduction
            points_to_spend -= deduction

            # record deduction in points_deducted
            points_deducted[payer] = points_deducted.get(payer, 0) - deduction

            # adjust transaction points
            remaining_points = points - deduction
            if remaining_points != 0:
                txn['points'] = remaining_points
                temp_transactions.appendleft(txn)

        # re-add any unused transactions
        transactions.extendleft(temp_transactions)

        # build the response
        response = []
        for payer, points in points_deducted.items():
            response.append({'payer': payer, 'points': points})

        return jsonify(response), 200

@app.route('/balance', methods=['GET'])
def get_balance():
    with lock:
        return jsonify(balances), 200


if __name__ == '__main__':
    app.run(port=8000) # port 8000