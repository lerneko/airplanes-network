import pyray as rl
from model import Model
from aircraft import Aircraft, CargoAircraft, PassengerAircraft
from drawable import Drawable
from stepable import Stepable

class FilterBox(Drawable):
    def __init__(self, graphics, aircrafts) -> None:
        super().__init__()
        self._aircrafts = aircrafts
        self._graphics = graphics
        
        self._raw_text = []
        
        self._shape = rl.Rectangle(graphics.screen_width - 245, graphics.screen_height - 45, 230, 30)
        
    def info(self) -> str:
        menu_text = 'Filtered aircrafts:\n'

        try:
            filter_time = float(self._input_text)
            l = list(filter(lambda x: x.life_time() - x.time <= filter_time and not x.destroyed, self._aircrafts))

            if not l:
                menu_text += '  No data'
            
            for i in l:
                menu_text += '  {}:\n    max {}\n    current {}\n    remain {}\n'.format(
                    i.name,
                    i.life_time(),
                    i.time,
                    i.life_time() - i.time)
        except:
            if self._input_text == '':
                menu_text += '  No input'
            else:
                menu_text += '  Incorrect input'
        
        return menu_text
            
    @property
    def _input_text(self):
        return ''.join(self._raw_text)
            
    def draw(self):
        rl.draw_text('''Output airplanes
with remaining flight time less
than the specified value:''',
                     self._graphics.screen_width - 245, self._graphics.screen_height - 90, 14, rl.DARKGRAY)
        rl.gui_text_box(self._shape, '', 18, self._marked)
        
        if self._marked:
            key = rl.get_key_pressed()
            while key > 0:
                if 32 <= key <= 125:
                    self._raw_text.append(chr(key))
                key = rl.get_key_pressed()
            
            if rl.is_key_pressed(rl.KeyboardKey.KEY_BACKSPACE) and self._raw_text:
                self._raw_text.pop()
        
    def check_collision(self, mouse) -> bool:
        return rl.check_collision_point_rec(mouse, self._shape)

class Menu:
    def __init__(self, graphics, aircrafts: list[Aircraft]) -> None:
        self._aircrafts = aircrafts
        
        self._info = None
        self._shape = rl.Rectangle(graphics.screen_width - 250, 5, 240, graphics.screen_height - 10)
        
    def _default_info(self):
        l = list(filter(lambda x: x.destroyed, self._aircrafts))
        dead_pas = sum([x.passangers for x in list(filter(lambda x: isinstance(x, PassengerAircraft), l))])
        dead_cargo = sum([x.cargoWeight for x in list(filter(lambda x: isinstance(x, CargoAircraft), l))])
        
        menu_text = f'''
Destroyed planes: {len(l)}
Dead passangers: {dead_pas}
Dead cargo: {dead_cargo} T

'''
        
        menu_text += 'Aircrafts:\n'
        for i in self._aircrafts:
            menu_text += '    {}: {:.1f}\n'.format(i.name, i.pos)
        return menu_text
            
    @property
    def info(self):
        if self._info is None:
            return self._default_info()
        return self._info
        
    @info.setter
    def info(self, value):
        self._info = value
        
    @info.deleter
    def info(self):
        self._info = None
                
    def draw(self):
        rl.draw_rectangle_rec(self._shape, rl.LIGHTGRAY)
        rl.draw_rectangle_lines_ex(self._shape, 2, rl.BLACK)
        
        rl.draw_text(self.info, int(self._shape.x) + 5, int(self._shape.y) + 5, 18, rl.BLACK)

class GUI:
    def __init__(self):
        self._screen_width = 1000
        self._screen_height = 800

        rl.set_target_fps(60)
        rl.init_window(self._screen_width, self._screen_height, bytes("Airport Simulation", 'utf-8'))
        
        

        self._paused = False
        self._current_marked = None
        
    @property
    def screen_width(self):
        return self._screen_width
    @property
    def screen_height(self):
        return self._screen_height
    
    def set_model(self, model):
        self._model = model
        self._menu = Menu(self, model.aircrafts)
        self._filter_box = FilterBox(self, model.aircrafts)
        
        self._drawable = model.drawable
        self._drawable.append(self._filter_box)
        
    def update_graphics(self):
        if rl.is_key_pressed(rl.KeyboardKey.KEY_SPACE):
            self._toggle_pause()
        
        self._update_menu()
        
        rl.begin_drawing()
        rl.clear_background(rl.WHITE)
        
        self._menu.draw()
        
        for i in self._drawable:
            i.draw()
            
        rl.draw_fps(10, 10)

        rl.end_drawing()

        if not self._paused:
            self._model.step()
    

    
    def should_close(self):
        cond = rl.window_should_close()
        if cond:
            rl.close_window()
        return cond
    
    def _update_menu(self):
        mouse = rl.get_mouse_position()
        click = rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)
        
        if self._current_marked and not click:
            self._menu.info = self._current_marked.info()
            return
        
        for i in self._drawable:
            if i.check_collision(mouse):
                if click:
                    if self._current_marked:
                        self._current_marked.toggle_marked()
                    i.toggle_marked()
                    self._current_marked = i
                self._menu.info = i.info()
                return
            
        del self._menu.info
        if click:
            if self._current_marked:
                self._current_marked.toggle_marked()
            self._current_marked = None
            
        

    

    def _toggle_pause(self):
        self._paused = not self._paused