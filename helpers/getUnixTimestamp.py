# ts.py
from datetime import datetime
import argparse

parser = argparse.ArgumentParser(description="Convert date to Unix timestamp")
parser.add_argument("date", help="Date in format YYYY-MM-DD")
parser.add_argument("--time", default="00:00:00", help="Time HH:MM:SS (default 00:00:00)")

args = parser.parse_args()

dt = datetime.strptime(f"{args.date} {args.time}", "%Y-%m-%d %H:%M:%S")
print(int(dt.timestamp()))