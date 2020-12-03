from .Graph import Graph

#Depth First Search

def depthFirstSearch(graph, startNode):
	g = Graph()
	depthFirstSearchRec(graph, g, startNode)
	return g

def depthFirstSearchRec(graph, tree, startNode, visitedSet = set(), lastNodeVal = -1):
	
	val = tree.append(startNode.getValue())
	if (lastNodeVal > 0):
		tree.addConnection(lastNodeVal, val)
	
	visitedSet = visitedSet + set([startNode]);
	
	for node in startNode.getChildren():
		depthFirstSearch(graph, tree, graph.findNode(node), visitedSet, node)

def findLoop(graph, startNode):
	return findLoopRec(graph, startNode, set(), [])

def findLoopRec(graph, startNode, visitedSet = set(), treeStack = []):
	visitedSet = visitedSet.union({startNode})
	for node in startNode.getParents():
		if not graph.contains(node):
			continue
		if node in treeStack:
			return treeStack[treeStack.index(node):]
		newStack = treeStack.copy()
		newStack.append(node)
		nodeObj = graph.findNode(node)
		res = findLoopRec(graph, nodeObj, visitedSet, newStack)
		if res != None:
			return res
	
	return None