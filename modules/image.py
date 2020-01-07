import pygame as pg
import numpy as np
import pygame.math as pm
import sys, os
import json
import cv2


from modules.drawable import Drawable



class Image(Drawable):

    def __init__(self,
                 pos=(0.0, 0.0),
                 angle=0.0,
                 filename='./CartaA.png',
                 scale=1.0,
                 parent=None):

        self.pos              = pm.Vector2(*pos)
        self.angle            = angle
        self.filename         = filename
        self.scale            = scale
        self.parent           = parent

        self.size_v = None

        
            
        while self.filename is None or self._load_image() == False:
            self._ask_image_path()
            
        return None

    def _load_image(self):
        try:
            self.img_array = cv2.imread(self.filename)[:, :, ::-1]
            self.original_size_v = self.img_array.shape[1::-1]
            
##            self.pg_img = pg.image.load(self.filename)
##            self.original_size_v = self.pg_img.get_size()
            return True
        
        except:
            print(' - WARNING, Image, no se pudo abrir la imagen:', self.filename, file=sys.stderr)
            return False

        
    def _ask_image_path(self):
        self.filename = input(' - Entre la dirección de la imagen a utilizar:')
        return None
    
    def __repr__(self):
        name = 'IMAGE {}'.format(self.filename)
        return name

    
    def draw_image(self):
        """ Plotea la imagene en el objeto screen."""

        zoom = self.scale*self.parent.global_zoom_factor
        
        new_size_v = tuple(int(zoom * s) for s in self.original_size_v)

        if self.size_v != new_size_v:
##            self.img_to_plot = pg.transform.scale(self.pg_img, new_size_v)
            self.img_to_plot = cv2.resize(self.img_array, new_size_v, interpolation=cv2.INTER_CUBIC)

            self.img_to_plot = np.transpose(self.img_to_plot, [1,0,2])
            self.img_to_plot = pg.surfarray.make_surface(self.img_to_plot)
            
            self.size_v = new_size_v
            
        self.parent.screen.blit(self.img_to_plot,
                                self.parent.coord_canvas2coord_screen(self.pos))

        return None

    
    def draw(self, screen):
        """Dibujamos en pantalla la imagen"""

        self.draw_image()
        
        return None


    def to_json(self):
        """Se exporta a texto un diccionario con todas los argumentos para poder instanciarlo"""
        
        to_save = {'type':'Image',
                   'init_args_d': {'pos':             [float(x) for x in self.pos],
                                   'angle':            float(self.angle),
                                   'filename':         str(self.filename),
                                   'scale':            float(self.scale),
                                   } }

        return json.dumps(to_save)
    
if __name__ == '__main__':
    img = Image()
