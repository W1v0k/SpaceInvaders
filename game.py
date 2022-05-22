#https://www.youtube.com/watch?v=Q-__8Xw9KTM
import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

#LOAD IMAGES
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))# from the pygame module use the image.load method and we load the images that's at os.path.join(name of the folder, name of the file)
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))

#player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

#LASERS
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

#BACKGROUND
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)
        
class Ship: #abstract class
    COOLDOWN = 30 #half a second because FPS = 60
    def __init__(self, x, y, health = 100): #health is an optional parameter, so it will be 100 default
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None #because it's a general class, we don't define them yet because we need player and enemy ships
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0 #makes sure that we can't just spam lasers

    def draw(self, window):
        #pygame.draw.rect(window, (255,0,0),(self.x, self.y, 50, 50), 0) #(where, (color), (x,y,width,height)rect properties, if we don't want a full rect, we put a number here for the outmargin size, if we wanted it to be filled, 0)
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)      
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship): #inherit from Ship; any methods from Ship you can use in Player class
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health) #super is parent class(Ship), use initialization method on Player
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER

        #we will use masks for pixel perfect collisions and not rectangle ones
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window): #overwrite
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                } #class variable, for specific variables we want to extract from a given string
    
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)      
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None # does the mask of obj1 overlap the mask of obj2 by the offset we give () by top left coords
                                                                 # != None because if they are not overlapping we will return (x, y), the point of intersection
def main():
    run = True
    FPS = 60
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 0
    enemy_velocity = 1

    player_velocity = 5
    laser_velocity = 5
    
    player = Player(int(WIDTH/2 - (YELLOW_SPACE_SHIP.get_width())/2), 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0 #how long we want to show the message

    def redraw_window():
        WINDOW.blit(BG, (0,0))
        #draw text
        levels_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        lives_label = main_font.render(f"Lives: {lives}", 1,(255,0,0))

        WINDOW.blit(lives_label, (10,10))
        WINDOW.blit(levels_label, (WIDTH - levels_label.get_width() - 10, 10))
        
        for enemy in enemies:
            enemy.draw(WINDOW)

        player.draw(WINDOW)

        if lost:
            lost_label = lost_font.render("YOU LOST!!!", 1, (255,255,255))
            WINDOW.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350)) #perfectly centered

        pygame.display.update()

    while run:
        clock.tick(FPS)
        
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 5: #FPS*5 = 5 seconds
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500 * level/2, -100), random.choice(["red","blue","green"])) #(smallestx,biggestx),(smallesty, biggesty)
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        #movement register; if we do it in the event for loop we couldn't move diagonally, aka press 2 diff keys at the same time
        #player.y, player.x are related to the top left corner of the rectangle
        keys = pygame.key.get_pressed() #returs a dictionary of all of the keys and tells if they are pressed or not at the current time
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - player_velocity > 0: #left
            player.x -= player_velocity
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player_velocity + player.get_width() < WIDTH: #right, we add player.get_width() for the width of the player so we check an edge; without it, we could go outside the screen until the left corner of the player touches the edge of the screen
            player.x += player_velocity
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - player_velocity > 0: #up
            player.y -= player_velocity
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player_velocity + player.get_height() + 15 < HEIGHT: #down
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]: #copy of the list so we don't modify the list that we loop through
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)

            if random.randrange(0, 4*FPS) == 1: #25% probability
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
     
        player.move_lasers(-laser_velocity, enemies) #negative velocity for going up

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WINDOW.blit(BG, (0,0))
        title_label = title_font.render("Press ENTER to start...", 1, (255,255,255))
        WINDOW.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                main()
    pygame.quit()

main_menu()
