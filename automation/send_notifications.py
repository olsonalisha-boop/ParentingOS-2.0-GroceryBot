#!/usr/bin/env python3
"""
Email notification system for deal alerts
Sends beautiful HTML emails with found deals
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import requests

class EmailNotifier:
    def __init__(self):
        self.sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        self.email_address = os.environ.get('EMAIL_ADDRESS')
        self.base_dir = Path(__file__).parent.parent
        
    def load_deals_report(self) -> Dict:
        """Load the latest deals report"""
        output_dir = self.base_dir / "output"
        reports = sorted(output_dir.glob("shopping_report_*.md"), reverse=True)
        
        if not reports:
            return None
            
        # Parse markdown report
        with open(reports[0], 'r') as f:
            content = f.read()
            
        # Extract key information
        deals = {
            'date': datetime.now().strftime('%B %d, %Y'),
            'total_savings': 0,
            'best_deals': [],
            'recommended_stores': []
        }
        
        # Parse savings amount
        import re
        savings_match = re.search(r'Total potential savings: \$(\d+\.\d+)', content)
        if savings_match:
            deals['total_savings'] = float(savings_match[1])
        
        # Parse deals
        deal_pattern = re.compile(r'### (.*?)\n.*?Best Price: \$([\d.]+) at (.*?)\n')
        for match in deal_pattern.finditer(content):
            deals['best_deals'].append({
                'item': match.group(1),
                'price': match.group(2),
                'store': match.group(3)
            })
        
        return deals
    
    def create_html_email(self, deals: Dict) -> str:
        """Create beautiful HTML email"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Shopping Deals for {deals['date']}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                    margin: -30px -30px 30px -30px;
                }}
                .savings-badge {{
                    display: inline-block;
                    background-color: #10b981;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 25px;
                    font-size: 24px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .deal-card {{
                    background-color: #f9fafb;
                    border-left: 4px solid #667eea;
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 5px;
                }}
                .deal-item {{
                    font-weight: bold;
                    color: #1f2937;
                    font-size: 16px;
                }}
                .deal-price {{
                    color: #059669;
                    font-size: 20px;
                    font-weight: bold;
                }}
                .deal-store {{
                    color: #6b7280;
                    font-size: 14px;
                }}
                .action-button {{
                    display: inline-block;
                    background-color: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #6b7280;
                    font-size: 12px;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛒 Your Shopping Deals Are Ready!</h1>
                    <div class="savings-badge">
                        Save ${deals['total_savings']:.2f} Today!
                    </div>
                </div>
                
                <h2>🔥 Top Deals Found</h2>
                <p>We've analyzed prices at all your local stores. Here are today's best deals:</p>
                """
        
        # Add deals
        for deal in deals['best_deals'][:5]:  # Top 5 deals
            html += f"""
                <div class="deal-card">
                    <div class="deal-item">{deal['item']}</div>
                    <div class="deal-price">${deal['price']}</div>
                    <div class="deal-store">Available at {deal['store']}</div>
                </div>
            """
        
        html += f"""
                <div style="text-align: center;">
                    <a href="https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}/actions" class="action-button">
                        View Full Report
                    </a>
                </div>
                
                <h3>📍 Recommended Shopping Route</h3>
                <p>Visit these stores in order for maximum efficiency:</p>
                <ol>
        """
        
        for store in deals.get('recommended_stores', [])[:3]:
            html += f"<li>{store}</li>"
        
        html += """
                </ol>
                
                <div class="footer">
                    <p>You're receiving this because you have deal alerts enabled.</p>
                    <p>Smart Shopping System • Save Money, Save Time</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_email(self, html_content: str, subject: str = None):
        """Send email via SendGrid"""
        if not self.sendgrid_key or not self.email_address:
            print("Email configuration missing")
            return False
        
        if not subject:
            subject = f"💰 Shopping Deals for {datetime.now().strftime('%B %d')}"
        
        # SendGrid API
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {self.sendgrid_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "personalizations": [{
                "to": [{"email": self.email_address}]
            }],
            "from": {"email": "deals@smartshoppingsystem.com", "name": "Smart Shopping System"},
            "subject": subject,
            "content": [
                {"type": "text/html", "value": html_content}
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 202:
                print(f"✅ Email sent successfully to {self.email_address}")
                return True
            else:
                print(f"❌ Email failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False
    
    def send_text_notification(self, message: str, phone: str = None):
        """Send SMS notification via Twilio (optional)"""
        twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
        twilio_from = os.environ.get('TWILIO_PHONE_NUMBER')
        
        if not all([twilio_sid, twilio_token, twilio_from, phone]):
            return False
        
        try:
            from twilio.rest import Client
            client = Client(twilio_sid, twilio_token)
            
            message = client.messages.create(
                body=message,
                from_=twilio_from,
                to=phone
            )
            
            print(f"✅ SMS sent: {message.sid}")
            return True
        except Exception as e:
            print(f"SMS error: {e}")
            return False

def main():
    """Main execution"""
    notifier = EmailNotifier()
    
    # Load deals
    deals = notifier.load_deals_report()
    
    if not deals:
        print("No deals report found")
        return
    
    # Only send if significant savings
    if deals['total_savings'] > 10:
        # Create and send email
        html = notifier.create_html_email(deals)
        notifier.send_email(html)
        
        # Optional: Send SMS for big savings
        if deals['total_savings'] > 50:
            sms_message = f"🔥 Shopping Alert: Save ${deals['total_savings']:.2f} today! Check your email for details."
            phone = os.environ.get('SMS_PHONE')
            if phone:
                notifier.send_text_notification(sms_message, phone)
    else:
        print("Savings too small, skipping notification")

if __name__ == "__main__":
    main()
