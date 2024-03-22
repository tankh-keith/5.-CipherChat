#!/usr/bin/python3

#PREFACE: IMPORT MODULES
import socket
import threading
import rsa



#1. DEFINE USER INPUTS:
print("Welcome to CipherChat™, your go-to encrypted chatroom!")
yourname=input("Enter your name:")
peername=input("Enter your peer's name:")
userinp=str(input("Enter '1' to HOST new chat. Enter '2' to CONNECT to existing chat."))



#2. SET UP RSA ENCRYPTION:
pub_key, priv_key=rsa.newkeys(1024) #generate 1024-bits pair of public key + private key, for the session
pub_keystore = None #created to store the public key of the chat partner, initialized with no value



#3. SET UP HOSTING VS CONNECTING LOGIC:
if userinp == "1": #if user chooses to host a chatroom...
	print("You will be HOSTING a new CipherChat™ room.")
	serverIPinp=input("Enter your machine's IP Address:") #prompt and save user's desired IPv4 address
	serverPORTinp=int(input("Choose a Port Number on your machine to listen:")) #prompt and save user's desired port number
	
	server=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #configure a new socket for server using user-specified IPv4 & TCP
	server.bind((serverIPinp, serverPORTinp)) #BIND the server's socket to the specified IPv4 address and port number
	
	server.listen() #server starts listening for incoming connections
	client, _ = server.accept() #when client makes a connection attempt, accept the client
	
	#HOSTING client SENDS public key first, then RECEIVES the public key of the connected client:
	client.send(pub_key.save_pkcs1("PEM"))
	pub_keystore = rsa.PublicKey.load_pkcs1(client.recv(1024))
	
	
elif userinp == "2": #else if user chooses to join a chatroom...
	print("You will be CONNECTING to an existing CipherChat™ room.")
	serverIPinp=input("Enter the server's IP Address:") #prompt the user for the server's IPv4 address
	serverPORTinp=int(input("Enter the server's Port Number:")) #prompt the user for the server's port number
	
	client=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #configure a new socket for client using user-specified IPv4 & TCP
	client.connect((serverIPinp, serverPORTinp)) #CONNECT the client to the server's IPv4 address and port number
	
	#CONNECTING client RECEIVES public key first, then SENDS its own public key:
	pub_keystore = rsa.PublicKey.load_pkcs1(client.recv(1024))
	client.send(pub_key.save_pkcs1("PEM"))
	
	
else: #if user keys in an invalid input for IP address or port number, alert user and exit the script
	print("Invalid input, exiting CipherChat™.")
	exit()
	
	

#4. SENDING & RECEIVING MESSAGES
def sendmessage(clnt): #function is defined for sending messages
	while True:
		msg=input('') #prompt the user to input their message, save to 'msg' variable
		encryptedmsg=rsa.encrypt(msg.encode(), pub_keystore) #encrypt the 'msg' using the other user's public key
		clnt.send(encryptedmsg) #send the encrypted message to the other user
		print(f"{yourname}(YOU): {msg}") #display the message

def receivemessage(clnt): #function is defined for receiving messages
	while True:
		#decrypt message using private key, print the result to the user
		print(peername + ': ' + rsa.decrypt(clnt.recv(1024), priv_key).decode())



#5. MULTI-THREADING
# To better manage inbound (receiving messages) & outbound (sending messages) tasks...
# ... where sending and receiving messages can run concurrently...
# ... thereby improving chat responsiveness

#set up 1st thread for sending messages, using 'sendmessage()' function
#pass the client socket as argument to the 'sendmessage()' function
threading.Thread(target=sendmessage, args=(client,)).start() 

#set up 2nd thread for receiving messages, using 'receivemessage()' function
#pass the client socket as argument to the 'receivemessage()' function
threading.Thread(target=receivemessage, args=(client,)).start()

	
