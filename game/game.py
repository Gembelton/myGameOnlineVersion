import pygame, math
from network import Network

black = (0, 0, 0)
white = (255, 255, 255)
blue = (50, 50, 255)
red = (255, 0, 0)


class Player(pygame.sprite.Sprite):
    width = height = 25

    def __init__(self, startx, starty):
        super().__init__()
        self.image = pygame.Surface([15, 15])
        self.image.fill(blue)
        self.alive = True
        self.rect = self.image.get_rect()
        self.rect.x = startx
        self.rect.y = starty
        self.velocity = 6

    def draw(self, g, color):
        pygame.draw.rect(g, color, (self.rect.x, self.rect.y, self.width, self.height), 0)

    def move(self, dirn):
        """
        :param dirn: 0 - 3 (right, left, up, down)
        :return: None
        """

        if dirn == 0:
            self.rect.x += self.velocity
        elif dirn == 1:
            self.rect.x -= self.velocity
        elif dirn == 2:
            self.rect.y -= self.velocity
        else:
            self.rect.y += self.velocity

    def is_collided_with(self, sprite):
        return self.rect.colliderect(sprite.rect)


# Класс оружия
class Bullet(pygame.sprite.Sprite):
    width = height = 10

    def __init__(self, start_x, start_y, end_x, end_y, speed_x_y):
        super().__init__()

        # Задает ширину ,высоту,цвет пуле
        self.image = pygame.Surface([10, 10])
        self.image.fill(black)
        self.color = (255, 120, 0)
        self.rect = self.image.get_rect()
        # Начальные координаты появления
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y
        # Из-за формул, возможно появление точки,позже эту переменную позже изменим на целочисленную
        self.floating_point_x = start_x
        self.floating_point_y = start_y

        # создание угла между начальной координатой и конечной
        x_diff = end_x - start_x
        y_diff = end_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # изменение по осям, с высчитыванием угла, а также скорость самой пули
        self.speed_x_y = speed_x_y
        self.change_x = math.cos(angle) * self.speed_x_y
        self.change_y = math.sin(angle) * self.speed_x_y

    def move(self):
        # обновление координаты пули, после всех высчитываний
        self.floating_point_y += self.change_y
        self.floating_point_x += self.change_x
        # Преображение в целочисленный тип
        self.rect.y = int(self.floating_point_y)
        self.rect.x = int(self.floating_point_x)

    def draw(self, g):
        pygame.draw.rect(g, self.color, (self.rect.x, self.rect.y, self.width, self.height), 0)


class Game:

    # Если запуск сервера идет с этого компа
    def __init__(self, w, h):

        self.create_bul = False
        self.net = Network()
        self.width = w
        self.yep = False
        self.height = h
        self.player = Player(900, 450)
        self.player2 = Player(100, 100)
        self.bullet2 = Bullet(-5, -5, -20, -30, 2)
        self.canvas = Canvas(self.width, self.height, "")

    def run(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                    run = False

            keys = pygame.key.get_pressed()
            if self.player.alive:
                if keys[pygame.K_RIGHT]:
                    if self.player.rect.x <= 1086:
                        self.player.move(0)

                if keys[pygame.K_LEFT]:
                    if self.player.rect.x >= 85:
                        self.player.move(1)

                if keys[pygame.K_UP]:
                    if self.player.rect.y >= 70:
                        self.player.move(2)

                if keys[pygame.K_DOWN]:
                    if self.player.rect.y <= 480:
                        self.player.move(3)

                if keys[pygame.K_SPACE]:
                    pos = pygame.mouse.get_pos()
                    self.mouse_x = pos[0]
                    self.mouse_y = pos[1]
                    # создает нашу пулю.Параметры:началльная позиция по Х и У, конечная по Х и У, скорость
                    self.bullet = Bullet(self.player.rect.x, self.player.rect.y, self.mouse_x,
                                         self.mouse_y, 12)
                    # создает нашу пулю.Параметры:началльная позиция по Х и У, конечная по Х и У, скорость

                    self.create_bul = True
            else:
                self.canvas.font_lose()
                # выстреливает пулю при нажатии кнопки мышки
                # получаем координаты самой мыши

                # добавляет ее в список
                # all_sprite_list.add(bullet)
                # bullet_list.add(bullet)

            # Send Network Stuff
            self.player2.rect.x, self.player2.rect.y = self.parse_data(self.send_data())
            self.bullet2.rect.x, self.bullet2.rect.y = self.parse_data_bullet(self.send_data())
            ##################
            if self.create_bul:
                self.bullet.rect.x, self.bullet.rect.y = self.parse_data(self.send_data())
            # Update Canvas
            self.canvas.draw_background()
            self.player.draw(self.canvas.get_canvas(), blue)
            self.player2.draw(self.canvas.get_canvas(), red)
            self.bullet2.draw(self.canvas.get_canvas())
            if self.create_bul == True:
                self.bullet.move()
                self.bullet.draw(self.canvas.get_canvas())

            # -----------!!!!!!!!!!!!!!!!!-----------#
            if self.player.is_collided_with(self.bullet2):
                self.yep = True
                self.player.rect.x = 50
                self.player.rect.y = 50
                self.player.alive = False
            if not self.player.alive:
                self.canvas.font_lose()
            if self.player2.rect.x == 50 and self.player2.rect.y == 50:
                self.canvas.font_win()

            self.canvas.update()

        pygame.quit()

    def send_data(self):
        """
        Send position to server
        :return: None
        """
        line = ''
        if self.create_bul:
            line = str(self.bullet.rect.x) + ',' + str(self.bullet.rect.y)

        data = str(self.net.id) + ":" + str(self.player.rect.x) + "," + str(self.player.rect.y) + "," + str(line)
        reply = self.net.send(data)
        return reply

    @staticmethod
    def parse_data(data):
        try:
            f = reversed(data)
            f = data.split(":")[1].split(",")
            reversed(data)
            d = data.split(":")[1].split(",")
            return int(d[0]), int(d[1])
        except:
            return 0, 0

    @staticmethod
    def parse_data_bullet(data):
        try:
            f = reversed(data)
            f = data.split(":")[1].split(",")
            reversed(data)
            return int(f[2]), int(f[3])
        except:
            return 0, 0


class Canvas(pygame.sprite.Sprite):

    def __init__(self, w, h, name=''):
        self.image = 0
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("PaTwoo Duel 1x1")
        self.image = pygame.image.load('arena.png').convert_alpha()

        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = [0, 0]

    @staticmethod
    def update():
        pygame.display.update()

    def get_canvas(self):
        return self.screen

    def draw_background(self):
        self.screen.fill([255, 255, 255])
        self.screen.blit(self.image, self.rect)

    def font_lose(self):
        pygame.font.init()
        font = pygame.font.SysFont('Calibri', 160, True, False)
        text = font.render("Вы проиграли", True, red)
        self.screen.blit(text, [120, 200])

    def font_win(self):
        pygame.font.init()
        font = pygame.font.SysFont('Calibri', 160, True, False)
        text = font.render("Вы выйграли", True, blue)
        self.screen.blit(text, [120, 200])

#class Interface():
   # def fonts_lose(self):
       # font = pygame.font.SysFont('Calibri', 160, True, False)
       # text = font.render("Вы проиграли", True, red)
       # window.blit(text, [300, 200])
# растовая графика
# меню (если оочень припрет)
