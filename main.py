import sys
import time
from datetime import datetime
from typing import Dict, List, Any
import urllib.request
import urllib.error
import argparse

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

def run_health_checker(urls: List[str]) -> Dict[str, Any]:
    """
    Coordinates the execution engine across a collection of URLs, 
    aggregating individual reports and general suite telemetry.
    """
    results: List[Dict[str, Any]] = []
    summary = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_checked": 0,
        "healthy_count": 0,
        "unhealthy_count": 0,
        "down_count": 0,
        "error_count": 0
    }
    
    if not urls:
        return {"summary": summary, "detail_reports": results}
        
    for url in urls:
        # Run our network checking step against the URL
        report = check_url_health(url)
        results.append(report)
        
        # Track metric categories based on status result
        status = report["status"]
        if status == "Healthy":
            summary["healthy_count"] += 1
        elif status == "Unhealthy":
            summary["unhealthy_count"] += 1
        elif status == "Down":
            summary["down_count"] += 1
        else:
            summary["error_count"] += 1
            
    summary["total_checked"] = len(urls)
    
    return {
        "summary": summary,
        "detail_reports": results
    }

def display_health_report(report_data: Dict[str, Any]) -> None:
    """
    Renders the aggregated health check telemetry and detail logs cleanly to stdout.
    """
    summary = report_data["summary"]
    detail_reports = report_data["detail_reports"]
    
    print("\n" + "=" * 50)
    print(f" WEBSITE HEALTH REPORT - {summary['timestamp']}")
    print("=" * 50)
    
    # Render detailed records line by line
    print("\n[DETAILED STATUS]")
    for report in detail_reports:
        code_str = f" (HTTP {report['code']})" if report['code'] is not None else ""
        error_str = f" -> {report['error_message']}" if report['error_message'] else ""
        
        print(f"- {report['url']}: [{report['status']}]"
              f"{code_str} | Latency: {report['response_time_ms']}ms{error_str}")
        
    # Render summary telemetry metrics dashboard
    print("\n" + "-" * 50)
    print("[METRICS SUMMARY]")
    print(f"Total Domains Audited : {summary['total_checked']}")
    print(f" Healthy Status     : {summary['healthy_count']}")
    print(f" Unhealthy Status   : {summary['unhealthy_count']}")
    print(f" Down / Unreachable : {summary['down_count']}")
    print(f" Internal Errors    : {summary['error_count']}")
    print("=" * 50 + "\n")

def main() -> None:
    """
    Main application entry point. Coordinates the loading, execution,
    and presentation phases of the Website Health Checker.
    """
    # Define the input target file
    target_file = "websites.txt"
    
    print(f"Initializing health check routine against data source: '{target_file}'...")
    
    # 1. Ingestion Phase
    urls = load_urls_from_file(target_file)
    
    if not urls:
        print(f"Aborting execution: No active URLs found to verify in '{target_file}'.")
        sys.exit(0)
        
    print(f"Loaded {len(urls)} target domains. Beginning verification suite...")
    
    # 2. Processing Phase
    report_data = run_health_checker(urls)
    
    # 3. Presentation Phase
    display_health_report(report_data)

if __name__ == "__main__":
    main()

def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line inputs to dynamically configure execution contexts.
    """
    parser = argparse.ArgumentParser(
        description="Production-grade, modular Website Health Checker utility."
    )
    
    parser.add_str_arg = parser.add_argument(
        "-f", "--file",
        type=str,
        default="websites.txt",
        help="Path to the target text file containing web addresses (default: websites.txt)"
    )
    
    return parser.parse_args()

def main() -> None:
    """
    Main application entry point. Coordinates the loading, execution,
    and presentation phases using runtime configurations.
    """
    # 0. Configuration Phase
    args = parse_arguments()
    target_file = args.file
    
    print(f"Initializing health check routine against data source: '{target_file}'...")
    
    # 1. Ingestion Phase
    urls = load_urls_from_file(target_file)
    
    if not urls:
        print(f"Aborting execution: No active URLs found to verify in '{target_file}'.")
        sys.exit(0)
        
    print(f"Loaded {len(urls)} target domains. Beginning verification suite...")
    
    # 2. Processing Phase
    report_data = run_health_checker(urls)
    
    # 3. Presentation Phase
    display_health_report(report_data)

if __name__ == "__main__":
    main()