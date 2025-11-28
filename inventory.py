import pygame
from config import *

class Inventory:
    def __init__(self, max_slots=20):
        self.max_slots = max_slots
        self.items = []  # Array to store inventory items
        self.selected_slot = 0

    def add_item(self, item):
        """Add item to inventory if there's space"""
        if len(self.items) < self.max_slots:
            self.items.append(item)
            return True
        return False

    def remove_item(self, index):
        """Remove item from inventory at specified index"""
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None

    def get_item(self, index):
        """Get item from inventory at specified index"""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def has_item(self, item_type):
        """Check if inventory contains specific item type"""
        return any(item.item_type == item_type for item in self.items)

    def get_items_by_type(self, item_type):
        """Get all items of a specific type"""
        return [item for item in self.items if item.item_type == item_type]

    def use_item(self, index):
        """Use item at specified index"""
        item = self.get_item(index)
        if item and item.use():
            self.remove_item(index)
            return True
        return False

    def get_inventory_array(self):
        """Return inventory as array for easy access"""
        return self.items.copy()

    def is_full(self):
        """Check if inventory is full"""
        return len(self.items) >= self.max_slots

    def get_empty_slots(self):
        """Get number of empty slots"""
        return self.max_slots - len(self.items)

    def clear_inventory(self):
        """Clear all items from inventory"""
        self.items.clear()
        self.selected_slot = 0

    def use_hp_potion(self, player):
        """Use a health potion from inventory"""
        for i, item in enumerate(self.items):
            if hasattr(item, 'name') and 'Health' in item.name:
                if player.use_hp_potion():
                    self.remove_item(i)
                    return True
        return False

    def use_mana_potion(self, player):
        """Use a mana potion from inventory"""
        for i, item in enumerate(self.items):
            if hasattr(item, 'name') and 'Mana' in item.name:
                if player.use_mana_potion():
                    self.remove_item(i)
                    return True
        return False

class Item:
    def __init__(self, name, item_type, description, icon=None, color=None):
        self.name = name
        self.item_type = item_type
        self.description = description
        self.icon = icon
        self.quantity = 1
        self.color = color or WHITE  # Default to white if no color specified

    def use(self):
        """Use the item - override in subclasses"""
        return False

    def get_display_name(self):
        """Get display name with quantity if > 1"""
        if self.quantity > 1:
            return f"{self.name} ({self.quantity})"
        return self.name

    def get_color(self):
        """Get the color of this item"""
        return self.color

class HealthPotion(Item):
    def __init__(self, heal_amount=2):
        super().__init__("Health Potion", "potion", f"Restores {heal_amount} HP", icon='img/hp_potion.png', color=RED)
        self.heal_amount = heal_amount

    def use(self):
        """Use health potion to restore HP"""
        # This will be implemented when we integrate with player
        return True

class ManaPotion(Item):
    def __init__(self, restore_amount=20):
        super().__init__("Mana Potion", "potion", f"Restores {restore_amount} Mana", icon='img/mana_potion.png', color=BLUE)
        self.restore_amount = restore_amount

    def use(self):
        """Use mana potion to restore mana"""
        # This will be implemented when we integrate with player
        return True

class Weapon(Item):
    def __init__(self, name, attack_bonus=1):
        super().__init__(name, "weapon", f"Increases attack by {attack_bonus}", color=RED)
        self.attack_bonus = attack_bonus

    def use(self):
        """Equip weapon to increase attack power"""
        # This will be implemented when we integrate with player
        return True

class Collectible(Item):
    def __init__(self, name, points=10):
        super().__init__(name, "collectible", f"Worth {points} points", color=(255, 215, 0))
        self.points = points

    def use(self):
        """Collectible items are used automatically when picked up"""
        return True
