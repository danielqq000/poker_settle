# 🌐 Poker Settlement Tracker - Web Application

A modern web-based version of the Poker Settlement Tracker, featuring RESTful APIs and an intuitive HTML/JavaScript frontend.

## 🚀 Features

### Web Interface
- **Responsive Design**: Bootstrap-based UI that works on desktop and mobile
- **Real-time Updates**: Instant table updates after each action
- **Interactive Forms**: Easy-to-use forms for all poker operations
- **Visual Feedback**: Toast notifications and color-coded balances
- **Settlement Visualization**: Clear display of transfers and balances

### API Endpoints
- **Game Management**: Start games, get current game status
- **Player Operations**: Buy-in, payments, cash-out, payouts
- **Data Analysis**: Summary statistics and settlement calculations
- **Data Export**: CSV export functionality
- **Historical Data**: Access to previous games

## 📋 Prerequisites

- Python 3.7+
- pip (Python package installer)

## 🛠️ Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/danielqq000/poker_settle.git
   cd poker_settle
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage

### Starting the Web Application

1. **Run the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

### Using the Web Interface

#### 1. Start a Game
- Enter a date in MM/DD format (e.g., "08/01")
- Click "Start Game"
- The current game will be displayed

#### 2. Player Actions
- **Buy In**: Enter player name and amount, click "Buy In"
- **Payment**: Record cash or Zelle payments from players
- **Cash Out**: Record when players cash out chips
- **Payout**: Record cash or Zelle payouts to players

#### 3. Game Management
- **Summary**: View total buy-ins, payments, cash-outs, and bank balance
- **Solve**: Calculate optimal settlement transfers
- **Export**: Export current game data to CSV
- **Save**: Manually save current game state

#### 4. Settlement Analysis
The "Solve" feature provides:
- Individual player balances
- Minimum number of transfers needed
- Step-by-step transfer instructions
- Final bank balance verification

## 🔌 API Reference

### Game Endpoints

#### Start Game
```http
POST /api/game/start
Content-Type: application/json

{
  "date": "08/01"
}
```

#### Get Current Game
```http
GET /api/game/current
```

### Player Endpoints

#### Buy In
```http
POST /api/players/buy-in
Content-Type: application/json

{
  "name": "Alice",
  "amount": 100
}
```

#### Record Payment
```http
POST /api/players/payment
Content-Type: application/json

{
  "name": "Alice",
  "amount": 50,
  "method": "cash"
}
```

#### Cash Out
```http
POST /api/players/cash-out
Content-Type: application/json

{
  "name": "Alice",
  "amount": 75
}
```

#### Record Payout
```http
POST /api/players/payout
Content-Type: application/json

{
  "name": "Alice",
  "amount": 25,
  "method": "zelle"
}
```

#### Remove Player
```http
DELETE /api/players/remove
Content-Type: application/json

{
  "name": "Alice"
}
```

### Data Endpoints

#### Get Table Data
```http
GET /api/table
```

#### Get Summary
```http
GET /api/summary
```

#### Calculate Settlement
```http
GET /api/solve
```

#### Get Historical Data
```http
GET /api/history/08/01
```

#### Export Data
```http
GET /api/export
```

#### Save Game
```http
POST /api/save
```

#### Clear Game
```http
POST /api/clear
```

## 🏗️ Architecture

### Backend (Flask)
- **app.py**: Main Flask application with RESTful API endpoints
- **settle/tracker.py**: Core business logic (unchanged from CLI version)
- **SQLite Database**: Persistent data storage in `data/settle.db`

### Frontend
- **templates/index.html**: Single-page application with Bootstrap UI
- **JavaScript**: Async API calls with fetch() and DOM manipulation
- **Bootstrap 5**: Responsive CSS framework
- **Font Awesome**: Icons for better UX

### Key Design Decisions
1. **RESTful API**: Clean separation between frontend and backend
2. **Single Page App**: All functionality on one page for simplicity
3. **Real-time Updates**: Table refreshes after each operation
4. **Error Handling**: Toast notifications for user feedback
5. **Responsive Design**: Works on desktop and mobile devices

## 📊 Data Flow

1. **User Action** → Frontend JavaScript
2. **API Call** → Flask Backend
3. **Business Logic** → tracker.py functions
4. **Database Update** → SQLite
5. **Response** → JSON data back to frontend
6. **UI Update** → DOM manipulation and visual feedback

## 🔧 Development

### Project Structure
```
poker_settle/
├── app.py                 # Flask web server
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── settle/
│   └── tracker.py        # Core logic (unchanged)
├── data/
│   └── settle.db         # SQLite database
├── run.py                # Original CLI entry point
└── README_WEBAPP.md      # This file
```

### Adding New Features

1. **Backend**: Add new endpoints in `app.py`
2. **Frontend**: Add UI elements and JavaScript functions in `index.html`
3. **Core Logic**: Extend functionality in `settle/tracker.py` if needed

### Testing

The web application maintains full compatibility with the original CLI version:
- Same database structure
- Same business logic
- Same settlement algorithm
- Data can be accessed via both interfaces

## 🚀 Deployment

### Development
```bash
python app.py
# Server runs on http://localhost:5000
```

### Production
For production deployment, consider:
- Using a WSGI server like Gunicorn
- Setting up a reverse proxy (nginx)
- Using environment variables for configuration
- Implementing proper logging and monitoring

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔒 Security Considerations

- **Input Validation**: All API endpoints validate input data
- **Error Handling**: Proper error responses without exposing internals
- **CORS**: Configured for cross-origin requests if needed
- **SQL Injection**: Using parameterized queries via SQLite

For production use, consider adding:
- Authentication and authorization
- Rate limiting
- HTTPS encryption
- Input sanitization
- Session management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both CLI and web interfaces
5. Submit a pull request

## 📝 License

Same as the original project - feel free to use and modify for your poker games!

## 🎯 Future Enhancements

- **Multi-game Management**: Switch between different games
- **Player Profiles**: Store player information and history
- **Game Templates**: Predefined buy-in amounts and structures
- **Real-time Collaboration**: Multiple users managing the same game
- **Mobile App**: Native mobile application
- **Advanced Analytics**: Charts and statistics over time
- **Backup/Restore**: Cloud backup functionality

---

**Enjoy your poker nights with the new web interface! 🃏💰**
