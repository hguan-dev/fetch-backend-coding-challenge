from flask import Flask, request, jsonify, abort
from collections import deque
from datetime import datetime
import threading

app = Flask(__name__)

lock = threading.Lock()

balanced = {}
transactions = deque()


@app.route('/add', methods=['POST'])
def add_points():
    pass

@app.route('/spend', methods=['POST'])
def spend_points():
    pass

@app.route('/balance', methods=['GET'])
def get_balance():
    pass


if __name__ == '__main__':
    app.run(port=8000)