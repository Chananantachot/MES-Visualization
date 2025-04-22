from opcua import Server
import json
import os

def run():
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/server/")
    server.set_server_name("MES OPC UA Server")
    server.start()
   
    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)

   # Create Products folder
    products_folder = objects.add_folder(f"ns={idx};s=Products", "Products")

    path = os.path.join("static", "data", "MOCK_DATA.json")
    with open(path, "r") as f:
        data = json.load(f)
       
        unique_entries = {}
        for item in data:
            if item['product_name'] not in unique_entries:
                unique_entries[item['product_name']] = item
        
        for item in unique_entries.values():
            product = products_folder.add_object(f"ns={idx};s={item['product_name']}", item['product_name'])
            product_rate = product.add_variable(idx, "ProductRate", item['productRate'])
            product_rate.set_writable()
 
    print("Server started. You can connect to opc.tcp://0.0.0.0:4840/server/")

    # Keep the server running
    input("Press Enter to stop the server...\n")
    server.stop()

if __name__ == "__main__":
    run()    