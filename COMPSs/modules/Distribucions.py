''' 
TREBALL DE SIMULACIO  -   Optimitzacio i Simulacio Q2 2015-2016

Juan Jose Garau
Agusti Oliveras
Gilbert Romani

Grup de classe: 30
Grup de treball: T30_14 

Professor: Ernest Benedito
'''

'''
------  Funcions auxiliars: distribucions de probabilitat  ------
'''



import random


def uniforme_discreta(a,b):
    return int(a + (b+1-a)*random.random())

def bernoulli(p,v1,v2):
    if random.random() < p:
        return v1
    return v2

# La funcio bernoulliN pren com a entrades un array de valors i un array de probabilitats,
# tant en format acumulatiu com individual
def bernoulliN(p,v):
	val = random.random()
	suma = sum(p)
	probs = []
	if suma > 1:
		probs = p
	else:
		acc = 0
		for i in range(0,len(p)):
			acc = acc + p[i]
			probs.append(acc)
	for i in range(0,len(probs)):
		if probs[i] >= val:
			return v[i]