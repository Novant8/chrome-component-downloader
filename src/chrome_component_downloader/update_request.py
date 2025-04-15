from uuid import uuid4
import platform
import psutil
import ctypes
import subprocess
import sys

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
OMAHA_VERSION = "1.3.36.261"
CUP_PROTOCOL_VERSION = "3.1"

def _get_os() -> str:
    os_name = platform.system()
    if os_name == "Linux":
        return "linux"
    elif os_name == "Windows":
        return "win"
    elif os_name == "Darwin":
        return "mac"
    else:
        raise ValueError(f"Unsupported operating system: {os_name}")

def _get_physmemory() -> int:
    """
    Returns the physical memory of the system in GB.
    :return: The physical memory of the system in GB.
    """
    try:
        if platform.system() == "Linux":
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal" in line:
                        mem = int(line.split()[1]) / 1024 / 1024
                        return int(mem)
        elif platform.system() == "Windows":
            return int(psutil.virtual_memory().total / (1024 ** 3))
        elif platform.system() == "Darwin":
            result = subprocess.run(
                ["sysctl", "hw.memsize"],
                capture_output=True,
                text=True,
                check=True
            )
            mem_bytes = int(result.stdout.split(":")[1].strip())
            return int(mem_bytes / (1024 ** 3))
        else:
            raise ValueError("Unsupported operating system")
    except:
        print("Warning: Failed to retrieve physical memory. Using default value (8GB)", file=sys.stderr)
        return 8

def _get_support_flags() -> dict:
    """
    Returns a dictionary with the CPU instruction sets supported by the system.
    :return: A dictionary with the CPU instruction sets supported by the system.
    """
    FLAGS = [ "avx", "avx2", "sse", "sse2", "sse3", "sse4_1", "sse4_2", "ssse3" ]
    sse_support = { flag: False for flag in FLAGS }
    try:
        if platform.system() == "Linux":
            with open("/proc/cpuinfo", "r") as f:
                supported_flags = []
                for line in f:
                    if line.startswith("flags"):
                        supported_flags = line.split(":")[1].strip().split(" ")
                        break
                for flag in FLAGS:
                    if flag in supported_flags:
                        sse_support[flag] = True
        elif platform.system() == "Windows":
            kernel32 = ctypes.windll.kernel32
            sys_info = kernel32.GetSystemInfo()
            if sys_info.dwProcessorType == 586:
                for flag in FLAGS:
                    if flag in sys_info.dwProcessorType:
                        sse_support[flag] = True
        elif platform.system() == "Darwin":
            result = subprocess.run(
                ["sysctl", "machdep.cpu.features"],
                capture_output=True,
                text=True,
                check=True
            )
            supported_flags = result.stdout.split(":")[1].strip().split(" ")
            for flag in FLAGS:
                if flag.upper() in supported_flags:
                    sse_support[flag] = True
        else:
            raise ValueError("Unsupported operating system")
    except:
        print("Warning: Failed to retrieve CPU flags. Assuming none are active.", file=sys.stderr)

    return sse_support

def generate(component_id: str, target_version = "", send_system_info = False) -> dict:
    req_system_info = {}
    if send_system_info:
        req_system_info = {
            "arch": platform.machine(),
            "hw": {
                "physmemory": _get_physmemory(),
                **_get_support_flags()
            },
            "nacl_arch": platform.machine().replace("_", "-"),
            "os": {
                "arch": platform.machine(),
                "platform": _get_os(),
                "version": platform.version()
            },
        }

    return {
        "request": {
            "@os": _get_os(),
            "@updater": "omaha",
            "acceptformat": "crx3",
            "app": [
                {
                    "appid": component_id,
                    "enabled": True,
                    "installsource": "ondemand",
                    "lang": "en-US",
                    # "ping": {
                    #     "r": -2
                    # },
                    "updatecheck": {
                        "targetversionprefix": target_version # Select only versions from given date
                    },
                    "version": "0.0.0.0"
                }
            ],
            "dedup": "cr",
            "ismachine": False,
            "prodversion": OMAHA_VERSION,
            "protocol": CUP_PROTOCOL_VERSION,
            "requestid": f"{uuid4()}",
            "sessionid": f"{uuid4()}",
            "updaterversion": OMAHA_VERSION,
            **req_system_info
        }
    }