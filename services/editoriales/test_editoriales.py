"""
Pruebas unitarias para el microservicio de EDITORIALES
Proyecto: Biblioteca - SENA ADSO
Sintaxis básica de aprendiz
"""
from conexion import *
import pytest

class Test_editoriales:

    def setup_class(self):
        # ---- Preparación del entorno de pruebas ----
        # Se asegura que el país de prueba exista (editoriales depende de paises)
        self.url = "http://localhost:5083/editoriales"

        sql_pais = "INSERT IGNORE INTO paises (idPais, nombre, continente) VALUES ('CO', 'Colombia', 'America')"
        mi_cursor.execute(sql_pais)
        mi_db.commit()

        # Se crea una editorial de prueba
        sql = "INSERT IGNORE INTO editoriales (idEditorial, nombre, idPais) VALUES ('ED01', 'Editorial Prueba', 'CO')"
        mi_cursor.execute(sql)
        mi_db.commit()

    def teardown_class(self):
        # ---- Limpieza de la base de datos ----
        sql = "DELETE FROM editoriales WHERE idEditorial='ED01'"
        mi_cursor.execute(sql)
        mi_db.commit()

    # ---------- PRUEBA 1: Listar todas las editoriales ----------
    def test_lista_editoriales(self):
        esperado = "editoriales"
        # Ejecutar la prueba
        calculado = requests.get(self.url)
        # Verificación
        assert calculado.status_code == 200
        assert calculado.json()["mensaje"] == esperado

    #Agregar editoriales ----------
    @pytest.mark.parametrize(
        ["nuevo_entrada", "esperado_entrada"],
        [
            # Caso exitoso: editorial nueva
            ({"id": "ED99", "nombre": "Nueva Editorial", "idPais": "CO"}, "Editorial agregada con éxito"),
            # Caso fallido: editorial ya existe
            ({"id": "ED01", "nombre": "Editorial Prueba", "idPais": "CO"}, "Id de editorial ya existe"),
        ]
    )
    def test_agregar(self, nuevo_entrada, esperado_entrada):
        # Ejecutar la prueba
        calculado = requests.post(self.url, json=nuevo_entrada)
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado_entrada == calculado.json()["mensaje"]

    # ---------- PRUEBA 3: Buscar una editorial por id ----------
    @pytest.mark.parametrize(
        ["id_entrada", "esperado_entrada"],
        [
            ("ED01", "Editorial encontrada"),   # Existe
            ("XXXX", "Editorial no encontrada"), # No existe
        ]
    )
    def test_busqueda(self, id_entrada, esperado_entrada):
        id = id_entrada
        esperado = esperado_entrada
        # Ejecutar la prueba
        calculado = requests.get(f"{self.url}/{id}")
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]

    # ---------- PRUEBA 4: Modificar editorial que sí existe ----------
    def test_modifica1(self):
        id = "ED01"
        nombre = "Editorial Modificada"
        idPais = "CO"
        nuevo = {"nombre": nombre, "idPais": idPais}
        esperado = "Editorial modificada con éxito"
        # Ejecutar la prueba
        calculado = requests.put(f"{self.url}/{id}", json=nuevo)
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]
        # Verificar en la base de datos que el cambio quedó guardado
        sql = f"SELECT * FROM editoriales WHERE idEditorial='{id}'"
        mi_cursor.execute(sql)
        datos = mi_cursor.fetchall()[0]
        assert nombre == datos[1] and idPais == datos[2]

    # ---------- PRUEBA 5: Modificar editorial que NO existe ----------
    def test_modifica2(self):
        id = "NOEXISTE"
        nuevo = {"nombre": "Nadie", "idPais": "CO"}
        esperado = "Editorial no existe"
        # Ejecutar la prueba
        calculado = requests.put(f"{self.url}/{id}", json=nuevo)
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]

    # ---------- PRUEBA 6: Eliminar editoriales ----------
    @pytest.mark.parametrize(
        ["id_entrada", "esperado_entrada"],
        [
            ("ED99",     "Editorial eliminada con éxito!"), # Existe (se creó en test_agregar)
            ("NOEXISTE", "Editorial no existe"),             # No existe
        ]
    )
    def test_elimina(self, id_entrada, esperado_entrada):
        id = id_entrada
        esperado = esperado_entrada
        # Ejecutar la prueba
        calculado = requests.delete(f"{self.url}/{id}")
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]
        # Si se eliminó, verificar que ya no esté en la BD
        if "éxito" in esperado_entrada:
            mi_db.commit()
            sql = f"SELECT * FROM editoriales WHERE idEditorial='{id}'"
            mi_cursor.execute(sql)
            datos = mi_cursor.fetchall()
            assert len(datos) == 0


    # Validacion doble FK (idEditorial + idPais)

    # idEditorial NO existe Y idPais SI existe → pasa 
    def test_agregar_editorial_pais_no_existe(self):
        id = "ED77"
        nombre = "Editorial Invalida"
        idPais = "ZZ"          # ZZ no existe en la base de datos
        nuevo = {"id": id, "nombre": nombre, "idPais": idPais}
        
        # CORREGIDO: El mensaje debe ser exactamente igual al de app.py
        esperado = "El pais no existe"
        
        # Ejecutar la prueba
        calculado = requests.post(self.url, json=nuevo)
        
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]

    def test_agregar_editorial_pais_no_existe(self):
        id = "ED77"
        nombre = "Editorial Invalida"
        idPais = "ZZ"          # ZZ no existe en la base de datos
        nuevo = {"id": id, "nombre": nombre, "idPais": idPais}
        
        # CORREGIDO: Se dejó exactamente el mismo mensaje corto que envía app.py
        esperado = "El pais no existe"
        
        # Ejecutar la prueba
        calculado = requests.post(self.url, json=nuevo)
        
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]

    #  idEditorial NO existe Y idPais NO existe → no pasa ----------
    def test_agregar_editorial_pais_no_existe(self):
        id = "ED77"
        nombre = "Editorial Invalida"
        idPais = "ZZ"          # ZZ no existe en la base de datos
        nuevo = {"id": id, "nombre": nombre, "idPais": idPais}
        esperado = "El pais no existe, no se puede agregar la editorial"
        # Ejecutar la prueba
        calculado = requests.post(self.url, json=nuevo)
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]
        # Verificar que NO se insertó en la base de datos
        sql = f"SELECT * FROM editoriales WHERE idEditorial='{id}'"
        mi_cursor.execute(sql)
        datos = mi_cursor.fetchall()
        assert len(datos) == 0

    #idEditorial SI existe → no consulta, ya existe ----------
    def test_agregar_editorial_ya_existe(self):
        id = "ED01"            # Ya existe desde setup_class
        nuevo = {"id": id, "nombre": "Cualquier nombre", "idPais": "CO"}
        esperado = "Id de editorial ya existe"
        # Ejecutar la prueba (no debe consultar el pais porque el id ya existe)
        calculado = requests.post(self.url, json=nuevo)
        # Verificar la prueba
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]
