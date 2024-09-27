import os
import zipfile
import json
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
import secrets
import string
import aiofiles
import logging
logger = logging.getLogger(__name__)

STATIC_FILE_NAME = "game.zip"
STATIC_FILES_CONTAINER = "holostaticfiles"
MATCH_LOG_CONTAINER = "holomatchlogs"

def generate_short_alphanumeric_id(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def _get_azure_blob_service_client():
    # Retrieve the connection string from an environment variable for security
    AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    if not AZURE_STORAGE_CONNECTION_STRING:
        logger.error("Please set the AZURE_STORAGE_CONNECTION_STRING environment variable.")
        return None

    # Initialize BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    return blob_service_client

def _get_azure_container_client(container_name):
    # Initialize BlobServiceClient
    blob_service_client = _get_azure_blob_service_client()
    if not blob_service_client:
        return None

    container_client = blob_service_client.get_container_client(container_name)
    return container_client

def upload_match_to_blob_storage(match_data):
    try:
        container_client = _get_azure_container_client(MATCH_LOG_CONTAINER)
        if not container_client:
            return

        uuid = generate_short_alphanumeric_id()
        blob_name = f"match_{uuid}_{match_data["player_info"][0]["username"]}_VS_{match_data["player_info"][1]["username"]}.json"

        metadata = {
            "player1": match_data["player_info"][0]["username"],
            "player2": match_data["player_info"][1]["username"],
            "player1_clock": str(match_data["player_clocks"][0]),
            "player2_clock": str(match_data["player_clocks"][1]),
            "player1_life": str(match_data["player_final_life"][0]),
            "player2_life": str(match_data["player_final_life"][1]),
            "oshi1": match_data["player_info"][0]["oshi_id"],
            "oshi2": match_data["player_info"][1]["oshi_id"],
            "game_over_reason": match_data["game_over_reason"],
            "queue_name": match_data["queue_name"],
            "starting_player": match_data["starting_player"],
            "turn_count": str(match_data["turn_number"]),
            "winner": match_data["winner"],
        }

        json_data = json.dumps(match_data, indent=2)
        upload_blob(container_client, json_data, blob_name, metadata)
    except Exception as e:
        logger.error(f"Error uploading match data to Blob Storage: {e}")

# Function to upload a file to Blob Storage with optional metadata
def upload_blob(client : ContainerClient, data, blob_name, metadata):
    """
    Uploads data to Azure Blob Storage with optional metadata.
    """
    blob_client = client.get_blob_client(blob_name)

    blob_client.upload_blob(data, overwrite=True, metadata=metadata)

def upload_game_package(game_zip_path):
    try:
        container_client = _get_azure_container_client(STATIC_FILES_CONTAINER)
        if not container_client:
            return

        blob_name = f"game.zip"
        with open(game_zip_path, "rb") as data:
            upload_blob(container_client, data, blob_name, None)

    except Exception as e:
        logger.error(f"Error uploading static files to Blob Storage: {e}")

async def download_and_extract_game_package(destination_path):
    # Make sure the base of destination_path exists.
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    # Store the local zip one directory up from the destination path.
    local_zip_path = os.path.join(os.path.dirname(destination_path), STATIC_FILE_NAME)

    try:
        blob_service_client = _get_azure_blob_service_client()
        blob_client = blob_service_client.get_blob_client(container=STATIC_FILES_CONTAINER, blob=STATIC_FILE_NAME)

        logger.info(f"Download files to {local_zip_path}")
        async with aiofiles.open(local_zip_path, 'wb') as file:
                stream = blob_client.download_blob()
                data = stream.readall()
                await file.write(data)

        logger.info(f"Unpacking zip file to {destination_path}")
        # Unpack the zip file
        with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
            zip_ref.extractall(destination_path)
    except Exception as e:
        logger.error(f"Error download static files: {e}")