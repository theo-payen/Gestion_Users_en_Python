#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sqlite3, threading, socket, smtplib, datetime

def envoie_mail( Suject, My_message, to):
	SMTP_SERVER = "smtp.gmail.com"
	SMTP_PORT = 587
	SMTP_USERNAME = "[votre adress mail]"
	SMTP_PASSWORD = "[votre mdp]"


	s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
	s.starttls()
	s.login(SMTP_USERNAME, SMTP_PASSWORD)
	message = 'Subject: {}\n\n{}'.format(Suject, My_message)
	s.sendmail(SMTP_USERNAME, to, message)
	s.quit()

def New_table():
	print ("nouvelle table Utilisateurs vient d'être crée ")
	QueryCurs.execute('''CREATE TABLE Utilisateur
	(id INTEGER PRIMARY KEY, LOGIN TEXT,PASSWORD TEXT,ROLE INTEGER, NOM TEXT, PRENOM TEXT,MAIL TEXT,DEPARTEMENT TEXT,DATE TEXT)''')

def add_User(LOGIN,PASSWORD,ROLE,NOM,PRENOM,MAIL,DEPARTEMENT):
	DATE = datetime.date.today()
	QueryCurs.execute('''INSERT INTO Utilisateur (LOGIN,PASSWORD,ROLE,NOM,PRENOM,MAIL,DEPARTEMENT,DATE)
	VALUES (?,?,?,?,?,?,?,?)''',(LOGIN,PASSWORD,ROLE,NOM,PRENOM,MAIL,DEPARTEMENT,DATE))
	DataBase.commit()

def file_exist(file):
	if os.path.getsize(file) == 0:
		print ("création du fichier",file)
		New_table()
		print ("création de l'utilisateur par default root avec comme mdp root ")
		add_User("root", "4813494d137e1631bba301d5acab6e7bb7aa74ce1185d456565ef51d737677b2","1","root","root","root@root", "IT")

def date_expire(date_db):	
	date_expire = datetime.date.today() + datetime.timedelta(-30)
	date_db = datetime.datetime.strptime(date_db, "%Y-%m-%d")
	if date_expire <= date_db.date():
		return True
	else:
		return False

def date_expire_bientot(date_db):
	date_expire = datetime.date.today() + datetime.timedelta(-20)
	date_db = datetime.datetime.strptime(date_db, "%Y-%m-%d")
	if date_expire <= date_db.date():
		return True
	else:
		return False

def update_password(PWD, LOGIN):
	date = datetime.date.today()
	QueryCurs.execute("UPDATE Utilisateur SET PASSWORD = ? WHERE LOGIN = ?",(PWD,LOGIN,),).fetchall()
	QueryCurs.execute("UPDATE Utilisateur SET DATE = ? WHERE LOGIN = ?",(date,LOGIN,),).fetchall()
	DataBase.commit() 

def Update_value_db (SET, SET_value, ID):
	if SET == "LOGIN":
		QueryCurs.execute("UPDATE Utilisateur SET LOGIN = ? WHERE id = ?",(SET_value,ID,),).fetchall()
	elif SET == "PASSWORD":
		date = datetime.date.today()
		QueryCurs.execute("UPDATE Utilisateur SET PASSWORD = ? WHERE id = ?",(SET_value,ID,),).fetchall()
		QueryCurs.execute("UPDATE Utilisateur SET DATE = ? WHERE id = ?",(date,ID,),).fetchall()
	elif SET == "ROLE":
		QueryCurs.execute("UPDATE Utilisateur SET ROLE = ? WHERE id = ?",(SET_value,ID,),).fetchall()
	elif SET == "MAIL":
		QueryCurs.execute("UPDATE Utilisateur SET MAIL = ? WHERE id = ?",(SET_value,ID,),).fetchall()
	elif SET == "NOM":
		QueryCurs.execute("UPDATE Utilisateur SET NOM = ? WHERE id = ?",(SET_value,ID,),).fetchall()
	elif SET == "PRENOM":
		QueryCurs.execute("UPDATE Utilisateur SET PRENOM = ? WHERE id = ?",(SET_value,ID,),).fetchall()
	elif SET == "DEPARTEMENT":
		QueryCurs.execute("UPDATE Utilisateur SET DEPARTEMENT = ? WHERE id = ?",(SET_value,ID,),).fetchall()
	DataBase.commit() 

def LOGIN_exist (LOGIN):
	try :
		Log = str(QueryCurs.execute("SELECT LOGIN FROM Utilisateur WHERE LOGIN=?",(LOGIN,),).fetchall())
	except:
		return "True"
	if LOGIN in Log :
		return "False"
	else :
		return "True"

def instanceServeur (client, infosClient, server):
	# fichier de log a la fin de la connection avec l'utilisateur le fichier est mis a jour
	LOG_SERVER = open("server.log", "a")
	# l'addres ip du client	
	adresseIP = infosClient[0]
	# numéro du client donné automatiquement par le serveur	
	port = str(infosClient[1])
	print(adresseIP + " : " + port + " : " + "Authentication" )
	LOG_SERVER.write(adresseIP + " : " + port + " : " + "Authentication\n")
	# message envoyer par le client recus dans message1
	message1 = client.recv(255).decode("utf-8").split(" ")
	# le client essaye de se connecter en envoyen Connection suiviue de son login et son password crypter 
	if message1[0] == "CONNECTION" :
		Login_db = str(QueryCurs.execute("SELECT LOGIN FROM Utilisateur WHERE LOGIN=?",(message1[1],),).fetchall())
		mots_de_passe_db = str(QueryCurs.execute("SELECT PASSWORD FROM Utilisateur WHERE LOGIN=?",(message1[1],),).fetchall())
		# verrifie si le login et le password corespon dans la base de donné 
		if message1[1] in Login_db and message1[2] in mots_de_passe_db :
			print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message1[0]+ " Autoriser" )
			LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message1[0]+ " Autoriser\n")
			# permet d'envoyer un message au client
			client.send("approved_connection".encode("utf-8"))
			date_db = str(QueryCurs.execute("SELECT DATE FROM Utilisateur WHERE LOGIN=?",(message1[1],),).fetchall())
			# verrifi la date d'expiration du compte sauf pour root si la date est plus vieille de 30 j alors l'utilisateur ne peux pas se connecter
			date_exp = date_expire(date_db[3:13])
			# le client va envoyer un message de confirmation de reception du messager présedant pour ne pas envoyer d'autre message par le serveur trop rapidement
			client.recv(255).decode("utf-8").split(" ")
			# si l'user = root alors on ne prend pas en compte la date expiration
			if message1[1] == "root":
				date_exp = True
			# teste la date expirtation 
			if date_exp == True:
				
				# pas erreur sur le script executer en local mais a distance oui 
				client.send("Password_expir_good".encode("utf-8"))
				client.recv(255).decode("utf-8").split(" ")
				# verrifi la date d'expiration du compte sauf pour root si la date arrive a expiration alter l'user 10 j avant
				date_exp2 = date_expire(date_db[3:13])
				# si l'user = root alors on ne prend pas en compte la date expiration
				if message1[1] == "root":
					date_exp2 = True
				# teste la date expiration entre 20 et 30 j pour alter l'utilisateur
				if date_exp2 == False :
					client.send("Password_expir_bientot".encode("utf-8"))
					print ("changer votre mdp car il va bientot expiré")
				else :
					client.send("Password_expir_bientot_good".encode("utf-8"))
				# recupère le role de l'utilisateur connecter 
				admin = str(QueryCurs.execute("SELECT ROLE FROM Utilisateur WHERE LOGIN=?",(message1[1],),).fetchall())
				# verrifi si l'utilisateur est admin
				client.recv(255).decode("utf-8").split(" ")
				if "1" in admin :
					print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message1[0]+ " Administrator" )
					LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message1[0]+ " Administrator\n")

					# envoie le message Administrator au client
					client.send("Administrator".encode("utf-8"))
					while True:
						# message envoyer par le client recus dans message2
						message2 = client.recv(255).decode("utf-8").split(" ")
						# si le client envoi Liste_User alors le serveur renvoi la liste des utilisateur
						if message2[0] == "List_User":				
							print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message2[0])
							LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message2[0] + "\n")
							# recupère toute les donnée dans la table Utilisateur
							list2 = QueryCurs.execute('SELECT * FROM Utilisateur')
							for x in list2:
								x = str(x)
								# envoie la liste des user 1 par 1
								client.send(x.encode("utf-8"))
								# permet de confirmé la reception du message d'avant par le client
								client.recv(255).decode("utf-8").split(" ")
							client.send("List_User_END".encode("utf-8"))
							del x
						# si le client envoi New_User avec comme paramettre login passowrd crypter nom prenom email departement alors le serveur crée le nouvelle user dans la base de donné
						elif message2[0] == "New_User":
							print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message2[0])
							LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message2[0]  + "\n")
							if message2[1] == "manual":
								while True:
									satus_login = LOGIN_exist(message2[2])
									if satus_login == "True":
										client.send(satus_login.encode("utf-8"))
										break
									else :
										client.send(satus_login.encode("utf-8"))
										message2 = client.recv(255).decode("utf-8").split(" ")
										
							else:
								satus_login = LOGIN_exist(message2[2])
								client.send(satus_login.encode("utf-8"))
							message2bis = client.recv(255).decode("utf-8").split(" ")
							
							add_User(message2bis[1],message2bis[2],message2bis[3],message2bis[4],message2bis[5],message2bis[6],message2bis[7])
							Suject = "Nouveau compte utilisateur"
							My_message =  f"""\
Bonjour {message2bis[4]} {message2bis[5]}
Votre nom de compte vient d'être crée avec comment login 
{message2bis[1]}
"""
							# permet de géré les erreur
							try:
								# envoie un mail a la personne plus lui infoirmer de la création de son compte mdp non envoyer pour des raison de securité
								envoie_mail(Suject, My_message, message2bis[6])
							except:
								print(adresseIP + " : " + port + " : " + message1[1]+ " : " + "Mail Error " +  message2bis[6])
								LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + "Mail Error "+  message2bis[6]  + "\n")
						# si le client envoi Modif_User avec son Id alors on entre dans une nouvelle boucle
						elif message2[0] == "Modif_User":
							print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message2[0])
							LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message2[0]  + "\n")
							List_in_ID = (str(QueryCurs.execute("SELECT * FROM Utilisateur WHERE id = ?",(message2[1],),).fetchall()))
							# envoie les donné de l'user [ID] dans la base de donée
							client.send(List_in_ID.encode("utf-8"))
							
							while True:
								# message envoyer par le client recus dans message3
								message3 = client.recv(255).decode("utf-8").split(" ")
								
								if message3[0] == "Modif_Login":
									
									while True :
										exist = LOGIN_exist(message3[1])
										# permet de verrifier si user existe deja
										if exist == True :
											# code a changer sur le client
											Update_value_db ("LOGIN", message3[1],message3[2])
											print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0])
											LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0]  + "\n")
											client.send("Update_LOGIN_Good".encode("utf-8"))
											break
										else :
											print ("Login existe deja")
											print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0] + ": Error")
											LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0] + ": Error"  + "\n")
											client.send("Update_LOGIN_Error".encode("utf-8"))
											# permet d'attendre la réponse du client a nouveau
											message3 = client.recv(255).decode("utf-8").split(" ")

								elif message3[0] == "Modif_Password":
									print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0])
									LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0]  + "\n")
									Update_value_db ("PASSWORD",message3[1],message3[2])
								
								elif message3[0] == "Modif_role_admin":
									print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0])
									LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0]  + "\n")
									Update_value_db ("ROLE","1",message3[1])
								
								elif message3[0] == "Modif_role_user":
									print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0])
									LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0]  + "\n")
									Update_value_db ("ROLE","0",message3[1])
								
								elif message3[0] == "Modif_nom":
									print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0])
									LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0]  + "\n")
									Update_value_db ("NOM",message3[1],message3[2])

								elif message3[0] == "Modif_prenom":
									print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0])
									LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0]  + "\n")
									Update_value_db ("PRENOM",message3[1],message3[2])

								elif message3[0] == "Modif_mail":
									print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0])
									LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0]  + "\n")
									Update_value_db ("MAIL",message3[1],message3[2])
								
								elif message3[0] == "Modif_departement":
									print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0])
									LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message3[0]  + "\n")
									Update_value_db ("DEPARTEMENT",message3[1],message3[2])
								
								elif message3[0] == "END":
									break

								else:
									break
						
						elif message2[0] == "Delete_user":
							print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message2[0])
							LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message2[0]  + "\n")
							# permet de supprimer un utilisateur via son id
							QueryCurs.execute(" DELETE FROM Utilisateur WHERE id = ?",(message2[1],),).fetchall()
							DataBase.commit()   
						
						elif message2[0] == "END":
							break
						
						else :
							break
								
				# connection en user
				else:
					print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message1[0]+ " User" )
					LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message1[0]+ " User\n")
					client.send("Utilisateur".encode("utf-8"))
					while True:
						message4 = client.recv(255).decode("utf-8").split(" ")
						
						if message4[0] == "Modif_password":
							pwd_h = str( QueryCurs.execute("SELECT PASSWORD FROM Utilisateur WHERE LOGIN = ?",(message1[1],),).fetchall())	
							if message4[1] in pwd_h:
								client.send("True".encode("utf-8"))
								print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message4[0])
								LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message4[0]  + "\n")
								message4bis = client.recv(255).decode("utf-8").split(" ")
								update_password(message4bis[1],message4bis[2])
							else :
								client.send("False".encode("utf-8"))
						
						elif message4[0] == "END":
							break
						
						else :
							break
					
			else:
				print(adresseIP + " : " + port + " : " + message1[1]+ " : " + " Mots de passe expiré"  + "\n")
				LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + " Mots de passe expiré" )
				client.send("Password_expir_error".encode("utf-8"))
		else :
			print(adresseIP + " : " + port + " : " + message1[1]+ " : " + message1[0]+ " Refuser" )
			LOG_SERVER.write(adresseIP + " : " + port + " : " + message1[1]+ " : " + message1[0]+ " Refuser"  + "\n")
			client.send("ERROR".encode("utf-8"))
	print(adresseIP + " : " + port + " : " + "Logout")
	LOG_SERVER.write(adresseIP + " : " + port + " : " + "Logout\n")
	# ferme le fichier de log 
	LOG_SERVER.close()
	# ferme la connection entre le serveur et le client
	client.close()



threadsClients = []
file = "DataBase.db"
DataBase = sqlite3.connect(file, check_same_thread=False)
QueryCurs = DataBase.cursor()
file_exist(file)

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# ecoute sur le port 65530
serveur.bind(('', 65530))
serveur.listen(5)
# permet de géré plusieur client en meme temps
while True:
	client, infosClient = serveur.accept()
	threadsClients.append(threading.Thread(None, instanceServeur, None, (client, infosClient, serveur), {}))
	threadsClients[-1].start()


#fichier.close()
#serveur.close()