from flask import Flask, jsonify ,render_template
from opcua import Client
from opcua import ua, Server
from opcua.common.type_dictionary_buider import DataTypeDictionaryBuilder, get_ua_class
import uuid
import json
import random

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/opcua/products")
def products():
    # Connect to the OPC UA server
    client = Client("opc.tcp://0.0.0.0:4840/server/")
    try:
        client.connect()
        
        #objects = client.get_objects_node()
        products_folder = client.get_node("ns=3;s=Products") 
       
        product_nodes = products_folder.get_children()
        labels = []
        data = []
        for product in product_nodes:
            labels.append(product.get_browse_name().Name)
            rate_node = product.get_child(["0:ProductRate"])  # assuming same namespace index
            rate_value = round(random.uniform(rate_node.get_value(), 50),2) #rate_node.get_value()
            data.append((rate_value))
       
    finally:
        client.disconnect()

    dataset = json.dumps({
        'labels': labels,
        'data': data
    })

    return dataset

@app.route("/opcua/structures")
def create_opcua_structures():
    server = Server()
    server.set_endpoint('opc.tcp://0.0.0.0:51210/OPCUA/SimulationServer')
    server.set_server_name('Custom structure demo server')

    uri = "http://www.prosysopc.com/OPCUA/SimulationNodes/"
    idx = server.register_namespace(uri)
    dict_builder = DataTypeDictionaryBuilder(server, idx, uri, 'MyContactPersons')

    person = dict_builder.create_data_type('Person')

    person.add_field('ID', ua.VariantType.Guid)
    person.add_field('Gender', ua.VariantType.Boolean)
    person.add_field('Email', ua.VariantType.String)
    person.add_field('Phone', ua.VariantType.String)
    person.add_field('Name', ua.VariantType.String)


    person.add_field('Notes', ua.VariantType.String)
    dict_builder.set_dict_byte_string()
    
    server.load_type_definitions()

    person_var = server.nodes.objects.add_variable(ua.NodeId(namespaceidx=idx), 'BasicStruct',
                                                ua.Variant(None, ua.VariantType.Null),
                                                datatype=person.data_type)
    person_var.set_writable()
    p = get_ua_class("Person")
    p.ID = uuid.uuid4()
    p.Name = 'Scott'
    p.Gender = True
    p.Email = 'Scott@mail.com'
    person_var.set_value(p)

    server.start()
    print(getattr(dict_builder, '_type_dictionary').get_dict_value())
    value = person_var.get_value()
    print(value.ID)
    print(value.Name)
   
    return "contact person created with custom structure"


if __name__ == '__main__':
    app.run(debug=True)    