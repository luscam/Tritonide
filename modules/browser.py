import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BrowserManager:
    def __init__(self):
        self.driver = None
        self.actions = None
        self.user_data_dir = os.path.join(os.getcwd(), "dados")
    
    def launch(self):
        self.quit()
        os.makedirs(self.user_data_dir, exist_ok=True)
        opts = webdriver.ChromeOptions()
        opts.add_argument(f"user-data-dir={os.path.abspath(self.user_data_dir)}")
        opts.add_argument('--disable-blink-features=AutomationControlled')
        opts.add_argument("--disable-infobars")
        opts.add_argument("--start-maximized")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--log-level=3")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=opts)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.navigator.chrome = { runtime: {}, };
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5], });
            """
        })
        self.driver.get("https://www.chess.com/play/online")
        self.actions = ActionChains(self.driver)

    def quit(self):
        try:
            if self.driver:
                self.driver.quit()
        except: pass
        self.driver = None

    def get_board_element(self):
        if not self.driver: return None
        try:
            return self.driver.find_element(By.CSS_SELECTOR, "chess-board, wc-chess-board")
        except: return None

    def make_move(self, source_sq, dest_sq, promotion=None, is_black=False):
        if not self.driver or not self.actions: return False
        try:
            board = self.get_board_element()
            
            try:
                src_el = board.find_element(By.CSS_SELECTOR, f".piece.square-{source_sq}")
            except:
                self.driver.execute_script(f"""
                    const el = document.querySelector('.piece.square-{source_sq}');
                    if(el) {{
                        const rect = el.getBoundingClientRect();
                        const x = rect.left + (rect.width/2);
                        const y = rect.top + (rect.height/2);
                        document.elementFromPoint(x, y).click();
                    }}
                """)
                time.sleep(0.05)
            else:
                self.actions.move_to_element(src_el).click().perform()
                time.sleep(0.02)
            
            try: 
                target_el = board.find_element(By.CSS_SELECTOR, f".hint.square-{dest_sq}")
            except: 
                target_el = board.find_element(By.CSS_SELECTOR, f".square-{dest_sq}")
            
            self.actions.move_to_element(target_el).click().perform()
            
            if promotion:
                time.sleep(0.15)
                prom_selector = f".promotion-piece.{'b' if is_black else 'w'}{promotion}"
                try:
                    self.actions.move_to_element(self.driver.find_element(By.CSS_SELECTOR, prom_selector)).click().perform()
                except:
                    self.driver.execute_script(f"document.querySelector('{prom_selector}')?.click();")
            
            return True
        except: return False

    def is_turn(self):
        if not self.driver: return None
        script = """
            const getClock = (isBottom) => {
                const selector = isBottom 
                    ? '.clock-bottom, [data-cy="clock-bottom"], .player-component.bottom .clock-component' 
                    : '.clock-top, [data-cy="clock-top"], .player-component.top .clock-component';
                return document.querySelector(selector);
            };

            const bottom = getClock(true);
            const top = getClock(false);

            if (!bottom || !top) return null;

            const activeKeywords = ['clock-player-turn', 'clock-active', 'clock-running'];
            
            const checkActive = (el) => activeKeywords.some(cls => el.classList.contains(cls)) || 
                                        el.querySelector('.clock-running') !== null;

            const isBottomActive = checkActive(bottom);
            const isTopActive = checkActive(top);

            if (isBottomActive) return true;
            if (isTopActive) return false;
            
            const bottomBg = window.getComputedStyle(bottom).backgroundColor;
            if (bottomBg === 'rgb(255, 255, 255)' || bottomBg === '#ffffff') return true;
            
            return null;
        """
        try:
            return self.driver.execute_script(script)
        except: return None

    def get_clock(self):
        try:
            script = """
                const el = document.querySelector('.clock-bottom, [data-cy="clock-bottom"], .player-component.bottom .clock-component');
                return el ? el.innerText : '';
            """
            txt = self.driver.execute_script(script).strip()
            txt = re.sub(r"[^\d:.]", "", txt)
            if not txt: return 9999.0
            
            p = txt.split(':')
            if len(p) == 2: return float(p[0])*60 + float(p[1])
            elif len(p) == 3: return float(p[0])*3600 + float(p[1])*60 + float(p[2])
            return float(p[0])
        except: return 9999.0

    def get_all_clocks(self):
        try:
            return self.driver.execute_script("""
                const getTxt = (sel) => document.querySelector(sel)?.innerText || '';
                return [
                    getTxt('.clock-white, .player-component.white .clock-component'),
                    getTxt('.clock-black, .player-component.black .clock-component')
                ]
            """)
        except: return None, None
    
    def resign(self):
        try:
            btns = self.driver.find_elements(By.XPATH, "//button[contains(., 'Desistir') or contains(., 'Resign')]")
            if not btns:
                btns = self.driver.find_elements(By.CSS_SELECTOR, ".resign-button-component")
            if btns:
                btns[0].click()
                time.sleep(0.5)
                conf = self.driver.find_elements(By.CSS_SELECTOR, "[data-cy='confirm-yes']")
                if conf:
                    conf[0].click()
                    return True
            return False
        except: return False

    def start_new_game(self):
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-cy='new-game-index-play']"))
            )
            btn.click()
            return True
        except: 
            try:
                self.driver.get("https://www.chess.com/play/online")
                return True
            except: return False