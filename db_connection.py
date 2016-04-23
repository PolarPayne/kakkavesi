import pymssql

_SERVER = '10.144.72.11:1433'
_USER = 'devuser1'
_PASSWORD = 'devuser123'

connection = pymssql.connect(_SERVER, _USER, _PASSWORD)

cursor = connection.cursor()
cursor.execute("SELECT code, next_station FROM [AWR].[dbo].[HSY_TARGETS]"
               #"WHERE target_type = 'JVP'"
               "WHERE next_station <> 'NULL'"
               "AND next_station <> ''")

rows = cursor.fetchall()

import pydotplus as pydot
import tqdm

tree = {}

for i in tqdm.tqdm(rows):
    fr, to = i[0], "VKM" if "VKM" in i[1] else i[1]
    if to not in tree:
        tree[to] = []
    tree[to].append(fr)


# Let's make some happy trees
t = pydot.Dot(graph_type="digraph", splines="line", layout="circo")

for i in tqdm.tqdm(tree):
    t.add_node(pydot.Node(i))

for i, j in tqdm.tqdm(tree.items()):
    for k in j:
        t.add_edge(pydot.Edge(k, i))

t.write_png("example2_graph.png")
