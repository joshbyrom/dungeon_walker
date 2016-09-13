from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

# entry file to program
class Walker:
    def __init__(self, **kwargs):
        self.name = 'Walker'
        self.position = kwargs.get('position') or (0, 0)
        self.facing_direction = kwargs.get('facing_direction') or \
                                kwargs.get('direction') or 'South'
        
    def move(self, direction):
        if direction == 'North':
            self.position = (self.position[0], self.position[1]+1)
        elif direction == 'South':
            self.position = (self.position[0], self.position[1]-1)
        elif direction == 'East':
            self.position = (self.position[0]+1, self.position[1])
        elif direction == 'West':
            self.position = (self.position[0]-1, self.position[1])
        else:
            raise TypeError('Only use strings: North, South, East, or West')

    def move_forward(self):
        self.move(self.facing_direction)

    def move_backward(self):
        self.move(self.get_reverse_direction(self.facing_direction))

    def get_reverse_direction(self, direction):
        if direction == 'South':
            return 'North'
        elif direction == 'North':
            return 'South'
        elif direction == 'West':
            return 'East'
        elif direction == 'East':
            return 'West'
        else:
            raise TypeError('argument recieved was not a valid direction')

    def get_direction_left_of(self, direction):
        if direction == 'North':
            return 'West'
        elif direction == 'South':
            return 'East'
        elif direction == 'West':
            return 'South'
        else:
            return 'North'
        
    def get_direction_right_of(self, direction):
            if direction == 'North':
                return 'East'
            elif direction == 'South':
                return 'West'
            elif direction == 'East':
                return 'South'
            else:
                return 'North'
        
    def turn(self, direction):
        if direction == 'Left':
            self.facing_direction = self.get_direction_left_of(self.facing_direction)
        elif direction == 'Right':
            self.facing_direction = self.get_direction_right_of(self.facing_direction)
        else:
            raise TypeError('Only use strings: Right or Left')

class Intro(BoxLayout):
    def __init__(self, **kwargs):
        BoxLayout.__init__(self, image='images/splash.png', **kwargs)

    def help_button_pressed(self, *args):
        print 'help button pressed'

    def start_button_pressed(self, *args):
        print 'start button pressed'
        
class Simulation(App):
    def __init__(self):
        App.__init__(self)
        print 'simulation created'

    def build(self):
        Builder.load_file('intro.kv')

        self.intro = Intro()
        return self.intro

        
if __name__ == '__main__':
    walker = Walker()

    print walker.position, walker.facing_direction
    walker.move('North')
    print walker.position
    walker.turn('Left')
    walker.turn('Left')
    walker.turn('Left')
    print walker.facing_direction

    walker.move_forward()
    print walker.position
    walker.move_backward()
    
    simulation = Simulation()
    simulation.run()
