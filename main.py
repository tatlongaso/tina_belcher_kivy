from kivy.app import App
from kivy.core.image import Image
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.properties import ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.config import Config


class Runner(Widget):
    image = ObjectProperty(None)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    is_jumping = False

    def move(self, delta):
        # update position from velocity
        self.pos = Vector(*self.velocity) + self.pos

        # apply gravity
        if self.velocity_y > -10 and self.pos[1] > 0:
            self.velocity_y -= delta * 10
        else:
            self.velocity_y = 0
            self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = 5.0

    def set_position(self, pos):
        self.pos = pos

    def set_position_x(self, x):
        self.pos[0] = x

    def set_position_y(self, y):
        self.pos[1] = y

    def change_source(self, source):
        self.image.source = source

    def stop(self):
        self.image.anim_delay = -1


class Chaser(Runner):
    default_speed = 2
    velocity_x = NumericProperty(default_speed)

    def slow_down(self):
        self.velocity_x = -1.5

    def move(self, delta):
        Runner.move(self, delta)

        if self.velocity_x < self.default_speed:
            self.velocity_x += delta
        else:
            self.velocity_x = self.default_speed


class Collectible(Widget):
    pass


class TinaBelcherGame(Widget):
    bg = ObjectProperty(None)
    end_label = ObjectProperty()

    is_game_running = True

    default_speed = -8.0
    velocity_x = NumericProperty(-8.0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    collectibles = []
    collectibles_cnt = 0

    score = NumericProperty(0)

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        self.runner = Runner()
        # reduce size of cat spirte
        self.runner.size = (160, 160)
        self.add_widget(self.runner)

        self.chaser = Chaser()
        self.chaser.set_position(Vector(0, 0))
        self.chaser.change_source('dog.zip')
        self.add_widget(self.chaser)

    def update(self, delta):
        if not self.is_game_running:
            self.end_label.text = "GAME OVER"
            self.runner.stop()
            self.chaser.stop()
            return

        self.runner.set_position_x(self.width / 2)

        # update runner
        self.runner.move(delta)
        self.chaser.move(delta)
        self.bg_move();

        # colectibles
        self.collectibles_cnt += 1
        if self.collectibles_cnt > 50:
            self.collectibles_cnt = 0
            collectible = Collectible()
            collectible.pos = self.width, 80
            self.collectibles.append(collectible)
            self.add_widget(collectible)

        # move collectibles
        for collectible in self.collectibles:
            x, y = collectible.pos
            collectible.pos = x - 10, y
            if collectible.pos[0] + collectible.width < 0:
                self.collectibles.remove(collectible)
                self.remove_widget(collectible)
                continue

            # check runner collision with collectible
            x1, y1 = self.runner.pos
            w1, h1 = self.runner.size
            x2, y2 = collectible.pos
            w2, h2 = collectible.size
            if (x2 >= x1 and x2 + w2 <= x1 + w1 and
                y2 >= y1 and y2 + h2 <= y1 + h1):
                self.score += 100
                self.collectibles.remove(collectible)
                self.remove_widget(collectible)


        # check runner chaser collision
        x1, y1 = self.runner.pos
        x2, y2 = self.chaser.pos
        w2, h2 = self.chaser.size
        # game over if dog catches cat
        if x2 + w2 / 2 > x1:
            self.is_game_running = False

        # reduce velocity if necessary
        if self.velocity_x < self.default_speed:
            self.velocity_x += delta
        else:
            self.velocity_x = self.default_speed


    def speed_up(self):
        self.velocity_x = self.default_speed - 3


    def bg_move(self):
        """Scroll over multiple background images"""
        self.pos = Vector(*self.velocity) + self.pos

        bg_size = self.bg.get_norm_image_size()
        if self.pos[0] + bg_size[0] < self.width:
            self.pos = self.width, self.pos[1]
            # switch bg image
            source = self.bg2.source
            self.bg2.source = self.bg.source
            self.bg.source = source
            self.bg3.source = self.bg.source

        self.bg2.pos = (self.pos[0] - bg_size[0]), 0
        self.bg3.pos = (self.pos[0] - bg_size[0] * 2), 0


    def on_touch_down(self, touch):
        self.runner.jump()
        self.chaser.slow_down()
        self.speed_up()


class TinaBelcherApp(App):
    def build(self):
        game = TinaBelcherGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ == '__main__':
    Config.set('graphics', 'width', '900')
    Config.set('graphics', 'height', '600')

    TinaBelcherApp().run()
