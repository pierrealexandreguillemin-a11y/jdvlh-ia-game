"""
Inventory Manager - Manages player inventory and equipment
Handles adding/removing items, equipping/unequipping, and crafting
"""

from typing import List, Dict, Optional, Tuple
from ..models.game_entities import Player, Item, ItemType, ItemRarity


# ============================================================================
# EQUIPMENT SLOTS
# ============================================================================

EQUIPMENT_SLOTS = {
    "head": "Casque",
    "chest": "Plastron",
    "legs": "Jambières",
    "feet": "Bottes",
    "weapon_main": "Arme principale",
    "weapon_off": "Arme secondaire / Bouclier",
    "ring_1": "Anneau 1",
    "ring_2": "Anneau 2",
}


# ============================================================================
# INVENTORY MANAGER
# ============================================================================


class InventoryManager:
    """Manages player inventory and equipment"""

    def __init__(self):
        self.max_inventory_size = 50

    def add_item(self, player: Player, item: Item) -> Dict[str, any]:
        """
        Add item to player inventory

        Args:
            player: The player
            item: The item to add

        Returns:
            Dict with success status and message
        """

        # Check if stackable
        if item.stackable:
            existing_item = self._find_item_by_id(player, item.item_id)
            if existing_item:
                existing_item.quantity += item.quantity
                return {
                    "success": True,
                    "message": f"{item.name} x{item.quantity} ajouté (total: {existing_item.quantity})",
                }

        # Check inventory space
        if len(player.inventory) >= self.max_inventory_size:
            return {
                "success": False,
                "message": "Inventaire plein ! Vendez ou détruisez des objets.",
            }

        # Add item
        player.inventory.append(item)

        return {"success": True, "message": f"{item.name} ajouté à l'inventaire !"}

    def remove_item(
        self, player: Player, item_id: str, quantity: int = 1
    ) -> Dict[str, any]:
        """
        Remove item from player inventory

        Args:
            player: The player
            item_id: ID of the item to remove
            quantity: How many to remove

        Returns:
            Dict with success status and message
        """

        item = self._find_item_by_id(player, item_id)

        if not item:
            return {"success": False, "message": "Objet non trouvé dans l'inventaire"}

        if item.stackable:
            if item.quantity < quantity:
                return {
                    "success": False,
                    "message": f"Pas assez d'exemplaires (vous avez {item.quantity})",
                }

            item.quantity -= quantity

            # Remove completely if quantity reaches 0
            if item.quantity <= 0:
                player.inventory.remove(item)

        else:
            player.inventory.remove(item)

        return {
            "success": True,
            "message": f"{item.name} x{quantity} retiré",
            "item": item,
        }

    def equip_item(self, player: Player, item_id: str, slot: str) -> Dict[str, any]:
        """
        Equip an item from inventory

        Args:
            player: The player
            item_id: ID of the item to equip
            slot: Equipment slot

        Returns:
            Dict with success status and message
        """

        # Validate slot
        if slot not in EQUIPMENT_SLOTS:
            return {"success": False, "message": f"Emplacement invalide: {slot}"}

        # Find item in inventory
        item = self._find_item_by_id(player, item_id)

        if not item:
            return {"success": False, "message": "Objet non trouvé dans l'inventaire"}

        # Check if item can be equipped in this slot
        if not self._can_equip_in_slot(item, slot):
            return {
                "success": False,
                "message": f"{item.name} ne peut pas être équipé dans cet emplacement",
            }

        # Unequip current item in slot if any
        if slot in player.equipped:
            self.unequip_item(player, slot)

        # Remove from inventory and equip
        player.inventory.remove(item)
        player.equipped[slot] = item

        # Apply bonuses
        self._apply_item_bonuses(player, item, equip=True)

        return {
            "success": True,
            "message": f"{item.name} équipé dans {EQUIPMENT_SLOTS[slot]} !",
            "item": item,
        }

    def unequip_item(self, player: Player, slot: str) -> Dict[str, any]:
        """
        Unequip an item to inventory

        Args:
            player: The player
            slot: Equipment slot

        Returns:
            Dict with success status and message
        """

        if slot not in player.equipped:
            return {
                "success": False,
                "message": "Aucun objet équipé dans cet emplacement",
            }

        item = player.equipped[slot]

        # Check inventory space
        if len(player.inventory) >= self.max_inventory_size:
            return {
                "success": False,
                "message": "Inventaire plein ! Impossible de déséquiper.",
            }

        # Remove bonuses
        self._apply_item_bonuses(player, item, equip=False)

        # Unequip and add to inventory
        del player.equipped[slot]
        player.inventory.append(item)

        return {"success": True, "message": f"{item.name} déséquipé", "item": item}

    def use_consumable(self, player: Player, item_id: str) -> Dict[str, any]:
        """
        Use a consumable item (potion, food, etc.)

        Args:
            player: The player
            item_id: ID of the consumable

        Returns:
            Dict with success status and effects
        """

        item = self._find_item_by_id(player, item_id)

        if not item:
            return {"success": False, "message": "Objet non trouvé"}

        if item.type not in [ItemType.POTION, ItemType.CONSUMABLE]:
            return {"success": False, "message": "Cet objet n'est pas consommable"}

        # Apply effects (basic implementation)
        effects = []

        if "health" in item.item_id or "heal" in item.item_id:
            heal_amount = 50  # TODO: Get from item properties
            player.heal(heal_amount)
            effects.append(f"HP restaurés: +{heal_amount}")

        if "mana" in item.item_id:
            mana_amount = 30  # TODO: Get from item properties
            player.restore_mana(mana_amount)
            effects.append(f"Mana restaurée: +{mana_amount}")

        # Remove item
        self.remove_item(player, item_id, quantity=1)

        return {
            "success": True,
            "message": f"Vous utilisez {item.name}",
            "effects": effects,
        }

    def sell_item(
        self, player: Player, item_id: str, quantity: int = 1
    ) -> Dict[str, any]:
        """
        Sell an item for gold

        Args:
            player: The player
            item_id: ID of the item to sell
            quantity: How many to sell

        Returns:
            Dict with success status and gold gained
        """

        item = self._find_item_by_id(player, item_id)

        if not item:
            return {"success": False, "message": "Objet non trouvé"}

        # Check quantity
        if item.stackable and item.quantity < quantity:
            return {
                "success": False,
                "message": f"Pas assez d'exemplaires (vous avez {item.quantity})",
            }

        # Calculate sell price (50% of value)
        sell_price = int(item.value * 0.5 * quantity)

        # Remove item
        result = self.remove_item(player, item_id, quantity)

        if not result["success"]:
            return result

        # Give gold
        player.gold += sell_price

        return {
            "success": True,
            "message": f"{item.name} x{quantity} vendu pour {sell_price} or",
            "gold_gained": sell_price,
        }

    def buy_item(self, player: Player, item: Item, price: int) -> Dict[str, any]:
        """
        Buy an item from a shop

        Args:
            player: The player
            item: The item to buy
            price: Purchase price

        Returns:
            Dict with success status
        """

        # Check gold
        if not player.can_afford(price):
            return {
                "success": False,
                "message": f"Pas assez d'or (besoin: {price}, vous avez: {player.gold})",
            }

        # Check inventory space
        if not item.stackable and len(player.inventory) >= self.max_inventory_size:
            return {"success": False, "message": "Inventaire plein !"}

        # Deduct gold
        player.gold -= price

        # Add item
        result = self.add_item(player, item)

        if not result["success"]:
            # Refund if failed
            player.gold += price
            return result

        return {
            "success": True,
            "message": f"{item.name} acheté pour {price} or !",
            "item": item,
        }

    def get_total_stats(self, player: Player) -> Dict[str, int]:
        """
        Calculate total stats including equipment bonuses

        Args:
            player: The player

        Returns:
            Dict with all stats
        """

        stats = {
            "strength": player.strength,
            "intelligence": player.intelligence,
            "agility": player.agility,
            "wisdom": player.wisdom,
            "constitution": player.constitution,
            "charisma": player.charisma,
            "max_hp": player.max_hp,
            "max_mana": player.max_mana,
            "armor": 0,
            "damage": 5,  # Base fist damage
        }

        # Add bonuses from equipped items
        for slot, item in player.equipped.items():
            stats["strength"] += item.strength_bonus
            stats["intelligence"] += item.intelligence_bonus
            stats["agility"] += item.agility_bonus
            stats["max_hp"] += item.hp_bonus
            stats["max_mana"] += item.mana_bonus

            if item.type == ItemType.ARMOR:
                stats["armor"] += item.armor

            if item.type == ItemType.WEAPON:
                stats["damage"] = item.damage

        return stats

    def sort_inventory(self, player: Player, sort_by: str = "type"):
        """
        Sort player inventory

        Args:
            player: The player
            sort_by: Sort criteria ("type", "rarity", "value", "name")
        """

        if sort_by == "type":
            player.inventory.sort(key=lambda item: item.type.value)
        elif sort_by == "rarity":
            rarity_order = {
                ItemRarity.COMMON: 0,
                ItemRarity.UNCOMMON: 1,
                ItemRarity.RARE: 2,
                ItemRarity.EPIC: 3,
                ItemRarity.LEGENDARY: 4,
            }
            player.inventory.sort(
                key=lambda item: rarity_order.get(item.rarity, 0), reverse=True
            )
        elif sort_by == "value":
            player.inventory.sort(key=lambda item: item.value, reverse=True)
        elif sort_by == "name":
            player.inventory.sort(key=lambda item: item.name)

    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================

    def _find_item_by_id(self, player: Player, item_id: str) -> Optional[Item]:
        """Find item in inventory by ID"""
        return next(
            (item for item in player.inventory if item.item_id == item_id), None
        )

    def _can_equip_in_slot(self, item: Item, slot: str) -> bool:
        """Check if item can be equipped in the given slot"""

        if item.type == ItemType.WEAPON:
            return slot in ["weapon_main", "weapon_off"]

        if item.type == ItemType.ARMOR:
            # Check armor subtype from item_id (simplified)
            if "helmet" in item.item_id or "casque" in item.item_id:
                return slot == "head"
            elif "chest" in item.item_id or "plastron" in item.item_id:
                return slot == "chest"
            elif "legs" in item.item_id or "jambe" in item.item_id:
                return slot == "legs"
            elif "boots" in item.item_id or "bottes" in item.item_id:
                return slot == "feet"
            elif "ring" in item.item_id or "anneau" in item.item_id:
                return slot in ["ring_1", "ring_2"]

        return False

    def _apply_item_bonuses(self, player: Player, item: Item, equip: bool = True):
        """Apply or remove item stat bonuses"""

        multiplier = 1 if equip else -1

        player.strength += item.strength_bonus * multiplier
        player.intelligence += item.intelligence_bonus * multiplier
        player.agility += item.agility_bonus * multiplier

        # HP and Mana bonuses affect max values
        player.max_hp += item.hp_bonus * multiplier
        player.max_mana += item.mana_bonus * multiplier

        # Don't go over new max
        player.hp = min(player.hp, player.max_hp)
        player.mana = min(player.mana, player.max_mana)


# ============================================================================
# ITEM DATABASE (EXAMPLES)
# ============================================================================

ITEM_DATABASE = {
    # Weapons
    "rusty_sword": Item(
        item_id="rusty_sword",
        name="Épée rouillée",
        type=ItemType.WEAPON,
        rarity=ItemRarity.COMMON,
        damage=10,
        value=15,
        description="Une vieille épée rouillée. Mieux que rien.",
    ),
    "elven_sword": Item(
        item_id="elven_sword",
        name="Lame Elfique",
        type=ItemType.WEAPON,
        rarity=ItemRarity.RARE,
        damage=35,
        agility_bonus=2,
        value=500,
        description="Une épée forgée par les elfes, légère et mortelle.",
    ),
    # Armor
    "leather_armor": Item(
        item_id="leather_armor_chest",
        name="Armure de cuir",
        type=ItemType.ARMOR,
        rarity=ItemRarity.COMMON,
        armor=10,
        value=50,
        description="Une armure de cuir simple mais efficace.",
    ),
    # Potions
    "health_potion": Item(
        item_id="health_potion",
        name="Potion de soin",
        type=ItemType.POTION,
        rarity=ItemRarity.COMMON,
        stackable=True,
        value=25,
        description="Restaure 50 HP",
    ),
    "mana_potion": Item(
        item_id="mana_potion",
        name="Potion de mana",
        type=ItemType.POTION,
        rarity=ItemRarity.COMMON,
        stackable=True,
        value=30,
        description="Restaure 30 Mana",
    ),
    # Quest items
    "ring_of_power": Item(
        item_id="ring_of_power",
        name="L'Anneau Unique",
        type=ItemType.QUEST_ITEM,
        rarity=ItemRarity.LEGENDARY,
        value=0,  # Priceless
        description="Un anneau d'or avec d'étranges inscriptions...",
    ),
}
