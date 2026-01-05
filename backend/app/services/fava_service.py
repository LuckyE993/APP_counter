import subprocess
import os
import signal
from typing import Optional
from ..config import settings

class FavaService:
    """Fava服务管理类"""
    
    _process: Optional[subprocess.Popen] = None
    _port: int = 5000
    
    @classmethod
    def start(cls, port: int = 5000) -> bool:
        """启动Fava服务"""
        if cls._process is not None:
            print("Fava is already running")
            return True
        
        try:
            cls._port = port
            # 启动fava服务
            cls._process = subprocess.Popen(
                [
                    "fava",
                    settings.BEANCOUNT_MAIN_PATH,
                    "-p", str(port),
                    "--host", "127.0.0.1"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            print(f"Fava started on port {port}")
            return True
        except Exception as e:
            print(f"Failed to start Fava: {e}")
            return False
    
    @classmethod
    def stop(cls) -> bool:
        """停止Fava服务"""
        if cls._process is None:
            return True
        
        try:
            if os.name == 'nt':
                # Windows
                cls._process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                # Unix-like
                cls._process.terminate()
            
            cls._process.wait(timeout=5)
            cls._process = None
            print("Fava stopped")
            return True
        except Exception as e:
            print(f"Failed to stop Fava gracefully: {e}")
            if cls._process:
                cls._process.kill()
                cls._process = None
            return False
    
    @classmethod
    def is_running(cls) -> bool:
        """检查Fava是否在运行"""
        if cls._process is None:
            return False
        
        # 检查进程是否还在运行
        return cls._process.poll() is None
    
    @classmethod
    def get_url(cls) -> str:
        """获取Fava访问URL"""
        return f"http://127.0.0.1:{cls._port}"
