import pytest
from unittest.mock import patch, MagicMock
from chrome_component_downloader import download_component
from chrome_component_downloader.errors import DownloadFailedException

@pytest.fixture
def mock_requests_post():
    with patch("chrome_component_downloader.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        )]}'
        {
            "response": {
                "app": [
                    {
                        "updatecheck": {
                            "status": "ok",
                            "urls": {
                                "url": [
                                    {"codebase": "http://example.com/"}
                                ]
                            },
                            "manifest": {
                                "version": "2025.03.31.0",
                                "packages": {
                                    "package": [
                                        {"name": "component.crx3"}
                                    ]
                                }
                            }
                        }
                    }
                ]
            }
        }
        """
        mock_post.return_value = mock_response
        yield mock_post

@pytest.fixture
def mock_requests_get():
    with patch("chrome_component_downloader.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"Cr24\x03\x00\x00\x00\x0D\x00\x00\x00headercontentzipcontent"
        mock_get.return_value = mock_response
        yield mock_get

def test_download_component_success(mock_requests_post, mock_requests_get):
    component_id = "niikhdgajlphfehepabhhblakbdgeefj"
    target_version = "2025.03.31"
    zip_bytes, version = download_component(component_id, target_version)

    assert zip_bytes == b"zipcontent"
    assert version == "2025.03.31.0"

def test_download_component_with_system_info_success(mock_requests_post, mock_requests_get):
    component_id = "niikhdgajlphfehepabhhblakbdgeefj"
    target_version = "2025.03.31"
    zip_bytes, version = download_component(component_id, target_version, send_system_info=True)

    assert zip_bytes == b"zipcontent"
    assert version == "2025.03.31.0"

def test_download_component_failure(mock_requests_post):
    mock_requests_post.return_value.status_code = 500

    with pytest.raises(DownloadFailedException):
        download_component("invalid_component_id")