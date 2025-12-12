import os
import requests
from dotenv import load_dotenv
import time
from azure.storage.queue import QueueClient


load_dotenv()


# --- CONFIGURATION ---
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_QUEUE_NAME = os.getenv("AZURE_QUEUE_NAME")

# CRITICAL: How long (in seconds) to "hide" the message while processing.
# If your AI takes 5 seconds, set this to 30s to be safe.
# If you don't delete the message by then, it reappears in the queue.
VISIBILITY_TIMEOUT = int(os.getenv("VISIBILITY_TIMEOUT", "60"))

COIN_API = os.getenv("COIN_API", "http://localhost:6080/predict")
GRAIN_API = os.getenv("GRAIN_API", "http://localhost:6081/predict")
DATABASE_API = os.getenv("DATABASE_API", "http://localhost:4321/api/process/")


def get_scale(image: bytes):
    response = requests.post(COIN_API, files={"image": image})
    response.raise_for_status()
    return response.json()


def get_grain_size(
    image: bytes,
    mm_per_pixel: str,
    coin_center_x: str,
    coin_center_y: str,
    coin_radius_px: str,
):
    response = requests.post(
        GRAIN_API,
        data={
            "coin_center_x": coin_center_x,
            "coin_center_y": coin_center_y,
            "coin_radius_px": coin_radius_px,
            "mm_per_pixel": mm_per_pixel,
        },
        files={
            "image": image,
        },
    )
    response.raise_for_status()
    return response.json()


def post_process_data(id: str, scale: str, size: str, distribution: dict[str, str]):
    payload = {
        "id": id,
        "scale": scale,
        "size": size,
        "D10": distribution.get("D10", ""),
        "D16": distribution.get("D16", ""),
        "D25": distribution.get("D25", ""),
        "D50": distribution.get("D50", ""),
        "D65": distribution.get("D65", ""),
        "D75": distribution.get("D75", ""),
        "D90": distribution.get("D90", ""),
        "D50mean": distribution.get("D50mean", ""),
    }

    response = requests.post(
        DATABASE_API,
        data=payload,
    )

    response.raise_for_status()
    return response.json()


def run_worker():
    print("[*] Connecting to Azure Storage Queue...")

    if not AZURE_STORAGE_CONNECTION_STRING or not AZURE_QUEUE_NAME:
        print("ERROR: Missing Azure Storage configuration in environment variables.")
        exit(1)

    # Setup Client
    # Note: We use Base64 encoding because some Azure tools expect it by default.
    queue_client = QueueClient.from_connection_string(
        conn_str=AZURE_STORAGE_CONNECTION_STRING,
        queue_name=AZURE_QUEUE_NAME,
    )

    print(f"[*] Watching queue: {AZURE_QUEUE_NAME}")

    while True:
        try:
            # 1. RECEIVE (POLL)
            messages = queue_client.receive_messages(
                messages_per_page=1, visibility_timeout=VISIBILITY_TIMEOUT
            )

            for msg in messages:
                print(f"\n[+] Received Message ID: {msg.id}")

                try:
                    # PARSE CONTENT
                    body = msg.content
                    print(f"    - Message Body: {body}")

                    id, image_url = body.split(",")
                    print(f"    - Processing Image ID: {id}")

                    # DOWNLOAD IMAGE
                    print(f"    - Downloading image from URL: {image_url}")
                    image = requests.get(image_url).content

                    # GET SCALE
                    print("    - Sending image to COIN API for scale detection...")
                    prediction = get_scale(image)
                    print(f"    - {prediction}")

                    # Get grain size
                    print(
                        "    - Sending image to GRAIN API for grain size detection..."
                    )
                    grain_prediction = get_grain_size(
                        image,
                        mm_per_pixel=str(prediction["mm_per_pixel"]),
                        coin_center_x=str(prediction["coin_center_x"]),
                        coin_center_y=str(prediction["coin_center_y"]),
                        coin_radius_px=str(prediction["coin_radius_px"]),
                    )

                    print(f"    - {grain_prediction}")

                    # update database
                    print("    - Posting results to Database API...")
                    db_response = post_process_data(
                        id=id,
                        scale=str(prediction["mm_per_pixel"]),
                        size=str(grain_prediction["size_mm"]),
                        distribution=grain_prediction.get("distribution_mm", {}),
                    )
                    print(f"    - Database response: {db_response}")

                    # DELETE (SUCCESS)
                    print("    - Deleting message from queue...")
                    queue_client.delete_message(msg)
                    print("    - Job Done. Message deleted.")

                except requests.HTTPError as http_e:
                    print(
                        f"    - HTTP ERROR {http_e.response.status_code} processing job: {http_e}"
                    )
                    print(http_e.response.text)

                except Exception as e:
                    print(f"    - ERROR processing job: {e}")
                    print()

            # Sleep briefly if queue was empty to save CPU/Bandwidth
            time.sleep(1)

        except Exception as main_e:
            print(f"CRITICAL WORKER ERROR: {main_e}")
            time.sleep(5)


if __name__ == "__main__":
    run_worker()
