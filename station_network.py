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
            fr, to = PumpStation(i[0]), PumpStation("VKM") if "VKM" in i[1] else PumpStation(i[1])
            self.stations.add_edge(fr, to)

    def neighbors(self, node, depth, visited=[]):
        if depth >= 0:
            for i in self.stations:
                if node == i:
                    yield i
                    break
        visited.append(node)
        for i in nx.all_neighbors(self.stations, node):
            if i not in visited:
                for j in self.neighbors(i, depth-1, visited):
                    yield j

class PumpStation:
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return "Pump station:\n\tCode: " + str(self.code)

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        if type(other) == str:
            return self.code == other
        return self.code == other.code

if __name__ == "__main__":
    import networkx.drawing.nx_pydot as pydot
    a = StationNetwork()
    for i in a.neighbors("1078", 1):
        print(i)
    #pydot.to_pydot(a.stations).write_png("hi.png", prog="fdp")