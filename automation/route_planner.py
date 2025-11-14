#!/usr/bin/env python3
"""
Route planner for optimal shopping trips in Milwaukee
Calculates the most efficient route between stores
"""

import json
import math
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import os

class RouteOptimizer:
    def __init__(self):
        # Milwaukee area coordinates
        self.home_location = (43.0389, -87.9065)  # Milwaukee downtown default
        self.stores = self.load_store_locations()
        
    def load_store_locations(self) -> Dict:
        """Load store locations with coordinates"""
        # Real coordinates for Milwaukee stores
        return {
            'Metro Market': {
                'address': '4075 N Oakland Ave, Shorewood, WI',
                'coords': (43.1122, -87.8856),
                'hours': {'open': '06:00', 'close': '23:00'},
                'pickup_time': 15  # minutes needed for pickup
            },
            "Sendik's": {
                'address': '500 E Silver Spring Dr, Whitefish Bay, WI',
                'coords': (43.1139, -87.8997),
                'hours': {'open': '07:00', 'close': '21:00'},
                'pickup_time': 20
            },
            'Walmart': {
                'address': '8700 N Servite Dr, Brown Deer, WI',
                'coords': (43.1783, -87.9812),
                'hours': {'open': '06:00', 'close': '23:00'},
                'pickup_time': 10
            },
            "Pick 'n Save": {
                'address': '6950 N Port Washington Rd, Glendale, WI',
                'coords': (43.1350, -87.9173),
                'hours': {'open': '06:00', 'close': '23:00'},
                'pickup_time': 15
            },
            'Cermak Fresh Market': {
                'address': '2238 S 13th St, Milwaukee, WI',
                'coords': (43.0089, -87.9312),
                'hours': {'open': '07:00', 'close': '22:00'},
                'pickup_time': 25
            }
        }
    
    def calculate_distance(self, coord1: Tuple, coord2: Tuple) -> float:
        """Calculate distance between two coordinates in miles"""
        # Haversine formula for distance calculation
        R = 3959  # Earth's radius in miles
        
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def estimate_drive_time(self, distance: float) -> int:
        """Estimate drive time in minutes based on distance"""
        # Assume average speed of 25 mph in Milwaukee area
        avg_speed = 25
        base_time = (distance / avg_speed) * 60
        # Add buffer for traffic and parking
        return int(base_time * 1.2) + 3
    
    def find_optimal_route(self, selected_stores: List[str], 
                          start_location: Tuple = None) -> Dict:
        """Find the optimal route using nearest neighbor algorithm"""
        if not start_location:
            start_location = self.home_location
        
        route = []
        unvisited = selected_stores.copy()
        current_location = start_location
        total_distance = 0
        total_time = 0
        
        while unvisited:
            # Find nearest unvisited store
            nearest_store = None
            min_distance = float('inf')
            
            for store in unvisited:
                store_coords = self.stores[store]['coords']
                distance = self.calculate_distance(current_location, store_coords)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_store = store
            
            # Add to route
            route.append({
                'store': nearest_store,
                'distance': min_distance,
                'drive_time': self.estimate_drive_time(min_distance),
                'pickup_time': self.stores[nearest_store]['pickup_time'],
                'address': self.stores[nearest_store]['address']
            })
            
            total_distance += min_distance
            total_time += self.estimate_drive_time(min_distance) + self.stores[nearest_store]['pickup_time']
            
            # Update current location
            current_location = self.stores[nearest_store]['coords']
            unvisited.remove(nearest_store)
        
        # Add return home
        home_distance = self.calculate_distance(current_location, start_location)
        total_distance += home_distance
        total_time += self.estimate_drive_time(home_distance)
        
        return {
            'route': route,
            'total_distance': round(total_distance, 1),
            'total_time': total_time,
            'return_home_distance': round(home_distance, 1)
        }
    
    def optimize_for_time_windows(self, selected_stores: List[str], 
                                 preferred_time: str = "10:00") -> Dict:
        """Optimize route considering store hours and pickup windows"""
        route_info = self.find_optimal_route(selected_stores)
        
        # Parse preferred start time
        hour, minute = map(int, preferred_time.split(':'))
        current_time = datetime.now().replace(hour=hour, minute=minute, second=0)
        
        schedule = []
        
        for stop in route_info['route']:
            store = stop['store']
            arrival_time = current_time + timedelta(minutes=stop['drive_time'])
            
            # Check if store is open
            store_hours = self.stores[store]['hours']
            open_time = datetime.now().replace(
                hour=int(store_hours['open'].split(':')[0]),
                minute=int(store_hours['open'].split(':')[1]),
                second=0
            )
            close_time = datetime.now().replace(
                hour=int(store_hours['close'].split(':')[0]),
                minute=int(store_hours['close'].split(':')[1]),
                second=0
            )
            
            # Adjust if arriving before opening
            if arrival_time < open_time:
                arrival_time = open_time
            
            departure_time = arrival_time + timedelta(minutes=stop['pickup_time'])
            
            schedule.append({
                'store': store,
                'arrival': arrival_time.strftime('%I:%M %p'),
                'departure': departure_time.strftime('%I:%M %p'),
                'address': stop['address'],
                'pickup_time': stop['pickup_time'],
                'status': 'OK' if arrival_time < close_time else 'CLOSED'
            })
            
            current_time = departure_time
        
        return {
            'schedule': schedule,
            'total_time': route_info['total_time'],
            'total_distance': route_info['total_distance'],
            'return_home': route_info['return_home_distance'],
            'finish_time': current_time.strftime('%I:%M %p')
        }
    
    def calculate_gas_cost(self, total_distance: float, 
                          gas_price: float = 3.29) -> float:
        """Calculate estimated gas cost for the trip"""
        avg_mpg = 25  # Average fuel efficiency
        gallons_needed = total_distance / avg_mpg
        return round(gallons_needed * gas_price, 2)
    
    def generate_route_report(self, stores: List[str], 
                             savings_data: Dict = None) -> str:
        """Generate a detailed route report"""
        route_info = self.find_optimal_route(stores)
        schedule = self.optimize_for_time_windows(stores)
        gas_cost = self.calculate_gas_cost(route_info['total_distance'])
        
        report = "# 🗺️ Optimized Shopping Route\n\n"
        report += f"**Date**: {datetime.now().strftime('%Y-%m-%d')}\n"
        report += f"**Stores to visit**: {', '.join(stores)}\n\n"
        
        report += "## 📍 Route Details\n\n"
        for i, stop in enumerate(schedule['schedule'], 1):
            report += f"### Stop {i}: {stop['store']}\n"
            report += f"- **Address**: {stop['address']}\n"
            report += f"- **Arrival**: {stop['arrival']}\n"
            report += f"- **Pickup Time**: {stop['pickup_time']} minutes\n"
            report += f"- **Departure**: {stop['departure']}\n"
            if stop['status'] == 'CLOSED':
                report += f"- ⚠️ **WARNING**: Store may be closed\n"
            report += "\n"
        
        report += "## 📊 Trip Summary\n\n"
        report += f"- **Total Distance**: {route_info['total_distance']} miles\n"
        report += f"- **Total Time**: {route_info['total_time']} minutes\n"
        report += f"- **Estimated Gas Cost**: ${gas_cost}\n"
        report += f"- **Return Home**: {route_info['return_home_distance']} miles\n"
        report += f"- **Expected Finish Time**: {schedule['finish_time']}\n\n"
        
        if savings_data:
            total_savings = sum(savings_data.values())
            net_savings = total_savings - gas_cost
            report += f"## 💰 Financial Summary\n\n"
            report += f"- **Total Savings**: ${total_savings:.2f}\n"
            report += f"- **Gas Cost**: -${gas_cost}\n"
            report += f"- **Net Savings**: ${net_savings:.2f}\n\n"
        
        report += "## 🚗 Driving Directions\n\n"
        report += "1. Start from home\n"
        for i, stop in enumerate(schedule['schedule'], 1):
            report += f"{i+1}. Drive to {stop['store']} ({stop['address']})\n"
        report += f"{len(schedule['schedule'])+2}. Return home\n\n"
        
        report += "*Note: Times are estimates. Check Google Maps for real-time traffic.*\n"
        
        return report

def main():
    """Test the route optimizer"""
    optimizer = RouteOptimizer()
    
    # Example: Find best route for these stores
    selected_stores = ["Metro Market", "Pick 'n Save", "Cermak Fresh Market"]
    
    # Generate route
    route_info = optimizer.find_optimal_route(selected_stores)
    print("Optimal Route:", route_info)
    
    # Generate schedule
    schedule = optimizer.optimize_for_time_windows(selected_stores, "09:00")
    print("\nShopping Schedule:", json.dumps(schedule, indent=2))
    
    # Generate full report
    report = optimizer.generate_route_report(
        selected_stores,
        savings_data={"Metro Market": 15.50, "Pick 'n Save": 12.30, "Cermak Fresh Market": 18.75}
    )
    
    # Save report
    with open("route_report.md", "w") as f:
        f.write(report)
    
    print("\nRoute report saved to route_report.md")

if __name__ == "__main__":
    main()
