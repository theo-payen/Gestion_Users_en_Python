import hashlib , os, random, string, re, socket

def hashe_password(password):
	mots_de_passe_hashe = hashlib.sha256(password.encode()).hexdigest()
	return mots_de_passe_hashe

def password_alleatoire():
	length = 8
	chars = string.ascii_letters + string.digits + '!@#$%^&*()'
	random.seed = (os.urandom(1024))
	return (''.join(random.choice(chars) for i in range(length)))

def Valide_password(): 
	while True:
		pwd =input ("modifier le mot de passe conetenant 8 caratere minimum : ")
		valid_pwd=password_check(pwd)
		if valid_pwd== True:
			pwd_h = hashe_password(pwd)
			return pwd_h
		elif valid_pwd== False:
			print ("mot de passe ne respecte pas l 'exigence ")

def password_check(pwd):
	if re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', pwd):
		return True
	else:
		return False

def reponse_serveur():
	Reponse = client.recv(255)
	Reponse =  Reponse.decode("utf-8")
	return Reponse

# address ip du serveur
adresseIP = "localhost"
# port d'ecoute du serveur
port = 65530


i = 0
while i != 3:	
	# se connecte au serveur
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect((adresseIP, port))
	print("Connecté au serveur",adresseIP, port)
	
	LOGIN = input ("Veillez saisir votre login : ")
	PASSWORD = input ("Veillez saisir votre mots de passe : ")
	PASSWORD = hashe_password(PASSWORD)
	# essaye de se conneter a la base de donné qui se trouve sur le serveur
	client.send(("CONNECTION"+ " " + LOGIN + " " + PASSWORD).encode("utf-8"))
	Reponse_connexion = reponse_serveur()
	print (Reponse_connexion)
	# connection ok
	if Reponse_connexion == "approved_connection" :
		print ("connexion autorisé par le serveur")
		break
	# connection false autre tentative
	elif Reponse_connexion  == "ERROR":
		print ("\n connexion refusé \n")
		# ferme la connection du client pour ne pas poser de probleme l'autre de la seconde tentative de connection
		client.close()
		pass
	else:
		# ferme la connection du client pour ne pas poser de probleme l'autre de la seconde tentative de connection
		client.close()
		pass
	# permet de quité le script si l'utilisazteur essaye de se connecter plus de 3 fois
	i += 1

# connection appreouver par le serveur
if Reponse_connexion == "approved_connection":
	# envoie une message de confirmation de reception du message au serveur 
	client.send(("ok").encode("utf-8"))
	Reponse_expir = reponse_serveur()
	if Reponse_expir == "Password_expir_good":
		client.send(("ok").encode("utf-8"))
		Reponse_expir_Bientot = reponse_serveur()
		if Reponse_expir_Bientot == "Password_expir_bientot":
			print ("Votre mdp va bientot expiré veillez le changer")
		
		print ("t'es connecter en", LOGIN)
		client.send(("ok").encode("utf-8"))
		Reponse_droit = reponse_serveur()
		# reponse du serveur me connect en adm
		if Reponse_droit == "Administrator":
			print ("vous avez les droit admin")

			while True:
				print ("""
					[1]     .afficher les utilisateurs
					[2]     .ajouter un nouvau utilisateur
					[3]     .modifier un utilisateur
					[4]     .supprimer un utilisateur
					[5]     .quitter
				""")
				option=input("?")
				# lister les users
				if option=="1": 
					
					print("\nafficher les utilisateurs") 
					# envoie Liste_User pour demander au serveur de lister les user
					client.send(("List_User").encode("utf-8"))
					while True:
						# récupaire la réponse du serveur 1 par 1
						Reponse_List_User = reponse_serveur()
						#si le client recois Liste_User_END alors il quite la boucle
						if Reponse_List_User == "List_User_END":
							break
						# envoie ok pour l'utilisateur suivant
						client.send(("OK").encode("utf-8"))
						# affiche les user 1 par 1 
						print (Reponse_List_User)

				
				elif option=="2":
					
					# ajoute un nouvelle user
					print("\n ajouter un nouvel utilisateur") 
					while True:
						NOM = input("NOM")
						PRENOM = input("PRENOM")
						config_login = input("Voulez-vous générer  le login (recommandée ) ?  (o) oui (n) non:  ")
						''' nous avons souhaité de donner à l administrateur de choisir un login si besoin '''
						if config_login == "o":
							# definir le login en automatique avec la première lettre du prenom et le nom de famille 
							LOGIN = PRENOM[0] + NOM
							# demande au serv si le login exsite
							client.send(("New_User"+ " " + "auto" +" " + LOGIN).encode("utf-8"))
							
							exist = reponse_serveur()
							# si le login existe deja ajouter 1 a la fin pour ne pas avoir de doublon
							if exist == "False" :
								LOGIN = LOGIN + "1"
							break

						elif config_login == "n":
							while True :
								LOGIN = input("LOGIN: ")
								# demande au serv si le login exsite
								client.send(("New_User"+ " " + "manual" +" " + LOGIN).encode("utf-8"))
								exist = reponse_serveur()
								
								if exist == "True" :
									break
								# si le login existe deja demander dans saisir un nouveau
								else :
									print ("Login existe deja")
							break
						else:
							print("\n choix non valide veuillez saisir une option ")
					while True:	
						mdp_all = input("Voulez-vous générer un mot de passe aléatoire?  (o) oui (n) non:  ")
						''' Ici, on appelle la fonction pour générer le mot de passe.  '''
						if mdp_all == "o" :
							# génaire le msp aléatoirement
							PASSWORD = password_alleatoire()
							print ("voici le mot de passe généré ", PASSWORD)
							# hacher le password 
							PASSWORD_h = hashe_password(PASSWORD)
							break
						elif mdp_all == "n" :
							# saisi le mots de passe puis verrifie si il est valide
							PASSWORD_h = Valide_password()
							break
						else:
							print("\n choix non valide veuillez saisir une option ") 
							
					while True:
						
						ROLE_confirm = input("souhaitez-vous donner les droits en tant que admin? (o) oui (n) non : ")
						if ROLE_confirm == "o":
							ROLE = "1"
							break
						elif ROLE_confirm == "n":
							ROLE = "0"
							break
						else:
							print("\n choix non valide veuillez saisir une option ") 
		
					
					# envoi un mail par le serveur lors de la création du nouvelle user 
					MAIL = input("MAIL")
					DEPARTEMENT = input("DEPARTEMENT")
					# ici on appelle la fonction add_User
					client.send(("New_User"+ " " + LOGIN + " " + PASSWORD_h + " " + ROLE + " " + NOM + " " + PRENOM + " " + MAIL + " " + DEPARTEMENT).encode("utf-8"))

				elif option=="3":
					# pour modifier un user on gère via l'id lister les user pour la voir
					ID = input("slect l'id de l'utilisateur :")
					# indique au client qu'on veux modifier l'user [ID]
					client.send(("Modif_User"+ " " + ID).encode("utf-8"))
					# le serveur renvoie les information consernan l'user [ID]
					Reponse_ID = reponse_serveur()
					while True:
						print (Reponse_ID)
						print ("""
						[1]     .modifer le login
						[2]     .modifier le mot de passe
						[3]     .modifier le role 
						[4]     .modifier le nom
						[5]     .modifier le prénom
						[6]     .modifier l'adresse mail
						[7]     .modifier le departement
						[8]     .quitter
						""")
						option2=input("?")
						
						if option2=="1":                            
							while True :
								# modifi le login de l'user [ID]
								Login =input ("modif login en : ")
								client.send(("Modif_Login"+ " " + Login + " " + ID).encode("utf-8"))
								# confirme que le nouveau login existe pas deja
								confirm_login = reponse_serveur()
								if confirm_login == "Update_LOGIN_Good":
									break
								elif confirm_login == "Update_LOGIN_Error":
									print ("le login existe deja")
								else : 
									print ("une erreur est survenu")

						
						elif option2 == "2":
							# modifi le mots de passe avant de l'envoier au serveur en le hache
							pwd =input ("pwd: ")
							pwd_h = hashe_password(pwd)
							client.send(("Modif_Password"+ " " + pwd_h + " " + ID).encode("utf-8"))
						
						elif option2 == "3":
							# permet de changer le role de l'utilisateur
							droit = input("voulez vous lui donne des droit administrateur (y)(n)")
							if droit == "y":
								client.send(("Modif_role_admin"+ " " + ID).encode("utf-8"))
							elif droit == "n" :
								client.send(("Modif_role_user"+ " " + ID).encode("utf-8"))
							else:
								print("\n choix non valide veuillez saisir une option ") 
						
						elif option2 == "4":
							# modifi le nom
							Nom =input ("modif nom: ")
							client.send(("Modif_nom"+ " " + Nom + " " + ID).encode("utf-8"))
						elif option2 == "5":
							# modfi le prenom
							Prenom =input ("modif prenom: ")
							client.send(("Modif_prenom"+ " " + Prenom + " " + ID).encode("utf-8"))
						elif option2 == "6":
							# modifi le mail
							Mail =input ("modif mail: ")
							client.send(("Modif_mail"+ " " + Mail + " " + ID).encode("utf-8"))
						elif option2 == "7":
							# modifi le département
							DEPARTEMENT =input ("modif Modif_departement: ")
							client.send(("Modif_mail"+ " " + DEPARTEMENT + " " + ID).encode("utf-8"))
						elif option2 == "8":
							# quite 
							print ("quiter")
							# informe le serveur qu'on ne veux plus modifier l'user
							client.send(("END").encode("utf-8"))
							break
						else:
							print("\n choix non valide veuillez saisir une option ") 
				elif option=="4":
					# supprimer un user via son id 
					ID = input("ton id: ")
					client.send(("Delete_user"+ " " + ID).encode("utf-8"))
				
				elif option=="5":
					# quiter le script
					print("\n au revoir  ")
					# informe le serveur qu'on ne veux quitter
					client.send(("END").encode("utf-8")) 
					break
				else:
					print("\n choix non valide veuillez saisir une option ") 		



		elif Reponse_droit == "Utilisateur":
			print ("Bienvenu")
			
			while True:
				print ("""
				[1]     .modifier le mot de passe 
				[2]     .message du jour
				[3]     .quitter
				""") 
				option3=input("?")
				
				if option3=="1": 
					# modifi le password de son utilisateur
					t=0
					while True:
						# entrer son password actuelle
						pwd_old = input ("veuillez saisir votre mot de passe actuel  : ")
						# hache le password
						pwd_old_hasher = hashe_password(pwd_old)
						# envoi le mdp au serveur pour qu'il verrifi si il corespond bien a la base de donée
						client.send(("Modif_password"+ " " + pwd_old_hasher + " " + LOGIN).encode("utf-8"))
						# le serveur confirme que le password correspond
						confirme_pwd = reponse_serveur()
						if confirme_pwd == "True":
							p=0
							while True:
								pwd_new = Valide_password()
								print ("confirme mots de passe")
								pwd_new_2= Valide_password()
								if pwd_new in pwd_new_2:
									client.send(("Modif_password"+ " " + pwd_new + " " + LOGIN).encode("utf-8"))
									t=2
									break
								else:
									print ("vous avez pas entrer le meme  pwd ")
								p+=1
								if p== 3:
									break
						elif confirme_pwd == "False":
							print ("mdp invalide")				
						else:
							print ("votre pwd actuel est non valid ")
						t+=1
						if t == 3:
							break
				elif option3=="2":
					print("\n passez une belle journée et gardez toujour le sourrire :)") 
					
				elif option3=="3":
					print("\n au revoir")
					client.send(("END").encode("utf-8")) 
					break
				else:
					print("\n choix non valide veuillez saisir une option ") 
	else :
		print ("Votre mots de passe a expiré veiilez contactez votre administrateur")


print("Connexion fermée")
client.close()