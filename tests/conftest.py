import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

# Create temporary directories for static files
temp_dir = tempfile.mkdtemp()
temp_static = Path(temp_dir) / "static"
temp_assets = Path(temp_dir) / "assets"
temp_static.mkdir(exist_ok=True)
temp_assets.mkdir(exist_ok=True)

# Mock GCP secret reading before ANY imports that might use it
mock_auth_secret = json.dumps({
    "client-id": "test-client-id",
    "client-secret": "test-client-secret",
    "secret-key": "test-secret-key"
})

# Patch before importing anything that triggers the secret read
with patch("google.cloud.secretmanager.SecretManagerServiceClient") as mock_client_class:
    mock_instance = MagicMock()
    mock_client_class.return_value = mock_instance
    
    # Mock the response structure
    mock_response = MagicMock()
    mock_response.payload.data = mock_auth_secret.encode("UTF-8")
    mock_response.payload.data_crc32c = 0
    mock_instance.access_secret_version.return_value = mock_response
    
    # Also patch google_crc32c to avoid checksum validation
    with patch("google_crc32c.Checksum") as mock_crc:
        mock_crc_instance = MagicMock()
        mock_crc_instance.hexdigest.return_value = "0"
        mock_crc.return_value = mock_crc_instance
        
        # Import config and patch the settings instance before app import
        from photo_album.config import settings
        settings.STATIC_DIR = temp_static
        settings.PHOTOS_DIR = temp_assets
        
        from main import app


@pytest.fixture()
def client():
    with TestClient(app) as client:
        yield client
