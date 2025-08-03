#!/usr/bin/env python3

import sqlite3
import csv
import os

from settle.exceptions import PlayerNotFoundException, BusinessLogicException, InvalidInputException


class Tracker:
    def __init__(self):
        self.db_path = os.path.join("data", "settle.db")
        db_dir = os.path.dirname(self.db_path)
        os.makedirs(db_dir, exist_ok=True)

        self.current_date = None
        self.table = {}

        self.allowed_payment_methods = ['cash', 'zelle']

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # 建立主表
            c.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    name TEXT,
                    buy_in INTEGER DEFAULT 0,
                    cash INTEGER DEFAULT 0,
                    zelle INTEGER DEFAULT 0,
                    cash_out INTEGER DEFAULT 0,
                    payout_cash INTEGER DEFAULT 0,
                    payout_zelle INTEGER DEFAULT 0
                )
            ''')
            # 若是舊版資料庫缺少欄位，則自動新增
            for col in ("payout_cash", "payout_zelle"):
                try:
                    c.execute(f"ALTER TABLE records ADD COLUMN {col} INTEGER DEFAULT 0")
                except sqlite3.OperationalError:
                    pass

            # 確保 (date, name) 是唯一的，方便使用 UPSERT
            c.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS idx_records_date_name
                ON records(date, name)
            ''')

            conn.commit()

    def ensure_player_exists(self, name):
        if name not in self.table or self.table[name]["buy_in"] == 0:
            raise PlayerNotFoundException(name)

    def start_game(self, date_str):
        self.current_date = date_str
        self.load_table()

    def load_table(self):
        self.table.clear()
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT name, buy_in, cash, zelle, cash_out, payout_cash, payout_zelle
                  FROM records
                 WHERE date = ?
            """, (self.current_date,))
            for row in c.fetchall():
                name, buy_in, cash, zelle, cash_out, payout_cash, payout_zelle = row
                self.table[name] = {
                    "buy_in": buy_in,
                    "cash": cash,
                    "zelle": zelle,
                    "cash_out": cash_out,
                    "payout_cash": payout_cash,
                    "payout_zelle": payout_zelle
                }
        print(f"Loaded data for {self.current_date}")

    def save_table(self):
        if not self.current_date:
            print("No game in progress.")
            return
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            for name, d in self.table.items():
                c.execute('''
                    INSERT INTO records
                        (date, name, buy_in, cash, zelle, cash_out, payout_cash, payout_zelle)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(date, name) DO UPDATE SET
                        buy_in = excluded.buy_in,
                        cash = excluded.cash,
                        zelle = excluded.zelle,
                        cash_out = excluded.cash_out,
                        payout_cash = excluded.payout_cash,
                        payout_zelle = excluded.payout_zelle
                ''', (
                    self.current_date, name,
                    d["buy_in"], d["cash"], d["zelle"], d["cash_out"],
                    d["payout_cash"], d["payout_zelle"]
                ))
            conn.commit()

    def buy_in(self, name, amount):
        amount = int(amount)
        entry = self.table.setdefault(name, {
            "buy_in": 0, "cash": 0, "zelle": 0,
            "cash_out": 0, "payout_cash": 0, "payout_zelle": 0
        })
        entry["buy_in"] += amount

    def payment(self, name, amount, method):
        # Would raise PlayerNotFoundException if player doesn't exist
        self.ensure_player_exists(name)

        if method not in self.allowed_payment_methods:
            raise InvalidInputException('payment method', method, self.allowed_payment_methods)

        amount = int(amount)
        self.table[name][method] += amount

    def cash_out(self, name, amount):
        # Would raise PlayerNotFoundException if player doesn't exist
        self.ensure_player_exists(name)

        amount = int(amount)
        self.table[name]["cash_out"] += amount

    def pay_out(self, name, amount, method):
        # Would raise PlayerNotFoundException if player doesn't exist
        self.ensure_player_exists(name)

        if method not in self.allowed_payment_methods:
            raise InvalidInputException('payout method', method, self.allowed_payment_methods)

        amount = int(amount)
        self.table[name][f"payout_{method}"] += amount

    def remove_player(self, name):
        # Would raise PlayerNotFoundException if player doesn't exist
        self.ensure_player_exists(name)

        del self.table[name]
        print(f"Player '{name}' remove from the table.")

    def show_table(self):
        # 欄位寬度：name 10, buy_in 5, payment 20, cash_out 5, payout 20
        header = (
            f"{'name':^10} | {'buy_in':^5} | "
            f"{'payment (cash+zelle)':^20} | "
            f"{'cash_out':^5} | "
            f"{'payout (cash+zelle)':^20}"
        )
        print(header)
        print("-" * (len(header) + 2))

        for name, d in self.table.items():
            cash_str = f"({d['cash']:.0f}{'+'}{d['zelle']:.0f})"
            payout_str = f"({d['payout_cash']:.0f}{'+'}{d['payout_zelle']:.0f})"

            print(
                f"{name:^10} | "
                f"{d['buy_in']:^6.0f} | "
                f"{cash_str:^20} | "
                f"{d['cash_out']:^8.0f} | "
                f"{payout_str:^20}"
            )

    def solve(self):
        # Step 1: 計算每個人的 balance
        balances = {}
        total_payment = 0
        total_payout = 0
        total_buy_in = 0
        total_cash_out = 0

        for name, record in self.table.items():
            payment_cash = record.get("cash", 0)
            payment_zelle = record.get("zelle", 0)
            payout_cash = record.get("payout_cash", 0)
            payout_zelle = record.get("payout_zelle", 0)
            buy_in = record.get("buy_in", 0)
            cash_out = record.get("cash_out", 0)

            payment_total = payment_cash + payment_zelle
            payout_total = payout_cash + payout_zelle

            # Balance = -buy_in + payment + cash_out - payout
            balance = -buy_in + payment_total + cash_out - payout_total
            balances[name] = int(round(balance))

            total_payment += payment_total
            total_payout += payout_total
            total_buy_in += buy_in
            total_cash_out += cash_out

        # Step 2: Bank balance
        bank_balance = total_buy_in - total_cash_out - total_payment + total_payout
        balances["bank"] = int(round(bank_balance))

        # Step 3: 顯示原始 balances
        print("Balances:")
        for name, bal in balances.items():
            print(f"{name}: {bal}")
        print()

        # Step 4: 使用新版 DFS + memo 找最少筆交易
        name_list = list(balances.keys())
        amount_list = list(balances.values())
        combined = [(name, amt) for name, amt in balances.items()]

        min_tx = float('inf')
        best_transactions = []
        memo = {}

        def dfs(state, current):
            nonlocal min_tx, best_transactions

            # 排序：正餘額在前，絕對值越大越優先
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

            # 最少還需要幾步
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

        # Step 5: 顯示轉帳
        print("Settlement Transfers:")
        if not best_transactions:
            print("Empty settlement list")
        else:
            for payer, receiver, amount in best_transactions:
                print(f"{payer} pays {receiver} {amount:.0f}")
        print()

        # Step 6: 更新 balances
        for payer, receiver, amount in best_transactions:
            balances[payer] += amount
            balances[receiver] -= amount

        # Step 7: 顯示非 0 餘額
        print("Missing Balances:")
        for name, bal in balances.items():
            if name != "bank" and bal != 0:
                print(f"{name}: {bal:.0f}")
        print()

        # Step 8: 顯示 bank balance（絕對值）
        final_bank_balance = balances["bank"]
        adjusted_bank_balance = abs(final_bank_balance)
        print(f"Bank Final Balance: {adjusted_bank_balance:.0f}")

    def clear(self):
        self.table.clear()
        print("Table cleared.")

    def history(self, date_str):
        self.load_table()
        self.show_table()
        self.summary()

    def summary(self):
        if not self.table:
            print("No data.")
            return

        total_buy_in = sum(d["buy_in"] for d in self.table.values())
        total_cash_out = sum(d["cash_out"] for d in self.table.values())
        total_payment = sum(d["cash"] + d["zelle"] for d in self.table.values())
        total_payout = sum(d["payout_cash"] + d["payout_zelle"] for d in self.table.values())
        bank_balance = total_buy_in - total_cash_out - total_payment + total_payout

        print("\n=== Summary ===")
        print(f"Total Buy In     : {total_buy_in:.0f}")
        print(f"Total Cash Out   : {total_cash_out:.0f}")
        print(f"Total Payment    : {total_payment:.0f}")
        print(f"Total Payout     : {total_payout:.0f}")
        print(f"Bank Balance     : {bank_balance:.0f}")

    def export_csv(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT date, name, buy_in, cash, zelle, cash_out, payout_cash, payout_zelle
                  FROM records
            """)
            rows = c.fetchall()
        filename = self.current_date.replace("/", "_") + ".csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "date", "name", "buy_in",
                "cash", "zelle", "cash_out",
                "payout_cash", "payout_zelle"
            ])
            writer.writerows(rows)
        print("Exported to " + filename)
