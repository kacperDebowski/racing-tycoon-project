import tkinter as tk
import curses
import math
import json
import random
from model import RaceModel, TRACKS, TEAMS

TRACK_GEOMETRIES = {
    "monza": {
        "waypoints": [
            (0.55, 0.88), (0.32, 0.88), (0.27, 0.88), (0.26, 0.84), (0.23, 0.84),
            (0.18, 0.78), (0.14, 0.65), (0.12, 0.50), (0.11, 0.42), (0.09, 0.41),
            (0.08, 0.37), (0.05, 0.24), (0.05, 0.19), (0.08, 0.17), (0.18, 0.15),
            (0.21, 0.16), (0.28, 0.28), (0.38, 0.42), (0.47, 0.53), (0.50, 0.52),
            (0.53, 0.55), (0.72, 0.55), (0.88, 0.55), (0.93, 0.58), (0.95, 0.68),
            (0.93, 0.79), (0.86, 0.86), (0.70, 0.88), (0.55, 0.88),
        ],
        "pit_lane": [(0.82, 0.86), (0.76, 0.82), (0.38, 0.82), (0.33, 0.87)],
        "pit_box": (0.56, 0.82),
        "pit_label": (0.56, 0.785),
    },
    "silverstone": {
        "waypoints": [
            (0.45, 0.86), (0.68, 0.86), (0.75, 0.81), (0.73, 0.73), (0.83, 0.67),
            (0.78, 0.60), (0.85, 0.55), (0.92, 0.34), (0.94, 0.24), (0.87, 0.18),
            (0.76, 0.22), (0.56, 0.20), (0.42, 0.15), (0.32, 0.24), (0.28, 0.20),
            (0.23, 0.27), (0.10, 0.52), (0.08, 0.62), (0.18, 0.72), (0.22, 0.83),
            (0.33, 0.86), (0.45, 0.86),
        ],
        "pit_lane": [(0.30, 0.85), (0.35, 0.80), (0.62, 0.80), (0.67, 0.85)],
        "pit_box": (0.48, 0.80),
        "pit_label": (0.48, 0.765),
    },
    "spa": {
        "waypoints": [
            (0.30, 0.72), (0.14, 0.86), (0.09, 0.85), (0.14, 0.75), (0.22, 0.62),
            (0.26, 0.54), (0.55, 0.26), (0.66, 0.16), (0.74, 0.22), (0.68, 0.32),
            (0.76, 0.38), (0.88, 0.34), (0.93, 0.43), (0.84, 0.52), (0.87, 0.62),
            (0.70, 0.68), (0.50, 0.70), (0.39, 0.66), (0.36, 0.71), (0.30, 0.72),
        ],
        "pit_lane": [(0.36, 0.73), (0.31, 0.77), (0.18, 0.86), (0.13, 0.84)],
        "pit_box": (0.24, 0.81),
        "pit_label": (0.27, 0.845),
    },
    "monaco": {
        "waypoints": [
            (0.26, 0.68), (0.26, 0.38), (0.24, 0.26), (0.36, 0.16), (0.50, 0.14),
            (0.60, 0.17), (0.62, 0.26), (0.74, 0.28), (0.76, 0.34), (0.64, 0.36),
            (0.74, 0.44), (0.88, 0.50), (0.86, 0.66), (0.68, 0.70), (0.52, 0.72),
            (0.46, 0.82), (0.36, 0.84), (0.24, 0.86), (0.18, 0.80), (0.26, 0.68),
        ],
        "pit_lane": [(0.22, 0.76), (0.31, 0.66), (0.31, 0.42), (0.26, 0.35)],
        "pit_box": (0.31, 0.54),
        "pit_label": (0.37, 0.54),
    },
}

TEAM_COLORS_MAP = {
    "redbull": "#3671C6",
    "ferrari": "#E80020",
    "mclaren": "#FF8000",
    "mercedes": "#27F4D2",
    "aston": "#229971",
    "williams": "#64C4FF",
    "rb": "#6692FF",
    "alpine": "#FF87BC",
    "sauber": "#52E252",
    "haas": "#B6BABD",
}


class TrackPreviewCanvas(tk.Canvas):
    """Miniaturowy podgląd wektorowego kształtu toru na ekranie wyboru Grand Prix."""

    def __init__(self, parent, track_id, **kwargs):
        super().__init__(parent, bg="#0f1117", highlightthickness=0, **kwargs)
        self.track_id = track_id
        self.bind("<Configure>", lambda _e: self.draw())

    def draw(self):
        self.delete("all")
        geom = TRACK_GEOMETRIES.get(self.track_id, TRACK_GEOMETRIES["monza"])
        w = max(self.winfo_width(), 160)
        h = max(self.winfo_height(), 100)
        pad = 16
        pts = []
        for nx, ny in geom["waypoints"]:
            pts.extend([pad + nx * (w - 2 * pad), pad + ny * (h - 2 * pad)])
        self.create_line(*pts, fill="#38bdf8", width=3, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        sx, sy = pts[0], pts[1]
        self.create_oval(sx - 4, sy - 4, sx + 4, sy + 4, fill="#ef4444", outline="#ffffff", width=1)


class CircuitTrackCanvas(tk.Canvas):
    """Pełnowymiarowy radar GPS toru renderujący nitkę dowolnego wybranego toru oraz 20 bolidów."""

    def __init__(self, parent, track_id="monza", **kwargs):
        super().__init__(parent, bg="#12151e", highlightthickness=1, highlightbackground="#2a2f3d", **kwargs)
        self.track_id = track_id
        self._load_geometry(track_id)
        self.bind("<Configure>", lambda _e: self.draw_static_track())

    def set_track(self, track_id):
        self.track_id = track_id
        self._load_geometry(track_id)
        self.draw_static_track()

    def _load_geometry(self, track_id):
        geom = TRACK_GEOMETRIES.get(track_id, TRACK_GEOMETRIES["monza"])
        self.waypoints = geom["waypoints"]
        self.pit_lane = geom["pit_lane"]
        self.pit_box = geom["pit_box"]
        self.pit_label = geom["pit_label"]

        self.cum_dist = [0.0]
        for i in range(1, len(self.waypoints)):
            dx = self.waypoints[i][0] - self.waypoints[i - 1][0]
            dy = self.waypoints[i][1] - self.waypoints[i - 1][1]
            self.cum_dist.append(self.cum_dist[-1] + math.hypot(dx, dy))
        self.total_len = self.cum_dist[-1]

    def _to_px(self, nx, ny):
        w = max(self.winfo_width(), 320)
        h = max(self.winfo_height(), 320)
        pad_x = 46
        pad_y = 54
        px = pad_x + nx * (w - 2 * pad_x)
        py = pad_y + ny * (h - 2 * pad_y)
        return px, py

    def get_track_point(self, progress):
        p = progress % 1.0
        target = p * self.total_len
        for i in range(1, len(self.cum_dist)):
            if self.cum_dist[i] >= target:
                seg_len = self.cum_dist[i] - self.cum_dist[i - 1]
                t = (target - self.cum_dist[i - 1]) / seg_len if seg_len > 0 else 0.0
                nx = self.waypoints[i - 1][0] + t * (self.waypoints[i][0] - self.waypoints[i - 1][0])
                ny = self.waypoints[i - 1][1] + t * (self.waypoints[i][1] - self.waypoints[i - 1][1])
                return self._to_px(nx, ny)
        return self._to_px(*self.waypoints[0])

    def draw_static_track(self):
        self.delete("static")
        pts = []
        for nx, ny in self.waypoints:
            px, py = self._to_px(nx, ny)
            pts.extend([px, py])

        w = max(self.winfo_width(), 320)
        track_title = TRACKS.get(self.track_id, TRACKS["monza"])["name"].upper()
        self.create_text(
            w // 2, 20,
            text=f"{track_title} — LIVE GPS RADAR",
            fill="#94a3b8", font=("Segoe UI", 10, "bold"), tags="static"
        )

        # Aleja serwisowa (Pit Lane)
        pit_coords = []
        for nx, ny in self.pit_lane:
            px, py = self._to_px(nx, ny)
            pit_coords.extend([px, py])
        self.create_line(*pit_coords, fill="#475569", width=5, smooth=True, tags="static")
        pit_lbl_x, pit_lbl_y = self._to_px(*self.pit_label)
        self.create_text(pit_lbl_x, pit_lbl_y, text="PIT LANE", fill="#64748b", font=("Consolas", 8, "bold"), tags="static")

        # Pobocza, asfalt i linia wyścigowa
        self.create_line(*pts, fill="#262c3a", width=20, capstyle=tk.ROUND, joinstyle=tk.ROUND, tags="static")
        self.create_line(*pts, fill="#3b4254", width=13, capstyle=tk.ROUND, joinstyle=tk.ROUND, tags="static")
        self.create_line(*pts, fill="#64748b", width=1, dash=(4, 4), tags="static")

        # Znaczniki sektorów S1, S2
        for sec_p, label in [(0.33, "S1"), (0.66, "S2")]:
            sx, sy = self.get_track_point(sec_p)
            self.create_oval(sx - 4, sy - 4, sx + 4, sy + 4, fill="#0f1117", outline="#38bdf8", width=2, tags="static")
            self.create_text(sx - 15, sy - 10, text=label, fill="#38bdf8", font=("Consolas", 8, "bold"), tags="static")

        # Linia START / META
        start_x, start_y = self._to_px(*self.waypoints[0])
        self.create_oval(start_x - 8, start_y - 8, start_x + 8, start_y + 8, outline="#ef4444", width=2, tags="static")
        self.create_line(start_x - 10, start_y, start_x + 10, start_y, fill="#ef4444", width=3, tags="static")
        self.create_text(start_x, start_y + 20, text="▲ START / META", fill="#38bdf8", font=("Consolas", 9, "bold"), tags="static")

    def render_cars(self, model):
        self.delete("dynamic")

        # 19 botów z kolorami swoich zespołów (przed startem ustawione na polach startowych)
        for idx, bot in enumerate(model.bots):
            if not model.race_started:
                grid_offset = -((idx + 1) * 0.0045)
                bx, by = self.get_track_point(grid_offset)
            else:
                bx, by = self.get_track_point(bot["progress"])

            in_pit = bot["pit_timer"] > 0
            dot_color = "#64748b" if in_pit else TEAM_COLORS_MAP.get(bot.get("team", ""), "#cbd5e1")
            self.create_oval(bx - 4, by - 4, bx + 4, by + 4, fill=dot_color, outline="#0f1117", width=1, tags="dynamic")
            self.create_text(bx, by - 10, text=bot["name"], fill="#94a3b8", font=("Consolas", 7), tags="dynamic")

        # Bolid Gracza w kolorze wybranego zespołu
        player_color = model.team_color
        if model.in_pit:
            px, py = self._to_px(*self.pit_box)
            self.create_oval(px - 8, py - 8, px + 8, py + 8, fill="#ef4444", outline="#ffffff", width=2, tags="dynamic")
            self.create_text(
                px, py - 18,
                text=f"PIT STOP ({model.pit_timer})",
                fill="#ef4444", font=("Consolas", 9, "bold"), tags="dynamic"
            )
        else:
            px, py = self.get_track_point(model.lap_progress)
            self.create_oval(px - 11, py - 11, px + 11, py + 11, outline="#ffffff", width=2, tags="dynamic")
            self.create_oval(px - 7, py - 7, px + 7, py + 7, fill=player_color, outline="#0f1117", width=1.5, tags="dynamic")
            self.create_text(px, py - 18, text=f"GRACZ ({model.team_short})", fill="#ffffff", font=("Consolas", 9, "bold"), tags="dynamic")


class GuiController:
    """Kontroler GUI: Menu Główne -> Wybór Toru -> Wybór Zespołu -> Pola Startowe & Opony -> 5 Świateł -> Wyścig."""

    def __init__(self, model=None, skip_menu=False):
        self.model = model if model is not None else RaceModel()
        self.switch_to_tui = False
        self._running = True
        self._start_seq_after_id = None

        self.selected_track = self.model.track_id
        self.selected_team = self.model.team_id
        self.selected_tire = self.model.starting_compound

        self.root = tk.Tk()
        self.root.title("Racing Tycoon — F1 Team Manager | GUI")
        self.root.geometry("1280x800")
        self.root.minsize(1140, 720)
        self.root.configure(bg="#0f1117")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.container = tk.Frame(self.root, bg="#0f1117")
        self.container.pack(fill=tk.BOTH, expand=True)

        if skip_menu:
            self._show_race_screen(run_start_lights=not self.model.race_started)
        else:
            self._show_main_menu()

    def _clear_container(self):
        if self._start_seq_after_id is not None:
            try:
                self.root.after_cancel(self._start_seq_after_id)
            except Exception:
                pass
            self._start_seq_after_id = None
        self.root.unbind("<KeyPress>")
        for widget in self.container.winfo_children():
            widget.destroy()

    def _build_wizard_header(self, step_num, subtitle):
        hdr = tk.Frame(self.container, bg="#181b24", height=64, highlightthickness=1, highlightbackground="#2a2f3d")
        hdr.pack(fill=tk.X, padx=24, pady=(20, 14))
        hdr.pack_propagate(False)

        tk.Label(
            hdr, text="🏁 RACING TYCOON — KREATOR WEEKENDU GP",
            bg="#181b24", fg="#38bdf8", font=("Segoe UI", 13, "bold")
        ).pack(side=tk.LEFT, padx=18)

        steps = ["1. MENU", "2. TOR", "3. ZESPÓŁ", "4. OPONY & START"]
        steps_frame = tk.Frame(hdr, bg="#181b24")
        steps_frame.pack(side=tk.RIGHT, padx=18)

        for idx, s_txt in enumerate(steps, start=1):
            is_curr = idx == step_num
            is_done = idx < step_num
            fg = "#0f1117" if is_curr else ("#4ade80" if is_done else "#64748b")
            bg = "#38bdf8" if is_curr else "#262c3a"
            tk.Label(
                steps_frame, text=s_txt, bg=bg, fg=fg,
                font=("Consolas", 9, "bold"), padx=10, pady=4
            ).pack(side=tk.LEFT, padx=3)

        tk.Label(
            self.container, text=subtitle, bg="#0f1117", fg="#94a3b8",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=26, pady=(0, 12))

    # =========================================================================
    # EKRAN 1: MENU GŁÓWNE
    # =========================================================================
    def _show_main_menu(self):
        self._clear_container()

        wrapper = tk.Frame(self.container, bg="#0f1117")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(wrapper, bg="#181b24", padx=48, pady=40, highlightthickness=1, highlightbackground="#2a2f3d")
        card.pack()

        tk.Label(
            card, text="F1 STRATEGY & RACE SIMULATOR",
            bg="#181b24", fg="#38bdf8", font=("Consolas", 11, "bold")
        ).pack(pady=(0, 6))

        tk.Label(
            card, text="🏁 RACING TYCOON",
            bg="#181b24", fg="#f8fafc", font=("Segoe UI", 28, "bold")
        ).pack(pady=(0, 10))

        tk.Label(
            card,
            text="Wybierz legendarny tor Formuły 1, obejmij dowodzenie nad wybranym zespołem,\n"
                 "dobierz mieszankę opon na polach startowych i poprowadź strategię pit stopów na żywo.",
            bg="#181b24", fg="#94a3b8", font=("Segoe UI", 10), justify="center"
        ).pack(pady=(0, 28))

        tk.Button(
            card, text="🏆  ROZPOCZNIJ WEEKEND GRAND PRIX",
            command=self._show_track_select,
            bg="#0284c7", fg="#ffffff", activebackground="#0369a1", activeforeground="#ffffff",
            font=("Segoe UI", 12, "bold"), relief=tk.FLAT, width=36, pady=12, cursor="hand2"
        ).pack(pady=6)

        tk.Button(
            card, text="⚡  SZYBKI START (Monza • Ferrari • Soft)",
            command=self._quick_start,
            bg="#262c3a", fg="#e2e8f0", activebackground="#334155", activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"), relief=tk.FLAT, width=36, pady=10, cursor="hand2"
        ).pack(pady=6)

        tk.Button(
            card, text="🖥  PRZEŁĄCZ NA TRYB TEKSTOWY (TUI)",
            command=self._request_tui_switch,
            bg="#1e293b", fg="#38bdf8", activebackground="#334155", activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"), relief=tk.FLAT, width=36, pady=10, cursor="hand2"
        ).pack(pady=6)

        tk.Button(
            card, text="✖  WYJŚCIE Z APLIKACJI",
            command=self._quit_without_save,
            bg="#181b24", fg="#94a3b8", activebackground="#262c3a", activeforeground="#ef4444",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, width=36, pady=8, cursor="hand2"
        ).pack(pady=(12, 0))

    def _quick_start(self):
        self.selected_track = "monza"
        self.selected_team = "ferrari"
        self.selected_tire = "Soft"
        self.model.configure_weekend("monza", "ferrari", "Soft")
        self.model.weather = "Słonecznie"
        self._show_race_screen(run_start_lights=True)

    # =========================================================================
    # EKRAN 2: WYBÓR TORU
    # =========================================================================
    def _show_track_select(self):
        self._clear_container()
        self._build_wizard_header(2, "Krok 1 z 3: Wybierz tor Grand Prix — każdy obiekt ma inną długość, degradację opon i ryzyko opadów.")

        grid_frame = tk.Frame(self.container, bg="#0f1117")
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=4)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.rowconfigure(0, weight=1)
        grid_frame.rowconfigure(1, weight=1)

        self._track_cards = {}
        for idx, (tid, tinfo) in enumerate(TRACKS.items()):
            r, c = divmod(idx, 2)
            is_sel = tid == self.selected_track
            border_col = "#38bdf8" if is_sel else "#2a2f3d"

            card = tk.Frame(grid_frame, bg="#181b24", highlightthickness=2, highlightbackground=border_col, cursor="hand2")
            card.grid(row=r, column=c, sticky="nsew", padx=8, pady=8)
            self._track_cards[tid] = card

            inner = tk.Frame(card, bg="#181b24")
            inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=14)

            preview = TrackPreviewCanvas(inner, tid, width=180, height=120)
            preview.pack(side=tk.RIGHT, fill=tk.Y, padx=(12, 0))

            info_box = tk.Frame(inner, bg="#181b24")
            info_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            tk.Label(
                info_box, text=tinfo["name"], bg="#181b24", fg="#f8fafc",
                font=("Segoe UI", 13, "bold"), anchor="w"
            ).pack(fill=tk.X)

            tk.Label(
                info_box,
                text=f"Dystans: {tinfo['laps']} okrążeń  •  Długość: {tinfo['length_km']}",
                bg="#181b24", fg="#38bdf8", font=("Consolas", 10, "bold"), anchor="w"
            ).pack(fill=tk.X, pady=(4, 6))

            tk.Label(
                info_box, text=tinfo["characteristics"], bg="#181b24", fg="#94a3b8",
                font=("Segoe UI", 9), anchor="w", wraplength=340, justify="left"
            ).pack(fill=tk.X, pady=(0, 8))

            wear_pct = int(tinfo["tire_wear_mult"] * 100)
            rain_pct = int(tinfo["rain_chance"] * 100)
            vsc_pct = int(tinfo["vsc_chance"] * 1000)
            tk.Label(
                info_box,
                text=f"Zużycie opon: {wear_pct}%  |  Ryzyko deszczu: {rain_pct}%  |  Ryzyko VSC: {vsc_pct}%",
                bg="#0f1117", fg="#cbd5e1", font=("Consolas", 8, "bold"), padx=8, pady=5, anchor="w"
            ).pack(fill=tk.X, side=tk.BOTTOM)

            self._bind_click_recursive(card, lambda _e, chosen=tid: self._select_track(chosen))

        nav = tk.Frame(self.container, bg="#0f1117")
        nav.pack(fill=tk.X, padx=24, pady=(8, 20))

        tk.Button(
            nav, text="← Powrót do Menu", command=self._show_main_menu,
            bg="#262c3a", fg="#cbd5e1", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=18, pady=10, cursor="hand2"
        ).pack(side=tk.LEFT)

        tk.Button(
            nav, text="DALEJ: WYBÓR ZESPOŁU →", command=self._show_team_select,
            bg="#0284c7", fg="#ffffff", activebackground="#0369a1", activeforeground="#ffffff",
            font=("Segoe UI", 11, "bold"), relief=tk.FLAT, padx=24, pady=10, cursor="hand2"
        ).pack(side=tk.RIGHT)

    def _select_track(self, track_id):
        self.selected_track = track_id
        for tid, card in self._track_cards.items():
            card.config(highlightbackground="#38bdf8" if tid == track_id else "#2a2f3d")

    # =========================================================================
    # EKRAN 3: WYBÓR ZESPOŁU
    # =========================================================================
    def _show_team_select(self):
        self._clear_container()
        track_title = TRACKS[self.selected_track]["name"]
        self._build_wizard_header(3, f"Krok 2 z 3: Wybierz konstruktora F1 na wyścig {track_title}.")

        grid_frame = tk.Frame(self.container, bg="#0f1117")
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=4)
        for c in range(3):
            grid_frame.columnconfigure(c, weight=1)
        grid_frame.rowconfigure(0, weight=1)
        grid_frame.rowconfigure(1, weight=1)

        self._team_cards = {}
        for idx, (team_id, tinfo) in enumerate(TEAMS.items()):
            r, c = divmod(idx, 3)
            is_sel = team_id == self.selected_team
            card = tk.Frame(
                grid_frame, bg="#181b24",
                highlightthickness=2, highlightbackground="#38bdf8" if is_sel else "#2a2f3d",
                cursor="hand2"
            )
            card.grid(row=r, column=c, sticky="nsew", padx=8, pady=8)
            self._team_cards[team_id] = card

            tk.Frame(card, bg=tinfo["color"], height=8).pack(fill=tk.X)

            body = tk.Frame(card, bg="#181b24")
            body.pack(fill=tk.BOTH, expand=True, padx=16, pady=14)

            tk.Label(
                body, text=tinfo["name"], bg="#181b24", fg="#f8fafc",
                font=("Segoe UI", 13, "bold"), anchor="w"
            ).pack(fill=tk.X)

            teammate = [d for d in tinfo["drivers"] if d != tinfo["replaced_driver"]][0]
            tk.Label(
                body,
                text=f"Skład: GRACZ + {teammate}  (zastępujesz: {tinfo['replaced_driver']})",
                bg="#181b24", fg=tinfo["color"], font=("Consolas", 9, "bold"), anchor="w"
            ).pack(fill=tk.X, pady=(4, 8))

            tk.Label(
                body, text=tinfo["trait"], bg="#181b24", fg="#94a3b8",
                font=("Segoe UI", 9), anchor="w", wraplength=310, justify="left"
            ).pack(fill=tk.X, pady=(0, 10))

            spd_txt = f"+{int(tinfo['speed_bonus']*100000)} pkt"
            tire_txt = f"{int((2.0 - tinfo['tire_save_mult'])*100)}%"
            pit_txt = f"{tinfo['pit_duration'] * 0.05:.2f}s"
            tk.Label(
                body,
                text=f"Moc: {spd_txt}  |  Opony: {tire_txt}  |  Pit Stop: ~{pit_txt}",
                bg="#0f1117", fg="#cbd5e1", font=("Consolas", 8, "bold"), padx=8, pady=5, anchor="w"
            ).pack(fill=tk.X, side=tk.BOTTOM)

            self._bind_click_recursive(card, lambda _e, chosen=team_id: self._select_team(chosen))

        nav = tk.Frame(self.container, bg="#0f1117")
        nav.pack(fill=tk.X, padx=24, pady=(8, 20))

        tk.Button(
            nav, text="← Wróć do wyboru toru", command=self._show_track_select,
            bg="#262c3a", fg="#cbd5e1", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=18, pady=10, cursor="hand2"
        ).pack(side=tk.LEFT)

        tk.Button(
            nav, text="DALEJ: POLA STARTOWE I OPONY →", command=self._show_starting_grid,
            bg="#0284c7", fg="#ffffff", activebackground="#0369a1", activeforeground="#ffffff",
            font=("Segoe UI", 11, "bold"), relief=tk.FLAT, padx=24, pady=10, cursor="hand2"
        ).pack(side=tk.RIGHT)

    def _select_team(self, team_id):
        self.selected_team = team_id
        for tid, card in self._team_cards.items():
            card.config(highlightbackground="#38bdf8" if tid == team_id else "#2a2f3d")

    # =========================================================================
    # EKRAN 4: POLA STARTOWE — WYBÓR OPON STARTOWYCH PRZED PROCEDURĄ STARTU
    # =========================================================================
    def _show_starting_grid(self):
        self._clear_container()
        self.model.configure_weekend(self.selected_track, self.selected_team, self.selected_tire)
        weather = self.model.roll_starting_weather()

        if weather == "Deszcz" and self.selected_tire != "Wet":
            self.selected_tire = "Wet"
            self.model.set_starting_compound("Wet")

        track_info = TRACKS[self.selected_track]
        team_info = TEAMS[self.selected_team]
        self._build_wizard_header(
            4,
            f"Krok 3 z 3: Pola startowe — {track_info['name']}  |  Zespół: {team_info['name']}"
        )

        w_colors = {
            "Słonecznie": ("☀ SŁONECZNIE (Suchy tor — 27°C)", "#facc15"),
            "Pochmurno": ("☁ POCHMURNO (Chłodny asfalt — 19°C, możliwe opady)", "#38bdf8"),
            "Deszcz": ("☂ OPADY DESZCZU (Mokry tor — zalecane opony WET!)", "#60a5fa"),
        }
        w_label, w_fg = w_colors.get(weather, (weather, "#f8fafc"))

        weather_banner = tk.Frame(self.container, bg="#181b24", highlightthickness=1, highlightbackground="#2a2f3d")
        weather_banner.pack(fill=tk.X, padx=24, pady=(0, 14))
        tk.Label(
            weather_banner, text=f"PROGNOZA POGODY NA START:   {w_label}",
            bg="#181b24", fg=w_fg, font=("Consolas", 11, "bold"), pady=12
        ).pack()

        tires_frame = tk.Frame(self.container, bg="#0f1117")
        tires_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=4)
        for c in range(3):
            tires_frame.columnconfigure(c, weight=1)
        tires_frame.rowconfigure(0, weight=1)

        tire_specs = [
            (
                "Soft", "🔴 SOFT (MIĘKKIE)", "#ef4444",
                "Maksymalna przyczepność i świetne przyspieszenie na 1. okrążeniu.\n"
                "Szybka degradacja — wymaga wcześniejszego pit stopu.",
                "Przyczepność: ★★★★★  |  Trwałość: ★★☆☆☆"
            ),
            (
                "Hard", "⚪ HARD (TWARDE)", "#f8fafc",
                "Bardzo wysoka wytrzymałość pozwalająca na długi pierwszy stint.\n"
                "Wolniejsze tempo na pierwszych okrążeniach.",
                "Przyczepność: ★★★☆☆  |  Trwałość: ★★★★★"
            ),
            (
                "Wet", "🔵 WET (DESZCZOWE)", "#3b82f6",
                "Głęboki bieżnik odprowadzający wodę podczas ulewy.\n"
                "Na suchym torze ulegają błyskawicznemu przegrzaniu!",
                "Przyczepność (Deszcz): ★★★★★  |  Suchy tor: ★☆☆☆☆"
            ),
        ]

        self._tire_cards = {}
        for idx, (comp, title, color, desc, rating) in enumerate(tire_specs):
            is_sel = comp == self.selected_tire
            card = tk.Frame(
                tires_frame, bg="#181b24",
                highlightthickness=2, highlightbackground="#38bdf8" if is_sel else "#2a2f3d",
                cursor="hand2"
            )
            card.grid(row=0, column=idx, sticky="nsew", padx=8, pady=8)
            self._tire_cards[comp] = card

            tk.Frame(card, bg=color, height=8).pack(fill=tk.X)
            body = tk.Frame(card, bg="#181b24")
            body.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

            tk.Label(body, text=title, bg="#181b24", fg=color, font=("Segoe UI", 14, "bold"), anchor="w").pack(fill=tk.X)
            tk.Label(
                body, text=desc, bg="#181b24", fg="#cbd5e1",
                font=("Segoe UI", 10), anchor="w", justify="left", wraplength=320
            ).pack(fill=tk.X, pady=(12, 16))
            tk.Label(
                body, text=rating, bg="#0f1117", fg="#94a3b8",
                font=("Consolas", 9, "bold"), padx=10, pady=8, anchor="w"
            ).pack(fill=tk.X, side=tk.BOTTOM)

            self._bind_click_recursive(card, lambda _e, chosen=comp: self._select_starting_tire(chosen))

        nav = tk.Frame(self.container, bg="#0f1117")
        nav.pack(fill=tk.X, padx=24, pady=(12, 20))

        tk.Button(
            nav, text="← Wróć do wyboru zespołu", command=self._show_team_select,
            bg="#262c3a", fg="#cbd5e1", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=18, pady=10, cursor="hand2"
        ).pack(side=tk.LEFT)

        tk.Button(
            nav, text="🚦 USTAW NA POLACH STARTOWYCH I ROZPOCZNIJ START",
            command=self._launch_race_with_lights,
            bg="#16a34a", fg="#ffffff", activebackground="#15803d", activeforeground="#ffffff",
            font=("Segoe UI", 11, "bold"), relief=tk.FLAT, padx=24, pady=11, cursor="hand2"
        ).pack(side=tk.RIGHT)

    def _select_starting_tire(self, comp):
        self.selected_tire = comp
        self.model.set_starting_compound(comp)
        for c_id, card in self._tire_cards.items():
            card.config(highlightbackground="#38bdf8" if c_id == comp else "#2a2f3d")

    def _launch_race_with_lights(self):
        self.model.set_starting_compound(self.selected_tire)
        self._show_race_screen(run_start_lights=True)

    def _bind_click_recursive(self, widget, callback):
        widget.bind("<Button-1>", callback)
        for child in widget.winfo_children():
            self._bind_click_recursive(child, callback)

    # =========================================================================
    # EKRAN 5: WYŚCIG + SEKWENCJA 5 CZERWONYCH ŚWIATEŁ F1
    # =========================================================================
    def _show_race_screen(self, run_start_lights=True):
        self._clear_container()
        self._build_race_ui()
        self._bind_race_keys()

        self.root.update_idletasks()
        self.track_canvas.draw_static_track()
        self._refresh_view()

        if run_start_lights and not self.model.race_started:
            self._start_lights_sequence(step=1)
        else:
            self.lights_banner.pack_forget()
            self._tick()

    def _start_lights_sequence(self, step):
        if not self._running:
            return
        if step <= 5:
            self.model.set_start_lights(step)
            self._update_lights_visual(step, "PROCEDURA STARTU — ZGAŚNIĘCIE ŚWIATEŁ ZA CHWILĘ...")
            self._refresh_view()
            self._start_seq_after_id = self.root.after(650, lambda: self._start_lights_sequence(step + 1))
        else:
            random_hold_ms = random.randint(600, 1500)
            self._update_lights_visual(5, "WSZYSTKIE ŚWIATŁA ZAPALONE — GOTOWOŚĆ!")
            self._start_seq_after_id = self.root.after(random_hold_ms, self._lights_out_go)

    def _lights_out_go(self):
        if not self._running:
            return
        self._update_lights_visual(0, "🟢 LIGHTS OUT AND AWAY WE GO! 🟢")
        self.model.begin_race()
        self._refresh_view()
        self._tick()
        self._start_seq_after_id = self.root.after(1800, self._hide_lights_banner)

    def _hide_lights_banner(self):
        try:
            if hasattr(self, "lights_banner") and self.lights_banner.winfo_exists():
                self.lights_banner.pack_forget()
        except Exception:
            pass

    def _update_lights_visual(self, lit_count, caption):
        if not hasattr(self, "light_bulbs"):
            return
        for idx, bulb in enumerate(self.light_bulbs):
            is_on = idx < lit_count
            bulb.config(
                fg="#ef4444" if is_on else "#262c3a",
                text="●"
            )
        self.lbl_lights_caption.config(
            text=caption,
            fg="#4ade80" if lit_count == 0 else "#facc15"
        )

    def _build_race_ui(self):
        header = tk.Frame(self.container, bg="#181b24", height=56, highlightthickness=1, highlightbackground="#2a2f3d")
        header.pack(fill=tk.X, padx=12, pady=(12, 8))
        header.pack_propagate(False)

        tk.Label(
            header, text=f"🏁 {self.model.track_name.upper()}",
            bg="#181b24", fg="#38bdf8", font=("Segoe UI", 12, "bold")
        ).pack(side=tk.LEFT, padx=(16, 10))

        tk.Label(
            header, text=f"  {self.model.team_name.upper()}  ",
            bg=self.model.team_color, fg="#0f1117", font=("Consolas", 9, "bold"), pady=3
        ).pack(side=tk.LEFT, padx=6)

        tk.Button(
            header, text="← Menu Główne",
            command=self._return_to_menu,
            bg="#262c3a", fg="#e2e8f0", activebackground="#334155", activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=6, cursor="hand2"
        ).pack(side=tk.RIGHT, padx=(6, 14))

        self.btn_switch_mode = tk.Button(
            header, text="🖥 Tryb TUI [M]",
            command=self._request_tui_switch,
            bg="#0284c7", fg="#ffffff", activebackground="#0369a1", activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=6, cursor="hand2"
        )
        self.btn_switch_mode.pack(side=tk.RIGHT, padx=4)

        self.lbl_vsc = tk.Label(
            header, text="", bg="#181b24", fg="#facc15", font=("Consolas", 10, "bold")
        )
        self.lbl_vsc.pack(side=tk.RIGHT, padx=12)

        body = tk.Frame(self.container, bg="#0f1117")
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        left_col = tk.Frame(body, bg="#0f1117", width=370)
        left_col.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_col.pack_propagate(False)

        self._build_status_card(left_col)
        self._build_resources_card(left_col)
        self._build_strategy_card(left_col)
        self._build_sectors_card(left_col)
        self._build_session_controls(left_col)

        center_col = tk.Frame(body, bg="#0f1117")
        center_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.lights_banner = tk.Frame(center_col, bg="#181b24", highlightthickness=1, highlightbackground="#ef4444")
        self.lights_banner.pack(fill=tk.X, pady=(0, 8))

        bulbs_row = tk.Frame(self.lights_banner, bg="#181b24")
        bulbs_row.pack(pady=(6, 0))
        self.light_bulbs = []
        for _ in range(5):
            b = tk.Label(bulbs_row, text="●", bg="#181b24", fg="#262c3a", font=("Segoe UI", 22, "bold"))
            b.pack(side=tk.LEFT, padx=8)
            self.light_bulbs.append(b)

        self.lbl_lights_caption = tk.Label(
            self.lights_banner, text="USTAWIANIE NA POLACH STARTOWYCH...",
            bg="#181b24", fg="#facc15", font=("Consolas", 9, "bold")
        )
        self.lbl_lights_caption.pack(pady=(0, 6))

        self.track_canvas = CircuitTrackCanvas(center_col, track_id=self.model.track_id)
        self.track_canvas.pack(fill=tk.BOTH, expand=True)

        right_col = tk.Frame(body, bg="#181b24", width=295, highlightthickness=1, highlightbackground="#2a2f3d")
        right_col.pack(side=tk.RIGHT, fill=tk.Y)
        right_col.pack_propagate(False)

        self._build_timing_tower(right_col)

    def _make_card(self, parent, title):
        card = tk.Frame(parent, bg="#181b24", highlightthickness=1, highlightbackground="#2a2f3d")
        card.pack(fill=tk.X, pady=(0, 8))
        tk.Label(
            card, text=title, bg="#181b24", fg="#38bdf8",
            font=("Consolas", 9, "bold"), anchor="w"
        ).pack(fill=tk.X, padx=12, pady=(8, 4))
        return card

    def _build_status_card(self, parent):
        card = self._make_card(parent, "STATUS WYŚCIGU")
        row1 = tk.Frame(card, bg="#181b24")
        row1.pack(fill=tk.X, padx=12, pady=2)

        self.lbl_lap = tk.Label(row1, text=f"Okrążenie: 0/{self.model.max_laps}", bg="#181b24", fg="#f8fafc", font=("Segoe UI", 11, "bold"))
        self.lbl_lap.pack(side=tk.LEFT)

        self.lbl_weather = tk.Label(row1, text="☀ Słonecznie", bg="#181b24", fg="#facc15", font=("Segoe UI", 10, "bold"))
        self.lbl_weather.pack(side=tk.RIGHT)

        self.lbl_status = tk.Label(
            card, text="Status: Oczekiwanie na start", bg="#181b24", fg="#4ade80",
            font=("Consolas", 9, "bold"), anchor="w"
        )
        self.lbl_status.pack(fill=tk.X, padx=12, pady=(4, 10))

    def _build_resources_card(self, parent):
        card = self._make_card(parent, "STAN BOLIDU")

        tire_hdr = tk.Frame(card, bg="#181b24")
        tire_hdr.pack(fill=tk.X, padx=12, pady=(2, 2))
        self.lbl_tire_title = tk.Label(tire_hdr, text="Zużycie Opon", bg="#181b24", fg="#cbd5e1", font=("Segoe UI", 9))
        self.lbl_tire_title.pack(side=tk.LEFT)
        self.lbl_tire_val = tk.Label(tire_hdr, text="100.0%", bg="#181b24", fg="#4ade80", font=("Consolas", 9, "bold"))
        self.lbl_tire_val.pack(side=tk.RIGHT)

        self.bar_tire = tk.Canvas(card, height=14, bg="#0f1117", highlightthickness=0)
        self.bar_tire.pack(fill=tk.X, padx=12, pady=(0, 8))

        fuel_hdr = tk.Frame(card, bg="#181b24")
        fuel_hdr.pack(fill=tk.X, padx=12, pady=(2, 2))
        tk.Label(fuel_hdr, text="Stan Paliwa", bg="#181b24", fg="#cbd5e1", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.lbl_fuel_val = tk.Label(fuel_hdr, text="100.0%", bg="#181b24", fg="#4ade80", font=("Consolas", 9, "bold"))
        self.lbl_fuel_val.pack(side=tk.RIGHT)

        self.bar_fuel = tk.Canvas(card, height=14, bg="#0f1117", highlightthickness=0)
        self.bar_fuel.pack(fill=tk.X, padx=12, pady=(0, 10))

    def _build_strategy_card(self, parent):
        card = self._make_card(parent, "STRATEGIA OPON I TRYB SILNIKA")

        tires_info = tk.Frame(card, bg="#181b24")
        tires_info.pack(fill=tk.X, padx=12, pady=(2, 6))

        tk.Label(tires_info, text="Obecne:", bg="#181b24", fg="#94a3b8", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.lbl_curr_tire = tk.Label(tires_info, text=self.model.compound, bg="#181b24", fg="#ef4444", font=("Consolas", 10, "bold"))
        self.lbl_curr_tire.pack(side=tk.LEFT, padx=(4, 16))

        tk.Label(tires_info, text="Na zjazd:", bg="#181b24", fg="#94a3b8", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.lbl_next_tire = tk.Label(tires_info, text=self.model.next_compound, bg="#181b24", fg="#ef4444", font=("Consolas", 10, "bold"))
        self.lbl_next_tire.pack(side=tk.LEFT, padx=4)

        pit_btns = tk.Frame(card, bg="#181b24")
        pit_btns.pack(fill=tk.X, padx=12, pady=(0, 8))

        self.btn_cycle_tire = tk.Button(
            pit_btns, text="[T] Zmień opony", command=self.model.cycle_tires,
            bg="#262c3a", fg="#f8fafc", activebackground="#334155", activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, pady=5, cursor="hand2"
        )
        self.btn_cycle_tire.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_pitstop = tk.Button(
            pit_btns, text="[P] Zaplanuj Pit Stop", command=self.model.call_pitstop,
            bg="#262c3a", fg="#f8fafc", activebackground="#334155", activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, pady=5, cursor="hand2"
        )
        self.btn_pitstop.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

        eng_frame = tk.Frame(card, bg="#181b24")
        eng_frame.pack(fill=tk.X, padx=12, pady=(0, 10))

        self.engine_buttons = {}
        for idx, (mode, label) in enumerate([("Eco", "[1] Eco"), ("Standard", "[2] Standard"), ("Push", "[3] Push")]):
            btn = tk.Button(
                eng_frame, text=label,
                command=lambda m=mode: self.model.set_engine_mode(m),
                bg="#262c3a", fg="#cbd5e1", font=("Segoe UI", 8, "bold"),
                relief=tk.FLAT, pady=5, cursor="hand2"
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0 if idx == 0 else 3, 0))
            self.engine_buttons[mode] = btn

    def _build_sectors_card(self, parent):
        card = self._make_card(parent, "CZASY OKRĄŻEŃ I SEKTORÓW")

        laps_row = tk.Frame(card, bg="#181b24")
        laps_row.pack(fill=tk.X, padx=12, pady=(2, 6))

        self.lbl_last_lap = tk.Label(laps_row, text="Ostatnie: --.--- s", bg="#181b24", fg="#e2e8f0", font=("Consolas", 9))
        self.lbl_last_lap.pack(side=tk.LEFT)

        self.lbl_best_lap = tk.Label(laps_row, text="Best: --.--- s", bg="#181b24", fg="#c084fc", font=("Consolas", 9, "bold"))
        self.lbl_best_lap.pack(side=tk.RIGHT)

        sec_row = tk.Frame(card, bg="#181b24")
        sec_row.pack(fill=tk.X, padx=12, pady=(0, 10))

        self.sector_labels = []
        for i in range(3):
            lbl = tk.Label(
                sec_row, text=f"S{i+1}: --.--s", bg="#0f1117", fg="#94a3b8",
                font=("Consolas", 9, "bold"), pady=5
            )
            lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0 if i == 0 else 4, 0))
            self.sector_labels.append(lbl)

    def _build_session_controls(self, parent):
        frame = tk.Frame(parent, bg="#0f1117")
        frame.pack(fill=tk.X, pady=(2, 0))

        self.btn_pause = tk.Button(
            frame, text="[SPACJA] Pauza", command=self.model.toggle_pause,
            bg="#ca8a04", fg="#ffffff", activebackground="#a16207", activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, pady=7, cursor="hand2"
        )
        self.btn_pause.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_quit = tk.Button(
            frame, text="[Q] Zakończ i zapisz", command=self._on_close,
            bg="#dc2626", fg="#ffffff", activebackground="#b91c1c", activeforeground="#ffffff",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, pady=7, cursor="hand2"
        )
        self.btn_quit.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

    def _build_timing_tower(self, parent):
        tk.Label(
            parent, text="🏁 TABELA WYNIKÓW (20)", bg="#181b24", fg="#38bdf8",
            font=("Consolas", 10, "bold")
        ).pack(fill=tk.X, padx=10, pady=(10, 4))

        hdr = tk.Frame(parent, bg="#262c3a")
        hdr.pack(fill=tk.X, padx=8, pady=(0, 4))
        tk.Label(hdr, text=" POZ | KIEROWCA | STRATA", bg="#262c3a", fg="#94a3b8", font=("Consolas", 9, "bold"), anchor="w").pack(fill=tk.X, pady=3)

        self.tower_rows = []
        for _ in range(20):
            row_frame = tk.Frame(parent, bg="#181b24")
            row_frame.pack(fill=tk.X, padx=8, pady=1)

            badge = tk.Label(row_frame, text=" ", bg="#38bdf8", width=1)
            badge.pack(side=tk.LEFT, fill=tk.Y)

            lbl = tk.Label(
                row_frame, text="", bg="#181b24", fg="#e2e8f0",
                font=("Consolas", 9), anchor="w", padx=6
            )
            lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.tower_rows.append((row_frame, badge, lbl))

    def _bind_race_keys(self):
        self.root.bind("<KeyPress>", self._on_key_press)

    def _on_key_press(self, event):
        k = event.keysym.lower()
        if k == "q":
            self._on_close()
        elif k == "p":
            self.model.call_pitstop()
        elif k == "t":
            self.model.cycle_tires()
        elif k == "1":
            self.model.set_engine_mode("Eco")
        elif k == "2":
            self.model.set_engine_mode("Standard")
        elif k == "3":
            self.model.set_engine_mode("Push")
        elif k == "space":
            self.model.toggle_pause()
        elif k == "m":
            self._request_tui_switch()

    def _draw_bar(self, canvas, pct, color):
        canvas.delete("all")
        w = max(canvas.winfo_width(), 200)
        h = max(canvas.winfo_height(), 14)
        fill_w = int((max(0.0, min(100.0, pct)) / 100.0) * w)
        canvas.create_rectangle(0, 0, fill_w, h, fill=color, width=0)

    def _refresh_view(self):
        if not hasattr(self, "lbl_lap") or not self.lbl_lap.winfo_exists():
            return

        m = self.model
        self.lbl_lap.config(text=f"Okrążenie: {m.laps}/{m.max_laps}")

        w_map = {
            "Słonecznie": ("☀ Słonecznie", "#facc15"),
            "Pochmurno": ("☁ Pochmurno", "#38bdf8"),
            "Deszcz": ("☂ Deszcz", "#60a5fa"),
        }
        w_txt, w_col = w_map.get(m.weather, (m.weather, "#f8fafc"))
        self.lbl_weather.config(text=w_txt, fg=w_col)

        if "PAUZA" in m.status:
            s_col = "#facc15"
            self.btn_pause.config(text="[SPACJA] Wznów", bg="#16a34a")
        elif "DNF" in m.status or "PIT STOP" in m.status or "PROCEDURA" in m.status:
            s_col = "#ef4444"
            self.btn_pause.config(text="[SPACJA] Pauza", bg="#ca8a04")
        elif "Zjazd" in m.status:
            s_col = "#fb923c"
            self.btn_pause.config(text="[SPACJA] Pauza", bg="#ca8a04")
        else:
            s_col = "#4ade80"
            self.btn_pause.config(text="[SPACJA] Pauza", bg="#ca8a04")
        self.lbl_status.config(text=f"Status: {m.status}", fg=s_col)

        self.lbl_vsc.config(text="⚠ VSC — ZWOLNIJ! ⚠" if m.vsc_active else "")

        tire_col = "#4ade80" if m.tire_wear > 50 else ("#facc15" if m.tire_wear > 20 else "#ef4444")
        fuel_col = "#4ade80" if m.fuel > 40 else ("#facc15" if m.fuel > 20 else "#ef4444")
        self.lbl_tire_title.config(
            text="Zużycie Opon" if m.tire_wear > 0 else "KAPEĆ (Zwolnij!)",
            fg=tire_col if m.tire_wear <= 20 else "#cbd5e1"
        )
        self.lbl_tire_val.config(text=f"{m.tire_wear:5.1f}%", fg=tire_col)
        self.lbl_fuel_val.config(text=f"{m.fuel:5.1f}%", fg=fuel_col)
        self._draw_bar(self.bar_tire, m.tire_wear, tire_col)
        self._draw_bar(self.bar_fuel, m.fuel, fuel_col)

        comp_colors = {"Soft": "#ef4444", "Hard": "#f8fafc", "Wet": "#3b82f6"}
        self.lbl_curr_tire.config(text=m.compound, fg=comp_colors.get(m.compound, "#f8fafc"))
        self.lbl_next_tire.config(text=m.next_compound, fg=comp_colors.get(m.next_compound, "#f8fafc"))

        if m.pit_requested:
            self.btn_pitstop.config(text="[P] Zjazd zaplanowany!", bg="#d97706", fg="#ffffff")
        else:
            self.btn_pitstop.config(text="[P] Zaplanuj Pit Stop", bg="#262c3a", fg="#f8fafc")

        eng_active_colors = {"Eco": "#16a34a", "Standard": "#0284c7", "Push": "#dc2626"}
        for mode, btn in self.engine_buttons.items():
            if m.engine_mode == mode:
                btn.config(bg=eng_active_colors[mode], fg="#ffffff")
            else:
                btn.config(bg="#262c3a", fg="#94a3b8")

        last_str = f"{m.last_lap_time:.3f} s" if m.last_lap_time > 0 else "--.--- s"
        best_str = f"{m.best_lap_time:.3f} s" if m.best_lap_time < 900 else "--.--- s"
        self.lbl_last_lap.config(text=f"Ostatnie: {last_str}")
        self.lbl_best_lap.config(text=f"Best: {best_str}")

        sec_color_map = {0: "#94a3b8", 1: "#4ade80", 2: "#facc15", 5: "#c084fc"}
        for i in range(3):
            t_txt = f"{m.sectors[i]:.2f}s" if m.sectors[i] > 0 else "--.--s"
            self.sector_labels[i].config(text=f"S{i+1}: {t_txt}", fg=sec_color_map.get(m.sector_colors[i], "#94a3b8"))

        self.track_canvas.render_cars(m)

        standings = m.get_standings()
        for i, driver in enumerate(standings[:20]):
            row_frame, badge, lbl = self.tower_rows[i]
            t_col = TEAM_COLORS_MAP.get(driver.get("team", ""), "#64748b")
            badge.config(bg=t_col)
            line = f" {driver['pos']:2d}  | {driver['name']:<8} | {driver['gap']:<9}"
            if driver["is_player"]:
                row_frame.config(bg="#3b0764")
                lbl.config(text=line, bg="#3b0764", fg="#f0abfc", font=("Consolas", 9, "bold"))
            else:
                row_frame.config(bg="#181b24")
                lbl.config(text=line, bg="#181b24", fg="#e2e8f0", font=("Consolas", 9))

    def _tick(self):
        if not self._running or not hasattr(self, "lbl_lap") or not self.lbl_lap.winfo_exists():
            return
        if "Koniec" not in self.model.status and "DNF" not in self.model.status:
            self.model.update()
        self._refresh_view()
        self.root.after(50, self._tick)

    def _return_to_menu(self):
        self.save_telemetry()
        self.model = RaceModel(self.selected_track, self.selected_team, self.selected_tire)
        self._show_main_menu()

    def _request_tui_switch(self):
        self.switch_to_tui = True
        self._running = False
        self.root.destroy()

    def _quit_without_save(self):
        self.switch_to_tui = False
        self._running = False
        self.root.destroy()

    def _on_close(self):
        self.switch_to_tui = False
        self._running = False
        if self.model.race_started:
            self.save_telemetry()
        self.root.destroy()

    def save_telemetry(self):
        data = {
            "track": self.model.track_name,
            "team": self.model.team_name,
            "completed_laps": self.model.laps,
            "best_lap_time": self.model.best_lap_time,
            "final_standings": self.model.get_standings(),
        }
        with open("race_telemetry.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def run(self):
        self.root.mainloop()
        return self.switch_to_tui


def run_application(start_mode="gui", shared_model=None):
    """Pętla przełączająca tryby GUI <-> TUI bez utraty instancji RaceModel."""
    model = shared_model if shared_model is not None else RaceModel()
    mode = start_mode
    came_from_tui = False

    while True:
        if mode == "gui":
            gui = GuiController(model=model, skip_menu=came_from_tui)
            to_tui = gui.run()
            if to_tui:
                mode = "tui"
                continue
            break
        elif mode == "tui":
            from app_tui import Controller as TuiController

            switch_flag = {"to_gui": False}

            def _tui_entry(stdscr):
                tui = TuiController(stdscr, model=model)
                tui.run()
                switch_flag["to_gui"] = tui.switch_to_gui

            try:
                curses.wrapper(_tui_entry)
            except RuntimeError as e:
                print(f"\n[BŁĄD INTERFEJSU TUI]: {e}")
                print("Powrót do trybu graficznego (GUI)...\n")
                mode = "gui"
                came_from_tui = True
                continue

            if switch_flag["to_gui"]:
                mode = "gui"
                came_from_tui = True
                continue
            break


if __name__ == "__main__":
    run_application(start_mode="gui")