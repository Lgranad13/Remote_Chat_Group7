#!/usr/bin/env python3
"""
-Leonardo Granados, Isaiah Villalobos
-CS 4470
-Programming Assignment #1 Remote Chat
-9/17/28
"""


import socket
import sys
import threading

connections = []   #initalize array to hold [ (id, sock, ip, port) ]
LISTEN_PORT = None   # remember which port our server listens on

#IV
#Function #1 Help - Displays info about the available user interface options or command manual.
def show_help():
    print(
        "Available commands:\n"
        "  help                          Show this help message\n"
        "  connect <ip> <port>           Open a TCP connection to a peer\n"
        "  list                          List active connections (id: ip:port)\n"
        "  terminate <id>                Close the connection by its id\n"
        "  myip                          Display this process's IP (non-127.*)\n"
        "  myport                        Display the port this process is listening on\n"
    )

#IV
#Function #2 Myip - Displays the IP address of this process. IP isn't local address. 
def get_my_ip():
    ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # No packets are sent; this just asks the OS which interface would be used
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        pass
    finally:
        try:
            s.close()
        except Exception:
            pass

    # Fallbacks in case the above still yields loopback
    if ip.startswith("127."):
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            pass

    if ip.startswith("127."):
        try:
            for fam, _, _, _, sockaddr in socket.getaddrinfo(socket.gethostname(), None):
                if fam == socket.AF_INET and not sockaddr[0].startswith("127."):
                    ip = sockaddr[0]
                    break
        except Exception:
            pass

    return ip

#LG
#Function #4 Connect -establishes a new TCP connection
def connect_to(ip, port):
    s = socket.socket()     #create the socket
    try:
        s.connect((ip, port))       #connect using user input for ip and port
        connections.append((len(connections)+1, s, ip, port))       #adds connections to array
        print(f"[chat> [info] Connected to {ip}:{port}")      #notifies user of successful connection
        threading.Thread(target=recv_from, args=(s, ip, port), daemon=True).start() #starts function to keep track of connection
    except Exception as e:
        print("Connection error:", e)

#LG
#Helper function to keep user notified of when connection is terminated/closed
def recv_from(sock, ip, port):
    while True:
        try:
            data = sock.recv(1024)      #while loop to check if data connection is still live
            if not data:        #if data is not alive checks connections array to remove and notify user of it closing
                for i in connections:
                    if i[2] == ip and i[3] == port:
                        print(f"[info] Connection closed with {ip}:{port} \n[chat> ", end="")
                        connections.remove(i)
                break
        except: 
            break
    sock.close()        #closes the socket
    

#LG
#Function #5 -display the IP address and the listening port of all the connections the process is connected to
def list_connections():
    if not connections:       #lets user know if nothing is connected
        print("[chat> No connections live.")
    else:               #lets user know of all connections avialabe for chat
        for pid, _, ip, port in connections:
            print(f"{pid}: {ip}:{port}")

#LG
#Function #6 terminate the connection listed under the specified number
def terminate(pid):
    for i in connections:       #for loop to go through connections array
        if i[0] == pid:         #grabs the id that user inputted and checks if it avialable
            i[1].close()        #closes the socket connections and removes it from the array
            connections.remove(i)
            print(f"[chat> Terminated {i[2]}:{i[3]}")
            return
    print("[chat> Invalid id")  #notifies user of error

#LG
#Server function that is listening to make connections
def server(port):
    s = socket.socket()
    s.bind(('', port))
    s.listen()
    print(f"Listening on port {port}\n[chat> ", end="")
    while True:     #while loop to accept connections if succesfull
        c, a = s.accept()
        pid = len(connections)+1    #gives id to the new connection
        connections.append((pid, c, a[0], a[1]))        #adds the info to the array connections
        print(f"[info] New connection from {a[0]}:{a[1]}\n[chat> ", end="")
        threading.Thread(target=recv_from, args=(c, a[0], a[1]), daemon=True).start()   #starts the thread to keep track of connection

#LG
#Main program to continously run until exited/closed
if __name__ == "__main__":
    if len(sys.argv) != 2:      #if statement to make sure user runs the executable with open port
        print("[chat> Missing open port. try ex: ./chat 4545")
        sys.exit(1)

    LISTEN_PORT = int(sys.argv[1])
    threading.Thread(target=server, args=(LISTEN_PORT,), daemon=True).start()

    #while loop to keep checking for user input
    while True:
        cmd = input("[chat> ").split() #grabs the user input, splits it and puts it into array cmd
        if not cmd: 
            continue
        if cmd[0]=="connect" and len(cmd)==3:           #4 if connect is selected runs connect function
            connect_to(cmd[1], int(cmd[2]))
        elif cmd[0] == "help":                          #1 if help is selected runs help function
            show_help()
        elif cmd[0] == "myip":                          #2 if myip is selected runs myip function
            print(get_my_ip())
        elif cmd[0] == "myport":
            print(LISTEN_PORT)
        elif cmd[0]=="list":                            #5 if list is selected runs the list function
            list_connections()
        elif cmd[0]=="terminate" and len(cmd)==2:       #6 if terminated is selected runs the terminated function
            terminate(int(cmd[1]))
        else: print("Command does not exist.")  #to let user know command doesn't exist
