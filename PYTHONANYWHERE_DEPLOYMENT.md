# 🚀 PythonAnywhere Deployment Guide

## 📋 Prerequisites
- PythonAnywhere account (free or paid)
- GitHub repository with your code
- WhatsApp Business API credentials

## 🔧 Step 1: Upload Code to PythonAnywhere

### Option A: Clone from GitHub
```bash
# In PythonAnywhere console
git clone https://github.com/sembesalum/cheka-comedian-vote-bot.git
cd cheka-comedian-vote-bot
```

### Option B: Upload via Files tab
1. Go to Files tab in PythonAnywhere
2. Upload all project files
3. Extract if needed

## 🐍 Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## ⚙️ Step 3: Configure Settings

### Update settings.py for production:
```python
# In comedian_voting_bot/settings.py
DEBUG = False
ALLOWED_HOSTS = ['levelsprotech2.pythonanywhere.com', 'www.levelsprotech2.pythonanywhere.com']

# WhatsApp Configuration (already set)
WHATSAPP_TOKEN = 'EAAr1kvlgqhIBPZA0Mq7685iD5aEGm9A2TC5Xp2nVtc8ZCFA2v7vQcdZCg1O1MGpZCchvDwpFvBLOUxyYg7nNJLK84phJhOPw4Hp66vPLcpH1TCg4YyaN78pf8tUzN48rKBR5oeSNU5EbhNNsGw9wAg6KqEoA1ipFNgLZAOjWc9V6VDrhlsQoLHcEUqMST2USjKwZDZD'
WHATSAPP_PHONE_NUMBER_ID = '537559402774394'
WHATSAPP_BUSINESS_ACCOUNT_ID = '528995370286469'
WHATSAPP_VERIFY_TOKEN = 'c2a49926-a81c-11ef-b864-0242ac120002'
```

## 🗄️ Step 4: Set Up Database

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Set up initial data
python manage.py setup_data
```

## 🌐 Step 5: Configure Web App

### In PythonAnywhere Web tab:
1. **Source code**: `/home/yourusername/cheka-comedian-vote-bot`
2. **Working directory**: `/home/yourusername/cheka-comedian-vote-bot`
3. **WSGI configuration file**: `/home/yourusername/cheka-comedian-vote-bot/comedian_voting_bot/wsgi.py`

### Update WSGI file:
```python
# In comedian_voting_bot/wsgi.py
import os
import sys

# Add your project directory to the Python path
path = '/home/yourusername/cheka-comedian-vote-bot'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comedian_voting_bot.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 🔗 Step 6: Configure WhatsApp Webhook

### In Meta Developer Console:
1. Go to your WhatsApp Business API app
2. Navigate to Configuration > Webhooks
3. Set webhook URL: `https://levelsprotech2.pythonanywhere.com/webhook/`
4. Set verify token: `c2a49926-a81c-11ef-b864-0242ac120002`
5. Subscribe to `messages` events

## 📊 Step 7: Test and Monitor

### Test Endpoints:
- **Webhook**: `https://levelsprotech2.pythonanywhere.com/webhook/`
- **Logs (HTML)**: `https://levelsprotech2.pythonanywhere.com/logs/`
- **Logs (JSON)**: `https://levelsprotech2.pythonanywhere.com/api/logs/`
- **Errors**: `https://levelsprotech2.pythonanywhere.com/api/errors/`
- **Votes**: `https://levelsprotech2.pythonanywhere.com/api/votes/`
- **Stats**: `https://levelsprotech2.pythonanywhere.com/api/vote-stats/`

### Test WhatsApp Bot:
1. Send message to your WhatsApp number
2. Check logs at `/logs/` to see activity
3. Verify webhook is receiving messages

## 🐛 Debugging on PythonAnywhere

### View Logs:
1. **HTML Interface**: Visit `https://levelsprotech2.pythonanywhere.com/logs/`
2. **Console Logs**: Check PythonAnywhere error logs in Web tab
3. **File Logs**: Access `/home/yourusername/cheka-comedian-vote-bot/logs/whatsapp_bot.log`

### Common Issues:

#### 1. Import Errors
```bash
# Check if all files are uploaded correctly
ls -la whatsapp_bot/
```

#### 2. Database Issues
```bash
# Run migrations
python manage.py migrate

# Check database
python manage.py dbshell
```

#### 3. Webhook Not Working
- Check webhook URL in Meta Developer Console
- Verify verify token matches
- Check PythonAnywhere error logs

#### 4. WhatsApp API Errors
- Check logs at `/logs/` for API errors
- Verify token is valid and not expired
- Check phone number ID

## 📱 Step 8: Test Complete Flow

### Send Test Messages:
1. **Start**: Send "hi" or "anza"
2. **Clear Session**: Send "#"
3. **Vote**: Follow the interactive flow
4. **Check Logs**: Monitor at `/logs/`

### Expected Log Entries:
- Webhook verification attempts
- Message processing
- Session management
- Payment processing
- API calls to WhatsApp

## 🔄 Step 9: Maintenance

### Regular Tasks:
1. **Monitor Logs**: Check `/logs/` regularly
2. **Check Errors**: Review `/api/errors/` for issues
3. **Update Data**: Use `/api/create-test-data/` to refresh comedians
4. **View Stats**: Monitor voting at `/api/vote-stats/`

### Log Rotation:
```bash
# Create log rotation script
echo "0 0 * * * find /home/yourusername/cheka-comedian-vote-bot/logs -name '*.log' -mtime +7 -delete" | crontab -
```

## 🚨 Troubleshooting

### If Bot Stops Working:
1. Check PythonAnywhere error logs
2. Verify webhook is still configured
3. Check WhatsApp token hasn't expired
4. Restart web app in PythonAnywhere

### If Logs Don't Show:
1. Check file permissions: `chmod 755 logs/`
2. Verify Django can write to logs directory
3. Check PythonAnywhere console for errors

### If Webhook Fails:
1. Test webhook URL manually
2. Check verify token matches exactly
3. Verify webhook is subscribed to messages
4. Check PythonAnywhere error logs

## 📞 Support

### Log Analysis:
- **All Logs**: `https://levelsprotech2.pythonanywhere.com/logs/`
- **Errors Only**: `https://levelsprotech2.pythonanywhere.com/api/errors/`
- **Vote Statistics**: `https://levelsprotech2.pythonanywhere.com/api/vote-stats/`

### File Locations:
- **Logs**: `/home/yourusername/cheka-comedian-vote-bot/logs/`
- **Code**: `/home/yourusername/cheka-comedian-vote-bot/`
- **Database**: `/home/yourusername/cheka-comedian-vote-bot/db.sqlite3`

---

## 🎉 Success!

Your WhatsApp voting bot is now deployed and ready to use! Users can:
- Send "hi" or "anza" to start voting
- Send "#" to clear any ongoing session
- Follow the interactive voting flow
- Receive tickets after payment

Monitor everything through the logs interface at `/logs/`! 🚀
