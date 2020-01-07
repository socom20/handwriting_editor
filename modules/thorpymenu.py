import pygame as pg
import pygame.locals

import thorpy

import numpy as np
import pygame.math as pm
import pygame.freetype
import sys, os
import json
import pickle
import hashlib as sh
import threading
import time

from matplotlib import pyplot as plt


class ThorpyMenu:
    def __init__(self, rel_pos=(1, 0), abs_off=(0, 0), rank=(0,2000), name='SimTime', parent=None):

        self.rel_pos = pm.Vector2(rel_pos)
        self.rel_pos_visible   = self.rel_pos
        self.rel_pos_invisible = pm.Vector2(1,1)
        
        self.abs_off = pm.Vector2(abs_off)
        self.parent  = parent
        self.rank    = rank
        self.name    = name
        
        self.slider          = None
        self.visible         = True
        self.on_manipulation = False
        
        self.update_pos( pm.Vector2(self.parent.screen_size) )
        
        return None

    def react(self, event):
        self.menu.react(event)
        return None

    def create_menu(self, screen_size):
##        print(screen_size, screen_size[0] - 2*self.abs_off[0])
        # Colocamos el Slider
        self.slider = thorpy.SliderX.make(screen_size[0] - 2*self.abs_off[0] - 130, self.rank, self.name)
##        self.button = thorpy.make_button("Quit", func=thorpy.functions.quit_func)

        self.box    = thorpy.Box.make(elements=[self.slider])
        self.menu   = thorpy.Menu(self.box)

        for element in self.menu.get_population():
            element.surface = self.parent.screen

        self.set_slider_value(100.0)
        return None

    def set_slider_rank(self, rank=(0.0, 2000.0)):
        self.rank = rank
        self.update_pos( pm.Vector2(self.parent.screen.get_size()) )
        return None
        
        
    def get_slider_value(self, value=0.0):
        if self.slider is not None:
            v = self.slider.get_value()
        else:
            v = 0.0

        return v

    def set_slider_value(self, value=0.0):
        self.slider.set_value(value)
        return None

    def update_pos(self, screen_size):
        v = self.get_slider_value()
        self.create_menu(screen_size)
        self.set_slider_value(v)
        
        self.pos = pm.Vector2(screen_size[0] * self.rel_pos[0] + self.abs_off[0],
                              screen_size[1] * self.rel_pos[1] + self.abs_off[1])
        
        self.box.set_topleft( self.pos )
        return None

    def set_visible(self, is_visible=True):
        self.visible = is_visible
        if self.visible:
            self.rel_pos = self.rel_pos_visible
        else:
            self.rel_pos = self.rel_pos_invisible

        self.update_pos(self.parent.screen.get_size())
        return None

    def get_visible(self, is_visible=True):
        return self.visible
    

    def draw(self, screen):
        if self.visible:
            self.box.blit()
            self.box.update()
        return None    
