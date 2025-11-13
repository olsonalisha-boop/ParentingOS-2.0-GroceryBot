#!/usr/bin/env python3
"""
Walmart scraper for Milwaukee area stores
Uses both web scraping and Walmart's search functionality
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict
from datetime import datetime, timedelta
import re

class WalmartScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Walmart store IDs for Milwaukee area
        self.store_ids = {
            'brown_deer': '1872',  # Brown Deer location
            'west_milwaukee': '3520',  # West Milwaukee
        }
        
        self.base_url = 'https://www.walmart.com'
        
    def search_product(self, product_name: str, max_results: int = 5) -> List[Dict]:
        """Search for a product and get prices"""
        results = []
        
        # Clean product name for search
        search_query = product_name.replace(' ', '+')
        
        # Note: Walmart's actual API requires authentication
        # This is a simplified example structure
        search_url = f"{self.base_url}/search?q={search_query}"
        
        try:
            # In production, you'd use selenium or playwright for dynamic content
            # This is a demonstration of the structure
            
            # Simulate finding products
            mock_results = self._get_mock_results(product_name)
            
            for item in mock_results[:max_results]:
                results.append({
                    'name': item['name'],
                    'price': item['price'],
                    'unit_price': item.get('unit_price', ''),
                    'in_stock': item.get('in_stock', True),
                    'url': item.get('url', ''),
                    'image': item.get('image', ''),
                    'savings': item.get('savings', 0),
                    'was_price': item.get('was_price', None)
                })
                
        except Exception as e:
            print(f"Error searching for {product_name}: {e}")
        
        return results
    
    def _get_mock_results(self, product_name: str) -> List[Dict]:
        """Return mock results for demonstration"""
        # In production, this would parse actual HTML/JSON from Walmart
        
        mock_data = {
            'milk': [
                {
                    'name': 'Great Value Whole Milk, 1 Gallon',
                    'price': 3.48,
                    'unit_price': '$3.48/gal',
                    'in_stock': True,
                    'url': '/ip/Great-Value-Whole-Milk-1-Gallon/10450114',
                    'savings': 0.51,
                    'was_price': 3.99
                },
                {
                    'name': 'Great Value 2% Milk, 1 Gallon',
                    'price': 3.48,
                    'unit_price': '$3.48/gal',
                    'in_stock': True,
                    'url': '/ip/Great-Value-2-Milk-1-Gallon/10450115'
                }
            ],
            'bread': [
                {
                    'name': 'Wonder Bread Classic White, 20 oz',
                    'price': 1.98,
                    'unit_price': '$0.10/oz',
                    'in_stock': True,
                    'url': '/ip/Wonder-Bread-Classic/10403044'
                },
                {
                    'name': 'Great Value White Bread, 20 oz',
                    'price': 0.98,
                    'unit_price': '$0.05/oz',
                    'in_stock': True,
                    'url': '/ip/Great-Value-White-Bread/10403045',
                    'savings': 0.50,
                    'was_price': 1.48
                }
            ],
            'eggs': [
                {
                    'name': 'Great Value Large Eggs, 12 Count',
                    'price': 2.97,
                    'unit_price': '$0.25/egg',
                    'in_stock': True,
                    'url': '/ip/Great-Value-Large-Eggs/10450116'
                }
            ],
            'chicken': [
                {
                    'name': 'Fresh Chicken Breast, per lb',
                    'price': 3.98,
                    'unit_price': '$3.98/lb',
                    'in_stock': True,
                    'url': '/ip/Fresh-Chicken-Breast/19399785',
                    'savings': 1.00,
                    'was_price': 4.98
                }
            ]
        }
        
        # Find best match for product
        product_lower = product_name.lower()
        for key in mock_data:
            if key in product_lower:
                return mock_data[key]
        
        # Default response if no match
        return [{
            'name': f'{product_name} - Generic',
            'price': 4.99,
            'unit_price': '',
            'in_stock': True,
            'url': '/search?q=' + product_name.replace(' ', '+')
        }]
    
    def get_weekly_deals(self) -> List[Dict]:
        """Get current weekly deals and rollbacks"""
        deals = []
        
        # Categories to check for deals
        categories = ['grocery', 'produce', 'meat-seafood', 'dairy-eggs']
        
        for category in categories:
            # In production, scrape actual deals pages
            category_deals = self._get_category_deals(category)
            deals.extend(category_deals)
        
        return deals
    
    def _get_category_deals(self, category: str) -> List[Dict]:
        """Get deals for a specific category"""
        # Mock deals data for demonstration
        mock_deals = {
            'grocery': [
                {'item': 'Pasta', 'price': 0.98, 'savings': 0.50, 'brand': 'Great Value'},
                {'item': 'Cereal', 'price': 2.48, 'savings': 1.50, 'brand': 'Kelloggs'},
                {'item': 'Coffee', 'price': 5.98, 'savings': 2.00, 'brand': 'Folgers'}
            ],
            'produce': [
                {'item': 'Bananas', 'price': 0.48, 'savings': 0.10, 'unit': 'per lb'},
                {'item': 'Apples', 'price': 0.98, 'savings': 0.30, 'unit': 'per lb'}
            ],
            'meat-seafood': [
                {'item': 'Ground Beef', 'price': 3.98, 'savings': 1.00, 'unit': 'per lb'},
                {'item': 'Pork Chops', 'price': 2.98, 'savings': 1.50, 'unit': 'per lb'}
            ],
            'dairy-eggs': [
                {'item': 'Cheese', 'price': 2.48, 'savings': 0.50, 'brand': 'Great Value'},
                {'item': 'Yogurt', 'price': 0.50, 'savings': 0.18, 'brand': 'Yoplait'}
            ]
        }
        
        deals = mock_deals.get(category, [])
        
        # Add metadata
        for deal in deals:
            deal['category'] = category
            deal['store'] = 'Walmart'
            deal['valid_until'] = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            deal['deal_type'] = 'Rollback' if deal['savings'] > 1 else 'Special'
        
        return deals
    
    def check_inventory(self, product_name: str, store_id: str = None) -> Dict:
        """Check if product is in stock at specific store"""
        if not store_id:
            store_id = self.store_ids['brown_deer']
        
        # In production, this would check actual inventory
        # Mock response for demonstration
        return {
            'product': product_name,
            'in_stock': True,
            'quantity': 'Limited Stock',
            'store_id': store_id,
            'aisle': 'A12',  # Mock aisle location
            'pickup_available': True,
            'delivery_available': True
        }
    
    def get_pickup_slots(self, store_id: str = None) -> List[Dict]:
        """Get available pickup time slots"""
        if not store_id:
            store_id = self.store_ids['brown_deer']
        
        slots = []
        base_time = datetime.now().replace(minute=0, second=0)
        
        # Generate mock pickup slots for next 3 days
        for day in range(3):
            date = base_time + timedelta(days=day)
            
            # Morning slots (8 AM - 12 PM)
            for hour in range(8, 12):
                slot_time = date.replace(hour=hour)
                slots.append({
                    'date': slot_time.strftime('%Y-%m-%d'),
                    'time': slot_time.strftime('%I:%M %p'),
                    'available': hour != 10,  # Mock 10 AM as unavailable
                    'express': hour >= 11  # Express pickup after 11 AM
                })
            
            # Afternoon/Evening slots (2 PM - 8 PM)
            for hour in range(14, 20):
                slot_time = date.replace(hour=hour)
                slots.append({
                    'date': slot_time.strftime('%Y-%m-%d'),
                    'time': slot_time.strftime('%I:%M %p'),
                    'available': True,
                    'express': False
                })
        
        return slots
    
    def create_shopping_list_url(self, items: List[str]) -> str:
        """Create a Walmart URL with all items in cart"""
        # Build URL with search parameters
        base_url = "https://www.walmart.com/search?q="
        query = "%20OR%20".join([item.replace(' ', '%20') for item in items])
        
        return base_url + query

def main():
    """Test the Walmart scraper"""
    scraper = WalmartScraper()
    
    print("🛒 Walmart Deal Finder - Milwaukee")
    print("=" * 50)
    
    # Search for specific products
    products_to_search = ['milk', 'bread', 'eggs', 'chicken']
    
    print("\n📍 Product Search Results:")
    for product in products_to_search:
        results = scraper.search_product(product, max_results=2)
        print(f"\n{product.upper()}:")
        for item in results:
            if item.get('was_price'):
                print(f"  - {item['name']}: ${item['price']:.2f} (was ${item['was_price']:.2f})")
            else:
                print(f"  - {item['name']}: ${item['price']:.2f}")
    
    # Get weekly deals
    print("\n🏷️ Weekly Deals:")
    deals = scraper.get_weekly_deals()
    for deal in deals[:10]:  # Show first 10 deals
        print(f"  - {deal['item']}: ${deal['price']:.2f} (save ${deal['savings']:.2f}) - {deal['deal_type']}")
    
    # Check pickup slots
    print("\n📅 Available Pickup Slots (Next 24 hours):")
    slots = scraper.get_pickup_slots()
    for slot in slots[:5]:
        if slot['available']:
            express = " [EXPRESS]" if slot['express'] else ""
            print(f"  - {slot['date']} at {slot['time']}{express}")
    
    # Create shopping URL
    shopping_items = ['milk', 'bread', 'eggs', 'chicken breast', 'ground beef']
    url = scraper.create_shopping_list_url(shopping_items)
    print(f"\n🔗 Quick Shopping URL:\n   {url[:80]}...")
    
    print("\n✅ Scraper test complete!")

if __name__ == "__main__":
    main()
