# DRDViz is a powerful graph visualizer graph specifically for
# visualizing searches in a given search space. It it designed to be
# used an an "attached helper" to some sort of graph searching class.
# The overall idea is that you you create an instance of your graph
# searcher object, loading some map file.  You then create yourself an
# instance of the DRDViz class, and load it with the same map file as
# your search class; the new DRDViz is stored in an instance variable
# of your graph searcher object.  Each time your graph searcher does
# something significant e.g. setting start/edge node, exploring a new
# node in the search, or adding new siblings to the OPEN list of the
# search, it simply calls a method on the attached DRDViz to visually
# show the evolving search on the graphical map.

## Usage examples:
# x=DRDViz()  # make yourself a new visualizer
# x.loadGraphFromFile('testfile.txt')  # load it up from a map file
# x.plot()  # make the plot of the road map appear
# x.markStart('A')  # mark starting node A
# x.markGoal('D')   # mark 'D' as a goal node
# x.exploreNode('J',['A','J'])  # mark node 'J' as being currently explored, along with the path to it from A
# x.exploreEdges('G',['C','B'])  # mark the edges coming from parent 'G' and going to children [C, B].
#
# x.reset()  # reset the visualizer, e.g., in preparation for a new search.
#
# ##

__author__ = "Eck Doerry"
__copyright__ = "Copyright 2018, Northern Arizona University, Flagstaff AZ"

import numpy as np
import scipy.spatial as graph
import matplotlib.pyplot as plt
from node import Node
from edge import Edge


### GRAPHVIZ
# This class implements a graph visualizer.  It can plot a graph, then provides methods to mark start/end nodes, and to
# color/re-color nodes and edges in various ways to visualize exploration of the space defined by the graph.
class DRDViz:

    # to create a GraphVisualizer, you first create the blank visualizer (no args taken by INIT).
    # You could then use either loadGraphFromFile() or loadGraphFromObjects() to suck in a map to visualize
    #  and create internal data structures for use in all other operations.
    def __init__(self):
        self.nodes=[]
        self.edges=[]
        self.nodeIndex={}
        self.markedNodes=[]
        self.markedEdges=[]


######   EXTERNAL INTERFACE METHODS   ############
#  The primary methods you call to use this visualizer

    #  Just resets the visualizer.  Easiest to just close the graph and redraw it
    def reset(self):
        self.markedEdges = []
        self.markedNodes = []
        plt.close()
        self.plot()

    def save(self, out):
        plt.savefig(out)

    # A function to load up a graph to visualize. The filename specified by "infile" should contain  a well-formed
    # input file describing the graph. The format is a set of edge descriptions, one line per edge, of following format:
    #    (nodeLabe1, nodeLabel2, edgeLabel, [x1,y1],[x2,y2],[midx,midy])
    # Reads each line and creates the appropriate node/edge objects.
    def loadGraphFromFile(self, infile):
        with open(infile) as f:
            lines = f.readlines()
        cleanlines = [x.strip() for x in lines] #strip off any weird leading or trailing spaces.
        for line in cleanlines:
            line=line.replace('\'','').replace('[','').replace(']','').replace(' ','').strip('()')
            rawEdge=line.split(',') # now just have nice clean comma-separated values. Make it a list
            [l1,l2,label,x1,y1,x2,y2]=rawEdge  # grab all the components of the edge
            if l1 not in self.nodeIndex:
                self.nodeIndex[l1]=(int(x1),int(y1))
                self.nodes.append(Node(int(x1),int(y1),l1))
            if l2 not in self.nodeIndex:
                self.nodeIndex[l2] = (int(x2), int(y2))
                self.nodes.append(Node(int(x2), int(y2), l2))
            # Now build and Edge object for it
            newEdge=Edge((int(x1),int(y1)), (int(x2),int(y2)), int(label))
            newEdge.setLabels(l1,l2)
            self.edges.append(newEdge)
        f.close()

    # Function to ask a loaded graph to plot itself.  If you're not in interactive Python mode, may need to call
    # plot.show() to see it.   Assumes that a graph has been loaded first!
    def plot(self):
        plt.close()  # just in case previous graphs were open!
        plt.ion  # turn on interactive mode.  Not sure if it's critical
        #  first plot the nodes
        plt.plot([x.x for x in self.nodes], [x.y for x in self.nodes], 'ko',
                 color="#BBBCBD")  # plot vertices circles first
        for node in self.nodes:  # now plot the labels
            plt.text(node.x, node.y, node.label, color='b', weight='normal', size="large")
        # Now plot in the edges
        for edge in self.edges:
            plt.plot([edge.x1, edge.x2], [edge.y1, edge.y2], 'b-', color='k', linewidth=0.5)  # make the lines
            plt.text(edge.midx, edge.midy, edge.label, size='small')  # label the edge at its midpoint
        self.paintGraph()


    # Takes in start node label, and repaints that node as start (ie, different node shape and green)
    start_color = 'c' #cyan  https://matplotlib.org/stable/tutorials/colors/colors.html
    def markStart(self,startLabel):
        #self.paintNode(startLabel, self.start_color, weight='bold')  # paint label of start node 
        self.plotVertex(startLabel, 'D', self.start_color)  # give start node a vertex
        self.paintGraph()

    # Takes in end node label, and repaints that node as end (ie, different node shape and red)
    def markGoal(self,goalLabel):
        #self.paintNode(goalLabel, 'r', weight='bold')  # paint label of endnode red
        self.plotVertex(goalLabel, 'D', 'r') # give end node a different label shape/color
        self.paintGraph()  # force a repaint


    # ExploreNode is a major method, called each time a new node is opened for exploration.
    # takes in: the label of the next node to explore, and the path (list of nodelabels) to that node.
    # it uses the latter to highlight the path leading to that node on the graph...could pass it an empty list
    # if you don't want that function.
    #  First it "cleans up" the graph from the last round of exploration:  it unmarks the parent node,
    #  and also unmarked all edges painted in the previous round by exploreEdges() and paintPath()
    # It then resets self.paintedEdges and is ready to start the new cycle by painting the node being
    # explored.
    def exploreNode(self,nodeLabel,nodePath):
        # First clean up.  Unmark highlights nodes/edges from last step
        for edge in self.markedEdges:  # first unmark any edges painted in last steps
            self.paintEdge(edge[0],edge[1],color='k')
        if self.markedNodes:  # if there was a previous node explored, unmark it
            self.paintNode(self.markedNodes[0], color='k')
        self.markedEdges = []
        # Ok, now highlight the newly explored node and its path
        self.paintNode(nodeLabel, color='r')
        self.paintPath(nodePath, color='r')  # mark path to current node in red
        self.markedNodes= [nodeLabel] # add node to explored nodes list
        self.paintGraph()  # force a repaint


    # ExploreEdges extends the explored frontier out from some parent node to its children.
    # take in a parent node label, and a set of children node labels.
    # it first paints all previously explored edges a neutral color, then paints the new
    # edges to highlight them.
    def exploreEdges(self,parentLabel, childLabelList):
        for newDest in childLabelList:
            #print("Painting: "+parentLabel+" to "+newDest)
            self.markedEdges += [(parentLabel,newDest)]  # add the new edge to explored edges
            self.paintEdge(parentLabel,newDest,color='m')  # paint edge to highlight
            self.paintNode(newDest,color='g') # color new dest node as part of frontier
        self.paintGraph()  # to redraw the graph!

    # paintPath takes in a contiguous path of node labels and paints it (default=red).
    def paintPath(self, nodePath, color='r'):
        last = ""
        for node in nodePath:
            if last:
                self.paintEdge(last, node, color=color)
                self.markedEdges += [(last, node)]
                last = node
            else:
                last = node


############    INTERNAL   UTILITY METHODS    ######################
##  Don't really need to call these to use DRDViz.  These methods are called by the External Interface
##  methods listed above to get the job done.
##  Also include various little methods useful for debugging or other purposes.

    # Takes in a node label and color.  If node exists, paint its label that color
    def paintNode(self,nodeLabel,color='r',weight='normal', size='medium'):
        p1=self.nodeLoc(nodeLabel)
        if p1:
            plt.text(p1[0], p1[1], nodeLabel, color=color, size=size, weight=weight)  # repaint the label!
            return 1
        else:
            print("PaintNode: No node labeled "+nodeLabel+" exists.")
            return 0

    # Load a graph given a list of nodes object and a list of edge objects.  Useful convenience when used  in
    #  conjunction with a GraphMaker,  allow you to just grab the Edge objects directly from the GraphMaker, rather
    # than exporting them to a file first and then reloading them with loadGraphFromFile()
    def loadGraphFromObjects(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

    # Useful if some outside object wants to get a list of edges in the visualization.
    # Just returns a big list of edges in form (endlabel,endlabel, edgelabel,[x1,y1],[x2,y2])
    def getSearchSpace(self):
        result = []
        for edge in self.edges:
            result.append((edge.endlabel1, edge.endlabel2, edge.label, edge.p1, edge.p2))
        return result

    #  Just returns a graphed node object based on its label
    def getNodeByLabel(self, nodeLabel):
        for node in self.nodes:
            if node.label == nodeLabel: return node
        print("getNodebyLabel: No node labeled " + nodeLabel + " exists")
        return 0

    # a function that repaints (replots) an edge on the graphical plot
    # take in to node labels and optionally, a color
    def paintEdge(self, startLabel, endLabel, color='r'):
        p1 = self.nodeLoc(startLabel)
        p2 = self.nodeLoc(endLabel)
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=1)  # repaint the edge

    ## Main External interface functions for using a RoadGraph
    def paintGraph(self):
        plt.pause(0.05)

    # Job is to (re)plot a node vertex in different shape/color. Takes in node label, a new vertex shape code,
    # and a new color, and redraws the vertex associated with that node accordingly.
    def plotVertex(self,nodeLabel,mtype,color):
        loc= self.nodeLoc(nodeLabel)
        plt.plot(loc[0],loc[1],color+mtype)




    def nodeLoc(self,label):  # finds and returns the location of node labeled 'label'
        for node in self.nodes:
            if node.label==label: return [node.x,node.y]
        print("nodeLoc: No node with label "+label+" exists")


    #mainly for debugging: Functions to have the graph display its edges and nodes
    def show(self):
        print("Here is the graph:")
        print("Nodes: ")
        print([x.get() for x in self.nodes])
        print("Edges: ")
        print([x.get() for x in self.edges])

    def die(self):    # just kills any open graph
        plt.close()

if __name__ == "__main__":
    x=DRDViz()
    x.loadGraphFromFile("test1.txt")

DRDViz_class = DRDViz
