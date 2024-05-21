from vector import Vec2d
from purpose import Purpose
import pyray as rl
from drawable import Drawable
from stepable import Stepable

class Airport(Drawable, Stepable):
    def __init__(self, name: str, pos: Vec2d, total_parkings: int, purpose: Purpose):
        Drawable.__init__(self)
        Stepable.__init__(self)
        self.__name = name
        self.__pos = pos
        self.__total_parkings = total_parkings
        self.__purpose = purpose

        self.__busy_parkings = 0

        self.__delay = 50
        self.__timer = 0

        self.__waiting_aircrafts = []
        self.__parked_aircrafts = []
        self.__destroyed_aircrafts = []
        
        self.__shape = rl.Rectangle(round(pos.x) - 5, round(pos.y) - 5, 10, 10)
        self.__model = None
    
    @property
    def name(self) -> str:
        return self.__name
    @property
    def pos(self) -> Vec2d:
        return self.__pos

    @property
    def purpose(self):
        return self.__purpose
    
    def info(self) -> str:
        info_text = f'''Airport {self.name}
purpose: {self.purpose.name}

Waiting aircrafts: {len(self.__waiting_aircrafts)}
'''
        info_text += self._format_aircrafts(self.__waiting_aircrafts)
            
        info_text += f'\nParked aircrafts: {len(self.__parked_aircrafts)}\n'
        info_text += self._format_aircrafts(self.__parked_aircrafts)
        
        info_text += f'\nDestroyed aircrafts: {len(self.__destroyed_aircrafts)}\n'
        info_text += self._format_aircrafts(self.__destroyed_aircrafts)
        
        return info_text
    
    def _format_aircrafts(self, aircrafts) -> str:
        info_text = ''
        for i in aircrafts:
            info_text += ' ' * 4 + i.name + '\n'
            
        return info_text
    
    def draw(self):
        pos = self.pos
        
        colors = {
            Purpose.General:  rl.BLUE,
            Purpose.Military: rl.GREEN,
            Purpose.Civil:    rl.YELLOW,
        }
        
        color = colors[self.purpose]

        if self._marked:
            color = rl.PURPLE
        
        rl.draw_rectangle_rec(self.__shape, color)
        
        rl.draw_text(f'{len(self.__destroyed_aircrafts)}', pos.x + 4, pos.y + 4, 3, rl.BLACK)
        
    def check_collision(self, mouse) -> bool:
        return rl.check_collision_point_rec(mouse, self.__shape)
    
    def set_model(self, model):
        self.__model = model
        
    def land_request(self, aircraft):
        self.__waiting_aircrafts.append(aircraft)
    
    def step(self):
        self._check_destroyed()
        
        if self.__timer >= self.__delay:
            self.__timer = 0
            
            if self._can_land():
                self._land()
            else:
                self._depart()

        self.__timer += 1
        
    def _check_destroyed(self):
        destroyed = list(filter(lambda x: x.destroyed, self.__waiting_aircrafts))
        self.__destroyed_aircrafts.extend(destroyed)
        for i in destroyed:
            self.__waiting_aircrafts.remove(i)
        
    def _can_land(self):
        return self.__busy_parkings < self.__total_parkings and self.__waiting_aircrafts
    
    def _land(self):
        from aircraft import PassengerAircraft
        
        to_land = list(filter(lambda x: x.left_time() <= 150, self.__waiting_aircrafts))

        if not to_land:
            to_land = list(filter(lambda x: isinstance(x, PassengerAircraft), self.__waiting_aircrafts))

        if not to_land:
            to_land = self.__waiting_aircrafts

        if to_land:
            aircraft = min(to_land, key=lambda x: x.left_time())
            aircraft.landed()
            self.__waiting_aircrafts.remove(aircraft)
            self.__parked_aircrafts.append(aircraft)
            self.__busy_parkings -= 1
    
    
    def _depart(self):
        to_depart = list(filter(lambda x: x.can_depart(), self.__parked_aircrafts))
        
        if not to_depart:
            return
        
        to_depart = max(to_depart, key=lambda x: x.time)
        
        self.__model.depart(to_depart)
        self.__parked_aircrafts.remove(to_depart)
        
        self.__busy_parkings += 1
    