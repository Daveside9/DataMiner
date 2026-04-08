# DataMiner - Historical Pattern Scraper

A powerful web scraping system for analyzing historical sports data and betting patterns.

## 🚀 Quick Start

### Option 1: Complete Startup (Recommended)
```bash
cd my-portfolio/DataMiner
python start_dataminer.py
```
This starts both backend and frontend servers automatically and opens your browser.

### Option 2: Manual Startup
```bash
# Terminal 1 - Start Backend
cd my-portfolio/DataMiner
python start_backend.py

# Terminal 2 - Start Frontend  
cd my-portfolio/DataMiner
python start_frontend.py
```

### Option 3: Test Backend Only
```bash
cd my-portfolio/DataMiner
python test_backend.py
```

## 🎯 How to Use Historical Pattern Scraper

1. **Open the Interface**: http://localhost:3000/historical-pattern-scraper.html

2. **Enter Website URL**: 
   - BBC Sport: `https://www.bbc.com/sport/football`
   - Livescore: `https://www.livescore.com/en/football/`
   - ESPN: `https://www.espn.com/soccer/`

3. **Enter Team Name**: e.g., "Real Madrid", "Manchester City", "Barcelona"

4. **Choose Time Period**: From 1 week to all available history

5. **Select Pattern Type**:
   - **Match Frequency**: How often the team plays
   - **Home vs Away Pattern**: Home/away match distribution
   - **Weekly Pattern**: Which days they play most
   - **Opponent Strength**: Most common opponents
   - **Match Density**: Games per week analysis

6. **Test First**: Click "🧪 Test Selectors" to verify CSS selectors work

7. **Start Scraping**: Click "🚀 Start Historical Scraping"

## 🔧 CSS Selectors

The system uses CSS selectors to find team names, dates, and match data. Default selectors work for most sports sites:

```
home_teams: .team-home, .home-team, .participant-home
away_teams: .team-away, .away-team, .participant-away
dates: .date, .match-date, .time
opponents: .opponent, .vs-team
venues: .venue, .stadium, .location
```

### Finding Custom Selectors:
1. Right-click on team names → "Inspect Element"
2. Copy the CSS selector
3. Test with "🧪 Test Selectors" button

## 🎲 Site Presets

Quick presets for popular sports websites:
- **🎲 Bet365**: Betting site selectors
- **⚽ Livescore**: Live scores and results
- **⚡ Flashscore**: Sports results
- **📺 BBC Sport**: BBC Sports section
- **🏆 ESPN**: ESPN Soccer section

## 📊 Pattern Analysis Types

### Match Frequency
- Analyzes how often a team plays
- Calculates average gaps between matches
- Predicts next match timing
- Shows matches per week

### Home vs Away Pattern
- Home/away match distribution
- Current home/away streak
- Predicts next match location
- Balance analysis

### Weekly Pattern
- Which days team plays most
- Day-of-week distribution
- Weekly consistency analysis

### Match Density
- Games per week analysis
- Busy vs quiet periods
- Match scheduling patterns

## 🛠️ Troubleshooting

### "Cannot convert undefined or null to object"
- **Cause**: CSS selectors not finding data
- **Solution**: Click "🧪 Test Selectors" first
- **Fix**: Try different website or update selectors

### "Backend not running"
- **Cause**: Flask server not started
- **Solution**: Run `python start_backend.py`
- **Check**: Visit http://localhost:5000/api/health

### "No matches found"
- **Cause**: Team name spelling or no data
- **Solution**: Try exact team names like "Real Madrid"
- **Fix**: Use "👁️ Preview Site" to check website

### Scraping Fails
- **Try**: Different sports website
- **Check**: Website allows scraping
- **Use**: Site presets for tested websites

## 📁 Project Structure

```
DataMiner/
├── start_dataminer.py      # Complete startup script
├── start_backend.py        # Backend only
├── start_frontend.py       # Frontend only  
├── test_backend.py         # Test connectivity
├── backend/
│   ├── app.py             # Flask API server
│   └── scraper/
│       └── web_scraper.py # Scraping engine
└── frontend/
    ├── historical-pattern-scraper.html  # Main interface
    ├── visual-inspector.html           # Site inspector
    ├── pattern-analyzer.html           # Pattern analysis
    └── screen-monitor.html             # Monitoring tool
```

## 🔍 Available Interfaces

- **Historical Pattern Scraper**: Main scraping and analysis tool
- **Visual Inspector**: Website structure analyzer  
- **Pattern Analyzer**: Advanced pattern analysis
- **Screen Monitor**: Continuous monitoring
- **Sports Dashboard**: General sports data dashboard

## 💡 Tips for Best Results

1. **Start with Test**: Always test selectors first
2. **Use Presets**: Try site presets for known working selectors
3. **Check Team Names**: Use exact spelling (e.g., "Real Madrid" not "Madrid")
4. **Longer Periods**: Use 1+ months for better pattern analysis
5. **Multiple Sites**: Try different sports websites if one fails
6. **Preview First**: Use "👁️ Preview Site" to understand website structure

## 🚨 Important Notes

- **Real Data Only**: No mock data - scrapes actual websites
- **Minimum History**: Needs 3+ months for meaningful patterns
- **Team Name Accuracy**: Must match exactly as shown on website
- **CSS Selector Dependency**: Success depends on correct selectors
- **Website Compatibility**: Some sites may block automated scraping

## 🎉 Success Indicators

✅ Backend health check passes
✅ Test selectors finds data  
✅ Team name matches found
✅ Historical data scraped
✅ Patterns analyzed successfully

## Tech Stack
- **Backend**: Python (Flask, Beautiful Soup, Selenium, Pandas)
- **Frontend**: HTML/CSS/JavaScript
- **Database**: SQLite
- **Scraping**: Beautiful Soup + Selenium for dynamic content