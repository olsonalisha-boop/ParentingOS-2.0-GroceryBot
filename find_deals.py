#!/usr/bin/env python3
"""
Main deal finder for Milwaukee area stores
Scrapes deals and matches them to your shopping list
"""

import json
import csv
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
import os
from typing import Dict, List, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MilwaukeeDealFinder:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.stores_config = self.load_stores_config()
        self.shopping_list = self.load_shopping_list()
        self.deals = {}
        
    def load_stores_config(self) -> dict:
        """Load store configuration"""
        config_path = self.base_dir / "data" / "stores_config.json"
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def load_shopping_list(self) -> List[Dict]:
        """Load user's shopping list"""
        list_path = self.base_dir / "data" / "shopping_list.csv"
        shopping_list = []
        
        if list_path.exists():
            with open(list_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    shopping_list.append({
                        'item': row['item_name'],
                        'quantity': int(row.get('quantity', 1)),
                        'preferred_brand': row.get('preferred_brand', ''),
                        'max_price': float(row.get('max_price', 999))
                    })
        else:
            # Create sample shopping list if none exists
            logger.info("Creating sample shopping list...")
            self.create_sample_shopping_list(list_path)
        
        return shopping_list
    
    def create_sample_shopping_list(self, path: Path):
        """Create a sample shopping list for new users"""
        sample_items = [
            ['item_name', 'quantity', 'preferred_brand', 'max_price'],
            ['Milk', '1', 'Kemps', '4.99'],
            ['Bread', '1', 'Brownberry', '3.99'],
            ['Eggs', '1', '', '3.99'],
            ['Chicken Breast', '2', '', '8.99'],
            ['Ground Beef', '2', '', '7.99'],
            ['Bananas', '1', '', '2.99'],
            ['Apples', '1', '', '4.99'],
            ['Cheese', '1', 'Sargento', '5.99'],
            ['Yogurt', '4', 'Chobani', '1.29'],
            ['Pasta', '2', 'Barilla', '2.99'],
            ['Pasta Sauce', '1', 'Rao\'s', '7.99'],
            ['Coffee', '1', 'Starbucks', '12.99'],
            ['Cereal', '1', 'Kellogg\'s', '4.99'],
            ['Orange Juice', '1', 'Simply', '5.99'],
            ['Butter', '1', 'Land O\'Lakes', '5.99']
        ]
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(sample_items)
    
    async def scrape_metro_market(self) -> List[Dict]:
        """Scrape deals from Metro Market"""
        deals = []
        # This would normally scrape the actual website
        # For demo purposes, returning sample deals
        sample_deals = [
            {'item': 'Milk', 'price': 3.49, 'unit': 'gallon', 'brand': 'Kemps', 'valid_until': '2024-01-21'},
            {'item': 'Chicken Breast', 'price': 3.99, 'unit': 'lb', 'brand': 'Tyson', 'valid_until': '2024-01-21'},
            {'item': 'Bread', 'price': 2.50, 'unit': 'loaf', 'brand': 'Brownberry', 'valid_until': '2024-01-21'},
        ]
        
        for deal in sample_deals:
            deal['store'] = 'Metro Market'
            deal['location_id'] = 'mm_shorewood'
        
        logger.info(f"Found {len(sample_deals)} deals at Metro Market")
        return sample_deals
    
    async def scrape_sendiks(self) -> List[Dict]:
        """Scrape deals from Sendik's"""
        deals = []
        sample_deals = [
            {'item': 'Ground Beef', 'price': 4.99, 'unit': 'lb', 'brand': 'USDA Choice', 'valid_until': '2024-01-21'},
            {'item': 'Cheese', 'price': 3.99, 'unit': 'package', 'brand': 'Sargento', 'valid_until': '2024-01-21'},
            {'item': 'Coffee', 'price': 9.99, 'unit': 'bag', 'brand': 'Starbucks', 'valid_until': '2024-01-21'},
        ]
        
        for deal in sample_deals:
            deal['store'] = "Sendik's"
            deal['location_id'] = 'sendiks_whitefish_bay'
        
        logger.info(f"Found {len(sample_deals)} deals at Sendik's")
        return sample_deals
    
    async def scrape_walmart(self) -> List[Dict]:
        """Scrape deals from Walmart using API or web scraping"""
        deals = []
        sample_deals = [
            {'item': 'Eggs', 'price': 2.97, 'unit': 'dozen', 'brand': 'Great Value', 'valid_until': '2024-01-21'},
            {'item': 'Pasta', 'price': 0.98, 'unit': 'box', 'brand': 'Great Value', 'valid_until': '2024-01-21'},
            {'item': 'Orange Juice', 'price': 3.48, 'unit': '64oz', 'brand': 'Great Value', 'valid_until': '2024-01-21'},
        ]
        
        for deal in sample_deals:
            deal['store'] = 'Walmart'
            deal['location_id'] = 'walmart_brown_deer'
        
        logger.info(f"Found {len(sample_deals)} deals at Walmart")
        return sample_deals
    
    async def scrape_pick_n_save(self) -> List[Dict]:
        """Scrape deals from Pick 'n Save"""
        deals = []
        sample_deals = [
            {'item': 'Yogurt', 'price': 0.69, 'unit': 'cup', 'brand': 'Yoplait', 'valid_until': '2024-01-21'},
            {'item': 'Cereal', 'price': 2.99, 'unit': 'box', 'brand': 'General Mills', 'valid_until': '2024-01-21'},
            {'item': 'Butter', 'price': 3.99, 'unit': 'package', 'brand': 'Land O\'Lakes', 'valid_until': '2024-01-21'},
        ]
        
        for deal in sample_deals:
            deal['store'] = "Pick 'n Save"
            deal['location_id'] = 'pns_glendale'
            deal['fuel_points'] = 2  # 2x fuel points on this item
        
        logger.info(f"Found {len(sample_deals)} deals at Pick 'n Save")
        return sample_deals
    
    async def scrape_cermak(self) -> List[Dict]:
        """Scrape deals from Cermak Fresh Market"""
        deals = []
        sample_deals = [
            {'item': 'Bananas', 'price': 0.39, 'unit': 'lb', 'brand': '', 'valid_until': '2024-01-21'},
            {'item': 'Apples', 'price': 0.99, 'unit': 'lb', 'brand': 'Gala', 'valid_until': '2024-01-21'},
            {'item': 'Pasta Sauce', 'price': 1.99, 'unit': 'jar', 'brand': 'Prego', 'valid_until': '2024-01-21'},
        ]
        
        for deal in sample_deals:
            deal['store'] = 'Cermak Fresh Market'
            deal['location_id'] = 'cermak_milwaukee'
        
        logger.info(f"Found {len(sample_deals)} deals at Cermak")
        return sample_deals
    
    async def scrape_all_stores(self):
        """Scrape deals from all enabled stores concurrently"""
        tasks = []
        
        if self.stores_config['stores']['metro_market']['enabled']:
            tasks.append(self.scrape_metro_market())
        if self.stores_config['stores']['sendiks']['enabled']:
            tasks.append(self.scrape_sendiks())
        if self.stores_config['stores']['walmart']['enabled']:
            tasks.append(self.scrape_walmart())
        if self.stores_config['stores']['pick_n_save']['enabled']:
            tasks.append(self.scrape_pick_n_save())
        if self.stores_config['stores']['cermak']['enabled']:
            tasks.append(self.scrape_cermak())
        
        all_deals = await asyncio.gather(*tasks)
        
        # Flatten the list of lists
        self.deals = [deal for store_deals in all_deals for deal in store_deals]
        logger.info(f"Total deals found: {len(self.deals)}")
    
    def match_deals_to_list(self) -> Dict[str, List[Dict]]:
        """Match found deals to shopping list items"""
        matched_deals = {}
        
        for item in self.shopping_list:
            item_name = item['item'].lower()
            matched_deals[item['item']] = []
            
            for deal in self.deals:
                # Simple fuzzy matching - in production, use fuzzywuzzy or AI
                if item_name in deal['item'].lower():
                    # Check if price is within budget
                    if deal['price'] <= item['max_price']:
                        matched_deals[item['item']].append(deal)
            
            # Sort by price for each item
            matched_deals[item['item']].sort(key=lambda x: x['price'])
        
        return matched_deals
    
    def optimize_shopping_route(self, matched_deals: Dict) -> Dict:
        """Determine optimal stores to visit based on deals and location"""
        store_savings = {}
        
        # Calculate total savings per store
        for item, deals in matched_deals.items():
            for deal in deals:
                store = deal['store']
                if store not in store_savings:
                    store_savings[store] = {
                        'items': [],
                        'total_savings': 0,
                        'item_count': 0
                    }
                
                # Find the item's max price from shopping list
                max_price = next(i['max_price'] for i in self.shopping_list if i['item'] == item)
                savings = max_price - deal['price']
                
                store_savings[store]['items'].append({
                    'item': item,
                    'price': deal['price'],
                    'savings': savings
                })
                store_savings[store]['total_savings'] += savings
                store_savings[store]['item_count'] += 1
        
        # Sort stores by total savings
        sorted_stores = sorted(store_savings.items(), 
                             key=lambda x: x[1]['total_savings'], 
                             reverse=True)
        
        # Limit to max stores per trip
        max_stores = self.stores_config['settings']['max_stores_per_trip']
        recommended_stores = sorted_stores[:max_stores]
        
        return {
            'recommended_stores': recommended_stores,
            'all_store_savings': store_savings
        }
    
    def generate_report(self, matched_deals: Dict, route_optimization: Dict):
        """Generate shopping report"""
        report_path = self.base_dir / "output" / f"shopping_report_{datetime.now().strftime('%Y%m%d')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write("# 🛒 Milwaukee Shopping Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n\n")
            
            # Best deals summary
            f.write("## 💰 Best Deals Found\n\n")
            for item, deals in matched_deals.items():
                if deals:
                    best_deal = deals[0]  # Already sorted by price
                    f.write(f"### {item}\n")
                    f.write(f"- **Best Price**: ${best_deal['price']:.2f} at {best_deal['store']}\n")
                    if len(deals) > 1:
                        f.write(f"- **Also available at**:\n")
                        for deal in deals[1:3]:  # Show up to 3 alternatives
                            f.write(f"  - ${deal['price']:.2f} at {deal['store']}\n")
                    f.write("\n")
            
            # Recommended shopping route
            f.write("## 🗺️ Recommended Shopping Route\n\n")
            total_savings = 0
            for store, data in route_optimization['recommended_stores']:
                f.write(f"### {store}\n")
                f.write(f"- **Items to buy**: {data['item_count']}\n")
                f.write(f"- **Total savings**: ${data['total_savings']:.2f}\n")
                f.write("- **Shopping list**:\n")
                for item in data['items']:
                    f.write(f"  - {item['item']}: ${item['price']:.2f} (save ${item['savings']:.2f})\n")
                f.write("\n")
                total_savings += data['total_savings']
            
            f.write(f"## 📊 Summary\n\n")
            f.write(f"- **Total potential savings**: ${total_savings:.2f}\n")
            f.write(f"- **Number of stores to visit**: {len(route_optimization['recommended_stores'])}\n")
            
        logger.info(f"Report generated: {report_path}")
        return report_path

async def main():
    """Main execution function"""
    logger.info("Starting Milwaukee Deal Finder...")
    
    finder = MilwaukeeDealFinder()
    
    # Scrape all stores
    await finder.scrape_all_stores()
    
    # Match deals to shopping list
    matched_deals = finder.match_deals_to_list()
    
    # Optimize shopping route
    route_optimization = finder.optimize_shopping_route(matched_deals)
    
    # Generate report
    report_path = finder.generate_report(matched_deals, route_optimization)
    
    logger.info("Deal finding complete!")
    
    # Print summary to console
    print("\n" + "="*50)
    print("SHOPPING SUMMARY")
    print("="*50)
    
    for store, data in route_optimization['recommended_stores'][:3]:
        print(f"\n{store}:")
        print(f"  Items: {data['item_count']}")
        print(f"  Savings: ${data['total_savings']:.2f}")
    
    print(f"\nFull report saved to: {report_path}")

if __name__ == "__main__":
    asyncio.run(main())
