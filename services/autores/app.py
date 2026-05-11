from conexion import *
from autores import mis_autores

programa = Flask(__name__)
api = Api(programa)

class ListaAutores(Resource):

    def get(self):
        # Retorna todos los autores
        autores = mis_autores.listar()
        return jsonify({"mensaje": "autores", "data": autores})

    def post(self):
        nuevo = request.json

        # Condicion 1: si el idAutor ya existe, no pasa
        resultado_autor = mis_autores.consultar(nuevo["id"])
        if len(resultado_autor) != 0:
            return jsonify({"mensaje": "Id de autor ya existe"})

        # Condicion 2: el idAutor NO existe, verificar si el idPais existe
        resultado_pais = mis_autores.consultar_pais(nuevo["idPais"])
        if len(resultado_pais) == 0:
            # idAutor no existe Y idPais no existe → no pasa
            return jsonify({"mensaje": "El pais no existe, no se puede agregar el autor"})

        # idAutor no existe Y idPais si existe → pasa
        mis_autores.agregar(nuevo["id"], nuevo["nombre"], nuevo["email"], nuevo["idPais"])
        return jsonify({"mensaje": "Autor agregado con exito"})


class Autor(Resource):

    def get(self, id):
        # Busca un autor por id
        resultado = mis_autores.consultar(id)
        if len(resultado) == 0:
            return jsonify({"mensaje": "Autor no encontrado"})
        else:
            return jsonify({"mensaje": "Autor encontrado", "autor": resultado[0]})

    def put(self, id):
        # Modifica un autor existente
        nuevo = request.json
        resultado = mis_autores.consultar(id)
        if len(resultado) == 0:
            return jsonify({"mensaje": "Autor no existe"})
        else:
            mis_autores.modificar(id, nuevo["nombre"], nuevo["email"], nuevo["idPais"])
            return jsonify({"mensaje": "Autor modificado con exito"})

    def delete(self, id):
        # Elimina un autor existente
        resultado = mis_autores.consultar(id)
        if len(resultado) == 0:
            return jsonify({"mensaje": "Autor no existe"})
        else:
            mis_autores.eliminar(id)
            return jsonify({"mensaje": "Autor eliminado con exito!"})


api.add_resource(ListaAutores, "/autores")
api.add_resource(Autor, "/autores/<id>")

if __name__ == "__main__":
    programa.run(host="0.0.0.0", debug=True, port=5081)
