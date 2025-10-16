import pygame
import sys
import random
import math

pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650

BG_COLOR = (12, 17, 30)
CARD_BG = (22, 32, 50)
OVERLAY_BG = (8, 12, 20)

ACCENT_PRIMARY = (66, 135, 245)
ACCENT_SECONDARY = (88, 166, 255)

SUCCESS_COLOR = (52, 211, 153)
SUCCESS_HOVER = (74, 222, 170)

DANGER_COLOR = (239, 68, 68)
DANGER_HOVER = (248, 113, 113)

WARNING_COLOR = (251, 191, 36)
WARNING_HOVER = (252, 211, 77)

PURPLE_COLOR = (168, 85, 247)
PURPLE_HOVER = (192, 132, 252)

INFO_COLOR = (96, 165, 250)
MANA_COLOR = (99, 179, 237)

TEXT_PRIMARY = (241, 245, 249)
TEXT_SECONDARY = (148, 163, 184)
TEXT_DISABLED = (100, 116, 139)

RARITY_COMMON = (156, 163, 175)
RARITY_UNCOMMON = (34, 197, 94)
RARITY_RARE = (59, 130, 246)
RARITY_EPIC = (168, 85, 247)
RARITY_LEGENDARY = (234, 179, 8)

pygame.font.init()
FONT_TITLE = pygame.font.Font(None, 48)
FONT_LARGE = pygame.font.Font(None, 32)
FONT_MEDIUM = pygame.font.Font(None, 26)
FONT_SMALL = pygame.font.Font(None, 22)
FONT_TINY = pygame.font.Font(None, 18)


class Skill:
    """Класс навыка"""
    def __init__(self, name, damage, mana_cost, effect_type="damage", effect_value=0, description=""):
        self.name = name
        self.damage = damage
        self.mana_cost = mana_cost
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.description = description


class Item:
    """Класс предмета с системой редкости и эффектами"""
    def __init__(self, name, item_type, value, description="", rarity="common", effect=None, armor_slot=None):
        self.name = name
        self.item_type = item_type
        self.value = value
        self.description = description
        self.rarity = rarity
        self.effect = effect
        self.armor_slot = armor_slot
        
        self.sell_price = self.calculate_sell_price()
    
    def calculate_sell_price(self):
        """Рассчитать цену продажи по редкости"""
        base_prices = {
            "common": 5,
            "uncommon": 15,
            "rare": 40,
            "epic": 100,
            "legendary": 300
        }
        
        if self.item_type == "potion_hp" or self.item_type == "potion_mana":
            return self.value // 2
        
        multiplier = 1
        if self.item_type == "weapon":
            multiplier = self.value * 2
        elif self.item_type == "armor":
            multiplier = self.value // 3
        
        return base_prices.get(self.rarity, 5) + multiplier
    
    def get_rarity_color(self):
        """Получить цвет редкости"""
        colors = {
            "common": RARITY_COMMON,
            "uncommon": RARITY_UNCOMMON,
            "rare": RARITY_RARE,
            "epic": RARITY_EPIC,
            "legendary": RARITY_LEGENDARY
        }
        return colors.get(self.rarity, RARITY_COMMON)
    
    def get_rarity_name(self):
        """Получить название редкости на русском"""
        names = {
            "common": "Обычный",
            "uncommon": "Необычный",
            "rare": "Редкий",
            "epic": "Эпический",
            "legendary": "Легендарный"
        }
        return names.get(self.rarity, "Обычный")


class ShopItem:
    """Товар в магазине"""
    def __init__(self, name, item_type, base_price, description, stock="unlimited", item_data=None):
        self.name = name
        self.item_type = item_type
        self.base_price = base_price
        self.description = description
        self.stock = stock
        self.item_data = item_data
        self.sold_count = 0
    
    def get_current_price(self, player=None):
        """Получить текущую цену (может зависеть от количества покупок)"""
        if self.item_type == "upgrade_attack" and player:
            return int(self.base_price * (1.5 ** player.attack_upgrades_bought))
        elif self.item_type == "upgrade_defense" and player:
            return int(self.base_price * (1.5 ** player.defense_upgrades_bought))
        return self.base_price
    
    def get_color(self):
        """Цвет товара в зависимости от типа"""
        if self.item_type == "potion_hp":
            return SUCCESS_COLOR
        elif self.item_type == "potion_mana":
            return MANA_COLOR
        elif self.item_type == "potion_multi":
            return PURPLE_COLOR
        elif self.item_type in ["upgrade_attack", "upgrade_defense"]:
            return WARNING_COLOR
        elif self.item_data and "rarity" in self.item_data:
            temp_item = Item("temp", "weapon", 0, "", self.item_data["rarity"])
            return temp_item.get_rarity_color()
        else:
            return ACCENT_PRIMARY


class Player:
    """Класс игрока с системой экипировки и статистикой"""
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.hp = 120
        self.max_hp = 120
        self.mana = 100
        self.max_mana = 100
        self.attack = 15
        self.defense = 8
        self.exp = 0
        self.exp_to_level = 100
        self.gold = 100
        
        self.attack_upgrades_bought = 0
        self.defense_upgrades_bought = 0
        
        self.equipped = {
            "head": None,      # Шлем
            "chest": None,     # Нагрудник
            "legs": None,      # Поножи
            "weapon": None     # Оружие
        }
        
        self.max_inventory = 10
        
        self.inventory = [
            Item("Зелье здоровья", "potion_hp", 50, "Восстанавливает 50 HP", "common"),
            Item("Зелье маны", "potion_mana", 40, "Восстанавливает 40 маны", "common"),
        ]
        
        self.skills = [
            Skill("Мощный удар", 35, 25, "damage", 0, "Сильная атака"),
            Skill("Молния", 45, 40, "damage", 0, "Магический урон"),
            Skill("Защита", 0, 20, "buff", 5, "+5 защиты на 2 хода"),
            Skill("Огненный шар", 55, 50, "damage", 0, "Мощное заклинание"),
        ]
        
        self.status_effects = {}
        
        self.stats = {
            "enemies_killed": 0,
            "bosses_killed": 0,
            "gold_earned": 0,
            "critical_hits": 0,
            "total_damage_dealt": 0,
            "total_damage_taken": 0,
            "items_collected": 0,
            "potions_used": 0
        }
        
        self.crit_chance = 0.15
        self.crit_multiplier = 2.0
    
    def equip_item(self, item):
        """Экипировать предмет в соответствующий слот"""
        if item.item_type == "weapon":
            if self.equipped["weapon"]:
                old_weapon = self.equipped["weapon"]
                self.attack -= old_weapon.value
                if len(self.inventory) < self.max_inventory:
                    self.inventory.append(old_weapon)
            
            self.equipped["weapon"] = item
            self.attack += item.value
            return True, f"Экипировано: {item.name}"
            
        elif item.item_type == "armor":
            if not item.armor_slot or item.armor_slot not in ["head", "chest", "legs"]:
                return False, "Неверный тип брони"
            
            slot = item.armor_slot
            
            if self.equipped[slot]:
                old_armor = self.equipped[slot]
                self.max_hp -= old_armor.value
                self.hp = min(self.hp, self.max_hp)
                if len(self.inventory) < self.max_inventory:
                    self.inventory.append(old_armor)
            
            self.equipped[slot] = item
            self.max_hp += item.value
            self.hp += item.value
            return True, f"Экипировано: {item.name}"
        
        return False, "Не удалось экипировать"
    
    def unequip_item(self, slot):
        """Снять предмет из слота"""
        if self.equipped[slot]:
            item = self.equipped[slot]
            
            if len(self.inventory) >= self.max_inventory:
                return False, "Инвентарь полон!"
            
            if item.item_type == "weapon":
                self.attack -= item.value
            elif item.item_type == "armor":
                self.max_hp -= item.value
                self.hp = min(self.hp, self.max_hp)
            
            self.inventory.append(item)
            self.equipped[slot] = None
            return True, f"Снято: {item.name}"
        
        return False, "Слот пуст"
    
    def sell_item(self, item_index):
        """Продать предмет"""
        if item_index < len(self.inventory):
            item = self.inventory[item_index]
            price = item.sell_price
            self.gold += price
            self.inventory.pop(item_index)
            return True, f"Продано за {price} золота!"
        return False, "Предмет не найден"
    
    def can_add_to_inventory(self):
        """Проверка, можно ли добавить предмет"""
        return len(self.inventory) < self.max_inventory
    
    def equip_weapon(self, bonus):
        """Экипировать оружие (старый метод для совместимости)"""
        self.attack += bonus
    
    def equip_armor(self, bonus):
        """Экипировать броню (старый метод для совместимости)"""
        self.max_hp += bonus
        self.hp += bonus
        
    def take_damage(self, damage):
        defense_bonus = self.status_effects.get("buff_defense", 0) * 5
        total_defense = self.defense + defense_bonus
        actual_damage = max(1, damage - total_defense)
        self.hp -= actual_damage
        self.stats["total_damage_taken"] += actual_damage
        if self.hp < 0:
            self.hp = 0
        return actual_damage
    
    def calculate_attack_damage(self, base_damage):
        """Рассчитать урон с учётом крита"""
        is_crit = random.random() < self.crit_chance
        damage = base_damage
        
        if is_crit:
            damage = int(base_damage * self.crit_multiplier)
            self.stats["critical_hits"] += 1
        
        if self.equipped["weapon"] and self.equipped["weapon"].effect:
            pass
        
        self.stats["total_damage_dealt"] += damage
        return damage, is_crit
    
    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
    
    def restore_mana(self, amount):
        self.mana += amount
        if self.mana > self.max_mana:
            self.mana = self.max_mana
    
    def use_item(self, item_index):
        if item_index < len(self.inventory):
            item = self.inventory[item_index]
            if item.item_type == "potion_hp":
                self.heal(item.value)
                self.inventory.pop(item_index)
                self.stats["potions_used"] += 1
                return True, f"Восстановлено {item.value} HP"
            elif item.item_type == "potion_mana":
                self.restore_mana(item.value)
                self.inventory.pop(item_index)
                self.stats["potions_used"] += 1
                return True, f"Восстановлено {item.value} маны"
            elif item.item_type == "potion_multi":
                hp_restore = item.value
                mana_restore = getattr(item, 'mana_value', 30)  # По умолчанию 30 маны
                self.heal(hp_restore)
                self.restore_mana(mana_restore)
                self.inventory.pop(item_index)
                self.stats["potions_used"] += 1
                return True, f"Восстановлено {hp_restore} HP и {mana_restore} маны"
            elif item.item_type == "weapon":
                success, msg = self.equip_item(item)
                if success:
                    self.inventory.pop(item_index)
                return success, msg
            elif item.item_type == "armor":
                success, msg = self.equip_item(item)
                if success:
                    self.inventory.pop(item_index)
                return success, msg
        return False, "Предмет недоступен"
    
    def use_skill(self, skill_index, target):
        if skill_index < len(self.skills):
            skill = self.skills[skill_index]
            if self.mana >= skill.mana_cost:
                self.mana -= skill.mana_cost
                
                if skill.effect_type == "damage":
                    damage = skill.damage + random.randint(-5, 5)
                    actual_damage = target.take_damage(damage)
                    return True, f"{skill.name} нанёс {actual_damage} урона!"
                elif skill.effect_type == "buff":
                    self.status_effects["buff_defense"] = 2
                    return True, "Защита усилена на 2 хода!"
                    
        return False, "Недостаточно маны!"
    
    def end_turn(self):
        for effect in list(self.status_effects.keys()):
            self.status_effects[effect] -= 1
            if self.status_effects[effect] <= 0:
                del self.status_effects[effect]
    
    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_level:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.exp = 0
        self.exp_to_level = int(self.exp_to_level * 1.5)
        self.max_hp += 25
        self.hp = self.max_hp
        self.max_mana += 20
        self.mana = self.max_mana
        self.attack += 5
        self.defense += 3


class Enemy:
    """Класс врага с ИИ"""
    def __init__(self, level, allow_stronger=True):
        self.level = level
        
        if allow_stronger and random.random() < 0.3:
            self.level = level + random.randint(1, 2)
            self.is_elite = True
        else:
            self.is_elite = False
        
        enemy_types = {
            "Гоблин": {"hp_mult": 1.0, "attack_mult": 0.9, "defense_mult": 0.8},
            "Орк": {"hp_mult": 1.3, "attack_mult": 1.2, "defense_mult": 1.0},
            "Скелет": {"hp_mult": 0.8, "attack_mult": 1.1, "defense_mult": 0.7},
            "Тёмный маг": {"hp_mult": 0.9, "attack_mult": 1.4, "defense_mult": 0.6},
            "Дракон": {"hp_mult": 1.5, "attack_mult": 1.3, "defense_mult": 1.2},
        }
        
        self.name, stats = random.choice(list(enemy_types.items()))
        if self.is_elite:
            self.name = f"[ЭЛИТНЫЙ] {self.name}"
        
        base_hp = 40 + (self.level * 20)
        self.max_hp = int(base_hp * stats["hp_mult"])
        self.hp = self.max_hp
        
        base_attack = 12 + (self.level * 4)
        self.attack = int(base_attack * stats["attack_mult"])
        
        base_defense = 5 + self.level
        self.defense = int(base_defense * stats["defense_mult"])
        
        self.exp_reward = 40 + (self.level * 15)
        self.gold_reward = 15 + (self.level * 8)
        
        if self.is_elite:
            self.exp_reward = int(self.exp_reward * 1.5)
            self.gold_reward = int(self.gold_reward * 1.5)
        
        self.defending = False
        self.charge = 0
        
        self.loot = self.generate_loot()
    
    def generate_loot(self):
        """Генерация выпадающих предметов с системой редкости"""
        loot = []
        
        rarity_roll = random.random()
        if rarity_roll < 0.50:
            rarity = "common"
        elif rarity_roll < 0.75:
            rarity = "uncommon"
        elif rarity_roll < 0.90:
            rarity = "rare"
        elif rarity_roll < 0.98:
            rarity = "epic"
        else:
            rarity = "legendary"
        
        rarity_multipliers = {
            "common": 1.0,
            "uncommon": 1.3,
            "rare": 1.7,
            "epic": 2.2,
            "legendary": 3.0
        }
        mult = rarity_multipliers[rarity]
        
        if random.random() < 0.2:
            weapon_bonus = int(random.randint(3, 8) * mult)
            effect = None
            effect_text = ""
            
            if rarity in ["rare", "epic", "legendary"] and random.random() < 0.3:
                effect = random.choice(["poison", "fire", "ice", "lightning"])
                effect_names = {
                    "poison": "[ЯД]",
                    "fire": "[ОГОНЬ]",
                    "ice": "[ЛЁД]",
                    "lightning": "[МОЛНИЯ]"
                }
                effect_text = f" {effect_names[effect]}"
            
            loot.append(Item(
                f"Меч +{weapon_bonus}{effect_text}",
                "weapon",
                weapon_bonus,
                f"Увеличивает атаку на {weapon_bonus}",
                rarity,
                effect
            ))
        
        if random.random() < 0.2:
            armor_bonus = int(random.randint(15, 35) * mult)
            slot = random.choice(["head", "chest", "legs"])
            slot_names = {"head": "Шлем", "chest": "Нагрудник", "legs": "Поножи"}
            
            loot.append(Item(
                f"{slot_names[slot]} +{armor_bonus}",
                "armor",
                armor_bonus,
                f"Увеличивает макс. HP на {armor_bonus}",
                rarity,
                None,
                slot
            ))
        
        if self.is_elite and random.random() < 0.4:
            weapon_bonus = int(random.randint(8, 15) * mult)
            elite_rarity = random.choice(["rare", "epic"]) if rarity in ["common", "uncommon"] else rarity
            loot.append(Item(
                f"Редкий меч +{weapon_bonus}",
                "weapon",
                weapon_bonus,
                f"Увеличивает атаку на {weapon_bonus}",
                elite_rarity
            ))
        
        return loot
    
    def take_damage(self, damage):
        defense_mult = 2 if self.defending else 1
        actual_damage = max(1, damage - (self.defense * defense_mult))
        self.hp -= actual_damage
        if self.hp < 0:
            self.hp = 0
        self.defending = False
        return actual_damage
    
    def choose_action(self, player):
        if self.hp < self.max_hp * 0.3 and random.random() < 0.4:
            return "defend"
        elif self.charge >= 1:
            self.charge = 0
            return "heavy_attack"
        elif random.random() < 0.3:
            self.charge += 1
            return "charge"
        else:
            return "attack"
    
    def perform_action(self, action, player):
        if action == "attack":
            damage = self.attack + random.randint(-3, 3)
            actual = player.take_damage(damage)
            return f"{self.name} атакует! Урон: {actual}"
        elif action == "heavy_attack":
            damage = int(self.attack * 1.8) + random.randint(-5, 5)
            actual = player.take_damage(damage)
            return f"{self.name} использует мощную атаку! Урон: {actual}"
        elif action == "defend":
            self.defending = True
            return f"{self.name} принимает защитную стойку!"
        elif action == "charge":
            return f"{self.name} готовит мощную атаку..."
        return ""


class Boss(Enemy):
    """Класс босса - усиленная версия врага"""
    def __init__(self, level, location_name):
        super().__init__(level, allow_stronger=False)
        
        self.is_elite = True
        self.is_boss = True
        
        boss_names = {
            "Тёмный лес": "Древний Энт",
            "Заброшенная крепость": "Рыцарь-Смерть",
            "Пещера гоблинов": "Король Гоблинов",
            "Логово орков": "Вождь Орков",
            "Драконье гнездо": "Древний Дракон"
        }
        
        self.name = f"[БОСС] {boss_names.get(location_name, 'Неизвестный босс')}"
        
        self.max_hp = int(self.max_hp * 2.5)
        self.hp = self.max_hp
        self.attack = int(self.attack * 1.8)
        self.defense = int(self.defense * 1.5)
        
        self.exp_reward = int(self.exp_reward * 3)
        self.gold_reward = int(self.gold_reward * 4)
        
        self.loot = self.generate_boss_loot()
    
    def generate_boss_loot(self):
        """Генерация уникального лута для боссов"""
        loot = []
        
        num_items = random.randint(1, 2)
        
        for _ in range(num_items):
            item_type = random.choice(["weapon", "armor"])
            rarity = random.choices(
                ["rare", "epic", "legendary"],
                weights=[50, 35, 15]
            )[0]
            
            if item_type == "weapon":
                bonus = random.randint(10, 25) if rarity == "rare" else random.randint(20, 40) if rarity == "epic" else random.randint(35, 60)
                effect = random.choice([None, "poison", "fire", "ice", "lightning"])
                effect_text = ""
                if effect == "poison":
                    effect_text = " [ЯД]"
                elif effect == "fire":
                    effect_text = " [ОГОНЬ]"
                elif effect == "ice":
                    effect_text = " [ЛЁД]"
                elif effect == "lightning":
                    effect_text = " [МОЛНИЯ]"
                
                loot.append(Item(
                    f"Меч босса +{bonus}{effect_text}",
                    "weapon",
                    bonus,
                    f"Легендарное оружие босса. Атака +{bonus}",
                    rarity,
                    effect
                ))
            else:
                bonus = random.randint(30, 60) if rarity == "rare" else random.randint(50, 90) if rarity == "epic" else random.randint(80, 130)
                slot = random.choice(["head", "chest", "legs"])
                slot_names = {"head": "Шлем", "chest": "Нагрудник", "legs": "Поножи"}
                
                loot.append(Item(
                    f"{slot_names[slot]} босса +{bonus}",
                    "armor",
                    bonus,
                    f"Легендарная броня босса. HP +{bonus}",
                    rarity,
                    None,
                    slot
                ))
        
        return loot


class Star:
    """Анимированная звезда для фона"""
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.uniform(1, 2.5)
        self.speed = random.uniform(0.05, 0.3)
        self.alpha = random.randint(80, 200)
        self.alpha_direction = random.choice([-1, 1])
        self.twinkle_speed = random.uniform(0.8, 2)
    
    def update(self, dt=0.016):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
        
        self.alpha += self.alpha_direction * self.twinkle_speed
        if self.alpha >= 200:
            self.alpha = 200
            self.alpha_direction = -1
        elif self.alpha <= 80:
            self.alpha = 80
            self.alpha_direction = 1
    
    def draw(self, screen):
        star_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(star_surface, (255, 255, 255, int(self.alpha)), 
                          (int(self.size), int(self.size)), int(self.size))
        screen.blit(star_surface, (int(self.x - self.size), int(self.y - self.size)))


class Particle:
    """Класс частицы для красивых эффектов"""
    def __init__(self, x, y, color, particle_type="circle"):
        self.x = x
        self.y = y
        self.color = color
        self.type = particle_type
        self.lifetime = random.uniform(0.5, 1.5)
        self.max_lifetime = self.lifetime
        self.size = random.uniform(2, 6)
        self.vel_x = random.uniform(-2, 2)
        self.vel_y = random.uniform(-4, -1)
        self.gravity = 0.15
    
    def update(self, dt):
        self.lifetime -= dt
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += self.gravity
        return self.lifetime > 0
    
    def draw(self, screen):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        current_size = self.size * (self.lifetime / self.max_lifetime)
        
        if current_size < 0.5:
            return
        
        if self.type == "star":
            surf = pygame.Surface((int(current_size * 3), int(current_size * 3)), pygame.SRCALPHA)
            color_with_alpha = (*self.color[:3], alpha)
            center_x, center_y = int(current_size * 1.5), int(current_size * 1.5)
            
            pygame.draw.circle(surf, color_with_alpha, (center_x, center_y), int(current_size))
            
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                end_x = int(center_x + math.cos(rad) * current_size * 2)
                end_y = int(center_y + math.sin(rad) * current_size * 2)
                pygame.draw.line(surf, color_with_alpha, (center_x, center_y), (end_x, end_y), 2)
            
            screen.blit(surf, (self.x - current_size * 1.5, self.y - current_size * 1.5))
        else:
            surf = pygame.Surface((int(current_size * 4), int(current_size * 4)), pygame.SRCALPHA)
            center = int(current_size * 2)
            
            glow_alpha = alpha // 3
            pygame.draw.circle(surf, (*self.color[:3], glow_alpha), 
                             (center, center), int(current_size * 2))
            
            pygame.draw.circle(surf, (*self.color[:3], alpha), 
                             (center, center), int(current_size))
            
            screen.blit(surf, (self.x - current_size * 2, self.y - current_size * 2))


class Button:
    """Современная компактная кнопка с плавными анимациями"""
    def __init__(self, x, y, width, height, text, color=ACCENT_PRIMARY, hover_color=None, icon=None):
        self.base_rect = pygame.Rect(x, y, width, height)
        self.rect = self.base_rect.copy()
        self.text = text
        self.base_color = color
        self.hover_color = hover_color if hover_color else tuple(min(255, c + 30) for c in color)
        self.color = color
        self.is_hovered = False
        self.hover_progress = 0.0
        self.click_progress = 0.0
        self.icon = icon
        
    def update(self, dt=0.016):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if self.is_hovered:
            self.hover_progress = min(1.0, self.hover_progress + dt * 6)
        else:
            self.hover_progress = max(0.0, self.hover_progress - dt * 6)
        
        self.color = tuple(
            int(self.base_color[i] + (self.hover_color[i] - self.base_color[i]) * self.hover_progress)
            for i in range(3)
        )
        
        if self.click_progress > 0:
            self.click_progress = max(0, self.click_progress - dt * 4)
        
        lift = int(self.hover_progress * 2)
        self.rect.y = self.base_rect.y - lift
    
    def draw(self, screen):
        border_radius = 10
        
        shadow_offset = 4 + int(self.hover_progress * 2)
        shadow_rect = self.rect.copy()
        shadow_rect.y += shadow_offset
        shadow_surface = pygame.Surface((self.rect.width + 8, self.rect.height + 8), pygame.SRCALPHA)
        shadow_alpha = int(30 + self.hover_progress * 20)
        pygame.draw.rect(shadow_surface, (0, 0, 0, shadow_alpha), 
                        shadow_surface.get_rect(), border_radius=border_radius)
        screen.blit(shadow_surface, (shadow_rect.x - 4, shadow_rect.y - 4))
        
        if self.hover_progress > 0.1:
            glow_alpha = int(40 * self.hover_progress)
            glow_rect = self.rect.inflate(8, 8)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*self.color, glow_alpha), 
                           glow_surface.get_rect(), border_radius=border_radius + 2)
            screen.blit(glow_surface, (glow_rect.x - 4, glow_rect.y - 4))
        
        pygame.draw.rect(screen, self.color, self.rect, border_radius=border_radius)
        
        border_alpha = int(80 + self.hover_progress * 60)
        border_color = tuple(min(255, c + 40) for c in self.color)
        pygame.draw.rect(screen, (*border_color, border_alpha), self.rect, 2, border_radius=border_radius)
        
        shine_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 2, self.rect.width - 10, self.rect.height // 3)
        shine_surface = pygame.Surface((shine_rect.width, shine_rect.height), pygame.SRCALPHA)
        for i in range(shine_rect.height):
            shine_alpha = int(25 * (1 - i / shine_rect.height))
            pygame.draw.line(shine_surface, (255, 255, 255, shine_alpha), 
                           (0, i), (shine_rect.width, i))
        screen.blit(shine_surface, (shine_rect.x, shine_rect.y))
        
        if self.click_progress > 0:
            click_overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            click_alpha = int(self.click_progress * 60)
            pygame.draw.rect(click_overlay, (255, 255, 255, click_alpha), 
                           click_overlay.get_rect(), border_radius=border_radius)
            screen.blit(click_overlay, self.rect)
        
        text_surface = FONT_SMALL.render(self.text, True, TEXT_PRIMARY)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        text_shadow = FONT_SMALL.render(self.text, True, (0, 0, 0, 100))
        shadow_rect = text_shadow.get_rect(center=(self.rect.centerx + 1, self.rect.centery + 1))
        screen.blit(text_shadow, shadow_rect)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_hovered = True
                self.click_progress = 1.0
                return True
        return False


class ModalWindow:
    """Модальное окно с анимацией появления"""
    def __init__(self, width, height, title=""):
        self.width = width
        self.height = height
        self.title = title
        self.x = (SCREEN_WIDTH - width) // 2
        self.y = (SCREEN_HEIGHT - height) // 2
        self.rect = pygame.Rect(self.x, self.y, width, height)
        self.animation_progress = 0.0
        self.is_open = False
        self.target_open = False
        
    def open(self):
        self.target_open = True
        self.is_open = True
        
    def close(self):
        self.target_open = False
        
    def update(self, dt=0.016):
        if self.target_open:
            self.animation_progress = min(1.0, self.animation_progress + dt * 8)
        else:
            self.animation_progress = max(0.0, self.animation_progress - dt * 8)
            if self.animation_progress == 0:
                self.is_open = False
    
    def draw_background(self, screen):
        """Затемнение фона"""
        if self.animation_progress > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay_alpha = int(180 * self.animation_progress)
            overlay.fill((*OVERLAY_BG, overlay_alpha))
            screen.blit(overlay, (0, 0))
    
    def draw(self, screen):
        """Отрисовка окна"""
        if self.animation_progress > 0:
            scale = 0.7 + (0.3 * self.animation_progress)
            scaled_width = int(self.width * scale)
            scaled_height = int(self.height * scale)
            scaled_x = (SCREEN_WIDTH - scaled_width) // 2
            scaled_y = (SCREEN_HEIGHT - scaled_height) // 2
            scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
            
            shadow_surface = pygame.Surface((scaled_width + 20, scaled_height + 20), pygame.SRCALPHA)
            shadow_alpha = int(60 * self.animation_progress)
            pygame.draw.rect(shadow_surface, (0, 0, 0, shadow_alpha), 
                           shadow_surface.get_rect(), border_radius=18)
            screen.blit(shadow_surface, (scaled_x - 10, scaled_y - 5))
            
            window_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            alpha = int(255 * self.animation_progress)
            pygame.draw.rect(window_surface, (*CARD_BG, alpha), 
                           window_surface.get_rect(), border_radius=15)
            
            pygame.draw.rect(window_surface, (*ACCENT_PRIMARY, int(100 * self.animation_progress)), 
                           window_surface.get_rect(), 2, border_radius=15)
            
            screen.blit(window_surface, scaled_rect)
            
            if self.title:
                title_surface = FONT_LARGE.render(self.title, True, TEXT_PRIMARY)
                title_rect = title_surface.get_rect(centerx=scaled_rect.centerx, y=scaled_y + 20)
                title_surface.set_alpha(alpha)
                screen.blit(title_surface, title_rect)
            
            return scaled_rect
        return None


class ItemDetailWindow:
    """Окно с подробной информацией о предмете"""
    def __init__(self):
        self.is_open = False
        self.item = None
        self.x = 0
        self.y = 0
        self.width = 350
        self.height = 200
        self.animation_progress = 0.0
    
    def open(self, item, x, y):
        """Открыть окно для предмета"""
        self.is_open = True
        self.item = item
        self.animation_progress = 0.0
        
        self.x = min(max(x + 20, 10), SCREEN_WIDTH - self.width - 10)
        self.y = min(max(y - self.height // 2, 10), SCREEN_HEIGHT - self.height - 10)
    
    def close(self):
        """Закрыть окно"""
        self.is_open = False
        self.item = None
    
    def update(self):
        """Обновление анимации"""
        if self.is_open and self.animation_progress < 1.0:
            self.animation_progress = min(1.0, self.animation_progress + 0.15)
        elif not self.is_open and self.animation_progress > 0:
            self.animation_progress = max(0.0, self.animation_progress - 0.15)
    
    def draw(self, screen):
        """Отрисовка окна"""
        if self.animation_progress > 0 and self.item:
            scale = self.animation_progress
            alpha = int(255 * self.animation_progress)
            
            shadow = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, int(80 * scale)), shadow.get_rect(), border_radius=12)
            screen.blit(shadow, (self.x - 5, self.y - 5))
            
            window_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(surf, (28, 38, 58, alpha), surf.get_rect(), border_radius=10)
            screen.blit(surf, window_rect)
            
            if self.item.item_type == "weapon":
                stripe_color = DANGER_COLOR
                type_text = "ОРУЖИЕ"
            elif self.item.item_type == "armor":
                stripe_color = ACCENT_PRIMARY
                type_text = "БРОНЯ"
            elif self.item.item_type == "potion_hp":
                stripe_color = SUCCESS_COLOR
                type_text = "ЗЕЛЬЕ ЗДОРОВЬЯ"
            elif self.item.item_type == "potion_mana":
                stripe_color = MANA_COLOR
                type_text = "ЗЕЛЬЕ МАНЫ"
            else:
                stripe_color = INFO_COLOR
                type_text = "ПРЕДМЕТ"
            
            stripe_surf = pygame.Surface((self.width, 4), pygame.SRCALPHA)
            stripe_surf.fill((*stripe_color, alpha))
            screen.blit(stripe_surf, (self.x, self.y))
            
            pygame.draw.rect(screen, (*stripe_color, int(150 * scale)), window_rect, 2, border_radius=10)
            
            type_surf = FONT_TINY.render(type_text, True, stripe_color)
            type_surf.set_alpha(alpha)
            screen.blit(type_surf, (self.x + 15, self.y + 15))
            
            name_surf = FONT_MEDIUM.render(self.item.name, True, TEXT_PRIMARY)
            name_surf.set_alpha(alpha)
            screen.blit(name_surf, (self.x + 15, self.y + 40))
            
            if self.item.description:
                desc_surf = FONT_SMALL.render(self.item.description, True, TEXT_SECONDARY)
                desc_surf.set_alpha(alpha)
                screen.blit(desc_surf, (self.x + 15, self.y + 75))
            
            y_offset = 110
            if self.item.item_type == "weapon":
                effect_text = f"Эффект: +{self.item.value} к атаке"
                effect_surf = FONT_SMALL.render(effect_text, True, DANGER_COLOR)
            elif self.item.item_type == "armor":
                effect_text = f"Эффект: +{self.item.value} к максимальному HP"
                effect_surf = FONT_SMALL.render(effect_text, True, ACCENT_PRIMARY)
            elif self.item.item_type == "potion_hp":
                effect_text = f"Эффект: восстанавливает {self.item.value} HP"
                effect_surf = FONT_SMALL.render(effect_text, True, SUCCESS_COLOR)
            elif self.item.item_type == "potion_mana":
                effect_text = f"Эффект: восстанавливает {self.item.value} маны"
                effect_surf = FONT_SMALL.render(effect_text, True, MANA_COLOR)
            else:
                effect_surf = None
            
            if effect_surf:
                effect_surf.set_alpha(alpha)
                screen.blit(effect_surf, (self.x + 15, self.y + y_offset))
            
            y_offset += 35
            if self.item.item_type in ["potion_hp", "potion_mana"]:
                hint_text = "Можно использовать в меню и бою"
            elif self.item.item_type in ["weapon", "armor"]:
                hint_text = "Можно экипировать в бою"
            else:
                hint_text = "Нажмите для использования"
            
            hint_surf = FONT_TINY.render(hint_text, True, TEXT_DISABLED)
            hint_surf.set_alpha(alpha)
            screen.blit(hint_surf, (self.x + 15, self.y + y_offset))


class EquipmentSlot:
    """Слот экипировки"""
    def __init__(self, x, y, slot_type, slot_name):
        self.x = x
        self.y = y
        self.size = 60
        self.slot_type = slot_type
        self.slot_name = slot_name
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.is_hovered = False
        self.item = None
    
    def draw(self, screen, equipped_item=None):
        """Отрисовка слота"""
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if self.is_hovered:
            bg_color = (40, 50, 70)
        else:
            bg_color = (25, 35, 50)
        
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        
        border_color = ACCENT_PRIMARY if self.is_hovered else (60, 70, 90)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)
        
        slot_labels = {
            "head": "ГОЛОВА",
            "chest": "ТОРС",
            "legs": "НОГИ",
            "weapon": "ОРУЖИЕ"
        }
        
        if equipped_item:
            item_color = equipped_item.get_rarity_color()
            
            short_name = equipped_item.name[:8] if len(equipped_item.name) > 8 else equipped_item.name
            item_text = FONT_TINY.render(short_name, True, item_color)
            text_rect = item_text.get_rect(center=(self.rect.centerx, self.rect.centery + 10))
            screen.blit(item_text, text_rect)
            
            bonus_text = FONT_TINY.render(f"+{equipped_item.value}", True, TEXT_PRIMARY)
            bonus_rect = bonus_text.get_rect(center=(self.rect.centerx, self.rect.centery - 10))
            screen.blit(bonus_text, bonus_rect)
        else:
            label = slot_labels.get(self.slot_type, "СЛОТ")
            label_surf = FONT_TINY.render(label, True, TEXT_DISABLED)
            label_rect = label_surf.get_rect(center=self.rect.center)
            screen.blit(label_surf, label_rect)
        
        name_surf = FONT_TINY.render(self.slot_name, True, TEXT_SECONDARY)
        name_rect = name_surf.get_rect(center=(self.rect.centerx, self.rect.bottom + 12))
        screen.blit(name_surf, name_rect)
    
    def handle_event(self, event):
        """Обработка событий слота"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_hovered = True
                return True
        return False


class Game:
    """Основной класс игры"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Убей злюк")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.state = "menu"
        self.player = None
        self.enemy = None
        self.message = ""
        self.message_timer = 0
        self.battle_log = []
        
        self.stars = [Star() for _ in range(120)]
        self.particles = []
        
        self.inventory_modal = ModalWindow(500, 450, "Инвентарь")
        self.skills_modal = ModalWindow(500, 500, "Навыки")
        self.item_detail_window = ItemDetailWindow()
        self.equipment_modal = ModalWindow(700, 500, "Экипировка")
        
        self.equipment_slots = {
            "head": EquipmentSlot(250, 150, "head", "Голова"),
            "chest": EquipmentSlot(250, 230, "chest", "Торс"),
            "legs": EquipmentSlot(250, 310, "legs", "Ноги"),
            "weapon": EquipmentSlot(250, 390, "weapon", "Оружие")
        }
        
        self.dragging_item = None
        self.dragging_from_index = None
        self.dragging_from_slot = None
        
        self.sell_mode = False
        self.selected_sell_item = None
        
        self.menu_buttons = [
            Button(325, 300, 250, 50, "Новая игра", SUCCESS_COLOR, SUCCESS_HOVER),
            Button(325, 370, 250, 50, "Выход", DANGER_COLOR, DANGER_HOVER)
        ]
        
        self.game_buttons = [
            Button(140, 560, 130, 45, "Локации", ACCENT_PRIMARY, tuple(min(255, c + 30) for c in ACCENT_PRIMARY)),
            Button(290, 560, 130, 45, "Магазин", WARNING_COLOR, WARNING_HOVER),
            Button(440, 560, 140, 45, "Экипировка", PURPLE_COLOR, PURPLE_HOVER),
            Button(600, 560, 130, 45, "Статистика", INFO_COLOR, tuple(min(255, c + 30) for c in INFO_COLOR))
        ]
        
        self.battle_main_buttons = [
            Button(130, 560, 140, 45, "Атаковать", DANGER_COLOR, DANGER_HOVER),
            Button(290, 560, 140, 45, "Навыки", PURPLE_COLOR, PURPLE_HOVER),
            Button(450, 560, 140, 45, "Предметы", SUCCESS_COLOR, SUCCESS_HOVER),
            Button(610, 560, 120, 45, "Бежать", (70, 80, 100))
        ]
        
        self.skill_buttons = []
        self.inventory_buttons = []
        
        self.shop_buttons = [
            Button(250, 260, 400, 45, "Зелье здоровья (30 золота)", SUCCESS_COLOR, SUCCESS_HOVER),
            Button(250, 320, 400, 45, "Зелье маны (25 золота)", MANA_COLOR, INFO_COLOR),
            Button(250, 380, 400, 45, "Улучшить атаку (60 золота)", DANGER_COLOR, DANGER_HOVER),
            Button(250, 520, 400, 45, "Назад", (60, 70, 90))
        ]
        
        self.equipment_back_button = Button(250, 475, 120, 45, "Назад", (60, 70, 90), (80, 90, 110))
        self.equipment_sell_button = Button(390, 475, 200, 45, "Продать предмет", DANGER_COLOR, DANGER_HOVER)
        
        self.stats_back_button = Button(250, 580, 400, 50, "Назад в меню", (70, 80, 100), (90, 100, 120))
        
        self.locations = [
            {"name": "Тёмный лес", "level_req": 1, "enemy_level_min": 1, "enemy_level_max": 2, "color": SUCCESS_COLOR},
            {"name": "Заброшенная крепость", "level_req": 3, "enemy_level_min": 3, "enemy_level_max": 4, "color": INFO_COLOR},
            {"name": "Пещера гоблинов", "level_req": 5, "enemy_level_min": 5, "enemy_level_max": 6, "color": WARNING_COLOR},
            {"name": "Логово орков", "level_req": 7, "enemy_level_min": 7, "enemy_level_max": 9, "color": DANGER_COLOR},
            {"name": "Драконье гнездо", "level_req": 10, "enemy_level_min": 10, "enemy_level_max": 13, "color": PURPLE_COLOR},
        ]
        
        self.location_buttons = []
        self.boss_buttons = []
        self.current_location = None
        
        self.shop_items = []
        self.shop_scroll_offset = 0
        self.shop_category = "all"  # "all", "potions", "upgrades", "equipment"
        self.refresh_shop_items()
    
    def refresh_shop_items(self):
        """Обновить ассортимент магазина"""
        self.shop_items = [
            ShopItem("Зелье здоровья", "potion_hp", 30, "Восстанавливает 50 HP", "unlimited", {"value": 50}),
            ShopItem("Зелье маны", "potion_mana", 25, "Восстанавливает 40 маны", "unlimited", {"value": 40}),
            
            ShopItem("Мульти зелье", "potion_multi", 50, "Восстанавливает 40 HP и 30 маны", "unlimited", {"hp": 40, "mana": 30}),
            
            ShopItem("Улучшить атаку", "upgrade_attack", 60, "+5 к атаке (навсегда)", "unlimited", {"value": 5}),
            ShopItem("Улучшить защиту", "upgrade_defense", 60, "+3 к защите (навсегда)", "unlimited", {"value": 3}),
        ]
    
    def new_game(self):
        self.player = Player("Герой")
        self.state = "game"
        self.message = "Добро пожаловать в игру!"
        self.message_timer = 90
        self.battle_log = []
    
    def open_locations(self):
        """Открыть экран выбора локаций"""
        self.state = "locations"
        
        self.location_buttons = []
        self.boss_buttons = []
        y_offset = 200
        
        for i, location in enumerate(self.locations):
            is_available = self.player.level >= location["level_req"]
            
            if is_available:
                btn_color = location["color"]
                hover_color = tuple(min(255, c + 30) for c in btn_color)
            else:
                btn_color = (50, 55, 70)
                hover_color = (60, 65, 80)
            
            if is_available:
                btn_text = f"{location['name']} (Уровень {location['level_req']}+)"
            else:
                btn_text = f"{location['name']} [ЗАКРЫТО - нужен {location['level_req']} ур.]"
            
            button = Button(170, y_offset, 320, 50, btn_text, btn_color, hover_color)
            self.location_buttons.append(button)
            
            boss_btn_text = "БОСС"
            boss_color = DANGER_COLOR if is_available else (50, 55, 70)
            boss_hover = DANGER_HOVER if is_available else (60, 65, 80)
            boss_button = Button(510, y_offset, 110, 50, boss_btn_text, boss_color, boss_hover)
            self.boss_buttons.append(boss_button)
            
            y_offset += 65
    
    def start_battle_in_location(self, location_index, is_boss=False):
        """Начать битву в выбранной локации"""
        location = self.locations[location_index]
        
        if self.player.level < location["level_req"]:
            self.message = f"Нужен {location['level_req']} уровень!"
            self.message_timer = 90
            return
        
        self.current_location = location
        
        if is_boss:
            self.enemy = Boss(location["enemy_level_max"], location["name"])
            self.battle_log = [f"БИТВА С БОССОМ: {self.enemy.name}!"]
        else:
            enemy_level = random.randint(location["enemy_level_min"], location["enemy_level_max"])
            self.enemy = Enemy(enemy_level)
            self.battle_log = [f"Встреча с врагом в локации '{location['name']}'!"]
        
        self.state = "battle"
        self.message = f"Бой начался!"
        self.message_timer = 90
        
        self.skill_buttons = []
        for i, skill in enumerate(self.player.skills):
            can_use = self.player.mana >= skill.mana_cost
            color = PURPLE_COLOR if can_use else (50, 55, 70)
            hover = PURPLE_HOVER if can_use else (60, 65, 80)
            self.skill_buttons.append(
                Button(220, 150 + i * 60, 360, 50, 
                      f"{skill.name} (Мана: {skill.mana_cost})", color, hover)
            )
    
    def start_battle(self):
        self.enemy = Enemy(self.player.level)
        self.state = "battle"
        self.battle_log = [f"Встреча с врагом: {self.enemy.name}!"]
        self.message = f"Бой начался!"
        self.message_timer = 90
        
        self.skill_buttons = []
        for i, skill in enumerate(self.player.skills):
            can_use = self.player.mana >= skill.mana_cost
            color = PURPLE_COLOR if can_use else (50, 55, 70)
            hover = PURPLE_HOVER if can_use else (60, 65, 80)
            self.skill_buttons.append(
                Button(220, 150 + i * 60, 360, 50, 
                      f"{skill.name} (Мана: {skill.mana_cost})", color, hover)
            )
    
    def open_inventory_modal(self):
        """Открыть модальное окно инвентаря"""
        self.inventory_modal.open()
        
        self.inventory_buttons = []
        for i, item in enumerate(self.player.inventory):
            color = item.get_rarity_color()
            
            if item.item_type == "weapon":
                item_text = f"{item.name} (+{item.value} АТК)"
            elif item.item_type == "armor":
                slot_names = {"head": "Ш", "chest": "Т", "legs": "Н"}
                slot_text = f"[{slot_names.get(item.armor_slot, '?')}]" if item.armor_slot else ""
                item_text = f"{slot_text} {item.name} (+{item.value} HP)"
            elif item.item_type == "potion_hp":
                item_text = f"{item.name} (+{item.value} HP)"
                color = SUCCESS_COLOR
            elif item.item_type == "potion_mana":
                item_text = f"{item.name} (+{item.value} MP)"
                color = MANA_COLOR
            else:
                item_text = item.name
            
            self.inventory_buttons.append(
                Button(220, 120 + i * 60, 360, 50, item_text, color, 
                      tuple(min(255, c + 30) for c in color))
            )
    
    def open_equipment(self):
        """Открыть окно экипировки"""
        self.equipment_modal.open()
        self.state = "equipment"
        
        self.update_equipment_inventory_buttons()
    
    def update_equipment_inventory_buttons(self):
        """Обновить кнопки инвентаря в окне экипировки (только оружие и броня)"""
        self.inventory_buttons = []
        start_x = 380
        start_y = 150
        
        equipment_items = [item for item in self.player.inventory 
                          if item.item_type in ["weapon", "armor"]]
        
        for i, item in enumerate(equipment_items):
            row = i // 2
            col = i % 2
            
            x = start_x + col * 140
            y = start_y + row * 65
            
            color = item.get_rarity_color()
            
            if item.item_type == "weapon":
                item_text = f"Оружие +{item.value}"
            elif item.item_type == "armor":
                slot_names = {"head": "Шлем", "chest": "Торс", "legs": "Ноги"}
                slot_name = slot_names.get(item.armor_slot, "Броня")
                item_text = f"{slot_name} +{item.value}"
            else:
                item_text = item.name[:6]
            
            button = Button(x, y, 130, 50, item_text, color, tuple(min(255, c + 30) for c in color))
            self.inventory_buttons.append(button)
    
    def open_skills_modal(self):
        """Открыть модальное окно навыков"""
        self.skills_modal.open()
        
        self.skill_buttons = []
        for i, skill in enumerate(self.player.skills):
            can_use = self.player.mana >= skill.mana_cost
            color = PURPLE_COLOR if can_use else (50, 55, 70)
            hover = PURPLE_HOVER if can_use else (60, 65, 80)
            self.skill_buttons.append(
                Button(220, 120 + i * 70, 360, 55, 
                      f"{skill.name} (Мана: {skill.mana_cost})", color, hover)
            )
    
    def player_basic_attack(self):
        base_damage = self.player.attack + random.randint(-4, 4)
        damage, is_crit = self.player.calculate_attack_damage(base_damage)
        actual_damage = self.enemy.take_damage(damage)
        
        crit_text = " [КРИТ!]" if is_crit else ""
        log_msg = f"[Атака] Вы атаковали{crit_text}! Урон: {actual_damage}"
        self.battle_log.append(log_msg)
        
        particle_count = 25 if is_crit else 15
        particle_color = WARNING_COLOR if is_crit else DANGER_COLOR
        self.spawn_particles(580, 120, particle_count, particle_color, "star" if is_crit else "circle")
        
        if self.player.equipped["weapon"] and self.player.equipped["weapon"].effect:
            self.apply_weapon_effect(self.player.equipped["weapon"].effect)
        
        if self.enemy.hp <= 0:
            self.victory()
            return
        
        self.player.end_turn()
        self.enemy_turn()
    
    def apply_weapon_effect(self, effect):
        """Применить эффект оружия"""
        if effect == "poison":
            dot_damage = random.randint(3, 8)
            self.enemy.hp -= dot_damage
            self.battle_log.append(f"[ЯД] Враг получил {dot_damage} урона от яда!")
            self.spawn_particles(580, 120, 10, (34, 197, 94), "circle")
        elif effect == "fire":
            fire_damage = random.randint(5, 12)
            self.enemy.hp -= fire_damage
            self.battle_log.append(f"[ОГОНЬ] Враг горит! Урон: {fire_damage}")
            self.spawn_particles(580, 120, 15, (239, 68, 68), "star")
        elif effect == "ice":
            if random.random() < 0.2:
                self.battle_log.append(f"[ЛЁД] Враг заморожен!")
                self.spawn_particles(580, 120, 12, (59, 130, 246), "star")
            else:
                ice_damage = random.randint(2, 6)
                self.enemy.hp -= ice_damage
                self.battle_log.append(f"[ЛЁД] Холод наносит {ice_damage} урона")
        elif effect == "lightning":
            lightning_damage = random.randint(8, 15)
            self.enemy.hp -= lightning_damage
            self.battle_log.append(f"[МОЛНИЯ] Разряд! Урон: {lightning_damage}")
            self.spawn_particles(580, 120, 20, (234, 179, 8), "star")
    
    def enemy_turn(self):
        action = self.enemy.choose_action(self.player)
        result = self.enemy.perform_action(action, self.player)
        self.battle_log.append(f"[Враг] {result}")
        
        if "урон" in result.lower() or "атаку" in result.lower():
            self.spawn_particles(160, 120, 10, DANGER_COLOR, "circle")
        
        if len(self.battle_log) > 4:
            self.battle_log = self.battle_log[-4:]
        
        if self.player.hp <= 0:
            self.defeat()
    
    def use_skill(self, skill_index):
        if skill_index < len(self.player.skills):
            skill = self.player.skills[skill_index]
            success, msg = self.player.use_skill(skill_index, self.enemy)
            
            if success:
                self.battle_log.append(f"[Навык] {msg}")
                self.skills_modal.close()
                
                if "Молния" in skill.name:
                    self.spawn_particles(580, 120, 20, (99, 179, 237), "star")
                elif "Огненный шар" in skill.name:
                    self.spawn_particles(580, 120, 25, (239, 68, 68), "star")
                elif "Мощный удар" in skill.name:
                    self.spawn_particles(580, 120, 15, WARNING_COLOR, "circle")
                else:
                    self.spawn_particles(160, 120, 10, SUCCESS_COLOR, "star")
                
                if self.enemy.hp <= 0:
                    self.victory()
                    return
                
                self.player.end_turn()
                self.enemy_turn()
            else:
                self.battle_log.append(f"[Ошибка] {msg}")
                
            if len(self.battle_log) > 4:
                self.battle_log = self.battle_log[-4:]
    
    def use_item_in_battle(self, item_index):
        if item_index < len(self.player.inventory):
            item = self.player.inventory[item_index]
            success, msg = self.player.use_item(item_index)
            if success:
                self.battle_log.append(f"[Предмет] {msg}")
                self.inventory_modal.close()
                
                if "здоров" in item.name.lower():
                    self.spawn_particles(160, 120, 15, SUCCESS_COLOR, "circle")
                elif "маны" in item.name.lower():
                    self.spawn_particles(160, 120, 15, MANA_COLOR, "star")
                
                self.inventory_buttons = []
                for i, inv_item in enumerate(self.player.inventory):
                    if inv_item.item_type == "weapon":
                        item_text = f"{inv_item.name} (+{inv_item.value} АТК)"
                        color = DANGER_COLOR
                    elif inv_item.item_type == "armor":
                        item_text = f"{inv_item.name} (+{inv_item.value} HP)"
                        color = ACCENT_PRIMARY
                    elif inv_item.item_type == "potion_hp":
                        item_text = f"{inv_item.name} (+{inv_item.value} HP)"
                        color = SUCCESS_COLOR
                    elif inv_item.item_type == "potion_mana":
                        item_text = f"{inv_item.name} (+{inv_item.value} MP)"
                        color = MANA_COLOR
                    elif inv_item.item_type == "potion_multi":
                        mana_val = getattr(inv_item, 'mana_value', 30)
                        item_text = f"{inv_item.name} (HP+MP)"
                        color = PURPLE_COLOR
                    else:
                        item_text = inv_item.name
                        color = SUCCESS_COLOR
                    
                    self.inventory_buttons.append(
                        Button(220, 120 + i * 60, 360, 50, item_text, color, 
                              tuple(min(255, c + 30) for c in color))
                    )
                
                self.enemy_turn()
            else:
                self.battle_log.append(f"[Ошибка] {msg}")
            
            if len(self.battle_log) > 4:
                self.battle_log = self.battle_log[-4:]
    
    def victory(self):
        """Победа в бою с выпадением лута"""
        self.player.gain_exp(self.enemy.exp_reward)
        self.player.gold += self.enemy.gold_reward
        
        self.player.stats["enemies_killed"] += 1
        self.player.stats["gold_earned"] += self.enemy.gold_reward
        
        if hasattr(self.enemy, 'is_boss') and self.enemy.is_boss:
            self.player.stats["bosses_killed"] += 1
        
        self.player.restore_mana(50)
        
        for _ in range(30):
            self.spawn_particles(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 1, WARNING_COLOR, "star")
        
        loot_messages = []
        skipped_items = 0
        
        for item in self.enemy.loot:
            if self.player.can_add_to_inventory():
                self.player.inventory.append(item)
                self.player.stats["items_collected"] += 1
                rarity_name = item.get_rarity_name()
                loot_messages.append(f"[ЛУТ] {item.name} ({rarity_name})")
            else:
                skipped_items += 1
        
        msg_parts = [f"ПОБЕДА! +{self.enemy.exp_reward} опыта, +{self.enemy.gold_reward} золота"]
        if loot_messages:
            msg_parts.extend(loot_messages)
        if skipped_items > 0:
            msg_parts.append(f"[!] Инвентарь полон! Пропущено предметов: {skipped_items}")
        
        self.message = "\n".join(msg_parts)
        self.message_timer = 180
        self.state = "victory"
    
    def defeat(self):
        self.message = "Вы погибли! Игра окончена."
        self.message_timer = 150
        self.state = "defeat"
    
    def run_away(self):
        chance = 0.6 if self.player.hp < self.player.max_hp * 0.3 else 0.4
        if random.random() < chance:
            self.battle_log.append("[Побег] Вы успешно сбежали!")
            self.state = "game"
        else:
            self.battle_log.append("[Побег] Не удалось сбежать!")
            self.enemy_turn()
        
        if len(self.battle_log) > 4:
            self.battle_log = self.battle_log[-4:]
    
    def spawn_particles(self, x, y, count, color, particle_type="circle"):
        """Создать частицы для эффектов"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color, particle_type))
    
    def update_particles(self, dt):
        """Обновить все частицы"""
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def draw_gradient_bg(self):
        """Красивый многослойный градиентный фон с эффектом глубины"""
        for i in range(SCREEN_HEIGHT):
            factor = i / SCREEN_HEIGHT
            if factor < 0.5:
                t = factor * 2
                color = (
                    int(BG_COLOR[0] + (18 - BG_COLOR[0]) * t),
                    int(BG_COLOR[1] + (12 - BG_COLOR[1]) * t),
                    int(BG_COLOR[2] + (45 - BG_COLOR[2]) * t)
                )
            else:
                t = (factor - 0.5) * 2
                color = (
                    int(18 + (BG_COLOR[0] - 18) * t),
                    int(12 + (BG_COLOR[1] - 12) * t),
                    int(45 + (BG_COLOR[2] - 45) * t)
                )
            pygame.draw.line(self.screen, color, (0, i), (SCREEN_WIDTH, i))
        
        time_ms = pygame.time.get_ticks()
        for i in range(3):
            offset_x = math.sin(time_ms / 3000 + i * 2) * 100
            offset_y = math.cos(time_ms / 4000 + i * 1.5) * 50
            x = SCREEN_WIDTH // 4 + i * SCREEN_WIDTH // 3 + offset_x
            y = SCREEN_HEIGHT // 3 + offset_y
            
            for radius in range(150, 0, -30):
                alpha = int(5 * (1 - radius / 150))
                surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                color = (40 + i * 20, 30 + i * 15, 80 + i * 30, alpha)
                pygame.draw.circle(surf, color, (radius, radius), radius)
                self.screen.blit(surf, (x - radius, y - radius))
    
    def draw_card(self, x, y, width, height, alpha=255):
        """Красивая современная карточка с эффектами"""
        shadow_layers = 3
        for i in range(shadow_layers):
            shadow_offset = 3 + i * 2
            shadow_alpha = int((40 - i * 10) * (alpha / 255))
            shadow = pygame.Surface((width + shadow_offset * 2, height + shadow_offset * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, shadow_alpha), shadow.get_rect(), border_radius=15)
            self.screen.blit(shadow, (x - shadow_offset // 2, y + shadow_offset))
        
        card = pygame.Surface((width, height), pygame.SRCALPHA)
        
        for i in range(height):
            factor = 1 - (i / height) * 0.08
            gradient_alpha = alpha
            color = tuple(int(c * factor) for c in CARD_BG)
            pygame.draw.line(card, (*color, gradient_alpha), (0, i), (width, i))
        
        pygame.draw.rect(card, (*CARD_BG, alpha), card.get_rect(), border_radius=12)
        
        self.screen.blit(card, (x, y))
        
        border_color = (255, 255, 255, int(35 * (alpha / 255)))
        pygame.draw.rect(self.screen, border_color, 
                        pygame.Rect(x, y, width, height), 1, border_radius=12)
        
        inner_border = pygame.Rect(x + 1, y + 1, width - 2, height - 2)
        pygame.draw.rect(self.screen, (255, 255, 255, int(15 * (alpha / 255))), 
                        inner_border, 1, border_radius=11)
        
        shine_width = width // 3
        shine_height = height // 4
        shine = pygame.Surface((shine_width, shine_height), pygame.SRCALPHA)
        for i in range(shine_height):
            for j in range(shine_width):
                distance = math.sqrt((i / shine_height) ** 2 + (j / shine_width) ** 2)
                shine_alpha = int(max(0, 25 * (1 - distance) * (alpha / 255)))
                shine.set_at((j, i), (255, 255, 255, shine_alpha))
        self.screen.blit(shine, (x + 10, y + 10))
    
    def draw_progress_bar(self, x, y, width, height, value, max_value, color, label=""):
        """Красивый прогресс-бар с градиентом и анимацией"""
        bg_rect = pygame.Rect(x, y, width, height)
        
        pygame.draw.rect(self.screen, (20, 25, 35), bg_rect, border_radius=height // 2)
        
        shadow_rect = bg_rect.inflate(-2, -2)
        pygame.draw.rect(self.screen, (15, 18, 25), shadow_rect, border_radius=height // 2)
        
        fill_width = int((value / max_value) * width) if max_value > 0 else 0
        if fill_width > 4:
            fill_rect = pygame.Rect(x, y, fill_width, height)
            
            for i in range(height):
                factor = 1 - (i / height) * 0.15
                gradient_color = tuple(int(c * factor) for c in color)
                line_rect = pygame.Rect(x + 2, y + i, fill_width - 4, 1)
                pygame.draw.rect(self.screen, gradient_color, line_rect)
            
            pygame.draw.rect(self.screen, color, fill_rect, border_radius=height // 2)
            
            shine_height = max(2, height // 3)
            shine = pygame.Surface((fill_width - 4, shine_height), pygame.SRCALPHA)
            for i in range(shine_height):
                shine_alpha = int(60 * (1 - i / shine_height))
                pygame.draw.line(shine, (255, 255, 255, shine_alpha), 
                               (0, i), (fill_width - 4, i))
            self.screen.blit(shine, (x + 2, y + 2))
            
            if fill_width < width - 2:
                pulse = abs(math.sin(pygame.time.get_ticks() / 800)) * 0.5 + 0.5
                edge_glow = pygame.Surface((8, height), pygame.SRCALPHA)
                for i in range(8):
                    alpha = int(40 * pulse * (1 - i / 8))
                    pygame.draw.line(edge_glow, (*color, alpha), (i, 0), (i, height))
                self.screen.blit(edge_glow, (x + fill_width - 4, y))
        
        border_color = tuple(min(255, c + 20) for c in color)
        pygame.draw.rect(self.screen, (*border_color, 100), bg_rect, 1, border_radius=height // 2)
        
        inner_border = bg_rect.inflate(-2, -2)
        pygame.draw.rect(self.screen, (255, 255, 255, 25), inner_border, 1, border_radius=height // 2)
        
        if label:
            text = FONT_TINY.render(f"{value}/{max_value}", True, TEXT_PRIMARY)
            text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
            
            shadow = FONT_TINY.render(f"{value}/{max_value}", True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(x + width // 2 + 1, y + height // 2 + 1))
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(text, text_rect)
            shadow_rect = shadow.get_rect(center=(x + width // 2 + 1, y + height // 2 + 1))
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(text, text_rect)
        
        pygame.draw.rect(self.screen, (255, 255, 255, 80), bg_rect, 1, border_radius=height // 2)
    
    def draw_menu(self):
        """Красивое главное меню с улучшенным дизайном"""
        self.draw_gradient_bg()
        
        for star in self.stars:
            star.update()
            star.draw(self.screen)
        
        for particle in self.particles:
            particle.draw(self.screen)
        
        if random.random() < 0.03:
            x = SCREEN_WIDTH // 2 + random.randint(-200, 200)
            y = 150 + random.randint(-30, 30)
            self.spawn_particles(x, y, 1, WARNING_COLOR, "star")
        
        title_text = "УБЕЙ ЗЛЮК"
        
        pulse = abs(math.sin(pygame.time.get_ticks() / 1000)) * 0.4 + 0.6
        
        glow_surface = pygame.Surface((SCREEN_WIDTH, 180), pygame.SRCALPHA)
        for i in range(50):
            glow_alpha = int(20 * pulse * (1 - i / 50))
            pygame.draw.ellipse(glow_surface, (*WARNING_COLOR, glow_alpha), 
                              (SCREEN_WIDTH // 2 - 280 - i, 70 - i // 2, 560 + i * 2, 50 + i))
        self.screen.blit(glow_surface, (0, 60))
        
        time_offset = pygame.time.get_ticks() / 1000
        for i in range(8):
            angle = (time_offset + i * math.pi / 4) % (2 * math.pi)
            x = SCREEN_WIDTH // 2 + math.cos(angle) * 180
            y = 145 + math.sin(angle) * 30
            particle_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            alpha = int(150 * pulse)
            pygame.draw.circle(particle_surf, (*WARNING_COLOR, alpha), (3, 3), 3)
            self.screen.blit(particle_surf, (x - 3, y - 3))
        
        for offset in range(3, 0, -1):
            shadow_alpha = 80 - offset * 20
            title_shadow = FONT_TITLE.render(title_text, True, (0, 0, 0, shadow_alpha))
            shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + offset, 147 + offset))
            self.screen.blit(title_shadow, shadow_rect)
        
        title = FONT_TITLE.render(title_text, True, WARNING_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 145))
        self.screen.blit(title, title_rect)
        
        title_outline = FONT_TITLE.render(title_text, True, (255, 255, 255, int(80 * pulse)))
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            outline_rect = title_outline.get_rect(center=(SCREEN_WIDTH // 2 + dx, 145 + dy))
            self.screen.blit(title_outline, outline_rect)
        self.screen.blit(title, title_rect)
        
        subtitle_pulse = abs(math.sin(pygame.time.get_ticks() / 800)) * 80 + 140
        subtitle = FONT_SMALL.render("Готовы к приключениям?", True, 
                                     (int(subtitle_pulse), int(subtitle_pulse), int(subtitle_pulse)))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 200))
        
        subtitle_shadow = FONT_SMALL.render("Готовы к приключениям?", True, (0, 0, 0))
        shadow_rect = subtitle_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 1, 201))
        self.screen.blit(subtitle_shadow, shadow_rect)
        self.screen.blit(subtitle, subtitle_rect)
        
        deco_y = 200
        for i in range(3):
            deco_x_left = SCREEN_WIDTH // 2 - 220 - i * 15
            deco_x_right = SCREEN_WIDTH // 2 + 220 + i * 15
            alpha = int(100 - i * 30)
            
            deco_surf = pygame.Surface((8, 2), pygame.SRCALPHA)
            deco_surf.fill((*TEXT_SECONDARY, alpha))
            self.screen.blit(deco_surf, (deco_x_left, deco_y))
            self.screen.blit(deco_surf, (deco_x_right, deco_y))
        
        for button in self.menu_buttons:
            button.update()
            button.draw(self.screen)
        
        footer_text = "v1.0 | RPG Adventure"
        footer = FONT_TINY.render(footer_text, True, TEXT_DISABLED)
        footer_rect = footer.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(footer, footer_rect)
    
    def draw_game(self):
        """Компактный игровой экран с улучшенным дизайном"""
        self.draw_gradient_bg()
        
        for i in range(0, len(self.stars), 4):
            self.stars[i].update()
            self.stars[i].draw(self.screen)
        
        for particle in self.particles:
            particle.draw(self.screen)
        
        if random.random() < 0.02:
            x = 210 + random.randint(-50, 50)
            y = 300 + random.randint(-100, 100)
            self.spawn_particles(x, y, 1, ACCENT_PRIMARY, "star")
        
        self.draw_card(30, 30, 360, 520)
        
        pulse = abs(math.sin(pygame.time.get_ticks() / 1200)) * 0.3 + 0.7
        title_color = tuple(int(c * pulse + (255 - c) * (1 - pulse) * 0.3) for c in ACCENT_PRIMARY)
        title = FONT_MEDIUM.render("Персонаж", True, title_color)
        self.screen.blit(title, (50, 45))
        
        for i in range(310):
            alpha = int(40 * (1 - abs(i - 155) / 155))
            pygame.draw.line(self.screen, (255, 255, 255, alpha), (50 + i, 70), (50 + i + 1, 70), 1)
        
        y = 80
        stats = [
            (f"Уровень: {self.player.level}", TEXT_PRIMARY),
            (f"Золото: {self.player.gold}", WARNING_COLOR),
        ]
        
        for text, color in stats:
            surface = FONT_SMALL.render(text, True, color)
            self.screen.blit(surface, (50, y))
            y += 28
        
        y = 140
        left_stats = [
            (f"Атака: {self.player.attack}", DANGER_COLOR),
            (f"Предметов: {len(self.player.inventory)}", INFO_COLOR),
        ]
        right_stats = [
            (f"Защита: {self.player.defense}", ACCENT_PRIMARY),
            (f"Навыков: {len(self.player.skills)}", PURPLE_COLOR),
        ]
        
        for (left_text, left_color), (right_text, right_color) in zip(left_stats, right_stats):
            left_surf = FONT_SMALL.render(left_text, True, left_color)
            right_surf = FONT_SMALL.render(right_text, True, right_color)
            self.screen.blit(left_surf, (50, y))
            self.screen.blit(right_surf, (220, y))
            y += 28
        
        for i in range(310):
            alpha = int(40 * (1 - abs(i - 155) / 155))
            pygame.draw.line(self.screen, (255, 255, 255, alpha), (50 + i, y + 5), (50 + i + 1, y + 5), 1)
        
        y = 235
        
        hp_label = FONT_SMALL.render("HP", True, DANGER_COLOR)
        self.screen.blit(hp_label, (50, y + 2))
        self.draw_progress_bar(90, y, 270, 20, self.player.hp, self.player.max_hp, DANGER_COLOR, "hp")
        
        y += 45
        mana_label = FONT_SMALL.render("MP", True, MANA_COLOR)
        self.screen.blit(mana_label, (50, y + 2))
        self.draw_progress_bar(90, y, 270, 20, self.player.mana, self.player.max_mana, MANA_COLOR, "mana")
        
        y += 45
        exp_label = FONT_SMALL.render("XP", True, WARNING_COLOR)
        self.screen.blit(exp_label, (50, y + 2))
        self.draw_progress_bar(90, y, 270, 20, self.player.exp, self.player.exp_to_level, WARNING_COLOR, "")
        
        exp_percent = int((self.player.exp / self.player.exp_to_level) * 100)
        percent_text = FONT_TINY.render(f"{exp_percent}%", True, TEXT_SECONDARY)
        percent_rect = percent_text.get_rect(center=(225, y + 28))
        self.screen.blit(percent_text, percent_rect)
        
        y += 50
        for i in range(310):
            alpha = int(40 * (1 - abs(i - 155) / 155))
            pygame.draw.line(self.screen, (255, 255, 255, alpha), (50 + i, y), (50 + i + 1, y), 1)
        
        if self.player.status_effects:
            y += 10
            status_title = FONT_TINY.render("Активные эффекты:", True, TEXT_SECONDARY)
            self.screen.blit(status_title, (50, y))
            y += 20
            for effect in self.player.status_effects:
                effect_text = FONT_TINY.render(f"[ЗАЩИТА] x{self.player.status_effects[effect]}", True, ACCENT_PRIMARY)
                self.screen.blit(effect_text, (50, y))
                y += 18
        
        y = 515
        hint_pulse = abs(math.sin(pygame.time.get_ticks() / 600)) * 0.3 + 0.7
        hint_color = tuple(int(c * hint_pulse) for c in TEXT_SECONDARY)
        hint_text = FONT_TINY.render("Выберите действие ниже", True, hint_color)
        hint_rect = hint_text.get_rect(center=(210, y))
        self.screen.blit(hint_text, hint_rect)
        
        if self.message_timer > 0:
            msg_width = 480
            msg_height = 90
            msg_x = SCREEN_WIDTH // 2 - msg_width // 2
            msg_y = 220
            
            pulse = abs(math.sin(pygame.time.get_ticks() / 500)) * 0.3 + 0.7
            
            self.draw_card(msg_x, msg_y, msg_width, msg_height)
            
            stripe_rect = pygame.Rect(msg_x, msg_y, msg_width, 4)
            pygame.draw.rect(self.screen, WARNING_COLOR, stripe_rect, border_radius=10)
            
            msg_surface = FONT_MEDIUM.render(self.message, True, WARNING_COLOR)
            msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, msg_y + 45))
            
            msg_surface.set_alpha(int(255 * pulse))
            self.screen.blit(msg_surface, msg_rect)
        
        for button in self.game_buttons:
            button.update()
            button.draw(self.screen)
    
    def draw_battle(self):
        """Компактный экран боя"""
        self.draw_gradient_bg()
        
        for i in range(0, len(self.stars), 3):
            self.stars[i].update()
            self.stars[i].draw(self.screen)
        
        for particle in self.particles:
            particle.draw(self.screen)
        
        self.draw_card(40, 30, 280, 180)
        player_title = FONT_MEDIUM.render("Герой", True, SUCCESS_COLOR)
        self.screen.blit(player_title, (60, 45))
        
        y = 85
        player_stats = [
            (f"АТК: {self.player.attack}", DANGER_COLOR),
            (f"ЗАЩ: {self.player.defense}", ACCENT_PRIMARY),
        ]
        
        x_pos = 60
        for text, color in player_stats:
            surface = FONT_SMALL.render(text, True, color)
            self.screen.blit(surface, (x_pos, y))
            x_pos += 110
        
        y = 120
        self.draw_progress_bar(60, y, 240, 18, self.player.hp, self.player.max_hp, DANGER_COLOR)
        y += 30
        self.draw_progress_bar(60, y, 240, 18, self.player.mana, self.player.max_mana, MANA_COLOR)
        
        if self.player.status_effects:
            y = 180
            status_text = "[ЗАЩИТА]"
            status_surf = FONT_TINY.render(status_text, True, ACCENT_PRIMARY)
            self.screen.blit(status_surf, (60, y))
        
        self.draw_card(580, 30, 280, 180)
        enemy_title = FONT_MEDIUM.render(f"{self.enemy.name}", True, DANGER_COLOR)
        self.screen.blit(enemy_title, (600, 45))
        
        y = 85
        enemy_stats = [
            (f"АТК: {self.enemy.attack}", DANGER_COLOR),
            (f"ЗАЩ: {self.enemy.defense}", ACCENT_PRIMARY),
        ]
        
        x_pos = 600
        for text, color in enemy_stats:
            surface = FONT_SMALL.render(text, True, color)
            self.screen.blit(surface, (x_pos, y))
            x_pos += 110
        
        y = 120
        self.draw_progress_bar(600, y, 240, 18, self.enemy.hp, self.enemy.max_hp, DANGER_COLOR)
        
        if self.enemy.defending:
            y = 150
            status_text = "[В ЗАЩИТЕ]"
            status_surf = FONT_TINY.render(status_text, True, INFO_COLOR)
            self.screen.blit(status_surf, (600, y))
        elif self.enemy.charge > 0:
            y = 150
            status_text = "[ЗАРЯДКА]"
            status_surf = FONT_TINY.render(status_text, True, WARNING_COLOR)
            self.screen.blit(status_surf, (600, y))
        
        if self.battle_log:
            log_height = min(len(self.battle_log) * 35 + 30, 180)
            self.draw_card(150, 240, 600, log_height)
            
            log_title = FONT_SMALL.render("Лог боя", True, TEXT_SECONDARY)
            self.screen.blit(log_title, (170, 250))
            
            y = 280
            for i, log in enumerate(self.battle_log[-4:]):
                log_surf = FONT_TINY.render(log, True, TEXT_PRIMARY)
                self.screen.blit(log_surf, (170, y))
                y += 35
        
        for button in self.battle_main_buttons:
            button.update()
            button.draw(self.screen)
        
        if self.skills_modal.is_open:
            self.skills_modal.update()
            self.skills_modal.draw_background(self.screen)
            modal_rect = self.skills_modal.draw(self.screen)
            
            if modal_rect and self.skills_modal.animation_progress > 0.5:
                for button in self.skill_buttons:
                    button.update()
                    button.draw(self.screen)
                
                desc_y = modal_rect.bottom - 100
                desc_text = FONT_TINY.render("Выберите навык для использования", True, TEXT_SECONDARY)
                desc_rect = desc_text.get_rect(centerx=modal_rect.centerx, y=desc_y)
                self.screen.blit(desc_text, desc_rect)
        
        if self.inventory_modal.is_open:
            self.inventory_modal.update()
            self.inventory_modal.draw_background(self.screen)
            modal_rect = self.inventory_modal.draw(self.screen)
            
            if modal_rect and self.inventory_modal.animation_progress > 0.5:
                if self.inventory_buttons:
                    for button in self.inventory_buttons:
                        button.update()
                        button.draw(self.screen)
                    
                    hint_y = modal_rect.bottom - 60
                    hint_text = FONT_TINY.render("Зелья можно использовать в меню и в бою", True, TEXT_SECONDARY)
                    hint_rect = hint_text.get_rect(centerx=modal_rect.centerx, y=hint_y)
                    self.screen.blit(hint_text, hint_rect)
                    
                    hint2_text = FONT_TINY.render("Оружие и броню можно использовать только в бою", True, TEXT_SECONDARY)
                    hint2_rect = hint2_text.get_rect(centerx=modal_rect.centerx, y=hint_y + 18)
                    self.screen.blit(hint2_text, hint2_rect)
                else:
                    empty_text = FONT_SMALL.render("Инвентарь пуст", True, TEXT_SECONDARY)
                    empty_rect = empty_text.get_rect(center=(modal_rect.centerx, modal_rect.centery))
                    self.screen.blit(empty_text, empty_rect)
        
        if self.item_detail_window.is_open or self.item_detail_window.animation_progress > 0:
            self.item_detail_window.update()
            self.item_detail_window.draw(self.screen)
    
    def draw_shop(self):
        """Улучшенный магазин"""
        self.draw_gradient_bg()
        
        for i in range(0, len(self.stars), 3):
            self.stars[i].update()
            self.stars[i].draw(self.screen)
        
        title = FONT_TITLE.render("МАГАЗИН", True, WARNING_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        
        title_shadow = FONT_TITLE.render("МАГАЗИН", True, (0, 0, 0))
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, 82))
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title, title_rect)
        
        info_y = 130
        info_width = 700
        info_x = (SCREEN_WIDTH - info_width) // 2
        self.draw_card(info_x, info_y, info_width, 60)
        
        gold_text = FONT_MEDIUM.render(f"Золото: {self.player.gold}", True, WARNING_COLOR)
        self.screen.blit(gold_text, (info_x + 20, info_y + 18))
        
        stats_text = FONT_SMALL.render(
            f"Атака: {self.player.attack}  Защита: {self.player.defense}  HP: {self.player.hp}/{self.player.max_hp}  Мана: {self.player.mana}/{self.player.max_mana}",
            True, TEXT_SECONDARY
        )
        self.screen.blit(stats_text, (info_x + 200, info_y + 20))
        
        for button in self.shop_buttons[:-1]:
            button.update()
            button.draw(self.screen)
        
        self.shop_buttons[-1].update()
        self.shop_buttons[-1].draw(self.screen)
        
        if self.message_timer > 0:
            msg_width = 500
            msg_height = 60
            msg_x = SCREEN_WIDTH // 2 - msg_width // 2
            msg_y = 560
            
            alpha = min(255, self.message_timer * 3)
            self.draw_card(msg_x, msg_y, msg_width, msg_height, alpha)
            msg_surface = FONT_SMALL.render(self.message, True, TEXT_PRIMARY)
            msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, msg_y + 30))
            self.screen.blit(msg_surface, msg_rect)
    
    def draw_locations(self):
        """Экран выбора локаций с современным дизайном"""
        self.draw_gradient_bg()
        
        for i in range(0, len(self.stars), 3):
            self.stars[i].update()
            self.stars[i].draw(self.screen)
        
        for particle in self.particles:
            particle.draw(self.screen)
        
        title_text = "ЛОКАЦИИ"
        
        glow_surface = pygame.Surface((SCREEN_WIDTH, 120), pygame.SRCALPHA)
        for i in range(30):
            glow_alpha = int(12 * (1 - i / 30))
            pygame.draw.ellipse(glow_surface, (*ACCENT_PRIMARY, glow_alpha), 
                              (SCREEN_WIDTH // 2 - 200 - i, 60 - i // 2, 400 + i * 2, 30 + i))
        self.screen.blit(glow_surface, (0, 60))
        
        title_shadow = FONT_TITLE.render(title_text, True, (0, 0, 0))
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, 102))
        self.screen.blit(title_shadow, shadow_rect)
        
        title = FONT_TITLE.render(title_text, True, ACCENT_PRIMARY)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        subtitle = FONT_SMALL.render(f"Ваш уровень: {self.player.level}", True, TEXT_PRIMARY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(subtitle, subtitle_rect)
        
        for i, (loc_button, boss_button) in enumerate(zip(self.location_buttons, self.boss_buttons)):
            loc_button.update()
            loc_button.draw(self.screen)
            
            boss_button.update()
            boss_button.draw(self.screen)
        
        back_button = Button(250, 540, 400, 50, "Назад в меню", (70, 80, 100), (90, 100, 120))
        back_button.update()
        back_button.draw(self.screen)
        
        if not hasattr(self, 'locations_back_button'):
            self.locations_back_button = back_button
        else:
            self.locations_back_button = back_button
    
    def draw_stats(self):
        """Экран статистики игрока"""
        self.draw_gradient_bg()
        
        for i in range(0, len(self.stars), 3):
            self.stars[i].update()
            self.stars[i].draw(self.screen)
        
        title_text = "СТАТИСТИКА"
        
        glow_surface = pygame.Surface((SCREEN_WIDTH, 120), pygame.SRCALPHA)
        for i in range(30):
            glow_alpha = int(12 * (1 - i / 30))
            pygame.draw.ellipse(glow_surface, (*INFO_COLOR, glow_alpha), 
                              (SCREEN_WIDTH // 2 - 200 - i, 60 - i // 2, 400 + i * 2, 30 + i))
        self.screen.blit(glow_surface, (0, 60))
        
        title_shadow = FONT_TITLE.render(title_text, True, (0, 0, 0))
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, 102))
        self.screen.blit(title_shadow, shadow_rect)
        
        title = FONT_TITLE.render(title_text, True, INFO_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        card_width = 600
        card_height = 400
        card_x = (SCREEN_WIDTH - card_width) // 2
        card_y = 160
        
        self.draw_card(card_x, card_y, card_width, card_height)
        
        y = card_y + 30
        
        stats_data = [
            ("Убито врагов:", self.player.stats["enemies_killed"], DANGER_COLOR),
            ("Убито боссов:", self.player.stats["bosses_killed"], PURPLE_COLOR),
            ("Заработано золота:", self.player.stats["gold_earned"], WARNING_COLOR),
            ("Критических ударов:", self.player.stats["critical_hits"], WARNING_COLOR),
            ("Нанесено урона:", self.player.stats["total_damage_dealt"], DANGER_COLOR),
            ("Получено урона:", self.player.stats["total_damage_taken"], INFO_COLOR),
            ("Собрано предметов:", self.player.stats["items_collected"], SUCCESS_COLOR),
            ("Использовано зелий:", self.player.stats["potions_used"], MANA_COLOR),
        ]
        
        for i, (label, value, color) in enumerate(stats_data):
            col = i % 2
            row = i // 2
            
            x = card_x + 40 + col * 300
            y_pos = y + row * 45
            
            label_surf = FONT_SMALL.render(label, True, TEXT_SECONDARY)
            self.screen.blit(label_surf, (x, y_pos))
            
            value_surf = FONT_MEDIUM.render(str(value), True, color)
            self.screen.blit(value_surf, (x, y_pos + 20))
        
        self.stats_back_button.update()
        self.stats_back_button.draw(self.screen)
    
    def draw_equipment(self):
        """Экран экипировки"""
        self.draw_gradient_bg()
        
        for i in range(0, len(self.stars), 3):
            self.stars[i].update()
            self.stars[i].draw(self.screen)
        
        if self.equipment_modal.is_open:
            self.equipment_modal.update()
            self.equipment_modal.draw_background(self.screen)
            modal_rect = self.equipment_modal.draw(self.screen)
            
            if modal_rect and self.equipment_modal.animation_progress > 0.5:
                for slot_type, slot in self.equipment_slots.items():
                    equipped_item = self.player.equipped.get(slot_type)
                    slot.draw(self.screen, equipped_item)
                
                inv_title = FONT_MEDIUM.render("Инвентарь", True, TEXT_PRIMARY)
                self.screen.blit(inv_title, (400, 115))
                
                equipment_items = [item for item in self.player.inventory 
                                  if item.item_type in ["weapon", "armor"]]
                slot_text = FONT_TINY.render(f"{len(equipment_items)} предметов", True, TEXT_SECONDARY)
                self.screen.blit(slot_text, (550, 120))
                
                for i, button in enumerate(self.inventory_buttons):
                    button.update()
                    button.draw(self.screen)
                
                hint_y = modal_rect.bottom - 60
                if self.sell_mode:
                    hint_text = FONT_TINY.render("РЕЖИМ ПРОДАЖИ: Выберите предмет для продажи", True, DANGER_COLOR)
                else:
                    hint_text = FONT_TINY.render("Кликните на предмет для экипировки или на слот для снятия", True, TEXT_SECONDARY)
                hint_rect = hint_text.get_rect(centerx=modal_rect.centerx, y=hint_y)
                self.screen.blit(hint_text, hint_rect)
                
                if self.sell_mode:
                    self.equipment_sell_button.text = "ОТМЕНИТЬ ПРОДАЖУ"
                    self.equipment_sell_button.color = WARNING_COLOR
                    self.equipment_sell_button.hover_color = tuple(min(255, c + 30) for c in WARNING_COLOR)
                else:
                    self.equipment_sell_button.text = "Продать предмет"
                    self.equipment_sell_button.color = DANGER_COLOR
                    self.equipment_sell_button.hover_color = DANGER_HOVER
                
                self.equipment_sell_button.update()
                self.equipment_sell_button.draw(self.screen)
                
                self.equipment_back_button.update()
                self.equipment_back_button.draw(self.screen)
        
        if self.item_detail_window.is_open or self.item_detail_window.animation_progress > 0:
            self.item_detail_window.update()
            self.item_detail_window.draw(self.screen)
    
    def handle_menu_events(self, event):
        for i, button in enumerate(self.menu_buttons):
            if button.handle_event(event):
                if i == 0:
                    self.new_game()
                elif i == 1:
                    self.running = False
    
    def handle_game_events(self, event):
        for i, button in enumerate(self.game_buttons):
            if button.handle_event(event):
                if i == 0:
                    self.open_locations()
                elif i == 1:
                    self.state = "shop"
                    self.update_shop_buttons()
                    self.message = "Добро пожаловать в магазин!"
                    self.message_timer = 60
                elif i == 2:
                    self.open_equipment()
                elif i == 3:
                    self.state = "stats"
    
    def handle_battle_events(self, event):
        if self.skills_modal.is_open:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                modal_rect = pygame.Rect(self.skills_modal.x, self.skills_modal.y, 
                                        self.skills_modal.width, self.skills_modal.height)
                if not modal_rect.collidepoint(mouse_pos):
                    self.skills_modal.close()
            
            for i, button in enumerate(self.skill_buttons):
                if button.handle_event(event):
                    self.use_skill(i)
            return
        
        if self.inventory_modal.is_open:
            mouse_pos = pygame.mouse.get_pos()
            hovered_item = None
            
            for i, button in enumerate(self.inventory_buttons):
                if button.rect.collidepoint(mouse_pos) and i < len(self.player.inventory):
                    hovered_item = (self.player.inventory[i], mouse_pos[0], mouse_pos[1])
                    break
            
            if hovered_item and event.type == pygame.MOUSEMOTION:
                self.item_detail_window.open(hovered_item[0], hovered_item[1], hovered_item[2])
            elif not hovered_item and self.item_detail_window.is_open:
                self.item_detail_window.close()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                modal_rect = pygame.Rect(self.inventory_modal.x, self.inventory_modal.y, 
                                        self.inventory_modal.width, self.inventory_modal.height)
                if not modal_rect.collidepoint(mouse_pos):
                    self.inventory_modal.close()
                    self.item_detail_window.close()
            
            for i, button in enumerate(self.inventory_buttons):
                if button.handle_event(event):
                    self.use_item_in_battle(i)
                    self.item_detail_window.close()
            return
        
        for i, button in enumerate(self.battle_main_buttons):
            if button.handle_event(event):
                if i == 0:
                    self.player_basic_attack()
                elif i == 1:
                    self.open_skills_modal()
                elif i == 2:
                    self.open_inventory_modal()
                elif i == 3:
                    self.run_away()
    
    def handle_shop_events(self, event):
        """Обработка событий магазина"""
        for i, button in enumerate(self.shop_buttons):
            if button.handle_event(event):
                if i < len(self.shop_items):
                    shop_item = self.shop_items[i]
                    self.buy_shop_item(shop_item)
                elif i == len(self.shop_items):
                    self.state = "game"
                return
    
    def buy_shop_item(self, shop_item):
        """Купить товар в магазине"""
        price = shop_item.get_current_price(self.player)
        
        if self.player.gold < price:
            self.message = f"Недостаточно золота! Нужно {price}"
            self.message_timer = 60
            return
        
        if shop_item.item_type in ["potion_hp", "potion_mana"]:
            if not self.player.can_add_to_inventory():
                self.message = "Инвентарь полон! (макс. 10 предметов)"
                self.message_timer = 90
                return
            
            self.player.gold -= price
            item_type = shop_item.item_type
            value = shop_item.item_data["value"]
            self.player.inventory.append(
                Item(shop_item.name, item_type, value, shop_item.description, "common")
            )
            self.message = f"Куплено: {shop_item.name}!"
            self.message_timer = 60
        
        elif shop_item.item_type == "potion_multi":
            if not self.player.can_add_to_inventory():
                self.message = "Инвентарь полон! (макс. 10 предметов)"
                self.message_timer = 90
                return
            
            self.player.gold -= price
            self.player.inventory.append(
                Item(shop_item.name, "potion_multi", shop_item.item_data["hp"], 
                     f"HP +{shop_item.item_data['hp']}, Мана +{shop_item.item_data['mana']}", 
                     "uncommon")
            )
            self.player.inventory[-1].mana_value = shop_item.item_data["mana"]
            self.message = f"Куплено: {shop_item.name}!"
            self.message_timer = 60
        
        elif shop_item.item_type == "upgrade_attack":
            self.player.gold -= price
            self.player.attack += shop_item.item_data["value"]
            self.player.attack_upgrades_bought += 1
            self.update_shop_buttons()
            self.message = f"Атака +{shop_item.item_data['value']}! Новая цена: {shop_item.get_current_price(self.player)} золота"
            self.message_timer = 90
        
        elif shop_item.item_type == "upgrade_defense":
            self.player.gold -= price
            self.player.defense += shop_item.item_data["value"]
            self.player.defense_upgrades_bought += 1
            self.update_shop_buttons()
            self.message = f"Защита +{shop_item.item_data['value']}! Новая цена: {shop_item.get_current_price(self.player)} золота"
            self.message_timer = 90
        
        elif shop_item.item_type == "upgrade_hp":
            self.player.gold -= price
            self.player.max_hp += shop_item.item_data["value"]
            self.player.hp += shop_item.item_data["value"]  # Восстанавливаем тоже
            self.message = f"Макс. HP +{shop_item.item_data['value']}!"
            self.message_timer = 60
        
        elif shop_item.item_type == "upgrade_mana":
            self.player.gold -= price
            self.player.max_mana += shop_item.item_data["value"]
            self.player.mana += shop_item.item_data["value"]  # Восстанавливаем тоже
            self.message = f"Макс. мана +{shop_item.item_data['value']}!"
            self.message_timer = 60
        
        elif shop_item.item_type == "equipment":
            if not self.player.can_add_to_inventory():
                self.message = "Инвентарь полон! (макс. 10 предметов)"
                self.message_timer = 90
                return
            
            self.player.gold -= price
            data = shop_item.item_data
            item = Item(
                shop_item.name,
                data["item_type"],
                data["value"],
                shop_item.description,
                data["rarity"],
                data.get("effect"),
                data.get("armor_slot")
            )
            self.player.inventory.append(item)
            
            if shop_item.stock != "unlimited":
                self.shop_items.remove(shop_item)
                self.update_shop_buttons()
            
            rarity_name = item.get_rarity_name()
            self.message = f"Куплено: {shop_item.name} ({rarity_name})!"
            self.message_timer = 90
    
    def update_shop_buttons(self):
        """Обновить кнопки магазина"""
        self.shop_buttons = []
        y = 230
        
        for i, shop_item in enumerate(self.shop_items):
            price = shop_item.get_current_price(self.player)
            text = f"{shop_item.name} ({price} золота)"
            
            color = shop_item.get_color()
            hover = tuple(min(255, c + 30) for c in color)
            
            button = Button(200, y, 500, 50, text, color, hover)
            self.shop_buttons.append(button)
            y += 60
        
        self.shop_buttons.append(
            Button(300, y + 10, 300, 50, "Назад", (60, 70, 90), (80, 90, 110))
        )
    
    def handle_locations_events(self, event):
        """Обработка событий экрана локаций"""
        if self.locations_back_button.handle_event(event):
            self.state = "game"
            return
        
        for i, button in enumerate(self.location_buttons):
            if button.handle_event(event):
                location = self.locations[i]
                if self.player.level >= location["level_req"]:
                    self.start_battle_in_location(i, is_boss=False)
                else:
                    self.message = f"Требуется {location['level_req']} уровень!"
                    self.message_timer = 90
                return
        
        for i, button in enumerate(self.boss_buttons):
            if button.handle_event(event):
                location = self.locations[i]
                if self.player.level >= location["level_req"]:
                    self.start_battle_in_location(i, is_boss=True)
                else:
                    self.message = f"Требуется {location['level_req']} уровень!"
                    self.message_timer = 90
                return
    
    def handle_equipment_events(self, event):
        """Обработка событий экрана экипировки"""
        if self.equipment_back_button.handle_event(event):
            self.state = "game"
            self.equipment_modal.close()
            self.item_detail_window.close()
            return
        
        equipment_items = [(idx, item) for idx, item in enumerate(self.player.inventory) 
                          if item.item_type in ["weapon", "armor"]]
        
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            hovered_item = None
            
            for i, button in enumerate(self.inventory_buttons):
                if button.rect.collidepoint(mouse_pos) and i < len(equipment_items):
                    hovered_item = (equipment_items[i][1], mouse_pos[0], mouse_pos[1])
                    break
            
            if hovered_item:
                self.item_detail_window.open(hovered_item[0], hovered_item[1], hovered_item[2])
            elif self.item_detail_window.is_open:
                self.item_detail_window.close()
        
        for slot_type, slot in self.equipment_slots.items():
            if slot.handle_event(event):
                success, msg = self.player.unequip_item(slot_type)
                if success:
                    self.message = msg
                    self.message_timer = 90
                    self.update_equipment_inventory_buttons()
                return
        
        for i, button in enumerate(self.inventory_buttons):
            if button.handle_event(event):
                if i < len(equipment_items):
                    actual_index, item = equipment_items[i]
                    
                    if self.sell_mode:
                        sell_price = item.calculate_sell_price()
                        self.player.gold += sell_price
                        self.player.inventory.pop(actual_index)
                        self.message = f"Продано: {item.name} за {sell_price} золота"
                        self.message_timer = 90
                        self.update_equipment_inventory_buttons()
                        self.sell_mode = False
                    else:
                        success, msg = self.player.use_item(actual_index)
                        if success:
                            self.message = msg
                            self.message_timer = 90
                            self.update_equipment_inventory_buttons()
                return
        
        if self.equipment_sell_button.handle_event(event):
            self.sell_mode = not self.sell_mode
            if self.sell_mode:
                self.message = "Выберите предмет для продажи"
                self.message_timer = 90
            else:
                self.message = "Режим продажи отключён"
                self.message_timer = 60
                self.selected_sell_item = None
            return
    
    def run(self):
        """Основной игровой цикл"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.state == "menu":
                    self.handle_menu_events(event)
                elif self.state == "game":
                    self.handle_game_events(event)
                elif self.state == "battle":
                    self.handle_battle_events(event)
                elif self.state == "victory":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.state = "game"
                        self.message = "Готовы к новым приключениям!"
                        self.message_timer = 60
                elif self.state == "defeat":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.state = "menu"
                elif self.state == "shop":
                    self.handle_shop_events(event)
                elif self.state == "locations":
                    self.handle_locations_events(event)
                elif self.state == "stats":
                    if self.stats_back_button.handle_event(event):
                        self.state = "game"
                elif self.state == "equipment":
                    self.handle_equipment_events(event)
            
            if self.message_timer > 0:
                self.message_timer -= 1
            
            for star in self.stars:
                star.update(dt)
            self.update_particles(dt)
            
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "game":
                self.draw_game()
            elif self.state == "battle":
                self.draw_battle()
            elif self.state == "victory":
                self.draw_battle()
                
                victory_width = 500
                message_lines = self.message.split('\n')
                victory_height = 140 + len(message_lines) * 25
                victory_x = SCREEN_WIDTH // 2 - victory_width // 2
                victory_y = SCREEN_HEIGHT // 2 - victory_height // 2
                
                self.draw_card(victory_x, victory_y, victory_width, victory_height)
                
                victory_text = FONT_LARGE.render("ПОБЕДА!", True, SUCCESS_COLOR)
                victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, victory_y + 30))
                self.screen.blit(victory_text, victory_rect)
                
                y_offset = victory_y + 70
                for line in message_lines:
                    line_surf = FONT_SMALL.render(line, True, TEXT_PRIMARY)
                    line_rect = line_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                    self.screen.blit(line_surf, line_rect)
                    y_offset += 25
                
                click_text = FONT_TINY.render("Нажмите для продолжения", True, TEXT_SECONDARY)
                click_rect = click_text.get_rect(center=(SCREEN_WIDTH // 2, victory_y + victory_height - 25))
                self.screen.blit(click_text, click_rect)
                
            elif self.state == "defeat":
                self.draw_gradient_bg()
                
                defeat_width = 420
                defeat_height = 180
                defeat_x = SCREEN_WIDTH // 2 - defeat_width // 2
                defeat_y = SCREEN_HEIGHT // 2 - defeat_height // 2
                
                self.draw_card(defeat_x, defeat_y, defeat_width, defeat_height)
                
                defeat_text = FONT_LARGE.render("ПОРАЖЕНИЕ", True, DANGER_COLOR)
                defeat_rect = defeat_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
                self.screen.blit(defeat_text, defeat_rect)
                
                click_text = FONT_SMALL.render("Нажмите для возврата", True, TEXT_SECONDARY)
                click_rect = click_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
                self.screen.blit(click_text, click_rect)
                
            elif self.state == "shop":
                self.draw_shop()
            elif self.state == "locations":
                self.draw_locations()
            elif self.state == "stats":
                self.draw_stats()
            elif self.state == "equipment":
                self.draw_equipment()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
