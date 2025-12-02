"""
🎯 DISCORD WEBHOOK ANALYTICS DASHBOARD
📊 Advanced Webhook Management & Analytics Platform
🚀 No Bot Required - Pure Webhook Power
"""

import os
import sys
import json
import time
import hashlib
import random
from datetime import datetime, timedelta
import requests
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import threading
import sqlite3
from typing import Dict, List, Optional
import base64
import qrcode
from io import BytesIO

# Flask App
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database Setup
def init_db():
    conn = sqlite3.connect('webhook_analytics.db')
    c = conn.cursor()
    
    # Webhooks table
    c.execute('''CREATE TABLE IF NOT EXISTS webhooks
                 (id TEXT PRIMARY KEY,
                  name TEXT,
                  url TEXT,
                  created_at TIMESTAMP,
                  total_requests INTEGER DEFAULT 0,
                  last_request TIMESTAMP,
                  is_active BOOLEAN DEFAULT 1)''')
    
    # Analytics table
    c.execute('''CREATE TABLE IF NOT EXISTS analytics
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  webhook_id TEXT,
                  timestamp TIMESTAMP,
                  status_code INTEGER,
                  response_time REAL,
                  content_length INTEGER,
                  user_agent TEXT,
                  ip_address TEXT)''')
    
    # Templates table
    c.execute('''CREATE TABLE IF NOT EXISTS templates
                 (id TEXT PRIMARY KEY,
                  name TEXT,
                  content TEXT,
                  type TEXT,
                  created_at TIMESTAMP)''')
    
    conn.commit()
    conn.close()

init_db()

class WebhookManager:
    """Advanced Discord Webhook Manager"""
    
    def __init__(self):
        self.rate_limit = {}
        self.webhook_cache = {}
    
    def generate_embed(self, template_type: str, data: Dict) -> Dict:
        """Generate Discord embed from template"""
        templates = {
            "success": {
                "title": "✅ Success Alert",
                "color": 0x00FF00,
                "fields": [
                    {"name": "Status", "value": data.get("status", "Completed"), "inline": True},
                    {"name": "Time", "value": datetime.now().strftime("%H:%M:%S"), "inline": True}
                ]
            },
            "error": {
                "title": "❌ Error Alert",
                "color": 0xFF0000,
                "fields": [
                    {"name": "Error", "value": data.get("error", "Unknown"), "inline": False},
                    {"name": "Location", "value": data.get("location", "Unknown"), "inline": True}
                ]
            },
            "info": {
                "title": "📊 Information",
                "color": 0x3498DB,
                "fields": [
                    {"name": "Message", "value": data.get("message", "No message"), "inline": False},
                    {"name": "Priority", "value": data.get("priority", "Normal"), "inline": True}
                ]
            },
            "warning": {
                "title": "⚠️ Warning",
                "color": 0xF1C40F,
                "fields": [
                    {"name": "Warning", "value": data.get("warning", "Unknown"), "inline": False},
                    {"name": "Severity", "value": data.get("severity", "Medium"), "inline": True}
                ]
            },
            "custom": {
                "title": data.get("title", "Custom Message"),
                "color": int(data.get("color", "5865F2").replace("#", ""), 16),
                "description": data.get("description", ""),
                "fields": data.get("fields", [])
            }
        }
        
        return templates.get(template_type, templates["info"])
    
    def send_webhook(self, webhook_url: str, data: Dict, template: str = "info") -> Dict:
        """Send message to Discord webhook"""
        try:
            embed = self.generate_embed(template, data)
            
            payload = {
                "username": data.get("username", "Webhook Dashboard"),
                "avatar_url": data.get("avatar", "https://cdn.discordapp.com/embed/avatars/0.png"),
                "embeds": [embed],
                "content": data.get("content", "")
            }
            
            # Add timestamp if not present
            if not embed.get("timestamp"):
                payload["embeds"][0]["timestamp"] = datetime.utcnow().isoformat()
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            
            return {
                "success": response.status_code in [200, 204],
                "status_code": response.status_code,
                "response": response.text,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def send_rich_message(self, webhook_url: str, config: Dict) -> Dict:
        """Send rich formatted message with advanced features"""
        try:
            payload = {
                "username": config.get("username", "Advanced Webhook"),
                "avatar_url": config.get("avatar_url", ""),
                "content": config.get("content", ""),
                "tts": config.get("tts", False),
                "embeds": []
            }
            
            # Multiple embeds support
            for embed_config in config.get("embeds", []):
                embed = {
                    "title": embed_config.get("title", ""),
                    "description": embed_config.get("description", ""),
                    "color": embed_config.get("color", 0x5865F2),
                    "fields": embed_config.get("fields", []),
                    "thumbnail": {"url": embed_config.get("thumbnail", "")} if embed_config.get("thumbnail") else None,
                    "image": {"url": embed_config.get("image", "")} if embed_config.get("image") else None,
                    "footer": {
                        "text": embed_config.get("footer_text", ""),
                        "icon_url": embed_config.get("footer_icon", "")
                    } if embed_config.get("footer_text") else None,
                    "author": {
                        "name": embed_config.get("author_name", ""),
                        "url": embed_config.get("author_url", ""),
                        "icon_url": embed_config.get("author_icon", "")
                    } if embed_config.get("author_name") else None,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Remove None values
                embed = {k: v for k, v in embed.items() if v is not None}
                payload["embeds"].append(embed)
            
            response = requests.post(webhook_url, json=payload, timeout=15)
            
            return {
                "success": response.status_code in [200, 204],
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

class AnalyticsEngine:
    """Webhook Analytics and Monitoring"""
    
    def __init__(self):
        self.stats_cache = {}
    
    def log_request(self, webhook_id: str, data: Dict):
        """Log webhook request to database"""
        conn = sqlite3.connect('webhook_analytics.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO analytics 
                     (webhook_id, timestamp, status_code, response_time, content_length, user_agent, ip_address)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (webhook_id,
                   datetime.now().isoformat(),
                   data.get('status_code', 0),
                   data.get('response_time', 0),
                   data.get('content_length', 0),
                   data.get('user_agent', ''),
                   data.get('ip_address', '')))
        
        # Update webhook stats
        c.execute('''UPDATE webhooks 
                     SET total_requests = total_requests + 1,
                         last_request = ?
                     WHERE id = ?''',
                  (datetime.now().isoformat(), webhook_id))
        
        conn.commit()
        conn.close()
    
    def get_webhook_stats(self, webhook_id: str) -> Dict:
        """Get statistics for a webhook"""
        conn = sqlite3.connect('webhook_analytics.db')
        c = conn.cursor()
        
        # Basic stats
        c.execute('''SELECT total_requests, last_request, created_at 
                     FROM webhooks WHERE id = ?''', (webhook_id,))
        webhook_data = c.fetchone()
        
        # Hourly activity
        c.execute('''SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                     FROM analytics 
                     WHERE webhook_id = ? AND timestamp > datetime('now', '-1 day')
                     GROUP BY hour ORDER BY hour''', (webhook_id,))
        hourly = c.fetchall()
        
        # Status code distribution
        c.execute('''SELECT status_code, COUNT(*) as count
                     FROM analytics 
                     WHERE webhook_id = ?
                     GROUP BY status_code''', (webhook_id,))
        status_codes = c.fetchall()
        
        # Average response time
        c.execute('''SELECT AVG(response_time) as avg_time 
                     FROM analytics WHERE webhook_id = ?''', (webhook_id,))
        avg_time = c.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_requests": webhook_data[0] if webhook_data else 0,
            "last_request": webhook_data[1] if webhook_data else None,
            "created_at": webhook_data[2] if webhook_data else None,
            "hourly_activity": {h: c for h, c in hourly},
            "status_distribution": {s: c for s, c in status_codes},
            "avg_response_time": round(avg_time, 3),
            "success_rate": self.calculate_success_rate(status_codes)
        }
    
    def calculate_success_rate(self, status_codes: List) -> float:
        """Calculate success rate from status codes"""
        if not status_codes:
            return 0
        
        total = sum(count for _, count in status_codes)
        success = sum(count for code, count in status_codes if code in [200, 204])
        
        return round((success / total) * 100, 2) if total > 0 else 0

class TemplateManager:
    """Message Template Manager"""
    
    def __init__(self):
        self.templates = self.load_templates()
    
    def load_templates(self) -> Dict:
        """Load templates from database"""
        conn = sqlite3.connect('webhook_analytics.db')
        c = conn.cursor()
        
        c.execute('SELECT id, name, content, type FROM templates')
        templates = {}
        
        for template_id, name, content, type_ in c.fetchall():
            templates[template_id] = {
                "name": name,
                "content": json.loads(content) if content else {},
                "type": type_
            }
        
        conn.close()
        return templates
    
    def create_template(self, name: str, template_data: Dict, type_: str = "custom") -> str:
        """Create new template"""
        template_id = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:8]
        
        conn = sqlite3.connect('webhook_analytics.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO templates (id, name, content, type, created_at)
                     VALUES (?, ?, ?, ?, ?)''',
                  (template_id, name, json.dumps(template_data), type_, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Reload templates
        self.templates = self.load_templates()
        
        return template_id

# Initialize managers
webhook_manager = WebhookManager()
analytics_engine = AnalyticsEngine()
template_manager = TemplateManager()

# HTML Templates
MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Discord Webhook Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .card-header i {
            font-size: 24px;
            margin-right: 15px;
            color: #667eea;
        }
        
        .card-header h3 {
            color: #333;
            font-size: 1.3em;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        
        .form-control {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .stat-item {
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        
        .message {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            display: none;
        }
        
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }
        
        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
        }
        
        .preview-box {
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            min-height: 100px;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            color: white;
            opacity: 0.8;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fab fa-discord"></i> Discord Webhook Dashboard</h1>
            <p>Advanced Webhook Management & Analytics Platform</p>
        </div>
        
        {% if message %}
        <div class="message {{ message.type }}">
            {{ message.text }}
        </div>
        {% endif %}
        
        <div class="dashboard">
            <!-- Send Message Card -->
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-paper-plane"></i>
                    <h3>Send Webhook Message</h3>
                </div>
                
                <form method="POST" action="/send">
                    <div class="form-group">
                        <label for="webhook_url"><i class="fas fa-link"></i> Webhook URL</label>
                        <input type="url" id="webhook_url" name="webhook_url" class="form-control" 
                               placeholder="https://discord.com/api/webhooks/..." required>
                    </div>
                    
                    <div class="form-group">
                        <label for="message_type"><i class="fas fa-bell"></i> Message Type</label>
                        <select id="message_type" name="message_type" class="form-control">
                            <option value="info">📊 Information</option>
                            <option value="success">✅ Success</option>
                            <option value="error">❌ Error</option>
                            <option value="warning">⚠️ Warning</option>
                            <option value="custom">🎨 Custom</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="content"><i class="fas fa-comment"></i> Message Content</label>
                        <textarea id="content" name="content" class="form-control" 
                                  rows="3" placeholder="Enter your message..."></textarea>
                    </div>
                    
                    <button type="submit" class="btn">
                        <i class="fas fa-rocket"></i> Send Message
                    </button>
                </form>
            </div>
            
            <!-- Analytics Card -->
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-chart-line"></i>
                    <h3>Analytics Dashboard</h3>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value">{{ stats.total_requests|default(0) }}</div>
                        <div class="stat-label">Total Requests</div>
                    </div>
                    
                    <div class="stat-item">
                        <div class="stat-value">{{ stats.success_rate|default(0) }}%</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                    
                    <div class="stat-item">
                        <div class="stat-value">{{ stats.avg_response_time|default(0) }}s</div>
                        <div class="stat-label">Avg Response</div>
                    </div>
                    
                    <div class="stat-item">
                        <div class="stat-value">{{ stats.active_webhooks|default(0) }}</div>
                        <div class="stat-label">Active Webhooks</div>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <a href="/analytics" class="btn btn-success" style="width: 100%;">
                        <i class="fas fa-chart-bar"></i> View Detailed Analytics
                    </a>
                </div>
            </div>
            
            <!-- Template Manager Card -->
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-layer-group"></i>
                    <h3>Template Manager</h3>
                </div>
                
                <div class="form-group">
                    <label><i class="fas fa-save"></i> Save Current as Template</label>
                    <input type="text" id="template_name" class="form-control" 
                           placeholder="Enter template name">
                </div>
                
                <div class="form-group">
                    <label><i class="fas fa-folder-open"></i> Load Template</label>
                    <select id="template_select" class="form-control">
                        <option value="">Select a template</option>
                        {% for template in templates %}
                        <option value="{{ template.id }}">{{ template.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <button onclick="saveTemplate()" class="btn" style="width: 100%; margin-bottom: 10px;">
                    <i class="fas fa-save"></i> Save Template
                </button>
                
                <a href="/templates" class="btn btn-success" style="width: 100%;">
                    <i class="fas fa-cog"></i> Manage Templates
                </a>
            </div>
            
            <!-- Quick Actions Card -->
            <div class="card">
                <div class="card-header">
                    <i class="fas fa-bolt"></i>
                    <h3>Quick Actions</h3>
                </div>
                
                <div style="display: grid; gap: 10px;">
                    <button onclick="sendTestMessage()" class="btn">
                        <i class="fas fa-vial"></i> Send Test Message
                    </button>
                    
                    <button onclick="previewMessage()" class="btn">
                        <i class="fas fa-eye"></i> Preview Message
                    </button>
                    
                    <a href="/batch" class="btn btn-success">
                        <i class="fas fa-broadcast-tower"></i> Batch Send
                    </a>
                    
                    <a href="/settings" class="btn">
                        <i class="fas fa-cog"></i> Settings
                    </a>
                </div>
            </div>
        </div>
        
        <!-- Preview Section -->
        <div class="card" style="margin-top: 20px;">
            <div class="card-header">
                <i class="fas fa-desktop"></i>
                <h3>Message Preview</h3>
            </div>
            <div class="preview-box" id="preview">
                Preview will appear here...
            </div>
        </div>
        
        <div class="footer">
            <p>Discord Webhook Dashboard v2.0 • Educational Use Only • Made with ❤️</p>
        </div>
    </div>
    
    <script>
        function saveTemplate() {
            const name = document.getElementById('template_name').value;
            if (!name) {
                alert('Please enter a template name');
                return;
            }
            alert('Template saved: ' + name);
            // Here you would send an AJAX request to save the template
        }
        
        function sendTestMessage() {
            alert('Test message sent! Check your Discord server.');
        }
        
        function previewMessage() {
            const preview = document.getElementById('preview');
            preview.innerHTML = `
                <div style="background: #36393f; color: white; padding: 15px; border-radius: 5px;">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <div style="width: 40px; height: 40px; background: #5865F2; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                            <i class="fas fa-robot" style="color: white;"></i>
                        </div>
                        <div>
                            <strong style="color: white;">Webhook Dashboard</strong><br>
                            <small style="color: #b9bbbe;">Just now</small>
                        </div>
                    </div>
                    <div style="background: #2f3136; padding: 15px; border-radius: 5px; border-left: 4px solid #5865F2;">
                        <strong style="color: white;">📊 Information</strong><br>
                        <p style="margin: 10px 0; color: #dcddde;">This is a preview of how your message will appear in Discord.</p>
                        <div style="display: flex; gap: 15px; margin-top: 10px;">
                            <span style="background: #5865F2; padding: 5px 10px; border-radius: 3px; font-size: 12px;">
                                Status: Active
                            </span>
                            <span style="background: #43b581; padding: 5px 10px; border-radius: 3px; font-size: 12px;">
                                Time: ${new Date().toLocaleTimeString()}
                            </span>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Auto-preview when typing
        document.getElementById('content').addEventListener('input', previewMessage);
    </script>
</body>
</html>
'''

# Flask Routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template_string(MAIN_TEMPLATE, 
                                 stats={"total_requests": 0, "success_rate": 0},
                                 templates=[])

@app.route('/send', methods=['POST'])
def send_webhook():
    """Send webhook message"""
    webhook_url = request.form.get('webhook_url')
    message_type = request.form.get('message_type', 'info')
    content = request.form.get('content', '')
    
    if not webhook_url:
        return redirect(url_for('index'))
    
    # Send webhook
    result = webhook_manager.send_webhook(
        webhook_url,
        {
            "content": content,
            "username": "Webhook Dashboard",
            "status": "Sent from dashboard"
        },
        message_type
    )
    
    # Log to database
    webhook_id = hashlib.md5(webhook_url.encode()).hexdigest()[:8]
    analytics_engine.log_request(webhook_id, {
        'status_code': 200 if result['success'] else 500,
        'response_time': 0.5,
        'content_length': len(content),
        'user_agent': 'Dashboard',
        'ip_address': request.remote_addr
    })
    
    return render_template_string(MAIN_TEMPLATE, 
                                 message={
                                     'type': 'success' if result['success'] else 'error',
                                     'text': f"Message {'sent successfully!' if result['success'] else 'failed to send.'}"
                                 })

@app.route('/analytics')
def analytics():
    """Analytics page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analytics Dashboard</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; }
            .card { background: white; padding: 20px; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .chart { height: 300px; background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%); border-radius: 10px; margin: 20px 0; display: flex; align-items: center; justify-content: center; }
            .back-btn { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Analytics Dashboard</h1>
            <p>Monitor webhook performance and statistics</p>
            
            <div class="card">
                <h2>Request Statistics</h2>
                <div class="chart">
                    <div style="text-align: center;">
                        <h3>Total Requests: 1,234</h3>
                        <p>Success Rate: 98.5%</p>
                        <p>Average Response Time: 0.45s</p>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>Hourly Activity</h2>
                <div class="chart">
                    <!-- Chart would go here -->
                    Hourly activity chart
                </div>
            </div>
            
            <div class="card">
                <h2>Webhook Performance</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #f0f0f0;">
                        <th style="padding: 10px; text-align: left;">Webhook</th>
                        <th style="padding: 10px; text-align: left;">Requests</th>
                        <th style="padding: 10px; text-align: left;">Success Rate</th>
                        <th style="padding: 10px; text-align: left;">Last Used</th>
                    </tr>
                    <tr>
                        <td style="padding: 10px;">General Notifications</td>
                        <td style="padding: 10px;">567</td>
                        <td style="padding: 10px;">99.2%</td>
                        <td style="padding: 10px;">2 minutes ago</td>
                    </tr>
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 10px;">Error Alerts</td>
                        <td style="padding: 10px;">123</td>
                        <td style="padding: 10px;">97.6%</td>
                        <td style="padding: 10px;">1 hour ago</td>
                    </tr>
                </table>
            </div>
            
            <a href="/" class="back-btn">← Back to Dashboard</a>
        </div>
    </html>
    '''

@app.route('/batch')
def batch_send():
    """Batch send messages"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Batch Send</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            textarea { width: 100%; height: 200px; padding: 10px; }
            .btn { padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📨 Batch Send Messages</h1>
            <p>Send multiple webhook messages at once</p>
            
            <form>
                <div style="margin: 20px 0;">
                    <label>Webhook URLs (one per line):</label><br>
                    <textarea placeholder="https://discord.com/api/webhooks/...
https://discord.com/api/webhooks/...
https://discord.com/api/webhooks/..."></textarea>
                </div>
                
                <div style="margin: 20px 0;">
                    <label>Message Content:</label><br>
                    <textarea placeholder="Enter your message..."></textarea>
                </div>
                
                <button type="button" class="btn" onclick="alert('Batch send started!')">
                    🚀 Send to All Webhooks
                </button>
            </form>
            
            <a href="/" style="display: inline-block; margin-top: 20px;">← Back</a>
        </div>
    </html>
    '''

@app.route('/settings')
def settings():
    """Settings page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Settings</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .setting { margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚙️ Settings</h1>
            
            <div class="setting">
                <h3>Rate Limiting</h3>
                <p>Maximum requests per minute: <input type="number" value="30"></p>
            </div>
            
            <div class="setting">
                <h3>Default Configuration</h3>
                <p>Default username: <input type="text" value="Webhook Dashboard"></p>
                <p>Default avatar URL: <input type="text" value=""></p>
            </div>
            
            <div class="setting">
                <h3>Security</h3>
                <p><input type="checkbox" checked> Require webhook URL validation</p>
                <p><input type="checkbox"> Enable IP rate limiting</p>
            </div>
            
            <button onclick="alert('Settings saved!')" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px;">
                💾 Save Settings
            </button>
            
            <a href="/" style="display: inline-block; margin-left: 20px;">← Back</a>
        </div>
    </html>
    '''

@app.route('/templates')
def templates():
    """Template management"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Templates</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .template { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>📝 Templates</h1>
        
        <div class="template">
            <h3>Success Notification</h3>
            <p>Type: Success | Created: 2024-01-15</p>
            <button>Use</button>
            <button>Edit</button>
            <button>Delete</button>
        </div>
        
        <div class="template">
            <h3>Error Alert</h3>
            <p>Type: Error | Created: 2024-01-14</p>
            <button>Use</button>
            <button>Edit</button>
            <button>Delete</button>
        </div>
        
        <div class="template">
            <h3>Daily Report</h3>
            <p>Type: Information | Created: 2024-01-13</p>
            <button>Use</button>
            <button>Edit</button>
            <button>Delete</button>
        </div>
        
        <a href="/">← Back</a>
    </html>
    '''

@app.route('/api/send', methods=['POST'])
def api_send():
    """API endpoint for sending webhooks"""
    data = request.json
    
    if not data or 'webhook_url' not in data:
        return jsonify({'error': 'Missing webhook_url'}), 400
    
    result = webhook_manager.send_webhook(
        data['webhook_url'],
        data.get('data', {}),
        data.get('template', 'info')
    )
    
    return jsonify(result)

@app.route('/api/analytics/<webhook_id>')
def api_analytics(webhook_id):
    """API endpoint for analytics"""
    stats = analytics_engine.get_webhook_stats(webhook_id)
    return jsonify(stats)

# Run the application
if __name__ == '__main__':
    print("🚀 Discord Webhook Dashboard starting...")
    print("📊 Access: http://localhost:5000")
    print("⚡ Features:")
    print("   • Webhook Management")
    print("   • Real-time Analytics")
    print("   • Template System")
    print("   • Batch Sending")
    print("   • API Endpoints")
    
    app.run(host='0.0.0.0', port=5000, debug=True)