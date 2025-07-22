import asyncio
import time
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page

from logger import StructuredLogger
from utils import sanitize_selector, get_browser_executable_path


class BrowserDebugger:
    def __init__(self, logger: StructuredLogger, headless: bool = True, keep_open: bool = False):
        self.logger = logger
        self.headless = headless
        self.keep_open = keep_open
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
    
    async def launch(self) -> None:
        """Launch browser instance."""
        try:
            self.playwright = await async_playwright().start()
            
            # Try to find system browser, fallback to Playwright's bundled browser
            executable_path = get_browser_executable_path()
            
            launch_options = {
                "headless": self.headless,
                "args": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu"
                ]
            }
            
            if executable_path:
                launch_options["executable_path"] = executable_path
            
            self.browser = await self.playwright.chromium.launch(**launch_options)
            self.page = await self.browser.new_page()
            
            # Set reasonable viewport
            await self.page.set_viewport_size({"width": 1280, "height": 720})
            
            self.logger.log_browser_event("launch", {
                "headless": self.headless,
                "executable_path": executable_path,
                "message": "Browser launched successfully"
            })
        
        except Exception as e:
            self.logger.log_error("Failed to launch browser", e)
            raise
    
    async def navigate_to_url(self, url: str, wait_timeout: int = 30000) -> None:
        """Navigate to URL and wait for page load."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        
        start_time = time.time()
        
        try:
            # Navigate to URL
            response = await self.page.goto(url, wait_until="networkidle", timeout=wait_timeout)
            load_time = time.time() - start_time
            
            if response:
                status = response.status
                self.logger.log_browser_event("navigate", {
                    "url": url,
                    "status_code": status,
                    "load_time_seconds": round(load_time, 2),
                    "message": f"Navigation completed with status {status}"
                })
                
                # Log page title
                title = await self.page.title()
                if title:
                    self.logger.log_browser_event("page_info", {
                        "title": title,
                        "url": url,
                        "message": f"Page title: {title}"
                    })
            else:
                self.logger.log_warning("Navigation completed but no response received")
        
        except Exception as e:
            self.logger.log_error(f"Failed to navigate to {url}", e)
            raise
    
    async def wait_for_element(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for element to appear on page."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        
        selector = sanitize_selector(selector)
        if not selector:
            self.logger.log_warning("Empty or invalid selector provided")
            return False
        
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            self.logger.log_browser_event("wait_element", {
                "selector": selector,
                "found": True,
                "message": f"Element '{selector}' found"
            })
            return True
        
        except Exception as e:
            self.logger.log_browser_event("wait_element", {
                "selector": selector,
                "found": False,
                "error": str(e),
                "message": f"Element '{selector}' not found"
            })
            return False
    
    async def click_element(self, selector: str) -> bool:
        """Click on element if it exists."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        
        selector = sanitize_selector(selector)
        if not selector:
            self.logger.log_warning("Empty or invalid selector provided")
            return False
        
        try:
            # Wait for element to be clickable
            await self.page.wait_for_selector(selector, timeout=5000)
            await self.page.click(selector)
            
            self.logger.log_browser_event("click", {
                "selector": selector,
                "success": True,
                "message": f"Clicked element '{selector}'"
            })
            
            # Brief wait after click
            await self.page.wait_for_timeout(1000)
            return True
        
        except Exception as e:
            self.logger.log_browser_event("click", {
                "selector": selector,
                "success": False,
                "error": str(e),
                "message": f"Failed to click element '{selector}'"
            })
            return False
    
    async def take_screenshot(self, file_path: str) -> bool:
        """Take screenshot of current page."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            await self.page.screenshot(path=file_path, full_page=True)
            
            self.logger.log_browser_event("screenshot", {
                "file_path": file_path,
                "success": True,
                "message": f"Screenshot saved to {file_path}"
            })
            return True
        
        except Exception as e:
            self.logger.log_error(f"Failed to take screenshot", e)
            return False
    
    async def start_screen_recording(self, video_path: str) -> bool:
        """Start screen recording (if supported)."""
        if not self.page:
            raise RuntimeError("Browser not launched")
        
        try:
            # Note: Video recording needs to be configured at browser context level
            # This is a simplified implementation - full video recording would require
            # context setup at browser launch
            self.logger.log_browser_event("recording", {
                "action": "start",
                "video_path": video_path,
                "message": "Screen recording not fully implemented - would need browser context setup"
            })
            return False
        
        except Exception as e:
            self.logger.log_error("Failed to start screen recording", e)
            return False
    
    async def get_page_metrics(self) -> dict:
        """Get basic page performance metrics."""
        if not self.page:
            return {}
        
        try:
            # Get basic page info
            title = await self.page.title()
            url = self.page.url
            
            # Try to get performance metrics
            metrics = await self.page.evaluate("""
                () => {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    return navigation ? {
                        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                        domElements: document.getElementsByTagName('*').length
                    } : {};
                }
            """)
            
            result = {
                "title": title,
                "url": url,
                "metrics": metrics
            }
            
            self.logger.log_browser_event("metrics", {
                "data": result,
                "message": "Page metrics collected"
            })
            
            return result
        
        except Exception as e:
            self.logger.log_error("Failed to get page metrics", e)
            return {}
    
    async def close(self) -> None:
        """Close browser and cleanup."""
        try:
            if self.browser:
                await self.browser.close()
                self.logger.log_browser_event("close", {
                    "message": "Browser closed successfully"
                })
            
            if self.playwright:
                await self.playwright.stop()
        
        except Exception as e:
            self.logger.log_error("Error during browser cleanup", e)