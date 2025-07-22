import asyncio
import json
import time
from typing import Dict, List, Optional, Any

import httpx

from logger import StructuredLogger
from utils import is_valid_http_method, format_duration


class ApiTester:
    def __init__(self, logger: StructuredLogger, timeout: int = 30):
        self.logger = logger
        self.timeout = timeout
        self.client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    async def test_endpoint(self, url: str, method: str = "GET", 
                          headers: Optional[Dict[str, str]] = None,
                          data: Optional[Dict[str, Any]] = None,
                          json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test a single API endpoint."""
        if not self.client:
            raise RuntimeError("ApiTester must be used as async context manager")
        
        method = method.upper()
        if not is_valid_http_method(method):
            raise ValueError(f"Invalid HTTP method: {method}")
        
        start_time = time.time()
        result = {
            "url": url,
            "method": method,
            "success": False,
            "status_code": None,
            "response_time_ms": None,
            "response_size_bytes": None,
            "error": None,
            "headers": {},
            "response_preview": None
        }
        
        try:
            # Prepare request
            request_kwargs = {
                "method": method,
                "url": url,
                "headers": headers or {}
            }
            
            # Add data if provided
            if json_data:
                request_kwargs["json"] = json_data
            elif data:
                request_kwargs["data"] = data
            
            # Make request
            response = await self.client.request(**request_kwargs)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Update result
            result.update({
                "success": True,
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "response_size_bytes": len(response.content),
                "headers": dict(response.headers)
            })
            
            # Get response preview (first 500 chars)
            try:
                if response.headers.get("content-type", "").startswith("application/json"):
                    response_json = response.json()
                    result["response_preview"] = json.dumps(response_json, indent=2)[:500]
                else:
                    result["response_preview"] = response.text[:500]
            except:
                result["response_preview"] = str(response.content)[:500]
            
            # Log the result
            self.logger.log_api_event(
                method=method,
                url=url,
                status_code=response.status_code,
                response_time=response_time,
                error=None
            )
            
            # Log success or warning based on status code
            if 200 <= response.status_code < 300:
                self.logger.log_success(
                    f"{method} {url} -> {response.status_code} ({format_duration(response_time/1000)})"
                )
            elif 400 <= response.status_code < 500:
                self.logger.log_warning(
                    f"{method} {url} -> {response.status_code} Client Error ({format_duration(response_time/1000)})"
                )
            elif response.status_code >= 500:
                self.logger.log_error(
                    f"{method} {url} -> {response.status_code} Server Error ({format_duration(response_time/1000)})"
                )
        
        except httpx.TimeoutException:
            response_time = (time.time() - start_time) * 1000
            error_msg = f"Request timeout after {self.timeout}s"
            result.update({
                "error": error_msg,
                "response_time_ms": round(response_time, 2)
            })
            self.logger.log_api_event(method, url, None, response_time, error_msg)
            self.logger.log_error(f"{method} {url} -> Timeout", None)
        
        except httpx.ConnectError as e:
            response_time = (time.time() - start_time) * 1000
            error_msg = f"Connection error: {str(e)}"
            result.update({
                "error": error_msg,
                "response_time_ms": round(response_time, 2)
            })
            self.logger.log_api_event(method, url, None, response_time, error_msg)
            self.logger.log_error(f"{method} {url} -> Connection failed", e)
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            error_msg = f"Unexpected error: {str(e)}"
            result.update({
                "error": error_msg,
                "response_time_ms": round(response_time, 2)
            })
            self.logger.log_api_event(method, url, None, response_time, error_msg)
            self.logger.log_error(f"{method} {url} -> Unexpected error", e)
        
        return result
    
    async def test_multiple_endpoints(self, endpoints: List[str], method: str = "GET") -> List[Dict[str, Any]]:
        """Test multiple endpoints concurrently."""
        if not endpoints:
            return []
        
        self.logger.log_event("api_test_batch", {
            "endpoint_count": len(endpoints),
            "method": method,
            "message": f"Starting batch test of {len(endpoints)} endpoints"
        })
        
        # Create tasks for concurrent execution
        tasks = []
        for endpoint in endpoints:
            task = self.test_endpoint(endpoint, method)
            tasks.append(task)
        
        # Execute all tests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        success_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle task exception
                error_result = {
                    "url": endpoints[i],
                    "method": method,
                    "success": False,
                    "error": f"Task failed: {str(result)}",
                    "status_code": None,
                    "response_time_ms": None
                }
                processed_results.append(error_result)
                self.logger.log_error(f"Task failed for {endpoints[i]}", result)
            else:
                processed_results.append(result)
                if result["success"] and result.get("status_code", 0) < 400:
                    success_count += 1
        
        # Log batch summary
        self.logger.log_event("api_test_batch_complete", {
            "total_endpoints": len(endpoints),
            "successful": success_count,
            "failed": len(endpoints) - success_count,
            "success_rate": f"{(success_count / len(endpoints)) * 100:.1f}%",
            "message": f"Batch test completed: {success_count}/{len(endpoints)} successful"
        })
        
        return processed_results
    
    async def test_endpoint_with_retry(self, url: str, method: str = "GET", 
                                     max_retries: int = 3, 
                                     retry_delay: float = 1.0) -> Dict[str, Any]:
        """Test endpoint with retry logic."""
        last_result = None
        
        for attempt in range(max_retries + 1):
            if attempt > 0:
                self.logger.log_event("api_retry", {
                    "url": url,
                    "attempt": attempt + 1,
                    "max_retries": max_retries,
                    "message": f"Retrying {url} (attempt {attempt + 1}/{max_retries + 1})"
                })
                await asyncio.sleep(retry_delay)
            
            result = await self.test_endpoint(url, method)
            last_result = result
            
            # Success conditions
            if result["success"] and result.get("status_code", 0) < 500:
                if attempt > 0:
                    self.logger.log_success(f"Retry successful for {url} on attempt {attempt + 1}")
                return result
        
        # All retries failed
        if last_result:
            last_result["retry_attempts"] = max_retries + 1
            self.logger.log_error(f"All retry attempts failed for {url}")
        
        return last_result or {
            "url": url,
            "method": method,
            "success": False,
            "error": "All retry attempts failed",
            "retry_attempts": max_retries + 1
        }