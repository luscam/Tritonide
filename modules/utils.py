from selenium.webdriver.common.by import By

def get_fen_from_board(board_element):
    try:
        piece_map = {}
        pieces = board_element.find_elements(By.CSS_SELECTOR, ".piece")
        
        for p in pieces:
            cls = p.get_attribute("class")
            sq, color, role = None, None, None
            for c in cls.split():
                if c.startswith("square-"): sq = c.split("-")[1]
                elif len(c) == 2 and c[0] in ['w', 'b']: color, role = c[0], c[1]
            if sq and color and role:
                piece_map[sq] = role.upper() if color == 'w' else role.lower()

        rows = []
        for r in range(8, 0, -1):
            empty, row_s = 0, ""
            for c in range(1, 9):
                k = f"{c}{r}"
                if k in piece_map:
                    if empty > 0: row_s += str(empty); empty = 0
                    row_s += piece_map[k]
                else: empty += 1
            if empty > 0: row_s += str(empty)
            rows.append(row_s)
        return "/".join(rows)
    except: return None

def coords_to_sq(alg):
    m = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
    return f"{m[alg[0]]}{alg[1]}"