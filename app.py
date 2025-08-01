#!/usr/bin/env python3

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sys

# Add the current directory to Python path to import settle module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from settle import tracker

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Initialize database
tracker.init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """Start a new game with a specific date"""
    try:
        data = request.get_json()
        date_str = data.get('date')
        if not date_str:
            return jsonify({'error': 'Date is required'}), 400
        
        tracker.start_game(date_str)
        return jsonify({'message': f'Game started for {date_str}', 'date': date_str})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/game/current', methods=['GET'])
def get_current_game():
    """Get current game date and table data"""
    try:
        return jsonify({
            'current_date': tracker.current_date,
            'table': tracker.table
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/buy-in', methods=['POST'])
def buy_in():
    """Player buy-in"""
    try:
        data = request.get_json()
        name = data.get('name')
        amount = data.get('amount')
        
        if not name or amount is None:
            return jsonify({'error': 'Name and amount are required'}), 400
        
        tracker.buy_in(name, amount)
        tracker.save_table()
        return jsonify({'message': f'{name} bought in for {amount}', 'table': tracker.table})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/payment', methods=['POST'])
def payment():
    """Record player payment"""
    try:
        data = request.get_json()
        name = data.get('name')
        amount = data.get('amount')
        method = data.get('method')
        
        if not name or amount is None or not method:
            return jsonify({'error': 'Name, amount, and method are required'}), 400
        
        if method not in ['cash', 'zelle']:
            return jsonify({'error': 'Method must be cash or zelle'}), 400
        
        tracker.payment(name, amount, method)
        tracker.save_table()
        return jsonify({'message': f'{name} paid {amount} via {method}', 'table': tracker.table})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/cash-out', methods=['POST'])
def cash_out():
    """Record player cash out"""
    try:
        data = request.get_json()
        name = data.get('name')
        amount = data.get('amount')
        
        if not name or amount is None:
            return jsonify({'error': 'Name and amount are required'}), 400
        
        tracker.cash_out(name, amount)
        tracker.save_table()
        return jsonify({'message': f'{name} cashed out {amount}', 'table': tracker.table})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/payout', methods=['POST'])
def payout():
    """Record player payout"""
    try:
        data = request.get_json()
        name = data.get('name')
        amount = data.get('amount')
        method = data.get('method')
        
        if not name or amount is None or not method:
            return jsonify({'error': 'Name, amount, and method are required'}), 400
        
        if method not in ['cash', 'zelle']:
            return jsonify({'error': 'Method must be cash or zelle'}), 400
        
        tracker.pay_out(name, amount, method)
        tracker.save_table()
        return jsonify({'message': f'{name} received payout of {amount} via {method}', 'table': tracker.table})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/players/remove', methods=['DELETE'])
def remove_player():
    """Remove a player from the table"""
    try:
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        tracker.remove_player(name)
        tracker.save_table()
        return jsonify({'message': f'{name} removed from table', 'table': tracker.table})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/table', methods=['GET'])
def get_table():
    """Get current table data"""
    try:
        return jsonify({'table': tracker.table, 'current_date': tracker.current_date})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get game summary"""
    try:
        if not tracker.table:
            return jsonify({'error': 'No data available'}), 400
        
        total_buy_in = sum(d["buy_in"] for d in tracker.table.values())
        total_cash_out = sum(d["cash_out"] for d in tracker.table.values())
        total_payment = sum(d["cash"] + d["zelle"] for d in tracker.table.values())
        total_payout = sum(d["payout_cash"] + d["payout_zelle"] for d in tracker.table.values())
        bank_balance = total_buy_in - total_cash_out - total_payment + total_payout
        
        return jsonify({
            'total_buy_in': total_buy_in,
            'total_cash_out': total_cash_out,
            'total_payment': total_payment,
            'total_payout': total_payout,
            'bank_balance': bank_balance
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/solve', methods=['GET'])
def solve():
    """Calculate settlement transfers"""
    try:
        if not tracker.table:
            return jsonify({'error': 'No data available'}), 400
        
        # Calculate balances
        balances = {}
        total_payment = 0
        total_payout = 0
        total_buy_in = 0
        total_cash_out = 0

        for name, record in tracker.table.items():
            payment_cash = record.get("cash", 0)
            payment_zelle = record.get("zelle", 0)
            payout_cash = record.get("payout_cash", 0)
            payout_zelle = record.get("payout_zelle", 0)
            buy_in = record.get("buy_in", 0)
            cash_out = record.get("cash_out", 0)

            payment_total = payment_cash + payment_zelle
            payout_total = payout_cash + payout_zelle

            balance = -buy_in + payment_total + cash_out - payout_total
            balances[name] = int(round(balance))

            total_payment += payment_total
            total_payout += payout_total
            total_buy_in += buy_in
            total_cash_out += cash_out

        # Bank balance
        bank_balance = total_buy_in - total_cash_out - total_payment + total_payout
        balances["bank"] = int(round(bank_balance))

        # Find minimum transactions using DFS
        name_list = list(balances.keys())
        combined = [(name, amt) for name, amt in balances.items()]

        min_tx = float('inf')
        best_transactions = []
        memo = {}

        def dfs(state, current):
            nonlocal min_tx, best_transactions

            state.sort(key=lambda x: (x[1] >= 0, -abs(x[1])))

            start = 0
            while start < len(state) and state[start][1] == 0:
                start += 1

            if start == len(state):
                if len(current) < min_tx:
                    min_tx = len(current)
                    best_transactions = current[:]
                return

            state_key = tuple(x[1] for x in state)
            if state_key in memo and memo[state_key] <= len(current):
                return
            memo[state_key] = len(current)

            pos = sum(1 for _, amt in state[start:] if amt > 0)
            neg = sum(1 for _, amt in state[start:] if amt < 0)
            min_remaining = max(pos, neg)
            if len(current) + min_remaining >= min_tx:
                return

            for i in range(start + 1, len(state)):
                if state[start][1] * state[i][1] < 0:
                    amt = min(abs(state[start][1]), abs(state[i][1]))
                    original_start = state[start][1]
                    original_i = state[i][1]

                    if state[start][1] < 0:
                        current.append((state[start][0], state[i][0], amt))
                        state[start] = (state[start][0], state[start][1] + amt)
                        state[i] = (state[i][0], state[i][1] - amt)
                    else:
                        current.append((state[i][0], state[start][0], amt))
                        state[start] = (state[start][0], state[start][1] - amt)
                        state[i] = (state[i][0], state[i][1] + amt)

                    dfs([x[:] if isinstance(x, list) else list(x) for x in state], current)

                    current.pop()
                    state[start] = (state[start][0], original_start)
                    state[i] = (state[i][0], original_i)

                    if original_start + original_i == 0:
                        break

        dfs([list(x) for x in combined], [])

        # Update balances after transfers
        final_balances = balances.copy()
        for payer, receiver, amount in best_transactions:
            final_balances[payer] += amount
            final_balances[receiver] -= amount

        # Get non-zero balances (excluding bank)
        missing_balances = {name: bal for name, bal in final_balances.items() 
                          if name != "bank" and bal != 0}

        return jsonify({
            'balances': balances,
            'transactions': [{'payer': t[0], 'receiver': t[1], 'amount': t[2]} 
                           for t in best_transactions],
            'missing_balances': missing_balances,
            'final_bank_balance': abs(final_balances["bank"])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<date_str>', methods=['GET'])
def get_history(date_str):
    """Get historical data for a specific date"""
    try:
        # Save current state
        current_date_backup = tracker.current_date
        current_table_backup = tracker.table.copy()
        
        # Load historical data
        tracker.current_date = date_str
        tracker.load_table()
        
        result = {
            'date': date_str,
            'table': tracker.table.copy()
        }
        
        # Restore current state
        tracker.current_date = current_date_backup
        tracker.table = current_table_backup
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['GET'])
def export_csv():
    """Export current game data to CSV"""
    try:
        if not tracker.current_date:
            return jsonify({'error': 'No active game'}), 400
        
        tracker.export_csv()
        filename = tracker.current_date.replace("/", "_") + ".csv"
        return jsonify({'message': f'Data exported to {filename}', 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save', methods=['POST'])
def save_game():
    """Save current game data"""
    try:
        if not tracker.current_date:
            return jsonify({'error': 'No active game'}), 400
        
        tracker.save_table()
        return jsonify({'message': f'{tracker.current_date} game saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_game():
    """Clear current game data"""
    try:
        if not tracker.current_date:
            return jsonify({'error': 'No active game'}), 400
        
        date_backup = tracker.current_date
        tracker.save_table()
        tracker.clear()
        tracker.current_date = None
        return jsonify({'message': f'{date_backup} game saved and cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
