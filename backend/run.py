
import sys
import asyncio
import uvicorn
import platform

def start_server():
    """
    ApplyIQ Startup Script for Windows Compatibility.
    Ensures the ProactorEventLoop is used so that Playwright can manage subprocesses.
    """
    print("-" * 50)
    print(f"ApplyIQ Startup - {platform.system()} {platform.release()}")
    print(f"Python Version: {platform.python_version()}")
    
    # ─── Windows Loop Policy ───
    if sys.platform == "win32":
        print("Setting WindowsProactorEventLoopPolicy...")
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    print("Launching Uvicorn...")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        loop="asyncio",
        log_level="info"
    )

if __name__ == "__main__":
    start_server()
