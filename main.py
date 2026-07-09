import sys
import time
from datetime import datetime
from typing import Dict, List, Any
import urllib.request
import urllib.error

# Global configuration configuration
DEFAULT_TIMEOUT: int = 5

def check_url_health(url: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Pings a given URL and returns its connectivity metrics and status.
    """
    status_report = {
        "url": url,
        "status": "Unknown",
        "code": None,
        "response_time_ms": 0,
        "error_message": None
    }
    
    start_time = time.time()
    
    try:
        # Create a request object with a realistic User-Agent header
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'WebsiteHealthChecker/1.0'}
        )
        
        # Open the connection and read the response code
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_report["code"] = response.getcode()
            status_report["status"] = "Healthy" if 200 <= response.getcode() < 300 else "Unhealthy"
            
    except urllib.error.HTTPError as e:
        # The server responded, but with an error status (e.g., 404, 500)
        status_report["code"] = e.code
        status_report["status"] = "Unhealthy"
        status_report["error_message"] = f"HTTP Error: {e.reason}"
        
    except urllib.error.URLError as e:
        # Failed to reach the server entirely (e.g., DNS failure, connection refused)
        status_report["status"] = "Down"
        status_report["error_message"] = f"Network Error: {e.reason}"
        
    except Exception as e:
        # Catch-all for unexpected runtimes (e.g., system-level timeouts)
        status_report["status"] = "Error"
        status_report["error_message"] = str(e)
        
    finally:
        # Compute exact response latency elapsed during the check
        elapsed = time.time() - start_time
        status_report["response_time_ms"] = round(elapsed * 1000, 2)
        
    return status_report

def load_urls_from_file(file_path: str) -> List[str]:
    """
    Reads a text file line-by-line, sanitizes whitespace, 
    and returns a clean list of target URLs to check.
    """
    urls: List[str] = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                # Strip leading/trailing whitespaces and newlines
                sanitized_line = line.strip()
                
                # Skip empty lines or comment lines (starting with '#')
                if not sanitized_line or sanitized_line.startswith("#"):
                    continue
                
                urls.append(sanitized_line)
                
    except FileNotFoundError:
        print(f"Error: The target file '{file_path}' was not found.")
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        
    return urls