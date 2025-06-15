# 💰 Settle.py – Poker Game Settlement Tracker

一款專為 Poker 私人局或桌遊聚會設計的結帳工具，使用 SQLite 儲存資料，支援多人買入、付款、兌現、派彩與結算轉帳推薦。

## 🧩 功能介紹

- 📦 **資料永久儲存**：使用 SQLite 自動建立資料表，依照日期記錄每場局
- 📝 **即時編輯**：隨時可新增玩家、買入、付款或兌現紀錄
- 📊 **餘額試算與自動結算**：內建演算法推薦最少筆轉帳以達成全員清帳
- 📤 **CSV 匯出**：可將指定日期資料匯出為 Excel 可讀的 `.csv` 檔案
- 🧠 **自動校正**：自動偵測遺失欄位、自動修復
- 🛠️ **CLI 介面**：簡潔直覺，使用命令快速操作

---

## 🗃 資料結構

SQLite 資料庫檔案：`settle.db`  
資料表：`records`

| 欄位名稱       | 說明                       |
|----------------|----------------------------|
| id             | 自動編號（主鍵）          |
| date           | 遊戲日期（格式: MM/DD）   |
| name           | 玩家名稱                   |
| buy_in         | 買入金額                   |
| cash           | 現金付款金額               |
| zelle          | Zelle 付款金額             |
| cash_out       | 現金兌換金額               |
| payout_cash    | 現金派彩金額               |
| payout_zelle   | Zelle 派彩金額             |

---

## ▶️ 使用方法

### 啟動程式

```bash
python3 run.py
```

### 基本指令

| 指令                                  | 說明             |
| ----------------------------------- | -------------- |
| `game <MM/DD>`                      | 開始新的一局         |
| `buy in <name> <amount>`            | 玩家買入           |
| `payment <name> <amt> <cash/zelle>` | 玩家付款方式         |
| `cash out <name> <amount>`          | 玩家兌現           |
| `pay out <name> <amt> <cash/zelle>` | 派彩紀錄           |
| `show`                              | 顯示目前所有玩家帳目     |
| `summary`                           | 顯示總計資訊         |
| `solve`                             | 自動計算最少轉帳結算     |
| `export`                            | 匯出目前資料為 CSV 檔案 |
| `history <MM/DD>`                   | 查看特定日期資料       |
| `remove <name>`                     | 刪除玩家           |
| `save`                              | 儲存目前資料         |
| `clear`                             | 清除當前遊戲資料       |
| `exit`                              | 離開程式（會自動儲存）    |

---

## 🧠 結算邏輯 (Solve)

結算演算法會計算每位玩家的：

```
Balance = -buy_in + payment + cash_out - payout
```

再透過 **DFS + Memoization** 最佳化，找出筆數最少的轉帳清單，達到所有玩家清帳為零（含虛擬銀行）。

---

## 📝 範例

```
>> game 06/07
>> buy in Alice 100
>> buy in Bob 100
>> payment Alice 50 cash
>> cash out Bob 30
>> pay out Bob 50 zelle
>> show
>> solve
>> export
>> exit
```

---

## 📁 專案結構

```
settle/
├── settle.py         # 主程式
├── settle.db         # 自動建立的資料庫檔案
├── 06_07.csv         # 匯出資料
└── README.md         # 說明文件
```

---

## 🔧 開發與貢獻

目前為單檔腳本設計，如需擴充：

* 將功能模組化（分拆成多檔案）
* 加入網頁前端 / Discord bot 操作介面
* 改為使用 PostgreSQL / 雲端儲存

Pull requests 與 issue 歡迎提出！

---

## 🧑‍💻 作者

Daniel Huang

Feel free to fork, modify, and use it for your next game night.
