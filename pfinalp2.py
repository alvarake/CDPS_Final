#!/usr/bin/python  
# -*- coding: utf-8 -*-   

#####################################################################################
#Esta practica ha sido realizada por Carlos Moreno Sanchez y Alvaro Cepeda Zamorano #
#####################################################################################


import sys
import os
import logging
from subprocess import call

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('pfinalp2')

####################################################################################
####################################################################################
								#METODOS#
####################################################################################
####################################################################################


#El metodo glusterconf() se encarga de la configuracion de GlusterFS

def glusterconf():

	logger.debug("Entramos al metodo glusterconf")
	#AÑADIMOS LOS SERVIDORES GLUSTER
	line="sudo lxc-attach --clear-env -n nas1 -- gluster peer probe 10.1.4.22"
	call(line, shell=True)
	line="sudo lxc-attach --clear-env -n nas1 -- gluster peer probe 10.1.4.23"
	call(line, shell=True)

    	#SOLUCION PROPIA AL PROBLEMA GLUSTER. CONSULTADO CON DAVID
	line="sudo lxc-attach --clear-env -n nas2 -- gluster peer probe 10.1.4.21"
	call(line, shell=True)
	line="sudo lxc-attach --clear-env -n nas2 -- gluster peer probe 10.1.4.23"
	call(line, shell=True)
	line="sudo lxc-attach --clear-env -n nas3 -- gluster peer probe 10.1.4.21"
	call(line, shell=True)
	line="sudo lxc-attach --clear-env -n nas3 -- gluster peer probe 10.1.4.22"
	call(line, shell=True)
		############################################################
	#CREAMOS EL VOLUMEN CON LOS TRES SERVIDORES NAS
	line="sudo lxc-attach --clear-env -n nas1 -- gluster volume create nas replica 3 transport tcp 10.1.4.21:/nas 10.1.4.22:/nas 10.1.4.23:/nas force "
	call(line, shell=True)
	#ARRANCAMOS EL VOLUMEN
	line="sudo lxc-attach --clear-env -n nas1 -- gluster volume start nas"
	call(line, shell=True)
	#PARA AGILIZAR LA RECUPERACION DEL VOLUMEN ANTE POSIBLES CAIDAS DE UNO DE LOS SERVIDORES
	line="sudo lxc-attach --clear-env -n nas1 -- gluster volume set nas network.ping-timeout 5"
	call(line, shell=True)
################################################################################################
################################################################################################


#El metodo bbdconf() se encarga de la configuracion de la Base de DATOS

def bbdconf():
	
	logger.debug("Entramos al metodo bbdconf")
	#INSTALAMOS POSTGRESQL
	line="sudo lxc-attach --clear-env -n bbdd --  apt update"
	call(line, shell=True)
	line="sudo lxc-attach --clear-env -n bbdd -- apt -y install postgresql"
	call(line, shell=True)
	#FIJA LA ESCUCHA DE LA BASE DE DATOS PARA ATENDER PETICIONS  EN LA DIRECION 10.1.4.31
	line="sudo lxc-attach -n bbdd -- bash -c \"echo 'listen_addresses='\\\"'10.1.4.31'\\\"'' >> /etc/postgresql/9.6/main/postgresql.conf \""
	call(line, shell=True)
	#AÑADIMOS A LA LISTA DE CONFIANZA TODAS LOS EQUIPOS DE LA LAN 10.1.4.0/24
	line="sudo lxc-attach --clear-env -n bbdd -- bash -c \"echo 'host all all 10.1.4.0/24 trust' >> /etc/postgresql/9.6/main/pg_hba.conf\""
	call(line, shell=True)
	#CONFIGURAMOS LA BASE DE DATOS DANDOLE UN NOMBRE UN USUARIO CON TODOS SUS PRIVILEGIOS Y UNA CONTRASEÑA PARA DICHO USUARIO
	line="sudo lxc-attach --clear-env -n bbdd -- bash -c \"echo 'CREATE USER crm with PASSWORD '\\\"'xxxx'\\\"';' | sudo -u postgres psql \""
	call(line, shell=True)
	line="sudo lxc-attach --clear-env -n bbdd -- bash -c \"echo 'CREATE DATABASE crm;' | sudo -u postgres psql\""
	call(line, shell=True)
	line="sudo lxc-attach --clear-env -n bbdd -- bash -c \"echo 'GRANT ALL PRIVILEGES ON DATABASE crm to crm;' | sudo -u postgres psql\""
	call(line, shell=True)
	#REINICIAMOS LA BASE DE DATOS CON LAS CONFIGURACIONES YA FIJADAS.
	line="sudo lxc-attach --clear-env -n bbdd -- systemctl restart postgresql"
	call(line, shell=True)
################################################################################################
################################################################################################

#El metodo crmconf() se encarga de la instalacion de la aplicacion CRM

def crmconf():

	logger.debug("Entramos al metodo crmconf")
	#PARA TODOS LOS SERVIDORES
	for i in [1,2,3]:
		#INSTALAMOS LOS PAQUETES: GIT, CURL, NODE
		print(str(i)+"\n\n\n")
		line="sudo lxc-attach --clear-env -n s"+str(i)+" -- apt-get update"
		call(line, shell=True)
		line="sudo lxc-attach --clear-env -n s"+str(i)+" -- apt-get install git -y"
		call(line, shell=True)
		line="sudo lxc-attach --clear-env -n s"+str(i)+" -- sudo apt-get install curl -y"
		call(line, shell=True)
		line="sudo lxc-attach --clear-env -n s"+str(i)+" -- bash -c \" curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -; sudo apt-get install nodejs\""
		call(line, shell=True)
		#DESCARGAMOS EL CRM
		line="sudo lxc-attach --clear-env -n s"+str(i)+" -- git clone https://github.com/CORE-UPM/CRM_2017"
		call(line, shell=True)
		#HACEMOS EL NPM INSTALL Y CON LA UTILIDAD FOREVER LO DEJAMOS EN BACKGROUND
		line="sudo lxc-attach --clear-env -n s"+str(i)+" --set-var 'DATABASE_URL=postgres://crm:xxxx@10.1.4.31:5432/crm' -- bash -c \" cd CRM_2017; npm install; npm install forever\""
		call(line, shell=True)
		#CONFIGURAMOS LA CARPETA DE SUBIDAS DE FOTOS
			#CREAMOS LA CARPETA
		line="sudo lxc-attach --clear-env -n s" + str(i) + " -- mkdir CRM_2017/public/uploads"
		call(line, shell=True)
			#LA ASIGNAMOS A LA NAS
		line="sudo lxc-attach --clear-env -n s" + str(i) + " -- mount -t glusterfs 10.1.4.21:/nas CRM_2017/public/uploads"
		call(line, shell=True)

		#SOLO EN EL SERVIDOR 1 HACEMOS EL MIGRATE Y EL SEED_LOCAL
		if i == 1:
			line="sudo lxc-attach --clear-env -n s1 --set-var 'DATABASE_URL=postgres://crm:xxxx@10.1.4.31:5432/crm' -- bash -c \" cd CRM_2017; npm run-script migrate_local; npm run-script seed_local\""
			call(line, shell=True)

		#ARRANCAMOS LA APLICACION EN BACKGROUND
		line="sudo lxc-attach --clear-env -n s"+str(i)+" --set-var 'DATABASE_URL=postgres://crm:xxxx@10.1.4.31:5432/crm' -- bash -c \" cd CRM_2017; ./node_modules/forever/bin/forever start ./bin/www\""
		call(line, shell=True)
################################################################################################
################################################################################################

#El metodo lbconf() se encarga de configurar el LB

def lbconf():
	logger.debug("Entramos al metodo lbconf")
	#ASIGNA AL PUERTO 80 DEL BALANCEADOR LO QUE SE VERIA EN EL 3000 DE LOS SERVIDORES. LA INTERFAZ PARA CONFIGURAR EL BALANCEADOR SE DEJA EN EL PUERTO 8001.
	line="sudo lxc-attach --clear-env -n lb -- bash -c \"xr -dr --server tcp:0:80 --backend 10.1.3.11:3000 --backend 10.1.3.12:3000 --backend 10.1.3.13:3000 --web-interface 0:8001\" &"
	call(line, shell=True)
################################################################################################
################################################################################################

#El metodo fwconf() se encarga de configurar el firewall dado un archivo .fw ya compilado con las normas deseadas

def fwconf():
	logger.debug("Entramos al metodo fwconf")
	#COPIA EL ARCHIVO .FW DENTRO DEL FIREWALL DEL ESCENARIO
	line="sudo cp fw.fw /var/lib/lxc/fw/rootfs/root"
	call(line, shell=True)
	#EJECUTA EL ARCHIVO .FW HACIENDO VIGENTES LAS NORMAS
	line="sudo lxc-attach --clear-env -n fw -- bash -c  /root/fw.fw"
	call(line, shell=True)
################################################################################################
################################################################################################
def arrancar():
	logger.debug("Arrancamos el escenario")
	os.system("sudo vnx -f /home/cdps/pfinal/pfinal.xml --create")

################################################################################################
################################################################################################	
def destruir():
	logger.debug("Destruimos el escenario")
	os.system("sudo vnx -f /home/cdps/pfinal/pfinal.xml --destroy")

################################################################################################
################################################################################################
def total():
	logger.debug("Todas las configuraciones de golpe")
	arrancar()
	glusterconf()
	bbdconf()		
	crmconf()
	lbconf()
	fwconf()

####################################################################################
#ESQUELETO#
####################################################################################
f = sys.argv
tamanoArgumentos = len(f)

if tamanoArgumentos > 1:
	metodo = f[1]
	logger.debug("El argurmento 1 es :"+  str(metodo))
	
	if metodo == "fw-conf":
		fwconf()
	elif metodo == "bdd-conf":
		bbdconf()		
	elif metodo == "gluster-conf":
		glusterconf()
	elif metodo == "crm-conf":
		crmconf()		
	elif metodo == "lb-conf":
		lbconf()

	elif metodo == "arrancar":
		arrancar()

	elif metodo == "total":
		total()

	elif metodo == "destruir":
		destruir()

	elif metodo == "ayuda":
		print("\n\n######## AYUDA #######\n")

		print("* 'python pfinalp2.py' ejecuta diferentes funciones segun la opcion que se añada detras: \n ")
		print("* 'python pfinalp2.py fw-conf' configura el FIREWALL\n")
		print("* 'python pfinalp2.py total' arranca todo el escenario \n ")
		print("* 'python pfinalp2.py bdd-conf' configura la base de datos\n")
		print("* 'python pfinalp2.py gluster-conf' configura el GLUSTER\n")
		print("* 'python pfinalp2.py lb-conf' configura el BALANCEADOR\n")
		print("* 'python pfinalp2.py crm-conf' configura el CRM\n")
		print("\n######## FIN DE LA AYUDA #######\n\n")
		
	else:
		print "Las opciones son erroneas. Introduzca 'python pfinalp2.py ayuda' para mas informacion"
