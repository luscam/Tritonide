import customtkinter as ctk
import threading
import time
import random
from modules.config import ConfigManager
from modules.utils import get_fen_from_board, coords_to_sq

class TritonideUI(ctk.CTk):
    COLORS = {
        "accent": "#00E5FF", "bg_card": "#141414", "text": "#E0E0E0",
        "danger": "#FF3333", "success": "#00FF7F", "warning": "#FFA500"
    }

    def __init__(self, browser, engine):
        super().__init__()
        self.browser = browser
        self.engine = engine
        self.title("TRITONIDE ELITE")
        self.geometry("550x800")
        self.resizable(False, False)
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color="#0B0B0B")
        
        self.app_state = {
            "autoplay": False, "auto_newgame": False, "auto_resign": False,
            "panic": True, "login_mode": False, "processing": False,
            "toxic_fen": "", "consecutive_errors": 0, "last_fen": "",
            "game_started": False, "last_white_time": "", "last_black_time": "",
            "clock_stable_start": 0, "new_game_clicked": False,
            "last_my_clock_val": 9999.0,
            "clock_stuck_frames": 0
        }
        
        self.init_components()
        self.load_settings()
        self.worker_thread = threading.Thread(target=self.core_loop, daemon=True)
        self.worker_thread.start()

    def init_components(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(pady=15)
        ctk.CTkLabel(self.header, text="TRITONIDE", font=("Segoe UI", 32, "bold"), text_color=self.COLORS["accent"]).pack()
        
        self.controls = ctk.CTkFrame(self, fg_color=self.COLORS["bg_card"])
        self.controls.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkButton(self.controls, text="OPEN CHROME", font=("Segoe UI", 12, "bold"), fg_color="#333", hover_color="#444", command=self.run_browser).pack(side="left", padx=10, pady=10, expand=True, fill="x")
        self.sw_login = ctk.CTkSwitch(self.controls, text="LOGIN MODE", font=("Segoe UI", 12), command=self.toggle_login)
        self.sw_login.pack(side="right", padx=10, pady=10)

        self.tabs = ctk.CTkTabview(self, width=500, height=550, fg_color=self.COLORS["bg_card"], corner_radius=10)
        self.tabs.pack(pady=10)
        for t in ["Dashboard", "Engine", "Personalities", "Settings"]: self.tabs.add(t)
        
        self.build_dashboard(self.tabs.tab("Dashboard"))
        self.build_engine(self.tabs.tab("Engine"))
        self.build_personalities(self.tabs.tab("Personalities"))
        self.build_settings(self.tabs.tab("Settings"))
        
        self.lbl_status = ctk.CTkLabel(self, text="WAITING FOR CHROME", font=("Consolas", 11), text_color="#444")
        self.lbl_status.pack(side="bottom", pady=10)

    def build_dashboard(self, parent):
        ctk.CTkButton(parent, text="FORCE BEST MOVE", font=("Segoe UI", 14, "bold"), fg_color=self.COLORS["accent"], text_color="#000", hover_color="#00B2CC", height=50, command=self.force_move).pack(fill="x", padx=30, pady=20)
        self.sw_auto = ctk.CTkSwitch(parent, text="AUTOPLAY MODE", font=("Segoe UI", 13, "bold"), progress_color=self.COLORS["success"], command=lambda: self.update_state("autoplay", self.sw_auto.get()))
        self.sw_auto.pack(pady=10)
        self.sw_newgame = ctk.CTkSwitch(parent, text="AUTO NEW GAME", font=("Segoe UI", 13, "bold"), progress_color=self.COLORS["success"], command=lambda: self.update_state("auto_newgame", self.sw_newgame.get()))
        self.sw_newgame.pack(pady=10)
        self.sw_panic = ctk.CTkSwitch(parent, text="PANIC MODE", font=("Segoe UI", 13, "bold"), progress_color=self.COLORS["warning"], command=lambda: self.update_state("panic", self.sw_panic.get()))
        self.sw_panic.pack(pady=10)
        self.txt_log = ctk.CTkTextbox(parent, height=150, font=("Consolas", 11), fg_color="#0F0F0F", text_color="#aaa")
        self.txt_log.pack(fill="x", padx=20, pady=20)

    def build_engine(self, parent):
        ctk.CTkLabel(parent, text="CONFIGURATION", font=("Segoe UI", 14, "bold")).pack(pady=15)
        self.sld_skill = self.create_slider(parent, "Skill", 0, 20, 20)
        self.sld_depth = self.create_slider(parent, "Depth", 1, 25, 24)
        self.sld_min = self.create_slider(parent, "Min Delay", 0.1, 10.0, 100, True)
        self.sld_max = self.create_slider(parent, "Max Delay", 0.1, 15.0, 150, True)

    def build_personalities(self, parent):
        ctk.CTkLabel(parent, text="LOAD PROFILE", font=("Segoe UI", 14, "bold")).pack(pady=20)
        profiles = [("GRANDMASTER", 20, 22, 0.6, 1.2, "#9B59B6"), ("LEGIT", 20, 12, 0.8, 3.5, "#00E5FF"), ("HUMAN BLITZ", 15, 10, 0.2, 0.6, "#3498DB"), ("BEGINNER", 5, 4, 2.5, 6.0, "#F1C40F"), ("AGGRESSIVE", 18, 15, 0.1, 0.3, "#E74C3C")]
        for n, s, d, mn, mx, c in profiles:
            ctk.CTkButton(parent, text=n, font=("Segoe UI", 12, "bold"), fg_color="transparent", border_width=2, border_color=c, text_color=c, height=40, command=lambda s=s, d=d, mn=mn, mx=mx, nm=n: self.load_profile(s, d, mn, mx, nm)).pack(fill="x", padx=40, pady=6)

    def build_settings(self, parent):
        ctk.CTkLabel(parent, text="AUTO-RESIGN", font=("Segoe UI", 14, "bold"), text_color=self.COLORS["danger"]).pack(pady=20)
        self.sw_resign = ctk.CTkSwitch(parent, text="ENABLE", font=("Segoe UI", 12), progress_color=self.COLORS["danger"], command=lambda: self.update_state("auto_resign", self.sw_resign.get()))
        self.sw_resign.pack()
        self.sld_eval = self.create_slider(parent, "Threshold", -2000, -300, 17)
        ctk.CTkLabel(parent, text="CONFIG MANAGEMENT", font=("Segoe UI", 14, "bold")).pack(pady=(40, 10))
        ctk.CTkButton(parent, text="SAVE CONFIG", fg_color="#333", command=self.save_settings).pack(fill="x", padx=40, pady=5)
        ctk.CTkButton(parent, text="LOAD CONFIG", fg_color="#333", command=self.load_settings).pack(fill="x", padx=40, pady=5)

    def create_slider(self, parent, label_text, vmin, vmax, steps, float_val=False):
        lbl = ctk.CTkLabel(parent, text=f"{label_text}: 0")
        lbl.pack()
        sld = ctk.CTkSlider(parent, from_=vmin, to=vmax, number_of_steps=steps, command=lambda v: lbl.configure(text=f"{label_text}: {v:.1f}" if float_val else f"{label_text}: {int(v)}"))
        sld.pack(fill="x", padx=30, pady=5)
        sld.label_ref = lbl
        sld.label_text = label_text
        sld.is_float = float_val
        return sld

    def log(self, text): self.txt_log.insert("end", f"> {text}\n"); self.txt_log.see("end")
    def status(self, text, color="#666"): self.lbl_status.configure(text=f"STATUS: {text}", text_color=color)
    
    def update_state(self, key, val): 
        self.app_state[key] = val
        self.log(f"{key}: {val}")
        if key in ["autoplay", "auto_newgame", "panic", "auto_resign"]:
            self.save_settings(silent=True)

    def run_browser(self): threading.Thread(target=self.browser.launch, daemon=True).start()
    def toggle_login(self): self.app_state["login_mode"] = self.sw_login.get(); self.log(f"Login Mode: {self.app_state['login_mode']}")

    def load_profile(self, s, d, mn, mx, n):
        self.sld_skill.set(s); self.sld_depth.set(d); self.sld_min.set(mn); self.sld_max.set(mx)
        for sld in [self.sld_skill, self.sld_depth, self.sld_min, self.sld_max]: sld._command(sld.get())
        self.log(f"Profile Loaded: {n}")

    def save_settings(self, silent=False):
        data = {
            "skill": self.sld_skill.get(), "depth": self.sld_depth.get(),
            "min_delay": self.sld_min.get(), "max_delay": self.sld_max.get(),
            "resign_threshold": self.sld_eval.get(), "auto_newgame": self.sw_newgame.get(),
            "autoplay": self.sw_auto.get(), "panic": self.sw_panic.get(),
            "auto_resign": self.sw_resign.get()
        }
        ConfigManager.save(data)
        if not silent: self.log("Config saved.")

    def load_settings(self):
        data = ConfigManager.load()
        self.sld_skill.set(data["skill"]); self.sld_depth.set(data["depth"])
        self.sld_min.set(data["min_delay"]); self.sld_max.set(data["max_delay"])
        self.sld_eval.set(data["resign_threshold"])
        for sld in [self.sld_skill, self.sld_depth, self.sld_min, self.sld_max, self.sld_eval]: sld._command(sld.get())
        
        if data["auto_newgame"]: self.sw_newgame.select(); self.app_state["auto_newgame"] = True
        else: self.sw_newgame.deselect(); self.app_state["auto_newgame"] = False

        if data["autoplay"]: self.sw_auto.select(); self.app_state["autoplay"] = True
        else: self.sw_auto.deselect(); self.app_state["autoplay"] = False

        if data["panic"]: self.sw_panic.select(); self.app_state["panic"] = True
        else: self.sw_panic.deselect(); self.app_state["panic"] = False

        if data["auto_resign"]: self.sw_resign.select(); self.app_state["auto_resign"] = True
        else: self.sw_resign.deselect(); self.app_state["auto_resign"] = False

        self.log("Config loaded.")

    def force_move(self):
        if not self.app_state["processing"] and self.browser.driver: threading.Thread(target=self.engine_step, daemon=True).start()

    def get_panic_params(self):
        sk, dp = int(self.sld_skill.get()), int(self.sld_depth.get())
        mn, mx = self.sld_min.get(), self.sld_max.get()
        if not self.app_state["panic"]: return sk, dp, mn, mx
        
        clock = self.browser.get_clock()
        if clock < 5.0: self.status("PANIC! < 5s", self.COLORS["danger"]); return 20, 1, 0.0, 0.05
        if clock < 15.0: self.status("BLITZ! < 15s", self.COLORS["warning"]); return 20, 8, 0.1, 0.3
        if clock < 30.0: self.status("FAST! < 30s", self.COLORS["accent"]); return sk, max(1, dp-4), 0.1, 0.5
        return sk, dp, mn, mx

    def engine_step(self):
        self.app_state["processing"] = True
        try:
            is_my_turn = False
            turn_indicator = self.browser.is_turn()
            
            if turn_indicator is True:
                is_my_turn = True
                self.app_state["clock_stuck_frames"] = 0
            elif turn_indicator is False:
                is_my_turn = False
                self.app_state["clock_stuck_frames"] = 0
            else:
                curr_clock = self.browser.get_clock()
                prev_clock = self.app_state.get("last_my_clock_val", 9999.0)
                
                if curr_clock < prev_clock - 0.01:
                    is_my_turn = True
                    self.app_state["clock_stuck_frames"] = 0
                elif curr_clock == prev_clock and prev_clock != 9999.0:
                    self.app_state["clock_stuck_frames"] += 1
                
                self.app_state["last_my_clock_val"] = curr_clock

            if not is_my_turn:
                if self.app_state["autoplay"]: 
                    self.status("OPPONENT'S TURN", "#666")
                self.app_state["processing"] = False; return

            board = self.browser.get_board_element()
            if not board: self.app_state["processing"] = False; return
            
            bfen = get_fen_from_board(board)
            if not bfen: self.app_state["processing"] = False; return
            
            is_black = "flipped" in board.get_attribute("class")
            fen = f"{bfen} {'b' if is_black else 'w'} KQkq - 0 1"
            
            if fen == self.app_state["toxic_fen"]: 
                self.app_state["processing"] = False; return
            
            if fen == self.app_state["last_fen"]:
                self.app_state["processing"] = False; return

            if self.app_state["auto_resign"]:
                eval_data = self.engine.get_evaluation(fen)
                score = eval_data['value']
                if eval_data['type'] == 'mate': score = -9999 if eval_data['value'] < 0 else 9999
                p_score = score if not is_black else -score
                if p_score < self.sld_eval.get():
                    self.log(f"Resigning (Eval {p_score})")
                    self.browser.resign()
                    self.app_state["processing"] = False; return

            sk, dp, mn, mx = self.get_panic_params()
            if sk == int(self.sld_skill.get()): self.status("CALCULATING...", self.COLORS["accent"])

            bm = self.engine.get_best_move(fen, sk, dp)
            if not bm: self.app_state["processing"] = False; return
            
            delay = random.uniform(mn, mx)
            self.status(f"MOVE: {bm.upper()} ({delay:.1f}s)", self.COLORS["success"])
            time.sleep(delay)

            src, dst = coords_to_sq(bm[:2]), coords_to_sq(bm[2:4])
            promo = bm[4] if len(bm) > 4 else None
            
            if self.browser.make_move(src, dst, promo, is_black):
                self.log(f"Played: {bm}")
                self.app_state["last_fen"] = fen
                self.app_state["consecutive_errors"] = 0
                self.status("IDLE")
            
        except Exception as e:
            self.app_state["consecutive_errors"] += 1
            if self.app_state["consecutive_errors"] >= 3: 
                self.log("Resetting Engine..."); self.engine.restart(); self.app_state["consecutive_errors"] = 0
            if "crashed" in str(e).lower(): self.app_state["toxic_fen"] = fen; self.engine.restart()
            
        self.app_state["processing"] = False

    def handle_game_end(self):
        if not self.app_state["auto_newgame"] or self.app_state["new_game_clicked"]: return
        
        wc, bc = self.browser.get_all_clocks()
        
        if wc != self.app_state["last_white_time"] or bc != self.app_state["last_black_time"]:
            self.app_state["last_white_time"] = wc; self.app_state["last_black_time"] = bc
            self.app_state["clock_stable_start"] = time.time()
            self.app_state["game_started"] = True
        
        elif self.app_state["game_started"] and (time.time() - self.app_state["clock_stable_start"] > 8.0):
            if self.browser.start_new_game():
                self.status("GAME OVER - NEW GAME", self.COLORS["success"])
                self.app_state["new_game_clicked"] = True
                self.app_state["game_started"] = False
                self.app_state["toxic_fen"] = ""
                self.app_state["last_fen"] = ""
                threading.Thread(target=lambda: (time.sleep(10), self.app_state.update({"new_game_clicked": False})), daemon=True).start()

    def core_loop(self):
        while True:
            try:
                if not self.browser.driver:
                    self.status("BROWSER CLOSED")
                    time.sleep(1); continue
                
                if self.app_state["login_mode"]:
                    self.status("LOGIN MODE ACTIVE", "#FFF")
                    time.sleep(1); continue

                self.handle_game_end()
                
                if self.app_state["autoplay"] and not self.app_state["processing"]:
                    self.engine_step()
            except: pass
            time.sleep(0.3)