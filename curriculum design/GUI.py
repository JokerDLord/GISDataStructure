from tkinter import *                              # get widget classes
from tkinter.messagebox import *                   # get standard dialogs
from tkinter.filedialog import askopenfilename        # get standard dialogs
from tkinter import ttk
from math import sqrt
import re

from osgeo import gdal, gdalconst, ogr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
font = FontProperties(fname="font/msyh.ttc")
from matplotlib.figure import Figure
from matplotlib.colors import NoNorm
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import *
from matplotlib.backend_bases import key_press_handler

def notdone():
    showerror('Not implemented', 'Not yet available')

# 打开文件操作
def openrasterfile():
    global rfilename
    rfilename = askopenfilename()
    if rfilename:
        showinfo("openfile", "successfully loaded!!!")
    
    find_lst = re.findall(r"[/]([^/.]*)",rfilename) #匹配所有“/”分割开的内容 并提取最后一个，即为图层的名称也就是文件名
    filepath[find_lst[-1]] = rfilename    
    layers.append(find_lst[-1]) #将新打开的文件名加入到图层列表中
    comblayer["values"] = layers
    print(layers)
    listb1.insert(END,find_lst[-1])


def clearcanvas(canvas):  # 清空相应frame中的所有控件
    for widget in canvas.winfo_children():
        widget.destroy()


def bandget(ds,*args):
    bands = [] #通过列表，可以获取指定数量与类别的波段
    flg = False
    gap = 0
    
    #注意 此处判断读取数据像元值是否越界，如果越界，一般为“dat”等类型文件，需要首先进行归一化至0-255的处理
    for i in args:
        bandarray = ds.GetRasterBand(i).ReadAsArray()
        # print(bandarray)
        dnmin = np.min(bandarray)
        dnmax = np.max(bandarray)
        if dnmin<0 or dnmax>255:
            flg = True
            gap = max(gap,dnmax-dnmin)

        bands.append(bandarray)
    
    if flg == True:
        for i in range(len(bands)):
            # t = bands[i]
            bands[i] = ((bands[i]-np.min(bands[i]))/gap*255).astype(int)

    # b = ds.GetRasterBand(b).ReadAsArray()
    # g = ds.GetRasterBand(g).ReadAsArray()
    # r = ds.GetRasterBand(r).ReadAsArray()
    data = np.dstack(tuple(bands))
    # print(data)


    return data

def draw2canvas(data):
    clearcanvas(canvasframe)  # 清除原来canvas上的空间，重新绘制单个波段的图像
    f = Figure(figsize=(5, 4), dpi=150)
    a = f.add_subplot(111)
    # 把绘制的图形显示到tkinter窗口上
    tifwin = FigureCanvasTkAgg(f, master=canvasframe)
    tifwin.get_tk_widget().pack(fill=X, expand=1)
    a.imshow(data)

    tifwin.draw()
    # matplotlib的导航工具栏显示上来(默认是不会显示它的)
    toolbar = NavigationToolbar2Tk(tifwin, canvasframe)
    toolbar.update()
    tifwin._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)    

def getgray():
    #根据设定的权重转换RGB至灰度值
    grayband = ds.GetRasterBand(1).ReadAsArray()*0.114+ds.GetRasterBand(2).ReadAsArray()*0.587+ds.GetRasterBand(3).ReadAsArray()*0.299
    grayband = grayband.astype(int)
    return grayband


#计算rgb图的灰度图
def rgb2gray():
    grayband = getgray()
    dnmin = np.min(grayband)
    dnmax = np.max(grayband)
    if dnmin<0 or dnmax>255:
        grayband = ((grayband-dnmin)/(dnmax-dnmin)*255).astype(int)
    data = np.dstack((grayband,grayband,grayband))
    draw2canvas(data)


#统计灰度直方图
def graystat(grayband=None):
    if grayband is None:
        grayband = getgray()#默认是获取原图的灰度值数组
    data = grayband.flatten()
    print(data)
    plt.hist(data,bins=255,facecolor = "red",edgecolor="white",alpha=0.7)
    plt.xlabel("灰度值",fontproperties=font)
    plt.ylabel("频数/频率",fontproperties=font)
    plt.title("灰度频数/频率分布直方图",fontproperties=font)
    plt.show()

#灰度值反比变换处理
def graycontra():
    grayband = getgray()
    dnmin = np.min(grayband)
    dnmax = np.max(grayband)
    if dnmin<0 or dnmax>255:
        grayband = ((grayband-dnmin)/(dnmax-dnmin)*255).astype(int)
    contraband = np.max(grayband) + np.min(grayband) - grayband
    
    data = np.dstack((contraband,contraband,contraband))
    draw2canvas(data)

#灰度二值化处理
def graybina():
    grayband = getgray()
    medline = np.mean(grayband)
    binaband = np.where(grayband < medline, 0, 255)
    data = np.dstack((binaband,binaband,binaband))
    draw2canvas(data)

#灰度值归一化处理
def gray21(grayband = None,draw = True):
    if grayband is None:
        grayband = getgray()
    gmax = np.max(grayband)
    gmin = np.min(grayband)
    print(gmax,gmin)
    gray21band = (grayband-gmin)/(gmax-gmin)##将原rgb转得的像元值进行在0-1区间的归一化处理
    gray21band=gray21band.astype("float")
    if draw is True:
        data = np.dstack((gray21band,gray21band,gray21band))
        draw2canvas(data)
    
    return gray21band


# 灰度值均衡化处理 提升对比度

# 灰度直方图均衡化实现的步骤：
# 1.统计灰度级中每个像素在整幅图像中的个数
# 2.计算每个灰度级占图像中的概率分布
# 3.计算累计分布概率
# 4.计算均衡化之后的灰度值
# 5.映射回原来像素的坐标的像素值
def grayequalization(grayband = None,draw = True):
    if grayband is None:
        grayband = getgray()
    hist = np.bincount(grayband.flatten(),minlength=256) #统计灰度值从0-255共256个值的出现次数
    unihist = (256-1)*(np.cumsum(hist)/(grayband.size * 1.0))#计算灰度统计图的累计概率密度 并映射到各个级别灰度值
    unihist = unihist.astype('uint8')
    # 相当于借助累计概率密度函数的拉伸（将原来的灰度像元变为至少255个级别的累计概率密度） 
    # 来达到从像元值到概率密度值的映射关系 再将概率密度值转回为像元值
    height, width = grayband.shape
    uniform_gray = np.zeros(grayband.shape, dtype='uint8')
    for i in range(height):
        for j in range(width):
            uniform_gray[i,j] = unihist[grayband[i,j]]
    
    if draw is True:
        data = np.dstack(tuple([uniform_gray]*3))
        draw2canvas(data)
        graystat(uniform_gray)
    return uniform_gray


# 计算NDVI植被指数

def getNDVI():#输出NDVI指数计算图像并显示
    band4 = ds.GetRasterBand(4).ReadAsArray().astype('f')  # 近红外波段数组
    band3 = ds.GetRasterBand(3).ReadAsArray().astype('f')  # 红色波段数组
    NDVI = np.where((band4+band3 > 0), (band4-band3) /
                    (band4+band3), -99)  # 满足分母大于0的情况
    print(NDVI)
    driver = gdal.GetDriverByName("Gtiff")
    outdata = driver.Create("NDVI1.tif", ds.RasterXSize, ds.RasterYSize,\
                            1, gdalconst.GDT_Float32)
    outdata.SetGeoTransform(ds.GetGeoTransform())
    outband = outdata.GetRasterBand(1)
    outband.WriteArray(NDVI)
    outdata.FlushCache()
    data = bandget(outdata,1,1,1)
    draw2canvas(data)

    outdata = None

#########################卷积运算部分
# #该函数会模拟卷积核计算的过程，最终值返回到二维数组中i,j
# def convosliding(convo,convo_gray_temp,i,j):
#     #返回卷积核和对应位置矩阵的对应元素分别相乘得到的矩阵的和
#     return np.sum(np.multiply(convo,convo_gray_temp[i:i+size,j:j+size]))


def showimg(band):
    data = np.dstack(tuple([band]*3))
    plt.rcParams['figure.dpi'] = 100
    plt.imshow(data)
    plt.show()

#进行卷积运算 注意此处的卷积运算是对于灰度进行的 需要先转换为灰度图
def convolutioncal(size,grayband = None):#此处函数有两层作用，一是在不给顶grayband的情况下对主图grayband进行卷积运算并显示；二是给定band情况下返回卷积运算的band
    # size = sqrt(len(convolst))#先根据建立好的convolst卷积核列表 确定卷积核大小
    if grayband is None:
        showflg = True
        grayband = getgray()
    height, width = grayband.shape
    convo_gray = np.zeros(grayband.shape, dtype=int)# 最终数组
    convo_gray_temp = np.zeros((height+2*(size//2),width+2*(size//2)), dtype=int) #构建一个边缘扩展的过渡数组 使得卷积核平滑时能够处理到边缘的像元
    convo_gray_temp[(size//2):(size//2+height),(size//2):(size//2+width)] = grayband.copy()
    print(convo_gray_temp)

    #获取卷积核
    convo = np.array([int(i.get()) for i in convolst]) #获取输入的卷积核算子
    convo.shape = (size,size)
    convo = 1/size*convo

    for i in range(height):
        for j in range(width):
            convo_gray[i,j] = int(np.sum(np.multiply(convo,convo_gray_temp[i:i+size,j:j+size])))
    dnmin = np.min(convo_gray)
    dnmax = np.max(convo_gray)
    if dnmin<0 or dnmax>255:
        convo_gray = ((convo_gray-dnmin)/(dnmax-dnmin)*255).astype(int) #范围拉伸至256内 便于显示图片
        
    if showflg is True:
        showimg(convo_gray)
    
    return convo_gray #返回卷积运算得到的band
    


#根据指定的大小创建卷积核
def makeconvolution(convolutionframe,Esize):
    clearcanvas(convolutionframe)
    global size
    size = Esize
    # global size
    # size = int(sizeE.get())
    global convolst
    convolst = [] #用以储存卷积核输入框的列表
    for i in range(size):
        for j in range(size):
            e = Entry(convolutionframe,width = 8)
            e.grid(row = i,column=j)
            convolst.append(e)
    return convolst

#进行robert算子的运算
def makeroberts(band):
    height,width = band.shape
    robert_gray = np.zeros(band.shape, dtype=int)
    for i in range(height):
        for j in range(width):
            if i<height-1 and j<width-1:
                robert_gray[i,j] = abs(band[i+1,j+1]-band[i,j])+abs(band[i+1,j]-band[i,j+1])
    
    return robert_gray

#进行sobel算子的运算
def makesobel(band):
    height,width = band.shape
    temp = np.zeros((height+2,width+2), dtype=int)
    temp[1:1+height,1:1+width] = band.copy()
    sobel_gray = np.zeros((height,width), dtype=int)
    for i in range(height):
        for j in range(width):
            dx = (temp[i+2,j] - temp[i,j]) + 2*(temp[i+2,j+1] - temp[i,j+1]) + (temp[i+2,j+2] - temp[i,j+2])
            dy = (temp[i,j+2] - temp[i,j]) + 2*(temp[i+1,j+2] - temp[i+1,j]) + (temp[i+2,j+2] - temp[i+2,j])
            sobel_gray[i,j] = int(sqrt((dx)**2+(dy)**2))
    
    # sobel_gray[np.where(sobel_gray<200)] = 0 #对图像进行优化，去除像元值较小的点
    return sobel_gray

#进行prewitt算子的运算
def makeprewitt(band):
    height,width = band.shape
    temp = np.zeros((height+2,width+2), dtype=int)
    temp[1:1+height,1:1+width] = band.copy()
    prewitt_gray = np.zeros((height,width), dtype=int)
    for i in range(height):
        for j in range(width):
            dx = (temp[i+2,j] - temp[i,j]) + 1*(temp[i+2,j+1] - temp[i,j+1]) + (temp[i+2,j+2] - temp[i,j+2])
            dy = (temp[i,j+2] - temp[i,j]) + 1*(temp[i+1,j+2] - temp[i+1,j]) + (temp[i+2,j+2] - temp[i+2,j])
            prewitt_gray[i,j] = int(sqrt((dx)**2+(dy)**2))
    
    return prewitt_gray


#打开新窗口，设定卷积算子
def convolutionwin():
    dicconvo={"Laplacian微分算子":[0,-1,0,-1,4,-1,0,-1,0],"Laplacian改(1)":[-1,-1,-1,-1,8,-1,-1,-1,-1],"Laplacian改(2)":[1,-2,1,-2,4,-2,1,-2,1],\
        "单方向微分算子(水平)":[1,2,1,0,0,0,-1,-2,-1],"单方向微分算子(垂直)":[1,0,-1,2,0,-2,1,0,-1],"单方向微分算子(对角)":[2,1,0,1,0,-1,0,-1,-2]}
    dictip = {"Laplacian微分算子":"注：\n 拉普拉斯微分算子是最简单的各向同性微分算子，对于一幅二维图像f(x,y)，它在像元(x,y)位置处拉普拉斯定义为:(delta f)^2 = (∂f/∂x)^2 + (∂f/∂y)^2于二阶微分算子。二阶微分算子对图像局部的灰度变化更为敏感，尤其是对斜坡渐变的细节。拉普拉斯算子具有各向同性、线性和位移不变性的特点，对细线和孤立点的检测效果好；但是边缘的方向信息丢失，常产生双向元的边缘，对噪声有双倍加强的作用。",\
        "Laplacian改(1)":"注：\n 改进算子具有在对角线方向实现各项同性的特点",\
            "Laplacian改(2)":"注：\n 改进算子具有在对角线方向实现各项同性的特点",\
                "单方向微分算子(水平)":"注：\n 水平微分算子将利用图像像元的上下差异，突出水平方向的边缘",\
                    "单方向微分算子(垂直)":"注：\n 垂直微分算子将利用图像像元的左右差异，突出垂直方向的边缘",\
                        "单方向微分算子(对角)":"注：\n 突出对角方向的边缘",\
                            "Roberts交叉微分算子":"注：\n Roberts交叉微分算子从两个方向来考虑锐化微分的计算，对于当前处理的像元f(x,y),其梯度计算的近似方法定义为g(x,y) = |f(x+1,y+1) - f(x,y)| + |f(x+1,y)-f(x,y+1)|，经过Robert算子计算，地物轮廓信息将得到明显增强",\
                                "Sobel微分算子":"注：\n Sobel微分算子采用3x3模板下的全方向微分，是一种将方向差分和局部平均结合的方法，其表达式为g(x,y) = sqrt(dx(x,y)^2 + dy(x,y)^2)",\
                                    "Prewitt微分算子":"注：\n Prewitt微分算子相当于将Sobel微分算子中权重的2改成了1"}
    def makeexconvolution():
        operater = combex.get()
        if operater == "Laplacian微分算子":
            convolst = makeconvolution(convolutionframe,3)
            for i in range(len(convolst)): #将算子的值依次插入到entry中
                convolst[i].insert(0,dicconvo[operater][i])
            labeltip["text"] = dictip[operater]
        elif operater == "Laplacian改(1)":
            convolst = makeconvolution(convolutionframe,3)
            for i in range(len(convolst)): #将算子的值依次插入到entry中
                convolst[i].insert(0,dicconvo[operater][i])
            labeltip["text"] = dictip[operater]
        elif operater == "Laplacian改(2)":
            convolst = makeconvolution(convolutionframe,3)
            for i in range(len(convolst)): #将算子的值依次插入到entry中
                convolst[i].insert(0,dicconvo[operater][i])
            labeltip["text"] = dictip[operater]
        elif operater == "单方向微分算子(水平)":
            convolst = makeconvolution(convolutionframe,3)
            for i in range(len(convolst)): #将算子的值依次插入到entry中
                convolst[i].insert(0,dicconvo[operater][i])
            labeltip["text"] = dictip[operater]
        elif operater == "单方向微分算子(垂直)":
            convolst = makeconvolution(convolutionframe,3)
            for i in range(len(convolst)): #将算子的值依次插入到entry中
                convolst[i].insert(0,dicconvo[operater][i])
            labeltip["text"] = dictip[operater]
        elif operater == "单方向微分算子(对角)":
            convolst = makeconvolution(convolutionframe,3)
            for i in range(len(convolst)): #将算子的值依次插入到entry中
                convolst[i].insert(0,dicconvo[operater][i])
            labeltip["text"] = dictip[operater]
        elif operater == "Roberts交叉微分算子":
            clearcanvas(convolutionframe)
            grayband = getgray()
            labeltip["text"] = dictip[operater]
            robertband = makeroberts(grayband)
            showimg(robertband)
        elif operater == "Sobel微分算子":
            clearcanvas(convolutionframe)
            grayband = getgray()
            labeltip["text"] = dictip[operater]
            robertband = makesobel(grayband)
            showimg(robertband)
        elif operater == "Prewitt微分算子":
            clearcanvas(convolutionframe)
            grayband = getgray()
            labeltip["text"] = dictip[operater]
            robertband = makeprewitt(grayband)
            showimg(robertband)
        
        
    top = Toplevel()
    top.title("卷积运算")
    top.geometry("800x300")
    rootnew  = Frame(top,width = 300,height = 300)
    rootnew.pack(side=LEFT, padx=10, fill=Y, expand=YES)
    labelframe = Frame(top,width = 300,height = 300,bg = "lightgray")#用于存放tip的frame
    labelframe.pack(side=LEFT, padx=10, fill=BOTH, expand=YES)


    label1 = Label(rootnew,text="图像增强：卷积运算")
    label1.grid(row=0,column=0)  
    label2 = Label(rootnew,text = "请输入自定义卷积核大小(单数):")
    label2.grid(row=1,column=0)
    sizeE = Entry(rootnew)
    sizeE.grid(row=1,column=1)
    sizeE.insert(0,3)
    Button(rootnew,text="创建自定义卷积核",command=lambda:makeconvolution(convolutionframe,int(sizeE.get()))).grid(row=1,column=2)
    

    label3 = Label(rootnew,text="选择示例卷积算子：")
    label3.grid(row = 2,column=0)
    cvex = StringVar()
    combex = ttk.Combobox(rootnew, textvariable=cvex)
    combex.grid(row=2, column=1, sticky=NSEW)
    combex["values"] = ("单方向微分算子(水平)","单方向微分算子(垂直)","单方向微分算子(对角)","Laplacian微分算子","Laplacian改(1)","Laplacian改(2)","Roberts交叉微分算子","Sobel微分算子","Prewitt微分算子")
    Button(rootnew,text = "创建示例卷积算子",command=makeexconvolution).grid(row=2,column=2)


    convolutionframe = Frame(rootnew)
    convolutionframe.grid(row=3,columnspan=2)
    makeconvolution(convolutionframe,int(sizeE.get()))#默认先创建3x3的卷积核

    
    Button(rootnew,text = "卷积核运算",command = lambda:convolutioncal(int(sqrt(len(convolutionframe.winfo_children()))))).grid(row=4,column=0)

    labeltip = Label(labelframe,text = "注：选择Robert交叉微分算子,Sobel微分算子,Prewitt微分算子将直接进行运算并显示结果",wraplength = 250,justify = 'left')#anchor = 'w'
    labeltip.grid(row=0,column=0)


###########################灰度形态学运算
#获取腐蚀运算波段
def geterosionband(gray,flg = False):
    height,width = gray.shape
    erosion_gray = np.zeros((height,width), dtype=int)
    temp = np.zeros((height+2,width+2), dtype=int)
    temp[1:1+height,1:1+width] = gray.copy()
    structure = np.array([[0,1,0],[1,2,1],[0,1,0]])#确定腐蚀的结构元素
    for i in range(height):
        for j in range(width):
            erosion_gray[i,j] = np.min(temp[i:i+3,j:j+3]-structure)
    
    print(erosion_gray)
    if flg == True:
        showimg(erosion_gray)
    
    return erosion_gray

#获取膨胀运算波段
def getdilateband(gray,flg = False):
    height,width = gray.shape
    dilate_gray = np.zeros((height,width), dtype=int)
    temp = np.zeros((height+2,width+2), dtype=int)
    temp[1:1+height,1:1+width] = gray.copy()
    structure = np.array([[0,1,0],[1,2,1],[0,1,0]])#确定腐蚀的结构元素
    for i in range(height):
        for j in range(width):
            dilate_gray[i,j] = np.max(temp[i:i+3,j:j+3]+structure)
    
    print(dilate_gray)
    if flg == True:
        showimg(dilate_gray)
    
    return dilate_gray

#获取开运算的波段，先腐蚀后膨胀
def getopenband(gray,flg = False): 
    erosion_gray = geterosionband(gray) #先获取腐蚀得到的波段并不绘制
    open_gray = getdilateband(erosion_gray) #膨胀且不绘制
    if flg == True:
        showimg(open_gray)
    return open_gray

#获取闭运算的波段，先膨胀后腐蚀
def getcloseband(gray,flg = False): 
    dilate_gray = getdilateband(gray) #先获取膨胀得到的波段并不绘制
    close_gray = geterosionband(dilate_gray) #腐蚀且不绘制
    if flg == True:
        showimg(close_gray)
    return close_gray

#获取腐蚀型梯度
def geterosiongrad(gray,flg = False):
    erosion_grad = gray - geterosionband(gray)
    erosion_grad = gray21(erosion_grad,False) #对边界进行优化使其更明显
    if flg == True:
        showimg(erosion_grad)
    return erosion_grad

#获取膨胀型梯度
def getdilategrad(gray,flg = False):
    dilate_grad = getdilateband(gray) - gray
    dilate_grad = gray21(dilate_grad,False) #对边界进行优化使其更明显
    if flg == True:
        showimg(dilate_grad)
    return dilate_grad

#获取膨胀腐蚀型梯度
def getdilaerograd(gray,flg = False):
    dilate = getdilateband(gray)
    erosion = geterosionband(gray)
    dilaero_grad = dilate - erosion
    # dilaero_grad+=gray
    dilaero_grad = gray21(dilaero_grad,False)
    if flg == True:
        showimg(dilaero_grad)
    return dilaero_grad    


def grayscale(type):
    top = Toplevel()
    top.title("灰度形态学梯度运算")
    top.geometry("400x200")
    lbframe = Frame(top,height = 150,width = 400)
    lbframe.pack()
    lb = Label(lbframe,text = " ",bg="lightgray",wraplength = 400)
    lb.pack()

    btframe = Frame(top)
    btframe.pack()
    gray = getgray()
    dnmin = np.min(gray)
    dnmax = np.max(gray)
    if dnmin<0 or dnmax>255:
        gray = ((gray-dnmin)/(dnmax-dnmin)*255).astype(int) #范围拉伸至256内 便于显示图片
    if type == "erosion":
        lb["text"] = """腐蚀：\n 腐蚀运算是用原始图像像元值与\n[[0,1,0],\n[1,2,1],\n[0,1,0]]\n的结构元素相减，取最小值赋给结果图像相应像元得到的。关于灰度腐蚀的效果有：1如果所有结构元素都为正，输出图像趋向于比原始图像更暗；2 在原始图像中亮细节的面积比结构元素的面积小则亮的效果将被削弱。"""
        Button(btframe,text ="确认运算",command = lambda:geterosionband(gray,True)).pack(side="left")
        Button(btframe,text = "退出",command = top.destroy).pack(side = "right")
    elif type == "dilate":
        lb["text"] = """膨胀：\n 膨胀运算是用原始图像像元值与\n[[0,1,0],\n[1,2,1],\n[0,1,0]]\n的结构元素相加，取最大值赋给结果图像相应像元得到的。关于灰度膨胀的效果有：1如果所有结构元素都为正，输出图像趋向于比原始图像更亮；2 膨胀所用结构元素的值和形状决定了暗细节是被减少还是被完全消除。"""
        Button(btframe,text ="确认运算",command = lambda:getdilateband(gray,True)).pack(side="left")
        Button(btframe,text = "退出",command = top.destroy).pack(side = "right")
    elif type == "open":
        lb["text"] = """开运算：\n 开运算将对原始图像先腐蚀后膨胀。开运算常用于消除图像中相对于结构元素而言较小的明亮细节，同时保持整体的灰度级和较明亮的区域相对不变。"""
        Button(btframe,text ="确认运算",command = lambda:getopenband(gray,True)).pack(side="left")
        Button(btframe,text = "退出",command = top.destroy).pack(side = "right")
    elif type == "close":
        lb["text"] = """闭运算：\n 闭运算将对原始图像先膨胀后腐蚀。闭运算常用于消除图像中相对于结构元素而言较小的暗细节，同时保持整体的灰度级和较大的暗区域相对不变。"""
        Button(btframe,text ="确认运算",command = lambda:getcloseband(gray,True)).pack(side="left")
        Button(btframe,text = "退出",command = top.destroy).pack(side = "right")
    elif type == "erosiongrad":
        lb["text"] = """腐蚀型梯度：\n 即原始图像与腐蚀图像之间的算术差。"""
        Button(btframe,text ="确认运算",command = lambda:geterosiongrad(gray,True)).pack(side="left")
        Button(btframe,text = "退出",command = top.destroy).pack(side = "right")
    elif type == "dilategrad":
        lb["text"] = """膨胀型梯度：\n 即膨胀图像与原始图像之间的算术差。"""
        Button(btframe,text ="确认运算",command = lambda:getdilategrad(gray,True)).pack(side="left")
        Button(btframe,text = "退出",command = top.destroy).pack(side = "right")
    elif type == "dilate_erosion":
        lb["text"] = """膨胀-腐蚀型梯度：\n 即膨胀图像与腐蚀图像之间的算术差。"""
        Button(btframe,text ="确认运算",command = lambda:getdilaerograd(gray,True)).pack(side="left")
        Button(btframe,text = "退出",command = top.destroy).pack(side = "right")




##############################################
def affirmlayer():  # 确认图层框上的操作
    # clearcanvas(rastercanvasframe)
    rfilename = filepath[comblayer.get()]
    global ds  # 打开文件、修改栅格图像都是对ds进行操作
    ds = gdal.Open(rfilename)
    if comb1.get() == "RGB三波段合成":
        msg["text"] = ('bands = '+np.str(ds.RasterCount))
    
        if rfilename[-3:]=="img":
            data = bandget(ds,1,2,3)
        elif ds.RasterCount>=3:
            data = bandget(ds,1,2,3)
        else:
            data = bandget(ds,1,1,1)
        
        draw2canvas(data)
    else:
        band = comb1.get()
        data = bandget(ds,rasterbands[band], rasterbands[band], rasterbands[band])
        draw2canvas(data)


# # 确认图层及显示文件操作
# def showimg():
#     global ds  # 打开文件、修改栅格图像都是对ds进行操作
#     ds = gdal.Open(rfilename)
#     msg["text"] = ('bands = '+np.str(ds.RasterCount))
    
#     if rfilename[-3:]=="img":
#         data = bandget(ds,1,2,3)
#     elif ds.RasterCount>=3:
#         data = bandget(ds,1,2,3)
#     else:
#         data = bandget(ds,1,1,1)
    
#     draw2canvas(data)

####################################################
#GUI maker

def guide():
    showinfo("guide","This GUI is so easy to use, have a try by yourself!!")


def Copyright():
    showinfo("Copyright","""Apache License
                    Version 2.0, January 2004
                    http://www.apache.org/licenses/
                         """)


def developer():
    showinfo("开发者","Joker.Lord       joker.lord@foxmail.com      https://github.com/JokerDLord")

def makemenu(parent):
    menubar = Frame(parent)                      
    menubar.pack(side=TOP, fill=X)

    fbutton = Menubutton(menubar, text='文件')
    fbutton.pack(side=LEFT)
    file = Menu(fbutton, tearoff=False)
    file.add_command(label='打开栅格文件',  command=openrasterfile,     underline=0)
    file.add_command(label='退出',    command=root.destroy, underline=0)
    fbutton.config(menu=file)
    
    raybutton = Menubutton(menubar, text='灰度变换/直方图调整', underline=0)
    raybutton.pack(side=LEFT)
    ray = Menu(raybutton,tearoff = False)
    ray.add_command(label='RGB-灰度值',command = rgb2gray, underline=0)
    ray.add_command(label='灰度值统计直方图',command = graystat, underline=0)
    ray.add_command(label='灰度值反比变换处理',command = graycontra, underline=0)
    ray.add_command(label='灰度值二值化处理',command = graybina, underline=0)
    ray.add_command(label='灰度值归一化处理',command = gray21, underline=0)
    ray.add_command(label='灰度直方图均衡化处理',command = grayequalization, underline=0)
    raybutton.config(menu = ray)

    bandbutton = Menubutton(menubar, text='波段运算', underline=0)
    bandbutton.pack(side=LEFT)
    ba = Menu(bandbutton,tearoff = False)
    ba.add_command(label='NDVI',command = getNDVI, underline=0)
    bandbutton.config(menu = ba)

    localbutton = Menubutton(menubar, text='邻域运算', underline=0)
    localbutton.pack(side=LEFT)
    convo = Menu(localbutton,tearoff = False)
    convo.add_command(label='卷积运算',command = convolutionwin, underline=0)
    localbutton.config(menu = convo)

    graysbutton = Menubutton(menubar, text='灰度形态学梯度运算', underline=0)
    graysbutton.pack(side=LEFT)
    grays = Menu(graysbutton,tearoff = False)
    grays.add_command(label='腐蚀',command = lambda:grayscale("erosion"), underline=0)
    grays.add_command(label='膨胀',command = lambda:grayscale("dilate"), underline=0)
    grays.add_command(label='开运算',command = lambda:grayscale("open"), underline=0)
    grays.add_command(label='闭运算',command = lambda:grayscale("close"), underline=0)
    grays.add_command(label='腐蚀型梯度',command = lambda:grayscale("erosiongrad"), underline=0)
    grays.add_command(label='膨胀型梯度',command = lambda:grayscale("dilategrad"), underline=0)
    grays.add_command(label='膨胀-腐蚀型梯度',command = lambda:grayscale("dilate_erosion"), underline=0)
    graysbutton.config(menu = grays)

    vbutton = Menubutton(menubar, text='帮助', underline=0)
    vbutton.pack(side=LEFT)
    edit = Menu(vbutton, tearoff=False)
    edit.add_command(label='使用说明',   command=guide,     underline=0)
    edit.add_command(label='版权信息',     command=Copyright,     underline=0)
    edit.add_command(label='开发者',   command=developer,     underline=0)
    
    # edit.add_separator()
    vbutton.config(menu=edit)
    # submenu = Menu(edit, tearoff=True)
    # submenu.add_command(label='Spam', command=parent.quit, underline=0)
    # submenu.add_command(label='Eggs', command=notdone,     underline=0)
    # edit.add_cascade(label='Stuff',   menu=submenu,        underline=0)
    return menubar



if __name__ == "__main__":
    # global rfilename

    widd = 1200

    root = Tk()
    root.geometry("{}x720".format(widd))                      # or Toplevel()
    # root.resizable(0, 0)
    root.title('remote process')                   # set window-mgr info
    makemenu(root)
    

    rootframe = Frame(root, width=widd, height=500, bg='#3b3a4a')
    rootframe.pack(expand=1, fill=BOTH)

    # 创建图层操作frame
    layerframe = Frame(rootframe, width=400, height=500, bg='white')
    #layerframe.pack(side="left", expand=0, fill=BOTH)
    layerframe.pack(side="left", expand=0, fill=BOTH)

    canvasframe = Frame(rootframe, width=600, height=500, bg='#c0c0c8')
    canvasframe.pack(side="left", expand=1, fill=BOTH)

    # 开始了
    photo1 = PhotoImage(file="photos/road.gif")
    lb = Label(layerframe, width=400, height=500, bg="white" ,image=photo1)#
    lb.pack(fill=BOTH, expand=1)
    #lb.grid(row=0, column=0, sticky=NSEW)



    Label(lb, text="请选择显示波段数").grid(row=0, column=0, sticky=NSEW)
    cv1 = StringVar()
    comb1 = ttk.Combobox(lb, textvariable=cv1)
    comb1.grid(row=1, column=0, sticky=NSEW)
    comb1["values"] = ("RGB三波段合成","波段1", "波段2", "波段3",
                       "波段4", "波段5", "波段6","波段7")
    rasterbands = {"RGB三波段合成":999,"波段1": 1, "波段2": 2, "波段3": 3,"波段4":4, "波段5":5, "波段6":6,"波段7":7}


    Label(lb, text="请选择显示的图层").grid(row=2, column=0, sticky=NSEW)
    # btshowlayer = Button(lb,text = "显示影像",command = showimg)
    # btshowlayer.grid(row=1, column=1, sticky=NSEW)

    cv0 = StringVar()
    comblayer = ttk.Combobox(lb, textvariable=cv0)
    comblayer.grid(row=3, column=0, sticky=NSEW)
    listb1 = Listbox(lb)
    listb1.grid(row=4, column=0, sticky=NSEW)
    layers = [] #用于存储多个打开的文件地址 以便选择不同的图层
    filepath = {"1":None} #字典用于从comb到文件path的查询
    btlayerok = Button(lb, text="显示影像", command=affirmlayer)
    btlayerok.grid(row=5, column=0, sticky=NSEW)
    ##########

    Labelframe = Frame(root, width=widd, height=20, bg='gray')
    Labelframe.pack(expand=0, fill=BOTH)
    msg = Label(Labelframe, text='bands = ',
                bg='gray')        # add something below
    msg.pack(side="left", expand=0, fill=BOTH)

    copyright = Label(Labelframe,text = "Copyright © 2019 Joker.Lord All Rights Reserved.")
    copyright.pack(side = "right",expand = 0,fill=BOTH)

    root.mainloop()


# add_separator  生成分割线
# underline 设定键盘快捷键
# tearoff = False 消除顶部的虚线
