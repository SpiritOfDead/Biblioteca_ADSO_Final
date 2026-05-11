from conexion import *
from editoriales import mis_editoriales

programa = Flask(__name__)
api = Api(programa)

class ListaEditoriales(Resource):

    def get(self):
        # Retorna todas las editoriales
        editoriales = mis_editoriales.listar()
        return jsonify({"mensaje": "editoriales", "data": editoriales})

    def post(self):
        nuevo = request.json

        # Condicion 1: si el idEditorial ya existe, no pasa
        resultado_editorial = mis_editoriales.consultar(nuevo["id"])
        if len(resultado_editorial) != 0:
            return jsonify({"mensaje": "Id de editorial ya existe"})

        # Condicion 2: el idEditorial NO existe, verificar si el idPais existe
        resultado_pais = mis_editoriales.consultar_pais(nuevo["idPais"])
        if len(resultado_pais) == 0:
            # idEditorial no existe Y idPais no existe → no pasa
            return jsonify({"mensaje": "El pais no existe, no se puede agregar la editorial"})

        # idEditorial no existe Y idPais si existe → pasa
        mis_editoriales.agregar(nuevo["id"], nuevo["nombre"], nuevo["idPais"])
        return jsonify({"mensaje": "Editorial agregada con exito"})


class Editorial(Resource):

    def get(self, id):
        # Busca una editorial por id
        resultado = mis_editoriales.consultar(id)
        if len(resultado) == 0:
            return jsonify({"mensaje": "Editorial no encontrada"})
        else:
            return jsonify({"mensaje": "Editorial encontrada", "editorial": resultado[0]})

    def put(self, id):
        # Modifica una editorial existente
        nuevo = request.json
        resultado = mis_editoriales.consultar(id)
        if len(resultado) == 0:
            return jsonify({"mensaje": "Editorial no existe"})
        else:
            mis_editoriales.modificar(id, nuevo["nombre"], nuevo["idPais"])
            return jsonify({"mensaje": "Editorial modificada con exito"})

    def delete(self, id):
        # Elimina una editorial existente
        resultado = mis_editoriales.consultar(id)
        if len(resultado) == 0:
            return jsonify({"mensaje": "Editorial no existe"})
        else:
            mis_editoriales.eliminar(id)
            return jsonify({"mensaje": "Editorial eliminada con exito!"})


api.add_resource(ListaEditoriales, "/editoriales")
api.add_resource(Editorial, "/editoriales/<id>")

if __name__ == "__main__":
    programa.run(host="0.0.0.0", debug=True, port=5083)
