# -*- coding: latin-1 -*-

import gurobipy as gb
import numpy as np
from itertools import permutations
from utils import *
from igraph import *

def main():

	instanceFileName = 'es10fst01.stp'
	nTerminalNodes = 3

	# Carregar estrutura do grafo
	g = read_graph(instanceFileName)
	print(g)
	nEdges = 10
	nVertices = 8
	# ---

	perm = list(permutations(np.linspace(1,nTerminalNodes-1,nTerminalNodes-1)))
	base = list(np.linspace(1,nTerminalNodes,nTerminalNodes).astype(np.int))

	for i in range(len(perm)):
		# Para cada família laminar, deve-se gerar e resolver
		# um modelo de programação linear

		# Toma família laminar
		P = []
		S = [base]
		sliced = [base]
		sliceCounter = nTerminalNodes-1
		for j in range(0,nTerminalNodes-1):
			cutPoint = int(perm[i][j])
			print(cutPoint)
			swap = []
			for s in sliced:
				if cutPoint in s and len(s) > 1:
					cut = s.index(cutPoint)+1
					swap.append(s[:cut])
					swap.append(s[cut:])
					S.append(s[:cut])
					S.append(s[cut:])
					P.append((s[:cut],s[cut:]))
			sliced = swap.copy()
			#print(sliced)
		print(S,P)
		# ---

		model = gb.Model('delivery')

		# Create variables
		f = addVars((nEdges, len(S)), vtype=GRB.BINARY)
		yhat, ybar = addVars((nVertices, len(S)), vtype=GRB.BINARY),addVars((nVertices, len(S)), vtype=GRB.BINARY)
		w = addVars((nVertices, len(P)), vtype=GRB.BINARY)

		# Set objective
	    m.setObjective(, GRB.MINIMIZE)

		'''
		# Create variables
	    x = m.addVar(vtype=GRB.BINARY, name="x")
	    y = m.addVar(vtype=GRB.BINARY, name="y")
	    z = m.addVar(vtype=GRB.BINARY, name="z")

	    # Set objective
	    m.setObjective(x + y + 2 * z, GRB.MAXIMIZE)

	    # Add constraint: x + 2 y + 3 z <= 4
	    m.addConstr(x + 2 * y + 3 * z <= 4, "c0")

	    # Add constraint: x + y >= 1
	    m.addConstr(x + y >= 1, "c1")

	    # Optimize model
	    m.optimize()
		'''
		
main()