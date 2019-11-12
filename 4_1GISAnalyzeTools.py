import math

class GISPoint: #定义一个基础类 点
    def __init__(self,x,y):
        self.x = x
        self.y = y
    
    def distance(self,point):
        return math.sqrt((self.x-point.x)**2+(self.y-point.y)**2)
    
    def __repr__(self): #重载打印方法 使得点可以以(x,y)的形式输出
        return "({},{})".format(self.x,self.y)

    def creatBuffer(self,d):
        return circle(self,d) #点的缓冲区 直接创建一个圆

#定义一个简单的折线段类 该类一个折线段可以有多个节点 待完善
# 通过*args参数将多个节点(GISPoint)作为一个列表传入以初始化
class GISPolyline:  #在GISTools暂仅在creatBuffer中使用到
    def __init__(self,*args):  #不建议通过实例直接访问节点和nodecount对象
        self._lines = args
        self._nodecount = len(self._lines)
    
    def append(self,point): #在末端加入GISPoint
        self._lines.append(point)
        self._nodecount+=1
    
    def generator(self): #构造生成器用于遍历所有节点
        i = 0
        while i<self._nodecount:
            yield self._lines[i]
            i+=1
    
    def getLines(self): #获取折线段所有单线
        linelst = []
        for i in range(self._nodecount-1):
            linelst.append((self._lines[i],self._lines[i+1]))
        linelst.append((self._lines[self._nodecount-1],self._lines[0])) 
        #linelst 是一个由点(GISPoint)对组成的线列表
        return linelst
    

#定义简单的GIS多边形类 部分方法与GISPolyline类似 待完善
# 通过*args参数将多个节点(GISPoint)作为一个列表传入以初始化
class GISPolygon:
    def __init__(self,*args): #不建议通过实例直接访问构成多边形的节点和nodecount对象
        self._polygon = args
        self._nodecount = len(self._polygon)
    
    def generator(self): #构造生成器用于遍历所有节点
        i = 0
        while i<self._nodecount:
            yield self._polygon[i]
            i+=1
    
    def getmaxExtent(self): #获取外包矩形
        xlst = []
        ylst = []
        for i in self._polygon:
            xlst.append(i.x)
            ylst.append(i.y)
        maxx = max(xlst)
        maxy = max(ylst)
        minx = min(xlst)
        miny = min(ylst)
        return GISPoint(minx,miny),GISPoint(maxx,maxy) #返回最大外界范围矩形的左下角和右上角的点
    
    def getLines(self): #获取多边形所有的边
        linelst = []
        for i in range(self._nodecount-1):
            linelst.append((self._polygon[i],self._polygon[i+1])) #此处加入列表的不是GISLine而是用两个点简单表示的边对象
        linelst.append((self._polygon[self._nodecount-1],self._polygon[0])) 
        #linelst 是一个由点对组成的边列表
        return linelst

class circle:  #简单的圆形对象 用以构造缓冲区
    def __init__(self,center,r):
        self.center = center
        self.r = r


########################
class GISTools: #GIS工具类 内有静态的各种空间计算的方法 通过类名直接调用
    def __init__(self):
        pass

    #定义基础的向量矢量积算法 供调用
    #点的形式为(x,y)而非GISPoint
    @staticmethod
    def vectorPro(p1,p2): 
        return (p1[0]*p2[1]-p1[1]*p2[0])

    @staticmethod ##判断p2相对于p0 p1的拐向方法
    def linedire(p0,p1,p2):
        res = GISTools.vectorPro((p2.x-p0.x,p2.y-p0.y),(p1.x-p0.x,p1.y-p0.y))
        if res<0:
            direction = "left"
        elif res > 0:
            direction = "right"
        else:
            return "{},{},{} is in the common line".format(p0,p1,p2)
        return "{}→{} turns {} to get {}→{}".format(p0,p1,direction,p1,p2)

    @staticmethod #判断点q在线p1p2上 两个条件
    def pWithinLine(q,p1,p2):
        flg = GISTools.vectorPro((q.x-p1.x,q.y-p1.y),(p2.x-p1.x,p2.y-p1.y))
        if flg==0:
            if min(p1.x,p2.x)<=q.x<=max(p1.x,p2.x) and min(p1.y,p2.y)<=q.y<=max(p1.y,p2.y):
                return True
        return False
    
        
    @staticmethod #判断直线段ab和cd是否相交（注意 此处是直线段）
    def intersect(a,b,c,d):
        #快速排斥实验 四个条件判断两线外接矩形重合
        # ab最下端小于cd最上端 最上端大于cd最下端
        # ab最左端小于cd最右端 最右端大于cd最左端
        flg1 = (min(a.y,b.y)<max(c.y,d.y) and max(a.y,b.y)>min(c.y,d.y) \
            and min(a.x,b.x)<max(c.x,d.x) and max(a.x,b.x)>min(c.x,d.x))
        #矢量跨立实验
        flg2 = GISTools.vectorPro((b.x-a.x,b.y-a.y),(c.x-a.x,c.y-a.y))*GISTools.vectorPro((b.x-a.x,b.y-a.y),(d.x-a.x,d.y-a.y))
        if flg2 == 0:
            return "in the common line"
        if flg1:
            if flg2<0:
                return "intersected"
        return "non-intersected"
    
    @staticmethod # 判断点在多边形内算法
    def pWithinPolygon(p,polygon):
        bottomleft,upright = polygon.getmaxExtent()
        #首先如果p不在复杂多边形的外包矩形之内 则直接判断点不可能在多边形内
        if not (bottomleft.x<=p.x<=upright.x and bottomleft.y<=p.y<=upright.y):
            return False
        #如果点p在polygon的边界上则直接判断点在边界上
        linelst = polygon.getLines()
        for line in linelst: 
            if GISTools.pWithinLine(p,line[0],line[1]):
                return "on the border"
        #构造射线 实际是一个线段 保证其长度能完全穿过多边形 且约束其不经过任何多边形的顶点
        #射线长设定为点p到外包矩形左下角点的距离+外包矩形对角线长 这样既可保证无论p点位置在哪儿该射线(线段)都可以完全穿过多边形
        raylength = p.distance(bottomleft) + bottomleft.distance(upright)
        import random
        while True:
            randcos = random.random()  #设定随机的射线与x轴夹角的cos值  绝大部分情况 第一次循环即可获得符合条件的射线 跳出循环
            randsin = math.sqrt(1-randcos**2) #cos和sin的值在0-1 显然对应着第一象限 既是射线发射方向
            endpx = p.x + raylength/randcos #计算处射线末端的xy值
            endpy = p.y + raylength/randsin
            endp = GISPoint(endpx,endpy)
            flg = []
            for point in polygon.generator():
                flg.append(GISTools.pWithinLine(point,p,endp))
            if True not in flg: #如果不存在顶点在多边形内的情况 则跳出
                break
        
        count = 0
        for line in linelst:
            if GISTools.intersect(p,endp,line[0],line[1]) == "intersected":
                count+=1
        if count%2 == 0:
            return False
        return True
    
    @staticmethod
    def pWithinCircle(p,circle): #用以判断点是否在圆内的简单方法
        distance = p.distance(circle.center)
        if distance < circle.r:
            return True
        elif distance > circle.r:
            return False
        else:
            return "point on the round"  

    @staticmethod
    def creatBuffer(obje,d): #暂时只有点和折线段的缓冲区创建 
        if isinstance(obje,GISPoint): #GISPoint对象直接返回一个r=d的圆
            return obje.creatBuffer(d)
        
        bufferpoly = []
        buffercir = [] #如果用同一个列表作为buffer的容器 会出现两次测试有不同的不稳定情况？？？？
        if isinstance(obje,GISPolyline):
            for p in obje.generator():
                buffercir.append(p.creatBuffer(d)) #首先将所有节点GISPoint形成的buffer全加入圆缓冲区
            for line in obje.getLines():
                ps,pe = line #一条线的首末端点
                sina = (pe.y-ps.y)/(ps.distance(pe)) #求出线段关于x轴的夹角的sin值
                cosa = (pe.x-ps.x)/(ps.distance(pe)) #注意此处cos可能为负 不能用cos = sqrt(1-sin^2)算
                p1 = GISPoint(ps.x+d*sina,ps.y-d*cosa)
                p2 = GISPoint(ps.x-d*sina,ps.y+d*cosa)
                p3 = GISPoint(pe.x-d*sina,pe.y+d*cosa)
                p4 = GISPoint(pe.x+d*sina,pe.y-d*cosa) #四个顶点构成的矩形既是缓冲区的一部分
                bufferpoly.append(GISPolygon(p1,p2,p3,p4))
        return buffercir,bufferpoly #返回两个分别由多个圆形和多边形组成的列表 两者共同构成缓冲区的整体 暂无将各个重叠部分合并的方法


if __name__=='__main__':
    #拐点判断测试
    print(GISTools.linedire(GISPoint(0,0),GISPoint(0,100),GISPoint(0,200)))
    print(GISTools.linedire(GISPoint(0,0),GISPoint(200,200),GISPoint(0,100)))
    print(GISTools.linedire(GISPoint(0,0),GISPoint(-100,100),GISPoint(100,50)))
    print()

    #点在线上判断测试
    print("{} within line{}→{} is {}".format(GISPoint(0,0),GISPoint(-100,-100),GISPoint(100,100),\
        GISTools.pWithinLine(GISPoint(0,0),GISPoint(-100,-100),GISPoint(100,100))))
    print()

    #直线段相交判断测试
    print("line ab{}→{} and line cd{}→{} is {}".format(GISPoint(0,0),GISPoint(100,200),GISPoint(300,600),GISPoint(400,800),\
        GISTools.intersect(GISPoint(0,0),GISPoint(100,200),GISPoint(200,400),GISPoint(400,800))))

    print("line ab{}→{} and line cd{}→{} is {}".format(GISPoint(0,0),GISPoint(100,200),GISPoint(0,100),GISPoint(100,100),\
        GISTools.intersect(GISPoint(0,0),GISPoint(100,200),GISPoint(0,100),GISPoint(100,100))))

    print("line ab{}→{} and line cd{}→{} is {}".format(GISPoint(0,0),GISPoint(100,200),GISPoint(0,100),GISPoint(100,300),\
        GISTools.intersect(GISPoint(0,0),GISPoint(100,200),GISPoint(0,100),GISPoint(100,300))))    
    print()
    
    '''# test for class GISPolyline and GISPolygon
    a = GISPolyline(GISPoint(0,0),GISPoint(100,0),GISPoint(0,100))
    print(a.nodecount)
    b = GISPolygon(GISPoint(0,0),GISPoint(100,0),GISPoint(0,100))
    for i in b.generator():
        print(i)
    '''
    #点在多边形内测试
    p = GISPoint
    polygon1 = GISPolygon(p(0,0),p(30,0),p(30,20),p(20,20),p(20,10),p(10,10),p(10,20),p(0,20))
    #polygon1类似一个凹字
    p1 = p(-100,-100)
    p2 = p(0,0)
    p3 = p(15,15)
    p4 = p(1,1) #该点显然在多边形内
    print(GISTools.pWithinPolygon(p1,polygon1))
    print(GISTools.pWithinPolygon(p2,polygon1))
    print(GISTools.pWithinPolygon(p3,polygon1))
    print(GISTools.pWithinPolygon(p4,polygon1))
    print()

    #测试缓冲区的建立
    p1 = p(0,0)
    p2 = p(100,0)
    p3 = p(100,100)
    polyline1 =GISPolyline(p1,p2,p3)
    buffercir,bufferpoly = GISTools.creatBuffer(polyline1,10)
    def testBufferin(p,buffercir,bufferpoly):
        for i in buffercir:
            if GISTools.pWithinCircle(p,i): #点如果在某个buffer部分里面 就返回true
                return True
        for i in bufferpoly:
            if GISTools.pWithinPolygon(p,i):
                return True
        return False #如果不在任何buffer部分内 就返回false
    
    p4 = p(-5,0) #in
    p5 = p(50,5) #in
    p6 = p(40,40) #out
    p7 = p(111,0) #out
    p8 = p(20,-20) #out
    print(testBufferin(p4,buffercir,bufferpoly))
    print(testBufferin(p5,buffercir,bufferpoly)) 
    print(testBufferin(p6,buffercir,bufferpoly))
    print(testBufferin(p7,buffercir,bufferpoly))
    print(testBufferin(p8,buffercir,bufferpoly))        
