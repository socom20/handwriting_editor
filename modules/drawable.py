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
import inspect

from matplotlib import pyplot as plt


class Drawable():
    def __init__(self):
        self.pos = pm.Vector2(100.0,100.0)
        return None

    def whoami(self):
        return inspect.stack()[1][3]

    def __str__(self):
        return self.__repr__()

    def edit_text(self):
        return None
    
    def is_color_able(self):
        """Retorna si el objeto es coloreable o no"""
        return self.color_able

    def draw(self, screen):
        """Dibujamos en pantalla el objeto dibujable"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return None
    
    def collide(self, screen_mouse_pos):
        """Verifica si existe o no colisión entre mouse y el objeto
           Retorna Verdadero si hay colisión
           Retorna Falso si no existe colisión"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return None

    def del_points(self):
        return None
    
    def select(self, screen_mouse_pos=None):
        """Se selecciona el objeto
           Vuelve Verdadero al flag isSelected"""
        self.isSelected  = True
        return self.isSelected

    def change_e(self):
        return None

    def cut_at_point(self):
        return None

    def add_mid_point(self):
        return None

    def select_all_points(self):
        return None
    
    def deselect(self, screen_mouse_pos=None):
        """Se deselecciona el objeto
           Vuelve Falso al flag isSelected"""
        self.isSelected  = False
        return not self.isSelected

    def is_Selected(self):
        return self.isSelected
    
    def aline(self, grid_size=10):
        """Se modifica la posición del objeto al punto mas cercano de una grilla cuadrada de ancho = grid_size"""
        self.pos = pm.Vector2(grid_size*round(self.pos.x/grid_size),
                              grid_size*round(self.pos.y/grid_size))
        return None

    def drag(self, d_pos=pm.Vector2(0.0,0.0)):
        """ Mueve self.pos en la dirección de d_pos.
            d_pos:     Vector2, unidades de canvas.
            return: None"""
        
        self.pos += d_pos
        return None
   
    def rotate(self, pos_ref=None, d_angle=15):
        """Rota el objeto un d_angle grados con respecto a pos_ref.
           Si pos_ref is None, rota con respecto a si mismo"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return None

    def rescale(self, pos_ref=None, scale_factor=1.0):
        """Modifica las dimensiones del objeto segun una posición de referencia y un factor de escala"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return None

    def copy(self):
        """Genera una copia del objeto. La copia se posiciona a (150,150) respecto de la posición del objeto origen"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return None

    def to_json(self):
        """Se exporta a texto un diccionario con todos los argumentos para poder instanciarlo"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return None

    def set_color(self, color=[(100,125,121)]):
        """Se modifica el color del objeto"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return None

    def get_color(self):
        """Retorna el color actual del objeto"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return None

    def set_pos(self, pos):
        """Se modifica la posición del objeto"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return None

    def get_pos(self):
        """Retorna la posición actual del pipe"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return self.pos

    def set_angle(self, angle):
        """Se modifica el ángulo de inclinación del objeto"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return None

    def get_angle(self):
        """Retorna el angulo actual del objeto"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return None

    def set_description_name(self, description_name):
        """Modificamos el nombre descriptivo"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return None

    def get_description_name(self):
        """Retorna el nombre descriptivo"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        return None


    def retrieve_corners(self):
        """Retorna los puntos de las esquinas del rectangulo que contiene al objeto"""
        print("WARNING, Drawable, Método {} no implementado".format(self.whoami()), file=sys.stderr)
        corner_list_v = [pm.Vector2(0.0,0.0) for i in range(4)]
        return corner_list_v

    def is_in_window(self):
        return True

    def update_is_in_window(self, win_canvas_v, win_screen_v):
        return None

    
    def collide_rect(self, rect_point_v, surface_point_list):
        """Verifica si existe colision o no entre rect_point_v y el objeto"""
        
        obj_corners_v = self.retrieve_corners()

        if self.__class__.__name__ is "Line":
            # si el rectángulo esta dentro del objeto
            if all(self.collide2(p) for p in surface_point_list):
                return True
        else:
            if all(self.collide(p) for p in surface_point_list):
                return True

        # si la posicion del objeto está adentro del rectángulo 
        if len(obj_corners_v) > 0:
            obj_pos = obj_corners_v[0]
            
            x_min = min(rect_point_v[0].x, rect_point_v[2].x)
            x_max = max(rect_point_v[0].x, rect_point_v[2].x)

            y_min = min(rect_point_v[0].y, rect_point_v[2].y)
            y_max = max(rect_point_v[0].y, rect_point_v[2].y)
            
            if (x_min <= obj_pos.x < x_max) and (y_min <= obj_pos.y < y_max):
                return True

        # si alguno de los segmentos del objeto intersecta a algun lado del rectángulo
        idx_start = -1 if self.__class__.__name__ is not "Junction" else 0
        for i_p in range(-1, len(rect_point_v)-1):
            p_0  = rect_point_v[i_p]
            p_1  = rect_point_v[i_p+1]
            p0p1 = p_1 - p_0
            for i_r in range(idx_start, len(obj_corners_v)-1):
                r_0  = obj_corners_v[i_r]
                r_1  = obj_corners_v[i_r+1]
                r0r1 = r_1 - r_0
                p0r0 = r_0 - p_0
                
                det_a = -p0p1.x*r0r1.y + r0r1.x*p0p1.y
                
                if det_a == 0:
                    continue                

                s = (-r0r1.y*p0r0.x + r0r1.x*p0r0.y)/det_a
                t = (-p0p1.y*p0r0.x + p0p1.x*p0r0.y)/det_a

                if (0 <= s <= 1) and (0 <= t <= 1):
                    return True

        return False
    
