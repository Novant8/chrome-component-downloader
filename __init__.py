import random
import base64
import hashlib
import json
import io
import requests
from zipfile import ZipFile
from .errors import DownloadFailedException, NotCrx3FileException, InvalidComponentException
from . import update_request

GOOGLE_UPDATE_URL = "https://update.googleapis.com/service/update2/json"
KEY_AMOUNT = 13
CUP_NONCE_LENGTH = 32

def _get_url(req_body_str: str) -> str:
    key_number = random.randint(1, KEY_AMOUNT)
    nonce_b64 = base64.urlsafe_b64encode(random.randbytes(CUP_NONCE_LENGTH)).decode()
    req_hash = hashlib.sha256(req_body_str.encode()).hexdigest()

    return f"{GOOGLE_UPDATE_URL}?cup2key={key_number}:{nonce_b64}&cup2hreq={req_hash}"

def _get_headers(req: dict) -> dict:
    return {
        "x-goog-update-appid": req["request"]["app"][0]["appid"],
        "x-goog-update-interactivity": "fg",
        "x-goog-update-updater": f"{req["request"]['@updater']}-{req["request"]['prodversion']}",
        # "user-agent": USER_AGENT,
        "content-type": "application/json",
    }

def _request_update_urls(component_id: str, target_version = "", send_system_info = False) -> list[str] | None:
    req = update_request.generate(component_id, target_version, send_system_info)
    req_str = json.dumps(req)

    try:
        res = requests.post(_get_url(req_str), headers=_get_headers(req), data=req_str)
    except requests.RequestException as e:
        return None
    
    res_str = res.text.lstrip(")]}'\n")
    res_json = json.loads(res_str)

    app = res_json.get("response", {}).get("app", [None])[0]
    if app is None:
        return None
    
    app_updatecheck = app.get("updatecheck")

    if app_updatecheck is None or app_updatecheck["status"] != "ok":
        return None

    manifest = app_updatecheck.get("manifest")
    if manifest is None:
        return None

    urls = app_updatecheck.get("urls", {}).get("url", [])
    name = manifest.get("packages", {}).get("package", [{}])[0].get("name")

    return [ url["codebase"] + name for url in urls ]

def _get_crx3_contents(crx3: bytes) -> tuple[bytes, bytes]:
    if not crx3.startswith(b"Cr24"):
        raise NotCrx3FileException()

    version = int.from_bytes(crx3[4:8], byteorder="little")
    if version != 3:
        raise NotCrx3FileException()

    header_length = int.from_bytes(crx3[8:12], byteorder="little")

    return crx3[12:12+header_length], crx3[12+header_length:]

def _verify_header(header: bytes) -> bool:
    """
    TODO: Implement header verification
    """
    return True

def _attempt_download(url: str) -> bytes:
    res = requests.get(url)
    if res.status_code != 200:
        raise DownloadFailedException()
    
    header, content = _get_crx3_contents(res.content)
    if not _verify_header(header):
        raise InvalidComponentException()
    
    return content

def download_chromium_component(component_id: str, target_version = "", send_system_info = False) -> ZipFile:
    urls = _request_update_urls(component_id, target_version, send_system_info)
    if urls is None:
        raise DownloadFailedException()

    for url in urls:
        try:
            zip_bytes = _attempt_download(url)
            return ZipFile(io.BytesIO(zip_bytes), mode="r")
        except DownloadFailedException:
            continue
    raise DownloadFailedException()