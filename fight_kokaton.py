import os
import random
import sys
import time
import pygame as pg
import math  
WIDTH = 1100
HEIGHT = 650
NUM_OF_BOMBS = 5
os.chdir(os.path.dirname(os.path.abspath(__file__)))
def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate
class Bird:
    delta = {
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)
    imgs = {
        (+5, 0): img,
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),
        (-5, 0): img0,
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),
    }
    def __init__(self, xy: tuple[int, int]):
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy
        self.dire = (+5, 0) 
    def change_img(self, num: int, screen: pg.Surface):
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)
    def update(self, key_lst: list[bool], screen: pg.Surface):
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
            self.dire = tuple(sum_mv) 
        screen.blit(self.img, self.rct)

class Beam:
    def __init__(self, bird:"Bird"):
       
        self.vx, self.vy = bird.dire
       
        ang = math.degrees(math.atan2(-self.vy, self.vx))
       
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), ang, 1.0)
        self.rct = self.img.get_rect()
     
        self.rct.centerx = bird.rct.centerx + bird.rct.width * self.vx / 5
        self.rct.centery = bird.rct.centery + bird.rct.height * self.vy / 5

    def update(self, screen: pg.Surface):
        if check_bound(self.rct)[0]:
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct)

class Bomb:
    def __init__(self, color: tuple[int, int, int], rad: int):
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5
    def update(self, screen: pg.Surface):
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Score:
    def __init__(self):
        self.fonto = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.score = 0
    def update(self, screen: pg.Surface):
        img = self.fonto.render(f"Score: {self.score}", True, self.color)
        screen.blit(img, (100, HEIGHT-50))

class Explosion:
    """爆発エフェクトクラス"""
    def __init__(self, center_pos:tuple[int,int]):
        img_ori = pg.image.load("fig/explosion.gif")
        img_flip = pg.transform.flip(img_ori, True, True)
        self.imgs = [img_ori, img_flip]
        self.rct = img_ori.get_rect()
        self.rct.center = center_pos
        self.life = 10
    def update(self, screen:pg.Surface):
        self.life -=1
        if self.life>0:
            screen.blit(self.imgs[self.life%2], self.rct)

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bombs = [Bomb((255,0,0),10) for _ in range(NUM_OF_BOMBS)]
    beams = []
    explosions = []   
    score = Score()
    clock = pg.time.Clock()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.append(Beam(bird))
        screen.blit(bg_img, [0,0])
        
        beams = [b for b in beams if check_bound(b.rct)[0]]
        
        explosions = [exp for exp in explosions if exp.life>0]
       
        for b in bombs:
            if bird.rct.colliderect(b.rct):
                bird.change_img(8, screen)
                f = pg.font.Font(None,80)
                txt = f.render("Game Over",True,(255,0,0))
                screen.blit(txt,(WIDTH//2-150, HEIGHT//2))
                pg.display.update()
                time.sleep(1)
                return
        
        new_bombs = []
        for bmb in bombs:
            hit = False
            for bm in beams:
                if bmb.rct.colliderect(bm.rct):
                    hit = True
                    score.score += 1
                    bird.change_img(6, screen)
                    explosions.append(Explosion(bmb.rct.center)) 
                    break
            if not hit:
                new_bombs.append(bmb)
        bombs = new_bombs
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        for bm in beams:
            bm.update(screen)
        for bmb in bombs:
            bmb.update(screen)
        for exp in explosions:
            exp.update(screen)
        score.update(screen)
        pg.display.update()
        clock.tick(50)
        
if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
