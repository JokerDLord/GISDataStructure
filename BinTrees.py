
#先定义一个结点类
class BiNode:
    def __init__(self,_data=None,_left=None,_right=None):
        self.data = _data
        self.left = _left
        self.right = _right



class BiTrees:
    def __init__(self,data_=None):#data是一个初始化根结点
        self.__root=data_
    
    def is_empty(self):
        return self.__root is None

    def root(self):
        return self.__root
    
    def set_root(self,rootnode):
        self.__root=rootnode

    def leftchild(self):
        return self.__root.left
    
    def rightchild(self):
        return self.__root.right 
    
    def set_left(self,left):
        self.__root.left = left

    def set_right(self,right):
        self.__root.right = right
    

    #通过递归定义二叉树的先序遍历
    def preorder(self,t):
        if t is None:
            print("None",end="")#空树输出^
            return
        print("("+repr(t.data),end="")
        self.preorder(t.left)
        self.preorder(t.right)
        print(")",end="")

    #非递归定义二叉树的先序遍历     
    def preorder_nonrec(self,t):
        if t is None:
            print("^",end="")#空树输出^
            return
        s = [] #列表可以模拟stack 通过append pop实现 后进 先出
        while (t is not None):#判断t存在
            while t is not None: #沿着左分支下行
                print(t.data,end=" ")
                if t.right:
                    s.append(t.right) #右分支入栈
                t = t.left
            if (s): #如果栈未被清空
                t = s.pop()
                

    #宽度优先遍历
    def levelorder(self,t):
        queue = [t] #先构建一个lst列表 通过列表的pop和append实现先进先出操作
        if t is None:
            print("^",end="")#空树输出^
            return
        while queue !=[]:#当列表不为空
            p = queue[0]
            print(p.data,end=" ")
            #如果队列头的左子树或右子树根结点存在 则让他们分别入队
            if p.left is not None:
                queue.append(p.left)
            if p.right is not None:
                queue.append(p.right)
            #最后队列头出队
            queue.pop(0)  

    #读取完全二叉树数组 生成一个二叉树
    def get_ATree(self,t):
        #读取一个按照完全二叉树规则存储的二叉树数组 生成对应二叉树
        tree = [BiNode(data) for data in t] #将t转换为所有树的结点存储在一个列表中
        root = tree[1]
        self.__root = root #生成一棵树 初始化根结点
        #假定该树是一个满二叉树按层次进行索引 父结点序号为i 则任意一个结点的左子结点序号l=2*i 右子结点序号r=2*i+1
        for i in range(1,len(tree)):
            if (2*i+1)<=len(tree)-1:#判断子结点不会越界
                if tree[i].data is None:#如果读取结点数值为空就进入下一次循环
                    continue
                else:
                    self.set_root(tree[i]) #每次根据遍历设定根结点 左右子结点
                    if tree[2*i].data is not None:#当子结点不为none时执行 设定左右子结点 
                        self.set_left(tree[2*i])
                    if tree[2*i+1].data is not None:
                        self.set_right(tree[2*i+1])
        self.set_root(root) #最后重新设置回根结点
        return self



if __name__ == '__main__':
    #测试递归的先序遍历
    t1 = BiTrees(BiNode(1,BiNode(2,None,BiNode(5)),BiNode(3)))
    t1.preorder(t1.root())
    #t1.preorder(t1.root())
    print()

    #测试非递归定义的先序遍历和宽度优先遍历
    t2 = BiTrees(BiNode(1))#根结点为1
    t2l = BiTrees(BiNode(2,None,BiNode(5)))#创建左子树
    t2r = BiTrees(BiNode(3))#创建右子树
    t2.set_left(t2l.root())#将左右子树的根结点与根结点相连
    t2.set_right(t2r.root())
    t2.preorder_nonrec(t2.root())
    print()
    t2.levelorder(t2.root())

    #构建题目2的二叉树 并测试先序遍历和宽度优先遍历
    print("\n构建题目2的二叉树 并先序遍历和宽度优先遍历")
    tree = [None,31,23,12,66,None,5,17,70,62,None,None,None,88,None,55]
    btree = BiTrees()
    btree.get_ATree(tree)
    print("\n递归先序遍历:")
    btree.preorder(btree.root())
    print("\n非递归先序遍历:")
    btree.preorder_nonrec(btree.root())
    print("\n宽度优先遍历:")
    btree.levelorder(btree.root())
