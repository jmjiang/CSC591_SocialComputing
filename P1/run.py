from snap import *
from csv import *
from operator import itemgetter
import matplotlib.pyplot as plt



"""
Compute the number of nodes,
number of edges,
betweenness centrality, and
clustering co-efficient
for the SNAP Social circles dataset.
Print the results onto the screen.
"""
def calcMeasures():
	# Create the graph G by reading the edges from facebook_combined.txt
	G = LoadEdgeList(PUNGraph, "datasets/facebook_combined.txt", 0, 1)
	f = open('measures.txt', 'wb')
	f.write("Number of Nodes = " + str(G.GetNodes()) + "\n")
	f.write("Number of Edges = " + str(G.GetEdges()) + "\n")

	# Calculate the graph's betweenness centrality, which is the average of the betweenness centralities of all nodes
	nodes = TIntFltH()
	edges = TIntPrFltH()
	GetBetweennessCentr(G, nodes, edges, 1.0)
	egoNodes = [0, 107, 348, 414, 686, 698, 1684, 1912, 3437, 3980]
	f.write("Betweenness Centrality: \n")
	for node in nodes:
		if node in egoNodes:
			f.write("    ego " + str(node) + ": " + str(nodes[node]) + "\n")

	# Calculate the graph's clustering co-efficient
	clusteringCoef = GetClustCf(G, -1)
	f.write("Clustering Co-efficient = " + str(clusteringCoef) + "\n")
	f.close()



"""
Test hypothesis 1: A node with higher degree would belong to more number of circles.
The output for ego nodes 0 and 348 are save in hypo1_ego0.csv and hypo1_ego348.csv, respectively.
"""
def hypo1():
	egoNodes = [0, 348]
	for egoNode in egoNodes:
		# Create a separate graph for the current ego node
		G = LoadEdgeList(PUNGraph, "datasets/facebook/" + str(egoNode) + ".edges", 0, 1)
		G.AddNode(egoNode)
		for node in G.Nodes():
			G.AddEdge(egoNode, node.GetId())

		# Calculate the number of circles each node is in
		circlesNum = {}
		for node in G.Nodes():
			circlesNum[node.GetId()] = 0
		f = open('datasets/facebook/' + str(egoNode) + '.circles', 'r')
		for line in f:
			line = line.split()
			#TODO: the ego node is in every circle?
			# circlesNum[egoNode] = circlesNum[egoNode] + 1
			for word in line:
				if word.isdigit():
					word = int(word)
					if word in circlesNum.keys():
						circlesNum[int(word)] = circlesNum[int(word)] + 1
					else:
						circlesNum[word] = 1

		# Create a list of the output information
		output = []
		for node in G.Nodes():
			output.append((node.GetId(), node.GetDeg(), circlesNum[node.GetId()]))

		# Sort the list of output in decreasing order of number of circles
		sortedOutput = sorted(output, key=itemgetter(2), reverse=True)

		# For each node, write its Id, degree and the number of circles it belongs to into a csvfile.
		with open('hypo1/hypo1_ego' + str(egoNode) + '.csv', 'wb') as csvfile:
			hypo1writer = writer(csvfile, delimiter=',',
					    quotechar='!', quoting=QUOTE_MINIMAL)
			for i in sortedOutput:
				hypo1writer.writerow(i)

		# Plot the output
		# Do not plot the ego node for better looking result.
		degrees = []
		circles = []
		for item in sortedOutput:
			if item[0] != egoNode:
				degrees.append(item[1])
				circles.append(item[2])
		plt.plot(degrees, circles, 'bo')
		plt.xlabel("degree")
		plt.ylabel("number of circles")
		plt.savefig("hypo1/hypo1_ego" + str(egoNode) + ".png")
		plt.clf()	# Clear the previously plotted figure and start a new one



"""
Test Hypothesis 2: A circile with higher density would have a greater degree of intersection of other circles.
"""
def hypo2():
	G = LoadEdgeList(PUNGraph, "datasets/facebook_combined.txt", 0, 1)
	egoNodes = [107, 686]
	for egoNode in egoNodes:
		# Create a dictionary of all the circles in the ego network
		f = open('datasets/facebook/' + str(egoNode) + '.circles', 'r')
		circles = {}
		circlesSnap = {}	# Same as circles but used the TIntSet type for future usage
		for line in f:
			line = line.split()
			circlesSnap[line[0]] = TIntSet()
			circles[line[0]] = []
			for i in range(1, len(line)):
				circlesSnap[line[0]].AddKey(int(line[i]))
				circles[line[0]].append(int(line[i]))
			circlesSnap[line[0]].AddKey(egoNode)	# the ego node is in every circle
			circles[line[0]].append(egoNode)

		output = []

		for c in circlesSnap:
			# Compute the density of the circle
			totalEdges = 0	# Calculate the number of existing edges within the members of circle c
			totalPossibleEdges = 0 	# Calculate the number of possible edges within the members of circle c
			nodes = circlesSnap[c]
			for node in nodes:
				totalEdges = totalEdges + CntEdgesToSet(G, node, nodes)
			totalEdges = totalEdges / 2
			totalPossibleEdges = nodes.Len() * (nodes.Len()-1) / 2
			density = float(totalEdges) / float(totalPossibleEdges)

			# Compute the degree of intersection of c with every other circle
			intersectionDegree = 0		# the sum, instead of average, of all intersection degrees with other circles for simplicity
			nodes2 = circles[c]
			for c2 in circles:
				unionSize = nodes.Len() + len(circles[c2]) - 1	# minus the common existence of the ego node
				intersectionSize = 0
				for node in nodes2:
					if node in circles[c2]:
						intersectionSize = intersectionSize + 1
				intersectionDegree = intersectionDegree + float(intersectionSize) / float(unionSize)
			
			# Save the name, density, degree of intersection of the circle to output
			output.append( (c, density, intersectionDegree) )

		# Sort the list of output in decreasing order of density of circles
		sortedOutput = sorted(output, key=itemgetter(1), reverse=True)

		# Write the output into a csv file
		with open('hypo2/hypo2_ego' + str(egoNode) + '.csv', 'wb') as csvfile:
			hypo2writer = writer(csvfile, delimiter=',',
					    quotechar='!', quoting=QUOTE_MINIMAL)
			for i in sortedOutput:
				hypo2writer.writerow(i)


		# Plot the output
		# Do not plot the ego node for better looking result.
		densities = []
		intersectionDegrees = []
		for item in sortedOutput:
			if item[0] != egoNode:
				densities.append(item[1])
				intersectionDegrees.append(item[2])
		plt.plot(densities, intersectionDegrees, 'bo')
		plt.xlabel("density")
		plt.ylabel("degree of intersection")
		plt.savefig("hypo2/hypo2_ego" + str(egoNode) + ".png")
		plt.clf()



"""
Test hypothesis 3: In a network, nodes with more common circles have more common features as compared to nodes with less common circles.
"""
def hypo3():
	egoNodes = [414, 698]
	for egoNode in egoNodes:
		# Create a separate graph for the current ego node
		G = LoadEdgeList(PUNGraph, "datasets/facebook/" + str(egoNode) + ".edges", 0, 1)

		# Calculate the number of circles each node is in
		circlesNum = {}
		for node in G.Nodes():
			circlesNum[node.GetId()] = 0
		f = open('datasets/facebook/' + str(egoNode) + '.circles', 'r')
		for line in f:
			line = line.split()
			#TODO: the ego node is in every circle?
			# circlesNum[egoNode] = circlesNum[egoNode] + 1
			for word in line:
				if word.isdigit():
					word = int(word)
					if word in circlesNum.keys():
						circlesNum[int(word)] = circlesNum[int(word)] + 1
					else:
						circlesNum[word] = 1

		# Calculate the number of common feature of each user with the ego user
		egoFeatures = []
		f = open('datasets/facebook/' + str(egoNode) + '.egofeat', 'r')
		line = f.readline().split()
		for word in line:
			if word.isdigit():
				egoFeatures.append(int(word))
		commonFeaturesNum = {}
		f = open('datasets/facebook/' + str(egoNode) + '.feat', 'r')
		for line in f:
			line = line.split()
			node = int(line[0])
			commonFeaturesNum[node] = 0
			for i in range(1, len(line)):
				if (int(line[i]) == 1) and (egoFeatures[i-1] == 1):
					commonFeaturesNum[node] = commonFeaturesNum[node] + 1

		# Save the results as a list of tuples
		output = []
		for item in circlesNum:
			if item not in commonFeaturesNum.keys():
				print "Node " + str(item) + "'s common features do not exist"
			else: 
				output.append( (item, circlesNum[item], commonFeaturesNum[item]) )

		# Sort the output in decreasing order of number of circles
		sortedOutput = sorted(output, key=itemgetter(1), reverse=True)

		# Write the output into a csv file
		with open('hypo3/hypo3_ego' + str(egoNode) + '.csv', 'wb') as csvfile:
			hypo3writer = writer(csvfile, delimiter=',',
					    quotechar='!', quoting=QUOTE_MINIMAL)
			for i in sortedOutput:
				hypo3writer.writerow(i)

		# Plot the output
		# Do not plot the ego node for better looking result.
		circles = []
		commonFeat = []
		for item in sortedOutput:
			if item[0] != egoNode:
				circles.append(item[1])
				commonFeat.append(item[2])
		plt.plot(circles, commonFeat, 'bo')
		plt.xlabel("number of circles")
		plt.ylabel("number of common features with ego node")
		plt.savefig("hypo3/hypo3_ego" + str(egoNode) + ".png")
		plt.clf()

	
	

				
if __name__ == "__main__":
	calcMeasures()
	hypo1()
	hypo2()
	hypo3()
