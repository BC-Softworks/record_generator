from random import randint, seed

class Node:  
    def __init__(self, height = 0, elem = None):
        self.elem = elem
        self.next = [None]*height

class SkipList:
    """ 
    Implementation of a skiplist 
    less_than is a function used for ordering the list
    returns true if the first parameter is less than the second.
    """
    def __init__(self, less_than):
        self.head = Node()
        self.len = 0
        self.maxHeight = 0
        self.less_than = less_than

    def __len__(self):
        return self.len

    def find(self, elem, update = None):
        if update == None:
            update = self.updateList(elem)
        if len(update) > 0:
            item = update[0].next[0]
            if item != None and item.elem == elem:
                return item
        return None
    
    def contains(self, elem, update = None):
        return self.find(elem, update) != None

    def randomHeight(self):
        return randint(1, 2)

    def updateList(self, elem):
        """ Inserts the list in order described by self.less_than"""
        update = [None]*self.maxHeight
        x = self.head
        for i in reversed(range(self.maxHeight)):
            while x.next[i] != None and self.less_than(x.next[i].elem, elem):
                x = x.next[i]
            update[i] = x
        return update
        
    def insert(self, elem):

        _node = Node(self.randomHeight(), elem)

        self.maxHeight = max(self.maxHeight, len(_node.next))
        while len(self.head.next) < len(_node.next):
            self.head.next.append(None)

        update = self.updateList(elem)            
        if self.find(elem, update) == None:
            for i in range(len(_node.next)):
                _node.next[i] = update[i].next[i]
                update[i].next[i] = _node
            self.len += 1

    def remove(self, elem):

        update = self.updateList(elem)
        x = self.find(elem, update)
        if x != None:
            for i in reversed(range(len(x.next))):
                update[i].next[i] = x.next[i]
                if self.head.next[i] == None:
                    self.maxHeight -= 1
            self.len -= 1            
                
    def to_generator(self):
        for i in range(len(self.head.next)-1, -1, -1):
            x = self.head
            while x != None and x.next[i] != None:
                yield x.next[i].elem
                x = x.next[i]
    
    def to_list(self):
        return list(self.to_generator())
