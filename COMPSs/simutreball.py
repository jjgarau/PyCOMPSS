
from modules.Distribucions import *  
from pycompss.api.task import task
from pycompss.api.parameter import *

def mergeReduce(function, data):
	from collections import deque
	q = deque(xrange(len(data)))
	while len(q):
		x = q.popleft()
		if len(q):
			y = q.popleft()
			data[x] = function(data[x],data[y])
			q.append(x)
		else:
			return data[x]


@task(returns=list)
def meanTask(a,b):
	import numpy as np
	c = []
	for i in range(len(a)):
		c.append(np.mean([a[i],b[i]]))
	return c

# Funcio principal
@task(returns=tuple)
def simular(numSim):

	# Declaram el rellotge
	global rellotge

	# Declaram les variables d'estat (SF i SS)
	global servidors_fisics
	global servidor_software

	# Declaram el temps maxim de simulacio
	global maxim_temps
	
	# Declaram els comptadors estadistics
	global clients_totals # Numero de clients que ha passat per l'entitat durant el dia
	global clients_espera_empleats # Numero de clients que han esperat per ser atesos pels empleats
	global clients_espera_terminal # Numero de clients que han esperat per usar el terminal
	global num_maxim_clients_espera_empleats # Numero maxim de clients que han esperat alhora per ser atesos pels empleats
	global num_maxim_clients_espera_terminal # Numero maxim de clients que han esperat alhora per usar el terminal

	# Declaram unes variables auxiliars que ajuden a calcular els temps d'espera
	global temps_espera_acumulat_empleats
	global temps_espera_acumulat_terminal
	global marker_temps_empleats
	global marker_temps_terminal
	global clients_terminal

	iniciar_variables()

	esdeveniment = obtenir_esdeveniment_proper()
	while not finalitzar_simulacio(esdeveniment):

		# Avanca rellotge
		rellotge = esdeveniment[0]

		# Determina tipus d'esdeveniment
		tipus_esdeveniment = esdeveniment[1]

		# Actualitza l'estat del sistema i la llista de nous esdeveniments, depenent del tipus d'esdeveniment
		if tipus_esdeveniment == "Arriba client":
			esdeveniment_arriba_client()
		elif tipus_esdeveniment == "Empleats despatxen client consultes":
			esdeveniment_acaba_empleats_consultes()
		elif tipus_esdeveniment == "Empleats despatxen client operacions":
			esdeveniment_acaba_empleats_operacions()
		elif tipus_esdeveniment == "Client acaba us terminal":
			esdeveniment_acaba_terminal()

		#Escriu informacio
		#escriure_informacio(servidors_fisics, servidor_software, esdeveniment)

		#Determina el proper event
		esdeveniment = obtenir_esdeveniment_proper()


	# S'ha de tenir en compte els clients que no poden ser atesos per falta de temps pero que han esperat
	if servidor_software > 1:
		temps_espera_acumulat_terminal += (maxim_temps - marker_temps_terminal)*(servidor_software - 1)
	if servidors_fisics > 2:
		temps_espera_acumulat_empleats += (maxim_temps - marker_temps_empleats)*(servidors_fisics - 2)


	# Calculam els temps d'espera mitjans
	if clients_espera_empleats != 0:
		temps_mitja_espera_empleats = float(temps_espera_acumulat_empleats)/clients_totals
	else:
		temps_mitja_espera_empleats = 0
	if clients_espera_terminal != 0:
		temps_mitja_espera_terminal = float(temps_espera_acumulat_terminal)/clients_terminal
	else:
		temps_mitja_espera_terminal = 0


	print(" ")
	print("{} {}".format("RESULTATS DE LA SIMULACIO:",numSim))
	print("--------------------------------------------------")
	print("{}: {}".format("Numero de clients que han passat per l'entitat",clients_totals))
	print("{}: {}".format("Numero de clients que han esperat per ser atesos pels empleats",clients_espera_empleats))
	print("{}: {}".format("Numero de clients que han esperat per usar el terminal",clients_espera_terminal))
	print("{}: {}".format("Numero maxim de clients que han esperat alhora per ser atesos pels empleats",num_maxim_clients_espera_empleats))
	print("{}: {}".format("Numero maxim de clients que han esperat alhora per usar el terminal",num_maxim_clients_espera_terminal))
	print("{}: {} {}".format("Temps mitja d'espera dels clients per ser atesos pels empleats",round(temps_mitja_espera_empleats,2),"min/client"))
	print("{}: {} {}".format("Temps mitja d'espera dels clients per usar el terminal",round(temps_mitja_espera_terminal,2),"min/client"))
	print(" ")
	

	return (clients_totals,clients_espera_empleats,clients_espera_terminal,
		num_maxim_clients_espera_empleats,num_maxim_clients_espera_terminal,
		temps_mitja_espera_empleats,temps_mitja_espera_terminal)


def escriure_informacio(servidors_fisics, servidor_software, esdeveniment):
	print ("Minut {}: {}  -  SF = {}, SS = {}".format(esdeveniment[0],esdeveniment[1],servidors_fisics,servidor_software))


def esdeveniment_arriba_client():
	# comptador
	global rellotge
	global servidors_fisics
	global clients_totals
	global clients_espera_empleats
	global num_maxim_clients_espera_empleats
	global temps_espera_acumulat_empleats
	global marker_temps_empleats

	# Actualitza l'estat del sistema
	servidors_fisics += 1

	# Actualitza comptadors
	clients_totals += 1
	if servidors_fisics > 2:
		clients_espera_empleats += 1
		temps_espera_acumulat_empleats += (servidors_fisics - 3)*(rellotge - marker_temps_empleats)
		if (servidors_fisics - 2) > num_maxim_clients_espera_empleats:
			num_maxim_clients_espera_empleats = servidors_fisics - 2

	# Afegeix nous esdeveniments
	afegir_esdeveniment_arriba_client(rellotge)
	if servidors_fisics <= 2:
		afegir_esdeveniment_acaba_empleats(rellotge)

	# Actualitza les variables auxiliars
	marker_temps_empleats = rellotge


def esdeveniment_acaba_empleats_consultes():
	global rellotge
	global servidors_fisics
	global temps_espera_acumulat_empleats
	global marker_temps_empleats

	# Actualitza l'estat del sistema 
	servidors_fisics -= 1

	# Actualitza comptadors 
	if servidors_fisics >= 2:
		temps_espera_acumulat_empleats += (servidors_fisics - 1)*(rellotge - marker_temps_empleats)

	#Afegerix nous esdeveniments
	if servidors_fisics >= 2:
		afegir_esdeveniment_acaba_empleats(rellotge)

	# Actualitza les variables auxiliars
	marker_temps_empleats = rellotge



def esdeveniment_acaba_empleats_operacions():
	global rellotge
	global servidors_fisics
	global servidor_software
	global clients_espera_terminal
	global num_maxim_clients_espera_terminal
	global temps_espera_acumulat_terminal
	global temps_espera_acumulat_empleats
	global marker_temps_terminal
	global marker_temps_empleats
	global clients_terminal

	# Actualitza l'estat del sistema
	servidors_fisics -= 1
	servidor_software += 1

	# Actualitza comptadors 
	if servidors_fisics >= 2:
		temps_espera_acumulat_empleats += (servidors_fisics - 1)*(rellotge - marker_temps_empleats)
	if servidor_software > 1:
		clients_espera_terminal += 1
		temps_espera_acumulat_terminal += (servidor_software - 2)*(rellotge - marker_temps_terminal)
		if (servidor_software - 1) > num_maxim_clients_espera_terminal:
			num_maxim_clients_espera_terminal = servidor_software - 1

	# Afegeix nous esdeveniments
	if servidors_fisics >= 2:
		afegir_esdeveniment_acaba_empleats(rellotge)
	if servidor_software == 1:
		afegir_esdeveniment_acaba_terminal(rellotge)

	# Actualitza les variables auxiliars
	marker_temps_terminal = rellotge
	marker_temps_empleats = rellotge
	clients_terminal += 1


def esdeveniment_acaba_terminal():
	global rellotge
	global servidor_software
	global temps_espera_acumulat_terminal
	global marker_temps_terminal

	#Actualitza l'estat del sistema
	servidor_software -= 1

	# Actualitza comptadors 
	temps_espera_acumulat_terminal += servidor_software*(rellotge - marker_temps_terminal)

	# Afegeix nous esdeveniments
	if servidor_software >= 1:
		afegir_esdeveniment_acaba_terminal(rellotge)

	# Actualitza les variables auxiliars
	marker_temps_terminal = rellotge


def afegir_esdeveniment_arriba_client(rellotge):
	global llista_esdeveniments

	temps_arribades = (1,2,3,4,5)
	probabilitats = (0.2,0.2,0.3,0.2,0.1)
	temps_arriba_client = bernoulliN(probabilitats,temps_arribades)
	temps_esdeveniment = rellotge + temps_arriba_client
	tipus_esdeveniment = 'Arriba client'

	nou_esdeveniment = temps_esdeveniment, tipus_esdeveniment

	# S'afegeix l'esdeveniment a la llista d'esdeveniments
	llista_esdeveniments += [nou_esdeveniment]


def afegir_esdeveniment_acaba_empleats(rellotge):
	global llista_esdeveniments

	if bernoulli(0.2,0,1) == 0:
		temps_acaba_empleats = uniforme_discreta(2,7)
		tipus_esdeveniment = 'Empleats despatxen client consultes'
	else:
		temps_acaba_empleats = uniforme_discreta(1,4)
		tipus_esdeveniment = 'Empleats despatxen client operacions'
	temps_esdeveniment = rellotge + temps_acaba_empleats
	nou_esdeveniment = temps_esdeveniment, tipus_esdeveniment

	# S'afegeix l'esdeveniment a la llista d'esdeveniments
	llista_esdeveniments += [nou_esdeveniment]



def afegir_esdeveniment_acaba_terminal(rellotge):
	global llista_esdeveniments

	temps_us = (1,2,3,4,5)
	probabilitats = (0.3,0.3,0.2,0.1,0.1)
	temps_terminal = bernoulliN(probabilitats,temps_us)
	temps_esdeveniment = rellotge + temps_terminal
	tipus_esdeveniment = 'Client acaba us terminal'

	nou_esdeveniment = temps_esdeveniment, tipus_esdeveniment

	# S'afegeix l'esdeveniment a la llista d'esdeveniments
	llista_esdeveniments += [nou_esdeveniment]


def iniciar_variables():
	global servidors_fisics
	global servidor_software
	global llista_esdeveniments
	global maxim_temps
	
	global clients_totals
	global clients_espera_terminal
	global clients_espera_empleats
	global num_maxim_clients_espera_terminal
	global num_maxim_clients_espera_empleats

	global temps_espera_acumulat_empleats
	global temps_espera_acumulat_terminal
	global marker_temps_empleats
	global marker_temps_terminal
	global clients_terminal

	temps_inicial = 0

	# Hi ha 2 variables d'estat: SF i SS
	servidors_fisics = 0
	servidor_software = 0
	llista_esdeveniments = []
	afegir_esdeveniment_arriba_client(temps_inicial)

	maxim_temps = 480 # Jornada laboral de 8 hores
	clients_totals = 0
	clients_espera_terminal = 0
	clients_espera_empleats = 0
	num_maxim_clients_espera_empleats = 0
	num_maxim_clients_espera_terminal = 0

	temps_espera_acumulat_empleats = 0
	temps_espera_acumulat_terminal = 0
	marker_temps_empleats = 0
	marker_temps_terminal = 0
	clients_terminal = 0

def finalitzar_simulacio(esdeveniment):
	global maxim_temps
	temps_esdeveniment = esdeveniment[0]

	return (maxim_temps <= temps_esdeveniment)


def obtenir_esdeveniment_proper():
	global llista_esdeveniments
	ordenar_llista_esdeveniments()
	esdeveniment_proper = llista_esdeveniments[0]
	esborrar_esdeveniment_proper()
	return esdeveniment_proper


def esborrar_esdeveniment_proper():
	global llista_esdeveniments
	llista_esdeveniments = llista_esdeveniments[1:]


def ordenar_llista_esdeveniments():
	global llista_esdeveniments
	llista_esdeveniments.sort(key=lambda tup: tup[0])


def startSim(numFrag):
	from pycompss.api.api import compss_wait_on

	X = [simular(i) for i in range(numFrag)]
	resultat = mergeReduce(meanTask,X)
	resultat = compss_wait_on(resultat)
	return resultat



if __name__ == "__main__":
	import sys

	numFrag = int(sys.argv[1])
	resultat = startSim(numFrag)
	print resultat
