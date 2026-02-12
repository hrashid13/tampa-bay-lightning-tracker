# Tampa Bay Lightning Player Statistics Tracker

A full-stack sports analytics application that automatically tracks and visualizes Tampa Bay Lightning hockey players across multiple leagues including NHL, AHL, ECHL, OHL, European leagues, and NCAA.

## Project Overview

This application serves as a comprehensive player tracking system for the Tampa Bay Lightning organization, monitoring both NHL roster players and prospects. The system combines automated web scraping, cloud database storage, and an interactive dashboard to provide real-time statistics and performance metrics.

[![Live Dashboard](https://img.shields.io/badge/Live-Dashboard-blue)](https://tbl-dashboard-hfrashid-5328-hesham-rashids-projects.vercel.app/)

## Architecture

The project consists of two main components:

### 1. Data Pipeline (Backend)
Automated ETL (Extract, Transform, Load) pipeline that collects player statistics daily from Elite Prospects and stores them in MongoDB Atlas.

### 2. Dashboard (Frontend)
React-based web application hosted on Vercel that provides interactive visualizations and filtering capabilities for the collected player data.

## Technology Stack

### Data Pipeline
- **Web Scraping:** Selenium WebDriver (Python)
- **Database:** MongoDB Atlas (Cloud NoSQL Database)
- **Automation:** Windows Task Scheduler
- **Language:** Python 3.x

### Dashboard
- **Framework:** Next.js (React)
- **Visualization:** Recharts
- **Styling:** Tailwind CSS
- **Hosting:** Vercel
- **Language:** TypeScript/JavaScript

## Features

### Data Collection
- Automated daily scraping at 2:00 AM
- Tracks 103 total players (57 NHL roster, 46 prospects)
- Multi-league support (NHL, AHL, ECHL, OHL, European leagues, NCAA)
- Flexible schema to accommodate different statistical formats across leagues

### Dashboard Features
- Real-time player statistics display
- Interactive search functionality
- Player type filtering (NHL Roster vs Prospects)
- League-specific filtering
- Data visualizations using Recharts
- Responsive design for mobile and desktop

## Project Structure

```
tampa-bay-lightning-tracker/
├── data-pipeline/              # Backend data collection
│   ├── scrape_lightning_roster.py
│   ├── selenium_nhl_scraper_windows.py
│   ├── prospects_importer_windows.py
│   ├── setup_database.py
│   ├── update_tbl_stats.bat
│   └── requirements.txt
│
└── dashboard/                  # Frontend application
    ├── app/
    ├── components/
    ├── lib/
    ├── public/
    ├── package.json
    └── next.config.ts
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Node.js 16.x or higher
- MongoDB Atlas account
- Google Chrome browser (for Selenium)

### Data Pipeline Setup

1. Navigate to the data pipeline directory:
```bash
cd data-pipeline
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your MongoDB credentials:
```
MONGODB_URI=your_mongodb_connection_string_here
```

4. Initialize the database:
```bash
python setup_database.py
```

5. Test the scraper:
```bash
python selenium_nhl_scraper_windows.py
```

6. Set up automated scheduling:
   - Open Windows Task Scheduler
   - Import or create a new task to run `update_tbl_stats.bat` daily at 2:00 AM
   - Ensure "Run whether user is logged on or not" is selected
   - Configure power settings to allow task execution during sleep

### Dashboard Setup

1. Navigate to the dashboard directory:
```bash
cd dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file with your MongoDB credentials:
```
MONGODB_URI=your_mongodb_connection_string_here
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

### Deployment

The dashboard is deployed on Vercel:

1. Connect your GitHub repository to Vercel
2. Configure environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

## Database Schema

The application uses MongoDB's flexible document structure to accommodate varying statistics across different leagues:

```javascript
{
  playerName: String,
  playerType: String,  // "NHL Roster" or "Prospect"
  league: String,
  team: String,
  position: String,
  gamesPlayed: Number,
  goals: Number,
  assists: Number,
  points: Number,
  // Additional league-specific statistics
  lastUpdated: Date
}
```

## Why MongoDB?

MongoDB was chosen over traditional SQL databases because:
- Different leagues track different statistics, requiring flexible schemas
- No need for complex joins across multiple tables
- Easy to add new statistical categories as leagues evolve
- Simplified data structure for time-series player statistics
- Cloud-native solution (MongoDB Atlas) for easy deployment

## Data Sources

Player statistics are sourced from Elite Prospects, which aggregates data from:
- NHL (National Hockey League)
- AHL (American Hockey League)
- ECHL (East Coast Hockey League)
- OHL (Ontario Hockey League)
- European leagues (SHL, Liiga, KHL, etc.)
- NCAA (College hockey)

## Future Enhancements

- Historical trend analysis and player progression tracking
- Advanced statistical metrics and analytics
- Player comparison tools
- Email notifications for significant player achievements
- Mobile application development
- API endpoint creation for third-party access

## Known Issues

- Windows Task Scheduler may require power management settings adjustment for consistent 2 AM execution
- Elite Prospects website structure changes may require scraper updates
- Rate limiting considerations for frequent data requests

## Contributing

This is a personal portfolio project, but suggestions and feedback are welcome. Please open an issue to discuss potential changes.

## License

This project is for educational and portfolio purposes. Player statistics are sourced from publicly available data on Elite Prospects.

**Hesham**
- Portfolio: https://www.heshamrashid.org/
- LinkedIn: https://www.linkedin.com/in/hesham-rashid/ 
- Email: h.f.rashid@gmail.com

Master's in AI and Business Analytics - University of South Florida

## Acknowledgments

- Elite Prospects for providing comprehensive hockey statistics
- Tampa Bay Lightning organization for inspiration
- MongoDB Atlas for cloud database hosting
- Vercel for frontend hosting

## Contact

For questions or collaboration opportunities, please reach out via h.f.rashid@gmail.com or LinkedIn.