from app.dbaccess import upload_game_package
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

GAME_ZIP_FILE = r"D:\Projects\godot\holocardclient\export\game.zip"

upload_game_package(GAME_ZIP_FILE)

print("Done!")