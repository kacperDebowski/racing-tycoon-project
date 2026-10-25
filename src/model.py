import random

class RaceModel:
    def __init__(self):
        self.laps = 0
        self.max_laps = 56 
        self.tire_wear = 100.0
        self.fuel = 100.0
        
        self.status = "Gotowy do startu"
        self.pit_requested = False
        self.in_pit = False
        self.pit_timer = 0
        self.lap_progress = 0.0
        self.lap_timer = 0.0
        
        # --- ZARZĄDZANIE PAUZĄ ---
        self.is_paused = False
        self.saved_status = ""

        self.weather = "Słonecznie"
        self.weather_timer = random.randint(300, 800)
        self.vsc_active = False
        self.vsc_timer = 100

        self.compound = "Soft"
        self.next_compound = "Soft"
        self.engine_mode = "Standard"

        self.last_lap_time = 0.0
        self.best_lap_time = 999.9
        self.current_sector = 0
        self.sectors = [0.0, 0.0, 0.0]
        self.best_sectors = [999.9, 999.9, 999.9]
        self.sector_colors = [0, 0, 0] 

        bot_names = ["VER", "NOR", "LEC", "SAI", "PIA", "RUS", "HAM", "ALO", 
                     "TSU", "STR", "HUL", "MAG", "GAS", "OCO", "ALB", "COL", 
                     "BOT", "ZHO", "LAW"]
        self.bots = []
        for name in bot_names:
            self.bots.append({
                'name': name,
                'progress': 0.0,
                'speed': random.uniform(0.00330, 0.00342), 
                'last_lap': 0,
                'pit_strategy': [random.randint(18, 28), random.randint(38, 48)],
                'pit_timer': 0
            })

    def update(self):
        # Jeśli gra jest zapauzowana, model całkowicie przerywa klatkę obliczeniową
        if self.is_paused:
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
        if self.pit_requested:
            self.status = "Zjazd na metę (IN-LAP)"
        elif self.vsc_active:
            self.status = "VSC - ZWOLNIJ!"
        else:
            self.status = f"Na torze | Silnik: {self.engine_mode}"
        
        step = 0.0033 
        
        compound_speed = {'Soft': 0.0004, 'Hard': -0.0001, 'Wet': -0.0008}
        if self.weather == 'Deszcz':
            if self.compound == 'Wet': compound_speed['Wet'] = 0.0005
            else: compound_speed[self.compound] = -0.0015
        step += compound_speed.get(self.compound, 0)
        
        fuel_bonus = ((100.0 - self.fuel) / 100.0) * 0.0004
        step += fuel_bonus
        
        if self.tire_wear <= 0:
            self.tire_wear = 0.0
            tire_penalty = 0.0025 
        else:
            tire_penalty = ((100.0 - self.tire_wear) / 100.0) * 0.0006
        step -= tire_penalty

        if self.engine_mode == 'Eco': step -= 0.0004
        elif self.engine_mode == 'Push': step += 0.0005

        if self.vsc_active: step *= 0.6

        base_deg = {'Soft': 0.018, 'Hard': 0.009, 'Wet': 0.014}
        if self.weather != 'Deszcz' and self.compound == 'Wet': 
            base_deg['Wet'] = 0.1 
            
        engine_wear_mult = {'Eco': 0.6, 'Standard': 1.0, 'Push': 1.6}
        self.tire_wear -= base_deg[self.compound] * engine_wear_mult[self.engine_mode]
        
        fuel_consumption = {'Eco': 0.004, 'Standard': 0.006, 'Push': 0.010}
        self.fuel -= fuel_consumption[self.engine_mode]

        if self.fuel <= 0:
            self.status = "DNF - Brak paliwa!"
            return

        self.lap_progress += step + random.uniform(-0.0001, 0.0001)
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
                self.pit_timer = 100 

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
        time = self.sectors[idx]
        if time < self.best_sectors[idx]:
            self.sector_colors[idx] = 5
            self.best_sectors[idx] = time
        elif time < self.best_sectors[idx] + 0.5:
            self.sector_colors[idx] = 1 
        else:
            self.sector_colors[idx] = 2 

    def _update_weather_and_events(self):
        self.weather_timer -= 1
        if self.weather_timer <= 0:
            self.weather_timer = random.randint(250, 600)
            if self.weather == "Słonecznie": self.weather = random.choices(["Słonecznie", "Pochmurno"], [80, 20])[0]
            elif self.weather == "Pochmurno": self.weather = random.choices(["Słonecznie", "Pochmurno", "Deszcz"], [30, 40, 30])[0]
            elif self.weather == "Deszcz": self.weather = random.choices(["Pochmurno", "Deszcz"], [40, 60])[0]

        self.vsc_timer -= 1
        if self.vsc_timer <= 0:
            if self.vsc_active:
                self.vsc_active = False
                self.vsc_timer = random.randint(500, 1500)
            else:
                if random.random() < 0.05: 
                    self.vsc_active = True
                    self.vsc_timer = random.randint(150, 350)
                else:
                    self.vsc_timer = 100

    def _update_bots(self):
        for bot in self.bots:
            if bot['pit_timer'] > 0:
                bot['pit_timer'] -= 1
                continue
            
            bot_step = bot['speed'] + (int(bot['progress']) * 0.000005) 
            if self.weather == 'Deszcz': bot_step *= 0.8
            if self.vsc_active: bot_step *= 0.6
            
            bot['progress'] += bot_step
            
            curr_lap = int(bot['progress'])
            if curr_lap > bot['last_lap']:
                bot['last_lap'] = curr_lap
                if curr_lap in bot['pit_strategy']:
                    bot['pit_timer'] = 100

    def get_standings(self):
        standings = []
        standings.append({'name': 'GRACZ', 'progress': self.laps + self.lap_progress, 'is_player': True})
        for bot in self.bots:
            standings.append({'name': bot['name'], 'progress': bot['progress'], 'is_player': False})
        
        standings.sort(key=lambda x: x['progress'], reverse=True)
        
        formatted = []
        leader_prog = standings[0]['progress']
        for i, s in enumerate(standings):
            if i == 0:
                gap = "LIDER"
            else:
                gap_sec = (leader_prog - s['progress']) * 15.0 
                gap = f"+{gap_sec:.3f}s"
            formatted.append({
                'pos': i + 1,
                'name': s['name'],
                'gap': gap,
                'is_player': s['is_player']
            })
        return formatted

    def call_pitstop(self):
        if not self.in_pit and not self.pit_requested:
            self.pit_requested = True

    def cycle_tires(self):
        opts = ["Soft", "Hard", "Wet"]
        idx = opts.index(self.next_compound)
        self.next_compound = opts[(idx + 1) % 3]

    def set_engine_mode(self, mode):
        if mode in ["Eco", "Standard", "Push"]:
            self.engine_mode = mode

    # --- NOWA METODA LOGIKI PAUZY ---
    def toggle_pause(self):
        if "Koniec" in self.status or "DNF" in self.status:
            return
            
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.saved_status = self.status
            self.status = "PAUZA (Wciśnij spację, aby wznowić)"
        else:
            self.status = self.saved_status