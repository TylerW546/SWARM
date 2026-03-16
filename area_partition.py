import RPi.GPIO as GPIO
import time
import math


class SearchArea: #Search areas defined by coordinates
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    @property
    def width(self):
        return self.x_max - self.x_min

    @property
    def height(self):
        return self.y_max - self.y_min


def partition_space_recursive(rovers, area): #partition based on 3 rovers in list and the search area
    if len(rovers) == 1:
        rovers[0].assigned_area = area
        return
    split_vertically = (area.width > area.height)
    if split_vertically:
        mid = area.x_min + area.width / 2
        area_a = SearchArea(area.x_min, area.y_min, mid, area.y_max)
        area_b = SearchArea(mid, area.y_min, area.x_max, area.y_max)
    else:
        mid = area.y_min + area.height / 2
        area_a = SearchArea(area.x_min, area.y_min, area.x_max, mid)
        area_b = SearchArea(area.x_min, mid, area.x_max, area.y_max)
    
    rovers[0].assigned_area = area_a
    partition_space_recursive(rovers[1:], area_b)
