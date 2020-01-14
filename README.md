# Handwriting Editor

El objetivo del **Plotter** es poder transcribir la escritura de las cartas en vectores de puntos para utilizarlo de *DataSet* para entrenar la red neuronal.

Los vectores de puntos los denominamos **Trazos.**
Cata trazo está formado por diferentes puntos conectados por **Segmentos**. Además cada **Trazo** tiene asociado una cadena de caracteres que representa el **Texto** escrito en la Carta.

Los segmentos de los trazos pueden ser verder, para indicar que el lapiz se encuentra escribiendo, o azul para indicar se que mueve el lapiz sin escribir. Es importante utilizar sólo un segmento Azul entre varios verdes.

Por lo generar un trazo debe agrupar no más de 5 palabras de las cartas.


# Instalando dependencias:

El editor está programado en Python3. Necesita las siguientes dependencias:
```
pip3 install opencv-contrib-python
pip3 install scikit-image
pip3 install pygame
pip3 install thorpy
pip3 install tkinter

pip3 install numpy
pip3 install scipy
pip3 install matplotlib
```

# Lanzar el editor

Desde la consola ejecutar por ejemplo:
```
python3 hw_plotter.py ./samples/CartaA.png
```

O simplemente:
```
python3 hw_plotter.py
```
Así se muestra un cuadro de diálogo para elegir el archivo de imagen con el que se desea trabajar.

# Manual de usuario del editor HW_Plotter

## Editar de trazos

Para crear un nuevo Trazo:
1) Presionar una vez la tecla L, luego con el mouse:
2) Botón Izquierdo para colocar un punto.
3) Botón Derecho para eliminarlo
4) Tecla escape para finalizar el Trazo.

Para continuar un Trazo:
1) Seleccionar un punto del Trazo que se desea continuar con el botón izquierdo de mouse.
2) Presionar la tecla L
3) Seguir editando.

Para crear un nuevo Trazo Continuo:
1) Botón Izquierdo para colocar el primer punto.
2) mover el mouse con el Botón Izquierdo presionado para dibujar el trazo.

Cambiar el espaciado de los punto en el trazo continuo
1) Precionar la Tecla + del numpad para aumentar el espaciado de los puntos
2) Precionar la Tecla - del numpad para dismunuir el espaciado de los puntos
Nota: Se puede ver el espaciado que se está utilizando en el modo Debug

Para borrar un punto de un Trazo:
1) Seleccionar el punto con botón izquierdo
2) Presionar la Tecla D

Para agregar un punto en una Línea del Trazo:
1) Seleccionar el punto con botón izquierdo
2) Presionar la Tecla A

Para partir un Trazo en 2 Trazos
1) Seleccionar el punto con botón izquierdo
2) Presionar la Tecla C

Para Borrar un Trazo completo:
1) Seleccionar el punto con botón izquierdo
2) Presionar la Tecla Supr

Para seleccionar más de un punto en un Trazo:
1) Mantener presionada la Tecla Ctrl
2) Ir Seleccionando los puntos con el Botón Izquierdo del Mouse

Para seleccionar todos los puntos de un Trazo:
1) Seleccionar cualquier punto del Trazo con el botón izquierdo del mouse 
2) Presionar la Tecla S

Para unir 2 Trazos en un solo:
1) Mantener presionada la tecla Ctrl
2) Seleccionar un punto del primer Trazo que se quiera unir con el botón izquierdo de mouse
3) Seleccionar un punto del segundo Trazo que se quiera unir con el botón izquierdo de mouse.
4) Presionar la tecla M

Para hacer azul un segmento del Trazo:
1) Seleccionar el segmento del Trazo con el botón izquierdo del mouse
2) Presionar la Tecla E

Para Modificar el Texto de un Trazo:
1) Seleccionar cualquier punto del Trazo con el botón izquierdo del mouse
2) Presionar la tecla T
3) Entrar el texto por consola y presionar ENTER para finalizar.

## Selección

Para DesSeleccionar todo:
1) Presionar la Tecla Esc

Para Seleccionar todos los puntos de un trazo:
1) Seleccionar cualquier punto del Trazo con el botón izquierdo del mouse
2) Presionar la Tecla S

## Rotación

Para rotar Trazos + Carta en sentido antihorario:
1) Mantener presionada la tecla Ctrl
2) Presionar la tecla R
3) Para realizar una rotación de 90º, mantener presionada la Tecla Alt también, de lo contrario se usa una rotación fina de 1º.

Para rotar un trazo en sentido horario:
1) Mantener presionada la tecla Ctrl
2) Mantener presionada la tecla Shift
3) Presionar la Tecla R
4) Para realizar una rotación de 90º, mantener presionada la Tecla Alt también, de lo contrario se usa una rotación fina de 1º.

## Control de Cambios
Para DesHacer los últimos cambios:
1) Mantener presionada la tecla Ctrl
2) Presionar la Tecla Z la cantidad de veces que se requiera.

Para ReHacer los últimos cambios:
1) Mantener presionada la tecla Ctrl
2) Mantener presionada la tecla Shift
3) Presionar la Tecla Z la cantidad de veces que se requiera.


## Salvado y Cargado

El archivo de salvado, tiene el mismo nombre que la imagen pero con la extensión ***.ptr**

Para guardar los cambios:
1) Mantener presionada la tecla Ctrl
2) Presionar la Tecla S

Para Cargar lo guardado:
1) Mantener presionada la tecla Ctrl
2) Presionar la Tecla L

Nota: El editor pregutna antes de cerrarlo si es que se quiere guardar cambios no salvados.

## Modo User

En modo User aparece una barra en la parte inferior de la pantalla para controlar el estado de completitud de un Trazo.

Para cambiar entre modos Edit y User
1) Presionar la Tecla F1

## Facilidades del Editor
Para pasar a modo FullScreen o volver del modo FullScreen
1) Presionar la Tecla F11

Para Activar/Desactivar la herrmienta Helper del mouse
1) Precionar la Tecla H


## Control de Excepciones

Si es que hay un fallo en la ejecución del editor, éste intentará recuperarse del fallo.
Antes de tratar de recuperarse, se intenta guardar una archivo de recuperación **nombre_imagen.ptr.rec**.
Se podría relanzar el editor modificando el nombre del archivo **nombre_imagen.ptr.rec** a **nombre_imagen.ptr**.
Se recomienda no perder el último salvado sin error antes de modificar el nombre del archivo de recuperación.






