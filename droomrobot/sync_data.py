from datetime import datetime
from os import environ
from pathlib import Path
import sys

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.webdav_sync import WebDAVSync

if __name__ == '__main__':
    load_dotenv(PROJECT_ROOT / 'conf' / '.env')
    client = WebDAVSync(base_url=environ["WEBDAV_BASE_URL"],
                        username=environ["WEBDAV_USERNAME"],
                        password=environ["WEBDAV_PASSWORD"])

    client.sync_once(local_folder=str(PACKAGE_ROOT / 'user_models'),
                     remote_folder=environ["WEBDAV_USER_MODELS_URL"])
    client.sync_once(local_folder=str(PACKAGE_ROOT / 'tts_cache'),
                     remote_folder=environ["WEBDAV_TTS_CACHE_URL"])

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    client.upload_folder(local_folder=str(PACKAGE_ROOT / 'logs'),
                         remote_folder=f'{environ["WEBDAV_INTERACTION_LOGS_URL"]}/{timestamp}')
