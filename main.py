# -*- coding: latin-1 -*-

import gurobipy as gb
import numpy as np
import sys
from itertools import permutations
from utils import *
from igraph import *
from random import random

def main():

	instanceFileName = str(sys.argv[1])#'es10fst01.stp'

	# Carregar estrutura do grafo
	g = read_graph(instanceFileName).as_directed()
	nEdges = len(g.es)
	print(nEdges)
	nVertices = len(g.vs)
	A = []
	for i in range(nEdges):
		edge = g.es[i].tuple 
		#print(edge)
		#g.add_edge(source=edge[1], target=edge[0], weight=g.es[i]['weight'])
	#nEdges = len(g.es)
	W = list(g.es['weight'])
	#print(W)
	ex = list(g.es.select(_source=1))
	#for e in ex:
	#	print(e.tuple)

	delta_p = []
	delta_m = []
	for i in range(nVertices):
		delta_p.append([])
		delta_m.append([])
	for i in range(nEdges):
		delta_p[g.es[i].source-1].append(i)
		delta_m[g.es[i].target-1].append(i)
	#print(delta_m, delta_p)
	
	# Selecionar terminais
	'''
	remainingNodes = np.linspace(0,nVertices-1,nVertices)
	terminalNodes = []
	startNode = remainingNodes[int(np.floor(random()*nTerminalNodes))]
	remainingNodes = np.delete(remainingNodes, startNode)
	for i in range(nTerminalNodes):
		posNode = int(np.floor(random()*remainingNodes.size))
		terminalNodes.append(remainingNodes[posNode])
		remainingNodes = np.delete(remainingNodes, posNode)
	print(startNode, terminalNodes)
	'''
	terminalNodes = []
	startNode = None
	for i in range(nVertices):
		if g.vs[i]["terminal"] == True:
			if startNode == None:
				startNode = i
			else:
				terminalNodes.append(i)
	nTerminalNodes = len(terminalNodes)
	print(startNode, terminalNodes)
	'''
	print(nVertices, nEdges)
	for i in range(nVertices):
		line = ""
		for j in range(nVertices):
			line += str(g[i,j])+" "
		print(line)
	'''
	# ---

	perm = list(permutations(np.linspace(1,nTerminalNodes-1,nTerminalNodes-1)))
	base = list(np.linspace(1,nTerminalNodes,nTerminalNodes).astype(np.int))

	bestSolution = None
	bestValue = np.inf
	bestS, bestP = [], []

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
			#print(cutPoint)
			swap = sliced.copy()
			for s in sliced:
				if cutPoint in s and len(s) > 1:
					cut = s.index(cutPoint)+1
					swap.append(s[:cut])
					swap.append(s[cut:])
					swap.remove(s)
					S.append(s[:cut])
					S.append(s[cut:])
					P.append((s[:cut],s[cut:]))
			sliced = swap.copy()
			print(sliced)
		print(S,P)
		# ---

		model = gb.Model('delivery')

		# Create variables
		f = model.addVars(nEdges, len(S), vtype=gb.GRB.BINARY, name="f")
		yhat, ybar = model.addVars(nVertices, len(S), vtype=gb.GRB.BINARY, name="yhat"),model.addVars(nVertices, len(S), vtype=gb.GRB.BINARY, name="ybar")
		w = model.addVars(nVertices, len(P), vtype=gb.GRB.BINARY, name="w")

		# Set objective
		model.setObjective(sum(W[edge]*f.sum(edge,'*') for edge in range(len(W))), gb.GRB.MINIMIZE)

	    # Add Constrainsts
		for i in range(nVertices):
			for s in range(len(S)):
				model.addConstr(f.sum(delta_p[i],s)-f.sum(delta_m[i],s) == yhat[i,s]-ybar[i,s]) #(1)
		for s in range(len(S)):
			if len(S[s]) >= 2:
				for p in range(len(P)):
					if list(P[p][0]+P[p][1]) == list(S[s]):
						for i in range(nVertices):
							model.addConstr(w[i,p] == ybar[i,s]) #(2)
		for p in range(len(P)):
			for s in P[p]:
				index_s = S.index(s)
				for i in range(nVertices):
					model.addConstr(w[i,p] == yhat[i,index_s]) #(3)
		for p in range(len(P)):
			model.addConstr(w.sum('*',p) == 1) #(4)

		model.addConstr(yhat[startNode,0] == 1) #(5)

		for i in range(nVertices):
			if i != startNode:
				model.addConstr(yhat[i,0] == 0) #(6)

		for b in base:
			unitIndex = S.index([b])
			model.addConstr(ybar[terminalNodes[b-1],unitIndex] == 1) #(7)
			for i in range(nVertices):
				if i != terminalNodes[b-1]:
					model.addConstr(ybar[i,unitIndex] == 0) #(8)

		model.optimize()

		if model.objVal < bestValue:
			bestValue = model.objVal
			bestSolution = model.copy()
			bestS = S.copy()
			bestP = P.copy()
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
	print(bestValue)
	bestSolution.optimize()
	file = open("report_"+str(instanceFileName).split('/')[1]+".log", 'w')
	file.write("cost: "+str(bestValue))
	file.write("S: "+str(bestS))
	file.write("P: "+str(bestP))
	f = bestSolution.getVars()
	for i in range(len(f)):
		if f[i].x != 0:
			file.write(f[i].varname,f[i].x)
	file.close()
	#for i in range(nEdges):
	#	for j in range(len(S)):
	#		print(f[i,j].X)
	model.write('best_model_'+str(instanceFileName).split('/')[1]+'.lp')
		
main()