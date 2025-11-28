SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILESIZE = 32
FPS = 60

PLAYER_LAYER = 4
ENEMY_LAYER = 3
BLOCK_LAYER = 2
GROUND_LAYER = 1
ITEM_LAYER = 0
TREASURE_LAYER = 1

PLAYER_SPEED = 5
ENEMY_SPEED = 2

RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
AZURE_BLUE = (240, 248, 255)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)


MAX_HP = 6
MAX_MANA = 180
HP_REGEN_RATE = 1
MANA_REGEN_RATE = 2
ATTACK_MANA_COST = 10
DAMAGE_COOLDOWN = 120  # 2 seconds at 60 FPS (120 frames)

# Inventory System Constants
INVENTORY_MAX_SLOTS = 20
INVENTORY_ROWS = 4
INVENTORY_COLS = 5
INVENTORY_SLOT_SIZE = 40
INVENTORY_SLOT_SPACING = 5
INVENTORY_UI_WIDTH = INVENTORY_COLS * (INVENTORY_SLOT_SIZE + INVENTORY_SLOT_SPACING) + INVENTORY_SLOT_SPACING
INVENTORY_UI_HEIGHT = INVENTORY_ROWS * (INVENTORY_SLOT_SIZE + INVENTORY_SLOT_SPACING) + INVENTORY_SLOT_SPACING

# Item spawn characters for tilemap
ITEM_CHARS = {
    'H': 'Health Potion',      # Health potions
    'M': 'Mana Potion',        # Mana potions
    'W': 'Iron Sword',         # Weapons
    'C': 'Gold Coin',           # Collectibles
    'T': 'Treasure Chest'      # Treasure chests
}

# Item spawn rates (probability out of 100)
ITEM_SPAWN_RATES = {
    'H': 15,  # 15% chance for health potions
    'M': 10,  # 10% chance for mana potions
    'W': 5,   # 5% chance for weapons
    'C': 20   # 20% chance for collectibles
}

# Inventory UI Colors
INVENTORY_BG_COLOR = (50, 50, 50, 180)  # Semi-transparent dark gray
INVENTORY_BORDER_COLOR = (200, 200, 200)
INVENTORY_SLOT_COLOR = (80, 80, 80)
INVENTORY_SLOT_HIGHLIGHT = (120, 120, 120)
INVENTORY_TEXT_COLOR = (255, 255, 255)
INVENTORY_ITEM_COUNT_COLOR = (255, 255, 0)

# Treasure Chest UI Constants
TREASURE_UI_WIDTH = 300
TREASURE_UI_HEIGHT = 200
TREASURE_UI_BG_COLOR = (139, 69, 19, 220)  # Brown color for treasure chest UI
TREASURE_UI_BORDER_COLOR = (255, 215, 0)    # Gold border
TREASURE_UI_TEXT_COLOR = (255, 255, 255)    # White text

# In-Game Menu Constants
MENU_BG_COLOR = (0, 0, 0, 180)  # Semi-transparent black
MENU_TEXT_COLOR = (255, 255, 255)  # White text
MENU_BUTTON_COLOR = (100, 100, 100)  # Gray buttons
MENU_BUTTON_HOVER_COLOR = (150, 150, 150)  # Lighter gray on hover
MENU_BUTTON_WIDTH = 450
MENU_BUTTON_HEIGHT = 50
MENU_BUTTON_SPACING = 20
MENU_TITLE_FONT_SIZE = 24
MENU_BUTTON_FONT_SIZE = 16

# Question Barrier Constants
QUESTION_TEXT = "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?"
QUESTION_OPTIONS = ["a. A ghost", "b. An echo", "c. A whistle", "d. A shadow"]
CORRECT_ANSWER = 1  # Index of correct answer (0-based)
QUESTION_UI_WIDTH = 600
QUESTION_UI_HEIGHT = 400
QUESTION_UI_BG_COLOR = (50, 50, 50, 220)  # Semi-transparent dark gray
QUESTION_UI_TEXT_COLOR = (255, 255, 255)  # White text
QUESTION_UI_OPTION_COLOR = (200, 200, 200)  # Light gray for options
QUESTION_UI_SELECTED_COLOR = (255, 255, 0)  # Yellow for selected option

tilemap = [
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
    'B.........B..............D............B...............B...............B.................B....Q.B',
    'B.P.......B....E....D........D........B...............B.....B.........B.......E.........B...T..B',
    'B.........B................B..........................B.....B.........B.................B.E....B',
    'B..BBBBB..B......B..BBBBBBBB..........................BBBBBBB.........B.................B....E.B',
    'B.....B...B......B.........BBBBBBBBBBBBBBB.......E...............B.........................BBBBB',
    'B.....B...G..D...B.........B.............B.......................B..........B..................B',
    'BBBBBBBB..G......B.......................B.......................B..........BBBBBBBBBBBBGGGGGGGB',
    'B.........BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBGGGGGBBBBBBBBBBBBBBBBBBBBB........B..................B',
    'B.........B........B.....................B.....B...................B........B..................B',
    'B.........B........B..............B......B.....B....BBBB...........BBBBBBBBBB..................B',
    'B.........B.......................BBBBBBBB.....B.......B...........B........B..................B',
    'B....BBBBBB..............B..................B..BBBBBBBBBBBBBBB.....B........B.......BBBB.....BBB',
    'B.T..B....BBBBB....BBBBBBB..................B......................B................B..........B',
    'BBBBBB....B...B....B.........BBBBBBBBBBBBBBBB......................B................B..........B',
    'B.........B...B....B.........B..........B..........................B................B..........B',
    'B......T..B........B....BBBBBB.......T..B..........................BBBBBBBBBBBBBBBBBB..........B',
    'B.........B...BBBBBB....B...............BBBBBBBBBBBBBBBBBBBBBB.....B...........................B',
    'B....BBBBBB........B....B.........BBBBBBBB.........................B...........................B',
    'B.........B........B....B.........B................................B...........................B',
    'B.........B........BBBBBB.........B................................B...........................B',
    'B.........B........B..............B...........B.......BBBBBBB......B..........BBBBBBBBBBBBBBBBBB',
    'B.........B........B.....BBBBBBBBBB...........B.......B............B..........B................B',
    'B..............BBBBB.....B..............BBBBBBBBBBBBBBB............B..........B................B',
    'BBBBB..........G.........B..............B..........................B..........B................B',
    'B...B..........G.........B..............B..........................B..........B................B',
    'B...B.....B....BBBBBBBBBBBBBBBBBBBBBBBBBB..........................B..........B................B',
    'B...BBB...B........B.............G.................................B...........................B',
    'B.........B........B.............G.................................B...........................B',
    'BBBBBBB...B........B.............G...........BBBBBBBBBBBBBBB.......B...........................B',
    'B.........B........B.............G...........B.....................BBBBBBBBBBBBBBBBBBB.........B',
    'B.........B..............BBBBBBBBBBBBBBBBBBBBB.....................B.................B.........B',
    'BBBB......B..............B............B...............B............B.................B.........B',
    'B.........B..............B............B...............B............B.........B.......B.........B',
    'B.........B..............B............................B............B.........B.......B.........B',
    'B.........B..............BBBB.........................B............B.........B.......B.........B',
    'B.........B..............B............................B............B.........B.................B',
    'B.........B..............B.......................B....B............B.........B.................B',
    'B...BBBBBBB..............B....BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB......B.........B.................B',
    'B.........B....BBBBBBBBBBB....B..........................B.........B.........BBBBBBBBBBBBBBBBBBB',
    'B.........B.....B........B....B..........................B.........B...........................B',
    'B.........B.....B...T...............B............BBBBBBBBB.........B...........................B',
    'B.........B.....B...................B............B.................BBBBBBBBBBBBBBBBB...........B',
    'B.....BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB.......BBBBBBBBBBBBBBBBBBBBBBBB...............B.....T.....B',
    'B........B...............B..........B.......B......................................B...........B',
    'B........BBBBBB..........B.......T..B.......B.............B........................BBBBBBBBBBBBB',
    'B........B...............B.....BBBBBB.......B.............BBBBBBBBBBBBBBBBBBB..................B',
    'BBBBBBBBBB..........B....B..................BBBBBBBBBBBBBBB....................................B',
    'B...............T...B....BBBBBB...........................B........................BBBBBBBB....B',
    'B...................B.........G....................................................B...........B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
]
