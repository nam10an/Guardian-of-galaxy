# pylint: disable=no-member
import pygame
from pygame import mixer
from pygame.locals import *
import random

#if sprite class is not used then we have to manually store all the instances of aliens and their coordinates in a list
# also to add the collision functionality, we would have to iterate on a for loop to check if it collides with 
# an alien. sprite class saves us all of that code

pygame.init()

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()


screen_width = 600
screen_height = 800
screen = pygame.display.set_mode((600,800))
pygame.display.set_caption('Guardians Of Galaxy')


#define fonts
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)


#load sounds
explosion_fx = pygame.mixer.Sound("explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("explosion2.wav")
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("laser.wav")
laser_fx.set_volume(0.25)




alien_cooldown=1000
last_alien_shot=pygame.time.get_ticks()
countdown=3 #to be used when the game ends. gives 3 sec to user to restart the game
last_count=pygame.time.get_ticks()
game_over = 0 #0 is no game over, 1 means player has won, -1 means player has lost

#background image
bgimg=pygame.image.load("Background.jpg")


def draw_background():
    screen.blit(bgimg,(0,0))

#We cannot add text directly on screen. We have to convert it into image first and then display by blit function
#define function for creating text
def draw_text(text,font,text_col,x,y):
	img=font.render(text,True,text_col)
	screen.blit(img,(x,y))



red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
# INHERITING FUNCTIONALITY OF PYGAME SPRITE CLASS IN THE Spaceship CLASS
# Spaceship class is child class of Sprite class to get the built_in update() and draw() function which are already
# there in sprite class
class Spaceship(pygame.sprite.Sprite):
	def __init__(self, x, y, health):
		pygame.sprite.Sprite.__init__(self)
		self.image=pygame.image.load("spaceship (2).png")
		self.rect=self.image.get_rect()
		self.rect.center=[x,y] # x and y are coordinates of spaceship //height and width depends on the image used
		self.health_start=health
		self.health_remaining=health
		self.last_shot=pygame.time.get_ticks()


	def update(self):
		#set movement speed
		speed=8
		#set a cooldown variable
		cooldown = 500 #milliseconds
		game_over = 0


		#get key press
		key=pygame.key.get_pressed()
		if (key[pygame.K_LEFT] and self.rect.left>0):
			self.rect.x-=speed
		if (key[pygame.K_RIGHT] and self.rect.right<screen_width):
			self.rect.x+=speed

		#record current time
		time_now = pygame.time.get_ticks()
		#shoot
		if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
			laser_fx.play()
			bullet = Bullets(self.rect.centerx, self.rect.top)
			bullet_group.add(bullet)
			self.last_shot = time_now


		#update mask (to get pixel perfect collision of alien bullet and the spaceship(to not get rect collision))
		self.mask=pygame.mask.from_surface(self.image)
        #mask is put in update function so that mask gets updates each time spaceship moves left or right

		#draw health bar just below(10 px) the spaceship and height is 15px and width is same as that of spaceship
        #therefore use only png image
		pygame.draw.rect(screen,red,(self.rect.x,(self.rect.bottom+10),self.rect.width,15))
		if self.health_remaining>0:
			pygame.draw.rect(screen,green,(self.rect.x,(self.rect.bottom+10),int(self.rect.width*(self.health_remaining/self.health_start)),15))
		elif self.health_remaining <= 0:
			explosion = Explosion(self.rect.centerx, self.rect.centery, 3) #3 is the size of explosion
			explosion_group.add(explosion)
			self.kill()  #destroys the spaceship
			game_over = -1
		return game_over

#create Bullets class
class Bullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image=pygame.image.load("bullet.png")
		self.rect=self.image.get_rect()
		self.rect.center=[x,y]

	def update(self):
		self.rect.y-=5  #negative sign moves the bullet upwards
		if self.rect.bottom<0:
			self.kill()
        
        #When collide set to True then it actually kills the alien but if false then it will collide with aliens
        # but it does not kill them (only collision will be detected in false) 
		if pygame.sprite.spritecollide(self,alien_group,True):
			self.kill()   #otherwise bullets will fill the bulllet_group (this kills the bullet itself after it kill
            #an alien)
			explosion_fx.play()
			explosion=Explosion(self.rect.centerx,self.rect.centery,2) #2 is the size of explosion
			explosion_group.add(explosion)


class Aliens(pygame.sprite.Sprite):
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image=pygame.image.load("alien"+str(random.randint(1,5))+".png")
		self.rect=self.image.get_rect()
		self.rect.center=[x,y]
		self.move_counter=0
		self.move_direction=1

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 75:
			self.move_direction *= -1
			self.move_counter *= self.move_direction

class Alien_Bullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("alien_bullet.png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.y += 2
		if self.rect.top > screen_height:
			self.kill()

        #IT is set to false because we do not want spaceship to destroy in one go (spaceship has HEALTH)
        #collide mask is used to hit spaceship only when it comes in contact of it and not on the rectangle corners
        #enclosing the spaceship. We want pixel perfect collision
		if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
			self.kill()
			explosion2_fx.play()
			#reduce spaceship health
			spaceship.health_remaining -= 1
			explosion = Explosion(self.rect.centerx, self.rect.centery, 1) #1 is the size of explosion
			explosion_group.add(explosion)


class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, size):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f"exp{num}.png")
			if size == 1:
				img = pygame.transform.scale(img, (20, 20))
			if size == 2:
				img = pygame.transform.scale(img, (40, 40))
			if size == 3:
				img = pygame.transform.scale(img, (160, 160))
			#add the image to the list
			self.images.append(img)
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.counter = 0


	def update(self):
		explosion_speed = 3
		#update explosion animation
		self.counter += 1

		if self.counter >= explosion_speed and self.index < len(self.images) - 1:
			self.counter = 0
			self.index += 1
			self.image = self.images[self.index]

		#if the animation is complete, delete explosion
		if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
			self.kill()





#create sprite groups to get more functionality
#to add different instances of aliens,bullet in the group
spaceship_group = pygame.sprite.Group()
bullet_group=pygame.sprite.Group()
alien_group=pygame.sprite.Group()
alien_bullet_group=pygame.sprite.Group()
explosion_group=pygame.sprite.Group()

#create player
spaceship = Spaceship(int(screen_width / 2), screen_height - 100,5) #created instance of spaceship
spaceship_group.add(spaceship)  #just like list (if we have number of spaceships then we can add in this group)

#instance of bullets are to be done by a spacebar unlike spaceship which is automatically created

#creating instance of aliens
rows=5
cols=5
def create_aliens():
	#generate aliens
	for row in range(0,rows):
		for col in range(0,cols):
			alien = Aliens(100+col*100,100+row*70)
			alien_group.add(alien)

create_aliens()
clock=pygame.time.Clock()
fps=60

run = True
while run:
    clock.tick(fps)
    # draw background
    draw_background()


    if countdown == 0:
		#create random alien bullets
		#record current time
        time_now=pygame.time.get_ticks()
		#shoot
        #len(alien_grp)<5 to limit the number of attacking bullets from aliens to 5 at any point of time
        if time_now-last_alien_shot>alien_cooldown and len(alien_bullet_group)<5 and len(alien_group)>0:
        	attacking_alien = random.choice(alien_group.sprites())
        	alien_bullet = Alien_Bullets(attacking_alien.rect.centerx,attacking_alien.rect.bottom)
        	alien_bullet_group.add(alien_bullet)
        	last_alien_shot = time_now

		#check if all the aliens have been killed
        if len(alien_group)==0:
        	game_over=1

        if game_over==0:
			#update spaceship
        	game_over=spaceship.update()

			#update sprite groups
        	bullet_group.update()
        	alien_group.update()
        	alien_bullet_group.update()
        else:
        	if game_over == -1:
        		draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
        	if game_over == 1:
        		draw_text('YOU WIN!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))

    if countdown > 0:
    	draw_text('GET READY!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
    	draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
    	count_timer = pygame.time.get_ticks()
    	if count_timer - last_count > 1000:
    		countdown -= 1
    		last_count = count_timer


	#update explosion group	
    explosion_group.update()


    #draw sprite groups on the screen
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)


    #event handlers
    for event in pygame.event.get():
        if(event.type==pygame.QUIT):
            run=False


    pygame.display.update()

pygame.quit()