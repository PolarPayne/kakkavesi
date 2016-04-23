from db_connection import connection
import networkx as nx

class StationNetwork:
    def __init__(self):
        self.stations = nx.Graph()

        cursor = connection.cursor()
        cursor.execute("SELECT code, next_station FROM [AWR].[dbo].[HSY_TARGETS]"
                       # "WHERE target_type = 'JVP'"
                       "WHERE next_station <> 'NULL'"
                       "AND next_station <> ''")
        rows = cursor.fetchall()

        for i in rows:
            fr, to = i[0], "VKM" if "VKM" in i[1] else i[1]
            self.stations.add_edge(fr, to)

    def neighbors(self, node, depth, visited=[]):
        if depth >= 0:
            yield node
        visited.append(node)
        for i in nx.all_neighbors(self.stations, node):
            if i not in visited:
                for j in self.neighbors(i, depth-1, visited):
                    yield j

if __name__ == "__main__":
    import networkx.drawing.nx_pydot as pydot
    a = StationNetwork()
    pydot.to_pydot(a.stations).write_png("hi.png", prog="fdp")