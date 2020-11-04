class Character:

    def __init__(self, name, height, favouriteFood):
        self.name = name
        self.height = height
        self.favouriteFood = favouriteFood
        self.health = 100

    def getFavouriteFood(self):
        return self.favouriteFood

    def takeDamage(self):
        self.health -= 10

    def changeFavouriteFood(newFood):
        self.favouriteFood = newFood