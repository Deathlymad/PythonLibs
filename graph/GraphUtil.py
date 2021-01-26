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
	return findLoopRec(graph, startNode, [])

def findLoopRec(graph, startNode, treeStack = []):
	treeStack.append(startNode)
	for node in startNode.getParents():
		if not graph.contains(node):
			continue
		idList = [obj.getID() for obj in treeStack]
		if node in idList:
			return [obj.getID() for obj in treeStack[idList.index(node):]]
		newStack = treeStack.copy()
		nodeObj = graph.findNode(node)
		res = findLoopRec(graph, nodeObj, newStack)
		if res != None:
			return res
	
	return None