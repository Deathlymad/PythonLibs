from .Graph import Graph
	
def writeRank(file, rank, nodeList):
	file.write("{ rank = same; " + str(rank) + "; ")
	for node in nodeList:
		file.write("\"" + node.replace("-", " ") + "\"; ")
	file.write("}\n")
def writeNode(file, nodeID, color = "black", alias = None):
	if alias:
		file.write(" " + nodeID.replace("-", "") + " [label = \"" + str(alias) + "\", color = \"" + color + "\"];\n");
	else:
		file.write(" " + nodeID.replace("-", "") + " [label = \"" + nodeID.replace("-", " ") + "\", color = \"" + color + "\"];\n");
def writeEdge(file, left, right):
	file.write(" " + left.replace("-", "") + " -> " + right.replace("-", "") + ";\n");

def writeGraphToFile(graph, name):
	if (not isinstance(graph, Graph)):
		raise TypeError("Not a Graph")
	
	
	with open(str(name) + ".dot", "w+") as f:
		f.write("digraph {\n")
		
		edges = []
		
		for node in graph.getNodes():
			if hasattr(node, "getName"):
				writeNode(f, str(node.getID()), alias = str(node.getName()))
			else:
				writeNode(f, str(node.getID()))
			for child in node.getChildren():
				edges.append((node.getID(), child))
			
		for (edgeStart, edgeEnd) in edges:
			writeEdge(f, str(edgeStart), str(edgeEnd))
		#graph stuff
		
		
		f.write("}\n")
		
		


if __name__ == "__main__": #test
	g = Graph()
	
	
	val1 = g.append(1)
	writeGraphToFile(g, "test/test1")
	val2 = g.append(2)
	val3 = g.append(3)
	writeGraphToFile(g, "test/test2")
	
	g.addConnection(val1, val2)
	g.addConnection(val2, val3)
	writeGraphToFile(g, "test/test3")
	g.addConnection(val3, val1)
	
	writeGraphToFile(g, "test/test4")
	g.deleteConnection(val2, val3)
	
	writeGraphToFile(g, "test/test5")
	g.deleteNode(val1)
	writeGraphToFile(g, "test/test6")

