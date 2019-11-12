"""
以一组第2题的数据为例，用Python语言上机实现一个顺序表，实现对顺序表中数据元素的增删除改查和遍历等基本操作。
"""
class SeqList(list): #创建顺序表类
    def __init__(self,lst = []):
        self._array = lst
        self._length = len(self._array)

    def get(self,idx):
        if idx>self._length or idx<0:
            return print("index out of range")
        return self._array[idx]
    
    def find(self,key):
        #查找值为key的元素的位置
        for i in range(len(self._array)):
            if self._array[i] == key:
                return i
        return None
        
    def insert(self,idx,elem):
        k=len(self._array)-1
        self._array.append(0)
        if (idx>k+1) or (idx<0):
            return False
        while k>=idx:
            self._array[k+1]=self._array[k]
            k-=1
        self._array[idx]=elem
        return True
        
    def delete(self,idx):
        if idx>self._length or idx<0:
            return print("index out of range")
        for i in range(idx,self._length):
            self._array[i] = self._array[i+1]
        del self._array[-1]
        self._length-=1
        return self._array
        
    def length(self):
        return len(self._array)

    def __repr__(self): #直接打印顺序表以list的形式
        return "{}".format(self._array)
    
    def traverse(self):#遍历并打印顺序表
        s=""
        for i in self._array:
            s=s+str(i)+" "
        return s
    
if __name__=="__main__":
    slst=[1,2,6,9]   
    slst = SeqList(slst) #创建顺序表slst
    print(slst.find(2)) #找到2所在的下标
    print(slst.insert(2,4)) #在索引2前插入4
    print(slst) #打印顺序表
    print(slst.length()) #输出顺序表长度
    print(slst.delete(2))#删除顺序表第二位的元素
    print(slst.traverse()) #遍历打印顺序表

    #把第二题的gdp数据导入一个顺序表中
    with open("gdp.txt","r") as f:
        gdps = SeqList()
        count = 0
        for row in f:
            year,GDP = row.split(",")
            gdps.insert(count,float(GDP))
            count+=1
        print(gdps) #打印顺序表

