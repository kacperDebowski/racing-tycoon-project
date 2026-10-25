import curses
import time
import json
from model import RaceModel

class ConsoleView:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        self.init_colors()
        
        # --- DOKŁADNY UKŁAD TORU Z PRZESŁANEGO ASCII ART ---
        self.track_offset_y = 1
        self.track_offset_x = 55
        
        self.track_art = [
            " ██████████████                                                                                    ",
            "██             ██                                                                                ",
            "██             ██                                                                                ",
            " █               ██                                                                              ",
            " ██               ██                                                                             ",
            " ██                ██                                                                            ",
            "  ██                 ██                                                                          ",
            "   ██                 ██                                                                         ",
            "    █                   ██                                                                       ",
            "    ████                 ██                                                                      ",
            "       ██                   ██                                                                   ",
            "       ██                     ██                                                                 ",
            "        █                       ██                                                               ",
            "        ██                        ██                                                             ",
            "        ██                          ██                                                           ",
            "         █                            ██████                                                     ",
            "         ██                                 ██                                                 ",
            "          █                                   ███████████████████████████████                  ",
            "          ██                                                                  ██                  ",
            "           █                                                                    ██                 ",
            "            █                                                                    ██                ",
            "             ██                  █                                              ██                  ",
            "               ███            ██ █                                            ██                    ",
            "                  ███████████     ███████████████████████████████████████████                         "
        ]
        
        self.path = self._generate_path_from_art()
        self.last_car_pos = None

        self.draw_static_ui()

    def _generate_path_from_art(self):
        # Automatyczne wyznaczenie ciągłej ścieżki po pikselach '█' z wykresów art
        coords = set()
        for y, line in enumerate(self.track_art):
            for x, char in enumerate(line):
                if char == '█':
                    coords.add((y, x))
        
        if not coords:
            return [(0, 0)]

        # Znajdź punkt startowy na dole toru
        bottom_points = [c for c in coords if c[0] == max(c[0] for c in coords)]
        start_point = min(bottom_points, key=lambda c: c[1])
        
        path = [start_point]
        remaining = set(coords)
        remaining.remove(start_point)
        
        current = start_point
        while remaining:
            neighbors = [n for n in remaining if abs(n[0] - current[0]) <= 1 and abs(n[1] - current[1]) <= 1]
            if not neighbors:
                next_p = min(remaining, key=lambda p: (p[0]-current[0])**2 + (p[1]-current[1])**2)
            else:
                next_p = min(neighbors, key=lambda p: (p[0]-current[0])**2 + (p[1]-current[1])**2)
            path.append(next_p)
            remaining.remove(next_p)
            current = next_p
            
        return path[::-1]

    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Kolor Bolidu
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK) # Hard
        curses.init_pair(8, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Wet
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLACK) # Tor asfalt
        curses.init_pair(10, curses.COLOR_RED, curses.COLOR_WHITE)  # Linia Startu

    def draw_progress_bar(self, y, x, label, value, max_value, color_pair):
        width = 20
        filled = int((value / max_value) * width)
        filled = max(0, min(width, filled))
        bar = "█" * filled + "-" * (width - filled)
        text = f"{label}: [{bar}] {value:5.1f}%".ljust(45)
        self.stdscr.addstr(y, x, text, curses.color_pair(color_pair))

    def draw_static_ui(self):
        self.stdscr.clear()
        self.stdscr.addstr(0, 2, "🏁 RACING TYCOON - GP WŁOCH (MONZA) 🏁", curses.A_BOLD | curses.color_pair(4))
        
        # --- 1. LEWA KOLUMNA (Telemetria) ---
        self.stdscr.addstr(11, 2, "[ SEKTORY ]".ljust(25, "-"), curses.color_pair(4))
        self.stdscr.addstr(16, 2, "[ STEROWANIE ]".ljust(50, "-"), curses.color_pair(4))
        
        self.stdscr.addstr(17, 2, "[1] Eco | [2] Standard | [3] Push  (Tryb Silnika)")
        self.stdscr.addstr(18, 2, "[T] Zmień opony na zjazd  |  [P] Zaplanuj Pit Stop")
        self.stdscr.addstr(19, 2, "[Q] Zakończ symulację")
        
        self.stdscr.addstr(6, 2, "Opony (Obecne): ")
        self.stdscr.addstr(6, 28, "Zjazd po: ")

        # --- 2. ŚRODKOWA KOLUMNA (Rysowanie toru z art) ---
        for i, line in enumerate(self.track_art):
            self.stdscr.addstr(self.track_offset_y + i, self.track_offset_x, line, curses.color_pair(9))
            
        # Oznaczenie mety na dole toru
        self.stdscr.addstr(self.track_offset_y + 23, self.track_offset_x + 40, "=== START / META ===", curses.color_pair(4) | curses.A_BOLD)
            
        # --- 3. PRAWA KOLUMNA (Timing Tower F1) ---
        tower_x = 155
        self.stdscr.addstr(2, tower_x, "=======================", curses.color_pair(4))
        self.stdscr.addstr(3, tower_x, " 🏁 TABELA WYNIKÓW 🏁  ", curses.color_pair(4) | curses.A_BOLD)
        self.stdscr.addstr(4, tower_x, "=======================", curses.color_pair(4))
        self.stdscr.addstr(5, tower_x, " POZ | KIEROWCA | CZAS ", curses.color_pair(7))
        self.stdscr.addstr(6, tower_x, "-----------------------", curses.color_pair(7))

        self.stdscr.refresh()

    def update(self, model):
        # Lewa kolumna
        self.stdscr.addstr(2, 2, f"Okrążenie: {model.laps}/{model.max_laps}".ljust(25), curses.A_BOLD)
        
        weather_icon = "☀" if model.weather == "Słonecznie" else ("☁" if model.weather == "Pochmurno" else "☂")
        weather_color = 2 if model.weather == "Słonecznie" else (4 if model.weather == "Pochmurno" else 8)
        self.stdscr.addstr(2, 30, f"Pogoda: {weather_icon} {model.weather}".ljust(20), curses.color_pair(weather_color) | curses.A_BOLD)

        status_color = curses.color_pair(3) if "DNF" in model.status else (curses.color_pair(2) if "Zjazd" in model.status else curses.color_pair(1))
        self.stdscr.addstr(3, 2, f"Status: {model.status}".ljust(50), status_color)
        
        if model.vsc_active:
            self.stdscr.addstr(4, 2, ">>> VSC - ZWOLNIJ! <<<".ljust(50), curses.color_pair(2) | curses.A_BLINK | curses.A_BOLD)
        else:
            self.stdscr.addstr(4, 2, "".ljust(50))

        compound_colors = {"Soft": 3, "Hard": 7, "Wet": 8}
        c_col = compound_colors.get(model.compound, 7)
        self.stdscr.addstr(6, 18, f"{model.compound}".ljust(8), curses.color_pair(c_col) | curses.A_BOLD)
        
        n_col = compound_colors.get(model.next_compound, 7)
        pit_blink = curses.A_BLINK if model.pit_requested else 0
        self.stdscr.addstr(6, 38, f"{model.next_compound}".ljust(8), curses.color_pair(n_col) | curses.A_BOLD | pit_blink)

        tire_color = 1 if model.tire_wear > 50 else (2 if model.tire_wear > 20 else 3)
        fuel_color = 1 if model.fuel > 40 else (2 if model.fuel > 20 else 3)
        self.draw_progress_bar(8, 2, "Zużycie Opon", model.tire_wear, 100.0, tire_color)
        self.draw_progress_bar(9, 2, "Stan Paliwa ", model.fuel, 100.0, fuel_color)

        for i in range(3):
            sec_time = f"{model.sectors[i]:.2f}s" if model.sectors[i] > 0 else "--.--"
            col = model.sector_colors[i]
            curses_col = curses.color_pair(col) | curses.A_BOLD if col > 0 else 0
            self.stdscr.addstr(12 + i, 2, f"Sektor {i+1}: {sec_time}".ljust(25), curses_col)

        time_str = f"{model.last_lap_time:.3f} s" if model.last_lap_time > 0 else "--.--- s"
        best_str = f"{model.best_lap_time:.3f} s" if model.best_lap_time < 900 else "--.--- s"
        self.stdscr.addstr(12, 30, f"Ostatnie: {time_str}".ljust(25))
        self.stdscr.addstr(13, 30, f"Najlepsze:{best_str}".ljust(25), curses.color_pair(5) | curses.A_BOLD)

        # Środkowa kolumna (Tor + Bolid)
        if self.last_car_pos:
            old_y, old_x = self.last_car_pos
            self.stdscr.addstr(self.track_offset_y + old_y, self.track_offset_x + old_x, "█", curses.color_pair(9))

        if model.in_pit:
            self.stdscr.addstr(self.track_offset_y + 11, self.track_offset_x + 35, "[ PIT STOP ]", curses.color_pair(3) | curses.A_BLINK | curses.A_BOLD)
            self.last_car_pos = None
        else:
            self.stdscr.addstr(self.track_offset_y + 11, self.track_offset_x + 35, "            ")
            path_idx = int(model.lap_progress * len(self.path))
            if path_idx >= len(self.path): path_idx = len(self.path) - 1
            new_y, new_x = self.path[path_idx]
            self.stdscr.addstr(self.track_offset_y + new_y, self.track_offset_x + new_x, "@", curses.color_pair(5) | curses.A_BOLD)
            self.last_car_pos = (new_y, new_x)

        # Prawa kolumna (Timing Tower)
        tower_x = 155
        if model.gap_to_leader >= 0:
            self.stdscr.addstr(7, tower_x, "  1  | BOT      | LIDER".ljust(23), curses.color_pair(7) | curses.A_BOLD)
            gap_text = f"+{model.gap_to_leader:.3f}s"
            self.stdscr.addstr(8, tower_x, f"  2  | GRACZ    | {gap_text}".ljust(23), curses.color_pair(5) | curses.A_BOLD)
        else:
            self.stdscr.addstr(7, tower_x, "  1  | GRACZ    | LIDER".ljust(23), curses.color_pair(5) | curses.A_BOLD)
            gap_text = f"+{abs(model.gap_to_leader):.3f}s"
            self.stdscr.addstr(8, tower_x, f"  2  | BOT      | {gap_text}".ljust(23), curses.color_pair(7) | curses.A_BOLD)
        
        self.stdscr.addstr(9, tower_x, "-----------------------", curses.color_pair(7))
        self.stdscr.refresh()

    def get_input(self):
        try:
            return self.stdscr.getkey()
        except curses.error:
            return None

    def show_end_screen(self):
        self.stdscr.nodelay(False)
        self.stdscr.addstr(23, 2, "Naciśnij dowolny klawisz, aby wyjść...", curses.A_BLINK | curses.color_pair(2))
        self.stdscr.getch()

class Controller:
    def __init__(self, stdscr):
        self.model = RaceModel()
        self.view = ConsoleView(stdscr)

    def run(self):
        last_tick = time.time()
        tick_rate = 0.05  

        while True:
            key = self.view.get_input()
            if key:
                k = key.lower()
                if k == 'q': break
                elif k == 'p': self.model.call_pitstop()
                elif k == 't': self.model.cycle_tires()
                elif k == '1': self.model.set_engine_mode("Eco")
                elif k == '2': self.model.set_engine_mode("Standard")
                elif k == '3': self.model.set_engine_mode("Push")

            current_time = time.time()
            if current_time - last_tick >= tick_rate:
                if "Koniec" not in self.model.status and "DNF" not in self.model.status:
                    self.model.update() 
                last_tick = current_time

            self.view.update(self.model)
            time.sleep(0.01)

        self.view.show_end_screen()
        self.save_telemetry()

    def save_telemetry(self):
        data = {
            "completed_laps": self.model.laps,
            "best_lap_time": self.model.best_lap_time,
            "gap_to_leader": self.model.gap_to_leader
        }
        with open("race_telemetry.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

def main(stdscr):
    app = Controller(stdscr)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)