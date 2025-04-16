import argparse
import re
import os
from .chromium_components import CHROMIUM_COMPONENT_IDS
from . import download_component
from .errors import DownloadFailedException

def validate_id(id: str):
    return bool(re.fullmatch(r"[a-z0-9]{32}", id))

def main():
    parser = argparse.ArgumentParser(description="""
    Chromium Cup Downloader CLI
    This script downloads a Chromium component using the browser's Client Update Protocol (CUP). This component is saved as a ZIP file.
    """,
    formatter_class=argparse.RawTextHelpFormatter
    )
    component_list = "\n".join(f"- {name}" for name in CHROMIUM_COMPONENT_IDS.keys())
    parser.add_argument(
        "component",
        type=str,
        help=f"The component's ID or name. The component names can be one of the following: \n{component_list}"
    )
    parser.add_argument(
        "--target_version",
        type=str,
        default="",
        help="The component's target version. It can be a prefix that the version number must match. If no value is specified, the latest version is downloaded."
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="The output file name. If no value is specified, the component's ID and version is used as the file name."
    )
    parser.add_argument(
        "--send_system_info",
        action="store_true",
        help="Send system information to the CUP server."
    )
    
    args = parser.parse_args()

    # Parse component ID: retrieve from name or use it directly
    component_name = args.component.strip().replace(" ", "_").lower()
    component_id = CHROMIUM_COMPONENT_IDS.get(component_name) or component_name
    if not validate_id(component_id):
        parser.error(f"Invalid component ID: {component_id}. The component ID must be a 32-character alphanumeric string.")

    print("Attempting to download component...")
    try:
        zipfile, downloaded_version = download_component(
            component_id,
            target_version=args.target_version,
            send_system_info=args.send_system_info
        )
        if zipfile is None or downloaded_version is None:
            parser.error(f"Component '{args.component}' (ID: {component_id}) does not have a version that matches '{args.target_version}'.")
    except DownloadFailedException:
        parser.error(f"Failed to download the component '{args.component}' (ID: {component_id}). Please check the component ID or network connection.")

    print("Component downloaded successfully. Saving to file...")
    try:
        filename = args.output or f"{component_id}-{downloaded_version}.zip"
        
        # Create output directory if it doesn't exist
        outdir = os.path.dirname(filename) or "."
        if not os.path.isdir(outdir):
            os.mkdir(outdir)
        
        # Save file
        with open(filename, "wb") as outfile:
            outfile.write(zipfile)
        
        print(f"Saved as '{filename}'.")
    except Exception as e:
        parser.error(f"Failed to save the ZIP file: {e}")

if __name__ == "__main__":
    main()