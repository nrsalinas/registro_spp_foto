################################################################################
#
# This program is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with 
# this program. If not, see <https://www.gnu.org/licenses/>. 
#
# Copyright 2025 Nelson R. Salinas
#
################################################################################

import streamlit as st
import pandas as pd
import gspread
import datetime
import pytz

gc = gspread.service_account_from_dict(st.secrets.credentials)
tz = pytz.timezone('America/Bogota')

if 'errors' not in st.session_state:
	st.session_state.errors = ''

if 'data' not in st.session_state:
	st.session_state.data = None

if 'submitted' not in st.session_state:
	st.session_state.submitted = False

##########     Object lists    ##############
listas = pd.read_csv("Lista_categorias.csv")
plants = listas.query('Plantas.notna()').Plantas.sort_values().to_list()
birds = listas.query('Aves.notna()').Aves.to_list()
insects = listas.query('Insectos.notna()').Insectos.to_list()
#animals = sorted(birds + insects)
taxa = sorted(birds + insects + plants)
observers = listas.query('Observadores.notna()').Observadores.to_list()
sites = listas.query('Sitios.notna()').Sitios.to_list()

digitizers = ['Angela', 'Nelson']

#observers = [
#	'Juliana Zuluaga',
#	'Carlos Vargas',
#	'Nelson Salinas'
#	]


id_observaciones = []

st.markdown("""

# Jardín Botánico de Bogotá

## Programa Conservación _in situ_

### Formato de digitalización de registros de especies a partir de fotografías.

#### Instrucciones

Insertar las observaciones en la forma abajo. Una vez termine de digitar los datos de una observación, presione el botón :red[**Validar**] para validar los datos. Si existen errores, un mensaje aparecerá indicando la naturaleza del error. Los datos no serán guardados si son erróneos, así que deben ser corregidos para que puedan ser guardados.

""")

# This doesn't work in Linux -> :blue-background[:red[**Enviar**]] 

def validate():
	"""
	Rutina principal de validadción de información del formulario.
	"""

	if st.secrets.token != st.session_state.token:
		st.session_state.errors += 'El token de autenticación es incorrecto.\n\n'

	if st.session_state.date is None:
		#st.info('Error: Falta fecha de observación.', icon="🔥")
		st.session_state.errors += 'La fecha de observación es un campo obligatorio.\n\n'

	if st.session_state.photo:
		
		if len(st.session_state.photo.name) < 5:
			#st.info("El nombre de la fotografía es sospechosamente pequeño.")
			st.session_state.errors += "El nombre de la fotografía es sospechosamente pequeño.\n\n"
		
	else:
		st.session_state.errors += "No hay fotografía adjudicada a la observación.\n\n"

	if st.session_state.observer is None:
		st.session_state.errors += 'El nombre del observador es un campo obligatorio.\n\n'

	if st.session_state.digitizer is None:
		st.session_state.errors += 'El digitador es un campo obligatorio.\n\n'

	if st.session_state.sp1 is None:
		if st.session_state.sp1alt is None:
			st.session_state.errors += 'El nombre de la especie 1 es obligatorio.\n\n'

	if st.session_state.site is None \
		and (st.session_state.lon is None or st.session_state.lat is None):

		st.session_state.errors += "Una ubicación geográfica es obligatoria, ya sea 'Sitio' o coordenadas geográficas.\n\n"

	st.session_state.submitted = False




def submit():
	
	sh = gc.open_by_key(st.secrets.table_link).worksheet(st.session_state.digitizer)
	now = datetime.datetime.now(tz)
	row = [
		str(st.session_state.date),
		st.session_state.photo.name,
		st.session_state.observer,
	]

	if st.session_state.sp1:
		row.append(st.session_state.sp1)
	else:
		row.append(st.session_state.sp1alt)
		
	row += [
		st.session_state.lat,
		st.session_state.lon,
		st.session_state.site,
		now.strftime('%Y-%m-%d %H:%M:%S'),
		st.session_state.digitizer,
	]
	sh.append_row(row)
	st.session_state.submitted = True




with st.form(
	"Fotografías - Registro de especies",
	clear_on_submit=True,
	):

	st.text_input(
		"Token de autenticación",
		help="Token de validación de usuario",
		placeholder='Digite el token',
		value=None,
		key="token"
	)

	st.date_input(
		"Fecha",
		help="Fecha en la cual fue realizada la observación.",
		value=None,
		key="date",
	)

	st.file_uploader(
		"Seleccione una fotografía", 
		key="photo",
		help='Fotografía base de observación.'
	)
	
	st.selectbox(
		"Observador", 
		observers, 
		index=None, 
		key='observer',
		placeholder="Seleccione un investigador",
		help='Persona que tomó la fotografía'
	)

	st.selectbox(
		"Digitalizador", 
		digitizers, 
		index=None, 
		key='digitizer',
		placeholder="Seleccione un investigador",
		help='Persona que sistematiza la fotografía'
	)

	st.selectbox(
		"Especie", 
		taxa,
		index=None, 
		key="sp1",
		placeholder='Digite el nombre científico',
		help="Nombre científico (sin autores) de la especie 1",
	)

	st.text_input(
		"Especie (si no está en el listado de arriba)",
		key="sp1alt",
		placeholder='Digite el nombre científico',
		help="Si el nombre científico de la especie no está en la lista de arriba, digitelo aquí. Verifique la ortografía en una base de datos apropiada (por ejemplo, GBIF).",
	)

	st.number_input(
		"Latitud", 
		key="lat",
		value=None,
		placeholder="Latitud",
		help='Latitud de la observación en formato decimal (e.g., 3.09284)',
		max_value=4.838990,
		min_value=3.725902,
		step=0.00001
	)

	st.number_input(
		"Longitud", 
		key="lon",
		value=None,
		placeholder="Longitud",
		help='Longitud de la observación en formato decimal (e.g., -77.2360184)',
		min_value=-74.2248,
		max_value=-73.99194,
		step=0.00001
	)

	st.selectbox(
		"Sitio", 
		sites, 
		index=None, 
		key='site',
		placeholder="Seleccione un sitio",
		help='Sitio (parque, localidad, etc.) donde se realizó la observación.'
	)


	st.form_submit_button('Validar', on_click=validate)

pretty_data = st.empty()

if len(st.session_state.errors) > 0:
	st.session_state.errors = "# Error\n\n" + st.session_state.errors
	st.info(st.session_state.errors)


else:

	# Present data before upload

	with pretty_data.container():

		if st.session_state.date:
			st.write(f"Fecha observación: '{str(st.session_state.date)}'")

		if st.session_state.photo:
			st.write(f"Nombre de la fotografía: '{str(st.session_state.photo.name)}'")

		if st.session_state.observer:
			st.write(f"Observador: '{st.session_state.observer}'")

		if st.session_state.digitizer:
			st.write(f"Digitador: '{st.session_state.digitizer}'")

		if st.session_state.sp1:
			st.write(f"Especie: '{st.session_state.sp1}'")

		elif st.session_state.sp1alt:
			st.write(f"Especie: '{st.session_state.sp1alt}'")

		if st.session_state.lat:
			st.write(f"Latitud: '{st.session_state.lat}'")

		if st.session_state.lon:
			st.write(f"Longitud: '{st.session_state.lon}'")

		if st.session_state.site:
			st.write(f"Sitio: '{st.session_state.site}'")


	st.markdown("""Si los datos arriba son correctos, presione el botón :red[**Guardar**] para enviar los datos.""")

	st.button("Guardar", on_click=submit)

	if st.session_state.submitted:
		pretty_data.empty()




exit(0)