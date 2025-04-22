from opcua import Server
import random
import uuid

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
    # Create ProductRate variable
    for i in range(1, 11):
        product_name = f'Products({i})'
        product = products_folder.add_object(f"ns=3;s={product_name}", product_name)
        product_rate = product.add_variable(f"ns=3;s={uuid.uuid4()}", "ProductRate", round(random.uniform(1, 10),2))
        product_rate.set_writable()

    print("Server started. You can connect to opc.tcp://0.0.0.0:4840/server/")

    # Keep the server running
    input("Press Enter to stop the server...\n")
    server.stop()

if __name__ == "__main__":
    run()    