import pygame
from sprite import *
from config import *
import sys
import os
from datetime import datetime
from inventory import *
from PIL import Image

class Game:
    def __init__(self):
        pygame.init()
        # Get display info for fullscreen resolution
        display_info = pygame.display.Info()
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH = display_info.current_w
        SCREEN_HEIGHT = display_info.current_h
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font('darkbyte.ttf', 16)

        # Camera system
        self.camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        self.character_spritesheet = Spritesheet('img/knight.png')
        self.terrain_spritesheet = Spritesheet('img/terrain2.png')
        self.enemy_spritesheet = Spritesheet('img/zombie.png')
        self.attack_spritesheet = Spritesheet('img/attack.png')
        self.chest_spritesheet = Spritesheet('img/chest.png')
        # Load animated GIF frames
        self.intro_background_frames = []
        self.intro_background_durations = []
        self.intro_background_frame = 0
        self.intro_background_timer = 0

        gif = Image.open('img/introbackground3.gif')
        try:
            while True:
                frame = gif.convert('RGBA')
                pygame_frame = pygame.image.fromstring(frame.tobytes(), frame.size, 'RGBA')
                # Scale the frame to fill the screen
                pygame_frame = pygame.transform.scale(pygame_frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.intro_background_frames.append(pygame_frame)
                duration = gif.info.get('duration', 100)  # Get frame duration in ms, default 100
                self.intro_background_durations.append(duration)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        gif.close()

        if self.intro_background_frames:
            self.intro_background = self.intro_background_frames[0]
        else:
            self.intro_background = pygame.transform.scale(pygame.image.load('img/introbackground3.gif'), (SCREEN_WIDTH, SCREEN_HEIGHT))  # fallback scaled
        self.go_background = pygame.image.load('img/gameover.png')
        self.devil_spritesheet = Spritesheet('img/devil.png')
        pygame.mixer.music.load("Music/background_music.mp3")
        pygame.mixer.music.play(-1)

        # Inventory system
        self.inventory = Inventory(INVENTORY_MAX_SLOTS)
        self.show_inventory = False

        # In-game menu system
        self.show_menu = False
        self.music_paused = False
        self.selected_button = 0  # Index of selected menu button (0: Save, 1: Music, 2: Return to Game, 3: Quit)
        self.return_to_menu = False

        # Question barrier system
        self.show_question_ui = False
        self.question_barrier = None
        self.selected_option = 0

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

        # Hide mouse cursor during gameplay
        pygame.mouse.set_visible(False)

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
                elif event.key == pygame.K_h and self.show_inventory:
                    # Use health potion
                    if self.inventory.use_hp_potion(self.player):
                        pass  # Potion used successfully
                elif event.key == pygame.K_m and self.show_inventory:
                    # Use mana potion
                    if self.inventory.use_mana_potion(self.player):
                        pass  # Potion used successfully
                elif event.key == pygame.K_ESCAPE:
                    # Toggle in-game menu
                    self.show_menu = not self.show_menu
                    if self.show_menu:
                        self.selected_button = 0  # Reset selection when opening menu
                elif self.show_menu and event.key in [pygame.K_UP, pygame.K_w]:
                    # Navigate up in menu
                    self.selected_button = (self.selected_button - 1) % 4
                elif self.show_menu and event.key in [pygame.K_DOWN, pygame.K_s]:
                    # Navigate down in menu
                    self.selected_button = (self.selected_button + 1) % 4
                elif self.show_menu and event.key == pygame.K_RETURN:
                    # Select current button
                    if self.selected_button == 0:  # Save Game
                        self.save_game()
                    elif self.selected_button == 1:  # Toggle Music
                        self.toggle_music()
                    elif self.selected_button == 2:  # Return to Game
                        self.show_menu = False
                    elif self.selected_button == 3:  # Quit Game
                        self.playing = False
                        self.running = False
                elif self.show_question_ui and event.key in [pygame.K_UP, pygame.K_w]:
                    # Navigate up in question options
                    self.selected_option = (self.selected_option - 1) % len(self.question_barrier.options)
                elif self.show_question_ui and event.key in [pygame.K_DOWN, pygame.K_s]:
                    # Navigate down in question options
                    self.selected_option = (self.selected_option + 1) % len(self.question_barrier.options)
                elif self.show_question_ui and event.key == pygame.K_RETURN:
                    # Select current option
                    if self.question_barrier:
                        self.question_barrier.select_option(self.selected_option)
                        self.show_question_ui = False
                        self.question_barrier = None
                        self.selected_option = 0

            if event.type == pygame.MOUSEBUTTONDOWN and self.show_menu:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    for i, button_rect in enumerate(self.menu_buttons):
                        if button_rect.collidepoint(mouse_pos):
                            if i == 0:  # Save Game
                                self.save_game()
                            elif i == 1:  # Toggle Music
                                self.toggle_music()
                            elif i == 2:  # Return to Game
                                self.show_menu = False
                            elif i == 3:  # Quit Game
                                self.playing = False
                                self.running = False
                            break

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

        # Draw in-game menu if active
        if self.show_menu:
            self.draw_menu()

        # Draw question UI if active
        if self.show_question_ui:
            self.draw_question_ui()

        self.clock.tick(FPS)
        pygame.display.update()

    def draw_ui(self):
        """Draw HP and Mana bars on screen"""
        bar_width = 200
        bar_height = 25
        ui_x = SCREEN_WIDTH - 220  # Position bars on the right
        ui_y = 50  # Position bars at the top

        # HP Bar (Red)
        # Background
        pygame.draw.rect(self.screen, RED, (ui_x, ui_y, bar_width, bar_height))
        # Current HP
        hp_ratio = self.player.current_hp / self.player.max_hp
        hp_width = int(bar_width * hp_ratio)
        pygame.draw.rect(self.screen, GREEN, (ui_x, ui_y, hp_width, bar_height))
        # Border
        pygame.draw.rect(self.screen, BLACK, (ui_x, ui_y, bar_width, bar_height), 3)

        # HP Text
        hp_text = self.font.render(f'{self.player.current_hp}/{self.player.max_hp}', False, WHITE)
        hp_text_rect = hp_text.get_rect(center=(ui_x + bar_width // 2, ui_y + bar_height + 15))
        self.screen.blit(hp_text, hp_text_rect)

        # Mana Bar (Azure Blue)
        mana_y = ui_y + bar_height + 50
        # Background
        pygame.draw.rect(self.screen, AZURE_BLUE, (ui_x, mana_y, bar_width, bar_height))
        # Current Mana
        mana_ratio = self.player.current_mana / self.player.max_mana
        mana_width = int(bar_width * mana_ratio)
        pygame.draw.rect(self.screen, BLUE, (ui_x, mana_y, mana_width, bar_height))
        # Border
        pygame.draw.rect(self.screen, BLACK, (ui_x, mana_y, bar_width, bar_height), 3)

        # Mana Text
        mana_text = self.font.render(f'{self.player.current_mana}/{self.player.max_mana}', False, WHITE)
        mana_text_rect = mana_text.get_rect(center=(ui_x + bar_width // 2, mana_y + bar_height + 15))
        self.screen.blit(mana_text, mana_text_rect)

        # Potion Counter removed

    def draw_potion_counter(self, x, y):
        """Draw potion counter showing available potions"""
        # Count health and mana potions
        hp_potions = sum(item.quantity for item in self.inventory.items
                        if hasattr(item, 'name') and 'Health' in item.name)
        mana_potions = sum(item.quantity for item in self.inventory.items
                          if hasattr(item, 'name') and 'Mana' in item.name)

        # Draw health potion counter (higher)
        hp_text = self.font.render(f"HP Potions: {hp_potions}", False, RED)
        self.screen.blit(hp_text, (x, y - 5))

        # Draw mana potion counter (lower)
        mana_text = self.font.render(f"Mana Potions: {mana_potions}", False, BLUE)
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
                        count_text = self.font.render(str(item.quantity), False, INVENTORY_ITEM_COUNT_COLOR)
                        count_rect = count_text.get_rect(bottomright=(slot_x + INVENTORY_SLOT_SIZE - 2, slot_y + INVENTORY_SLOT_SIZE - 2))
                        self.screen.blit(count_text, count_rect)

        # Draw inventory title
        title_text = self.font.render("Inventory (Press I to close)", False, INVENTORY_TEXT_COLOR)
        title_rect = title_text.get_rect(centerx=SCREEN_WIDTH // 2, top=inventory_y - 40)
        self.screen.blit(title_text, title_rect)

        # Draw inventory info
        info_text = self.font.render(f"Items: {len(self.inventory.items)}/{self.inventory.max_slots}", False, INVENTORY_TEXT_COLOR)
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
                        prompt_text = self.font.render("Press E to open treasure chest", False, WHITE)
                        prompt_rect = prompt_text.get_rect(centerx=SCREEN_WIDTH // 2, top=50)
                        self.screen.blit(prompt_text, prompt_rect)
                        break

    def draw_menu(self):
        """Draw the in-game menu overlay"""
        # Semi-transparent background
        menu_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        menu_surface.fill(MENU_BG_COLOR[:3])
        menu_surface.set_alpha(MENU_BG_COLOR[3])
        self.screen.blit(menu_surface, (0, 0))

        # Menu title
        title_font = pygame.font.Font('darkbyte.ttf', MENU_TITLE_FONT_SIZE)
        title_text = title_font.render("Game Menu", False, MENU_TEXT_COLOR)
        title_rect = title_text.get_rect(centerx=SCREEN_WIDTH // 2, top=100)
        self.screen.blit(title_text, title_rect)

        # Menu buttons
        button_font = pygame.font.Font('darkbyte.ttf', MENU_BUTTON_FONT_SIZE)
        buttons = [
            ("Save Game", SCREEN_HEIGHT // 2 - 100),
            ("Music: " + ("Off" if self.music_paused else "On"), SCREEN_HEIGHT // 2 - 100 + MENU_BUTTON_HEIGHT + MENU_BUTTON_SPACING),
            ("Return to Game", SCREEN_HEIGHT // 2 - 100 + 2 * (MENU_BUTTON_HEIGHT + MENU_BUTTON_SPACING)),
            ("Quit Game", SCREEN_HEIGHT // 2 - 100 + 3 * (MENU_BUTTON_HEIGHT + MENU_BUTTON_SPACING))
        ]

        self.menu_buttons = []
        for i, (text, y) in enumerate(buttons):
            button_rect = pygame.Rect(
                (SCREEN_WIDTH - MENU_BUTTON_WIDTH) // 2,
                y,
                MENU_BUTTON_WIDTH,
                MENU_BUTTON_HEIGHT
            )
            self.menu_buttons.append(button_rect)

            # Check if mouse is hovering over button or if it's selected via keyboard
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = button_rect.collidepoint(mouse_pos)
            is_selected = (i == self.selected_button)
            button_color = MENU_BUTTON_HOVER_COLOR if (is_hovered or is_selected) else MENU_BUTTON_COLOR

            # Draw button
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, WHITE, button_rect, 2)

            # Draw button text
            button_text = button_font.render(text, False, MENU_TEXT_COLOR)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)

        # Instructions
        instr_text = self.font.render("Use Arrow/WASD keys to navigate, Enter to select, ESC to close", False, MENU_TEXT_COLOR)
        instr_rect = instr_text.get_rect(centerx=SCREEN_WIDTH // 2, top=SCREEN_HEIGHT - 100)
        self.screen.blit(instr_text, instr_rect)

    def draw_question_ui(self):
        """Draw the question UI overlay"""
        if not self.question_barrier:
            return

        # Semi-transparent background
        ui_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        ui_surface.fill((0, 0, 0))
        ui_surface.set_alpha(150)
        self.screen.blit(ui_surface, (0, 0))

        # Question box
        box_width = 600
        box_height = 400
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2

        # Draw box background
        pygame.draw.rect(self.screen, (50, 50, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height), 3)

        # Question text
        question_font = pygame.font.Font('darkbyte.ttf', 24)
        question_text = question_font.render(self.question_barrier.question, False, WHITE)
        question_rect = question_text.get_rect(centerx=SCREEN_WIDTH // 2, top=box_y + 30)
        self.screen.blit(question_text, question_rect)

        # Options
        option_font = pygame.font.Font('darkbyte.ttf', 20)
        for i, option in enumerate(self.question_barrier.options):
            color = YELLOW if i == self.selected_option else WHITE
            option_text = option_font.render(f"{chr(65 + i)}. {option}", False, color)
            option_rect = option_text.get_rect(centerx=SCREEN_WIDTH // 2, top=box_y + 100 + i * 40)
            self.screen.blit(option_text, option_rect)

        # Instructions
        instr_text = self.font.render("Use Up/Down to navigate, Enter to select", False, WHITE)
        instr_rect = instr_text.get_rect(centerx=SCREEN_WIDTH // 2, top=box_y + box_height - 50)
        self.screen.blit(instr_text, instr_rect)

    def save_game(self, slot=1):
        """Save the current game state to a file"""
        import pickle
        save_data = {
            'player_hp': self.player.current_hp,
            'player_mana': self.player.current_mana,
            'player_x': self.player.rect.x,
            'player_y': self.player.rect.y,
            'inventory': self.inventory.items,
            'music_paused': self.music_paused
        }
        try:
            with open(f'save{slot}.pkl', 'wb') as f:
                pickle.dump(save_data, f)
            print(f"Game saved to slot {slot} successfully!")
        except Exception as e:
            print(f"Failed to save game: {e}")

    def load_game(self, filename):
        """Load the game state from a file"""
        import pickle
        try:
            with open(filename, 'rb') as f:
                save_data = pickle.load(f)
            self.player.current_hp = save_data['player_hp']
            self.player.current_mana = save_data['player_mana']
            self.player.rect.x = save_data['player_x']
            self.player.rect.y = save_data['player_y']
            self.inventory.items = save_data['inventory']
            self.music_paused = save_data['music_paused']
            if self.music_paused:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
            print("Game loaded successfully!")
        except Exception as e:
            print(f"Failed to load game: {e}")

    def toggle_music(self):
        """Toggle background music on/off"""
        if self.music_paused:
            pygame.mixer.music.unpause()
            self.music_paused = False
        else:
            pygame.mixer.music.pause()
            self.music_paused = True

    def main(self):
        #gameloop
        while self.playing:
            self.events()
            if not self.show_menu:
                self.update()
            self.draw()

    def game_over(self):
        text = self.font.render('Game Over', False, WHITE)
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

    def main_menu(self):
        menu_running = True
        self.selected_button = 0
        buttons = ["Start", "Continue", "Options", "Quit"]
        self.show_continue_menu = False
        self.continue_selected = 0

        # Removed main menu title

        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_running = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        if self.show_continue_menu:
                            self.continue_selected = (self.continue_selected - 1) % 4  # 3 saves + back
                        else:
                            self.selected_button = (self.selected_button - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        if self.show_continue_menu:
                            self.continue_selected = (self.continue_selected + 1) % 4
                        else:
                            self.selected_button = (self.selected_button + 1) % 4
                    elif event.key == pygame.K_RETURN:
                        if self.show_continue_menu:
                            if self.continue_selected == 3:  # Back
                                self.show_continue_menu = False
                            else:
                                # Load save
                                save_file = f'save{self.continue_selected + 1}.pkl'
                                if os.path.exists(save_file):
                                    self.load_game(save_file)
                                    menu_running = False
                        else:
                            if self.selected_button == 0:  # Start
                                menu_running = False
                            elif self.selected_button == 1:  # Continue
                                self.show_continue_menu = True
                                self.continue_selected = 0
                            elif self.selected_button == 2:  # Options
                                pass  # Placeholder
                            elif self.selected_button == 3:  # Quit
                                menu_running = False
                                self.running = False
                    elif event.key == pygame.K_ESCAPE:
                        if self.show_continue_menu:
                            self.show_continue_menu = False
                        else:
                            menu_running = False
                            self.running = False

            # Update GIF animation
            if self.intro_background_frames:
                self.intro_background_timer += self.clock.get_time()
                current_duration = self.intro_background_durations[self.intro_background_frame] if self.intro_background_durations else 100
                if self.intro_background_timer >= current_duration:
                    self.intro_background_timer = 0
                    self.intro_background_frame = (self.intro_background_frame + 1) % len(self.intro_background_frames)
                    self.intro_background = self.intro_background_frames[self.intro_background_frame]

            self.screen.blit(self.intro_background.convert_alpha(), (0,0))

            if self.show_continue_menu:
                self.draw_continue_menu()
            else:
                self.draw_main_menu_buttons(buttons)

            self.clock.tick(FPS)
            pygame.display.update()

    def draw_main_menu_buttons(self, buttons):
        button_font = pygame.font.Font('darkbyte.ttf', 40)
        for i, button_text in enumerate(buttons):
            color = WHITE if i == self.selected_button else GRAY
            text = button_font.render(button_text, False, color)
            extra_space = 60 if i == 3 else 30 if i == 2 else 20 if i == 1 else 0
            rect = text.get_rect(centerx=SCREEN_WIDTH // 2, centery=600 + i * 90 + extra_space)
            self.screen.blit(text, rect)

    def draw_continue_menu(self):
        continue_title_font = pygame.font.Font('darkbyte.ttf', 40)
        title = continue_title_font.render('Select Save File', False, WHITE)
        title_rect = title.get_rect(centerx=SCREEN_WIDTH // 2, y=150)
        self.screen.blit(title, title_rect)

        button_font = pygame.font.Font('darkbyte.ttf', 40)
        for i in range(3):
            save_file = f'save{i+1}.pkl'
            if os.path.exists(save_file):
                # Get save date
                mod_time = os.path.getmtime(save_file)
                date_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M')
                text = f'Save {i+1}: {date_str}'
            else:
                text = f'Save {i+1}: Empty'
            color = WHITE if i == self.continue_selected else GRAY
            text_surf = button_font.render(text, False, color)
            rect = text_surf.get_rect(centerx=SCREEN_WIDTH // 2, centery=200 + i * 60)
            self.screen.blit(text_surf, rect)

        # Back option
        color = WHITE if 3 == self.continue_selected else GRAY
        back_text = button_font.render('Back', False, color)
        back_rect = back_text.get_rect(centerx=SCREEN_WIDTH // 2, centery=200 + 3 * 60)
        self.screen.blit(back_text, back_rect)

g = Game()
g.main_menu()
g.new()
while g.running:
    g.main()
    if g.return_to_menu:
        g.return_to_menu = False
        g.main_menu()
        g.new()
    else:
        g.game_over()

pygame.quit()
sys.exit()