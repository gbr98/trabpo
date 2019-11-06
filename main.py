# -*- coding: latin-1 -*-

import time
import csv
import gurobipy as gb
import numpy as np
import scipy as cp
import sys
from itertools import permutations
from itertools import combinations
from datetime import datetime
from utils import *
from igraph import *

def main():

	start_time = time.time()

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
	print(W)
	ex = list(g.es.select(_source=1))
	#for e in ex:
	#	print(e.tuple)

	delta_p = []
	delta_m = []
	for i in range(nVertices):
		delta_p.append([])
		delta_m.append([])
	for i in range(nEdges):
		delta_p[g.es[i].source].append(i)
		delta_m[g.es[i].target].append(i)
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

	#perm = list(permutations(np.linspace(1,nTerminalNodes-1,nTerminalNodes-1)))
	base = list(np.linspace(1,nTerminalNodes,nTerminalNodes).astype(np.int))

	def generateLb(base, part, staged, b):
		print(base, part, staged, b)
		S = []
		P = []
		if len(staged) == 0:
			return [base], [part]
		for s in staged:
			if len(s) > 1:
				for i in range(1,len(s)):
					comb = combinations(s, i)
					for c in comb:
						cp_base = base.copy()
						cp_staged = staged.copy()
						cp_staged.remove(s)
						cp_s = s.copy()
						for k in c:
							cp_s.remove(k)
						cp_base.append(list(c))
						cp_base.append(cp_s)
						if len(c) > 1:
							cp_staged.append(list(c))
						if len(cp_s) > 1:
							cp_staged.append(cp_s)
						cp_part = part.copy()
						cp_part.append((list(c), cp_s))
						S_i, P_i = generateLb(cp_base, cp_part, cp_staged, b)
						for k in range(len(S_i)):
							S.append(S_i[k])
							P.append(P_i[k])
		return S, P


	F, G = generateLb([base], [], [base], len(base))

	bestSolution = None
	bestValue = np.inf
	bestS, bestP = [], []

	for i in range(len(F)):
		print("it:"+str(i))
		# Para cada família laminar, deve-se gerar e resolver
		# um modelo de programação linear

		# Toma família laminar
		'''
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
		'''
		S = F[i]
		P = G[i]
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
					aux1 = list(P[p][0]+P[p][1])
					aux2 = list(S[s])
					aux1.sort()
					aux2.sort()
					if aux1 == aux2:
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
			unitIndex = S.index(list([b]))
			model.addConstr(ybar[terminalNodes[b-1],unitIndex] == 1) #(7)
			for i in range(nVertices):
				if i != terminalNodes[b-1]:
					model.addConstr(ybar[i,unitIndex] == 0) #(8)

		model.presolve()
		model.optimize()

		#bestS = S.copy()
		#bestP = P.copy()
		optW = []
		for i in range(len(P)):
			for j in range(nVertices):
				#print(bestSolution.getVarByName("w["+str(j)+","+str(i)+"]"))
				if model.getVarByName("w["+str(j)+","+str(i)+"]").x == 1:
					optW.append(j)
					break
		totalCost = 0
		for i in range(len(S)):
			for j in range(nEdges):
				if model.getVarByName("f["+str(j)+","+str(i)+"]").x > 0:
					totalCost += W[j]
					print(j,i,"(",g.es[j].source,g.es[j].target,")")

		'''
		print(bestP)
		print(optW)
		print("S="+str(startNode)+" :: T="+str(terminalNodes))
		totalCost = 0
		actS = [[base, startNode]]
		while len(actS) > 0:
			print(actS)
			newActS = actS.copy()
			for s in actS:
				for i in range(len(bestP)):
					print(bestP[i], newActS)
					a = list(bestP[i][0]+bestP[i][1])
					b = list(s[0])
					a.sort()
					b.sort()
					if a == b:
						#print(g.shortest_paths_dijkstra(s[1],optW[i]))
						totalCost += g.shortest_paths_dijkstra(s[1],optW[i],W)[0][0]
						print(s[1],optW[i])
						print(totalCost)
						newActS.remove(s)
						if len(bestP[i][0]) > 1:
							newActS.append([bestP[i][0], optW[i]])
						else:
							totalCost += g.shortest_paths_dijkstra(optW[i],terminalNodes[bestP[i][0][0]-1],W)[0][0]
							print(optW[i],terminalNodes[bestP[i][0][0]-1])
							print(totalCost)
						if len(bestP[i][1]) > 1:
							newActS.append([bestP[i][1], optW[i]])
						else:
							totalCost += g.shortest_paths_dijkstra(optW[i],terminalNodes[bestP[i][1][0]-1],W)[0][0]
							print(optW[i],terminalNodes[bestP[i][1][0]-1])
							print(totalCost)
						break
			actS = newActS.copy()
		'''
		print("Cost:"+str(totalCost))
		if totalCost < bestValue:
			bestValue = totalCost
			bestS = S.copy()
			bestP = P.copy()
			bestSolution = model.copy()
		'''
		if model.objVal < bestValue:
			bestValue = model.objVal
			bestSolution = model.copy()
			bestS = S.copy()
			bestP = P.copy()
		'''
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
	print(bestS, bestP)
	bestSolution.presolve()
	bestSolution.optimize()
	optW = []
	for i in range(len(bestP)):
		for j in range(nVertices):
			#print(bestSolution.getVarByName("w["+str(j)+","+str(i)+"]"))
			if bestSolution.getVarByName("w["+str(j)+","+str(i)+"]").x == 1:
				optW.append(j)
				break
	print(bestP)
	print(optW)
	print("S="+str(startNode)+" :: T="+str(terminalNodes))
	
	totalCost = 0
	for i in range(len(S)):
		for j in range(nEdges):
			if bestSolution.getVarByName("f["+str(j)+","+str(i)+"]").x > 0:
				totalCost += W[j]
				print(j,i,"(",g.es[j].source,g.es[j].target,")")
	print(totalCost)

	totalCost = 0
	actS = [[base, startNode]]
	while len(actS) > 0:
		print(actS)
		newActS = actS.copy()
		for s in actS:
			for i in range(len(bestP)):
				print(bestP[i], newActS)
				a = list(bestP[i][0]+bestP[i][1])
				b = list(s[0])
				a.sort()
				b.sort()
				if a == b:
					#print(g.shortest_paths_dijkstra(s[1],optW[i]))
					totalCost += g.shortest_paths_dijkstra(s[1],optW[i],W)[0][0]
					print(s[1],optW[i])
					print(totalCost)
					newActS.remove(s)
					if len(bestP[i][0]) > 1:
						newActS.append([bestP[i][0], optW[i]])
					else:
						totalCost += g.shortest_paths_dijkstra(optW[i],terminalNodes[bestP[i][0][0]-1],W)[0][0]
						print(optW[i],terminalNodes[bestP[i][0][0]-1])
						print(totalCost)
					if len(bestP[i][1]) > 1:
						newActS.append([bestP[i][1], optW[i]])
					else:
						totalCost += g.shortest_paths_dijkstra(optW[i],terminalNodes[bestP[i][1][0]-1],W)[0][0]
						print(optW[i],terminalNodes[bestP[i][1][0]-1])
						print(totalCost)
					break
		actS = newActS.copy()
	print("Cost:"+str(totalCost))

	#Plotar o gráfico
	#Atenção: não recomendado para grafos grandes
	#g = read_graph("./ES10FST/es10fst01.stp")
	#layout = g.layout("fr")
	#color_dict = {False: "white", True: "grey"}
	#g.vs["color"] = [color_dict[terminal] for terminal in g.vs["terminal"]]
	#plot(g, layout = layout)

	### Printing ###
	file = open("report_"+str(instanceFileName).split('/')[1]+".log", 'w')
	file.write("cost: "+str(bestValue)+'\n')
	file.write("S: "+str(bestS)+'\n')
	file.write("P: "+str(bestP)+'\n')
	f = bestSolution.getVars()
	finalSolution = ""
	for i in range(len(f)):
		if f[i].x != 0:
			finalSolution+=str(f[i].varname)+": "+str(f[i].x)+'\t'
			file.write(str(f[i].varname)+": "+str(f[i].x)+'\n')
	file.close()
	#for i in range(nEdges):
	#	for j in range(len(S)):
	#		print(f[i,j].X)
	model.write('best_model_'+str(instanceFileName).split('/')[1]+'.lp')

	if(str(instanceFileName=="/instances/c01.stp")):
		bestKnownSolutionCost = 85
	elif(str(instanceFileName=="/instances/c06.stp")):
		bestKnownSolutionCost = 55
	elif(str(instanceFileName=="/instances/c11.stp")):
		bestKnownSolutionCost = 32
	elif(str(instanceFileName=="/instances/c16.stp")):
		bestKnownSolutionCost = 11
	elif(str(instanceFileName=="/instances/d01.stp")):
		bestKnownSolutionCost = 106
		
	total_time = time.time()-start_time

	with open('data.csv','a') as data:
		data.write(str(datetime.now())+"\t"+str(instanceFileName)+"\t"+"nVertices = "+str(nVertices)+"\t"+"nEdges = "+str(nEdges)+"\t"+"nTerminalNodes = "+str(nTerminalNodes+1)+"\t"+"Execution time: "+str(total_time)+"s"+"\t"+"Solution: "+str(finalSolution)+"\t"+"Cost: "+str(bestValue)+"\t"+"OptSolution: "+str(bestKnownSolutionCost)+"\n\n\n\n")


main()