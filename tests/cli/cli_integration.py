from unittest.mock import patch
from chrome_component_downloader.__main__ import main

def test_cli_download_component(capsys):
    with patch("chrome_component_downloader.download_component") as mock_download:
        mock_download.return_value = (b"zipcontent", "2025.03.31.0")
        
        args = [
            "privacy_sandbox_attestations",
            "--target_version", "2025.03.31",
            "--output", "downloads/test.zip"
        ]
        with patch("sys.argv", ["__main__.py"] + args):
            main()
        
        captured = capsys.readouterr()
        assert "Component downloaded successfully" in captured.out