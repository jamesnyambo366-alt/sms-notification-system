import os
import time
from twilio.rest import Client
import sqlite3
from apscheduler.schedulers.blocking import BlockingScheduler

# Twilio API credentials
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Database connection
DATABASE_NAME = 'notifications.db'

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Connect to the database
conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

# Create a table for messages if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS messages\n                  (id INTEGER PRIMARY KEY, recipient TEXT, message TEXT, status TEXT)''')
conn.commit()

def send_sms(recipient, message):
    try:
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=recipient
        )
        print(f"Message sent to {recipient}: {message.sid}")
        # Update the message status in the database
        cursor.execute('''INSERT INTO messages (recipient, message, status)\n                          VALUES (?, ?, ?)''', (recipient, message.body, 'sent'))
        conn.commit()
    except Exception as e:
        print(f"Failed to send message to {recipient}: {str(e)}")

# Scheduled sending function
def scheduled_sending():
    # Example message and recipient
    recipient = '+1234567890' # Replace with actual number
    message = 'This is a scheduled SMS notification.'
    send_sms(recipient, message)

# Scheduler setup
scheduler = BlockingScheduler()
# Schedule the task every day at 10:00 AM
scheduler.add_job(scheduled_sending, 'cron', hour=10, minute=0)

if __name__ == '__main__':
    print('Starting SMS notification system...')
    scheduler.start()