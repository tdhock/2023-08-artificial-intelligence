# Define Searcher class here.

# 10test.txt map
x=Searcher("10test.txt", searchType="DEPTH", verbose=True)
x.setStartGoal('h','k')
x.search()

x=Searcher("10test.txt", searchType="BREADTH", verbose=True)
x.setStartGoal('h','k')
x.search()

x=Searcher("10test.txt", searchType="BEST", verbose=True)
x.setStartGoal('h','k')
x.search()

x=Searcher("10test.txt", searchType="A*", verbose=True)
x.setStartGoal('h','k')
x.search()

# 50test.txt map
x=Searcher("50test.txt", searchType="DEPTH", verbose=False)
x.setStartGoal('s','c')
x.search()

x=Searcher("50test.txt", searchType="BREADTH", verbose=False)
x.setStartGoal('s','c')
x.search()

x=Searcher("50test.txt", searchType="BEST", verbose=False)
x.setStartGoal('s','c')
x.search()

x=Searcher("50test.txt", searchType="A*", verbose=False)
x.setStartGoal('s','c')
x.search()

