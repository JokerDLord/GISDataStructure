from SeqList import SeqList
"""
用Python语言设计一个简单的Point类，用顺序表实现一个Points列表（List）。
实现对Points中的元素进行管理的基本功能，包括：指定位置增加点，删除指定点，修改指定点的值，
遍历和打印输出等操作。
"""
class Point(): #创建点类别
    def __init__(self,name,loc):
        self.name = name
        self.loc = loc
    
    def __repr__(self):
        return "点{}，位于{}".format(self.name,self.loc)

class Points(SeqList): #点列表继承自顺序表
    def __init__(self,lst=[]):
        SeqList.__init__(self,lst=[])
        self._array = lst
        self._length = len(self._array)

    def delete(self,idx): #删除指定点
        super().delete(idx)

    def insert(self,idx,point): #指定位置增加点
        super().insert(idx,point)
    
    def update(self,idx,point): #修改指定点的值
        self._array[idx] = point
        return self._array

    def __repr__(self): #遍历和打印输出
        s=""
        for point in self._array:
            s=s+"{}位于{}".format(point.name,point.loc)+";"
        return s


if __name__=="__main__":
    a = Point("A",(130,35))
    b = Point("B",(130,34))
    shanghai = Point("上海",(121,31))
    print(a)

    lst = [a,b,shanghai]
    p_lst = Points(lst) #新建一个顺序表实现Points列表（List）
    print(p_lst)

    c = Point("C",(119,41))
    p_lst.insert(2,c) #将c点插入至指定位置（索引为2）
    b = Point("B",(130,44))
    p_lst.update(1,b) #修改索引1的点
    p_lst.delete(0) #删除索引为0的点
    print(p_lst)




    
    

