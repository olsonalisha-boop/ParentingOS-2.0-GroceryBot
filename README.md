# ParentingOS-2.0-GroceryBot
Automating Grocery Chaos

## 📋 Project Structure

```
ParentingOS-2.0-GroceryBot/
├── .github/
│   └── workflows/           # GitHub Actions automation
│       ├── daily_deals.yml        # Main deal finder (runs daily at 6 AM CST)
│       ├── notion_sync.yml        # Notion database synchronization
│       ├── weekly_analytics.yml   # Weekly savings reports
│       └── setup.yml              # One-time setup workflow
│
├── automation/              # Python automation scripts
│   ├── find_deals.py              # Main deal finder for Milwaukee stores
│   ├── route_planner.py           # Shopping route optimization
│   ├── notion_sync.py             # Notion API connector
│   ├── send_notifications.py     # Email notification system
│   ├── sheets_integration.py     # Google Sheets integration
│   └── walmart_scraper.py        # Walmart-specific scraper
│
├── data/                    # Configuration and data files
│   ├── shopping_list.csv          # Your shopping items and target prices
│   └── stores_config.json         # Store locations and settings
│
├── output/                  # Generated reports (created by workflows)
│   ├── shopping_report_*.md       # Daily deal reports
│   ├── route_report_*.md          # Route optimization reports
│   └── weekly_report_*.md         # Weekly analytics
│
└── requirements.txt         # Python dependencies

```

## 🚀 Quick Start

1. **Setup**: Run the setup workflow from the Actions tab
2. **Customize**: Edit `data/shopping_list.csv` with your items
3. **Automate**: Let the daily workflow find deals automatically
4. **Save Money**: Check your savings in weekly reports!

## 📦 Features

- 🛒 **Automated Deal Finding**: Scans multiple Milwaukee-area stores daily
- 🗺️ **Route Optimization**: Plans efficient shopping trips
- 📧 **Email Notifications**: Get alerted about great deals
- 📊 **Analytics**: Track your savings over time
- 🔄 **Notion Integration**: Sync with your Notion databases
- 📈 **Google Sheets**: Export data to spreadsheets

## 🔧 Configuration

See `data/stores_config.json` for store settings and preferences.
Edit `data/shopping_list.csv` to add your regular grocery items.

## 📝 Supported Stores

- Metro Market
- Sendik's
- Walmart
- Pick 'n Save
- Cermak Fresh Market
