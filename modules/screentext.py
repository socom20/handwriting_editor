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

class ScreenText:
    """Esta clase controla el texto que será mostrado por pantalla"""
    def __init__(self,
                 rel_pos=(0,0),
                 abs_off=(100,-50),
                 scale=1.0,
                 color=(243,207,122),
                 text='colocar texto aqui',
                 f_updater=(lambda self: None),
                 parent=None):
        
        self.rel_pos   = pm.Vector2(rel_pos)
        self.abs_off   = pm.Vector2(abs_off)
        
        self.scale     = scale
        self.f_updater = f_updater
        self.text      = text
        self.parent    = parent
        self.color     = color

        self.update_pos( self.parent.screen_size )

        return None

    def update(self):
        self.f_updater(self)
        return None
    

    def print(self,  *args_v, sep='\n'):
        self.text = sep.join([a if type(a) is str else repr(a) for a in args_v])
        return None
    
        
    def draw(self, screen):
        self.update()  
        for i, text in enumerate(self.text.split('\n')):
            self.color = self.parent.screen_txt_c
            text_surface, rect = self.parent.myfont.render(text, self.color)
            self.parent.screen.blit(text_surface, self.pos+pm.Vector2(0, 20*i))

            
        return None

    def update_pos(self, screen_size):
        self.pos = pm.Vector2(screen_size[0] * self.rel_pos[0] + self.abs_off[0],
                              screen_size[1] * self.rel_pos[1] + self.abs_off[1])
        return None



        


