import sys
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
    return os.path.join(base_path, relative_path)


phase_diagram_bg = resource_path("resources/phase diagram bg.svg")
favicon = resource_path("resources/favicon.png")