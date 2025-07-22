#!/usr/bin/env python3

import argparse
import asyncio
import sys
import time
from pathlib import Path

from browser_debugger import BrowserDebugger
from api_tester import ApiTester
from logger import StructuredLogger
from utils import validate_url, parse_endpoints, get_default_log_file, format_duration


async def main():
    parser = argparse.ArgumentParser(
        description="Playwright + curl-style HTTP testing tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url https://example.com
  %(prog)s --url https://example.com --test-endpoints /api/users,/api/posts
  %(prog)s --url https://api.github.com --test-endpoints /users/octocat --verbose
  %(prog)s --url https://example.com --click-selector "button.login" --record
        """
    )
    
    parser.add_argument("--url", required=True, help="URL to launch in Playwright")
    parser.add_argument("--test-endpoints", 
                       help="Comma-separated list of API endpoints to test (e.g., /api/foo,/api/bar)")
    parser.add_argument("--click-selector", 
                       help="CSS selector to click after page load (optional)")
    parser.add_argument("--wait-selector",
                       help="CSS selector to wait for before continuing (optional)")
    parser.add_argument("--record", action="store_true", 
                       help="Record screen session (experimental)")
    parser.add_argument("--screenshot", 
                       help="Take screenshot and save to specified path")
    parser.add_argument("--headless", action="store_true", default=True,
                       help="Run browser in headless mode (default)")
    parser.add_argument("--headed", action="store_true", 
                       help="Run browser in headed mode (visible)")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose output")
    parser.add_argument("--log-file", 
                       help="Path to write structured log file (default: auto-generated)")
    parser.add_argument("--timeout", type=int, default=30,
                       help="Request timeout in seconds (default: 30)")
    parser.add_argument("--method", default="GET",
                       help="HTTP method for API testing (default: GET)")
    parser.add_argument("--retry", type=int, default=0,
                       help="Number of retry attempts for API requests (default: 0)")
    parser.add_argument("--keep-open", action="store_true", 
                       help="Keep browser open after completion (requires --headed)")
    
    args = parser.parse_args()
    
    # Validate arguments
    try:
        validated_url = validate_url(args.url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Handle headless/headed mode
    headless = args.headless and not args.headed
    
    # Validate keep-open requires headed mode
    if args.keep_open and headless:
        print("Error: --keep-open requires --headed mode", file=sys.stderr)
        sys.exit(1)
    
    # Setup logging
    log_file = args.log_file or get_default_log_file()
    logger = StructuredLogger(log_file=log_file, verbose=args.verbose)
    
    # Parse endpoints
    endpoints = parse_endpoints(args.test_endpoints or "", validated_url)
    
    # Log session start
    logger.log_event("session_start", {
        "url": validated_url,
        "endpoints": endpoints,
        "headless": headless,
        "log_file": log_file,
        "message": "Starting play_curl session"
    })
    
    start_time = time.time()
    browser_debugger = None
    
    try:
        # Initialize browser
        browser_debugger = BrowserDebugger(logger, headless=headless)
        await browser_debugger.launch()
        
        # Navigate to URL
        logger.log_event("phase", {"name": "browser_navigation", "message": "Starting browser navigation"})
        await browser_debugger.navigate_to_url(validated_url)
        
        # Wait for specific selector if provided
        if args.wait_selector:
            logger.log_event("phase", {"name": "wait_selector", "message": f"Waiting for selector: {args.wait_selector}"})
            await browser_debugger.wait_for_element(args.wait_selector, timeout=10000)
        
        # Click element if selector provided
        if args.click_selector:
            logger.log_event("phase", {"name": "click_element", "message": f"Clicking selector: {args.click_selector}"})
            await browser_debugger.click_element(args.click_selector)
        
        # Take screenshot if requested
        if args.screenshot:
            logger.log_event("phase", {"name": "screenshot", "message": f"Taking screenshot: {args.screenshot}"})
            await browser_debugger.take_screenshot(args.screenshot)
        
        # Start recording if requested (experimental)
        if args.record:
            logger.log_event("phase", {"name": "recording", "message": "Screen recording requested (experimental)"})
            video_path = f"play_curl_recording_{int(time.time())}.webm"
            await browser_debugger.start_screen_recording(video_path)
        
        # Get page metrics
        metrics = await browser_debugger.get_page_metrics()
        
        # Test API endpoints if provided
        if endpoints:
            logger.log_event("phase", {"name": "api_testing", "message": f"Testing {len(endpoints)} API endpoints"})
            
            async with ApiTester(logger, timeout=args.timeout) as api_tester:
                if args.retry > 0:
                    # Test with retry
                    results = []
                    for endpoint in endpoints:
                        result = await api_tester.test_endpoint_with_retry(
                            endpoint, args.method.upper(), max_retries=args.retry
                        )
                        results.append(result)
                else:
                    # Test all endpoints concurrently
                    results = await api_tester.test_multiple_endpoints(endpoints, args.method.upper())
                
                # Summary of API results
                success_count = sum(1 for r in results if r.get("success") and r.get("status_code", 0) < 400)
                logger.log_event("api_summary", {
                    "total_endpoints": len(endpoints),
                    "successful": success_count,
                    "failed": len(endpoints) - success_count,
                    "results": results,
                    "message": f"API testing completed: {success_count}/{len(endpoints)} successful"
                })
        
        # Session completed successfully
        total_time = time.time() - start_time
        logger.log_success(f"Session completed successfully in {format_duration(total_time)}")
        
        # Print summary to console
        print(f"\n=== Play Curl Session Summary ===")
        print(f"URL: {validated_url}")
        print(f"Total time: {format_duration(total_time)}")
        
        if metrics.get("title"):
            print(f"Page title: {metrics['title']}")
        
        if endpoints:
            print(f"API endpoints tested: {len(endpoints)}")
            if 'results' in locals():
                success_count = sum(1 for r in results if r.get("success") and r.get("status_code", 0) < 400)
                print(f"API success rate: {success_count}/{len(endpoints)} ({(success_count/len(endpoints)*100):.1f}%)")
        
        print(f"Log file: {log_file}")
        print("=== End Summary ===\n")
    
    except KeyboardInterrupt:
        logger.log_warning("Session interrupted by user")
        print("\nSession interrupted by user", file=sys.stderr)
        sys.exit(130)
    
    except Exception as e:
        logger.log_error("Session failed with unexpected error", e)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    finally:
        # Cleanup
        if browser_debugger:
            await browser_debugger.close()
        
        logger.finalize_session()


def run():
    """Entry point for the CLI tool."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    run()