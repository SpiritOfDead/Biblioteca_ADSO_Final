"""
Pruebas unitarias para el microservicio de EDITORIALES
Proyecto: Biblioteca - SENA ADSO
"""
from conexion import *
import pytest
import requests

class Test_editoriales:

    def setup_class(self):
        # ---- Preparación del entorno de pruebas ----
        self.url = "http://localhost:5083/editoriales"

        # Se asegura que el país de prueba exista (editoriales depende de paises)
        sql_pais = "INSERT IGNORE INTO paises (idPais, nombre, continente) VALUES ('CO', 'Colombia', 'America')"
        mi_cursor.execute(sql_pais)
        mi_db.commit()

        # Se crea una editorial de prueba
        sql = "INSERT IGNORE INTO editoriales (idEditorial, nombre, idPais) VALUES ('ED01', 'Editorial Prueba', 'CO')"
        mi_cursor.execute(sql)
        mi_db.commit()

    def teardown_class(self):
        # ---- Limpieza de la base de datos (Opcional) ----
        sql = "DELETE FROM editoriales WHERE idEditorial IN ('ED01', 'ED99', 'ED88', 'ED77')"
        mi_cursor.execute(sql)
        mi_db.commit()

    # ---------- PRUEBA 1: Listar todas las editoriales ----------
    def test_lista_editoriales(self):
        esperado = "editoriales"
        calculado = requests.get(self.url)
        assert calculado.status_code == 200
        assert calculado.json()["mensaje"] == esperado

    # ---------- PRUEBAS 2 y 3: Agregar editoriales (Parametrizado) ----------
    @pytest.mark.parametrize(
        ["nuevo_entrada", "esperado_entrada"],
        [
            ({"id": "ED99", "nombre": "Nueva Editorial", "idPais": "CO"}, "Editorial agregada con éxito"),
            ({"id": "ED01", "nombre": "Editorial Prueba", "idPais": "CO"}, "Id de editorial ya existe"),
        ]
    )
    def test_agregar(self, nuevo_entrada, esperado_entrada):
        calculado = requests.post(self.url, json=nuevo_entrada)
        assert calculado.status_code == 200
        assert esperado_entrada == calculado.json()["mensaje"]

    # ---------- PRUEBAS 4 y 5: Buscar una editorial por id ----------
    @pytest.mark.parametrize(
        ["id_entrada", "esperado_entrada"],
        [
            ("ED01", "Editorial encontrada"),   
            ("XXXX", "Editorial no encontrada"), 
        ]
    )
    def test_busqueda(self, id_entrada, esperado_entrada):
        calculado = requests.get(f"{self.url}/{id_entrada}")
        assert calculado.status_code == 200
        assert esperado_entrada in calculado.json()["mensaje"]

    # ---------- PRUEBA 6: Modificar editorial que sí existe ----------
    def test_modifica1(self):
        id = "ED01"
        nuevo = {"nombre": "Editorial Modificada", "idPais": "CO"}
        esperado = "Editorial modificada con éxito"
        calculado = requests.put(f"{self.url}/{id}", json=nuevo)
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]

    # ---------- PRUEBA 7: Modificar editorial que NO existe ----------
    def test_modifica2(self):
        id = "NOEXISTE"
        nuevo = {"nombre": "Nadie", "idPais": "CO"}
        esperado = "Editorial no existe"
        calculado = requests.put(f"{self.url}/{id}", json=nuevo)
        assert calculado.status_code == 200
        assert esperado in calculado.json()["mensaje"]

    # ---------- PRUEBAS 8 y 9: Eliminar editoriales ----------
    @pytest.mark.parametrize(
        ["id_entrada", "esperado_entrada"],
        [
            ("ED99",     "Editorial eliminada con éxito!"), 
            ("NOEXISTE", "Editorial no existe"),             
        ]
    )
    def test_elimina(self, id_entrada, esperado_entrada):
        calculado = requests.delete(f"{self.url}/{id_entrada}")
        assert calculado.status_code == 200
        assert esperado_entrada in calculado.json()["mensaje"]

    # ---------- PRUEBA 10: idEditorial NO existe Y idPais SI existe → PASA ----------
    def test_agregar_editorial_pais_existe(self):
        id = "ED88"
        nuevo = {"id": id, "nombre": "Editorial Valida", "idPais": "CO"}
        esperado = "Editorial agregada con éxito"
        calculado = requests.post(self.url, json=nuevo)
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]

    # ---------- PRUEBA 11: idEditorial NO existe Y idPais NO existe → FALLA POR PAÍS ----------
    def test_agregar_editorial_pais_no_existe(self):
        id = "ED77"
        nuevo = {"id": id, "nombre": "Editorial Invalida", "idPais": "ZZ"}
        esperado = "El pais no existe"
        calculado = requests.post(self.url, json=nuevo)
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]

    # ---------- PRUEBA 12: idEditorial SI existe → FALLA POR ID (NO CONSULTA PAÍS) ----------
    def test_agregar_editorial_ya_existe(self):
        id = "ED01"
        nuevo = {"id": id, "nombre": "Nombre X", "idPais": "ZZ"} # Aunque el país no existe, debe fallar primero por el ID
        esperado = "Id de editorial ya existe"
        calculado = requests.post(self.url, json=nuevo)
        assert calculado.status_code == 200
        assert esperado == calculado.json()["mensaje"]