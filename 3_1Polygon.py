"""
用Python定义多边形数据结构(polygon)
实现对多边形元素的编辑功能：增、删、改（移动）、查多边形的顶点。
"""
import math

class LNode: #定义节点（顶点）类 元素elem为坐标
    def __init__(self,elem_,next_=None):
        self.elem = elem_
        self.next = next_

class Polygon_LList:
    def __init__(self):
        self.head=None

    def isEmpty(self):
        pn = self.head
        if pn is None:  #判断是否为空
            return "没有点存在"
        j=0
        while j<3 and pn is not None:
            pn = pn.next
            j+=1
        return pn is None #少于三个点 返回false 则不存在多边形

    def insert(self,elem,index): #多边形顶点增加
        pn = self.head
        j=0
        while (j<index-1) and (pn!=None):#找到索引处j 
            pn = pn.next
            j+=1
        if j==0 or pn==None:
            pn = LNode(elem)
        else:
            pnode = LNode(elem)
            pnode.next = pn.next
            pn.next = pnode
    
    def append(self,elem): #在最后的位置加点
        if self.head is None:
            self.head = LNode(elem)
            return
        p = self.head
        while p.next is not None:
            p = p.next
        p.next = LNode(elem)

    def delete(self,idx): #删除顶点
        pn1 = self.head
        j=0
        while (j<idx-1):
            pn1 = pn1.next
            if pn1.next ==None:break
            else:j+=1
        if (j==0)or(pn1.next==None):
            return False
        else:
            pn2=pn1.next #pn2是要被删除的节点
            pn1.next = pn2.next
            return True
        
    def alter(self,elem,index): #修改索引index处的Polygon点
        pn = self.head
        j=0
        while (j<index) and (pn!=None):#找到索引处j
            pn = pn.next
            j+=1
        if j==0 or pn==None:
            pn = LNode(elem)
        else:
            pn.elem = elem


    def indexOf(self,key): #查找(按序号)
        pn =self.head
        j=0
        while pn is not None:
            if pn.elem ==key:
                break
            else:
                pn=pn.next
                j+=1
        if pn is None:
            return -1
        else:
            return j

    def get(self,index): #查找（按元素）
        pn = self.head
        if pn is None:
            return None
        j=0
        while j<index and pn!=None:
            pn = pn.next
            j+=1
        return pn.elem
    
    def printall(self):  #打印所有节点
        p = self.head
        while p is not None:
            print(p.elem, end = '')
            if p.next is not None:
                print(', ',end='')
            p = p.next
        print('\n')

    def element(self): #通过生成器 遍历所有节点 
        pn = self.head
        while True:
            yield pn.elem
            pn = pn.next
            if pn is None:
                break
    
    def combine(self,polygonlst):
        pn = self.head
        if pn is None:
            return polygonlst        
        while pn.next is not None:
            pn = pn.next
        pn.next = polygonlst.head
    
    @staticmethod #构造静态方法，用于矢量积的计算
    def vectorPro(node1,node2):
        return (node1.elem[0]*node2.elem[1]-node2.elem[0]*node1.elem[1])

    @staticmethod #构造静态方法，用于计算两节点之间的距离
    def distance(node1,node2):
        return math.sqrt((node2.elem[0]-node1.elem[0])**2+(node2.elem[1]-node1.elem[1])**2)
    
    #计算单个多边形（封闭）的面积 这里用到了一个通用的面积计算公式
    #先求两个相邻节点之间的矢量积：pi = xi*y(i+1)-x(i+1)*yi
    #area = (p1 + p2 + p3 + ...... + pn)/2
    def sumArea(self):
        pn = self.head
        area = 0
        while pn.next is not None:
            area += self.vectorPro(pn,pn.next)
            pn = pn.next
        area += self.vectorPro(pn, self.head)
        area/=2
        return abs(area)
    
    def sumLength(self):
        pn = self.head
        length = 0
        while pn.next is not None:
            length+=self.distance(pn,pn.next)
            pn = pn.next
        length+=self.distance(pn, self.head)
        return length


if __name__ == '__main__':
    a = Polygon_LList()
    print(a.isEmpty()) #判断多边形链表是否为空
    ######添加操作
    a.append((0,0)) 
    a.append((100,0))
    a.append((0,100)) #为多边形链表末端添加节点
    a.printall()

    ######删除与修改操作
    a.insert((100,100),2) #在第三个点前插入节点(100,100)
    a.alter((200,0),1)   #将第二个点修改为(200,0)
    a.printall()
    
    ######查找元素或索引操作
    a.delete(3)  #删除最后一个（第四个）节点
    print(a.get(0)) #获取第一个节点的元素（坐标）
    print(a.indexOf((0,0))) #查找（0，0）节点的序号
    a.printall()
    
    ######链表合并操作
    b = Polygon_LList()
    b.append((0,200))
    b.append((300,200))
    b.append((300,100))
    a.combine(b) #将b与链表合并
    a.printall()

    ######单个多边形面积计算
    c = Polygon_LList()
    c.append((0,0))
    c.append((200,0))
    c.append((300,100))
    c.append((100,100)) #c是一个底长200高为100的平行四边形
    print("Area is {}".format(c.sumArea()))
    print("Length is {}".format(c.sumLength()))

    

    
