import subprocess
import sys
import psutil
from typing import Optional
from fastapi import HTTPException


class ProcessService:
    """Service for managing agent processes"""
    
    @staticmethod
    def start_agent_process(agent_id: str, filepath: str) -> subprocess.Popen:
        """Start the agent process"""
        try:
            process = subprocess.Popen(
                [sys.executable, filepath],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return process
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")
    
    @staticmethod
    def stop_agent_process(process_id: int) -> bool:
        """Stop the agent process"""
        try:
            if psutil.pid_exists(process_id):
                process = psutil.Process(process_id)
                process.terminate()
                process.wait(timeout=5)
                return True
            return False
        except Exception:
            return False
    
    @staticmethod
    def is_process_running(process_id: int) -> bool:
        """Check if a process is running"""
        try:
            return psutil.pid_exists(process_id)
        except Exception:
            return False
    
    @staticmethod
    def get_process_uptime(process_id: int) -> Optional[str]:
        """Get process uptime in seconds"""
        try:
            if not psutil.pid_exists(process_id):
                return None
            process = psutil.Process(process_id)
            uptime_seconds = psutil.time.time() - process.create_time()
            return f"{int(uptime_seconds)}s"
        except Exception:
            return "unknown"
