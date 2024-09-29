import os
from app.dbaccess import download_blobs_between_dates
from dotenv import load_dotenv
from datetime import datetime, timezone
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


# Define date range for filtering blobs (UTC time)
START_DATE = datetime(2024, 9, 1, tzinfo=timezone.utc)  # Change to your start date
END_DATE = datetime(2024, 10, 30, tzinfo=timezone.utc)   # Change to your end date

# Make the directory to download this dir + tests\match_logs
current_directory = os.getcwd()
download_path = os.path.join(current_directory, "tests", "match_logs")

download_blobs_between_dates(START_DATE, END_DATE, download_path)

print("Done!")