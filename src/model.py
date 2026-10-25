import random

class RaceModel:
    def __init__(self):
        self.laps = 0
        self.max_laps = 15
        self.tire_wear = 100.0
        self.fuel = 100.0
        
        self.status = "Gotowy do startu"
        self.pit_requested = False
        self.in_pit = False
        self.pit_timer = 0
        self.lap_progress = 0.0
        self.lap_timer = 0.0

        self.weather = "Słonecznie"
        self.weather_timer = random.randint(150, 400)
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

        self.leader_progress = 0.0
        self.gap_to_leader = 0.0

    def update(self):
        if self.laps >= self.max_laps:
            self.status = "Koniec wyścigu!"
            self.lap_progress = 0.0
            return

        self._update_weather_and_events()
        self._update_leader()

        if self.in_pit:
            self.pit_timer -= 1
            self.status = f"PIT STOP ({self.pit_timer})"
            if self.pit_timer <= 0:
                self.in_pit = False
                self.compound = self.next_compound
                self.tire_wear = 100.0
                self.fuel = 100.0
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
        
        # --- ZAAWANSOWANA FIZYKA JAZDY ---
        
        # 1. Baza prędkości
        step = 0.0033 
        
        # 2. Wpływ mieszanki opon
        compound_speed = {'Soft': 0.0004, 'Hard': -0.0001, 'Wet': -0.0008}
        if self.weather == 'Deszcz':
            if self.compound == 'Wet': compound_speed['Wet'] = 0.0005
            else: compound_speed[self.compound] = -0.0015 # Slicki na mokrym lodowisku
        step += compound_speed.get(self.compound, 0)
        
        # 3. Wpływ wagi paliwa (Lżejsze auto = szybsze)
        fuel_bonus = ((100.0 - self.fuel) / 100.0) * 0.0004
        step += fuel_bonus
        
        # 4. Kara za zniszczone opony (Zużyte opony = uślizg i mniejsza prędkość)
        tire_penalty = ((100.0 - self.tire_wear) / 100.0) * 0.0006
        step -= tire_penalty

        # 5. Wpływ Trybu Silnika
        if self.engine_mode == 'Eco': 
            step -= 0.0004
        elif self.engine_mode == 'Push': 
            step += 0.0005

        # 6. Wirtualny Samochód Bezpieczeństwa (Tnie prędkość drastycznie)
        if self.vsc_active: 
            step *= 0.6

        # --- ZUŻYCIE ZASOBÓW ---
        
        # Degradacja opon zależy teraz od wybranego trybu silnika! (Push zjada opony)
        base_deg = {'Soft': 0.08, 'Hard': 0.04, 'Wet': 0.06}
        if self.weather != 'Deszcz' and self.compound == 'Wet': 
            base_deg['Wet'] = 0.3 # Opony deszczowe palą się na suchym asfalcie
            
        engine_wear_mult = {'Eco': 0.6, 'Standard': 1.0, 'Push': 1.6}
        
        current_deg = base_deg[self.compound] * engine_wear_mult[self.engine_mode]
        self.tire_wear -= current_deg + random.uniform(0, 0.01)
        
        # Spalanie paliwa
        fuel_consumption = {'Eco': 0.02, 'Standard': 0.035, 'Push': 0.06}
        self.fuel -= fuel_consumption[self.engine_mode]

        # Aktualizacja pozycji i czasu
        self.lap_progress += step + random.uniform(-0.0001, 0.0001)
        self.lap_timer += 0.05 

        if self.tire_wear <= 0 or self.fuel <= 0:
            self.status = "DNF - Awaria z braku zasobów!"
            return

        self._record_sectors()

        # Koniec okrążenia
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

    def _update_leader(self):
        # Lider teraz też "traci wagę paliwa", dzięki czemu z każdym okrążeniem jest o ułamek sekundy szybszy
        leader_step = 0.00355 + (self.laps * 0.00001)
        
        if self.weather == 'Deszcz': leader_step = 0.0028
        if self.vsc_active: leader_step *= 0.6
        
        self.leader_progress += leader_step
        player_total_progress = self.laps + self.lap_progress
        diff_laps = self.leader_progress - player_total_progress
        self.gap_to_leader = diff_laps * 15.0 

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