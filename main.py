import os
from modules.browser import BrowserManager
from modules.engine import EngineManager
from modules.ui import TritonideUI

os.system("taskkill /f /im chrome.exe >nul 2>&1")
os.system("taskkill /f /im chromedriver.exe >nul 2>&1")

def main():
    try:
        engine_mgr = EngineManager()
        if not engine_mgr.init_engine():
            print("Stockfish initialization failed. Check stockfish.exe.")
            return

        browser_mgr = BrowserManager()
        app = TritonideUI(browser_mgr, engine_mgr)
        app.mainloop()

    except Exception as e:
        print(f"Critical Error: {e}")
        os.system("pause")

if __name__ == "__main__":
    main()