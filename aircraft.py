from enum import Enum
from vector import Vec2d
import airport
from random import randint
from purpose import Purpose
import pyray as rl
import math
from drawable import Drawable
from stepable import Stepable

class AircraftStatus(Enum):
    EnRoute = 1
    Landing = 2
    Landed = 3


class Aircraft(Drawable, Stepable):
    _texture = None
    _texture_size = 12
    
    def __init__(self, 
                 name: str,
                 destination: airport.Airport,
                 pos: Vec2d,
                 speed: float,
                 maxFlightTime: int,
                 stopTime: int,
                 weightFueled: float,
                 maxWeight: float,
                 purpose: Purpose,
                 ) -> None:
        Drawable.__init__(self)
        Stepable.__init__(self)
        self.__name = name
        self.__destination = destination
        self.__pos = pos
        self.__speed = speed
        self.__max_flight_time = maxFlightTime
        self.__stop_time = stopTime
        self._weight_fueled = weightFueled
        self.__max_weight= maxWeight
        
        if purpose == Purpose.General:
            raise ValueError("purpose of aircraft can't be Purpose.General")

        self.__purpose = purpose

        self.__time = 0

        self.__status = AircraftStatus.EnRoute
        self.__destroyed = False
        self.__visited_airports = []
        
    @staticmethod
    def load():
        if Aircraft._texture is None:
            img = rl.load_image('img/airplane2.png')
            rl.image_resize(img, Aircraft._texture_size, Aircraft._texture_size)
            rl.image_rotate(img, 45)
            #img = rl.load_image_svg('img/airplane.svg', 10, 10)
            Aircraft._texture = rl.load_texture_from_image(img)
            rl.unload_image(img)

    @staticmethod
    def unload():
        if Aircraft._texture is not None:
            rl.unload_texture(Aircraft._texture)
            Aircraft._texture = None

    @staticmethod
    def new_rand(name: str, destination, pos):
        speed = randint(5, 25) / 10.0
        weightFueled = randint(150, 300)
        maxWeight = randint(800, 1000)
        maxFlightTime = randint(2500, 3500)
        stopTime = randint(100, 300)
        purpose = Purpose.Military if destination.purpose == Purpose.Military else Purpose.Civil

        return Aircraft(name, destination, Vec2d(pos.x, pos.y), speed, 
                            maxFlightTime, stopTime, weightFueled, maxWeight, purpose)

    @property
    def name(self) -> str:
        return self.__name
    @property
    def purpose(self) -> Purpose:
        return self.__purpose
    @property
    def pos(self) -> Vec2d:
        return self.__pos
    @property
    def time(self) -> int:
        return self.__time

    @property
    def visited_airports(self) -> list[airport.Airport]:
        return self.__visited_airports[:]
    
    @property
    def destroyed(self):
        return self.__destroyed
    @property
    def status(self):
        return self.__status
    
    
    @property
    def destination(self):
        return self.__destination
    @destination.setter
    def destination(self, value: airport.Airport):
        self.__destination = value

    def _basic_info(self):
        return f'''{self.name}
status: {self.status.name}
destroyed: {self.destroyed}
purpose: {self.purpose.name}
pos: {self.pos:.2f}
destination: {self.destination.name}
weight: {self.weight()}
time: {self.time}
life time: {self.life_time()}
'''
    def _history_info(self):
        hist = self.visited_airports
        hist.reverse()

        info_text = ''

        if hist:
            info_text += '\nvisited airports:\n'
            for i in hist[:5]:
                info_text += f'{i.name}\n'
        return info_text

    def info(self) -> str:
        return self._basic_info() + self._history_info()
    
    def draw(self):
        if not self.status == AircraftStatus.EnRoute:
            return
        
        pos = self.pos

        color = rl.PURPLE
        
        if self.destroyed:
            if not self._marked:
                color = rl.RED
            rl.draw_poly(pos.Vector2(), 4, 5, math.pi / 4, color)
            #rl.draw_texture_ex(self._texture, self.pos.Vector2(), 0, 0.1, rl.WHITE)
        else:  
            if not self._marked:
                color = rl.BLACK
                
            dpos = self.destination.pos
            line = (dpos - pos).normalize()
            ox = Vec2d(1, 0)
            
            
            angle_rad = rl.vector2_angle(ox.Vector2(), line.Vector2())
            #расчёт угла поворота
            #angle_rad = math.acos((ox.x * line.x + ox.y * line.y) / (ox.length() * line.length()))
            #if line.y < 0:
            #    angle_rad = -angle_rad
            
            angle_deg = angle_rad / (2 * math.pi) * 360 
            
            angle_dis = angle_rad + math.pi / 4
            
            displacement = (Aircraft._texture_size) * Vec2d(math.cos(angle_dis), math.sin(angle_dis))
            #pos = pos - Vec2d(Aircraft._texture_size, Aircraft._texture_size)
            
            rl.draw_texture_ex(self._texture, (pos - displacement).Vector2(), angle_deg, 1, color)
            #rl.draw_circle(round(pos.x), round(pos.y), 3, color)
            
    
    def check_collision(self, mouse) -> bool:
        return rl.check_collision_point_circle(mouse, rl.Vector2(self.pos.x - self._texture_size / 2, self.pos.y - self._texture_size / 2), self._texture_size)

    def step(self):
        #TODO переделать приземление
        self.__destroy_check()
        
        if not self.destroyed and self.status == AircraftStatus.EnRoute:    
            self.__move()

        self.__time += 1

    def can_depart(self):
        return self.status == AircraftStatus.Landed and self.__time >= self.__stop_time
    
    def depart(self, destination: airport.Airport):
        self.__visited_airports.append(self.__destination)
        self.__destination = destination
        self.__status = AircraftStatus.EnRoute
        self.__time = 0

    def depart_rand(self, destination: airport.Airport):
        self.depart(destination)

    def __move(self):
        dpos = self.destination.pos
        line = dpos - self.__pos

        if line.length() <= self.__speed:
            self.__pos = dpos
            self.__land_request()
            return
        
        self.__pos += line.normalize() * self.__speed

    def __land_request(self):
        self.__status = AircraftStatus.Landing
        self.destination.land_request(self)
        
    def landed(self):
        self.__status = AircraftStatus.Landed

    def life_time(self):
        return int(self.__max_flight_time * (self.weight() / self.__max_weight))
    
    def left_time(self):
        return self.life_time() - self.time
    
    def weight(self):
        return self._weight_fueled
    
    def __destroy_check(self):
        if self.__destroyed or self.__status == AircraftStatus.Landed:
            return

        if self.__time >= self.life_time():
            self.__destroyed = True

class CargoAircraft(Aircraft):
    def __init__(self, 
                 name: str,
                 destination: airport.Airport, 
                 pos: Vec2d, 
                 speed: float, 
                 maxFlightTime: int, 
                 stopTime: int, 
                 weightFueled: float, 
                 maxWeight: float, 
                 purpose: Purpose,
                 cargoWeight: float,
                 maxCargoWeight: float,
                 ) -> None:
        super().__init__(name, destination, pos, speed, maxFlightTime, stopTime, weightFueled, maxWeight, purpose)

        self.__max_cargo_weight = maxCargoWeight
        self.__cargo_weight = cargoWeight
    
    @property
    def max_cargo_weight(self):
        return self.__max_cargo_weight

    @property
    def cargo_weight(self):
        return self.__cargo_weight
    @cargo_weight.setter
    def cargo_weight(self, value: float):
        self.__cargo_weight = value

    def weight(self):
        return self._weight_fueled + self.cargo_weight
    
    @staticmethod
    def new_rand(name: str, destination, pos):
        speed = randint(5, 25) / 10.0
        weightFueled = randint(150, 300)
        maxWeight = randint(900, 1300)
        maxFlightTime = randint(2500, 3500)
        stopTime = randint(100, 300)
        purpose = Purpose.Military if destination.purpose == Purpose.Military else Purpose.Civil
        maxCargoWeight = randint(100, 250) / 10.0
        cargoWeight = randint(0, int(maxCargoWeight * 10)) / 10.0

        return CargoAircraft(name, destination, Vec2d(pos.x, pos.y), speed, 
                             maxFlightTime, stopTime,
                             weightFueled, maxWeight, purpose,
                             cargoWeight, maxCargoWeight)
    
    def depart_rand(self, destination: airport.Airport):
        self.cargo_weight = randint(0, round(self.max_cargo_weight * 100)) / 100.0
        self.depart(destination)

    def info(self):
        return self._basic_info() + f'\ncargo: {self.cargo_weight} T\n' + self._history_info()
    
class PassengerAircraft(Aircraft):
    def __init__(self, 
                 name: str,
                 destination: airport.Airport, 
                 pos: Vec2d, 
                 speed: float, 
                 maxFlightTime: int, 
                 stopTime: int, 
                 weightFueled: float, 
                 maxWeight: float, 
                 purpose: Purpose,
                 passangers: int,
                 maxPassangers: int,
                 ) -> None:
        super().__init__(name, destination, pos, speed, maxFlightTime, stopTime, weightFueled, maxWeight, purpose)

        self.__passangers = passangers
        self.__max_passangers = maxPassangers

    @property
    def max_passangers(self):
        return self.__max_passangers
    
    @property
    def passangers(self):
        return self.__passangers
    @passangers.setter
    def passangers(self, value: int):
        self.__passangers = value

    
    def weight(self):
        return self._weight_fueled + 0.07 * self.passangers
    
    @staticmethod
    def new_rand(name: str, destination, pos):
        speed = randint(5, 25) / 10.0
        weightFueled = randint(150, 300)
        maxWeight = randint(1000, 1200)
        maxFlightTime = randint(2500, 3500)
        stopTime = randint(100, 300)
        purpose = Purpose.Military if destination.purpose == Purpose.Military else Purpose.Civil
        passengers = randint(50, 300)
        maxPassengers = randint(100, 500)

        return PassengerAircraft(name, destination, Vec2d(pos.x, pos.y), speed, 
                                 maxFlightTime, stopTime, 
                                 weightFueled, maxWeight, purpose,
                                 passengers, maxPassengers)
    
    def depart_rand(self, destination: airport.Airport):
        self.passangers = randint(0, self.max_passangers)
        self.depart(destination)

    def info(self) -> str:
        return self._basic_info() + f'\npassangers: {self.passangers}\n' + self._history_info()