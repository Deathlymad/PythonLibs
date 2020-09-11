
class AbstractGraph():
	def findNode(self, id):
		raise NotImplementedError()
		
	def isID(id):			#verify against graph
		if (not isinstance(id, int)):
			return False
		elif (id < 0):
			return False
		else:
			return True;
	

class GraphObj():
	def __init__(self, owner, id, value, parents, children):
		#Graph owner
		if (isinstance(owner, AbstractGraph)):
			self.owner = owner;
		else:
			raise TypeError("Owner is not a valid Graph Object.");
		
		#ID
		if (AbstractGraph.isID(id)):
			self.id = id;
		else:
			raise TypeError("Invalid Graph Object ID.");
		
		#Value
		self.val = value;
		
		self.parents = []
		self.children = []
		
		#parents
		for p in parents:
			if (AbstractGraph.isID(p)):
				self.parents.append(p);
				owner.findNode(p).appendChild(self.id)
			else:
				print("WARNING! Invalid parent ID for graph object. Ignoring.");
		
		#children
		for p in children:
			if (AbstractGraph.isID(p)):
				self.children.append(p);
				owner.findNode(p).appendParent(self.id)
			else:
				print("WARNING! Invalid child ID for graph object. Ignoring.");
		
		
	def getGraph(self):
		return self.owner
		
	def getValue(self):
		return self.val;
	def setValue(self, val):
		self.val = val
	
	def getID(self):
		return self.id;
	
	def getParents(self):
		return self.parents
	
	def getChildren(self):
		return self.children
	
	def appendParent(self, id):
		if (AbstractGraph.isID(id)):
			self.parents.append(id);
		else:
			raise ValueError("Not a valid Graph ID.")
	
	def appendChild(self, id):
		if (AbstractGraph.isID(id)):
			self.children.append(id);
		else:
			raise ValueError("Not a valid Graph ID.")
	
	

class Graph(AbstractGraph):
	def __init__(self):
		AbstractGraph.__init__(self)
		self.nodes = []
		self.IDCtr = 0;
		
	def append(self, value):
		val = self.IDCtr
		self.IDCtr = self.IDCtr + 1
		node = GraphObj(self, val, value, [], []);
		self.nodes.append(node)
		return val
	
	def getNodes(self):
		return self.nodes
	
	def getLeaves(self):
		return [n for n in self.nodes if len(n.getChildren()) == 0]
	
	def findNode(self, id):
		if (len(self.nodes) == 0):
			raise ValueError("Empty node list.");
		if ((not AbstractGraph.isID(id)) or (id > self.nodes[len(self.nodes) - 1].getID())):
			raise ValueError("Bad ID.");
		
		node = self.__findNodeRec(id, 0, len(self.nodes))
		
		
		if (node.getID() != id):
			raise KeyError("ID is not stored in this graph.")
		if (node.getGraph() != self):
			raise RuntimeError("This node doesn't belong to this graph.")
		return node
		
	def __findNodeRec(self, id, start, end):
		range = end - start
		
		if (range == 0):
			return self.nodes[start];
		elif (id <= self.nodes[start + (range >> 1)].getID()):
			return Graph.__findNodeRec(self, id, start, start + (range >> 1));
		else:
			return Graph.__findNodeRec(self, id, start + (range >> 1) + (range & 1), end);
	
	def addConnection(self, parent, child):
		if (len(self.nodes) == 0):
			raise ValueError("Empty node list.");
		if ((not AbstractGraph.isID(parent)) or (parent > self.nodes[len(self.nodes) - 1].getID())):
			raise ValueError("Bad parent ID.");
		if ((not AbstractGraph.isID(child)) or (child > self.nodes[len(self.nodes) - 1].getID())):
			raise ValueError("Bad child ID.");
		
		parentNode = self.findNode(parent);
		childNode = self.findNode(child);
		
		parentNode.appendChild(childNode.getID())
		childNode.appendParent(parentNode.getID())
	
	#add propagate function
	
	def deleteConnection(self, parent, child):
		if (len(self.nodes) == 0):
			raise ValueError("Empty node list.");
		if ((not AbstractGraph.isID(parent)) or (parent > self.nodes[len(self.nodes) - 1].getID())):
			raise ValueError("Bad parent ID.");
		if ((not AbstractGraph.isID(child)) or (child > self.nodes[len(self.nodes) - 1].getID())):
			raise ValueError("Bad child ID.");
		
		parentNode = self.findNode(parent);
		childNode = self.findNode(child);
		
		parentNode.getChildren().remove(child)
		childNode.getParents().remove(parent)
	
	def deleteNode(self, id):
		if (len(self.nodes) == 0):
			raise ValueError("Empty node list.");
		if ((not AbstractGraph.isID(id)) or (id > self.nodes[len(self.nodes) - 1].getID())):
			raise ValueError("Bad ID.");
		
		node = self.findNode(id);
		
		for parent in node.getParents():
			self.deleteConnection(parent, node.getID())
		for child in node.getChildren():
			self.deleteConnection(node.getID(), child)
		
		self.nodes.remove(node)


if __name__ == "__main__": #test
	g = Graph()
	
	val1 = g.append(1)
	val2 = g.append(2)
	val3 = g.append(3)
	
	g.addConnection(val1, val2)
	g.addConnection(val2, val3)
	g.addConnection(val3, val1)
	
	g.deleteConnection(val2, val3)
	
	g.deleteNode(val1)

