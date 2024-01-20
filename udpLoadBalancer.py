import sys
import socket


# Create a UDP socket for the load balancer
loadBalancerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
loadBalancerSocket.bind(('localhost', 8888))

# Server addresses and corresponding ports
servers = [('localhost', 2526), ('localhost', 2527), ('localhost', 2528)]

# Initialize the current server index to 0
current_server_index = 0

# Set a timeout for the load balancer socket (adjust as needed)
loadBalancerSocket.settimeout(2)  # Set a timeout longer than the client's timeout

while True:
    try:
        # Receive the client packet along with the address it is coming from
        message, client_address = loadBalancerSocket.recvfrom(1024)

        # Choose the next server in the list using round-robin
        server_address = servers[current_server_index]
        current_server_index = (current_server_index + 1) % len(servers)

        
        # Add information and create a new message
        additional_info = f"(This message came from load balancer !!!) The port of this server is {server_address[1]}"
        new_message = message + additional_info.encode('utf-8')
            
        # Create a new socket for the server communication
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.settimeout(2)  # Set a timeout longer than the client's timeout for server sockets

            # Send the modified client request to the selected server
            server_socket.sendto(new_message, server_address)

            # Receive the response from the server
            response, _ = server_socket.recvfrom(1024)

            # Forward the server's response back to the client
            loadBalancerSocket.sendto(response, client_address)

    except socket.timeout:
        print('Load Balancer: REQUEST TIMED OUT')
    except Exception as e:
        print(f'Load Balancer: An error occurred - {e}')
