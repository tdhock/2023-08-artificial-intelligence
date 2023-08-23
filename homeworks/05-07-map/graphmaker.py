
## INTRO.   Purpose of the GraphMaker class is to generate random graphs; these graphs can then also be edited, adding
# or deleting edges while visually inspecting the evolving map.  This makes it quick and easy to create custom "road
# networks" to use as search spaces for developing and visualizing the behavior of searching algorithms.
#
#  You ask it to create a graph, you can optionally ask it to
# plot that graph for you for visual verification purposes.  You can then edit the graph as desired, quickly adding
# or deleting edge.   Finall, you can export that graph as a simple text file of Edges
# for use in other programs.
#
# The class has multiple parameters that you can set to fine tune the nature of the graphs produced.  For now, these are
# just set by editing the values in the __init__ function below. For instance,
# you can specify edge distance distortion, percentage of edges to drop (to make sparse graphs), min. distance between
# nodes generated, etc. See comments in the init function below
#
## Usage examples:
##  x=GraphMaker(20)    # create a new random 20 node map.
#
#   x.plot()  # now graphically show it
#   x.edit()  # enter edit mode.  It repeatedly asks you to add/delete edges.
#   x.export('outfile')   # exports the current map to the file "outfile.txt" in the working dir

# TO-DO: implement a load-graph-from-file to *reload* a graph after saving...in case you want to edit and re-save

__author__ = "Eck Doerry"
__copyright__ = "Copyright 2018, Northern Arizona University, Flagstaff AZ"


import numpy as np
import scipy.spatial as graph
import matplotlib.pyplot as plt
from node import Node
from edge import Edge

class GraphMaker:

    def __init__(self,nodeCount=10):
        self.numNodes=nodeCount  # number of nodes to create in graph.  
        self.expansion=2  # how wide the graph will be. Basically a factor that increases the x-y extents of plane
        self.mindist = 0.3 * self.expansion  # the minimum separation distance between nodes.  Prevents cluttered graphs
        # distDistortion.  Often you might want to have a graph where the distances are *based on* the actual
        # distances, but not exactly that.  distDistortion is a percentage within which the cartesian distances
        # between points will be randomly distorted while labeling the new edges in the graph.  So at 0.3, 30% of the
        # distance will be randomly distorted between 0 and 100%.  So you could lose/gain 30% distance, randomly.
        self.distDistortion = 0.5  # usually 0.3 is nice
        # edgeLoss: in a roadmap, we don't want edges between EVERY point to EVERY other point.  Hence we randomly drop some edges
        # the edgeLoss specifies the percentage of edges we should randomly drop
        self.edgeLoss= 0.1
        self.nodes=[] # array of node objects in this graph
        self.edges=[] # array of edges in this graph
        self.buildGraph()  # Build the new graph!  Commented out.  Call it separately after creation!

    # if you don't like the graph generated, just try another one!
    def redo(self,numNodes=-1):
        self.edges=[]
        self.nodes=[]
        if numNodes>0: self.numNodes=numNodes
        plt.close()
        self.buildGraph()
        self.plot()

    # Lets you interactively edit a graph to whack out edges
    def edit(self):
        entry=""
        print("Edit Mode:  {k/b}a,b to kill/build an edge between a,b ;  r to replot, q to quit")
        while True:
            plt.pause(0.05)
            entry=input("What now?")
            entry = entry.strip()
            if entry=='r':
                self.replot()
            elif entry=='q': break
            else:
                command=entry[0]
                [start,end]=entry[1:].split(',')
                if command=='b': self.buildEdge(start,end)
                else: self.whackEdge(start,end)
        print("End Edit mode")


    # This method lets one whack out edges.  So you can edit away edges after you generate the graph!
    def whackEdge(self,node1,node2):
        node1=node1.upper()
        node2=node2.upper()
        newEdges=[]
        for edge in self.edges:
            if edge.connects(node1,node2):  # whack the edge
                plt.plot([edge.x1, edge.x2], [edge.y1, edge.y2], 'b-', color='w', linewidth=0.5)  # make the lines
                plt.text(edge.midx, edge.midy, edge.label, size='x-small', color='w')  # label the edge at its midpoint
                plt.pause(0.05)
            else: newEdges.append(edge)
        self.edges=newEdges

    def buildEdge(self,node1,node2):
        node1 = node1.upper()
        node2 = node2.upper()
        for edge in self.edges:  # avoid building redundant new edges!
            if edge.connects(node1,node2):
                print("already an edge  from "+node1+" to "+node2)
                return
        p1=self.nodeLocation(node1)
        p2=self.nodeLocation(node2)
        if p1!=0 and p2!=0:    # both nodes exist
            print("building edge!")
            edge=Edge(p1,p2, self.distDistortion)  # make a new edge
            edge.setLabels(node1,node2)
            self.edges.append(edge)
            plt.plot([edge.x1, edge.x2], [edge.y1, edge.y2], 'b-', color='k', linewidth=0.5)  # make the lines
            plt.text(edge.midx, edge.midy, edge.label, size='x-small',color='k')  # label the edge at its midpoint
        else: print("start or end node doesn't exist")


    # Just kill and redraw the plot.  Useful after you've edited the graph
    def replot(self):
        plt.close()
        self.plot()
        plt.show()


    # MAIN WORKER:  Does the actual work of building a Roadmap.
    # The biggest challenge here is linking the given points with a *non-intersecting* set of edges.  In other words,
    # we would like a "planar graph" imposed on these points. This is what Delauney function gives us:  it basically
    # finds non-overlapping triangles that cover all points; any one point is often a vertex in multiple triagles of
    # the "puzzle" of triangles produced.  We then need to extract unique edges and the nodes from this.
    def buildGraph(self):
        pointsArray = self.genPoints()  # makes the array of (x,y) points to connect
        tri=graph.Delaunay(pointsArray)  # creates a planar graph on the given points. Creates a tri data structure.
        triangles=pointsArray[tri.simplices]  # list of triplets of three points. Each set of three points marks a
        # triangle laid out by Delauney.  Next need to extract the edges (point-to-point connections) from this.
        # Now extract the unique edges from all the triangles to generate all edges in the graph
        self.makeEdges(triangles)  # populates self.edges with Edge objects
        # Finally, turn the points array into actual Node objects.
        Node.reset(Node)  # Starts Node labeling at 'A'
        self.nodes=list(map(Node,pointsArray[:,0], pointsArray[:,1]))  #populates self.nodes with Node objects
        self.labelEdges()  # Just to make edge objects complete, go back and add endlabel (nodelabels) to those objects


    #  Makes all the edges in the new graph, based on the array of tris (basically triagles) produced by Delauney and
    # pass in.  Appends the new edges to the "edges" array.
    def makeEdges(self,triArray):
        edges = []  # temp array holding unique ((x,y),(x1,y1)) edge segments found so far

        # an important helper. When we extract a new edges from a triagle, it might well be the duplicate
        # of an edge from an adjacent triangle created by Delauney.
        def checkAddAdj(adjs):
            for adj in adjs:
                if (adj in edges) or ((adj[1], adj[0]) in edges):  # if edges already in there, skip it
                    continue
                else:
                    edges.append((adj[0], adj[1]))
        # go through the triangle array, extract each edge, check that we don't have it already, and add to edges.
        for triplet in triArray:
            s = list(map(list,triplet))
            adjs = [(s[0], s[1]), (s[1], s[2]), (s[2], s[0])]  # extracting the arcs between the points
            checkAddAdj(adjs)

        # okay, now edges array contains all unique edge segment.  Now make edge objects out of them!
        # use edgeLoss value to randomly drop some pct of Edges
        for edge in edges:
            if (np.random.rand() > self.edgeLoss):
                self.edges.append(Edge(edge[0],edge[1],self.distDistortion))  #make Edge object
            else: print("blip")

    # For each edge, finds the label for its endpoints in the nodes, and adds to edge object.
    def labelEdges(self):
        for edge in self.edges:
            edge.endlabel1=self.getNodeAtXY(edge.p1).label
            edge.endlabel2=self.getNodeAtXY(edge.p2).label

    # Function to ask the roadgraph to plot itself.  If not interactive, need to call plot.show() to see it.
    def plot(self):
        plt.ion # turn on interactive mode.  Not sure if it's critical
        #  first plot the nodes
        plt.plot([x.x for x in self.nodes], [x.y for x in self.nodes], 'ko', color="#BBBCBD")  # plot vertices circles first
        for node in self.nodes:  # now plot the labels
            plt.text(node.x, node.y, node.label, color='b', size='large', weight='normal')
        # Now plot in the edges
        for edge in self.edges:
            plt.plot([edge.x1,edge.x2],[edge.y1,edge.y2], 'b-', color='k', linewidth=0.5) # make the lines
            plt.text(edge.midx,edge.midy,edge.label, size='x-small')  # label the edge at its midpoint



    # Function to return the roadgraph as simple list that can be fed to search program.
    # prints it out, one line per edge.  Format (nodeLabel1, nodeLabel2, edgeLabel, ((x1,y1),(x2,y2),(midx,midy)) )
    # if you pass it a text string, it will print to that, else prints to console
    def export(self,outfile=0):
        if outfile != 0:
            outfilename=outfile+".txt"
            out=open(outfilename,'w')
        for edge in self.edges:
            theEdge=((self.getNodeAtXY(edge.p1).label,self.getNodeAtXY(edge.p2).label,edge.label))
            locInfo=((edge.p1,edge.p2))
            if outfile:
                out.write(str(theEdge+locInfo)+"\n")
            else:
                print(theEdge+locInfo)
        if outfile: out.close()
        print("tada!")


    # Returns a node that is located at a given point
    def getNodeAtXY(self,aPoint):  # gets the Node at location x-y of point
        for node in self.nodes:
            if (node.x==aPoint[0]) and (node.y==aPoint[1]): return node
        return 0

    # Just returns x-y location of a node, given its label
    def nodeLocation(self,label):  # finds and returns the location of node labeled 'label'
        for node in self.nodes:
            if node.label==label: return [node.x,node.y]
        print("nodeLoc: No node with label "+label+" exists")

    # a key function.  Generates a random set of points that are some minimum distance apart.
    def genPoints(self):
        # While you still need points, generate random points, add to set if min dist from all currently found points.
        points = []  # An array to put your points in as you find them.
        found = 0  # Tracks points found so far

        # Simple function that checks that candidate points are some min dist from all other points.
        # keeps it from making cluttered graphs!
        def checkpt(apoint, allpoints):
            for point in allpoints:
                dst = graph.distance.euclidean(point, apoint)
                if (dst < self.mindist): return False
            return True

        while found < self.numNodes:
            p1 = self.expansion * np.random.randn(2)
            if checkpt(p1, points):
                points.append(p1)
                found = found + 1
                # print("found one:"+str(found))
            if len(points) == 0: points.append(p1)

        # Now just turn the points into a numpy array
        pArray = np.array(points)
        # print(points)

        # AWESOME.  Now shift all the points into the positive x-y quadrant
        xmin = min(pArray[:, [0]])[0]
        ymin = min(pArray[:, [1]])[0]
        xshift = abs(xmin) + 1
        yshift = abs(ymin) + 1
        posArray = pArray + [xshift, yshift]
        posArray = posArray.astype(int)  # truncate the entire array of points into integer values. Easier!
        return posArray


    #mainly for debugging: Functions to have the graph display its edges and nodes
    def show(self):
        print("Here is the graph:")
        print("Nodes: ")
        print([x.get() for x in self.nodes])
        print("Edges: ")
        print([x.get() for x in self.edges])

    def die(self):    # just kills any open graph
        plt.close()

### UNIT TESTING
if __name__ == "__main__":
    import sys
    x=GraphMaker(sys.argv[1])
    x.export(sys.argv[2])
