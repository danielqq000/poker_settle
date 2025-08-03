from settle.tracker import Tracker


def main():
    tracker = Tracker()
    tracker.init_db()
    while True:
        try:
            cmd = input(">> ").strip()
            if not cmd:
                continue
            args = cmd.split()
            cmd0 = args[0].lower()

            if cmd0 == "game":
                if len(args) != 2:
                    print("Usage: game <MM/DD>")
                elif tracker.current_date:
                    tracker.save_table()
                    tracker.start_game(args[1])
                else:
                    tracker.start_game(args[1])
            elif cmd0 == "history":
                if len(args) != 2:
                    print("Usage: history <MM/DD>")
                else:
                    tracker.history(args[1])
            elif cmd0 == "exit":
                if tracker.current_date:
                    tracker.save_table()
                    print(f"{tracker.current_date} game saved.")
                break
            elif not tracker.current_date:
                print("Please start a game first: game <MM/DD>")
            elif cmd0 == "buy" and args[1].lower() == "in":
                tracker.buy_in(args[2], args[3])
                tracker.save_table()
            elif cmd0 == "payment":
                tracker.payment(args[1], args[2], args[3].lower())
                tracker.save_table()
            elif cmd0 == "cash" and args[1].lower() == "out":
                tracker.cash_out(args[2], args[3])
                tracker.save_table()
            elif cmd0 == "pay" and args[1].lower() == "out":
                tracker.pay_out(args[2], args[3], args[4].lower())
                tracker.save_table()
            elif cmd0 == "remove":
                if len(args) != 2:
                    print("Usage: remove <name>")
                else:
                    tracker.remove_player(args[1])
                    tracker.save_table()
            elif cmd0 == "show":
                tracker.show_table()
            elif cmd0 == "export":
                tracker.export_csv()
            elif cmd0 == "summary":
                tracker.summary()
            elif cmd0 == "solve":
                tracker.solve()
            elif cmd0 == "save":
                tracker.save_table()
                print(f"{tracker.current_date} game saved.")
            elif cmd0 == "clear":
                tracker.save_table()
                print(f"{tracker.current_date} game saved.")
                tracker.clear()
                tracker.current_date = None
            else:
                print("Invalid command.")
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
