

class BSNode():
    def __init__(self,k,left_=None,right_=None):
        self.key=k
        self.left=left_
        self.right=right_


class BSTree:
    def __init__(self):
        self.root = None
    
    #查找
    def search(self,k):
        if self.root is None:
            return None
        pn=self.root
        while pn is not None:#不为空时继续
            if k>pn.key:#右子树下行
                pn=pn.right
            elif k<pn.key:#左子树下行
                pn=pn.left
            elif k==pn.key:#找到
                return print("{} is found".format(pn.key))
        return print("{} is not found".format(k))

                
    #插入
    def insert(self,k):
        if self.root is None:#空树插入根节点
            self.root=BSNode(k)
            return None
        else:
            pn1=self.root
            while pn1 is not None:
                pn2=pn1
                if k>pn1.key:#比当前关键值大 沿着右子树下行
                    pn1=pn1.right
                    flg=1
                elif k<pn1.key:#比当前关键值小 沿着左子树下行
                    pn1=pn1.left
                    flg=2
                elif k==pn1.key:#节点已经存在
                    return None
        pn1 = BSNode(k)
        if flg == 1:#右子树插入
            pn2.right=pn1
        elif flg == 2:#左子树插入
            pn2.left=pn1
    
    #删除元素
    def delete(self,k):
        if self.root is None:
            return False
        else:
            pn1=self.root#设为根节点
            flg = 0
            while pn1 is not None:#当pn1不为None时循环 直到pn1为pn2叶节点的左/右空节点
                if k>pn1.key:#向右子树下行 flg为1
                    pn2=pn1
                    pn1=pn1.right
                    flg=1
                elif k<pn1.key:#向左子树下行 flg为2
                    pn2=pn1
                    pn1=pn1.left
                    flg=2
                elif k==pn1.key:#找到k值 跳出循环 pn1为k对应节点
                    break

            if pn1 is None:
                return False
            
            elif flg==1:
                #pn1==pn2.right
                if (pn1.left is None) &(pn1.right is None):#无左右节点 直接删除叶节点
                    pn2.right=None
                elif (pn1.left is None):#左节点为空则将右节点上接
                    pn2.right=pn1.right
                elif (pn1.right is None):#右节点为空则将左节点上接
                    pn2.right=pn1.left
                else: #左右子树均不为空的节点
                    bn2=pn1.left#当前节点的左子树bn2
                    while (bn2 is not None):#左子树的右路径到底
                        p2=bn2#p2为当前bn2的父节点
                        bn2=bn2.right#右子树下行
                    p2.right = pn1.right#将左子树的最大节点链接pn1的右节点
                    pn2.right=pn1.left#pn1左节点代替pn1
            
            elif flg==2:
                #pn1==pn2.left
                if (pn1.left is None)&(pn1.right is None):#直接删除叶节点
                    pn2.right=None
                elif (pn1.left is None):#左节点为空则将右节点上接
                    pn2.left=pn1.right
                elif (pn1.right is None):#右节点为空则将左节点上接
                    pn2.left=pn1.left
                else:#删除左右子树均不为空的根节点
                    bn2=pn1.left
                    while (bn2 is not None):
                        p2=bn2
                        bn2=bn2.right
                    p2.right=pn1.right#将左子树的最大节点链接pn1的右节点
                    pn2.left=pn1.left#pn1左节点代替pn1
                    
            elif flg==0:#删除的是根节点
                if (self.root.right is None) & (self.root.left is None):
                    self.root=None
                elif self.root.left is None:
                    self.root=self.root.right
                elif self.root.right is None:
                    self.root=self.root.left
                else:
                    bn3=self.root.left
                    while (bn3 is not None):
                        bn4=bn3
                        bn3=bn3.right
                    bn4.right=pn1.right#根节点的左子树最右节点链接根节点右节点
                    self.root=self.root.left#左节点设置为根节点
    
    #通过递归定义二叉树的先序遍历 
    def preorder(self,t):
        if t is None:
            return
        print(repr(t.key),end=" ")
        self.preorder(t.left)
        self.preorder(t.right)
    
    #通过递归定义二叉树的中序遍历 中序遍历会将排序树按照从小到大输出
    def midorder(self,t):
        if t is None:
            return
        self.midorder(t.left)
        print(repr(t.key),end=" ")
        self.midorder(t.right)
    


if __name__ == "__main__":
    bst=BSTree()
    lnum=[63,90,70,55,67,42,98,83,10,45,58]
    for num in lnum:
        bst.insert(num)
    
    print("bst先序/中序遍历：")
    bst.preorder(bst.root)
    print()
    bst.midorder(bst.root)
    print()
    bst.search(10)

    print('删除63并先序/中序遍历:')
    bst.delete(65)
    bst.preorder(bst.root)
    print()
    bst.midorder(bst.root)
    print()
    bst.search(65)