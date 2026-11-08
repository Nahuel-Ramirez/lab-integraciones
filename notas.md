# Notas Semanales 
Cuando se envia un pedido a traves de HTTP con el metodo POST, el sistema que recibe el pedido deberia enviar el codigo exitoso 201 - CREATED. 200 es para un GET, ya que te indica OK, aca tenes lo que pediste.

Codigos de error posibles:
- 4xx: Este tipo de errores es de QUIEN MANDA, por ejemplo, Mobile Farma mando un cliente que no existe, una cantidad negativa o falta la fecha. Ahi va un 400 o 422 y hay que corregir el pedido y lo que envia.
- 5xx: El error es de QUIEN RECIBE, a plataforma se le cayo la base o tuvo un bug. Aca reintentar mas tarde tiene sentido.
- Si falla la conexion no hay codigo: llega un timeout o error de red. 

SOAP tambien viaja por http casi siempre con POST. El contenido es un XML con un "sobre" o envelope de estructura muy estricta.
El contrato esta en un archivo WSDL que describe exactamente que operaciones hay y que campos lleva cada una.

REST es mal libre, usa JSON, URLs que representan cosas como /pedidos /clientes, etc. y los metodos HTTP para decidir que hacer.

Ejemplo de envio de un pedido a plataforma:

POST /pedidos HTTP/1.1                      ← método + URL
Host: mini-plataforma.local
Content-Type: application/json              ← headers (metadatos)
Authorization: Bearer abc123

{                                           ← body (los datos)
  "fecha": "2026-11-07",
  "codigo_cliente": "FAR-0042",
  "vendedor": "V-015",
  "items": [
    {"articulo": "IBU-400", "cantidad": 12}
  ]
}

Respuesta:

HTTP/1.1 201 Created                        ← código de estado
Content-Type: application/json

{"numero_pedido": 1234, "estado": "recibido"}


- 400 Bad Request (o 422 si el formato está bien pero el contenido no valida). Bien dicho lo de “corregir y volver a enviar”: reenviar exactamente lo mismo no sirve, porque va a fallar igual.
- 503 Service Unavailable es el código típico de “estoy caído, probá después”. Un detalle para la semana 5: reintentar está bien, pero no en loop cada un segundo. Lo que se hace es esperar cada vez más (1s, 2s, 4s...). Y aparece una trampa: ¿y si Plataforma sí guardó el pedido, pero se cayó justo antes de contestar? Si Mobile Pharma reintenta, el pedido queda duplicado. Guardate esa pregunta, que es el corazón de la semana 5.
- 200 Perfecto: GET /pedidos/1234 devuelve 200 con los datos. Y si el pedido 1234 no existe, la respuesta es 404 Not Found.

En REST, la URL dice sobre qué cosa trabajás y el método dice qué hacés con ella:

Método	Qué hace	Ejemplo con Plataforma
GET	Consultar	GET /pedidos/1234: ver un pedido
POST	Crear	POST /pedidos: cargar un pedido nuevo
PUT	Reemplazar entero	PUT /pedidos/1234: mandar el pedido completo corregido
PATCH	Modificar una parte	PATCH /pedidos/1234: cambiar solo el estado
DELETE	Borrar o anular	DELETE /pedidos/1234: anular el pedido

Fijate que la URL es la misma (/pedidos/1234) y lo único que cambia es el método. Esa es la gracia de REST.


# Lab Fase 1


## Paso 1
### Venv
Un venv es un entorno virtual, se usa para instalar librerias para desarrollar aplicaciones y que no esten esparcidas por ahi.
La idea es que si vos tenes una app, por ejemplo "Ventanita" en una carpeta, e instalas librerias sin venv, cuando desarrolles otra app que utiliza las mismas librerias pero otra version, al no estar contenidas dentro de un venv, las mismas pueden romper la otra app, al tener una version distinta. De esta manera es como que "empaquetas" toda la app bajo un entorno virtual y todas sus dependencias estan contenidas ahi sin perjudicar a las demas.

Como se crea un venv?

python -m venv <nombre_que_quieras (por lo general se vuelve a poner ".venv")>

- "-m" -> le dice a python "ejecuta este modulo"
- por convension, se coloca como nombre de carpeta ".venv" porque de esta manera, el "." la marca como carpeta de sistema, no de tu codigo.


## Paso 2
### Git y el entorno virtual

Git se usa para versionar codigo, no programas.
Entonces, un venv se puede recrear en cualquier momento con un comando y ademas pesa varios MB, no tiene sentido versionarlo.
Para esto se crea un archivo llamado ".gitignore" y todo lo que ingresemos ahi NO se subira a Github y no se versionara. Esta carpeta se encuentra en la raiz del proyecto.

## Paso 3
### Instalacion de librerias

Vamos a comenzar el lab instalando 2 librerias necesarias para el desarrollo de codigo y la creacion de nuestro backend para la integracion.
Cuales son esas librerias?
- uvicorn: es como una ventana, o mejor dicho un servidor que se queda escuchando en un puerto de mi PC, no sabe nada de reglas de negocio, recibe los mensajes HTTP y devuelve la respuesta, nada mas.
- FastAPI: es un framework que lo que hace es validar ese mensaje con el pedido que llega. Lee el JSON, lo valida y arma la respuesta con el codigo de estado correcto. Es como si le dijeras: "Si llega un POST /pedidos, ejecuta esta funcion".

La primera se ocupa de la red. La segunda de la logica de la API.

Como se instalan?
- pip: es el comando que se utiliza para instalar librerias (pip install <libreria1> <libreria2>)
- con "pip list" listamos lo que instalamos. Por que aparecen mas librerias si solo instale 2?
La respuesta es que por ejemplo FastAPI no hace todo el trabajo, sino que se apoya ademas en otras librerias que pip instala automaticamente, y estas otras librerias se llaman "dependencias"

Por ejemplo:
- pydantic: Valida los datos
- starlette: es la base de FastAPI, la que maneja la parte HTTP.
- zipp y el resto: son dependencias de dependencias.

## Paso 4
### Dejamos anotados lo que se instalo.

Si el dia de mañana, todo el codigo que armamos en una PC, lo necesitamos en otra PC, necesitamos clonar el repositorio donde este el codigo.
Pero que pasa? .venv no lo versionamos, entonces necesitamos la lista de las librerias y dependencias para instalarlas en la PC nueva.
Entonces en la nueva PC hariamos lo siguiente:
- Clonamos el repositorio
- Creamos el .venv
- Instalamos las librerias. (pip install -r requirements.txt)

Como las anotamos? con el comando "pip freeze" y esa salida la tenes que mandar en un archivo llamado requirements.txt para que luego con el comando "pip install -r requirements.txt" tengas todas las librerias con su version exacta instaladas en la nueva PC.

## Paso 5
### Primer archivo main. Prueba de conexion y primer codigo.

El primer endpoint que se crea es uno de prueba: un GET / que conteste "la plataforma esta viva" y es lo primero que se arma en cualquier integracion real, para chequear que el servicio responde.

Para esto vamos a necesitar 3 piezas:
1- Importar la clase: "FastAPI" desde la libreria fastapi. Representa a la app entera.
2- Crear una instancia de esa clase y guardarla en una variable llamada "app". Esa variable es tu mini plataforma: todo lo que agregues despues se cuelga de ella.
3- Una funcion que responda al GET. Se escribe como una funcion normal de python con un decorador arriba que dice que metodo y que ruta atiende.

   @app.<metodo>("<ruta>")

Que es un decorador?
es una linea con un "@" arriba de una funcion que la "registra". Aca le dice a FastAPI que cuando llegue ese metodo a esa ruta, ejecuta la funcion de mas abajo.


