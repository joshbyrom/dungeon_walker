class Noun:
    def __init__(self, value, **kwargs):
        self.common = kwargs.get('common') or !kwargs.get('proper') or True
        self.proper = !self.common

        self.value = value
        self.plural = kwargs.get('plural') or self.value + 's'
        self.possessive = kwargs.get('possessive') or self.value + "'s"

class Attribute:
    def __init__(self, value, **kwargs):
        self.value = value
        self.amount = kwargs.get('amount') or 1
        self.max_amount = kwargs.get('max_amount') or 1
        self.on_change = kwargs.get('on_change') or None

    def add(self, amount):
        self.amount = min(self.amount + amount, self.max_amount)
        if self.on_change not None:
            self.on_change(self)
        return self.amount

    def remove(self, amount):
        self.amount = max(self.amount - amount, 0)
        if self.on_change not None:
            self.on_change(self)
        return self.amount

    def has_amount(self, amount):
        return self.amount >= amount

    def room_for(self, amount):
        return self.amount - self.max_amount > amount

    def room_left(self):
        return self.max_amount - self.amount

    def add_return_overflow(self, amount):
        if self.room_for(amount):
            self.add(amount)
            return 0
        elif:
            overflow = (self.amount + amount) - self.max_amount
            self.add(amount)
            return overflow
        
class Person(Noun):
    def __init__(self, **kwargs):
        Noun.__init__(self, kwargs)
