from conexion import *
from editoriales import mis_editoriales

programa = Flask(__name__)
api = Api(programa)

class ListaEditoriales(Resource):
    def get(self):
        editoriales = mis_editoriales.listar()
        return jsonify({"mensaje": "editoriales", "data": editoriales})

    def post(self):
        nuevo = request.json
        id_edi = nuevo["id"]
        id_pais = nuevo["idPais"]
        
        # CONDICIÓN 1: Si el ID de la editorial YA EXISTE, no busca nada más y se detiene.
        if len(mis_editoriales.consultar(id_edi)) > 0:
            return jsonify({"mensaje": "Id de editorial ya existe"})
            
        # CONDICIÓN 2: Si el ID del país NO EXISTE, no pasa.
        if len(mis_editoriales.consultar_pais(id_pais)) == 0:
            return jsonify({"mensaje": "El pais no existe"})
            
        # CONDICIÓN 3: Si pasó los dos filtros anteriores (Editorial no existe Y País sí existe), entonces PASA y guarda.
        mis_editoriales.agregar(id_edi, nuevo["nombre"], id_pais)
        return jsonify({"mensaje": "Editorial agregada con éxito"})

class Editorial(Resource):
    def get(self, id):
        resultado = mis_editoriales.consultar(id)
        if len(resultado) == 0:
            return jsonify({"mensaje": "Editorial no encontrada"})
        else:
            return jsonify({"mensaje": "Editorial encontrada", "editorial": resultado[0]})

    def put(self, id):
        nuevo = request.json
        if len(mis_editoriales.consultar(id)) == 0:
            return jsonify({"mensaje": "Editorial no existe"})
        else:
            mis_editoriales.modificar(id, nuevo["nombre"], nuevo["idPais"])
            return jsonify({"mensaje": "Editorial modificada con éxito"})

    def delete(self, id):
        if len(mis_editoriales.consultar(id)) == 0:
            return jsonify({"mensaje": "Editorial no existe"})
        else:
            mis_editoriales.eliminar(id)
            return jsonify({"mensaje": "Editorial eliminada con éxito!"})

api.add_resource(ListaEditoriales, "/editoriales")
api.add_resource(Editorial, "/editoriales/<id>")

if __name__ == "__main__":
    programa.run(host="0.0.0.0", debug=True, port=5083)