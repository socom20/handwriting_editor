import pygame as pg
import numpy as np
import pygame.math as pm
import sys, os
import json

from modules.drawable import Drawable
    
class Line(Drawable):
    def __init__(self,
                 text='Empty',
                 pos=(100.0, 100.0),
                 txt_size=10,
                 width=3,
                 is_drawing=False,
                 pos_points_list=[],
                 e_points_list=[],
                 parent=None):

        self.text = text
        self.pos              = pm.Vector2(*pos)
        self.txt_size         = txt_size
        self.is_drawing       = is_drawing
        self.pos_points_list  = [pm.Vector2(*v) for v in pos_points_list]
        self.e_points_list    = e_points_list[:]
        self.sel_point_list   = [False for i in e_points_list]
        self.parent           = parent
        self.width            = width
     

        self.points_list          = []
        self.values_v             = []
        self.screen_mouse_point_v = []
        self.color_able           = False
        self.isSelected           = False
        self.is_in_window         = True

        self.value = 1.0

        assert len(pos_points_list) == len(e_points_list), ' Deben ser iguales: len(pos_points_list) == len(e_points_list)'
        return None

    def __repr__(self):
        name = 'AUX_LINE {}'.format(self.text)
        return name

    def update_mouse_pos(self, screen_point):
        if self.is_drawing:
                    
            if len(self.screen_mouse_point_v) > 0:
                self.screen_mouse_point_v[-1] = screen_point
            else:
                self.screen_mouse_point_v.append(screen_point)
        else:
            print('WARNING, Junction, no deberías llamar a este método', file=sys.stderr)
            
        return None

    def update(self):
        """Actualizamos la posición de los puntos para contruir las lineas"""

        # Modificamos la posición de los vectores de la polilinea 
        self.points_list = [v + self.pos for v in self.pos_points_list]

        return None      
        
    def start_drawing(self):
        if not self.is_drawing:
            self.is_drawing = True

        return None
    
    def finish_drawing(self):
        if self.is_drawing:
            self.is_drawing = False
            self.screen_mouse_point_v.clear()

        return None

    def extend_line(self, screen_point, solid=True):
        if self.is_drawing:
            canvas_point = self.parent.coord_screen2coord_canvas(screen_point)

            if len(self.pos_points_list) == 0:
                self.pos = canvas_point

            diff = canvas_point - self.pos
            
            self.pos_points_list.append(diff)

            if solid:
                self.e_points_list.append(0)
            else:
                self.e_points_list.append(1)

            if len(self.sel_point_list) > 0:
                self.sel_point_list[-1] = False
                
            self.sel_point_list.append(True)

        else:
            print('WARNING, Junction, no se puede extender la junction si is_drawing == False', file=sys.stderr)
     
        return None
    
    def short_line(self):
        if self.is_drawing:
            if len(self.pos_points_list) > 1:
                p = self.pos_points_list.pop(-1)
                self.e_points_list.pop(-1)
                self.sel_point_list.pop(-1)

                if len(self.sel_point_list) > 0:
                    self.sel_point_list[-1] = True
                
        else:
            print('WARNING, Junction, no se puede acortar la junction si is_drawing == False', file=sys.stderr)
            
        return None

    

    def draw(self, screen):
        """Dibujamos en pantalla la linea"""
        self.update()

        self.draw_line()
        
        if len(self.points_list) > 1:
            if self.parent.global_zoom_factor > 0.21:
                #dibujamos la descripción del esquema
                self.draw_name()

        return None

    def draw_screen_lines(self):

        to_draw = []

        if len(self.points_list) > 0:
            to_draw.append( self.parent.coord_canvas2coord_screen(self.points_list[-1]) )

        to_draw += self.screen_mouse_point_v

        if len( to_draw ) > 1:
            pg.draw.lines(self.parent.screen, self.parent.EM_obj_line_selected_c, False, to_draw, self.width)

        return None

        
    def draw_line(self):
        """dibujamos la linea de la linea"""

        points_list_screen = [self.parent.coord_canvas2coord_screen(v) for v in self.points_list]

        if self.parent.edit_Mode:
            n_dots = len(points_list_screen)
        else:
            n_dots = min(len(points_list_screen), max(min(1, len(points_list_screen)), int(self.value * len(points_list_screen))))

        for i in range(1, n_dots):
            e   = self.e_points_list[i]
            sel = self.sel_point_list[i]
            
            pos0 = tuple(int(p) for p in points_list_screen[i-1])
            pos1 = tuple(int(p) for p in points_list_screen[i])

            if sel:
                line_width = self.width + 2
                if e == 0:
                    line_color  =  self.parent.color_line_e0_sel
                else:
                    line_color  = self.parent.color_line_e1_sel
            else:
                line_width = self.width
                if e == 0:
                    line_color  =  self.parent.color_line_e0
                else:
                    line_color  = self.parent.color_line_e1
                
            pg.draw.line(self.parent.screen, line_color, pos0, pos1)
            
            
        for i in range(n_dots):
            e   = self.e_points_list[i]
            sel = self.sel_point_list[i]
            
            pos = tuple(int(p) for p in points_list_screen[i])
                
            if sel:
                circle_r = self.width + 4
                if e == 0:
                    dot_color = self.parent.color_dot_e0_sel
                else:
                    dot_color = self.parent.color_dot_e1_sel
            else:
                circle_r = self.width + 2
                if e == 0:
                    dot_color = self.parent.color_dot_e0
                else:
                    dot_color = self.parent.color_dot_e1
                
            pg.draw.circle(self.parent.screen, dot_color, pos, circle_r, circle_r)
            
        self.draw_screen_lines()
        
        return None

    

    def draw_name(self):
        """dibujamos el nombre de la linea"""

        (x_min, x_max), (y_min, y_max) = self.return_box()

        
        name_angle = 0
        name_color = self.parent.color_line_text
        
        name_str   = '{}'.format(self.text)
        offset_v = pm.Vector2()
        offset_v.from_polar( (6, 90) )

        name_pos = pm.Vector2(0.5*(x_min + x_max), y_max) + offset_v
        
        name_size = max(0.8*self.txt_size*self.parent.global_zoom_factor, 0.2 * (y_max-y_min) * self.parent.global_zoom_factor)

        name_surface, name_rect = self.parent.lowercases_font.render(name_str, name_color, size=name_size)
        name_rect.center = self.parent.coord_canvas2coord_screen( name_pos )
        self.parent.screen.blit(name_surface, name_rect)
        return None


    def _collide(self, screen_mouse_pos):
        """Verifica si existe o no colisión entre screen_mouse_pos y el objeto.
           Retorna Verdadero si hay colisión
           Retorna Falso si no existe colisión"""
        
        canvas_mouse_pos =  self.parent.coord_screen2coord_canvas(screen_mouse_pos)
        dmin = 5/self.parent.global_zoom_factor

        p_list = self.points_list

        for i_p in range(len(p_list)):
            r = (canvas_mouse_pos - p_list[i_p]).length()
            if r < dmin:
                return ['dot', i_p]
    
        for i_p in range(len(p_list)-1):
            dA = (canvas_mouse_pos - p_list[i_p]).length()
            dB = (canvas_mouse_pos - p_list[i_p+1]).length()
            dS = (p_list[i_p] - p_list[i_p+1]).length()
            
            touching = dA + dB < dmin + dS
            if touching:
                return ['line', i_p+1]
            
        return None


    def collide(self, screen_mouse_pos):
        if self._collide(screen_mouse_pos) is None:
            return False
        else:
            return True
     

    def rotate(self, pos_ref=None, d_angle=15):
        """ Rota el objeto respecto a pos un ángulo d_angle.
            pos_ref:     Vector2, centro de rotación, si es None, rota respecto a self.pos
            d_angle:     float, ángulo en grados
            return: None"""

        if self.is_drawing:
            print('WARNING, junction: No se puede rotar mientras se esta editando la linea.', file=sys.stderr)
            return None
                  
        angle = d_angle
        
        if pos_ref is not None:
            diff = self.pos - pos_ref
            diff.rotate_ip(d_angle)
            self.pos = pos_ref + diff

        while angle >= 360:
            angle -= 360

        while angle < 0:
            angle += 360
            
        # Modificamos el ángulo de los vectores de la polilinea 
        for v in self.pos_points_list:
            v.rotate_ip(angle)
            
        return None


    def to_json(self):
        """Se exporta a texto un diccionario con todas los argumentos para poder instanciarlo"""
        to_save = {'type':'Line',
                   'init_args_d': {'text': self.text,
                                   'pos':             [float(x) for x in self.pos],
                                   'txt_size':         float(self.txt_size),
                                   'is_drawing':       False,
                                   'width':            self.width,
                                   'pos_points_list': [[float(x) for x in c] for c in self.pos_points_list],
                                   'e_points_list':   [float(x) for x in self.e_points_list]}}

        return json.dumps(to_save)

    def return_box(self):
        x_coords = [p.x for p in self.points_list]
        y_coords = [p.y for p in self.points_list]

        return (min(x_coords), max(x_coords)), (min(y_coords), max(y_coords))



        
    def select(self, screen_mouse_pos=None):
        """Se selecciona el objeto
           Vuelve Verdadero al flag isSelected"""
        sel_all = False
        if screen_mouse_pos is None:
            sel_all = True
        else:
            col = self._collide(screen_mouse_pos)
            if col is not None:
                if col[0] == 'line':
##                    sel_all = True
                    self.sel_point_list[col[1]] = True
                else:
                    self.sel_point_list[col[1]] = True
        if sel_all:
            for i in range(len(self.sel_point_list)):
                self.sel_point_list[i] = True
            
        if any(self.sel_point_list):
            self.isSelected  = True
        else:
            self.isSelected  = False
            
        return self.isSelected


    def deselect(self, screen_mouse_pos=None):
        """Se deselecciona el objeto
           Vuelve Falso al flag isSelected"""

        if screen_mouse_pos is None:
            for i in range(len(self.sel_point_list)):
                self.sel_point_list[i] = False
                
        if any(self.sel_point_list):
            self.isSelected  = True
        else:
            self.isSelected  = False
            
        return not self.isSelected


    def drag(self, d_pos=pm.Vector2(0.0,0.0)):
        """ Mueve self.pos en la dirección de d_pos.
            d_pos:     Vector2, unidades de canvas.
            return: None"""

        for i in range(len(self.sel_point_list)):
            if self.sel_point_list[i]:
                self.pos_points_list[i] += d_pos

        if len(self.pos_points_list) > 0 and self.pos_points_list[0].x != 0 and self.pos_points_list[0].y != 0:
            self.pos += d_pos
            for i_p in range(len(self.pos_points_list)):
                self.pos_points_list[i_p] -= d_pos
            
        return None

    def change_e(self):
        for i_p in range(len(self.sel_point_list)):
            if self.sel_point_list[i_p]:
                self.e_points_list[i_p] = not self.e_points_list[i_p]

        return None


    def del_points(self):
        for i_p in range(len(self.sel_point_list)-1, -1, -1):
            if self.sel_point_list[i_p]:
                self.pos_points_list.pop(i_p)
                self.e_points_list.pop(i_p)
                self.sel_point_list.pop(i_p)

        if len(self.pos_points_list) > 0 and self.pos_points_list[0].x != 0 and self.pos_points_list[0].y != 0:
            d_pos = self.pos_points_list[0]
            self.pos += d_pos
            for i_p in range(len(self.pos_points_list)):
                self.pos_points_list[i_p] -= d_pos

        return None


    def cut_at_point(self):
        if sum(1 if i else 0 for i in self.sel_point_list) != 1:
            print(' - WARNING, cut_at_point: Solo se puede cortar si hay un solo punto seleccionado.', file=sys.stderr)
            return None

        if len(self.sel_point_list) > 0 and (self.sel_point_list[0] or self.sel_point_list[-1]):
            print(' - WARNING, cut_at_point: No se puede cortar si se seleccionan los puntos de los extremos.', file=sys.stderr)
            return None

            
        for i_p in range(len(self.sel_point_list)):
            if self.sel_point_list[i_p]:
                
                pos_new = self.pos_points_list[i_p] + self.pos
                pos_points_list_new = [self.pos_points_list[i] - self.pos_points_list[i_p] for i in range(i_p, len(self.pos_points_list))]
                e_points_list_new   = [self.e_points_list[i] for i in range(i_p, len(self.e_points_list))]
                                       
                new_line = Line(text=self.text,
                                pos=pos_new,
                                txt_size=self.txt_size,
                                width=self.width,
                                is_drawing=False,
                                pos_points_list=pos_points_list_new,
                                e_points_list=e_points_list_new,
                                parent=self.parent)


                self.pos_points_list = self.pos_points_list[:i_p]
                self.e_points_list   = self.e_points_list[:i_p]
                self.sel_point_list  = self.sel_point_list[:i_p]

                return new_line

        return None


    def merge_line(self, line):
        d_pos = line.pos - self.pos
        pos_points_list_new = [p + d_pos for p in line.pos_points_list]
        self.pos_points_list += pos_points_list_new
        
        line.e_points_list[0] = 1
        self.e_points_list   += line.e_points_list
        
        self.sel_point_list  += line.sel_point_list
        self.text += ' ' + line.text
        
        return None


    def add_mid_point(self):
        if len(self.sel_point_list) > 0 and self.sel_point_list[0]:
            self.sel_point_list[0] = False

        to_ret = None
        for i_p in range(len(self.sel_point_list)-1,-1,-1):
            if self.sel_point_list[i_p]:
                pos_new = 0.5 * (self.pos_points_list[i_p] + self.pos_points_list[i_p-1])
                
                self.pos_points_list = self.pos_points_list[:i_p] + [pos_new] + self.pos_points_list[i_p:]
                self.e_points_list   = self.e_points_list[:i_p] + [0] + self.e_points_list[i_p:]
                self.sel_point_list  = self.sel_point_list[:i_p] + [True] + self.sel_point_list[i_p:]

                to_ret = True
                
        return to_ret
        
    def select_all_points(self):
        for i_p in range(len(self.sel_point_list)):
            self.sel_point_list[i_p] = True
        return None
        
    def get_width(self):
        return self.width

    def edit_text(self):
        print('\n\n')
        print(' - Editando Texto!!!')
        print(' Texto anterior: {}'.format(self.text))
        text = input('Entre el texto de la linea (Presione ENTER al finalizar):\n >>> ')
        self.set_text(text)
        print('OK!"')
        return None
    
    def set_text(self, text):
        """Modificamos el nombre descriptivo"""
        self.text  = str(text)
        return None

    def get_text(self):
        """Retorna el nombre descriptivo"""
        return self.text


    def set_pos(self, pos):
        """Se modifica la posición de la linea"""
        self.pos = pm.Vector2(*pos)
        return None

    def get_pos(self):
        """Retorna la posición actual de la linea"""
        return self.pos


    def get_angle(self):
        """Retorna el angulo actual de la linea"""
        return self.angle

    def retrieve_corners(self):
        """Retorna la lista de puntos que conforman la linea"""
        return self.points_list


    def set_value(self, value=1.0):
        self.value = max(0.0, min(1.0, float(value)))
        return None
    
