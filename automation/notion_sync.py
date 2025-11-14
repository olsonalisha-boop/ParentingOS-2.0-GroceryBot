#!/usr/bin/env python3
"""
Notion API Connector for shopping list synchronization
Syncs shopping list between Notion database and local CSV
"""

import os
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionSyncError(Exception):
    """Custom exception for Notion sync errors"""
    pass

class NotionSync:
    """
    Handles synchronization between Notion databases and local CSV files
    for the grocery shopping automation system
    """
    
    def __init__(self):
        """Initialize Notion sync with API credentials from environment"""
        self.base_dir = Path(__file__).parent.parent
        self.notion_token = os.environ.get('NOTION_TOKEN')
        self.shopping_db_id = os.environ.get('NOTION_DATABASE_ID')
        self.deals_db_id = os.environ.get('NOTION_DEALS_DATABASE_ID')
        
        if not self.notion_token:
            raise NotionSyncError("NOTION_TOKEN environment variable not set")
        
        # Try to import notion-client
        try:
            from notion_client import Client
            self.notion = Client(auth=self.notion_token)
        except ImportError:
            logger.error("notion-client package not installed. Install with: pip install notion-client")
            raise NotionSyncError("notion-client package not installed")
    
    def sync_shopping_list_from_notion(self) -> int:
        """
        Sync shopping list from Notion database to local CSV file
        
        Returns:
            Number of items synced
        """
        if not self.shopping_db_id:
            logger.warning("NOTION_DATABASE_ID not set, skipping shopping list sync")
            return 0
        
        logger.info(f"Syncing shopping list from Notion database: {self.shopping_db_id}")
        
        try:
            # Query the Notion database
            results = self.notion.databases.query(database_id=self.shopping_db_id)
            
            # Extract shopping list items from Notion pages
            items = []
            for page in results['results']:
                props = page['properties']
                
                # Extract item details from Notion properties
                # Adjust property names based on your Notion database structure
                item = {
                    'item_name': self._extract_title(props.get('Item Name', props.get('Name', {}))),
                    'quantity': self._extract_number(props.get('Quantity', {}), default=1),
                    'preferred_brand': self._extract_text(props.get('Preferred Brand', props.get('Brand', {}))),
                    'max_price': self._extract_number(props.get('Max Price', props.get('Target Price', {})), default=99.99)
                }
                
                # Only add items with valid names
                if item['item_name']:
                    items.append(item)
            
            # Write to local CSV file
            csv_path = self.base_dir / 'data' / 'shopping_list.csv'
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(csv_path, 'w', newline='') as f:
                fieldnames = ['item_name', 'quantity', 'preferred_brand', 'max_price']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(items)
            
            logger.info(f"✅ Successfully synced {len(items)} items from Notion to {csv_path}")
            return len(items)
            
        except Exception as e:
            logger.error(f"Failed to sync from Notion: {e}")
            raise NotionSyncError(f"Notion sync failed: {e}")
    
    def sync_deals_to_notion(self) -> int:
        """
        Sync found deals from local report to Notion deals database
        
        Returns:
            Number of deals synced
        """
        if not self.deals_db_id:
            logger.warning("NOTION_DEALS_DATABASE_ID not set, skipping deals sync")
            return 0
        
        logger.info(f"Syncing deals to Notion database: {self.deals_db_id}")
        
        # Find the most recent shopping report
        output_dir = self.base_dir / 'output'
        if not output_dir.exists():
            logger.warning("No output directory found, no deals to sync")
            return 0
        
        reports = sorted(output_dir.glob('shopping_report_*.md'), reverse=True)
        if not reports:
            logger.warning("No shopping reports found, no deals to sync")
            return 0
        
        # Parse the latest report
        latest_report = reports[0]
        logger.info(f"Parsing report: {latest_report}")
        
        try:
            with open(latest_report, 'r') as f:
                content = f.read()
            
            # Extract deals from markdown report
            import re
            deal_pattern = re.compile(
                r'### (.*?)\n.*?Best Price.*?\$([\d.]+) at (.*?)\n',
                re.DOTALL
            )
            
            deals_synced = 0
            for match in deal_pattern.finditer(content):
                item_name = match.group(1).strip()
                price = float(match.group(2))
                store = match.group(3).strip()
                
                try:
                    # Create a new page in Notion deals database
                    self.notion.pages.create(
                        parent={'database_id': self.deals_db_id},
                        properties={
                            'Deal': {
                                'title': [{'text': {'content': item_name}}]
                            },
                            'Price': {
                                'number': price
                            },
                            'Store': {
                                'select': {'name': store}
                            },
                            'Date Found': {
                                'date': {'start': datetime.now().isoformat()}
                            }
                        }
                    )
                    deals_synced += 1
                    
                except Exception as e:
                    logger.error(f"Failed to create deal for {item_name}: {e}")
                    continue
            
            logger.info(f"✅ Successfully synced {deals_synced} deals to Notion")
            return deals_synced
            
        except Exception as e:
            logger.error(f"Failed to sync deals to Notion: {e}")
            raise NotionSyncError(f"Deals sync failed: {e}")
    
    def _extract_title(self, prop: Dict) -> str:
        """Extract title text from Notion property"""
        try:
            if prop.get('type') == 'title' and prop.get('title'):
                return prop['title'][0]['text']['content']
            return ''
        except (KeyError, IndexError, TypeError):
            return ''
    
    def _extract_text(self, prop: Dict) -> str:
        """Extract plain text from Notion property"""
        try:
            if prop.get('type') == 'rich_text' and prop.get('rich_text'):
                return prop['rich_text'][0]['text']['content']
            return ''
        except (KeyError, IndexError, TypeError):
            return ''
    
    def _extract_number(self, prop: Dict, default: float = 0) -> float:
        """Extract number from Notion property"""
        try:
            if prop.get('type') == 'number' and prop.get('number') is not None:
                return float(prop['number'])
            return default
        except (KeyError, TypeError, ValueError):
            return default

def main():
    """Main execution function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync shopping data with Notion')
    parser.add_argument(
        '--sync',
        action='store_true',
        help='Sync shopping list from Notion to local CSV'
    )
    parser.add_argument(
        '--update-deals',
        action='store_true',
        help='Update deals in Notion from local reports'
    )
    parser.add_argument(
        '--both',
        action='store_true',
        help='Sync both shopping list and deals'
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, default to syncing shopping list
    if not (args.sync or args.update_deals or args.both):
        args.sync = True
    
    try:
        sync = NotionSync()
        
        if args.sync or args.both:
            logger.info("=" * 50)
            logger.info("SYNCING SHOPPING LIST FROM NOTION")
            logger.info("=" * 50)
            items_synced = sync.sync_shopping_list_from_notion()
            print(f"\n✅ Synced {items_synced} shopping list items from Notion\n")
        
        if args.update_deals or args.both:
            logger.info("=" * 50)
            logger.info("SYNCING DEALS TO NOTION")
            logger.info("=" * 50)
            deals_synced = sync.sync_deals_to_notion()
            print(f"\n✅ Synced {deals_synced} deals to Notion\n")
        
        logger.info("Notion sync completed successfully!")
        sys.exit(0)
        
    except NotionSyncError as e:
        logger.error(f"Sync failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
