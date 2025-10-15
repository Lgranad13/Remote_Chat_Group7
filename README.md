# 🗨️ CS4470 Programming Assignment 1
## Chat Application using TCP Sockets

---

## 👤 Authors
### **Name:** Leonardo Granados, Isaiah Villalobos, Cooper Palmer
### **Group:** 7
### **Course:** CS4470 – Computer Networks

---

## 📘 Overview
This project implements a simple peer-to-peer chat system using TCP sockets in Python.
Each instance of the program acts as both a server and a client.

The program allows users to:
 - Connect to peers by IP and port
 - List active connections
 - Terminate specific connections
 - Detect when peers disconnect unexpectedly
 - Display user IP
 - Display user Port
 - Display help commands
 - Sends message to connected peers
 - Exit program and closes all connections

 ---

## ⚙️ Commands Implemented
| # | Command | Description |
|----------|----------|--------------|
| **1** | **help** | Displays all commands |
| **2** | **myip** | Displays user IP |
| **3** | **myport** | Displays user port |
| **4** | **connect `<ip>` `<port>`** | Establish a new TCP connection to the given peer |
| **5** | **list** | Display all active peer connections with IDs, IPs, and ports |
| **6** | **terminate `<id>`** | Close the connection identified by the given ID |
| **7** | **send `<id>` `<msg>`** | Sends a message to choosen connected peer |
| **8** | **exit** | Exit program and closes all connections |

---
