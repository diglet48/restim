from PySide6.QtCore import *
from qt_ui import settings


class AdditionalSearchPathsModel(QStringListModel):
    def __init__(self, strings, parent=None):
        self.checkedStates = []
        # If any of the path strings ends with a wildcard, remove it
        # and set the checkbox state accordingly
        for i in range(len(strings)):
            if strings[i][-2:] == '/*':
                self.checkedStates.insert(i,Qt.Checked)
                strings[i]=strings[i][0:-2]
            else:
                self.checkedStates.insert(i,Qt.Unchecked)
        super(AdditionalSearchPathsModel, self).__init__(strings, parent)

    # drag-move in listview only, not drag-copy
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEditable | Qt.ItemIsUserCheckable
        return super(AdditionalSearchPathsModel, self).flags(index)

    def data(self, index: QModelIndex, role):
        if role == Qt.CheckStateRole:
            return self.checkedStates[index.row()]
        return super(AdditionalSearchPathsModel, self).data(index, role)

    def setData(self, index: QModelIndex, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole:
            self.checkedStates[index.row()]=Qt.CheckState(value)
            self.dataChanged.emit(index,index)
            return True
        return super(AdditionalSearchPathsModel, self).setData(index, value, role)

    # Do not implement removeRow() - base implementation actually calls removeRows() with count=1

    def removeRows(self, row, count, parent: QModelIndex=QModelIndex()):
        for i in range(count):
            self.checkedStates.pop(row)
        return super(AdditionalSearchPathsModel, self).removeRows(row,count,parent)

    # The same is NOT the case for insertRow() / moveRow()

    def insertRow(self, row, parent: QModelIndex=QModelIndex()):
        self.checkedStates.insert(row,Qt.Unchecked)
        return super(AdditionalSearchPathsModel, self).insertRow(row,parent)

    def insertRows(self, row, count, parent: QModelIndex=QModelIndex()):
        for i in range(count):
            self.checkedStates.insert(row,Qt.Unchecked)
        return super(AdditionalSearchPathsModel, self).insertRows(row,count,parent)

    def moveRow(self, sourceParent: QModelIndex, sourceRow, destinationParent: QModelIndex, destinationChild):
        if destinationChild > sourceRow:
            dest = destinationChild-1
        else:
            dest = destinationChild
        val = self.checkedStates.pop(sourceRow)
        self.checkedStates.insert(dest,val)
        return super(AdditionalSearchPathsModel, self).moveRow(sourceParent, sourceRow, destinationParent, destinationChild)

    def moveRows(self, sourceParent: QModelIndex, sourceRow, count, destinationParent: QModelIndex, destinationChild):
        if destinationChild > sourceRow:
            for i in range(count):
                val = self.checkedStates.pop(sourceRow)
                self.checkedStates.insert(destinationChild-1, val)
        else:
            for i in range(count):
                val = self.checkedStates.pop(sourceRow+i)
                self.checkedStates.insert(destinationChild+i, val)
        return super(AdditionalSearchPathsModel, self).moveRows(sourceParent, sourceRow, count, destinationParent, destinationChild)

    @staticmethod
    def load_from_settings():
        paths = settings.additional_search_paths.get()
        return AdditionalSearchPathsModel(paths)

    def save_to_settings(self):
        pathlist = []
        # Make sure every entry with a checked box gets an asterisk to
        # mark it for recursive searching
        for i in range(self.rowCount()):
            index = self.index(i,0)
            string = self.data(index, Qt.DisplayRole)
            if Qt.CheckState(self.data(index, Qt.CheckStateRole)) == Qt.Checked:
                string += "/*"
            pathlist.append(string)
        settings.additional_search_paths.set(pathlist)
