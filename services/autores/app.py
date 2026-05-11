from conexion import *
from autores import mis_autores

programa = Flask(__name__)
api = Api(programa)

class ListaAutores(Resource):
    def get(self):
        autores = mis_autores.listar()
        return jsonify({"mensaje": "autores", "data": autores})

    def post(self):
        nuevo = request.json
        id_autor = nuevo["id"]
        id_pais = nuevo["idPais"]
        
        # CONDICIÓN 1: Si el ID del autor YA EXISTE, corta y no busca más.
        if len(mis_autores.consultar(id_autor)) > 0:
            return jsonify({"mensaje": "Id de autor ya existe"})
            
        # CONDICIÓN 2: Si el ID del país NO EXISTE, no pasa.
        if len(mis_autores.consultar_pais(id_pais)) == 0:
            return jsonify({"mensaje": "El pais no existe"})
            
        # CONDICIÓN 3: Si llega aquí, significa que el autor no existe Y el país sí existe. ¡PASA!
        mis_autores.agregar(id_autor, nuevo["nombre"], nuevo["email"], id_pais)
        return jsonify({"mensaje": "Autor agregado con éxito"})

class Autor(Resource):
    def get(self, id):
        resultado = mis_autores.consultar(id)
        if len(resultado) == 0:
            return jsonify({"mensaje": "Autor no encontrado"})
        else:
            return jsonify({"mensaje": "Autor encontrado", "autor": resultado[0]})

    def put(self, id):
        nuevo = request.json
        if len(mis_autores.consultar(id)) == 0:
            return jsonify({"mensaje": "Autor no existe"})
        else:
            mis_autores.modificar(id, nuevo["nombre"], nuevo["email"], nuevo["idPais"])
            return jsonify({"mensaje": "Autor modificado con éxito"})

    def delete(self, id):
        if len(mis_autores.consultar(id)) == 0:
            return jsonify({"mensaje": "Autor no existe"})
        else:
            mis_autores.eliminar(id)
            return jsonify({"mensaje": "Autor eliminado con éxito!"})

api.add_resource(ListaAutores, "/autores")
api.add_resource(Autor, "/autores/<id>")

if __name__ == "__main__":
    programa.run(host="0.0.0.0", debug=True, port=5081)