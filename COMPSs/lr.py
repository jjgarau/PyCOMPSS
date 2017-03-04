import numpy as np 
from sklearn import datasets, linear_model
import random
from pycompss.api.task import task
from pycompss.api.parameter import *

def mergeReduce(function, data):
	from collections import deque
	q = deque(range(len(data)))
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
	return (a+b)/2


@task(returns=int)
def getPreds(X,Y,numP):
	split = int(numP/5)
	X_train = X[:-split]
	X_test = X[-split:]
	Y_train = Y[:-split]
	Y_test = Y[-split:]

	regr = linear_model.LinearRegression()

	regr.fit(X_train,Y_train)
	res = np.mean((regr.predict(X_test) - Y_test) ** 2)
	return res

def multiply(X,equation):
	res = 0
	for i in range(len(X)):
		res += X[i]*equation[i]
	res += random.uniform(-2.5,2.5)
	return res

@task(returns=list)
def getPoints(X,equation):
	return [multiply(X[i],equation) for i in range(len(X))]


def init_random(size,dim):
	from numpy import random 
	return [100*np.random.rand(dim) for _ in range(size)]


@task(returns=list)
def genFragment(size,dim):
	return init_random(size, dim)


def getScore(numP,dim,numFrag):
	from pycompss.api.api import compss_wait_on
	size = int(numP/numFrag)

	X = [genFragment(size,dim) for _ in range(numFrag)]
	equation = np.random.rand(dim)
	Y = [getPoints(X[i],equation) for i in range(numFrag)]
	scores = [getPreds(X[i],Y[i],size) for i in range(numFrag)]

	print(scores)
	resultat = mergeReduce(meanTask,scores)
	resultat = compss_wait_on(resultat)
	return resultat


if __name__ == "__main__":
	import sys

	numP = int(sys.argv[1])
	dim = int(sys.argv[2])
	numFrag = int(sys.argv[3])

	result = getScore(numP, dim, numFrag)
	print("The average score is ")
	print(result)
	