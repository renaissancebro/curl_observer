import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class StructuredLogger:
    def __init__(self, log_file: Optional[str] = None, verbose: bool = False):
        self.verbose = verbose
        self.log_file = log_file
        self.session_data = {
            "session_start": datetime.now().isoformat(),
            "events": []
        }
        
        # Setup console logger
        self.console_logger = logging.getLogger("play_curl")
        self.console_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        
        if not self.console_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.console_logger.addHandler(handler)
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        self.session_data["events"].append(event)
        
        # Console output
        if self.verbose or event_type in ["error", "success", "warning"]:
            level = getattr(logging, data.get("level", "INFO").upper(), logging.INFO)
            message = data.get("message", json.dumps(data))
            self.console_logger.log(level, f"[{event_type}] {message}")
    
    def log_browser_event(self, action: str, details: Dict[str, Any]) -> None:
        self.log_event("browser", {"action": action, **details})
    
    def log_api_event(self, method: str, url: str, status_code: Optional[int] = None, 
                     response_time: Optional[float] = None, error: Optional[str] = None) -> None:
        data = {
            "method": method,
            "url": url,
            "status_code": status_code,
            "response_time_ms": response_time,
            "error": error
        }
        self.log_event("api", data)
    
    def log_error(self, message: str, error: Exception = None) -> None:
        data = {"message": message, "level": "ERROR"}
        if error:
            data["error_type"] = type(error).__name__
            data["error_details"] = str(error)
        self.log_event("error", data)
    
    def log_success(self, message: str) -> None:
        self.log_event("success", {"message": message, "level": "INFO"})
    
    def log_warning(self, message: str) -> None:
        self.log_event("warning", {"message": message, "level": "WARNING"})
    
    def finalize_session(self) -> None:
        self.session_data["session_end"] = datetime.now().isoformat()
        
        if self.log_file:
            self._write_to_file()
        
        if self.verbose:
            self.console_logger.info("Session completed")
    
    def _write_to_file(self) -> None:
        try:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_path, 'w') as f:
                json.dump(self.session_data, f, indent=2)
            
            self.console_logger.info(f"Session log written to {self.log_file}")
        except Exception as e:
            self.console_logger.error(f"Failed to write log file: {e}")