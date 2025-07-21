import requests
import schedule
import time
import urllib3
import os
import logging
from dotenv import load_dotenv
load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

UNIFI_URL = os.getenv("UNIFI_URL")
USERNAME = os.getenv("UNIFI_USERNAME")
PASSWORD = os.getenv("UNIFI_PASSWORD")
SITE = os.getenv("UNIFI_SITE", "default")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_USER = os.getenv("PUSHOVER_USER")
TRUSTED_MACS_PATH = os.getenv("TRUSTED_MACS_PATH", "/app/config/trusted.txt")
interval = int(os.getenv("CHECK_INTERVAL", "5"))  # default to 5 minutes

# Ensure log directory exists
os.makedirs("/app/logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/logs.txt"),
        logging.StreamHandler()  # also prints to Docker logs
    ]
)

log = logging.getLogger(__name__)

def load_trusted_macs():
    macs = set()
    try:
        with open(TRUSTED_MACS_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                mac = line.split("#")[0].strip().lower()
                macs.add(mac)
    except Exception as e:
        log.error(f"Failed to read trusted MACs: {e}")
    return macs

def send_pushover_alert(mac, ip, hostname):
    message = (
        f"⚠️ Unknown device detected\n"
        f"MAC: {mac}\n"
        f"IP: {ip}\n"
        f"Name: {hostname}"
    )
    payload = {
        "token": PUSHOVER_TOKEN,
        "user": PUSHOVER_USER,
        "message": message,
        "title": "NetWatcher Alert",
        "priority": 0
    }
    r = requests.post("https://api.pushover.net/1/messages.json", data=payload)
    r.raise_for_status()

def get_session():
    session = requests.Session()
    session.verify = False  # For self-signed certs; set to True for trusted certs

    login_url = f"{UNIFI_URL}/api/auth/login"
    payload = {"username": USERNAME, "password": PASSWORD}
    headers = {"Content-Type": "application/json"}

    response = session.post(login_url, json=payload, headers=headers)
    response.raise_for_status()

    return session

def fetch_mac_addresses(session):
    url = f"{UNIFI_URL}/proxy/network/api/s/{SITE}/stat/sta"
    response = session.get(url)
    response.raise_for_status()
    data = response.json()
    return data.get("data", [])  # Return the full list of clients (dicts)

def check_macs():
    try:
        log.info("Checking MAC addresses...")
        session = get_session()
        clients = fetch_mac_addresses(session)
        trusted_macs = load_trusted_macs()

        for client in clients:
            mac = client.get("mac", "").lower()
            ip = client.get("ip", "N/A")
            hostname = client.get("hostname", "Unknown")

            if mac and mac not in trusted_macs:
                log.warning(f"Unknown MAC: {mac} | IP: {ip} | Hostname: {hostname}")
                send_pushover_alert(mac, ip, hostname)
    except Exception as e:
        log.error(f"Error during check: {e}")

schedule.every(interval).minutes.do(check_macs)

log.info(f"Scheduling MAC check every {interval} minutes.")

log.info("NETWATCHER Service started...")
while True:
    schedule.run_pending()
    time.sleep(1)
