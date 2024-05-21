import random
from airport import Airport
from aircraft import Aircraft
from purpose import Purpose
from stepable import Stepable

class Model(Stepable):
    def __init__(self, aircrafts: list[Aircraft], airports: list[Airport]):
        super().__init__()
        self._aircrafts = aircrafts
        self._airports = airports
        
        for i in self._airports:
            i.set_model(self)
         
    def depart(self, aircraft):
        options = self.airports[:]
        options.remove(aircraft.destination)
        options = list(filter(lambda x: x.purpose in [aircraft.purpose, Purpose.General], options))

        target = random.choice(options)
        aircraft.depart_rand(target)
    


    def step(self):
        for aircraft in self._aircrafts:
            '''
            if aircraft.can_depart():
                options = self.airports[:]
                options.remove(aircraft.destination)
                options = list(filter(lambda x: x.purpose in [aircraft.purpose, Purpose.General], options))

                target = random.choice(options)
                aircraft.depart_rand(target)
            '''
            aircraft.step()
            
        for airport in self._airports:
            airport.step()

    @property
    def airports(self) -> list[Airport]:
        return self._airports

    @property
    def aircrafts(self) -> list[Aircraft]:
        return self._aircrafts
    
    @property
    def drawable(self) -> list[Aircraft | Airport]:
        return self._airports[:] + self._aircrafts[:]
