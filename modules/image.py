import pygame as pg
import numpy as np
import pygame.math as pm
import sys, os
import json
import cv2
import skimage.morphology
import skimage.filters


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

        self.run_helper       = False
        self.blit_helper      = False


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


    def proc_array_helper(self, array_helper):
        array_proc = array_helper.mean(axis=-1).astype(np.uint8)

        img_th = skimage.filters.threshold_yen(array_proc, nbins=256)
        array_proc = (array_proc < img_th ).astype(np.uint8)
        array_proc = skimage.morphology.erosion(array_proc, skimage.morphology.square(4))

##        array_proc = skimage.morphology.medial_axis(array_proc,
##                                                    mask=None,
##                                                    return_distance=False)


        array_proc = np.repeat(255*array_proc[...,np.newaxis], 3, axis=-1).astype(np.uint8)
        
        return array_proc

    def activate_mouse_helper(self, do_blit=True):
        self.run_helper       = True
        self.blit_helper      = do_blit

        return None

    def deactivate_mouse_helper(self):
        self.run_helper       = False
        self.blit_helper      = False

        return None
    
    def draw_win_helper(self, array_cuted, blit_pos, win_size=(100,100)):

        
        H2_win, W2_win = win_size[0]//2, win_size[1]//2
        
        W_m, H_m = self.parent.screen_mouse_pos

        H_m_a, W_m_a = int(H_m - blit_pos[1]), int(W_m - blit_pos[0])

        W_a, H_a = array_cuted.shape[:2]


        if H2_win <= H_m_a <= H_a-H2_win and W2_win <= W_m_a <= W_a-W2_win:
            W_s, H_s = self.parent.screen.get_size()

##            # Blit button right
##            blit_pos_helper = pm.Vector2(W_s-win_size[1], H_s-win_size[0])

            # Mouse Pos
            blit_pos_helper = pm.Vector2(W_m+W2_win, H_m+H2_win)
##            blit_pos_helper = pm.Vector2(W_m-W2_win, H_m-H2_win)
            
            t_h = H_m_a - H2_win
            b_h = H_m_a + H2_win

            l_h = W_m_a - W2_win
            r_h = W_m_a + W2_win
            
            array_helper = array_cuted[l_h:r_h, t_h:b_h]
            array_proc = self.proc_array_helper(array_helper)

            if self.blit_helper:
                img_helper = pg.surfarray.make_surface(array_proc)
                self.parent.screen.blit(img_helper, blit_pos_helper)

        return None


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
            array_cuted = self.array_to_plot[l_i:r_i, t_i:b_i]
            img_cuted = pg.surfarray.make_surface(array_cuted)

            blit_pos += pm.Vector2(l_i, t_i)
            self.parent.screen.blit(img_cuted, blit_pos)
            
            if self.run_helper:
                self.draw_win_helper(array_cuted, blit_pos)

                
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
