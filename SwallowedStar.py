import pygame
import os
import sys

from pygame import mouse
from sprites import *
from config import *
from draw_texte import *
from song import *

class Game : 
    def __init__(self) :
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))       
        self.NameGame = pygame.display.set_caption("Swallowed Star")        #Screen Name
        self.icon = pygame.display.set_icon(pygame.image.load(os.path.join("Image","icon.jpg")))
        self.clock = pygame.time.Clock()                            #Framerate
        self.font = os.path.join("Text","font.ttf")
        self.running = True
        self.show_init = True
        self.GameisOver = False
        self.Background_Img = pygame.image.load(os.path.join("Image","Background3.jpg")).convert()
        self.Background = pygame.transform.scale(self.Background_Img,(845,800))
        self.Background_Y = 0
        self.score = 0
        self.score_max = 500
        self.draw_screen = Draw_screen(self)
        self.hidden = False
        self.hide_time = 0
        self.Boss1_IsAlive = False
        self.Boss2_IsAlive = False
        self.last_time_boss = 0
        self.LaserIsActive = False
        self.cooldown_anim_boss1 = 0
        self.cooldown_anim_boss2 = 0
        self.laser = Laser(self,'Laser_ult')
        self.maximum_sbire = 0
        self.rock_random_time = 0
        self.level_boss1 = 1
        self.level_boss2 = 1

    def RankUpBoss1(self) :

        for i in range(self.level_boss1) :
            self.boss1.health = self.boss1.max_health * 2
            self.boss1.max_health = self.boss1.health
        self.level_boss1 += 1
    
    def RankUpBoss2(self) :
        for i in range(self.level_boss2) :
            self.boss2.health = self.boss2.max_health * 2
            self.boss2.max_health = self.boss2.health
        self.level_boss2 += 1

    def hide(self) :
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.player.kill()

    def new_rock(self) : 
        self.rock = Rock()
        self.all_sprites.add(self.rock)
        self.Rocks.add(self.rock)
    
    def new_rock_random(self) :
        self.rock_random = RockRandom()
        self.all_sprites.add(self.rock_random)
        self.Rocks_Random.add(self.rock_random)

    def new_boss1(self) :
        self.boss1 = Boss1(self)
        self.Boss1_IsAlive = True
        self.all_sprites.add(self.boss1)
        self.the_boss.add(self.boss1)
        self.RankUpBoss1()

    def new_boss2(self) :
        self.boss2 = Boss2(self)
        self.Boss2_IsAlive = True
        self.all_sprites.add(self.boss2)
        self.the_boss.add(self.boss2)
        self.RankUpBoss2()
    
    def new_sbire(self) :
        self.sbire = Sbire(self)
        self.all_sprites.add(self.sbire)
        self.Allies.add(self.sbire)
    
    def new_player(self) :
        self.hidden = False
        self.all_sprites.add(self.player)
        self.player.rect.centerx = WIN_WIDTH / 2
        self.player.rect.bottom = WIN_HEIGHT - 50

    def events(self) :

        for event in pygame.event.get() :
            if event.type == pygame.QUIT :
                self.running = False
            
            elif event.type == pygame.KEYDOWN :                                             #Press some key Down
                if event.key == pygame.K_SPACE :                                            #Press SPACE                                                
                    #self.player.shoot()                                                    #Player Shoot
                    pass
                if event.key == pygame.K_LCTRL:
                    if not(self.hidden) :
                        if self.player.mana > 0 :
                            Laser_sound.play(-1)
                if event.key == pygame.K_c :
                    if self.player.nb_sbire > 0 and self.maximum_sbire < 5:
                        self.new_sbire()
                        self.player.nb_sbire -= 1
                        self.maximum_sbire += 1
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LCTRL] :
            if self.player.mana > 0 :
                if not(self.hidden) :
                    self.player.mana -= 1
                    self.LaserIsActive = True
                    self.all_sprites.add(self.laser)
                    self.Laser_sprites.add(self.laser)
            else :
                self.LaserIsActive = False
                self.laser.kill()
                Laser_sound.stop()
        else :
            self.LaserIsActive = False
            self.laser.kill()
            Laser_sound.stop()

    def update(self) :
        self.all_sprites.update()
        now = pygame.time.get_ticks()

        if self.score > self.score_max :                                                    #Spawn the boss2
            while not(self.Boss2_IsAlive) :
                self.new_boss2()
                self.score_max += 2500
                break

        if now - self.last_time_boss > 45000 :                                               #Spawn the boss1 every 60 sec
            self.last_time_boss = now
            while not(self.Boss1_IsAlive) :
                self.new_boss1()
                break

        if now - self.rock_random_time > 30000 :                                            #Every 30s, Spawn rock coming right/left
            self.rock_random_time = now
            for i in range(0,10) :
                self.new_rock_random()

        if self.hidden and now - self.hide_time > 1500 :                                    #after 1.5 s we spawn player
            self.new_player()

        if self.player.live == 0 and not(self.death_expl.alive()):                          #Game over 
            #self.show_init = True
            self.game_over()

    def Collision(self) :
        now = pygame.time.get_ticks()

        #Rock and Bullets
        hits1 = pygame.sprite.groupcollide(self.Rocks, self.Bullets, True, True)             #Collision between Rock and Bullet, if they collide so we delete
        for i in hits1 :
            explo = Explosion(i.rect.center, 'big')
            self.all_sprites.add(explo)
            self.score += int(i.radius)
            random.choice(explo_sound).play()
            self.new_rock()
            self.player.mana += 5
            self.player.dps += 0.01
            #Item 
            if random.random() > 0.8 :
                item = Item(i.rect.center)
                self.all_sprites.add(item)
                self.Items.add(item)

        #Player and Rock
        if not(self.hidden) :                                                                   #activate collision by checking if player still has health
            hits2 = pygame.sprite.spritecollide(self.player, self.Rocks, True, pygame.sprite.collide_circle)
            for i in hits2 :
                self.new_rock()
                explo = Explosion(i.rect.center, 'small')
                self.all_sprites.add(explo)
                self.player.health -= int(i.radius)
                if self.player.health < 1 :
                    self.death_expl = Explosion(i.rect.center, 'player')
                    self.all_sprites.add(self.death_expl)
                    Death_sound.play()
                    self.player.live -= 1
                    self.player.health = self.player.max_health
                    self.hide()
        
        #Boss2 and Bullet_player
        if self.Boss2_IsAlive :                                                          #activate collision by checking if boss still has health
            hits3 = pygame.sprite.spritecollide(self.boss2, self.Bullets, True, pygame.sprite.collide_mask)
            for i in hits3 :
                explo = Explosion(i.rect.center, 'big')
                self.all_sprites.add(explo)
                random.choice(explo_sound).play()
                self.boss2.health -= self.player.dps
                if self.boss2.health < 1 :
                    self.boss2.final_shot()
                    explo = Explosion(i.rect.center, 'player')
                    self.all_sprites.add(explo)

        #Boss1 and Bullet_player
        if self.Boss1_IsAlive :
            hit6 = pygame.sprite.spritecollide(self.boss1, self.Bullets, True, pygame.sprite.collide_mask)
            for i in hit6 :
                explo = Explosion(i.rect.center, 'big')
                self.all_sprites.add(explo)
                self.boss1.health -= self.player.dps
                self.score += 10
                random.choice(explo_sound).play()
                if self.boss1.health < 1 :
                    explo = Explosion(i.rect.center, 'player')
                    self.all_sprites.add(explo)
                    self.boss1.final_shot()
                    

        #Bullet_player and Bullet_Boss
        hit4 = pygame.sprite.groupcollide(self.Bullets, self.Bullets_boss, True, True)
        for i in hit4 :
            explo = Explosion(i.rect.center, 'small')
            self.all_sprites.add(explo)
            random.choice(explo_sound).play()
        
        #Player and Bullet_Boss
        if not(self.hidden) :        #if player hasn't die
            hit5 = pygame.sprite.spritecollide(self.player, self.Bullets_boss, True, pygame.sprite.collide_mask)
            for i in hit5 :
                explo = Explosion(i.rect.center, 'small')
                self.all_sprites.add(explo)
                self.player.health -= int(random.randrange(5,20))
                random.choice(explo_sound).play()
                if self.player.health < 1 :
                    self.death_expl = Explosion(i.rect.center, 'player')
                    self.all_sprites.add(self.death_expl)
                    Death_sound.play()
                    self.player.live -= 1
                    self.player.health = self.player.max_health
                    self.hide()

        #Player and Boss1, Boss2
        if not(self.hidden) :
            hit7 = pygame.sprite.spritecollide(self.player, self.the_boss, False, pygame.sprite.collide_mask)
            for i in hit7 :
                self.player.health -= 101
                if self.player.health < 1 :
                    self.death_expl = Explosion(self.player.rect.center, 'player')
                    self.all_sprites.add(self.death_expl)
                    Death_sound.play()
                    self.player.live -= 1
                    self.player.health = self.player.max_health
                    self.hide()

        #Laser and Rock
        if self.LaserIsActive :
            hit8 = pygame.sprite.spritecollide(self.laser, self.Rocks, True, pygame.sprite.collide_mask)
            for i in hit8 :
                explo = Explosion(i.rect.center, 'big')
                self.all_sprites.add(explo)
                self.score += int(i.radius)
                random.choice(explo_sound).play()
                self.new_rock()

        #Laser and Bullet_boss
        if self.LaserIsActive :
            hit9 = pygame.sprite.spritecollide(self.laser, self.Bullets_boss, True, pygame.sprite.collide_mask)
            for i in hit9 :
                explo = Explosion(i.rect.center, 'small')
                self.all_sprites.add(explo)
                random.choice(explo_sound).play()

        #Laser and Boss2
        if self.Boss2_IsAlive  :
            if self.LaserIsActive :                                                          
                self.hits10 = pygame.sprite.spritecollide(self.laser, self.the_boss, False, pygame.sprite.collide_mask)
                for i in self.hits10 :
                    if now - self.cooldown_anim_boss2 > 200 :
                        self.cooldown_anim_boss2 = now
                        explo = Explosion(i.rect.center, 'big')
                        self.all_sprites.add(explo)
                        random.choice(explo_sound).play()
                        self.boss2.health -= self.player.dps
                    if self.boss2.health < 1 :
                        explo = Explosion(i.rect.center, 'player')
                        self.all_sprites.add(explo)
                        self.boss2.final_shot()


        #Laser and Boss1
        if self.Boss1_IsAlive :
            if self.LaserIsActive :                                                          
                self.hits11 = pygame.sprite.spritecollide(self.laser, self.the_boss, False, pygame.sprite.collide_mask)
                for i in self.hits11 :
                    if now - self.cooldown_anim_boss1 > 200 :
                        self.cooldown_anim_boss1 = now
                        explo = Explosion(i.rect.center, 'big')
                        self.all_sprites.add(explo)
                        random.choice(explo_sound).play()
                        self.boss1.health -= self.player.dps
                    if self.boss1.health < 1:
                        explo = Explosion(i.rect.center, 'player')
                        self.all_sprites.add(explo)
                        self.boss1.final_shot()
        
        #Player and Item
        hits12 = pygame.sprite.spritecollide(self.player, self.Items, True, pygame.sprite.collide_mask)
        for i in hits12 :
            if i.type == 'potion' :
                self.player.health += random.randint(10,30)
                random.choice(item_sound).play()
            if i.type == 'sbire' :
                if self.player.nb_sbire < 5 :
                    self.player.nb_sbire += 1
                random.choice(item_sound).play()
            if i.type == 'speed' :
                self.player.speedX += 1
                self.player.speedY += 1
                self.player.cooldown -= 5
                random.choice(item_sound).play()
            if i.type == 'boost' :
                self.player.GunUp()
                random.choice(item_sound).play()

        #Sbire and Rock
        hits13 = pygame.sprite.groupcollide(self.Allies, self.Rocks, True, True, pygame.sprite.collide_circle)
        for i in hits13 :
            self.new_rock()
            self.death_expl = Explosion(i.rect.center, 'player')
            self.all_sprites.add(self.death_expl)
            Death_sound.play()
            self.maximum_sbire -= 1
        
        #Sbire and Bullet_Boss2
        hit14 = pygame.sprite.groupcollide(self.Allies, self.Bullets_boss, True, True, pygame.sprite.collide_mask)
        for i in hit14 :
            self.death_expl = Explosion(i.rect.center, 'player')
            self.all_sprites.add(self.death_expl)
            Death_sound.play()
            self.maximum_sbire -= 1

        #Sbire and Boss1, Boss2
        hit15 = pygame.sprite.groupcollide(self.Allies, self.the_boss, True, False, pygame.sprite.collide_mask)
        for i in hit15 :
            self.death_expl = Explosion(i.rect.center, 'player')
            self.all_sprites.add(self.death_expl)
            Death_sound.play()
            self.maximum_sbire -= self.player.dps

        #Rock_random and Playez_Bullet
        hits16 = pygame.sprite.groupcollide(self.Rocks_Random, self.Bullets, True, True)             #Collision between Rock and Bullet, if they collide so we delete
        for i in hits16 :
            explo = Explosion(i.rect.center, 'big')
            self.all_sprites.add(explo)
            self.score += int(i.radius)
            random.choice(explo_sound).play()
            self.player.mana += 5
            self.player.dps += 0.1

        #Player and Rock_random
        if not(self.hidden) :                                                                   #activate collision by checking if player still has health
            hits17 = pygame.sprite.spritecollide(self.player, self.Rocks_Random, True, pygame.sprite.collide_circle)
            for i in hits17 :
                explo = Explosion(i.rect.center, 'small')
                self.all_sprites.add(explo)
                self.player.health -= int(i.radius)
                if self.player.health < 1 :
                    self.death_expl = Explosion(i.rect.center, 'player')
                    self.all_sprites.add(self.death_expl)
                    Death_sound.play()
                    self.player.live -= 1
                    self.player.health = self.player.max_health
                    self.hide()
        
        #Laser and Rock_random
        if self.LaserIsActive :
            hit18 = pygame.sprite.spritecollide(self.laser, self.Rocks_Random, True, pygame.sprite.collide_mask)
            for i in hit18 :
                explo = Explosion(i.rect.center, 'big')
                self.all_sprites.add(explo)
                self.score += int(i.radius)
                random.choice(explo_sound).play()

        #Sbire and Rock_random
        hits19 = pygame.sprite.groupcollide(self.Allies, self.Rocks_Random, True, True, pygame.sprite.collide_circle)
        for i in hits19 :
            self.death_expl = Explosion(i.rect.center, 'player')
            self.all_sprites.add(self.death_expl)
            Death_sound.play()
            self.maximum_sbire -= 1
        
        #Player and final_shoot
        if not(self.hidden) :        #if player hasn't die
            hit20 = pygame.sprite.spritecollide(self.player, self.final_shoot, True, pygame.sprite.collide_mask)
            for i in hit20 :
                explo = Explosion(i.rect.center, 'small')
                self.all_sprites.add(explo)
                self.player.health -= int(random.randrange(5,20))
                random.choice(explo_sound).play()
                if self.player.health < 1 :
                    self.death_expl = Explosion(i.rect.center, 'player')
                    self.all_sprites.add(self.death_expl)
                    Death_sound.play()
                    self.player.live -= 1
                    self.player.health = self.player.max_health
                    self.hide()

        #Bullet_player and final_shoot
        hit21 = pygame.sprite.groupcollide(self.Bullets, self.final_shoot, True, True)
        for i in hit21 :
            explo = Explosion(i.rect.center, 'small')
            self.all_sprites.add(explo)
            random.choice(explo_sound).play()
        
        #sbire and final_shoot
        hit22 = pygame.sprite.groupcollide(self.Allies, self.Bullets_boss, True, True, pygame.sprite.collide_mask)
        for i in hit22 :
            self.death_expl = Explosion(i.rect.center, 'player')
            self.all_sprites.add(self.death_expl)
            Death_sound.play()
            self.maximum_sbire -= 1

    def draw(self) :
        self.screen.fill(BLACK)                                                             #Draw the background colors

        Background_X = int(-0.05 * self.player.rect.centerx)                                 #Move the background moving axe X

        self.screen.blit(self.Background,(Background_X,self.Background_Y))                  #Draw the background
        self.screen.blit(self.Background,(Background_X,-WIN_HEIGHT  + self.Background_Y))   #Draw the seconde background
        if self.Background_Y == WIN_HEIGHT :                                                
            self.Background_Y = 0
        self.Background_Y += 1

        self.all_sprites.draw(self.screen)                                                  #Draw all sprites on screen like player, rock, boss, 
        
        self.draw_screen.Draw_score(self.screen, str(self.score), 20, WIN_WIDTH/2, 10)      #Draw Score on center-top screen
        self.draw_screen.Draw_health(self.screen, self.player.health, 5, 10)                #Draw health on screen
        self.draw_screen.Draw_Mana(self.screen, self.player.mana, 5, 20)
        self.draw_screen.Draw_live(self.screen, self.player.live, self.draw_screen.Player_Lives_Img, WIN_WIDTH - 100, 15)           #Draw Lives on screen
        self.draw_screen.Draw_sbire(self.screen, self.player.nb_sbire, self.draw_screen.Sbire_Lives_Img, 0, WIN_HEIGHT - 30)
        self.draw_screen.Draw_dps(self.screen, str(int(self.player.dps)), 20, WIN_WIDTH- 100,WIN_HEIGHT-25)
        if self.Boss1_IsAlive :
            self.draw_screen.Draw_health_boss1(self.screen, self.boss1.health, self.boss1.rect.x, self.boss1.rect.y)
        if self.Boss2_IsAlive :
            self.draw_screen.Draw_health_boss2(self.screen, self.boss2.health, self.boss2.rect.x, self.boss2.rect.y)

        self.clock.tick(FPS)                                                                #FPS by sec
        pygame.display.update()                                                             #Draw the screen

    def main(self) :
        self.events()
        self.update()
        self.Collision()
        self.draw()

        #print(f"{self.clock.get_fps()} FPS")                #Show FPS in terminal

    def game_over(self) :
        self.screen.blit(self.draw_screen.Background_Img_GameOver,(-35,0))
        self.draw_screen.draw_text(self.screen,'Your score is ', 64, WIN_WIDTH/2, WIN_HEIGHT/4)
        self.draw_screen.Draw_score(self.screen, str(self.score), 64, WIN_WIDTH/2, WIN_HEIGHT/2 - 100)
        self.draw_screen.Rank()

        MainMenu_Button = Button(WIN_WIDTH/4, WIN_HEIGHT/1.15, 250, 75, WHITE, BLACK, 'Main Menu', 32)
        Retry_Button = Button(WIN_WIDTH/1.35, WIN_HEIGHT/1.15, 250, 75, WHITE, BLACK, 'Retry', 32)

        for sprite in self.all_sprites :
            sprite.kill()

        self.waiting = True
        while self.waiting :
            for event in pygame.event.get() :
                mouse_pos = pygame.mouse.get_pos()
                mouse_pressed = pygame.mouse.get_pressed()
                if event.type == pygame.QUIT :
                    pygame.quit()
                    #sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN :
                    if MainMenu_Button.Is_Pressed(mouse_pos, mouse_pressed) :
                        self.show_init = True
                        self.waiting = False
                    if Retry_Button.Is_Pressed(mouse_pos, mouse_pressed) :
                        self.waiting = False
                        self.show_init = False
                        self.new_game()
                        self.main()

            self.screen.blit(MainMenu_Button.image, MainMenu_Button.rect)
            self.screen.blit(Retry_Button.image, Retry_Button.rect)

            self.clock.tick(FPS)
            pygame.display.update()

    def new_game(self) :
        #A New game starts
        
        self.all_sprites = pygame.sprite.Group()            
        self.Rocks = pygame.sprite.Group()                  #Rock
        self.Bullets = pygame.sprite.Group()                #Bullets player
        self.Items = pygame.sprite.Group()                  #Items
        self.the_boss = pygame.sprite.Group()               #The boss
        self.Bullets_boss = pygame.sprite.Group()           #Bullets Boss
        self.Laser_sprites = pygame.sprite.Group()          #Laser
        self.Allies = pygame.sprite.Group()                 #Sbire
        self.Rocks_Random = pygame.sprite.Group()           #Rock coming to the right / to the left
        self.final_shoot = pygame.sprite.Group()            #Final shoot (boss)
        
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.sbire = Sbire(self)

        self.Boss1_IsAlive = False
        self.Boss2_IsAlive = False
        self.level_boss1 = 1
        self.level_boss2 = 1
        self.last_time_boss = pygame.time.get_ticks()
        self.cooldown_anim_boss1 = pygame.time.get_ticks()
        self.cooldown_anim_boss2 = pygame.time.get_ticks()
        self.rock_random_time = pygame.time.get_ticks()

        for i in range(0,5) :
            self.new_rock()
            pass
        self.score = 0
        #self.new_boss2()
        #self.new_boss1()

game = Game()
pygame.mixer.music.play(-1)

while game.running :                                        #Game running 
    if game.show_init :                                     #Open Main Menu
        close_game = game.draw_screen.Draw_init()
        if close_game :                                     #If we close the game, so break
            break
        else :
            game.show_init = False                          #Else if player chose to start a game so we close Main Menu
            game.new_game()                                 #Add all Sprites 
    game.main()                                             #Game start !!

pygame.quit()
sys.exit()