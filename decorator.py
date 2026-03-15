from abc import ABC, abstractmethod


class Hero(ABC):

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def get_damage(self) -> int:
        pass

    @abstractmethod
    def get_defense(self) -> int:
        pass


class Warrior(Hero):
    def get_description(self):
        return "Warrior"

    def get_damage(self):
        return 15

    def get_defense(self):
        return 20


class Mage(Hero):
    def get_description(self):
        return "Mage"

    def get_damage(self):
        return 20

    def get_defense(self):
        return 10


class Palladin(Hero):
    def get_description(self):
        return "Palladin"

    def get_damage(self):
        return 30

    def get_defense(self):
        return 40


class ItemDecorator(Hero):
    def __init__(self, hero: Hero):
        self._hero = hero

    def get_description(self):
        return self._hero.get_description()

    def get_damage(self):
        return self._hero.get_damage()

    def get_defense(self):
        return self._hero.get_defense()


class Sword(ItemDecorator):
    def get_description(self): return self._hero.get_description() + " + Меч"
    def get_damage(self): return self._hero.get_damage() + 15


class MageRobe(ItemDecorator):
    def get_description(self): return self._hero.get_description() + " + Мантія"
    def get_defense(self): return self._hero.get_defense() + 10


class Amulet(ItemDecorator):
    def get_description(self): return self._hero.get_description() + " + Амулет"
    def get_damage(self): return self._hero.get_damage() + 20
    def get_defense(self): return self._hero.get_defense() + 10


def show(hero: Hero):
    print(f"{hero.get_description()}")
    print(f"Атака: {hero.get_damage()} | Захист: {hero.get_defense()}\n")


def main():
    warrior = Sword(Sword(Warrior()))
    mage = Amulet(MageRobe(Mage()))
    paladin = Sword(Amulet(Palladin()))

    show(warrior)
    show(mage)
    show(paladin)


if __name__ == "__main__":
    main()