#!/usr/bin/env python3
"""
-Leonardo Granados, Isaiah Villalobos, Cooper Palmer
-CS 4470
-Programming Assignment #1 Remote Chat
-9/17/25
github repo: https://github.com/Lgranad13/Remote_Chat_Group7
"""

import socket
import sys
import threading

connections = []   #initalize array to hold [ (id, sock, ip, port) ]
MAX_USERS = 3
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
        "  send <id> <message>           Send a message (<= 100 chars) to a peer\n"     
        "  exit                          Close all connections and terminate\n"              
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
def connect_to(ip, port, LISTEN_PORT):       #takes user ip, port, uses global LISTEN_PORT to hold self port
    s = socket.socket()     #create the socket

    self_IP = get_my_ip()     #checks ip addr

    if self_IP == ip and LISTEN_PORT == port:        #if statement to prevent self connections
        print("Connection error: Self connection is not allowed")
        return
    
    for _,_,ip_i,port_i in connections:     #for loop to check array for dupes
        if ip_i == ip and port_i == port:
            print("Connection error: Duplicate connections is not allowed")
            return
        
    if len(connections) >= MAX_USERS:       #if statement to limit connections to 3 max
        print("Connection error: Reached Max of 3 connections, please terminate one before trying to connect again")
        s.close()
        return

    try:
        s.connect((ip, port))       #connect using user input for ip and port    

        s.settimeout(0.5)  # small timeout to catch server response
        try:
            server_msg = s.recv(1024) #check if server sent a message
            if server_msg: #if there is data
                print(server_msg.decode().strip())  # prints connection error server full ...
                s.close()  # closes the socket
                return
        except socket.timeout: #if it times out continues
            pass
        s.settimeout(None) #sets the timeout back to none 
        connections.append((len(connections)+1, s, ip, port))       #adds connections to array
        print(f"[chat> [info] Connected to {ip}:{port}")      #notifies user of successful connection
        threading.Thread(target=recv_from, args=(s, ip, port), daemon=True).start() #starts function to keep track of connection
    except Exception as e:
        print(f"Connection error: {e}")

#LG
#Helper function to keep user notified of when connection is terminated/closed
def recv_from(sock, ip, port):
    while True:
        try:
            data = sock.recv(1024)      #while loop to check if data connection is still live
            if not data:        #if data is not alive checks connections array to remove and notify user of it closing 
                break                
            try:
                msg = data.decode(errors="ignore")
            except Exception:
                msg = ""
            if msg.startswith("MSG|"):
                parts = msg.split("|", 2)
                if len(parts) == 3 and parts[1].isdigit():
                    sender_listen_port = int(parts[1])
                    body = parts[2]
                else:
                    sender_listen_port = port
                    body = msg
                print(f"Message received from {ip}")
                print(f"Sender's Port: {sender_listen_port}")
                print(f"Message: \"{body}\" \n[chat> ", end="")
        except: 
            break
    
    for i in connections:
        if i[2] == ip and i[3] == port:
            connections.remove(i)
            print(f"[info] Connection closed with {ip}:{port} \n[chat> ", end="")
            
    for i, p in enumerate(connections, start=1):  #goes through the array and changes the id to new reflection
                            connections[i-1] = (i, p[1], p[2], p[3])

    sock.close()        #closes the socket

#LG
#Function #5 -display the IP address and the listening port of all the connections the process is connected to
def list_connections():
    if not connections:       #lets user know if nothing is connected
        print("[chat> No connections live.")
    else:               #lets user know of all connections available for chat
        print(f"    id:  IP address       Port No.")
        for pid, _, ip, port in connections:
            print(f"    {pid}:  {ip}     {port}")

#LG
#Function #6 terminate the connection listed under the specified number
def terminate(pid):
    for i in connections:       #for loop to go through connections array
        if i[0] == pid:         #grabs the id that user inputted and checks if it available
            i[1].shutdown(socket.SHUT_RDWR) #closes socket for linux
            i[1].close()        #closes the socket connections and removes it from the array
            print(f"[chat> Terminated {i[2]}:{i[3]}")

            for i, p in enumerate(connections, start=1):    #goes through connections array and changes ids to show new reflection
                connections[i-1] = (i, p[1], p[2], p[3])
            return
    
    print("[chat> Invalid id")  #notifies user of error

#LG
#Server function that is listening to make connections
def server(port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #fixes linux issue when trying to use reuse a closed port
    s.bind(('', port))
    s.listen()
    print(f"Listening on port {port}\n[chat> ", end="")
    while True:     #while loop to accept connections if succesfull
            c, a = s.accept()

            #checks if array is at max
            if len(connections) >= MAX_USERS:       #if reached max connections denies connection, notifies client to terminate one, and sends data to user that it is currently full
                print("Connection error: Reached Max of 3 connections, please terminate one to accept connection \n[chat> ", end="")
                c.sendall("Connection error: Server is full: connection was denied".encode())
                c.close()
            else:
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
    threading.Thread(target=server, args=(LISTEN_PORT,), daemon=True).start()   #Theard to start the server

    #while loop to keep checking for user input
    while True:
        cmd = input("[chat> ").split() #grabs the user input, splits it and puts it into array cmd
        if not cmd: 
            continue
        if cmd[0]=="connect" and len(cmd)==3:           #4 if connect is selected runs connect function
            connect_to(cmd[1], int(cmd[2]), LISTEN_PORT)
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
        elif cmd[0]=="send" and len(cmd)>=3:            #7 if id is correct sends message
            try:
                pid = int(cmd[1])
            except ValueError:
                print("[chat> Invalid id")
                continue
            message = ' '.join(cmd[2:])
            send_message(pid, message)
        elif cmd[0]=="exit":                            #8 if exit is selected exits 
            exit_program()
        
        else: print("Command does not exist. Please type - help - for commands")  #to let user know command doesn't exist
