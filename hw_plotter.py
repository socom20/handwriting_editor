import cv2
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

from modules.screentext import ScreenText
from modules.thorpymenu import ThorpyMenu
from modules.line import Line
from modules.image import Image


class Plotter:

    def __init__(self, screen_size=(1440,810)):

        self.screen_size          = screen_size # tamaño de la pantalla
    
        self.monitor_size         = None
        self.global_pos           = pm.Vector2(0, -self.screen_size[1]) # coord canvas    
        self.global_zoom_factor   = 1.0 # coord screen
        self.global_zoomf_min     = 0.2
        self.global_zoomf_max     = 5
        self.screen_mouse_pos     = pm.Vector2(0,0) # coord screen
        self.screen_mouse_dx      = 0
        self.screen_mouse_dy      = 0
        
        self.canvas_mouse_pos     = self.coord_screen2coord_canvas(self.screen_mouse_pos) # coord canvas



        self.obj_list_v           = [] # lista de objetos a dibujar 
        self.edit_obj_list_v      = [] # lista de objetos a editar



        self.screen_text_v        = [] # lista de texto a mostrar en Modo Usuario
        self.debug_text_v         = [] # lista de texto a mostrar en Modo Debugging
        self.edit_text_v          = [] # lista de texto a mostrar en Modo Edición



        self.debugging_Mode       = False  # Modo para encontrar errores: inicia en Falso
        self.edit_Mode            = False  # Modo para editar objetos: Inicia en Falso
        self.is_running           = True   # Inicia con el programa corriendo
        self.fullScreen           = False  # Modo pantalla completa: Inicia desactivado


        self.click_on_edit_obj    = False
        self.onSelectionChanged   = False
        self.onEditionChanged     = True
        self.onUndoChanged        = False
        self.drawing_junction     = False
        self.pos_is_dragging      = False
        self.using_aux_axes       = False
        self.last_click           = None

        self.file_name = 'salvado.ptr'

        
        self.palette_color_d = {  'black' :  {'color_1': ( 14, 17, 17),
                                              'color_2': ( 35, 43, 43),
                                              'color_3': ( 53, 56, 57),
                                              'color_4': (101,115,126),
                                              'color_5': (192,197,206),
                                              'color_6': (243,207,122),
                                              'color_7': (172, 63, 33),
                                              
                                              'red':     (255,  0,  0),
                                              'green':   (  0,255,  0),
                                              'blue':    (  0,  0,255),

                                              'red_sel':     (128,  0,  0),
                                              'green_sel':   (  0,128,  0),
                                              'blue_sel':    (  0,  0,128)}

                                  }



        self.color_palette_v   = sorted(list(self.palette_color_d.keys()))
        self.color_palette_idx = 0
        self.color_palette     = self.color_palette_v[self.color_palette_idx]  # seleccionamos la paleta de colores a utilizar para la visualización del programa (opciones: black, white, neon)
        self.set_color_palette(color_palette=self.color_palette)
        self.global_bg_color   = self.UM_bg_c                                  # color de background



        
        self.debug_txt = ScreenText(rel_pos=(0,0), abs_off=(50,50), text='Debug Text', parent=self)               
        self.debug_text_v.append( self.debug_txt )

        self.edit_txt = ScreenText(rel_pos=(1,0), abs_off=(-200,25), text='Edit Mode', parent=self)
        self.edit_text_v.append( self.edit_txt )

        self.screen = self.init_display(display_size=self.screen_size, fullScreen=self.fullScreen)


        self.myfont = pg.freetype.Font("./fonts/BebasNeue-Regular.ttf", 24) # fuente elegida para el texto
        self.lowercases_font = pg.freetype.Font("./fonts/Helvetica.ttf", 10) # fuente elegida para el texto



        self.slider = ThorpyMenu(rel_pos=(0,1), abs_off=(0,-30), rank=(0,1.0), name='TextProp', parent=self)
        
        self.screen_text_v.append(self.slider)


        self.undo_pointer = -1
        self.undo_v       = []

        
        return None


    def update_txt_pos(self, size=(0,0)):
        """Actualizo la posición del texto que se muestra en pantalla en funcion del tamaño de la ventana"""
        self.edit_text_v[0].update_pos(size)
        
        for txt in self.screen_text_v:
            txt.update_pos(size)
        return None
    

    def set_color_palette(self, color_palette='black'):

        print(color_palette)

        self.UM_bg_c                = self.palette_color_d[color_palette]['color_1'] # color de background en Modo Usuario
        self.EM_bg_c                = self.palette_color_d[color_palette]['color_3'] # color de background en Modo Edición
        self.screen_txt_c           = self.palette_color_d[color_palette]['color_6'] # color usado para el texto de la información mostrada por pantalla
        
        self.EM_obj_body_selected_c = self.palette_color_d[color_palette]['color_4'] # color de cuerpo del objeto node en Modo Edición cuando esta seleccionado
        self.EM_obj_line_selected_c = self.palette_color_d[color_palette]['color_7'] # color de linea del objeto Node en Modo Edición cuando esta seleccionado
        self.EM_aux_axes_c          = self.palette_color_d[color_palette]['color_4'] # color de linea los ejes auxiliares en Modo Edición



        self.color_line_text       = self.palette_color_d[color_palette]['red']
        
        self.color_dot_e0          = self.palette_color_d[color_palette]['green']
        self.color_dot_e1          = self.palette_color_d[color_palette]['blue']
        
        self.color_line_e0         = self.palette_color_d[color_palette]['green']
        self.color_line_e1         = self.palette_color_d[color_palette]['blue']
        
        self.color_dot_e0_sel      = self.palette_color_d[color_palette]['green_sel']
        self.color_dot_e1_sel      = self.palette_color_d[color_palette]['blue_sel']
        
        self.color_line_e0_sel     = self.palette_color_d[color_palette]['green_sel']
        self.color_line_e1_sel     = self.palette_color_d[color_palette]['blue_sel']


        
        self.set_bg_color()
  
        return None

    def delete_obj(self):
        """se elimina el objeto seleccionado"""
        if len(self.edit_obj_list_v) > 0:
            self.edit_obj_list_v.clear()
            self.onEditionChanged = True
            
        return None

    def clear(self):
        """Se eliminan todos los objetos existentes"""
        if len(self.edit_obj_list_v)>0 or len(self.obj_list_v)>0:
            self.edit_obj_list_v.clear()
            self.obj_list_v.clear()
            self.onEditionChanged = True
        return None

    
    def set_bg_color(self):
        """Establezco el color de fondo de pantalla"""
        if self.edit_Mode:
            self.global_bg_color = self.EM_bg_c
        else:
            self.global_bg_color = self.UM_bg_c 
        return None
    

    def coord_screen2coord_canvas(self, screen_pos = (0,0)):
        """Transformo una posición de coordenadas SCREEN en una posicion de coordenadas CANVAS"""
        screen_pos = pm.Vector2(screen_pos[0], -screen_pos[1])
        canvas_pos = (screen_pos - self.global_pos)/self.global_zoom_factor
        return canvas_pos

    def coord_canvas2coord_screen(self, canvas_pos = (0,0)):
        """Transformo una posición de coordenadas CANVAS en una posicion de coordenadas SCREEN"""
        canvas_pos = pm.Vector2(canvas_pos)
        screen_pos = canvas_pos * self.global_zoom_factor + self.global_pos

        screen_pos = pm.Vector2(int(round(screen_pos.x)), -int(round(screen_pos.y)))
        return screen_pos


    def init_display(self, display_size=(0,0), screen_name="Plotter", fullScreen = False):
        """ Inicializa pygame y crea un onjeto screen.
            display_size: tamaño de la ventana de pygame.
            screen_name: Nombre que aparecerá en la ventana abierta
            fullScreen: Modo pantalla completa. Inicia en Falso
            return: screen"""

        pg.init()
        display_info = pg.display.Info()
        window_size  = (display_info.current_w, display_info.current_h)
        
        if self.monitor_size is None:
            self.monitor_size = window_size
            
        self.clock = pg.time.Clock()
        
        if fullScreen:
            screen = pg.display.set_mode(self.monitor_size, pg.HWSURFACE | pg.FULLSCREEN)
            self.update_txt_pos(size=self.monitor_size)
        else:
            screen = pg.display.set_mode(display_size, pygame.locals.HWSURFACE | pygame.locals.DOUBLEBUF | pygame.locals.RESIZABLE)
            self.update_txt_pos(size=display_size)
            
        pg.display.set_caption(screen_name)

        return screen

    
    def quit(self):
        """Se cierra Pygame"""
        self.is_running = False
        return None

    def _onEditionChanged(self):
        self.undo_update()            
        self.onEditionChanged = False
        return None

    def get_editor_state(self):
        
        set_plotter = json.dumps({'type':'Plotter',
                                  'set_args_d': {'global_zoom_factor':  float(self.global_zoom_factor),
                                                 'global_pos':         [float(x) for x in self.global_pos]
                                                 }
                                  } )
        state_v = [set_plotter]
        
        for o in self.obj_list_v+self.edit_obj_list_v:
            state_v.append( o.to_json() )
            
        return state_v

    def set_editor_state(self, state_v=[], del_current_state=True):
        if self.drawing_junction:
            # finalizamos el dibujo de la Junction
            self.end_edit_junction()
                
        if del_current_state:
            # borramos todos los objetos
            self.clear()

        for s_str in state_v:
            init_d = json.loads(s_str)
            obj_class = eval(init_d['type'])
            if obj_class == Plotter:
                for attr_name in init_d['set_args_d'].keys():
                    meth = 'set_' + attr_name
                    value = init_d['set_args_d'][attr_name]
                    try:
                        self.__getattribute__(meth)(value)
                    except Exception as e:
                        print('WARNING, Plotter: Error al setear el metodo {} del objeto {}. Error: {}. Saltando setear'.format( meth, self, e), file=sys.stderr)
                        continue
            else:
                self.obj_list_v.append( obj_class(**init_d['init_args_d'], parent=self) )
                
        self.onEditionChanged = True
            
        return None

    def rotate(self, d_angle=5, clockwise=True):
        """Rotación de los objetos seleccionados segun self.rotation_angle
           d_angle: salto angular de rotación
           clockwise = True:  horario
           clockwise = False: anti-horario """

        to_rotate_v = self.edit_obj_list_v + self.obj_list_v
        if len(to_rotate_v) == 0:
            return None
        
        pos_ref = to_rotate_v[0].get_pos()
        
        if not clockwise:
            d_angle = -d_angle
    
        for o in to_rotate_v:
            o.rotate(pos_ref=pos_ref, d_angle=d_angle)
            
        self.onEditionChanged = True
        return None

    
    def undo_update(self):
        if self.onUndoChanged:
            self.onUndoChanged = False
            return None

        state_v = self.get_editor_state()
        for s_str in state_v:
            init_d = json.loads(s_str)
            obj_class = eval(init_d['type'])
            if obj_class == Plotter:
                state_v.remove(s_str)
                break

        if len(self.undo_v) != 0 and len(self.undo_v)-1 != self.undo_pointer:
            self.undo_v = self.undo_v[:self.undo_pointer+1]

        self.undo_v.append(state_v)
        self.undo_pointer = len(self.undo_v)-1

        return None


    def undo(self):
        """Deshace la ultima edición realizada sobre los objetos"""
        if self.drawing_junction:
            print('WARNING, undo, No es posible desahcer acciones mientras se edita una junction', file=sys.stderr)
            return None
        
        if self.undo_pointer > 0:
            self.undo_pointer -= 1
            self.set_editor_state(self.undo_v[self.undo_pointer])

            self.onUndoChanged = True
        return None
    
    def redo(self):
        """Rehace la ultima edición realizada sobre los objetos"""
        if self.drawing_junction:
            print('WARNING, redo, No es posible resahcer acciones mientras se edita una junction', file=sys.stderr)
            return None

        if self.undo_pointer < len(self.undo_v)-1:
            self.undo_pointer += 1
            self.set_editor_state(self.undo_v[self.undo_pointer])

            self.onUndoChanged = True
            
        return None
    

    def fullScreen_Mode(self):
        """Si "fullScreen is True" activa el modo pantalla completa"""
        self.screen = self.init_display(fullScreen=self.fullScreen)
        return None

    
    def zoom_in(self):
        """Acerco la vista en la pantalla"""
        if self.global_zoom_factor <= self.global_zoomf_max:
            self.global_zoom_factor = self.global_zoom_factor*1.25
            self.global_pos += pm.Vector2(self.global_pos.x-self.screen_mouse_pos[0], self.global_pos.y+self.screen_mouse_pos[1])*(1.25-1)
        return None

    def zoom_out(self):
        """Alejo la vista en la pantalla"""
        if self.global_zoom_factor >= self.global_zoomf_min:
            self.global_zoom_factor = self.global_zoom_factor*0.8
            self.global_pos += pm.Vector2(self.global_pos.x-self.screen_mouse_pos[0], self.global_pos.y+self.screen_mouse_pos[1])*(0.8-1)
        return None

    def _onSelectionChanged(self):
        self.onSelectionChanged = False
        return None

    
    def update_display(self):
        """ Actualiza los objetos que se dibujan en Screen.   
            return: None"""

        self.clock_tick  = self.clock.tick(60)

        if self.onSelectionChanged:
            self._onSelectionChanged()

        if self.onEditionChanged:
            self._onEditionChanged()
        
        
        self.screen.fill(self.global_bg_color)

        for obj in self.obj_list_v:
            if obj.is_in_windows:
                obj.draw(self.screen)

        for obj in self.edit_obj_list_v:
            if obj.is_in_windows:
                obj.draw(self.screen)

        if not self.edit_Mode:   
            for txt in self.screen_text_v:
                txt.draw(self.screen)

        elif self.edit_Mode:
            for e_txt in self.edit_text_v:
                e_txt.draw(self.screen)

        if self.debugging_Mode:
            for d_txt in self.debug_text_v:
                d_txt.draw(self.screen)

            
        pg.display.flip()


        return None

    def switch_mode(self):
        """Cambio el modo (user/edit)"""
        self.edit_Mode = not(self.edit_Mode)
        self.set_bg_color()
        
        if self.edit_Mode:
            print('EDIT_MODE_ON')

        else:
            print('EDIT_MODE_OFF')
            self.last_time_um = pg.time.get_ticks()
            self.deselect_all()
            self.using_aux_axes = False

        if self.slider is not None:
            self.slider.set_visible(not self.edit_Mode)
            
        return None

    def drag_view(self):
        """Desplazo la vista en la pantalla"""
        self.global_pos += pm.Vector2(self.screen_mouse_dx, -self.screen_mouse_dy)
        return None

    def del_points(self):
        for o in self.edit_obj_list_v:
            o.del_points()

        self.onEditionChanged = True
        return None
                

    def drag_pos(self):
        """Desplazo la posición de los objetos seleccionados"""
        self.pos_is_dragging = True
   
        if self.click_on_edit_obj:
            d_pos = pm.Vector2(self.screen_mouse_dx, -self.screen_mouse_dy) / self.global_zoom_factor
                
            for o in self.edit_obj_list_v:
                o.drag(d_pos)

        return None

    def edit_text(self):
        print('Editando:')
        print( self.edit_obj_list_v, type(self.edit_obj_list_v[0]), type(self.edit_obj_list_v[0]) is Line)
        if len(self.edit_obj_list_v) == 1 and type(self.edit_obj_list_v[0]) is Line:
            self.edit_obj_list_v[0].edit_text()
            self.onEditionChanged = True
            
        return None

    def change_e(self):
        for o in self.edit_obj_list_v:
            o.change_e()
            self.onEditionChanged = True

        return None

    def cut_at_point(self):
        for o in self.edit_obj_list_v:
            new_o = o.cut_at_point()
            if new_o is not None:
                self.obj_list_v.append(new_o)
                self.onEditionChanged = True

        return None

    def merge_lines(self):
        if len(self.edit_obj_list_v) == 2 and type(self.edit_obj_list_v[0]) is Line and type(self.edit_obj_list_v[1] is Line):
            self.edit_obj_list_v[0].merge_line(self.edit_obj_list_v[1])
            self.edit_obj_list_v.remove(self.edit_obj_list_v[1])

        else:
            print(' Solo se pude juntar las lineas cuando con dos objetos Line seleccionados.', file=sys.stderr)

        return None


    def add_mid_point(self):
        for o in self.edit_obj_list_v:
            if o.add_mid_point() is not None:
                self.onEditionChanged = True

        return None


    def set_line_prop(self, text_prop):
        
        for o in self.obj_list_v + self.edit_obj_list_v:
            if type(o) is Line:
                o.set_value(text_prop)
                self.onEditionChanged = True
                
        return None


    def select_all_points(self):
        for o in self.edit_obj_list_v:
            o.select_all_points()

        return None
        
    
    
    def main_loop(self):
        """Loop principal"""
        while self.is_running:

            self.event_handler()

            if self.debugging_Mode:
                pass
                self.debug_txt.print('DEBUGGING MODE {}'.format('ON' if self.debugging_Mode else 'OFF'),
                                     'EDIT MODE {}'.format('ON' if self.edit_Mode else 'OFF'),
                                     '{} : {}'.format('Time', pg.time.get_ticks()),
                                     '{} : {:0.2f}'.format('Fps', self.clock.get_fps()),
                                     '{} : {:0.2f}'.format('Tick', self.clock_tick),                                     
                                     '{} : {:.2f}'.format('Zoom factor',self.global_zoom_factor),
                                     '{} : {:d}'.format('obj count', len(self.edit_obj_list_v)+len(self.obj_list_v)),
                                     '{} : {}'.format('Canvas Pos', self.canvas_mouse_pos)
                                     )

                                                           
            self.canvas_mouse_pos = self.coord_screen2coord_canvas(self.screen_mouse_pos)
            self.update_display()
        
        pg.quit()
        pg.display.quit()

        return None

    def update_mouse_pos(self, pos):
        """Actualizo la posición del mouse en la pantalla"""
        self.screen_mouse_dx = pos[0] - self.screen_mouse_pos[0]
        self.screen_mouse_dy = pos[1] - self.screen_mouse_pos[1]
        self.screen_mouse_pos = pos
        return None


    def collide(self, collision_pos=(0,0)):
        """Comparo la colision entre los objetos y el punto collision_pos"""
        coll_v = self.edit_obj_list_v[::-1] + self.obj_list_v[::-1]
        for o in coll_v:
            if o.collide(collision_pos):
                return o
        return None

    def select_by_click(self, click_pos=(0,0), add=False):
        """Selecciono el objeto si click_pos es un punto dentro del mismo
           add = False: selecciono de a un objeto a la vez
           add = True: acumulo los objetos seleccionados"""
        
        to_select_obj_v=[]
        
        for o in (self.obj_list_v + self.edit_obj_list_v):
            if o.collide(click_pos):
                to_select_obj_v.append( o )
                break
            
        self.select(to_select_obj_v, add, click_pos)

        return None

    def select(self, to_select_obj_v=[], add=False, screen_mouse_pos=None):
        """se seleccionan los objetos de la lista to_select_obj_v"""

        if add:
            to_select_obj_v += self.edit_obj_list_v
        else:
            self.deselect_all()

        if len(to_select_obj_v) > 0:
            for obj in to_select_obj_v:
                if not obj.is_Selected():
                    self.obj_list_v.remove( obj )
                    self.edit_obj_list_v.append( obj )
                    self.onSelectionChanged = True

                obj.select(screen_mouse_pos)
                
        return None


    def deselect(self, click_pos=(0,0)):
        """Deselecciono el objeto si click_pos es un punto dentro del mismo"""
        for i_o, o in enumerate(self.edit_obj_list_v):
            if o.collide(click_pos):
                if o.deselect(click_pos) :
                    self.obj_list_v.append( self.edit_obj_list_v.pop(i_o) )
                    
                self.onSelectionChanged = True
                break
        return None

    
    def deselect_all(self):
        """Deselecciono todos los objetos seleccionados a la vez"""
                            
        if len(self.edit_obj_list_v) > 0:
            
            if self.drawing_junction:
                # finalizamos el dibujo de la Junction
                self.end_edit_junction()
                
            while len(self.edit_obj_list_v) > 0:
                o = self.edit_obj_list_v.pop(0)
                self.obj_list_v.append( o )
                assert o.deselect(), 'ERROR, el objeto {} no se desseleccinó.'
                
            self.onSelectionChanged = True
        return None


    def new_image(self, screen_pos=(0,0), image_path='./CartaA.png'):
        """Genero un nuevo objeto Image"""

        self.file_name = os.path.splitext(image_path)[0] + '.ptr'
        
        pos = self.coord_screen2coord_canvas(screen_pos = screen_pos)
        new_obj = Image(pos=pos,
                        filename=image_path,
                        parent=self)
        self.obj_list_v.append(new_obj)
        self.onEditionChanged = True
        
        return None


    def new_junction(self):
        """Genero un nuevo objeto Line"""
        
        new_obj = Line(is_drawing=True, parent=self)
        print('creando Line', new_obj)
        
        self.obj_list_v.append(new_obj)
        self.onEditionChanged = True
        self.select([new_obj])
        return new_obj

    def extend_junction(self, point):
        j = self.edit_obj_list_v[0]
        j.extend_line(point)
        return None

    def update_mouse_pos_junction(self, point):
        j = self.edit_obj_list_v[0]
        j.update_mouse_pos(point)
        return None
        
    def end_edit_junction(self):
        j = self.edit_obj_list_v[0]
        j.finish_drawing()

        if len(j.points_list) < 2:
            self.edit_obj_list_v.pop(0)
            print('No se ha creado ninguna Junction')
        else:
            print('Junction finalizada', j)
            
        self.drawing_junction = False
        self.onEditionChanged = True
        self.using_aux_axes   = False
        return None
    
    def short_junction(self):
        j = self.edit_obj_list_v[0]
        j.short_line()
        return None

    def start_edit_junction(self):
        if not self.drawing_junction:
            if len(self.edit_obj_list_v) > 1 or (len(self.edit_obj_list_v) == 1 and type(self.edit_obj_list_v[0]) is not Line ):
                self.deselect_all()

            if len(self.edit_obj_list_v) == 1:
                if type(self.edit_obj_list_v[0]) is Line:
                    j = self.edit_obj_list_v[0]
                    self.drawing_junction = True
                    j.start_drawing()
        
            elif len(self.edit_obj_list_v) == 0:
                self.drawing_junction = True
                j = self.new_junction()
                
        return None


    def get_global_pos(self):
        return self.global_pos

    def set_global_pos(self, global_pos):
        self.global_pos = pm.Vector2(global_pos)
        return None

    def get_global_zoom_factor(self):
        return self.global_zoom_factor
    
    def set_global_zoom_factor(self, global_zoom_factor):
        self.global_zoom_factor = global_zoom_factor
        return None
    
    def event_handler(self):
        """Lista de comandos para manejar los eventos desde teclado y mouse"""
        keys_pressed_v = pg.key.get_pressed()
        events_v       = pg.event.get()

        pressed_ctrl  = (keys_pressed_v[pg.K_LCTRL] or keys_pressed_v[pg.K_RCTRL])
        pressed_shift = (keys_pressed_v[pg.K_LSHIFT] or keys_pressed_v[pg.K_RSHIFT])
        for event in events_v:
            self.slider.react(event)

            if event.type == pg.USEREVENT and event.id == 5:
##                print('slider move!!!', self.slider.get_slider_value(), event)
                self.set_line_prop( self.slider.get_slider_value() )


            if event.type == pg.QUIT:
                self.quit()
                break
                
            elif event.type == pg.VIDEORESIZE and not self.fullScreen:
               screen_size = event.dict['size']
               self.screen = self.init_display(display_size = screen_size)

               
               
            # SUELTO UN BOTON DEL MOUSE
            elif event.type == pg.MOUSEBUTTONUP:
                if self.slider is not None:
                    self.slider.on_manipulation = False
                    
                self.click_on_edit_obj = False
                
                if self.pos_is_dragging:
                    self.onEditionChanged = True
                    self.pos_is_dragging = False

                
            # PRESIONO UN BOTON DEL MOUSE
            elif event.type == pg.MOUSEBUTTONDOWN:
                if self.slider is not None:
                    self.slider.on_manipulation = True
                    
                if self.collide(event.pos) in self.edit_obj_list_v:
                    self.click_on_edit_obj = True
                    
                if self.edit_Mode:
                    if event.button == 1: # boton izquierdo del mouse

                        if self.drawing_junction:
                            self.extend_junction(event.pos)

                        
                        # se selecciona el objeto clickeado
                        elif pressed_ctrl:
                            self.select_by_click(event.pos, add=True)
                            
                        else:
                            self.select_by_click(event.pos, add=False)
                            
                                            
                    elif event.button == 3: # boton derecho del mouse

                        # se acorta la junction en edición
                        if self.drawing_junction:
                            self.short_junction()
                            
                        # se deselecciona el objeto clickeado
                        else:
                            self.deselect(event.pos)
                       
                if event.button == 4: # ruedita del mouse hacia arriba
                    # zoom in
                    self.zoom_in()

                elif event.button == 5: # ruedita del mouse hacia abajo
                    # zoom out
                    self.zoom_out()

            # MUEVO EL MOUSE
            if event.type == pg.MOUSEMOTION:
                self.update_mouse_pos(event.pos)

                if self.drawing_junction:
                    self.update_mouse_pos_junction(event.pos)
                
                mouseState = pg.mouse.get_pressed()
                if mouseState[1]:  # Ruedita apretada
                    # arrastro lo que se muestra por pantalla
                    self.drag_view()

                elif mouseState[0] and self.edit_Mode and not self.drawing_junction: # Edit_Mode + boton izquierdo del mouse
                    # arrastro la posición del objeto seleccionado.
##                    if keys_pressed_v[pg.K_m] or keys_pressed_v[pg.K_c]:
                    self.drag_pos()
                        


            # PRESIONO UNA TECLA
            elif event.type ==  pg.KEYDOWN:
                
                # guardo en un archivo de texto            
                if event.key == pg.K_s and pressed_ctrl:
                    self.save()
                            
                # activo o desactivo el modo edit
                if (event.key == pg.K_F1):
                    self.switch_mode()


                # activo o desactivo el modo debugging    
                if (event.key == pg.K_F2):    
                    self.debugging_Mode = not(self.debugging_Mode)
                    if self.debugging_Mode:
                        print('DEBUGGING_MODE_ON')
                    else:
                        print('DEBUGGING_MODE_OFF')
                        
                # FullScreen
                if (event.key == pg.K_F11):
                    self.fullScreen = not(self.fullScreen)
                    self.fullScreen_Mode()

                # cambio la paleta de colores
                if (event.key == pg.K_F12):
                    self.color_palette_idx = (self.color_palette_idx + 1)%len(self.color_palette_v)
                    self.color_palette     = self.color_palette_v[self.color_palette_idx]
                    self.set_color_palette(color_palette=self.color_palette)


            
                # --------------------------------------- MODO EDICIÓN ----------------------------------------
                if self.edit_Mode:

                    # rotación de los objetos seleccionados (anti-horario)
                    if (event.key == pg.K_r):
                        self.rotate(clockwise= not pressed_shift)

                    elif (event.key == pg.K_e):
                        self.change_e()

                    elif (event.key == pg.K_c):
                        self.cut_at_point()
                        
                    elif (event.key == pg.K_a):
                        self.add_mid_point()


                    elif (event.key == pg.K_s) and not pressed_ctrl:
                        self.select_all_points()

                    elif (event.key == pg.K_m):
                        self.merge_lines()
                        
                    elif (event.key == pg.K_i):
                        print('New Image')
                        self.new_image()

                    elif (event.key == pg.K_l) and not pressed_ctrl:
                        print('New Line')
                        self.start_edit_junction()


                    elif pressed_ctrl:

                        # dibujo objetos desde un arqchivo de texto       
                        if event.key == pg.K_l:
                            self.load()

                        # deshacer/rehacer
                        if (event.key == pg.K_z):
                            if keys_pressed_v[pg.K_LSHIFT]:
                                self.redo()
                            else:
                                self.undo()
             
                    # elimino los objetos seleccionados        
                    elif event.key == pg.K_DELETE:
                        self.delete_obj()

                    # elimino un punto de la linea
                    elif event.key == pg.K_d:
                        self.del_points()

                    # Edito el texto de la linea
                    elif event.key == pg.K_t:
                        self.edit_text()
    
                    # Deselecciono todos los objetos que estaban seleccionados    
                    elif event.key == pg.K_ESCAPE:
                        self.deselect_all()


                    elif self.drawing_junction or self.pos_is_dragging:                            
                        if (event.key == pg.K_SPACE) or (event.key == pg.K_RETURN):
                            # finalizamos el dibujo de la Junction
                            self.deselect_all()
                            
                            

                # --------------------------------------------- MODO USUARIO ---------------------------------------------                                
                elif not self.edit_Mode:
                    pass

                            
                # ---------------------------------------------------------------------------------------------------- 
            
                
        return None


    def save(self):
        print(' Salvando en archivo {0}'.format(self.file_name))
        with open(self.file_name, 'w') as f:
            f.write( '\n'.join(self.get_editor_state()) )
                
        return None
    

    def load(self, del_current_state=True):
        """Cargamos un archivo de salvado."""

        if not os.path.exists(self.file_name):
            print(' ERROR, No se encontró el archivo: "{}", no se podrá cargarlo.'.format(self.file_name), file=sys.stderr)
            return None
        
        print(' Cargando !!!!')
        with open(self.file_name, 'r') as f:
            ml_v = f.readlines()

        state_v = []
        for i_l, s_str in enumerate(ml_v):
            try:
                i_comment = s_str.find('#')
                if i_comment != -1:
                    s_str = s_str[:i_comment].strip()

                s_str = s_str.replace('\n', '')
                if len(s_str) > 0:
                    json.loads(s_str)
                    state_v.append( s_str )
            except Exception as e:
                print(' - WARNING, linea número:{} no interpretada en el archivo de salvado: "{}".\n - El error: {}'.format(i_l, s_str, str(e)), file=sys.stderr)
                continue
        
        self.set_editor_state(state_v, del_current_state)
        # Reseteamos el deshacer
        self.undo_pointer = -1
        self.undo_v       = []
        self.onEditionChanged = True
        return None
    
if __name__ =='__main__':

    ptr = Plotter()
    ptr.switch_mode()
    ptr.new_image(image_path='./samples/CartaA.png')
    ptr.main_loop()

    

    print('Programa Finalizado !!!')
