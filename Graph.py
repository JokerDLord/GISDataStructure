# 邻接矩阵实现无向图 Dijkstra算法
inf = float("inf")


class Graph():
    def __init__(self, n):
        self.vertexn = n
        self.gType = 0
        self.vertexes = [inf]*n
        self.arcs = [self.vertexes*n]  # 邻接矩阵
        self.visited = [False]*n  # 用于深度遍历记录结点的访问情况

    def addvertex(self, v, i):
        self.vertexes[i] = v

    def addarcs(self, row, column, weight):
        self.arcs[row][column] = weight

    # 深度优先遍历
    def DFS(self, i):
        j = 0
        print("vertex:{}".format(self.vertexes[i]), end=" ")  # 先打印访问到的节点
        self.visited[i] = True
        while j < self.vertexn:
            if (self.arcs[i][j] != inf) and (not self.visited[j]):
                print(self.arcs[i][j], end=" ")
                self.DFS(j)
            j += 1

    # 广度优先遍历
    def BFS(self, k):
        self.visited = [False]*self.vertexn  # 访问性重置
        q = []
        print("vertex:{}".format(self.vertexes[k]), end=" ")
        self.visited[k] = True
        q.append(k)
        while q != []:
            i = q.pop(0)
            for j in range(self.vertexn):
                if(self.arcs[i][j] != inf) and (not self.visited[j]):
                    print(self.arcs[i][j], end=" ")  # 父节点与子节点的距离
                    print("vertex:{}".format(self.vertexes[j]), end=" ")
                    self.visited[j] = True
                    q.append(j)

    # 最短路径算法-Dijkstra 输入点v0，找到所有点到v0的最短距离
    def Dijkstra(self, v0):
        # 初始化操作
        D = [inf]*self.vertexn  # 用于存放从顶点v0到v的最短路径长度
        path = [None]*self.vertexn  # 用于存放从顶点v0到v的路径
        final = [None]*self.vertexn  # 表示从v0到v的最短路径是否找到最短路径
        for i in range(self.vertexn):
            final[i] = False
            D[i] = self.arcs[v0][i]
            path[i] = ""  # 路径先置空
            if D[i] < inf:
                path[i] = self.vertexes[i]  # 如果v0直接连到第i点，则路径直接改为i
        D[v0] = 0
        final[v0] = True
        ###
        for i in range(1, self.vertexn):
            min = inf  # 找到离v0最近的顶点
            for k in range(self.vertexn):
                if(not final[k]) and (D[k] < min):
                    v = k
                    min = D[k]
            final[v] = True  # 最近的点找到，加入到已得最短路径集合S中 此后的min将在处S以外的vertex中产生
            for k in range(self.vertexn):
                if(not final[k]) and (min+self.arcs[v][k] < D[k]):
                    # 如果最短的距离(v0-v)加上v到k的距离小于现存v0到k的距离
                    D[k] = min+self.arcs[v][k]
                    path[k] = path[v]+","+self.vertexes[k]
        return D, path


if __name__ == "__main__":
    g = Graph(5)
    g.vertexes = ["A", "B", "C", "D", "E"]
    g.arcs = [[inf, 60, 80, 30, inf], [60, inf, 40, 75, inf], [
        80, 40, inf, inf, 35], [30, 75, inf, inf, 45], [inf, inf, 35, 45, inf]]

    print("深度优先遍历：")
    g.DFS(0)
    print("\n广度优先遍历：")
    g.BFS(0)
    print()

    print("Dijkstra搜索点到图中各点的最短路径:")
    D, path = g.Dijkstra(0)
    print(D)
    print(path)
