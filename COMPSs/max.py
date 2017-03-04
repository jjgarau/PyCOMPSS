from pycompss.api.task import task
from pycompss.api.parameter import *
import random

@task(returns=int)
def maxFinal(a,b):
	return max(a,b)

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

@task(returns=int)
def computeMaximum(X):
	import numpy as np 
	maximum = np.linalg.norm(X[0])
	for i in range(len(X)):
		if np.linalg.norm(X[i]) > maximum:
			maximum = np.linalg.norm(X[i])
	return maximum


def init_random(size, dim):
	from numpy import random
	return [10000*random.random(dim) for _ in range(size)]


@task(returns=list)
def genFragment(size,dim):
	return init_random(size,dim)


def getMaximum(numP,dim,numFrag):
	from pycompss.api.api import compss_wait_on
	import time
	import numpy as np

	size = int(numP/numFrag)

	X = [genFragment(size,dim) for _ in range(numFrag)]
	maxs = [computeMaximum(X[i]) for i in range(numFrag)]
	result = mergeReduce(maxFinal,maxs)
	result = compss_wait_on(result)
	return result


if __name__ == "__main__":
	import sys 
	import time

	numP = int(sys.argv[1])
	dim = int(sys.argv[2])
	numFrag = int(sys.argv[3])

	startTime = time.time()
	result = getMaximum(numP,dim,numFrag)
	print "The maximum norm is %f" % result
	print "Ellapsed Time {} (s)".format(time.time() - startTime)