from tkinter import *                              # get widget classes
from tkinter.messagebox import *                   # get standard dialogs
from tkinter.filedialog import askopenfilename        # get standard dialogs
from tkinter import ttk

from osgeo import gdal, gdalconst, ogr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
font = FontProperties(fname="C:\Windows\Fonts\msyh.ttc")
from matplotlib.figure import Figure
from matplotlib.colors import NoNorm
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import *
from matplotlib.backend_bases import key_press_handler

# from RasterAnalysis import *


def notdone():
    showerror('Not implemented', 'Not yet available')

# 打开文件操作


def openrasterfile():
    global rfilename
    rfilename = askopenfilename()
    if rfilename:
        showinfo("openfile", "successfully loaded!!!")
    print(rfilename)
    global ds  # 打开文件、修改栅格图像都是对ds进行操作
    ds = gdal.Open(rfilename)
    print('bands : '+np.str(ds.RasterCount))  # 波段数
    msg["text"] = 'mouse location @ ' + ('bands = '+np.str(ds.RasterCount))


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
    print(data)


    return data

def draw2canvas(data):
    clearcanvas(canvasframe)  # 清除原来canvas上的空间，重新绘制单个波段的图像
    f = Figure(figsize=(5, 4), dpi=100)
    a = f.add_subplot(111)
    # 把绘制的图形显示到tkinter窗口上
    tifwin = FigureCanvasTkAgg(f, master=canvasframe)
    tifwin.get_tk_widget().pack(fill=BOTH, expand=1)
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
    dnmin = np.min(grayband)
    dnmax = np.max(grayband)
    if dnmin<0 or dnmax>255:
        grayband = ((grayband-dnmin)/(dnmax-dnmin)*255).astype(int)
    return grayband


#计算rgb图的灰度图
def rgb2gray():
    grayband = getgray()
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

#灰度二值化处理
def graybina():
    grayband = getgray()
    medline = np.median(grayband)
    binaband = np.where(grayband < medline, 0, 255)
    data = np.dstack((binaband,binaband,binaband))
    draw2canvas(data)

#灰度值归一化处理
def gray21():
    grayband = getgray()
    gmax = np.max(grayband)
    gmin = np.min(grayband)
    print(gmax,gmin)
    gray21band = (grayband-gmin)/(gmax-gmin)##将原rgb转得的像元值进行在0-1区间的归一化处理
    gray21band=gray21band.astype("float")
    data = np.dstack((gray21band,gray21band,gray21band))
    draw2canvas(data)


#灰度值均衡化处理 提升对比度

# 灰度直方图均衡化实现的步骤：
# 1.统计灰度级中每个像素在整幅图像中的个数
# 2.计算每个灰度级占图像中的概率分布
# 3.计算累计分布概率
# 4.计算均衡化之后的灰度值
# 5.映射回原来像素的坐标的像素值
def grayequalization():
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
    data = np.dstack(tuple([uniform_gray]*3))
    draw2canvas(data)
    graystat(uniform_gray)



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

def convolutioncal():
    pass


#打开新窗口，设定卷积算子
def convolutionwin():
    rootnew = Toplevel()
    label1 = Label(rootnew,text="请填入卷积滤波算子数量以实现卷积运算")
    label1.pack()


    convolutionframe = Frame(rootnew,bg = "darkgray")
    convolutionframe.pack()
    global entrylst
    entrylst = []
    for i in range(3):
        for j in range(3):
            e = Entry(convolutionframe,width = 20)
            e.grid(row = i,column=j)
            entrylst.append(e)
    
    Button(rootnew,text = "确定",command = convolutioncal).pack()
    # e1 = Entry(convolution,width = 20)
    # e.grid(row =0,column =0)
    # e1 = Entry(convolution,width = 20)
    # e.grid(row =0,column =0)
    # e1 = Entry(convolution,width = 20)
    # e.grid(row =0,column =0)
    # e1 = Entry(convolution,width = 20)
    # e.grid(row =0,column =0)
    # e1 = Entry(convolution,width = 20)
    # e.grid(row =0,column =0)
    # e1 = Entry(convolution,width = 20)
    # e.grid(row =0,column =0)
    # e1 = Entry(convolution,width = 20)
    # e.grid(row =0,column =0)
    # e1 = Entry(convolution,width = 20)
    # e.grid(row =0,column =0)
    # e1 = Entry(convolution,width = 20)
    # e.grid(row =0,column =0)


def affirmlayer():  # 确认图层框上的操作
    # clearcanvas(rastercanvasframe)

    band = comb1.get()
    data = bandget(ds,rasterbands[band], rasterbands[band], rasterbands[band])
    draw2canvas(data)


# 显示文件操作
def showimg():
    try:
        ds1 = ds.GetRasterBand(0)
    except Exception as e:
        print(repr(e))
    
    # clearcanvas(rastercanvasframe)
    if rfilename[-3:]=="img":
        data = bandget(ds,2,3,4)
    elif ds.RasterCount>=3:
        data = bandget(ds,1,2,3)
    else:
        data = bandget(ds,1,1,1)
    
    draw2canvas(data)


####################################################
#GUI maker

def makemenu(parent):
    menubar = Frame(parent)                        # relief=RAISED, bd=2...
    menubar.pack(side=TOP, fill=X)

    fbutton = Menubutton(menubar, text='File')
    fbutton.pack(side=LEFT)
    file = Menu(fbutton, tearoff=False)
    file.add_command(label='打开栅格文件',  command=openrasterfile,     underline=0)
    file.add_command(label='退出',    command=root.destroy, underline=0)
    fbutton.config(menu=file)

    vbutton = Menubutton(menubar, text='View', underline=0)
    vbutton.pack(side=LEFT)
    edit = Menu(vbutton, tearoff=False)
    edit.add_command(label='Cut',     command=notdone,     underline=0)
    edit.add_command(label='Paste',   command=notdone,     underline=0)
    # edit.add_separator()
    vbutton.config(menu=edit)

    # submenu = Menu(edit, tearoff=True)
    # submenu.add_command(label='Spam', command=parent.quit, underline=0)
    # submenu.add_command(label='Eggs', command=notdone,     underline=0)
    # edit.add_cascade(label='Stuff',   menu=submenu,        underline=0)
    return menubar

    # submenu = Menu(edit, tearoff=True)
    # submenu.add_command(label='Spam', command=win.quit, underline=0)
    # submenu.add_command(label='Eggs', command=notdone,  underline=0)
    # edit.add_cascade(label='Stuff',   menu=submenu,     underline=0)


if __name__ == "__main__":
    # global rfilename

    widd = 1200

    root = Tk()
    root.geometry("{}x600".format(widd))                      # or Toplevel()
    # root.resizable(0, 0)
    root.title('remote process')                   # set window-mgr info
    makemenu(root)                                     # associate a menu bar
    # add something below
    toolbarframe = Frame(root, width=1500, height=20, bg='gray')
    toolbarframe.pack()  # side="top"expand=1, fill=BOTH
    btaddtiffile = Button(toolbarframe, bg='gray',
                          text="显示栅格数据", command=showimg)
    btaddtiffile.pack(side="left")

    btaddgray = Button(toolbarframe, bg='gray',
                         text="RGB-灰度值", command=rgb2gray)
    btaddgray.pack(side="left")
    btgraysta = Button(toolbarframe, bg='gray',
                         text="灰度值统计直方图", command=graystat)
    btgraysta.pack(side="left")
    btbina = Button(toolbarframe, bg='gray',
                         text="灰度值二值化处理", command=graybina)
    btbina.pack(side="left")
    btgray1 = Button(toolbarframe, bg='gray',
                         text="灰度值归一化处理", command=gray21)
    btgray1.pack(side="left")
    btequalization = Button(toolbarframe, bg='gray',
                         text="灰度直方图均衡化处理", command=grayequalization)
    btequalization.pack(side="left")
    
    btaddNDVI = Button(toolbarframe, bg='gray',
                         text="NDVI", command=getNDVI)
    btaddNDVI.pack(side="left")
    btaddfilter = Button(toolbarframe,bg = "gray",text = "卷积运算",command = convolutionwin)
    btaddfilter.pack(side="left")

    

    rootframe = Frame(root, width=widd, height=500, bg='white')
    rootframe.pack(expand=1, fill=BOTH)

    # 创建图层操作frame
    layerframe = Frame(rootframe, width=400, height=500, bg='darkgray')
    #layerframe.pack(side="left", expand=0, fill=BOTH)
    layerframe.pack(side="left", expand=0, fill=BOTH)

    canvasframe = Frame(rootframe, width=600, height=500, bg='white')
    canvasframe.pack(side="left", expand=1, fill=BOTH)

    # 开始了
    photo = PhotoImage(file="photos/road.gif")
    lb = Label(layerframe, width=400, height=500, bg="white", image=photo)
    lb.pack(fill=BOTH, expand=1)
    #lb.grid(row=0, column=0, sticky=NSEW)

    Label(lb, text="请选择显示波段数").grid(row=0, column=0, sticky=NSEW)
    cv1 = StringVar()
    comb1 = ttk.Combobox(lb, textvariable=cv1)
    comb1.grid(row=1, column=0, sticky=NSEW)
    comb1["values"] = ("波段1", "波段2", "波段3",
                       "波段4(近红外)", "波段5(中红外)", "波段6(远红外)")
    rasterbands = {"波段1": 1, "波段2": 2, "波段3": 3,"波段4(近红外)":4, "波段5(中红外)":5, "波段6(远红外)":6}
    btlayerok = Button(lb, text="OK", command=affirmlayer)
    btlayerok.grid(row=1, column=1, sticky=NSEW)
    ##########

    Labelframe = Frame(root, width=widd, height=20, bg='gray')
    Labelframe.pack(expand=0, fill=BOTH)
    msg = Label(Labelframe, text='mouse location @ ',
                bg='gray')        # add something below
    msg.pack(side="left", expand=0, fill=BOTH)

    # rfilename = None
    # vfilename = None

    root.mainloop()


# add_separator  生成分割线
# underline 设定键盘快捷键
# tearoff = False 消除顶部的虚线
