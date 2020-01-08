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


        self.last_angle = None
        self.last_zoom = None
        self.last_mode = None
            
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
        self.filename = input(' - Entre la dirección de la imagen a utilizar: ')
        return None
    
    def __repr__(self):
        name = 'IMAGE {}'.format(self.filename)
        return name

    def rotate_bound(self, image, angle=0.0, zoom=1.0, borderValue=(0,0,0)):

        # grab the dimensions of the image and then determine the
        # center
        (h, w) = image.shape[:2]
        (cX, cY) = (w // 2, h // 2)
     
        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        M = cv2.getRotationMatrix2D((cX, cY), -angle, zoom)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
     
        # compute the new bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))
     
        # adjust the rotation matrix to take into account translation
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY
     
        # perform the actual rotation and return the image
        return cv2.warpAffine(image, M, (nW, nH), borderValue=borderValue)


    def draw_image(self):
        """ Plotea la imagene en el objeto screen."""

##        self.angle += 1.0

##        self.pos += pm.Vector2(1.0,0.0)
        
        zoom = self.scale*self.parent.global_zoom_factor
        
##        new_size_v = tuple(int(zoom * s) for s in self.original_size_v)

        if self.last_zoom != zoom or self.angle != self.last_angle or self.parent.edit_Mode != self.last_mode:

            if self.parent.edit_Mode:
                borderValue = self.parent.EM_bg_c
            else:
                borderValue = self.parent.UM_bg_c

            
            # Image Rotation + scale
##            image_center = (0.0,0.0)
##            rot_mat = cv2.getRotationMatrix2D(image_center, self.angle, zoom)
##            self.img_to_plot = cv2.warpAffine(self.img_array, rot_mat, new_size_v, flags=cv2.INTER_CUBIC)

            self.array_to_plot = self.rotate_bound(self.img_array, angle=self.angle, zoom=zoom, borderValue=borderValue)
            self.array_to_plot = np.transpose(self.array_to_plot, [1,0,2])

            self.d_screen_pos = pm.Vector2( self.array_to_plot.shape[0]//2, self.array_to_plot.shape[1]//2)

            self.last_zoom  = zoom
            self.last_angle = self.angle
            self.last_mode = self.parent.edit_Mode


        
        blit_pos = self.parent.coord_canvas2coord_screen(self.pos)  - self.d_screen_pos



        W, H, C = self.array_to_plot.shape
        t = int(blit_pos[1])
##        b = t + H
        l = int(blit_pos[0])
##        r = l + W


        W_s, H_s = self.parent.screen.get_size()
        
        t_s = -t
        b_s = t_s + H_s
        l_s = -l
        r_s = l_s + W_s

        t_i = min(max(0, t_s), H)
        b_i = max(min(H, b_s), 0)

        l_i = min(max(0, l_s), W)
        r_i = max(min(W, r_s), 0)

##        print('S:',t_s, b_s, l_s, r_s)
##        print('I:',t_i, b_i, l_i, r_i, 'SS:', (W_s, H_s))


        if l_i != r_i and t_i != b_i:
            img_cuted = self.array_to_plot[l_i:r_i, t_i:b_i]
            img_cuted = pg.surfarray.make_surface(img_cuted)

            blit_pos += pm.Vector2(l_i, t_i)
            self.parent.screen.blit(img_cuted, blit_pos)

##        self.img_to_plot = pg.surfarray.make_surface(self.array_to_plot)
##        self.parent.screen.blit(self.img_to_plot, blit_pos)
        
        return None

    def collide(self, screen_mouse_pos):
        return False
    
    def draw(self, screen):
        """Dibujamos en pantalla la imagen"""

        self.draw_image()
        
        return None


    def rotate(self, pos_ref=None, d_angle=15):
        """ Rota el objeto respecto a pos un ángulo d_angle.
            pos_ref:     Vector2, centro de rotación, si es None, rota respecto a self.pos
            d_angle:     float, ángulo en grados
            return: None"""

        self.angle -= d_angle
        
        if pos_ref is not None:
            diff = self.pos - pos_ref

            
            diff.rotate_ip(d_angle)
            self.pos = pos_ref + diff

        while self.angle >= 360:
            self.angle -= 360

        while self.angle < 0:
            self.angle += 360
            
            
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
