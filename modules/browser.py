import os
import time
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
            self.actions.move_to_element(board.find_element(By.CSS_SELECTOR, f".piece.square-{source_sq}")).click().perform()
            time.sleep(0.05)
            
            try: t_el = board.find_element(By.CSS_SELECTOR, f".hint.square-{dest_sq}")
            except: t_el = board.find_element(By.CSS_SELECTOR, f".square-{dest_sq}")
            
            self.actions.move_to_element(t_el).click().perform()
            
            if promotion:
                time.sleep(0.3)
                self.actions.move_to_element(self.driver.find_element(By.CSS_SELECTOR, f".promotion-piece.{'b' if is_black else 'w'}{promotion}")).click().perform()
            return True
        except: return False

    def is_turn(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, ".clock-bottom.clock-player-turn")
            return True
        except: return False

    def get_clock(self):
        try:
            txt = self.driver.find_element(By.CSS_SELECTOR, ".clock-bottom").text.strip()
            p = txt.split(':')
            if len(p) == 2: return float(p[0])*60 + float(p[1])
            elif len(p) == 3: return float(p[0])*3600 + float(p[1])*60 + float(p[2])
            return float(p[0])
        except: return 9999.0

    def get_all_clocks(self):
        try:
            wc = self.driver.find_element(By.CSS_SELECTOR, ".clock-white").text.strip()
            bc = self.driver.find_element(By.CSS_SELECTOR, ".clock-black").text.strip()
            return wc, bc
        except: return None, None
    
    def resign(self):
        try:
            try: self.driver.find_element(By.XPATH, "//span[contains(text(), 'Desistir')]").click()
            except: self.driver.find_element(By.CSS_SELECTOR, ".resign-button-component").click()
            time.sleep(0.5)
            self.driver.find_element(By.CSS_SELECTOR, "[data-cy='confirm-yes']").click()
            return True
        except: return False

    def start_new_game(self):
        try:
            self.driver.get("https://www.chess.com/play/online")
            wait = WebDriverWait(self.driver, 10)
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-cy='new-game-index-play']")))
            btn.click()
            return True
        except: return False