# -*- coding: utf-8 -*-

# Importamos las librerias que nos servirán para trabajar con ventanas
from tkinter import ttk
from tkinter import *
# Importamos el modulo para hacer la conexión con la db
import sqlite3


class Product():

	# Asiganamos a esta variable el nombre de nuestra db
	db_name = 'productos.db'

	def __init__(self, windows):
		# Iniciamos nuestro programa de escritorio
		self.wind = windows
		self.wind.title('Mojarras Familia Martínez')
		# para que el programa se abra con cierto tamaño
		self.wind.geometry("405x425")

		# Cramos un Frame que sirve para crear un cuadrado de objetos
		frame = LabelFrame(self.wind, text='Registra un nuevo producto')
		# De esta manera centramos todo el cuadrado.
		frame.grid(row=0, column=0, columnspan= 6, pady = 20)

		# Creamos un input, para recibir data del usuario
		Label(frame, text='Nombre: ').grid(row=1, column= 0)
		# De esta manera mostramos un recuadro para insertar datos
		self.name = Entry(frame)
		# Sirve para que el cursos este dentro de este recuadro
		self.name.focus()
		self.name.grid(row= 1, column = 1)

		# Creamos input para el precio
		Label(frame, text='Precio: ').grid(row= 2, column=0)
		self.price = Entry(frame)
		self.price.grid(row = 2, column = 1)

		# Creamos un boton para enviar los datos
		ttk.Button(frame, text='Guardar platillo', command= self.add_product).grid(row=3, columnspan= 2, sticky= W + E)

		# Creamos un mensaje en caso de ejecutarse correctamente
		self.message = Label(text = '', fg= 'red')
		self.message.grid(row = 3, column=0, columnspan=2, sticky= W + E)


		# Creamos una tabla para después mostrar el contenido de nuestra db
		# es el espacio donde se mostraran los productos
		self.table = ttk.Treeview(height= 10 , columns= 2)
		self.table.grid(row=4, column= 0, columnspan= 2)

		# Creamos botones para eliminar, borrar y actualizar
		ttk.Button(text='Eliminar', command=self.delete_product).grid(row=5, column=0, sticky= W+E)
		ttk.Button(text='Actualizar', command=self.edit_product).grid(row=5, column=1, sticky= W+E)
		ttk.Button(text='Cerrar', command=self.end_program).grid(row=6, column=0, columnspan=2,sticky= W+E)

		# Creamos los encabezados, estos estaran dentro de la tabla donde se mostraran los datos
		self.table.heading('#0', text= 'Platillo', anchor= CENTER)
		self.table.heading('#1', text= 'Precio', anchor=CENTER)

		# Llenamos la tabla con los datos de la db
		self.get_products()


	# Función encargada de crear la conexion con la base de datos
	def run_query(self, query, parameters = ()):
		# Establecemos conexion con la db
		with sqlite3.connect(self.db_name) as conn:
			cursor = conn.cursor() # abrimos la conexion
			result = cursor.execute(query, parameters) # parametros de la consulta
			conn.commit() # confirmamos la ejecucion del query
		return result

	# Función para obtener los productos de nuestra base de datos
	def get_products(self):
		# Eliminar información de la base de datos para no tener datos repetidos
		records = self.table.get_children()
		for element in records:
			self.table.delete(element)

		# Mostramos los datos de nuestra db en nuestra tabla
		query = 'SELECT * FROM platillos ORDER BY nombre DESC'
		db_rows = self.run_query(query)

		#obteniendo datos de la tabla
		for row in db_rows:
			# De esta manera cada registro dentro de la db quedara en la tabla
			self.table.insert('', 0, text= row[1], values= row[2])

	# Funcion para validar si los cuadros donde ingresa el usuario sus datos estan vacios o llenos
	def validate(self):
		# Si ambos cuadros de texto tienen info, se ejecuta.
		return len(self.name.get()) != 0 and len(self.price.get()) != 0

	# Función para añadir un producto a nuestra base de datos
	def add_product(self):
		# si no esta vacio ningun cuadro se ejecuta este código
		if self.validate():
			query = 'INSERT INTO platillos VALUES(NULL, ?, ?)'
			# con .get() solo obtenemos exactamente lo que el usuario ingreso
			parameters = (self.name.get(), self.price.get())
			# Enviamos los parametros que guardará la db
			self.run_query(query, parameters)

			# Mostramos mensaje de exito, enviamos el mensaje como parametro del atributo text
			self.message['text'] = 'El producto {} se agrego correctamente'.format(self.name.get())
			# Limpiamos los input, de esta manera al precionar guardar, se limpian los cuadros de texto
			self.name.delete(0, END)
			self.price.delete(0, END)
		else:
			self.message['text'] = 'El nombre y precio son requeridos'
		# Una vez se guardo o no, se refresca la tabla con los datos de nuestra db
		self.get_products()

	# Función que elimina un producto selecionado
	def delete_product(self):
		# Vaciamos nuestro mensaje en caso de contenga algo dentro
		self.message['text'] = ''
		try:
			# De esta manera solo obtenemos el nombre del producto que se encuentra en el indice 0 de un diccionario
			self.table.item(self.table.selection())['text'][0]
			#print(self.table.item(self.table.selection()))
		except IndexError as e:
			self.message['text'] = 'Selecciona un producto'
			return
		self.message['text'] = ''
		# Ahora obtenemos el nombre del producto y lo guardamos en variable
		name = self.table.item(self.table.selection())['text']
		# En la variable query, gurdamos la consulta que ejecutaremos en la db
		query = 'DELETE FROM platillos WHERE nombre = ?'
		# Enviamos los parametros que espera la Función run_query
		# colocamos (name, ) porque es una tupla de un solo valor, si no dara mensaje
		self.run_query(query, (name, ))
		self.message['text'] = '{} se ha eliminado correctamente'.format(name)
		self.get_products()

	# Funcion para editar un producto
	def edit_product(self):
		self.message['text'] = ''
		try:
			# Al igual que en el ejemplo anterior verificamos de que podemos obtener un texto, si no
			# significa que el usuario no ha seleccionado nada
			self.table.item(self.table.selection())['text'][0]
		except IndexError as e:
			self.message['text'] = 'Seleccione un producto'
			return
		# obtemos solo el nombre del producto, para despues compararlo en el SQL
		name = self.table.item(self.table.selection())['text']
		# Obtenemos el texto que el usuario inserto de la otra ventana de editar
		old_price = self.table.item(self.table.selection())['values'][0]

		# Abrimos otra ventana
		self.edit_window = Toplevel()
		self.edit_window.title('Editar precio')

		# Old name, creamos un cuadro de texto donde el usuario escriba
		Label(self.edit_window, text='Nombre: ').grid(row=0,column=1)
		# Mostramos el nombre actual antes de actualizar, pero solo de lectura
		Entry(self.edit_window, textvariable=StringVar(self.edit_window, value=name), state='readonly').grid(row=0, column=2)

		# New name, crea un cuadro para que ingreses texto, el nuevo nombre del producto
		Label(self.edit_window, text='Nuevo nombre: ').grid(row=1, column=1)
		new_name = Entry(self.edit_window)
		new_name.focus()
		new_name.grid(row=1, column=2)

		# Old price, muestra el precio actual del producto, solo de lectura
		Label(self.edit_window, text='Precio: ').grid(row=2, column=1)
		Entry(self.edit_window, textvariable= StringVar(self.edit_window, value=old_price), state='readonly').grid(row=2, column=2)

		# New price, crea cuadro para que ingreses el nuevo precio
		Label(self.edit_window, text='Nuevo precio: ').grid(row=3, column=1)
		new_price = Entry(self.edit_window)
		new_price.grid(row=3, column=2)

		# Botón para actualizar, el botón actualizar envia parametros a la Función Editar
		# envia el nombre antes y después de actualizar, envia el precio antes y después de actualizar
		Button(self.edit_window, text='Actualizar', command= lambda: self.edit_records(new_name.get(), name, new_price.get(), old_price)).grid(row=4, column=1)
		Button(self.edit_window, text='Cancelar', command= self.cancel).grid(row=4, column=2)

	# Esta Función sera la encargada de ejecutar el query para el UPDATE
	def edit_records(self, new_name, name, new_price, old_price):
		# si no esta vacio los cuadros donde debe el usuario ingresar texto entonces se guardara
		# esto para evitar que la db se actualize vacia
		if self.validate_edit(new_name, new_price):
			query = 'UPDATE platillos SET nombre = ?, precio = ? WHERE nombre = ? AND precio = ?'
			parameters = (new_name, new_price, name, old_price)
			self.run_query(query, parameters)
			self.edit_window.destroy()
			self.message['text'] = 'Se actualizo {} correctamente'.format(name)
		else:
			self.message['text'] = 'Por favor ingresa los nuevos datos'
		self.get_products()

	# cierra la ventana de actualizar
	def cancel(self):
		self.edit_window.destroy()

	# Función que evalua los recuadros que no esten vacios, devuelve True o False
	def validate_edit(self, new_name, new_price):
		return len(new_name) != 0 and len(new_price) != 0

	# Unicamente cierra la venta, para cerrar el programa
	def end_program(self):
		self.wind.destroy()

if __name__ == '__main__':
	# Creamos una nueva ventana para iniciar el programa
	window = Tk()
	aplication = Product(window)

	window.mainloop()
