#!/usr/bin/python  
# -*- coding: utf-8 -*-   

####################################################################################
#Esta practica ha sido realizada por Carlos Moreno Sanchez y Alvaro Cepeda Zamorano#
####################################################################################


import sys
import os
import logging
from lxml import etree

#####  DEBUG ######	
logging.basicConfig(level=logging.INFO) #Cambiando DEBUG por INFO se ven los mensajes 
logger = logging.getLogger('pfinalp1')

################################################################################################
################################################################################################

#####  Numero de servidores creados en el entorno ######
def numeroservidores():
	logging.basicConfig(level=logging.INFO)
	logger.debug("++++++++Metodo numeroservidores: Entrar" )
	f = open ('nmaquina.txt','r')
	numeroserv = int(f.read())
	f.close()
	logger.debug("++++++++Metodo numeroservidores: El documento tiene : " + str(numeroserv)+ " servidores" )	
	logger.debug("++++++++Metodo numeroservidores: Salir" )
	logging.basicConfig(level=logging.INFO)			
	return  numeroserv

################################################################################################
################################################################################################

#####  CONFIGURAMOS los servidores ######	
def modificaServ(s):		
	#####  CONFIGURAMOS XML ######			
	logging.basicConfig(level=logging.INFO)
	logger.debug("++++++++Metodo modificaServ: Entrar")
	
		##### Cogemos la raiz del archivo xml ######
	tree = etree.parse("s"+str(s)+".xml")
	root = tree.getroot()

		#####  Cambiamos el nombre ######	
	name = root.find("name")
	name.text = "s" +str(s)
	
		#####  Cambiamos el source file ######	
	source = root.find("./devices/disk/source")
	logger.debug("++++++++Metodo modificaServ: Valor inicial del source: "+ source.get("file"))
	rutaServidores =os.getcwd()
	source.set("file",rutaServidores+"/s"+ str(s)+".qcow2")
	logger.debug("++++++++Metodo modificaServ: Valor final del source: "+ source.get("file"))

		#####  Cambiamos el source bridge ######	
	source = root.find("./devices/interface/source")
	logger.debug("++++++++Metodo modificaServ: Valor inicial del bridge: "+ source.get("bridge"))
	source.set("bridge","LAN2")
	logger.debug("++++++++Metodo modificaServ: Valor final del bridge: "+ source.get("bridge"))

		#####  Abrimos el fichero y lo modificamos ######	
	f = open("s"+str(s)+".xml", 'w') 
	f.write(etree.tostring(tree, pretty_print=True))
	f.close()

	logger.debug("++++++++Metodo modificaServ: Salir")
	logging.basicConfig(level=logging.INFO)


	#####  Cambiamos archivos MVs ######
	os.system("sudo vnx_mount_rootfs -s -r s"+str(s)+".qcow2 mnt")
	
		#####  Configuracion inteface de red######
	f2 = open("mnt/etc/network/interfaces", 'w')
	f2.write("auto lo \niface lo inet loopback \n\nauto eth0 \n\niface eth0 inet static \naddress 10.0.2.1"+str(s)+" \nnetmask 255.255.255.0 \nnetwork 10.0.2.0 \nbroadcast 10.0.2.255 \ngateway 10.0.2.1")
	f2.close()
	
		#####  Configuracion HOSTNAME######
	f3 = open("mnt/etc/hostname", 'w')
	f3.write("s"+str(s)+"\n")
	f3.close()

		#####  Configuracion html######
	os.system("chmod 777 mnt/var/www/html/index.html")
	f9 = open("mnt/var/www/html/index.html", 'w')
	f9.write("s"+str(s)+"\n")
	f9.close()

		#####  Configuracion HOSTS######
	f1 = open("mnt/etc/hosts", 'r').readlines()
	f5 = open("mnt/etc/hosts", 'w')
	for line in f1:
		if "127.0.1.1 cdps cdps" in line:
			f5.write("127.0.1.1 s"+str(s)+"\n")
		else:
			f5.write(line)

	f5.close()
		#####  Guardamos modificaciones ######
	os.system("sudo vnx_mount_rootfs -u mnt")

################################################################################################
################################################################################################

#####  CONFIGURAMOS LB ######		
def modificaLb():			
	logging.basicConfig(level=logging.INFO)
	logger.debug("++++++++Metodo modificaLb: Entrar")
	#####  CONFIGURAMOS XML ######
		##### Añadimos segunda Interfaz ######
	f1 = open("lb.xml", 'r').readlines()
	f2 = open("lb.xml", 'w')
	for line in f1:
		if "</interface>" in line:
			f2.write(line)
			f2.write('<interface type="bridge">\n')
			f2.write('<source bridge="LAN2"/>\n')
			f2.write('<model type="virtio"/>\n')
			f2.write('</interface>\n')
		else:
			f2.write(line)
	f2.close()

		##### Cogemos la raiz del archivo xml ######
	tree = etree.parse("lb.xml")
	root = tree.getroot()

		#####  Cambiamos el nombre ######	
	name = root.find("name")
	name.text = "lb"
	
		#####  Cambiamos el source file ######	
	source = root.find("./devices/disk/source")
	logger.debug("++++++++Metodo modificalb: Valor inicial del source: "+ source.get("file"))	

	rutalb =os.getcwd()
	source.set("file",rutalb + "/lb.qcow2")
	logger.debug("++++++++Metodo modificalb: Valor final del source: "+ source.get("file"))	
	
		#####  Cambiamos el source bridge ######	
	source = root.find("./devices/interface/source")
	logger.debug("++++++++Metodo modificalb: Valor inicial del bridge: " + source.get("bridge"))
	source.set("bridge","LAN1")
	logger.debug("++++++++Metodo modificalb: Valor final del bridge: "+ source.get("bridge"))
	
		#####  Abrimos el fichero y lo modificamos ######	
	f = open("lb.xml", 'w') 
	f.write(etree.tostring(tree, pretty_print=True))
	f.close()

	logger.debug("++++++++Metodo modificaLb: Salir")
	logging.basicConfig(level=logging.INFO)
	

	#####  Cambiamos los archivos de la MV ######
	os.system("sudo vnx_mount_rootfs -s -r lb.qcow2 mnt")
	
		#####  Configuracion inteface de red######
	f2 = open("mnt/etc/network/interfaces", 'w')
	f2.write("auto lo \niface lo inet loopback\n\nauto eth0 \n\niface eth0 inet static \naddress 10.0.1.1 \nnetmask 255.255.255.0 \nnetwork 10.0.1.0 \nbroadcast 10.0.1.255\n\nauto eth1 \n\niface eth1 inet static \naddress 10.0.2.1 \nnetmask 255.255.255.0 \nnetwork 10.0.2.0 \nbroadcast 10.0.2.255")
	f2.close()
	
		#####  Configuracion HOSTNAME######
	f3 = open("mnt/etc/hostname", 'w')
	f3.write("lb\n")
	f3.close()
		#####  Configuracion balanceador como ROUTER######
	f6 = open("mnt/etc/sysctl.conf", 'w')
	f6.write("net.ipv4.ip_forward = 1")
	f6.close()
	os.system("sysctl -p /etc/sysctl.conf")
		#####  Configuracion HOSTS######

	f4 = open("mnt/etc/hosts", 'r').readlines()
	f9 = open("mnt/etc/hosts", 'w')
	for line in f4:
		if "127.0.1.1 cdps cdps" in line:
			f9.write("127.0.1.1 lb")
		else:
			f9.write(line)

	f9.close()

		#####  Mejora Balanceador al Iniciar ######
	
	f7 = open("mnt/etc/rc.local", 'r').readlines()
	f8 = open("mnt/etc/rc.local", 'w')
	for line in f7:
		if "# By default this script does nothing." in line:
			f8.write(line)
			f8.write("#!/usr/bin/python\n")
			f8.write("# -*- coding: utf-8 -*-\n")
			f8.write("service apache2 stop\n\n")
			f8.write("sleep 1\n")
			num = numeroservidores()
			var2 = "sudo xr -dr --server  tcp:0:80 "
			for i in range(1,num+1):
				var1 = "--backend 10.0.2.1"+str(i)+":80 "
				var2 += var1
					
			#f8.write("sudo xr -dr --server  tcp:0:80 --backend  10.0.2.11:80 --backend 10.0.2.12:80 --backend 10.0.2.13:80 --web-interface 0:8001 & \n")
			f8.write(var2+" --web-interface 0:8001 & \n")
		else:
			f8.write(line)

	f8.close()

	#####  Guardamos modificaciones ######
	os.system("sudo vnx_mount_rootfs -u mnt")

################################################################################################
################################################################################################

#####  CONFIGURAMOS C1 ######
def modificaC1():
	#####  CONFIGURAMOS XML ######
	logging.basicConfig(level=logging.INFO)
	logger.debug("++++++++Metodo modificaC1: Iniciar")
	
		##### Cogemos la raiz del archivo xml ######
	tree = etree.parse("c1.xml")
	root = tree.getroot()

		#####  Cambiamos el nombre ######	
	name = root.find("name")
	name.text = "c1"
	
		#####  Cambiamos el source file ######	
	source = root.find("./devices/disk/source")
	logger.debug("++++++++Metodo modificaC1: Valor inicial del source: "+ source.get("file"))
	rutac1 =os.getcwd()
	source.set("file",rutac1 + "/c1.qcow2")
	logger.debug("++++++++Metodo modificaC1: Valor final del source: "+ source.get("file"))
	
		#####  Cambiamos el source bridge ######	
	source = root.find("./devices/interface/source")
	
	logger.debug("++++++++Metodo modificaC1: Valor inicial del bridge: " + source.get("bridge"))
	source.set("bridge","LAN1")
	logger.debug("++++++++Metodo modificaC1: Valor final del bridge: " + source.get("bridge"))
	
		#####  Abrimos el fichero y lo modificamos ######	
	f = open("c1.xml", 'w') 
	f.write(etree.tostring(tree, pretty_print=True))
	f.close()
	logger.debug("++++++++Metodo modificaC1: Salir")
	logging.basicConfig(level=logging.INFO)

	#####  Cambiamos archivos C1 ######
	os.system("sudo vnx_mount_rootfs -s -r c1.qcow2 mnt")
	
		#####  Configuracion inteface de red######
	f2 = open("mnt/etc/network/interfaces", 'w')
	f2.write("auto lo \niface lo inet loopback\n\nauto eth0 \n\niface eth0 inet static \naddress 10.0.1.2 \nnetmask 255.255.255.0 \nnetwork 10.0.1.0 \nbroadcast 10.0.1.255 \ngateway 10.0.1.1")
	f2.close()
	
		#####  Configuracion HOSTNAME######
	f3 = open("mnt/etc/hostname", 'w')
	f3.write("c1\n")
	f3.close()

		#####  Configuracion HOSTS######
	f1 = open("mnt/etc/hosts", 'r').readlines()
	f4 = open("mnt/etc/hosts", 'w')
	for line in f1:
		if "127.0.1.1 cdps cdps" in line:
			f4.write("127.0.1.1 c1")
		else:
			f4.write(line)

	f4.close()

		#####  Guardamos modificaciones ######
	os.system("sudo vnx_mount_rootfs -u mnt")


################################################################################################
################################################################################################
################################################################################################
################################################################################################



#####  Crear el numero de servidores pasados como parametro, el lb y el c1 ######
def crear(s):
	logging.basicConfig(level=logging.INFO)
	logger.debug("++++++++Metodo crear: Has introducido el numero: " + str(s))
	
	#####  Configuracion bridges ######
	logger.debug("++++++++Metodo crear: Se configuran LAN1")
	os.system("sudo brctl addbr LAN1")
	logger.debug("++++++++Metodo crear: Se configura LAN2")
   	os.system("sudo brctl addbr LAN2")
   	os.system("sudo ifconfig LAN1 up")
   	os.system("sudo ifconfig LAN2 up")
	logger.debug("++++++++Metodo crear: Se configuran los bridges")
	
	#####  Creamos el directorio mnt ######

	os.system("mkdir mnt")
	#####  Creamos el archivo con el numero de servidores ######
	f = open ('nmaquina.txt','w')
	f.write(str(s))
	f.close()
	logger.debug("++++++++Metodo crear: Se crea el fichero")

	#####  Creamos las MVs y las configuramos ######
		#####  Servidores ######
	for i in range(1,s+1):
		os.system("qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 s"+str(i)+".qcow2")
		os.system("cp plantilla-vm-p3.xml s"+str(i)+".xml")
		logger.debug("++++++++Metodo crear: Se crea s"+str(i)+".qcow2 y s"+str(i)+".xml")		
		modificaServ(i)
		
    		##### LB ######
    	os.system("qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 lb.qcow2")
	os.system("cp plantilla-vm-p3.xml lb.xml")
	modificaLb()
		##### C1 ######
    	os.system("qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 c1.qcow2")
	os.system("cp plantilla-vm-p3.xml c1.xml")	
	logger.debug("++++++++Metodo crear: Se crea c1.xml, c1.qcow, lb.qcow y lb.xml")
	modificaC1()

	#####  CONFIGURACION HOST ######	
	os.system("sudo ifconfig LAN1 10.0.1.3/24")
	os.system("sudo ip route add 10.0.0.0/16 via 10.0.1.1")

	logger.debug("++++++++Metodo crear: FINAL")
	logging.basicConfig(level=logging.INFO)


################################################################################################
################################################################################################	
	
	
#####  Arrancar las MVs ######
def arrancar(n):
	os.system("sudo virt-manager")
	if n == 0:
		logging.basicConfig(level=logging.INFO)
		logger.debug('++++++++Metodo arrancar: Has entrado al metodo')
	
		#####  Arrancamos c1 ######
		os.system("sudo virsh define c1.xml")
		os.system("sudo virsh start c1")
		os.system("xterm -rv -sb -rightbar -fa monospace -fs 10 -title 'c1' -e 'sudo virsh console c1' &")
	
		#####  Arrancamos lb ######
		os.system("sudo virsh define lb.xml")
		os.system("sudo virsh start lb")
		os.system("xterm -rv -sb -rightbar -fa monospace -fs 10 -title 'lb' -e 'sudo virsh console lb' &")

		#####  Arrancamos Servidores ######
		servidores = numeroservidores()
		for i in range(1,1+servidores):
			#####  Arrancamos maquinas actualizadas ######
			os.system("sudo virsh define s"+str(i)+".xml")
			os.system("sudo virsh start s"+str(i))
			os.system("xterm -rv -sb -rightbar -fa monospace -fs 10 -title 's"+str(i)+"' -e 'sudo virsh console s"+str(i)+"' &")
		logging.basicConfig(level=logging.INFO)

	else:
		
		os.system("sudo virsh define "+n+".xml")
		os.system("sudo virsh start "+n)
		os.system("xterm -rv -sb -rightbar -fa monospace -fs 10 -title '"+n+"' -e 'sudo virsh console "+n+"' &")
	
################################################################################################
################################################################################################

#####  Parar las MVs ######
def parar(n):
	if n == 0:
		logging.basicConfig(level=logging.INFO)
		logger.debug('++++++++Metodo parar: Has entrado al metodo')
	
		#####  Paramos Servidores ######
		servidores = numeroservidores()
		for i in range(1,1+servidores):
			os.system("sudo virsh shutdown s"+str(i))
	
		#####  Paramos lb y c1 ######
		os.system("sudo virsh shutdown lb")
		os.system("sudo virsh shutdown c1")	
		logger.debug('++++++++Metodo parar: Has salido del metodo')
		logging.basicConfig(level=logging.INFO)
	else:
		os.system("sudo virsh shutdown "+n)

################################################################################################
################################################################################################

#####  Destruir las MVs ######
def destruir():	
	logging.basicConfig(level=logging.INFO)
	logger.debug('++++++++Metodo destruir: Has entrado al metodo')
	
	#####  Borramos Archivos de Servidores y destruimos sus MVs ######
	nums = numeroservidores()
	
	for i in range(1, nums+1):
		#os.system("chmod 666 s"+str(i)+".qcow2")
		os.system("rm -f s"+str(i)+".*")
		os.system("sudo virsh undefine s"+str(i))
			
		os.system("sudo virsh destroy s"+str(i))
		
	
	#####  Borramos Archivos de lb y c1, y destruimos sus Mvs ######
	
	os.system("rm -f lb.*")
	
	os.system("sudo virsh undefine lb")
			
	os.system("sudo virsh destroy lb")
		
	os.system("rm -f c1.*")
	
	os.system("sudo virsh undefine c1")
			
	os.system("sudo virsh destroy c1")
	#####  Desconfiguramos LANS ######
	
	os.system("sudo ifconfig LAN1 down")
	os.system("sudo brctl delbr LAN1")
	os.system("sudo ifconfig LAN2 down")
	os.system("sudo brctl delbr LAN2")

	
	os.system("rm nmaquina.txt")
	os.system("rmdir mnt")
	logger.debug('++++++++Metodo destruir: Has borrado nmaquina.txt')
	logger.debug('++++++++Metodo destruir: Se han borrado todo')	
	logging.basicConfig(level=logging.INFO)

################################################################################################
################################################################################################
################################################################################################
################################################################################################


######################################   MAIN   ###################################### 
f = sys.argv
tamanoArgumentos = len(f)
logging.basicConfig(level=logging.INFO)
if tamanoArgumentos > 1:
	metodo = f[1]
	logger.debug("El argurmento 1 es "+  str(metodo))
	logger.debug("El tamaño del argurmento  es " + str(tamanoArgumentos))
	

	if metodo == "crear":
		logger.debug('********Deteccion de argumentos: Entramos en Crear')
		if tamanoArgumentos > 2:
			numero = int(f[2])	
			logger.debug("El argurmento 2 es "+  str(numero))
			if (numero > 5) or (numero < 1):
				logger.debug('********Deteccion de argumentos: Crear: Numero Erroneo')
				print "Solo puedes crear maquinas en un rango del 1 al 5"
			else:
				logger.debug('********Deteccion de argumentos: Crear: Numero entre 1 o 5')
				crear(numero)				
		else:
			logger.debug('********Deteccion de argumentos: Crear: Numero por defecto 2')	
			crear(2)
			
	elif metodo == "arrancar":
		
		if os.path.isfile("nmaquina.txt"):
			if tamanoArgumentos > 2:
				
				mvirtual = str(f[2])	
				logger.debug("El argurmento 2 es "+  mvirtual)
				if os.path.isfile(mvirtual +".qcow2"):

					os.system("sudo virsh list > prueba")
					os.system('grep -c "'+mvirtual+'" prueba > prueba2')
					f2 = open ('prueba2','r')
					cosa = int(f2.read())
					if cosa == 1:
						print(mvirtual+" ya esta arrancada")
						
					else:
						arrancar(mvirtual)

					f2.close()	
		
					os.system("rm -f prueba*")
					
				else:
					print "No exite esta maquina virtual"
									
			else:
				logger.debug('********Deteccion de argumentos: Crear: Numero por defecto 2')	
				arrancar(0)
			
		else:
			print("No hay nada que arrancar. Debes haber creado el entorno primero")

	
	elif metodo == "parar":
		if os.path.isfile("nmaquina.txt"):
			if tamanoArgumentos > 2:
				mvirtual = str(f[2])
	
				logger.debug("El argurmento 2 es "+  mvirtual)
				if os.path.isfile(mvirtual +".qcow2"):

					os.system("sudo virsh list > prueba")
					os.system('grep -c "'+mvirtual+'" prueba > prueba2')
					f2 = open ('prueba2','r')
					cosa = int(f2.read())
					if cosa == 1:
						parar(mvirtual)
					else:
						print(mvirtual+" esta creada, pero su estado es apagada o no inicializada")

					f2.close()
					os.system("rm -f prueba*")						
									
					
				else:
					print "No exite esta maquina virtual"
			else:
				parar(0)
		else:
			print("No hay nada que parar. Debes haber creado el entorno primero")

	elif metodo == "destruir":
		if os.path.isfile("nmaquina.txt"):
			logger.debug('********Deteccion de argumentos: Entramos en Destruir')
			destruir()
		else:
			print("No hay nada que destruir")	
	
	elif metodo == "ayuda":
		print("\n\n######## AYUDA #######\n")
		print("* 'python pfinalp1.py' ejecuta diferentes funciones segun la opcion que se añada detras: \n ")
		print("* 'python pfinalp1.py crear 'n'' crea el entorno de trabajo con n servidores hasta un maximo de 5. Si no se especifica n, se crean 2 servidores\n")
		print("* 'python pfinalp1.py arrancar 'maquina'' arranca la maquina especificada, si no se especifica maquina se arrancaran todas las creadas\n")
		print("* 'python pfinalp1.py parar 'maquina'' para la maquina especificada, si no se especifica maquina se pararan todas las creadas\n")
		print("* 'python pfinalp1.py destruir' destruye el entorno de trabajo borrando todos los ficheros y configuraciones\n")
		print("\n######## FIN DE LA AYUDA #######\n\n")
		


	else:
		print "Las opciones son erroneas. Introduzca 'python pfinalp1.py ayuda' para mas informacion"







