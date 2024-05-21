import pyray as rl
from aircraft import Aircraft, CargoAircraft, PassengerAircraft
from airport import Airport
from purpose import Purpose
from model import Model
from vector import Vec2d
from gui import GUI

def main():
    graphics = GUI()
    
    Aircraft.load()
    
    # Создаем аэропорты
    airports = [
        Airport("Civil 1", Vec2d(100, 100), 5, Purpose.Civil),
        Airport("Civil 2", Vec2d(93, 633), 5, Purpose.Civil),
        Airport("Military 1", Vec2d(700, 100), 5, Purpose.Military),
        Airport("Military 2", Vec2d(300, 50), 5, Purpose.Military),
        Airport("General 1", Vec2d(400, 500), 5, Purpose.General)
    ]
    
    # Создаем самолеты разных типов
    aircrafts = [
        CargoAircraft.new_rand('Cargo 1', airports[0], Vec2d(150, 150)),
        CargoAircraft.new_rand('Cargo 2', airports[0], Vec2d(200, 300)),
        PassengerAircraft.new_rand('Pass 1', airports[1], Vec2d(700, 150)),
        PassengerAircraft.new_rand('Pass 2', airports[1], Vec2d(600, 300)),
        Aircraft.new_rand('Empty 1', airports[2], Vec2d(400, 400)),
        Aircraft.new_rand('Empty 2', airports[2], Vec2d(450, 450))
    ]

    model = Model(aircrafts, airports)
    graphics.set_model(model)

    while not graphics.should_close():
        graphics.update_graphics()

    Aircraft.unload()
    
    rl.close_window()

if __name__ == "__main__":
    main()