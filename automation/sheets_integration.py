#!/usr/bin/env python3
"""
Google Sheets integration for Milwaukee Shopping Automation
Syncs shopping lists and deals with Google Sheets
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Note: In production, you'd use google-auth and google-api-python-client
# For now, this is a template showing the structure

class GoogleSheetsIntegration:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        # In production, authenticate with Google Sheets API
        # self.sheets_service = self.authenticate()
        
    def create_shopping_template(self) -> str:
        """Create a Google Sheets template URL for shopping list"""
        # This would normally create a sheet via API
        # For now, return a template structure
        
        template = {
            "Shopping List": {
                "headers": ["Item Name", "Quantity", "Preferred Brand", "Max Price", "Category", "Notes"],
                "sample_data": [
                    ["Milk", "1", "Kemps", "4.99", "Dairy", "2% preferred"],
                    ["Bread", "1", "Brownberry", "3.99", "Bakery", "Whole wheat"],
                    ["Eggs", "1", "", "3.99", "Dairy", "Large eggs"],
                ]
            },
            "Found Deals": {
                "headers": ["Date", "Store", "Item", "Price", "Regular Price", "Savings", "Valid Until"],
                "sample_data": []
            },
            "Shopping Routes": {
                "headers": ["Date", "Store Order", "Address", "Arrival Time", "Items to Buy", "Total at Store"],
                "sample_data": []
            },
            "Settings": {
                "headers": ["Setting", "Value"],
                "sample_data": [
                    ["Max Stores Per Trip", "3"],
                    ["Weekly Budget", "200"],
                    ["Preferred Shopping Day", "Saturday"],
                    ["Home Zip Code", "53217"],
                ]
            }
        }
        
        # Save template locally
        template_path = self.base_dir / "output" / "sheets_template.json"
        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        return str(template_path)
    
    def export_to_sheets_format(self, deals_data: Dict, route_data: Dict) -> Dict:
        """Convert deal and route data to Google Sheets format"""
        sheets_data = {
            "timestamp": datetime.now().isoformat(),
            "deals": [],
            "route": [],
            "summary": {}
        }
        
        # Format deals for sheets
        for store, store_deals in deals_data.items():
            for item in store_deals.get('items', []):
                sheets_data["deals"].append([
                    datetime.now().strftime('%Y-%m-%d'),
                    store,
                    item['item'],
                    f"${item['price']:.2f}",
                    f"${item.get('regular_price', item['price']):.2f}",
                    f"${item.get('savings', 0):.2f}",
                    item.get('valid_until', 'Check store')
                ])
        
        # Format route for sheets
        for stop in route_data.get('schedule', []):
            sheets_data["route"].append([
                datetime.now().strftime('%Y-%m-%d'),
                stop['store'],
                stop['address'],
                stop['arrival'],
                stop.get('items_count', 'Multiple'),
                f"${stop.get('estimated_total', 0):.2f}"
            ])
        
        # Add summary
        sheets_data["summary"] = {
            "total_savings": sum(d['savings'] for d in deals_data.values() if 'savings' in d),
            "stores_to_visit": len(route_data.get('schedule', [])),
            "estimated_time": route_data.get('total_time', 0),
            "gas_cost": route_data.get('gas_cost', 0)
        }
        
        return sheets_data
    
    def import_shopping_list(self, sheets_id: str = None) -> List[Dict]:
        """Import shopping list from Google Sheets"""
        # In production, this would fetch from actual Google Sheets
        # For now, read from local CSV
        
        shopping_list = []
        list_path = self.base_dir / "data" / "shopping_list.csv"
        
        if list_path.exists():
            with open(list_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    shopping_list.append(row)
        
        return shopping_list
    
    def update_deals_sheet(self, deals_data: List[Dict]) -> bool:
        """Update Google Sheets with latest deals"""
        # This would normally use sheets.values().update() API call
        
        # For now, save to CSV format that can be imported to Sheets
        output_path = self.base_dir / "output" / f"deals_{datetime.now().strftime('%Y%m%d')}.csv"
        
        with open(output_path, 'w', newline='') as f:
            if deals_data:
                writer = csv.DictWriter(f, fieldnames=deals_data[0].keys())
                writer.writeheader()
                writer.writerows(deals_data)
        
        print(f"Deals data saved to {output_path}")
        print("You can import this CSV file into Google Sheets")
        
        return True
    
    def create_importable_csv(self, report_data: Dict):
        """Create CSV files that can be easily imported to Google Sheets"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = self.base_dir / "output" / "sheets_import"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create deals CSV
        deals_file = output_dir / f"deals_{timestamp}.csv"
        with open(deals_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Store", "Item", "Price", "Savings", "Valid Until"])
            for deal in report_data.get('deals', []):
                writer.writerow([
                    deal.get('store'),
                    deal.get('item'),
                    deal.get('price'),
                    deal.get('savings'),
                    deal.get('valid_until')
                ])
        
        # Create route CSV
        route_file = output_dir / f"route_{timestamp}.csv"
        with open(route_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Stop", "Store", "Address", "Arrival Time", "Items"])
            for i, stop in enumerate(report_data.get('route', []), 1):
                writer.writerow([
                    i,
                    stop.get('store'),
                    stop.get('address'),
                    stop.get('arrival'),
                    stop.get('items_count')
                ])
        
        print(f"✅ Google Sheets import files created:")
        print(f"   - Deals: {deals_file}")
        print(f"   - Route: {route_file}")
        print("\nTo import to Google Sheets:")
        print("1. Open Google Sheets")
        print("2. File → Import → Upload")
        print("3. Select the CSV file")
        print("4. Choose 'Replace current sheet' or 'Create new sheet'")
        
        return {
            'deals_file': str(deals_file),
            'route_file': str(route_file)
        }

def setup_google_sheets():
    """Helper function to set up Google Sheets integration"""
    print("📊 Google Sheets Setup Helper")
    print("=" * 50)
    print("\nTo integrate with Google Sheets:")
    print("\n1. MANUAL METHOD (Easiest):")
    print("   - The automation creates CSV files in output/sheets_import/")
    print("   - Simply import these into Google Sheets manually")
    
    print("\n2. AUTOMATED METHOD (Advanced):")
    print("   a. Go to https://console.cloud.google.com")
    print("   b. Create a new project")
    print("   c. Enable Google Sheets API")
    print("   d. Create credentials (OAuth 2.0)")
    print("   e. Download credentials.json")
    print("   f. Add to GitHub Secrets:")
    print("      - GOOGLE_SHEETS_CREDENTIALS")
    print("      - GOOGLE_SHEETS_ID")
    
    print("\n3. TEMPLATE METHOD:")
    print("   - Copy this template: [would provide actual template link]")
    print("   - Share it with your GitHub Actions service account")
    print("   - Add the sheet ID to GitHub Secrets")
    
    integrator = GoogleSheetsIntegration()
    template_path = integrator.create_shopping_template()
    print(f"\n✅ Template structure saved to: {template_path}")
    print("   Use this as a guide for setting up your Google Sheet")

if __name__ == "__main__":
    setup_google_sheets()
