import pygame
from sprite import *
from config import *
import sys
from inventory import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font('anime-ace.ttf', 32)

        # Camera system
        self.camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        self.character_spritesheet = Spritesheet('img/knight.png')
        self.terrain_spritesheet = Spritesheet('img/terrain2.png')
        self.enemy_spritesheet = Spritesheet('img/zombie.png')
        self.attack_spritesheet = Spritesheet('img/attack.png')
        self.chest_spritesheet = Spritesheet('img/chest.png')
        self.intro_background = pygame.image.load('img/introbackground2.png')
        self.go_background = pygame.image.load('img/gameover.png')
        self.devil_spritesheet = Spritesheet('img/devil.png')
        pygame.mixer.music.load("Music/background_music.mp3")
        pygame.mixer.music.play(-1)


        # Inventory system
        self.inventory = Inventory(INVENTORY_MAX_SLOTS)
        self.show_inventory = False

    def createTilemap(self):
        for i, row in enumerate(tilemap):
            for j, col in enumerate(row):
                Ground(self, j, i)
                if col == 'B':
                    Block(self, j, i)
                if col == 'E':
                    Enemy(self, j, i)
                if col == "D":
                    Devil(self, j ,i) 
                if col == 'P':
                    self.player = Player(self, j, i)
                if col == 'T':
                    TreasureChest(self, j, i)  # Spawn treasure chest
                # Spawn items based on tilemap characters
                elif col in ITEM_CHARS:
                    self.spawn_item(j, i, col)

    def spawn_item(self, x, y, item_char):
        """Spawn an item at the specified location"""
        item_name = ITEM_CHARS[item_char]

        # Create appropriate item based on character
        if item_char == 'H':
            item = HealthPotion()
        elif item_char == 'M':
            item = ManaPotion()
        elif item_char == 'W':
            item = Weapon("Iron Sword", 2)
        elif item_char == 'C':
            item = Collectible("Gold Coin", 10)
        else:
            return

        # Create item sprite
        ItemSprite(self, x, y, item)

    def new(self):
        # Initialize a new game
        self.playing = True

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.devil = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.items = pygame.sprite.LayeredUpdates()  # Item sprites
        self.treasure_chests = pygame.sprite.LayeredUpdates()  # Treasure chests

        self.createTilemap()

    def events(self):
        #game loop events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Check if player has enough mana to attack
                    if self.player.can_attack():
                        self.player.use_mana(ATTACK_MANA_COST)
                        if self.player.facing == 'up':
                            Attack(self, self.player.rect.x, self.player.rect.y - TILESIZE)
                        if self.player.facing == 'down':
                            Attack(self, self.player.rect.x, self.player.rect.y + TILESIZE)
                        if self.player.facing == 'left':
                            Attack(self, self.player.rect.x - TILESIZE, self.player.rect.y)
                        if self.player.facing == 'right':
                            Attack(self, self.player.rect.x + TILESIZE, self.player.rect.y)
                elif event.key == pygame.K_i:
                    # Toggle inventory display
                    self.show_inventory = not self.show_inventory
                elif event.key == pygame.K_h:
                    # Use health potion
                    if self.inventory.use_hp_potion():
                        self.player.use_hp_potion()
                elif event.key == pygame.K_m:
                    # Use mana potion
                    if self.inventory.use_mana_potion():
                        self.player.use_mana_potion()

    def update(self):
        #game loop updates
        self.all_sprites.update()
        self.update_camera()

    def update_camera(self):
        """Update camera position to follow player"""
        if self.player:
            # Center camera on player
            self.camera.centerx = self.player.rect.centerx
            self.camera.centery = self.player.rect.centery

            # Keep camera within world bounds
            self.camera.x = max(0, min(self.camera.x, len(tilemap[0]) * TILESIZE - SCREEN_WIDTH))
            self.camera.y = max(0, min(self.camera.y, len(tilemap) * TILESIZE - SCREEN_HEIGHT))

    def draw(self):
        #game loop draw
        self.screen.fill((BLACK))

        # Draw all sprites with camera offset
        for sprite in self.all_sprites:
            offset_x = sprite.rect.x - self.camera.x
            offset_y = sprite.rect.y - self.camera.y
            self.screen.blit(sprite.image, (offset_x, offset_y))

        # Draw HP and Mana bars
        self.draw_ui()

        # Draw inventory if toggled
        if self.show_inventory:
            self.draw_inventory()

        # Draw treasure chest interaction prompt
        self.draw_treasure_prompt()

        self.clock.tick(FPS)
        pygame.display.update()

    def draw_ui(self):
        """Draw HP and Mana bars on screen"""
        bar_width = 200
        bar_height = 20
        ui_x = 10
        ui_y = SCREEN_HEIGHT - 150  # Position bars higher up

        # HP Bar (Red)
        # Background
        pygame.draw.rect(self.screen, RED, (ui_x, ui_y, bar_width, bar_height))
        # Current HP
        hp_ratio = self.player.current_hp / self.player.max_hp
        hp_width = int(bar_width * hp_ratio)
        pygame.draw.rect(self.screen, GREEN, (ui_x, ui_y, hp_width, bar_height))
        # Border
        pygame.draw.rect(self.screen, WHITE, (ui_x, ui_y, bar_width, bar_height), 2)

        # HP Text
        hp_text = self.font.render(f'{self.player.current_hp}/{self.player.max_hp}', True, WHITE)
        self.screen.blit(hp_text, (ui_x, ui_y + bar_height + 5))

        # Mana Bar (Blue)
        mana_y = ui_y + bar_height + 35
        # Background
        pygame.draw.rect(self.screen, BLUE, (ui_x, mana_y, bar_width, bar_height))
        # Current Mana
        mana_ratio = self.player.current_mana / self.player.max_mana
        mana_width = int(bar_width * mana_ratio)
        pygame.draw.rect(self.screen, WHITE, (ui_x, mana_y, mana_width, bar_height))
        # Border
        pygame.draw.rect(self.screen, WHITE, (ui_x, mana_y, bar_width, bar_height), 2)

        # Mana Text
        mana_text = self.font.render(f'{self.player.current_mana}/{self.player.max_mana}', True, WHITE)
        self.screen.blit(mana_text, (ui_x, mana_y + bar_height + 5))

        # Potion Counter (right side, aligned with bars)
        self.draw_potion_counter(ui_x + bar_width + 10, ui_y)

    def draw_potion_counter(self, x, y):
        """Draw potion counter showing available potions"""
        # Count health and mana potions
        hp_potions = sum(item.quantity for item in self.inventory.items
                        if hasattr(item, 'name') and 'Health' in item.name)
        mana_potions = sum(item.quantity for item in self.inventory.items
                          if hasattr(item, 'name') and 'Mana' in item.name)

        # Draw health potion counter (higher)
        hp_text = self.font.render(f"HP Potions: {hp_potions}", True, RED)
        self.screen.blit(hp_text, (x, y - 5))

        # Draw mana potion counter (lower)
        mana_text = self.font.render(f"Mana Potions: {mana_potions}", True, BLUE)
        self.screen.blit(mana_text, (x, y + 30))

    def draw_inventory(self):
        """Draw inventory UI"""
        # Draw inventory background
        inventory_x = (SCREEN_WIDTH - INVENTORY_UI_WIDTH) // 2
        inventory_y = (SCREEN_HEIGHT - INVENTORY_UI_HEIGHT) // 2

        # Semi-transparent background
        inventory_surface = pygame.Surface((INVENTORY_UI_WIDTH, INVENTORY_UI_HEIGHT))
        inventory_surface.fill(INVENTORY_BG_COLOR[:3])
        inventory_surface.set_alpha(INVENTORY_BG_COLOR[3])
        self.screen.blit(inventory_surface, (inventory_x, inventory_y))

        # Draw inventory slots
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                slot_x = inventory_x + col * (INVENTORY_SLOT_SIZE + INVENTORY_SLOT_SPACING) + INVENTORY_SLOT_SPACING
                slot_y = inventory_y + row * (INVENTORY_SLOT_SIZE + INVENTORY_SLOT_SPACING) + INVENTORY_SLOT_SPACING

                # Draw slot background
                pygame.draw.rect(self.screen, INVENTORY_SLOT_COLOR,
                               (slot_x, slot_y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE))

                # Draw slot border
                pygame.draw.rect(self.screen, INVENTORY_BORDER_COLOR,
                               (slot_x, slot_y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE), 2)

                # Get item index
                item_index = row * INVENTORY_COLS + col

                # Draw item if exists
                if item_index < len(self.inventory.items):
                    item = self.inventory.items[item_index]

                    # Draw item icon if available
                    if hasattr(item, 'icon') and item.icon:
                        try:
                            # Load and scale the item icon
                            item_image = pygame.image.load(item.icon).convert_alpha()
                            item_image = pygame.transform.scale(item_image, (INVENTORY_SLOT_SIZE - 4, INVENTORY_SLOT_SIZE - 4))
                            self.screen.blit(item_image, (slot_x + 2, slot_y + 2))
                        except (pygame.error, FileNotFoundError):
                            # Fallback to colored rectangle if image loading fails
                            item_color = GREEN if item.item_type == "potion" else \
                                        RED if item.item_type == "weapon" else \
                                        (255, 215, 0) if item.item_type == "collectible" else WHITE
                            pygame.draw.rect(self.screen, item_color,
                                           (slot_x + 2, slot_y + 2, INVENTORY_SLOT_SIZE - 4, INVENTORY_SLOT_SIZE - 4))
                    else:
                        # Fallback to colored rectangle if no icon
                        item_color = GREEN if item.item_type == "potion" else \
                                    RED if item.item_type == "weapon" else \
                                    (255, 215, 0) if item.item_type == "collectible" else WHITE
                        pygame.draw.rect(self.screen, item_color,
                                       (slot_x + 2, slot_y + 2, INVENTORY_SLOT_SIZE - 4, INVENTORY_SLOT_SIZE - 4))

                    # Draw item count if > 1
                    if item.quantity > 1:
                        count_text = self.font.render(str(item.quantity), True, INVENTORY_ITEM_COUNT_COLOR)
                        count_rect = count_text.get_rect(bottomright=(slot_x + INVENTORY_SLOT_SIZE - 2, slot_y + INVENTORY_SLOT_SIZE - 2))
                        self.screen.blit(count_text, count_rect)

        # Draw inventory title
        title_text = self.font.render("Inventory (Press I to close)", True, INVENTORY_TEXT_COLOR)
        title_rect = title_text.get_rect(centerx=SCREEN_WIDTH // 2, top=inventory_y - 40)
        self.screen.blit(title_text, title_rect)

        # Draw inventory info
        info_text = self.font.render(f"Items: {len(self.inventory.items)}/{self.inventory.max_slots}", True, INVENTORY_TEXT_COLOR)
        info_rect = info_text.get_rect(centerx=SCREEN_WIDTH // 2, top=inventory_y + INVENTORY_UI_HEIGHT + 10)
        self.screen.blit(info_text, info_rect)

    def draw_treasure_prompt(self):
        """Draw prompt to interact with nearby treasure chests"""
        if self.player:
            # Check if player is near any treasure chest
            for chest in self.treasure_chests:
                if not chest.is_open:
                    player_distance = math.sqrt(
                        (self.player.rect.centerx - chest.rect.centerx)**2 +
                        (self.player.rect.centery - chest.rect.centery)**2
                    )

                    if player_distance <= chest.interaction_range:
                        # Draw interaction prompt
                        prompt_text = self.font.render("Press E to open treasure chest", True, WHITE)
                        prompt_rect = prompt_text.get_rect(centerx=SCREEN_WIDTH // 2, top=50)
                        self.screen.blit(prompt_text, prompt_rect)
                        break

    def main(self):
        #gameloop
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def game_over(self):
        text = self.font.render('Game Over', True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

        restart_button = Button(10, SCREEN_HEIGHT - 60, 120, 50, WHITE, BLACK, 'Restart', 20)

        for sprite in self.all_sprites:
            sprite.kill()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if restart_button.is_pressed(mouse_pos, mouse_pressed):
                self.new()
                self.main()

            self.screen.blit(self.go_background, (0,0))
            self.screen.blit(text, text_rect)
            self.screen.blit(restart_button.image, restart_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def intro_screen(self):
        intro = True

        title = self.font.render('Prototype Ni Andrei', True, WHITE)
        title_rect = title.get_rect(x=10, y=10)

        play_button = Button(10, 50, 100, 50, WHITE, BLACK, 'Play', 32)

        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if play_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False

            self.screen.blit(self.intro_background, (0,0))
            self.screen.blit(title, title_rect)
            self.screen.blit(play_button.image, play_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

g = Game()
g.intro_screen()
g.new()
while g.running:
    g.main()
    g.game_over()

pygame.quit()
sys.exit()