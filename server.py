from opcua import Server
import uuid
import json
import os

def run():
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/server/")
    server.set_server_name("MES OPC UA Server")
    server.start()
   
    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()
   # uri = "http://examples.freeopcua.github.io"
   # idx = server.register_namespace(uri)

   # Create Products folder
    products_folder = objects.add_folder("ns=3;s=Products", "Products")
    path = os.path.join("static", "data", "MOCK_DATA.json")
    
    with open(path, "r") as f:
        data = json.load(f)
       
        unique_entries = {}
        for item in data:
            # Create a new object for each product
            product_name = item['product_name']
            if product_name not in unique_entries:
                unique_entries[product_name] = item
        
        for item in unique_entries.values():
            product_name = item['product_name']
            product = products_folder.add_object(f"ns=3;s={product_name}", product_name)
            product_rate = product.add_variable(f"ns=3;s={uuid.uuid4()}", "ProductRate", item['productRate'])
            product_rate.set_writable()
 
    print("Server started. You can connect to opc.tcp://0.0.0.0:4840/server/")

    # Keep the server running
    input("Press Enter to stop the server...\n")
    server.stop()

if __name__ == "__main__":
    run()    