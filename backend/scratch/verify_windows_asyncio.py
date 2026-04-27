
import asyncio
import sys
import os

# Set encoding for Windows stdout
sys.stdout.reconfigure(encoding='utf-8')

# Replicate the fix
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def test_minimal():
    print("Testing subprocess creation with ProactorEventLoop...")
    try:
        # Playwright essentially does this:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        print(f"Subprocess success: {stdout.decode().strip()}")
        
        print("Testing Playwright specifically...")
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                print("Playwright connection started!")
                # Don't actually launch browser to save time/resources if not needed
                # Just starting the connection verifies the loop compatibility
                return True
        except ImportError:
            print("Playwright not installed in venv, skipping browser test but loop fix verified.")
            return True
            
    except NotImplementedError:
        print("FAILED: NotImplementedError still occurring!")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_minimal())
    if success:
        print("\n[SUCCESS] Windows Asyncio fix verified!")
        sys.exit(0)
    else:
        sys.exit(1)
