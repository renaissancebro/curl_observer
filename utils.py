import os
import time
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urljoin, urlparse


def validate_url(url: str) -> str:
    """Validate and normalize URL."""
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    
    return url


def parse_endpoints(endpoints_str: str, base_url: str) -> List[str]:
    """Parse comma-separated endpoints and convert to full URLs."""
    if not endpoints_str:
        return []
    
    endpoints = [ep.strip() for ep in endpoints_str.split(',')]
    full_urls = []
    
    for endpoint in endpoints:
        if endpoint.startswith(('http://', 'https://')):
            full_urls.append(endpoint)
        else:
            # Ensure endpoint starts with /
            if not endpoint.startswith('/'):
                endpoint = f"/{endpoint}"
            full_urls.append(urljoin(base_url, endpoint))
    
    return full_urls


def get_default_log_file() -> str:
    """Generate default log file path."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return f"play_curl_session_{timestamp}.log"


def ensure_directory(file_path: str) -> None:
    """Ensure parent directory exists for given file path."""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


def sanitize_selector(selector: str) -> str:
    """Basic sanitization of CSS selector."""
    if not selector:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", ';', '&', '|']
    for char in dangerous_chars:
        selector = selector.replace(char, '')
    
    return selector.strip()


def is_valid_http_method(method: str) -> bool:
    """Check if HTTP method is valid."""
    valid_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'}
    return method.upper() in valid_methods


def get_browser_executable_path() -> Optional[str]:
    """Try to find browser executable path for different platforms."""
    # This is optional - Playwright will download its own browsers if needed
    common_paths = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser", 
        "/usr/bin/google-chrome",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None