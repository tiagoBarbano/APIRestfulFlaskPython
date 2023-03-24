from flask import Flask, jsonify, request
from client import Client
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import logging, requests, xmltodict, json
from logstash_async.handler import AsynchronousLogstashHandler
from xml.etree import ElementTree


logger = logging.getLogger('python-logstash-logger')
logger.setLevel(logging.INFO)
# logger.addHandler(AsynchronousLogstashHandler(
#     "localhost", 5959, database_path=None))


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/estudo"
mongo = PyMongo(app)


@app.route('/usuario', methods=['GET'])
def get_tasks():
    logger.info("Inicio da Consulta")  
    
    clients = []
    for c in mongo.db.clients.find():
        newClient = Client()
        newClient._id = str(c['_id'])
        newClient.name = c['name']
        newClient.phone = c['phone']
        newClient.email = c['email']
        clients.append(newClient)

    logger.info("Fim da Consulta")      
    return jsonify([c.__dict__ for c in clients]),200


@app.route('/usuario', methods=['POST'])
def create_client():
    logger.info("Inicio da Gravação")  
    
    newcli = Client()
    newcli._id = ObjectId()
    newcli.name = request.json['name']
    newcli.email = request.json['email']
    newcli.phone = request.json['phone']

    ret = mongo.db.clients.insert_one(newcli.__dict__).inserted_id
    
    logger.info("Dados Inseridos", extra={"id": str(ret) })  
    return jsonify({'id': str(ret)}),201


@app.route('/consulta/<string:cep>', methods=['POST'])
def consuta(cep):

    r1 = consutaCep(cep)
    r2 = consutaCidade(r1.get("localidade"))
        
    return { "consutaCep": r1,
             "consutaCidade": json.loads(r2)}


@app.route('/consulta-cep/<string:cep>', methods=['POST'])
def consutaCep(cep):

    r = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
    
    return r.json()


@app.route('/consulta-cidade/<string:cidade>', methods=['POST'])
def consutaCidade(cidade):
    c = cidade.lower().replace("ã", "a")
    
    r = requests.get(f'http://servicos.cptec.inpe.br/XML/listaCidades?city={c}')
    
    tree = ElementTree.fromstring(r.content)
    
    # for child in tree.iter('*'):
    #     city = child.find('nome')
    #     print(city.text)
    #     if city == cidade:
    #         codigo = child.find('id').text
    #         print(codigo)
    
    
    codigo = 244
    
    r = requests.get(f'http://servicos.cptec.inpe.br/XML/cidade/{codigo}/previsao.xml')
       
    return (json.dumps(xmltodict.parse(r.content), indent=4))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

