"""
Pruebas unitarias para el microservicio de AUTORES
Proyecto: Biblioteca - SENA ADSO
"""
from conexion import *
import pytest
import requests

class Test_autores:

    def setup_class(self):
        self.url = "http://localhost:5081/autores"
        # Usamos IGNORE para que no se estrelle si CO o AU001 ya vienen en el SQL de la base de datos
        sql_pais = "INSERT IGNORE INTO paises (idPais, nombre, continente) VALUES ('CO', 'Colombia', 'America')"
        mi_cursor.execute(sql_pais)
        mi_db.commit()
        
        sql = "INSERT IGNORE INTO autores (idAutor, nombre, email, idPais) VALUES ('AU001', 'Autor de Prueba', 'prueba@test.com', 'CO')"
        mi_cursor.execute(sql)
        mi_db.commit()

    def test_lista_autores(self):
        esperado = "autores"
        calculado = requests.get(self.url)
        assert calculado.status_code == 200
        assert calculado.json()["mensaje"] == esperado

    @pytest.mark.parametrize(
        ["nuevo_entrada", "esperado_entrada"],
        [
            ({"id": "AU999", "nombre": "Nuevo Autor", "email": "nuevo@test.com", "idPais": "CO"}, "Autor agregado con éxito"),
            ({"id": "AU001", "nombre": "Autor de Prueba", "email": "prueba@test.com", "idPais": "CO"}, "Id de autor ya existe"),
        ]
    )
    def test_agregar(self, nuevo_entrada, esperado_entrada):
        calculado = requests.post(self.url, json=nuevo_entrada)
        assert calculado.status_code == 200
        assert esperado_entrada == calculado.json()["mensaje"]

    @pytest.mark.parametrize(
        ["id_entrada", "esperado_entrada"],
        [("AU001", "Autor encontrado"), ("XXXX", "Autor no encontrado")]
    )
    def test_busqueda(self, id_entrada, esperado_entrada):
        calculado = requests.get(f"{self.url}/{id_entrada}")
        assert calculado.status_code == 200
        assert esperado_entrada in calculado.json()["mensaje"]

    def test_modifica1(self):
        id = "AU001"
        nuevo = {"nombre": "Autor Modificado", "email": "modificado@test.com", "idPais": "CO"}
        calculado = requests.put(f"{self.url}/{id}", json=nuevo)
        assert calculado.status_code == 200
        assert "Autor modificado con éxito" in calculado.json()["mensaje"]

    def test_modifica2(self):
        id = "NOEXISTE"
        nuevo = {"nombre": "Nadie", "email": "nadie@test.com", "idPais": "CO"}
        calculado = requests.put(f"{self.url}/{id}", json=nuevo)
        assert calculado.status_code == 200
        assert "Autor no existe" in calculado.json()["mensaje"]

    @pytest.mark.parametrize(
        ["id_entrada", "esperado_entrada"],
        [("AU999", "Autor eliminado con éxito!"), ("NOEXISTE", "Autor no existe")]
    )
    def test_elimina(self, id_entrada, esperado_entrada):
        calculado = requests.delete(f"{self.url}/{id_entrada}")
        assert calculado.status_code == 200
        assert esperado_entrada in calculado.json()["mensaje"]

    
    def test_agregar_autor_pais_existe(self):
        #id NO existe, Pais SI existe -> Pasa
        nuevo = {"id": "AU900", "nombre": "Autor Valido", "email": "valido@test.com", "idPais": "CO"}
        calculado = requests.post(self.url, json=nuevo)
        assert calculado.status_code == 200
        assert calculado.json()["mensaje"] == "Autor agregado con éxito"

    def test_agregar_autor_pais_no_existe(self):
        #id NO existe, Pais NO existe  Falla por pais
        nuevo = {"id": "AU901", "nombre": "Autor Invalido", "email": "invalido@test.com", "idPais": "ZZ"}
        calculado = requests.post(self.url, json=nuevo)
        assert calculado.status_code == 200
        assert calculado.json()["mensaje"] == "El pais no existe"

    def test_agregar_autor_ya_existe(self):
        #id SI existe  Corta antes de revisar el país
        nuevo = {"id": "AU001", "nombre": "Ya existo", "email": "existo@test.com", "idPais": "CO"}
        calculado = requests.post(self.url, json=nuevo)
        assert calculado.status_code == 200
        assert calculado.json()["mensaje"] == "Id de autor ya existe"