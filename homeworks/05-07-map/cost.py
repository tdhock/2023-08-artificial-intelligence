import sys
prog, filename, path = sys.argv
edge_dict = {}
for line in open(filename):
    city_from, city_to, cost, xy_from, xy_to = eval(line)
    edge_dict[(city_from,city_to)] = cost
    edge_dict[(city_to,city_from)] = cost
city_list = path.split(",")
cost = 0
for from_index in range(len(city_list)-1):
    to_index = from_index + 1
    from_city = city_list[from_index]
    to_city = city_list[to_index]
    cost += edge_dict[(from_city,to_city)]
print(cost)
