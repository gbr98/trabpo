#import gurobipy as gb
import numpy as np
from itertools import permutations
#from utils import *
#from igraph import *

def main():

	instanceFileName = 'exemple'
	nTerminalNodes = 5

	# Carregar estrutura do grafo
	#g = read_graph(instanceFileName)
	# ---

	perm = list(permutations(np.linspace(1,nTerminalNodes,nTerminalNodes)))
	base = fam = np.linspace(1,nTerminalNodes,nTerminalNodes)

	for i in range(len(perm)):
		# Para cada família laminar, deve-se gerar e resolver
		# um modelo de programação linear

		# Toma família laminar
		
		# ---
		a = 5
		#model = gb.Model('delivery')

		
main()