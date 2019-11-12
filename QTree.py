import math
class Point:
    def __init__(self,x=None,y=None):
        self.x = x
        self.y = y
    
    def distance(self,p):
        return math.sqrt((self.x-p.x)**2 + (self.y-p.y)**2)

class QNode:
    def __init__(self,p,city = None):
        self.p = p
        self.NE = None #N belongs to NE
        self.NW = None #W belongs to NW
        self.SW = None #S belongs to SW
        self.SE = None #E belongs to SE
        self.city = None

class QTree:
    def __init__(self):
        self.root=None
    
    def add(self,p,node,city=None):#添加点的参数为点p,node,city名
        if node is None:
            self.root = QNode(p,city)
            return True
        
        #通过递归判断并将点p插入对应的方位和对应的子节点
        elif p.x>=node.p.x and p.y>node.p.y:
            if node.NE is None:
                node.NE=QNode(p,city)
                return True
            self.add(p,node.NE,city)
        
        elif p.x<node.p.x and p.y>=node.p.y:
            if node.NW is None:
                node.NW=QNode(p,city)
                return True
            self.add(p,node.NW,city)
        
        elif p.x<=node.p.x and p.y<node.p.y:
            if node.SW is None:
                node.SW=QNode(p,city)
                return True
            self.add(p,node.SW,city)
        
        elif p.x>node.p.x and p.y<=node.p.y:
            if node.SE is None:
                node.SE=QNode(p,city)
                return True
            self.add(p,node.SE,city)
    
    #使用递归实现点的四叉树的先序遍历
    def preorder(self,node):
        if node is None:
            return False
        print("({},{})".format(node.p.x,node.p.y), end=" ")
        self.preorder(node.NE)
        self.preorder(node.NW)
        self.preorder(node.SW)
        self.preorder(node.SE)
    
    #查找一个点半径r范围内的所有点
    def within(self,p,r,node,container=[]):
        if node is None:
            return None
        
        self.within(p,r,node.NE,container)
        self.within(p,r,node.NW,container)
        self.within(p,r,node.SW,container)
        self.within(p,r,node.SE,container)
        distance = p.distance(node.p)
        if distance<=r:
            container.append((node.p,node.city))#符合距离小于半径条件即加入container中

if __name__ == "__main__":
    plst = [(40,60),(10,75),(70,20),(25,15),(80,70),(20,45),(35,45),(60,50)]
    point_lst = [Point(x,y) for (x,y) in plst]
    qtree = QTree()
    for p in point_lst:
        qtree.add(p,qtree.root)
    
    print("先序遍历方位四叉树qtree：")
    qtree.preorder(qtree.root)
    print()

    p = Point(50,50)
    r=20
    print("查找点({},{})半径为{}范围内的点有：".format(p.x,p.y,r))
    con = []
    qtree.within(p,r,qtree.root,con)
    for (point,city) in con:
        print("({},{})".format(point.x,point.y), end=" ")
    print()

