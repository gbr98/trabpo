import gurobipy as gb
import numpy as np

def loadInst(filename):
	print("Loading instance "+filename+"...")

def main():

	# Carregar estrutura do grafo

	# ---

	nTerminalNodes = 5

	for i in range(2**nTerminalNodes):
		# Para cada família laminar, deve-se gerar e resolver
		# um modelo de programação linear

		# Toma família laminar
		
		# ---

		model = gb.Model('delivery')

		
