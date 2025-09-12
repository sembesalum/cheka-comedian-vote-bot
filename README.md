# Comedian Voting WhatsApp Bot

A Django-based WhatsApp bot for voting on comedians with ticket generation and payment processing.

## Features

- WhatsApp webhook integration
- Interactive voting flow with buttons and lists
- Comedian selection and vote quantity options
- Dummy payment processing
- Unique ticket generation
- API endpoints for viewing votes and statistics

## Setup

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration:**
   WhatsApp credentials are already configured in `settings.py`. No additional setup needed!

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Set up initial data:**
   ```bash
   python manage.py setup_data
   ```

6. **Start the server:**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

- `GET /webhook/` - WhatsApp webhook endpoint
- `GET /api/votes/` - View all votes
- `GET /api/vote-stats/` - Get voting statistics
- `POST /api/create-test-data/` - Create test data

## WhatsApp Flow

1. **Welcome Message** - User sends any message to start
2. **Comedian Selection** - Interactive list of comedians
3. **Vote Confirmation** - Shows selected comedian with quantity options
4. **Payment Processing** - Dummy payment with instant success
5. **Ticket Generation** - Generates unique ticket codes
6. **Confirmation** - Shows tickets and winner announcement date
7. **Play Again** - Option to start new vote

## Models

- **Comedian** - Stores comedian information
- **VotingSession** - Manages voting periods
- **Vote** - Individual vote records
- **Ticket** - Generated ticket codes
- **Payment** - Payment tracking (dummy implementation)

## Testing

Use ngrok to expose your local server for WhatsApp webhook testing:

```bash
ngrok http 8000
```

Then update your WhatsApp webhook URL to: `https://your-ngrok-url.ngrok.io/webhook/`
