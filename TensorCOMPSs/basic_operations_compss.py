from pycompss.api.task import task
from pycompss.api.parameter import *
import tensorflow as tf

@task(returns=float)
def suma(a,b):
	return a+b

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

@task(returns=float)
def computeSums(X):
	# Basic constant operations
	# The value returned by the constructor represents the output
	# of the Constant op.
	a = tf.constant(X[0])
	b = tf.constant(X[1])

	# Launch the default graph.
	with tf.Session() as sess:
	    return sess.run(a+b)


@task(returns=list)
def genFragment():
	from numpy import random
	return [random.random() for _ in range(2)]


def getSum(numFrag):
	from pycompss.api.api import compss_wait_on 
	X = [genFragment() for _ in range(numFrag)]
	sums = [computeSums(X[i]) for i in range(numFrag)]
	result = mergeReduce(suma,sums)
	result = compss_wait_on(result)
	return result

if __name__ == "__main__":
	import sys

	numFrag = int(sys.argv[1])

	result = getSum(numFrag)
	print "The sum is " + str(result)