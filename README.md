# Chrome Component Downloader

A Python module and CLI tool to manually download Chrome/Chromium components.

## Features

* Generate update requests for Chromium components.
* Support for Omaha protocol version `3.1`.
* Download latest **and** previous versions of each component.

## Installation

To use this component yourself, you can clone this repo or install it with `pip`:

```shell
pip install chrome-component-downloader
```

## Python Module

The module allows to download Chromium components and generate update requests.

### Example usage

Download component and save as zip file locally:

```py
from chrome_component_downloader import download_component

component_zip, version = download_component(
    component_id = "niikhdgajlphfehepabhhblakbdgeefj", # Privacy Sandbox Attestations
    target_version = "2025.03.31",
    send_system_info = False
)

print(f"Version: {version}")
with open("component.zip", "wb") as out_file:
    out_file.write(component_zip)
```

Generate an update request:

```py
from chrome_component_downloader.update_request import generate as generate_update_request

update_request = generate_update_request(
    component_id = "niikhdgajlphfehepabhhblakbdgeefj", # Privacy Sandbox Attestations
    target_version = "2025.03.31",
    send_system_info = False
)

print(update_request)
```

## CLI Tool

The CLI tool provides a simple way to download a component from the command line.

### Usage

```
usage: chrome-component-downloader [-h] [--target_version TARGET_VERSION] [--output OUTPUT] [--send_system_info] component

positional arguments:
  component             The component's ID or name. The component names can be one of the following: 
                        - autofill_states_data
                        - pki_metadata
                        - subresource_filter_rules
                        - crowd_deny
                        - certificate_error_assistant
                        - related_website_sets
                        - amount_extraction_heuristic_regexes
                        - crlset
                        - hyphenation
                        - third_party_cookie_deprecation_metadata
                        - safety_tips
                        - file_type_policies
                        - trust_token_key_commitments
                        - mei_preload
                        - origin_trials
                        - optimization_hints
                        - cookie_readiness_list
                        - screenai_library
                        - privacy_sandbox_attestations
                        - ondeviceheadsuggest
                        - widevine_content_decryption_module
                        - zxcvbn_data_dictionaries
                        - open_cookie_database

options:
  -h, --help            show this help message and exit
  --target_version TARGET_VERSION
                        The component's target version. It can be a prefix that the version number must match. If no value is specified, the latest version is downloaded.
  --output OUTPUT       The output file name. If no value is specified, the component's ID and version is used as the file name.
  --send_system_info    Send system information to the CUP server.
```

### Example usage

Download a specific component:

```shell
chrome-component-downloader privacy_sandbox_attestations --target_version 2025.03.31
```

### Docker container

The CLI tool can also be used as a Docker container. You can use the `salb98/chrome-component-downloader` pre-compiled image. Here is an example command:

```shell
docker run -v ./output:/app/out:rw salb98/chrome-component-downloader privacy_sandbox_attestations --output /app/out/component.zip
```

This creates and saves the component zip in the `output/` folder in your current working directory.