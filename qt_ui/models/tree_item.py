from abc import abstractmethod


# base class for tree models
class TreeItem:
    def __init__(self, parent=None):
        self.parent = parent
        self.children = []

    def appendChild(self, item: 'TreeItem'):
        self.children.append(item)

    def child(self, row: int) -> 'TreeItem':
        try:
            return self.children[row]
        except IndexError:
            return None

    @abstractmethod
    def data(self, column: int):
        pass

    def childCount(self):
        return len(self.children)

    @abstractmethod
    def columnCount(self):
        return 3 # TODO?

    def row(self):
        if self.parent:
            self.parent.children.index(self)
        return 0

    def parentItem(self):
        return self.parent

    def removeChild(self, row: int):
        del self.children[row]
