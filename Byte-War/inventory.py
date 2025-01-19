class Inventory:
    def __init__(self, owner):
        self.owner = owner
        self.items = []

    @property
    def can_store(self):
        return len(self.items) == 0

    @property
    def can_drop(self):
        return len(self.items) > 0

    def pick(self, item):
        if self.can_store:
            self.items.append(item)

    def drop(self):
        if self.can_drop:
            return self.items.pop()
