import pygame
from config import *
import random
import math
from inventory import *

class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height))
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        return sprite

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):

        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.facing = 'down'
        self.animation_loop = 1

        # HP and Mana System
        self.max_hp = MAX_HP
        self.current_hp = self.max_hp
        self.max_mana = MAX_MANA
        self.current_mana = self.max_mana

        # Damage cooldown system
        self.damage_cooldown = 0

        self.image = self.game.character_spritesheet.get_sprite(3, 2, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.down_animations = [self.game.character_spritesheet.get_sprite(3, 2, self.width, self.height),
                           self.game.character_spritesheet.get_sprite(35, 2, self.width, self.height),
                           self.game.character_spritesheet.get_sprite(68, 2, self.width, self.height)]

        self.up_animations = [self.game.character_spritesheet.get_sprite(3, 34, self.width, self.height),
                         self.game.character_spritesheet.get_sprite(35, 34, self.width, self.height),
                         self.game.character_spritesheet.get_sprite(68, 34, self.width, self.height)]

        self.left_animations = [self.game.character_spritesheet.get_sprite(3, 98, self.width, self.height),
                           self.game.character_spritesheet.get_sprite(35, 98, self.width, self.height),
                           self.game.character_spritesheet.get_sprite(68, 98, self.width, self.height)]

        self.right_animations = [self.game.character_spritesheet.get_sprite(3, 66, self.width, self.height),
                            self.game.character_spritesheet.get_sprite(35, 66, self.width, self.height),
                            self.game.character_spritesheet.get_sprite(68, 66, self.width, self.height)]

    def update(self):
        self.movement()
        self.animate()
        self.collide_enemy()

        # Update damage cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')

        self.x_change = 0
        self.y_change = 0

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x_change -= PLAYER_SPEED
            self.facing = 'left'
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x_change += PLAYER_SPEED
            self.facing = 'right'
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y_change -= PLAYER_SPEED
            self.facing = 'up'
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y_change += PLAYER_SPEED
            self.facing = 'down'

    def collide_enemy(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits and self.damage_cooldown <= 0:
            self.take_damage(1)  # Take 1 damage instead of dying instantly
            self.damage_cooldown = DAMAGE_COOLDOWN  # Set cooldown

    def collide_blocks(self, direction):
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right

        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom

    def animate(self):

        if self.facing == 'down':
            if self.y_change == 0:
                self.image = self.game.character_spritesheet.get_sprite(3, 2, self.width, self.height)
            else:
                self.image = self.down_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1

        if self.facing == 'up':
            if self.y_change == 0:
                self.image = self.game.character_spritesheet.get_sprite(3, 34, self.width, self.height)
            else:
                self.image = self.up_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1

        if self.facing == 'left':
            if self.x_change == 0:
                self.image = self.game.character_spritesheet.get_sprite(3, 98, self.width, self.height)
            else:
                self.image = self.left_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1

        if self.facing == 'right':
            if self.x_change == 0:
                self.image = self.game.character_spritesheet.get_sprite(3, 66, self.width, self.height)
            else:
                self.image = self.right_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1

    def can_attack(self):
        """Check if player has enough mana to attack"""
        return self.current_mana >= ATTACK_MANA_COST

    def use_mana(self, amount):
        """Use mana for attacks or abilities"""
        if self.current_mana >= amount:
            self.current_mana -= amount
            return True
        return False

    def take_damage(self, damage):
        """Take damage and reduce HP"""
        self.current_hp = max(0, self.current_hp - damage)
        if self.current_hp <= 0:
            self.kill()
            self.game.playing = False

    def is_alive(self):
        """Check if player is still alive"""
        return self.current_hp > 0

    def use_hp_potion(self):
        """Use a health potion to restore HP"""
        if self.current_hp < self.max_hp:
            self.current_hp = min(self.max_hp, self.current_hp + 2)  # Restore 2 HP
            return True
        return False

    def use_mana_potion(self):
        """Use a mana potion to restore mana"""
        if self.current_mana < self.max_mana:
            self.current_mana = min(self.max_mana, self.current_mana + 30)  # Restore 30 mana
            return True
        return False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        # AI Pathfinding attributes
        self.speed = ENEMY_SPEED
        self.detection_range = 80  # pixels (increased from 50 for better gameplay)

        self.x_change = 0
        self.y_change = 0

        self.facing = random.choice(['left', 'right', 'up', 'down'])
        self.animation_loop = 1

        self.image = self.game.enemy_spritesheet.get_sprite(3, 2, self.width, self.height)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.down_animations = [self.game.enemy_spritesheet.get_sprite(3, 2, self.width, self.height),
                           self.game.enemy_spritesheet.get_sprite(35, 2, self.width, self.height),
                           self.game.enemy_spritesheet.get_sprite(68, 2, self.width, self.height)]

        self.up_animations = [self.game.enemy_spritesheet.get_sprite(3, 34, self.width, self.height),
                         self.game.enemy_spritesheet.get_sprite(35, 34, self.width, self.height),
                         self.game.enemy_spritesheet.get_sprite(68, 34, self.width, self.height)]

        self.left_animations = [self.game.enemy_spritesheet.get_sprite(3, 98, self.width, self.height),
                           self.game.enemy_spritesheet.get_sprite(35, 98, self.width, self.height),
                           self.game.enemy_spritesheet.get_sprite(68, 98, self.width, self.height)]

        self.right_animations = [self.game.enemy_spritesheet.get_sprite(3, 66, self.width, self.height),
                            self.game.enemy_spritesheet.get_sprite(35, 66, self.width, self.height),
                            self.game.enemy_spritesheet.get_sprite(68, 66, self.width, self.height)]

    def update(self):
        """Update enemy with AI pathfinding logic"""
        if self.game.player:
            self.update_ai()
            self.animate()

            # Apply movement with collision detection
            self.rect.x += self.x_change
            self.collide_blocks('x')
            self.rect.y += self.y_change
            self.collide_blocks('y')

            self.x_change = 0
            self.y_change = 0

    def update_ai(self):
        """Update enemy AI logic"""
        if self.game.player:
            player_x = self.game.player.rect.centerx
            player_y = self.game.player.rect.centery

            # Calculate distance to player
            distance = math.sqrt((player_x - self.rect.centerx) **2 + (player_y - self.rect.centery) **2)

            # If player is within detection range, follow them
            if distance <= self.detection_range and distance > 0:
                # Calculate direction vector (normalized)
                direction_x = (player_x - self.rect.centerx) / distance
                direction_y = (player_y - self.rect.centery) / distance

                # Move towards player
                self.x_change = direction_x * self.speed
                self.y_change = direction_y * self.speed

                # Update facing direction based on movement
                if abs(self.x_change) > abs(self.y_change):
                    if self.x_change > 0:
                        self.facing = 'right'
                    else:
                        self.facing = 'left'
                else:
                    if self.y_change > 0:
                        self.facing = 'down'
                    else:
                        self.facing = 'up'
            else:
                # If player is outside range, enemy stands still
                self.x_change = 0
                self.y_change = 0

    def collide_blocks(self, direction):
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                    self.x_change = 0
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right
                    self.x_change = 0
        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                    self.y_change = 0
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom
                    self.y_change = 0

    def animate(self):
        if self.facing == 'down':
            if self.y_change == 0:
                self.image = self.game.enemy_spritesheet.get_sprite(3, 2, self.width, self.height)
            else:
                self.image = self.down_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1

        if self.facing == 'up':
            if self.y_change == 0:
                self.image = self.game.enemy_spritesheet.get_sprite(3, 34, self.width, self.height)
            else:
                self.image = self.up_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1

        if self.facing == 'left':
            if self.x_change == 0:
                self.image = self.game.enemy_spritesheet.get_sprite(3, 98, self.width, self.height)
            else:
                self.image = self.left_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1

        if self.facing == 'right':
            if self.x_change == 0:
                self.image = self.game.enemy_spritesheet.get_sprite(3, 66, self.width, self.height)
            else:
                self.image = self.right_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1

class Devil(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        # AI Pathfinding attributes
        self.speed = ENEMY_SPEED
        self.detection_range = 80  # pixels (increased from 50 for better gameplay)

        self.x_change = 0
        self.y_change = 0

        self.facing = random.choice(['left', 'right', 'up', 'down'])
        self.animation_loop = 1

        self.image = self.game.devil_spritesheet.get_sprite(3, 2, self.width, self.height)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.down_animations = [self.game.devil_spritesheet.get_sprite(3, 2, self.width, self.height),
                           self.game.devil_spritesheet.get_sprite(35, 2, self.width, self.height),
                           self.game.devil_spritesheet.get_sprite(68, 2, self.width, self.height)]

        self.up_animations = [self.game.devil_spritesheet.get_sprite(3, 34, self.width, self.height),
                         self.game.devil_spritesheet.get_sprite(35, 34, self.width, self.height),
                         self.game.devil_spritesheet.get_sprite(68, 34, self.width, self.height)]

        self.left_animations = [self.game.devil_spritesheet.get_sprite(3, 98, self.width, self.height),
                           self.game.devil_spritesheet.get_sprite(35, 98, self.width, self.height),
                           self.game.devil_spritesheet.get_sprite(68, 98, self.width, self.height)]

        self.right_animations = [self.game.devil_spritesheet.get_sprite(3, 66, self.width, self.height),
                            self.game.devil_spritesheet.get_sprite(35, 66, self.width, self.height),
                            self.game.devil_spritesheet.get_sprite(68, 66, self.width, self.height)]

    def update(self):
        """Update enemy with AI pathfinding logic"""
        if self.game.player:
            self.update_ai()
            self.animate()

            # Apply movement with collision detection
            self.rect.x += self.x_change
            self.collide_blocks('x')
            self.rect.y += self.y_change
            self.collide_blocks('y')

            self.x_change = 0
            self.y_change = 0

    def update_ai(self):
        """Update enemy AI logic"""
        if self.game.player:
            player_x = self.game.player.rect.centerx
            player_y = self.game.player.rect.centery

            # Calculate distance to player
            distance = math.sqrt((player_x - self.rect.centerx) **2 + (player_y - self.rect.centery) **2)

            # If player is within detection range, follow them
            if distance <= self.detection_range and distance > 0:
                # Calculate direction vector (normalized)
                direction_x = (player_x - self.rect.centerx) / distance
                direction_y = (player_y - self.rect.centery) / distance

                # Move towards player
                self.x_change = direction_x * self.speed
                self.y_change = direction_y * self.speed

                # Update facing direction based on movement
                if abs(self.x_change) > abs(self.y_change):
                    if self.x_change > 0:
                        self.facing = 'right'
                    else:
                        self.facing = 'left'
                else:
                    if self.y_change > 0:
                        self.facing = 'down'
                    else:
                        self.facing = 'up'
            else:
                # If player is outside range, enemy stands still
                self.x_change = 0
                self.y_change = 0

    def collide_blocks(self, direction):
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                    self.x_change = 0
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right
                    self.x_change = 0
        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                    self.y_change = 0
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom
                    self.y_change = 0

    def animate(self):
        if self.facing == 'down':
            if self.y_change == 0:
                self.image = self.game.devil_spritesheet.get_sprite(3, 2, self.width, self.height)
            else:
                self.image = self.down_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1

        if self.facing == 'up':
            if self.y_change == 0:
                self.image = self.game.devil_spritesheet.get_sprite(3, 34, self.width, self.height)
            else:
                self.image = self.up_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1

        if self.facing == 'left':
            if self.x_change == 0:
                self.image = self.game.devil_spritesheet.get_sprite(3, 98, self.width, self.height)
            else:
                self.image = self.left_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1

        if self.facing == 'right':
            if self.x_change == 0:
                self.image = self.game.devil_spritesheet.get_sprite(3, 66, self.width, self.height)
            else:
                self.image = self.right_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.image = self.game.terrain_spritesheet.get_sprite(960, 448, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.image = self.game.terrain_spritesheet.get_sprite(64, 352, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Button:
    def __init__(self, x, y, width, height, fg, bg, content, fontsize):
        self.font = pygame.font.Font('anime-ace.ttf', fontsize)
        self.content = content

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.fg = fg
        self.bg = bg

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.bg)
        self.rect = self.image.get_rect()

        self.rect.x = self.x
        self.rect.y = self.y

        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect = self.text.get_rect(center=(self.width/2, self.height/2))
        self.image.blit(self.text, self.text_rect)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
            return False
        return False

class Attack(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x
        self.y = y
        self.width = TILESIZE
        self.height = TILESIZE

        self.animation_loop = 0

        self.image = self.game.attack_spritesheet.get_sprite(0, 0, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.right_animations = [self.game.attack_spritesheet.get_sprite(0, 64, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(32, 64, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(64, 64, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(96, 64, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(128, 64, self.width, self.height)]

        self.down_animations = [self.game.attack_spritesheet.get_sprite(0, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(32, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(64, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(96, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(128, 32, self.width, self.height)]

        self.left_animations = [self.game.attack_spritesheet.get_sprite(0, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(32, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(64, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(96, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(128, 96, self.width, self.height)]

        self.up_animations = [self.game.attack_spritesheet.get_sprite(0, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(32, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(64, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(96, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(128, 0, self.width, self.height)]

    def update(self):
        self.animate()
        self.collide()

    def collide(self):
        hits = pygame.sprite.spritecollide(self, self.game.enemies, True)
        if hits:
            self.kill()

    def animate(self):
        direction = self.game.player.facing


        if direction == 'up':
            self.image = self.up_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

        if direction == 'down':
            self.image = self.down_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

        if direction == 'left':
            self.image = self.left_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

        if direction == 'right':
            self.image = self.right_animations[math.floor(self.animation_loop)]
            self.animation_loop += 0.5
            if self.animation_loop >= 5:
                self.kill()

class ItemSprite(pygame.sprite.Sprite):
    """Base class for collectible items in the game world"""
    def __init__(self, game, x, y, item):
        self.game = game
        self._layer = ITEM_LAYER
        self.groups = self.game.all_sprites, self.game.items
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.item = item

        # Load item image or fallback to colored rectangle
        self.image = self.get_item_image()

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def get_item_color(self):
        """Return color based on item type"""
        # Use the item's color property if available, otherwise determine by type
        if hasattr(self.item, 'get_color'):
            return self.item.get_color()
        elif self.item.item_type == "potion":
            if hasattr(self.item, 'name') and 'Health' in self.item.name:
                return RED  # Red for HP potions
            elif hasattr(self.item, 'name') and 'Mana' in self.item.name:
                return BLUE  # Blue for mana potions
            else:
                return GREEN  # Default green for other potions
        elif self.item.item_type == "weapon":
            return RED
        elif self.item.item_type == "collectible":
            return (255, 215, 0)  # Gold color
        else:
            return WHITE

    def get_item_image(self):
        """Load and return the item's image"""
        if hasattr(self.item, 'icon') and self.item.icon:
            try:
                # Load the image from the icon path
                image = pygame.image.load(self.item.icon).convert_alpha()
                # Scale to fit tile size
                return pygame.transform.scale(image, (self.width, self.height))
            except (pygame.error, FileNotFoundError):
                # Fallback to colored rectangle if image loading fails
                pass

        # Fallback to colored rectangle if no icon or loading failed
        fallback_image = pygame.Surface((self.width, self.height))
        fallback_image.fill(self.get_item_color())
        return fallback_image

    def update(self):
        """Check for collision with player"""
        if pygame.sprite.collide_rect(self, self.game.player):
            if self.game.inventory.add_item(self.item):
                self.kill()

class TreasureChest(pygame.sprite.Sprite):
    """Interactive treasure chest that opens when player presses E nearby"""
    def __init__(self, game, x, y):
        self.game = game
        self._layer = TREASURE_LAYER
        self.groups = self.game.all_sprites, self.game.treasure_chests
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        # Load closed chest sprite from chest.png (first 32x32 image)
        self.image = self.game.chest_spritesheet.get_sprite(0, 0, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        # Treasure chest state
        self.is_open = False
        self.interaction_range = 50  # pixels

        # Treasure chest contents (HP and Mana potions)
        self.contents = [
            HealthPotion(),  # Red health potion
            ManaPotion(),    # Blue mana potion
            HealthPotion(),  # Red health potion
            ManaPotion()     # Blue mana potion
        ]

    def update(self):
        """Check for player interaction"""
        if not self.is_open:
            # Check if player is nearby and presses E
            player_distance = math.sqrt(
                (self.game.player.rect.centerx - self.rect.centerx)**2 +
                (self.game.player.rect.centery - self.rect.centery)**2
            )

            if player_distance <= self.interaction_range:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_e]:
                    self.open_chest()

    def open_chest(self):
        """Open the treasure chest and show contents"""
        self.is_open = True
        # Load opened chest sprite from chest.png (second 32x32 image below the first)
        self.image = self.game.chest_spritesheet.get_sprite(0, 32, self.width, self.height)

        # Add all items to player's inventory
        for item in self.contents:
            self.game.inventory.add_item(item)
