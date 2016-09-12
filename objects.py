class Noun:
    def __init__(self, value, **kwargs):
        self.common = kwargs.get('common') or (not kwargs.get('proper')) or True
        self.proper = not self.common

        self.value = value
        self.plural = kwargs.get('plural') or self.value + 's'
        self.possessive = kwargs.get('possessive') or self.value + "'s"

class Attribute:
    def __init__(self, value, **kwargs):
        self.value = value
        self.amount = kwargs.get('amount') or 0
        self.max_amount = kwargs.get('max_amount') or self.amount
        self.on_change = kwargs.get('on_change') or None

    def add(self, amount):
        self.amount = min(self.amount + amount, self.max_amount)
        if self.on_change is not None:
            self.on_change(self)
        return self.amount

    def remove(self, amount):
        self.amount = max(self.amount - amount, 0)
        if self.on_change is not None:
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
        else:
            overflow = (self.amount + amount) - self.max_amount
            self.add(amount)
            return overflow

class LeveledAttribute(Attribute):
    def __init__(self, **kwargs):
        Attribute.__init__(self, **kwargs)

        self.level = kwargs.get('level') or 1
        self.max_level = kwargs.get('max_level') or 999999999
        self.experience = kwargs.get('experience') or 0
        self.experience_to_level = kwargs.get('experience_to_level') or 1000
        
        self.amount_per_level = kwargs.get('per_level') or 1

    def gain_experience(self, amount):
        self.experience = self.experience + amount

        if self.experience_to_level == 0:
            return
        
        while self.experience > self.experience_to_level:
            self.experience = self.experience - self.experience_to_level
            self.level = min(self.level + 1, self.max_level)
            self.amount = self.amount + self.amount_per_level
        
class Person(Noun):
    def __init__(self, **kwargs):
        Noun.__init__(self, kwargs.get('name') or 'unknown', **kwargs)

        self.proper = True
        self.common = False
        
        self.name = self.value
        self.possessive = self.value + "'s"
        
        self.position = kwargs.get('position') or (0,0)
        self.animation = kwargs.get('animation') or None
        self.attributes = kwargs.get('attributes') or []

        self.inventory = Inventory()

    def _run_callback_on_attribute(self, attribute, callback=None):
        if callback is not None:
            if isinstance(callback, list):
                for f in callback:
                    f(attribute)
            else:
                callback(attribute)
        return attribute

    def get_attribute(self, value, fun=None):
        for attribute in self.attributes:
            if attribute.value == value:
                return self._run_callback_on_attribute(attribute, fun)

        # always return an attribute that is mutable
        as_needed = Attribute(value=value, amount=0)
        self.attributes.append(as_needed)
        return self._run_callback_on_attribute(as_needed, fun)

    def get_attribute_as_string(self, value, fun=None):
        attr = self.get_attribute(value, fun)
        return self.possessive + ' ' + value + ' is ' + str(attr.amount) + ' of ' + str(attr.max_amount)

    def add_attribute(self, attribute):
        exists = self.get_attribute(attribute.value)
        if exists is not None:
            exists.add(attribute.amount)
        else:
            self.attributes.append(attribute)

    def interact(self, other):
        pass

class Thing(Noun):
    def __init__(self, **kwargs):
        Noun.__init__(self, kwargs.get('name') or 'unknown', **kwargs)

        self.type = kwargs.get('type') or 'generic'
        self.identified = kwargs.get('identified') or False
        self.stackable = kwargs.get('stackable') or False
        self.stacksize = kwargs.get('stacksize') or 1
        self.usable = kwargs.get('usable') or False
        self.consumable = kwargs.get('consumable') or False
        self.amount = kwargs.get('amount') or 1

        self.active = True
        self.listeners = {'amount': [], 'attribute': []}

        self.name = self.value
        self.attributes = kwargs.get('attributes') or []

    def as_str(self):
        s = str(self.amount) + ' ' + self.name
        if self.amount > 1:
            s = s + 's'
        return s

    def add_listener(self, change_type, listener):
        if change_type not in self.listeners:
            self.listeners[change_type] = []
            
        self.listeners[change_type].append(listener)
        return self

    def remove_listener(self, change_type, listener):
        if change_type in self.listeners:
            if listener in self.listeners[change_type]:
                self.listeners[change_type].remove(listener)

    def _alert_listeners(self, change_type, event_type):
        if change_type in self.listeners:
            to_remove = []
            for listener in self.listeners[change_type]:
                result = listener(event_type, self)
                if result == 'remove' or result == 'finished':
                    to_remove.append(listener)
            for finished in to_remove:
                self.listeners[change_type].remove(finished)
        

    def decrease_amount(self, amount, callback=None):
        self.amount = max(0, self.amount - amount)
        if self.amount == 0:
            self.active = False
        if callback is not None:
            callback(self)

        self._alert_listeners('amount', 'decrease')
        return self

    def increase_amount(self, amount, callback=None):
        if not self.stackable:
            print 'stacking an unstackable item'
            return self
        
        self.amount = min(self.stacksize, self.amount + amount)
        if callback is not None:
            callback(self)
            
        self._alert_listeners('amount', 'increase')
        return self
        
    def _run_callback_on_attribute(self, attribute, callback=None):
        if callback is not None:
            if isinstance(callback, list):
                for f in callback:
                    f(attribute)
            else:
                callback(attribute)
        return attribute

    def get_attribute(self, value, fun=None):
        for attribute in self.attributes:
            if attribute.value == value:
                return self._run_callback_on_attribute(attribute, fun)

        # always return an attribute that is mutable
        as_needed = Attribute(value=value, amount=0)
        self.attributes.append(as_needed)
        return self._run_callback_on_attribute(as_needed, fun)

    def get_attribute_as_string(self, value, fun=None):
        attr = self.get_attribute(value, fun)
        return self.possessive + ' ' + value + ' is ' + str(attr.amount) + ' of ' + str(attr.max_amount)

    def add_attribute(self, attribute):
        exists = self.get_attribute(attribute.value)
        if exists is not None:
            exists.add(attribute.amount)
        else:
            self.attributes.append(attribute)

    def use(self):
        pass

class Inventory:
    def __init__(self, items=[]):
        self.items = items

    def as_str(self):
        s = 'Inventory: '
        for item in self.items:
            s = s + item.as_str() + ', '
        return s
    
    def get_items(self, relevant=None):
        if relevant is not None:
            to_return = []
            for item in self.items:
                if item.type == relevant.type:
                    if item.name == relevant.name:
                        to_return.append(item)
            return to_return
        else:
            return self.items

    def add_item(self, item):
        if isinstance(item, Thing):
            if not item.stackable and item not in self.items:
                self.items.append(item)
                return self

            relevant_items = self.get_items(item)
            if len(relevant_items) == 0:
                self.items.append(item)
                return self
            
            for relevant_item in relevant_items:
                if item.amount <= 0:
                    item.active = False
                    return self
                if relevant_item.stackable:
                    headroom = relevant_item.stacksize - relevant_item.amount
                    to_add = min(headroom, item.amount)

                    relevant_item.increase_amount(to_add)
                    item.decrease_amount(to_add)
                    
            if item.amount > 0:
                self.items.append(item)
                
        return self

    def has_amount(self, item_name, item_type, amount):
        accum = 0
        for item in self.items:
            if item.type == item_type or item.name == item_name:
                accum = accum + item.amount
                if accum >= amount:
                    return True
        return False
    
    def remove_item(self, item_name, item_type, amount):
        if not self.has_amount(item_name, item_type, amount):
            return False
        
        items_to_remove = []

        amount_removed = 0
        for item in self.items:
            if amount_removed < amount:
                if item.type == item_type and item.name == item_name:
                    amount_to_remove = min(item.amount, amount - amount_removed)
                    item.decrease_amount(amount_to_remove)
                    amount_removed = amount_removed + amount_to_remove
                    if item.amount <= 0:
                        item.active = False
                        items_to_remove.append(item)
        return False
                
    
if __name__ == '__main__':
    strength = Attribute(value='strength', amount=10, max_amount=500)
    print strength.value, strength.amount

    non_weak_person = Person(name='Strong Man', attributes=[strength])
    
    strength.add(100)
    print strength.value, strength.amount
    print non_weak_person.get_attribute_as_string('strength')
    print non_weak_person.get_attribute_as_string('weakness')

    def increase_max_amount(attr):
        attr.max_amount += 5
    non_weak_person.get_attribute('intelligence', increase_max_amount)
    print non_weak_person.get_attribute_as_string('intelligence', lambda i: i.add(5))
    
    apple = Thing(name='Apple', amount=1, stackable=True, stacksize=99)

    def apple_events(event, apple):
        if event == 'increase':
            print 'you found another apple!'
        elif event == 'decrease':
            print 'you lost another apple!'
        
    apple.add_listener('amount', apple_events)
    for x in xrange(5):
        apple.increase_amount(1)

    for x in xrange(60):
        non_weak_person.inventory.add_item(Thing(name='Potion', amount=2, stacksize=33, stackable=True))

    non_weak_person.inventory.add_item(Thing(name='Sword of Mourning', amount = 1, stackable = False))
    non_weak_person.inventory.add_item(Thing(name='Sword of Mourning', amount = 1, stackable = False))
    
    print non_weak_person.inventory.as_str()
