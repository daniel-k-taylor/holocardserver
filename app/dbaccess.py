import os
import json
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
import secrets
import string
import logging
logger = logging.getLogger(__name__)

MATCH_LOG_CONTAINER = "holomatchlogs"

def generate_short_alphanumeric_id(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def upload_match_to_blob_storage(match_data):
    # Retrieve the connection string from an environment variable for security
    AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    if not AZURE_STORAGE_CONNECTION_STRING:
        raise ValueError("Please set the AZURE_STORAGE_CONNECTION_STRING environment variable.")

    # Initialize BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

    # Define the container name
    container_name = MATCH_LOG_CONTAINER

    container_client = blob_service_client.get_container_client(container_name)

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
    try:
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
