import random

TRACKS = {
    "monza": {
        "id": "monza",
        "name": "GP Włoch — Monza",
        "short_name": "MONZA",
        "country": "Włochy",
        "laps": 53,
        "length_km": "5.793 km",
        "characteristics": "Świątynia Prędkości • Niskie zużycie opon • Długie proste",
        "tire_wear_mult": 0.85,
        "rain_chance": 0.20,
        "vsc_chance": 0.04,
        "base_step": 0.00345,
    },
    "silverstone": {
        "id": "silverstone",
        "name": "GP Wielkiej Brytanii — Silverstone",
        "short_name": "SILVERSTONE",
        "country": "Wielka Brytania",
        "laps": 52,
        "length_km": "5.891 km",
        "characteristics": "Szybkie zakręty Maggotts-Becketts • Wysokie zużycie opon • Zmienna pogoda",
        "tire_wear_mult": 1.30,
        "rain_chance": 0.45,
        "vsc_chance": 0.05,
        "base_step": 0.00330,
    },
    "spa": {
        "id": "spa",
        "name": "GP Belgii — Spa-Francorchamps",
        "short_name": "SPA",
        "country": "Belgia",
        "laps": 44,
        "length_km": "7.004 km",
        "characteristics": "Eau Rouge / Raidillon • Bardzo długie okrążenie • Wysokie ryzyko deszczu",
        "tire_wear_mult": 1.10,
        "rain_chance": 0.60,
        "vsc_chance": 0.06,
        "base_step": 0.00295,
    },
    "monaco": {
        "id": "monaco",
        "name": "GP Monako — Circuit de Monaco",
        "short_name": "MONAKO",
        "country": "Monako",
        "laps": 78,
        "length_km": "3.337 km",
        "characteristics": "Tor uliczny • Minimalne zużycie opon • Bardzo częste VSC",
        "tire_wear_mult": 0.65,
        "rain_chance": 0.15,
        "vsc_chance": 0.12,
        "base_step": 0.00365,
    },
}

TEAMS = {
    "redbull": {
        "id": "redbull",
        "name": "Red Bull Racing",
        "short_name": "RBR",
        "color": "#3671C6",
        "accent": "#FCD700",
        "drivers": ["VER", "LAW"],
        "replaced_driver": "LAW",
        "trait": "Ekspresowy Pit Stop i wysoka efektywność aero",
        "speed_bonus": 0.00008,
        "tire_save_mult": 0.96,
        "pit_duration": 85,
    },
    "ferrari": {
        "id": "ferrari",
        "name": "Scuderia Ferrari",
        "short_name": "FER",
        "color": "#E80020",
        "accent": "#FFF200",
        "drivers": ["LEC", "HAM"],
        "replaced_driver": "HAM",
        "trait": "Najwyższa moc jednostki napędowej na prostych",
        "speed_bonus": 0.00010,
        "tire_save_mult": 1.00,
        "pit_duration": 95,
    },
    "mclaren": {
        "id": "mclaren",
        "name": "McLaren F1 Team",
        "short_name": "MCL",
        "color": "#FF8000",
        "accent": "#47C7FC",
        "drivers": ["NOR", "PIA"],
        "replaced_driver": "PIA",
        "trait": "Doskonałe zarządzanie temperaturą i zużyciem opon",
        "speed_bonus": 0.00007,
        "tire_save_mult": 0.88,
        "pit_duration": 92,
    },
    "mercedes": {
        "id": "mercedes",
        "name": "Mercedes-AMG F1",
        "short_name": "MER",
        "color": "#27F4D2",
        "accent": "#FFFFFF",
        "drivers": ["RUS", "ANT"],
        "replaced_driver": "ANT",
        "trait": "Stabilne tempo wyścigowe w zmiennych warunkach",
        "speed_bonus": 0.00006,
        "tire_save_mult": 0.93,
        "pit_duration": 95,
    },
    "aston": {
        "id": "aston",
        "name": "Aston Martin F1",
        "short_name": "AST",
        "color": "#229971",
        "accent": "#CEDC00",
        "drivers": ["ALO", "STR"],
        "replaced_driver": "STR",
        "trait": "Świetna trakcja na wyjściach z wolnych zakrętów",
        "speed_bonus": 0.00003,
        "tire_save_mult": 0.94,
        "pit_duration": 100,
    },
    "williams": {
        "id": "williams",
        "name": "Williams Racing",
        "short_name": "WIL",
        "color": "#64C4FF",
        "accent": "#FFFFFF",
        "drivers": ["SAI", "ALB"],
        "replaced_driver": "ALB",
        "trait": "Niski opór aerodynamiczny i wysoka prędkość maksymalna",
        "speed_bonus": 0.00005,
        "tire_save_mult": 1.02,
        "pit_duration": 102,
    },
}

ALL_GRID_DRIVERS = [
    ("VER", "redbull"), ("LAW", "redbull"),
    ("LEC", "ferrari"), ("HAM", "ferrari"),
    ("NOR", "mclaren"), ("PIA", "mclaren"),
    ("RUS", "mercedes"), ("ANT", "mercedes"),
    ("ALO", "aston"), ("STR", "aston"),
    ("SAI", "williams"), ("ALB", "williams"),
    ("TSU", "rb"), ("HAD", "rb"),
    ("GAS", "alpine"), ("DOO", "alpine"),
    ("HUL", "sauber"), ("BOR", "sauber"),
    ("OCO", "haas"), ("BEA", "haas"),
]


class RaceModel:
    def __init__(self, track_id="monza", team_id="ferrari", starting_compound="Soft"):
        self.track_id = track_id if track_id in TRACKS else "monza"
        self.team_id = team_id if team_id in TEAMS else "ferrari"
        self.starting_compound = starting_compound if starting_compound in ["Soft", "Hard", "Wet"] else "Soft"
        self.reset_race()

    def configure_weekend(self, track_id=None, team_id=None, starting_compound=None):
        if track_id in TRACKS:
            self.track_id = track_id
        if team_id in TEAMS:
            self.team_id = team_id
        if starting_compound in ["Soft", "Hard", "Wet"]:
            self.starting_compound = starting_compound
        self.reset_race()

    def roll_starting_weather(self):
        """Losuje warunki pogodowe na polach startowych zgodnie z charakterystyką wybranego toru."""
        rain_prob = TRACKS[self.track_id]["rain_chance"]
        r = random.random()
        if r < rain_prob * 0.45:
            self.weather = "Deszcz"
        elif r < rain_prob + 0.25:
            self.weather = "Pochmurno"
        else:
            self.weather = "Słonecznie"
        return self.weather

    def set_starting_compound(self, compound):
        if compound in ["Soft", "Hard", "Wet"]:
            self.starting_compound = compound
            self.compound = compound
            self.next_compound = compound

    def reset_race(self):
        track = TRACKS[self.track_id]
        team = TEAMS[self.team_id]

        self.track_name = track["name"]
        self.team_name = team["name"]
        self.team_color = team["color"]
        self.team_short = team["short_name"]

        self.laps = 0
        self.max_laps = track["laps"]
        self.tire_wear = 100.0
        self.fuel = 100.0

        self.race_started = False
        self.start_lights = 0  # 0..5 zapalonych czerwonych świateł przed startem
        self.status = "Na polach startowych — Oczekiwanie na światła"
        self.pit_requested = False
        self.in_pit = False
        self.pit_timer = 0
        self.lap_progress = 0.0
        self.lap_timer = 0.0
        self.is_paused = False
        self.saved_status = ""

        if not hasattr(self, "weather") or self.weather is None:
            self.weather = "Słonecznie"
        self.weather_timer = random.randint(300, 800)
        self.vsc_active = False
        self.vsc_timer = 100

        self.compound = self.starting_compound
        self.next_compound = self.starting_compound
        self.engine_mode = "Standard"

        self.last_lap_time = 0.0
        self.best_lap_time = 999.9
        self.current_sector = 0
        self.sectors = [0.0, 0.0, 0.0]
        self.best_sectors = [999.9, 999.9, 999.9]
        self.sector_colors = [0, 0, 0]

        # Generowanie 19 botów (zastępujemy 1 kierowcę w wybranym przez gracza zespole)
        replaced = team["replaced_driver"]
        base_step = track["base_step"]
        pit_1 = max(10, int(self.max_laps * 0.36))
        pit_2 = max(pit_1 + 10, int(self.max_laps * 0.72))

        self.bots = []
        for drv_name, drv_team in ALL_GRID_DRIVERS:
            if drv_name == replaced:
                continue
            self.bots.append({
                "name": drv_name,
                "team": drv_team,
                "progress": 0.0,
                "speed": random.uniform(base_step * 0.985, base_step * 1.025),
                "last_lap": 0,
                "pit_strategy": [
                    random.randint(pit_1 - 3, pit_1 + 3),
                    random.randint(pit_2 - 3, pit_2 + 3),
                ],
                "pit_timer": 0,
            })

    def set_start_lights(self, count):
        self.start_lights = max(0, min(5, count))
        if not self.race_started:
            if self.start_lights == 0:
                self.status = "Na polach startowych — Gotowy"
            else:
                self.status = f"PROCEDURA STARTU: {'●' * self.start_lights}{'○' * (5 - self.start_lights)}"

    def begin_race(self):
        self.start_lights = 0
        self.race_started = True
        self.status = "LIGHTS OUT! Wyścig wystartował!"

    def update(self):
        if not self.race_started or self.is_paused:
            return

        if self.laps >= self.max_laps:
            self.status = "Koniec wyścigu!"
            self.lap_progress = 0.0
            return

        self._update_weather_and_events()
        self._update_bots()

        if self.in_pit:
            self.pit_timer -= 1
            self.status = f"PIT STOP ({self.pit_timer})"
            if self.pit_timer <= 0:
                self.in_pit = False
                self.compound = self.next_compound
                self.tire_wear = 100.0
                self.status = "Wyjazd z boksu!"
                self.lap_progress = 0.0
                self.lap_timer = 0.0
                self.current_sector = 0
        else:
            self._process_driving()

    def _process_driving(self):
        track = TRACKS[self.track_id]
        team = TEAMS[self.team_id]

        if self.pit_requested:
            self.status = "Zjazd do PIT (IN-LAP)"
        elif self.vsc_active:
            self.status = "VSC - ZWOLNIJ!"
        else:
            self.status = f"Na torze | Silnik: {self.engine_mode}"

        step = track["base_step"] + team["speed_bonus"]

        compound_speed = {"Soft": 0.0004, "Hard": -0.0001, "Wet": -0.0008}
        if self.weather == "Deszcz":
            if self.compound == "Wet":
                compound_speed["Wet"] = 0.00055
            else:
                compound_speed[self.compound] = -0.0015
        step += compound_speed.get(self.compound, 0)

        fuel_bonus = ((100.0 - self.fuel) / 100.0) * 0.0004
        step += fuel_bonus

        if self.tire_wear <= 0:
            self.tire_wear = 0.0
            tire_penalty = 0.0025
        else:
            tire_penalty = ((100.0 - self.tire_wear) / 100.0) * 0.0006
        step -= tire_penalty

        if self.engine_mode == "Eco":
            step -= 0.0004
        elif self.engine_mode == "Push":
            step += 0.0005

        if self.vsc_active:
            step *= 0.6

        base_deg = {"Soft": 0.018, "Hard": 0.009, "Wet": 0.014}
        if self.weather != "Deszcz" and self.compound == "Wet":
            base_deg["Wet"] = 0.1

        engine_wear_mult = {"Eco": 0.6, "Standard": 1.0, "Push": 1.6}
        total_wear_mult = track["tire_wear_mult"] * team["tire_save_mult"] * engine_wear_mult[self.engine_mode]
        self.tire_wear -= base_deg[self.compound] * total_wear_mult

        fuel_consumption = {"Eco": 0.004, "Standard": 0.006, "Push": 0.010}
        self.fuel -= fuel_consumption[self.engine_mode]

        if self.fuel <= 0:
            self.status = "DNF - Brak paliwa!"
            return

        self.lap_progress += max(0.0005, step + random.uniform(-0.0001, 0.0001))
        self.lap_timer += 0.05

        self._record_sectors()

        if self.lap_progress >= 1.0:
            self.lap_progress = 0.0
            self.last_lap_time = self.lap_timer
            if self.lap_timer < self.best_lap_time:
                self.best_lap_time = self.lap_timer

            self.laps += 1
            self.lap_timer = 0.0
            self.current_sector = 0

            if self.pit_requested and self.laps < self.max_laps:
                self.in_pit = True
                self.pit_requested = False
                self.pit_timer = team["pit_duration"]

    def _record_sectors(self):
        if self.lap_progress >= 0.33 and self.current_sector == 0:
            self.sectors[0] = self.lap_timer
            self._eval_sector(0)
            self.current_sector = 1
        elif self.lap_progress >= 0.66 and self.current_sector == 1:
            self.sectors[1] = self.lap_timer - self.sectors[0]
            self._eval_sector(1)
            self.current_sector = 2
        elif self.lap_progress >= 1.0 and self.current_sector == 2:
            self.sectors[2] = self.lap_timer - (self.sectors[0] + self.sectors[1])
            self._eval_sector(2)

    def _eval_sector(self, idx):
        t = self.sectors[idx]
        if t < self.best_sectors[idx]:
            self.sector_colors[idx] = 5
            self.best_sectors[idx] = t
        elif t < self.best_sectors[idx] + 0.5:
            self.sector_colors[idx] = 1
        else:
            self.sector_colors[idx] = 2

    def _update_weather_and_events(self):
        track = TRACKS[self.track_id]
        rain_bias = track["rain_chance"]

        self.weather_timer -= 1
        if self.weather_timer <= 0:
            self.weather_timer = random.randint(250, 600)
            if self.weather == "Słonecznie":
                cloud_w = int(rain_bias * 60)
                self.weather = random.choices(["Słonecznie", "Pochmurno"], [100 - cloud_w, cloud_w])[0]
            elif self.weather == "Pochmurno":
                rain_w = int(rain_bias * 75)
                sun_w = max(15, 70 - rain_w)
                self.weather = random.choices(["Słonecznie", "Pochmurno", "Deszcz"], [sun_w, 30, rain_w])[0]
            elif self.weather == "Deszcz":
                stay_rain = int(40 + rain_bias * 40)
                self.weather = random.choices(["Pochmurno", "Deszcz"], [100 - stay_rain, stay_rain])[0]

        self.vsc_timer -= 1
        if self.vsc_timer <= 0:
            if self.vsc_active:
                self.vsc_active = False
                self.vsc_timer = random.randint(500, 1500)
            else:
                if random.random() < track["vsc_chance"]:
                    self.vsc_active = True
                    self.vsc_timer = random.randint(150, 350)
                else:
                    self.vsc_timer = 100

    def _update_bots(self):
        for bot in self.bots:
            if bot["pit_timer"] > 0:
                bot["pit_timer"] -= 1
                continue

            bot_step = bot["speed"] + (int(bot["progress"]) * 0.000005)
            if self.weather == "Deszcz":
                bot_step *= 0.8
            if self.vsc_active:
                bot_step *= 0.6

            bot["progress"] += bot_step

            curr_lap = int(bot["progress"])
            if curr_lap > bot["last_lap"]:
                bot["last_lap"] = curr_lap
                if curr_lap in bot["pit_strategy"]:
                    bot["pit_timer"] = 95

    def get_standings(self):
        standings = []
        standings.append({
            "name": "GRACZ",
            "team": self.team_id,
            "progress": self.laps + self.lap_progress,
            "is_player": True,
        })
        for bot in self.bots:
            standings.append({
                "name": bot["name"],
                "team": bot["team"],
                "progress": bot["progress"],
                "is_player": False,
            })

        standings.sort(key=lambda x: x["progress"], reverse=True)

        formatted = []
        leader_prog = standings[0]["progress"]
        for i, s in enumerate(standings):
            if not self.race_started:
                gap = "GRID"
            elif i == 0:
                gap = "LIDER"
            else:
                gap_sec = (leader_prog - s["progress"]) * 15.0
                gap = f"+{gap_sec:.3f}s"
            formatted.append({
                "pos": i + 1,
                "name": s["name"],
                "team": s["team"],
                "gap": gap,
                "is_player": s["is_player"],
            })
        return formatted

    def call_pitstop(self):
        if self.race_started and not self.in_pit and not self.pit_requested:
            self.pit_requested = True

    def cycle_tires(self):
        opts = ["Soft", "Hard", "Wet"]
        if not self.race_started:
            idx = opts.index(self.compound)
            chosen = opts[(idx + 1) % 3]
            self.set_starting_compound(chosen)
        else:
            idx = opts.index(self.next_compound)
            self.next_compound = opts[(idx + 1) % 3]

    def set_engine_mode(self, mode):
        if mode in ["Eco", "Standard", "Push"]:
            self.engine_mode = mode

    def toggle_pause(self):
        if not self.race_started or "Koniec" in self.status or "DNF" in self.status:
            return

        self.is_paused = not self.is_paused

        if self.is_paused:
            self.saved_status = self.status
            self.status = "PAUZA (Wciśnij spację, aby wznowić)"
        else:
            self.status = self.saved_status