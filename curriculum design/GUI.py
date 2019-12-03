from tkinter import *                              # get widget classes
from tkinter.messagebox import *                   # get standard dialogs
from tkinter.filedialog import askopenfilename        # get standard dialogs
from tkinter import ttk

from osgeo import gdal
from osgeo import ogr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import *
from matplotlib.backend_bases import key_press_handler

# from RasterAnalysis import *


def notdone():
    showerror('Not implemented', 'Not yet available')

# 打开文件操作


def openrasterfile():
    # global rfilename
    rfilename = askopenfilename()
    if rfilename:
        showinfo("openfile", "successfully loaded!!!")
    print(rfilename)
    global ds  # 打开文件、修改栅格图像都是对ds进行操作
    ds = gdal.Open(rfilename)
    print('bands=: '+np.str(ds.RasterCount))  # 波段数
    msg["text"] = 'mouse location @ ' + ('bands = '+np.str(ds.RasterCount))


def openvectorfile():
    # global vfilename
    vfilename = askopenfilename()
    if vfilename:
        showinfo("openfile", "successfully loaded!!!")
    print(vfilename)

def clearcanvas(canvas):  # 清空相应frame中的所有控件
    for widget in canvas.winfo_children():
        widget.destroy()


def bandget(b, g, r):
    clearcanvas(canvasframe)
    f = Figure(figsize=(5, 4), dpi=100)
    a = f.add_subplot(111)
    # 把绘制的图形显示到tkinter窗口上
    tifwin = FigureCanvasTkAgg(f, master=canvasframe)
    tifwin.get_tk_widget().pack(fill=BOTH, expand=1)

    b = ds.GetRasterBand(b).ReadAsArray()
    g = ds.GetRasterBand(g).ReadAsArray()
    r = ds.GetRasterBand(r).ReadAsArray()
    data = np.dstack((b, g, r))
    a.imshow(data)
    tifwin.draw()
    # matplotlib的导航工具栏显示上来(默认是不会显示它的)
    toolbar = NavigationToolbar2Tk(tifwin, canvasframe)
    toolbar.update()
    # get_tk_widget()得到的就是_tkcanvas
    tifwin._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

def vectorget():
    vs = ogr.Open(vfilename)
    lyr = vs.GetLayer(0)

    for row in lyr:
        geom = row.geometry()
        ring = geom.GetGeometryRef(0)
        coords = ring.GetPoints()
        x = []
        y = []
        if coords != None:
            for xy in coords:
                xy = list(xy)
                x.append(xy[0])
                y.append(xy[1])
                # print(x)
            plt.plot(x, y, 'k')
    plt.axis('equal')
    plt.show()

def affirmlayer():  # 确认图层框上的操作
    # clearcanvas(rastercanvasframe)

    band = comb1.get()
    bandget(rasterbands[band], rasterbands[band], rasterbands[band])
    vectorget()


# 显示文件操作
def showimg():
    #clearcanvas(rastercanvasframe)
    bandget(1, 2, 3)

    # f = Figure(figsize=(5, 4), dpi=100)
    # a = f.add_subplot(111)
    # # 把绘制的图形显示到tkinter窗口上
    # tifwin = FigureCanvasTkAgg(f, master=rootframe)
    # # tifwin.show()
    # # tifwin.get_tk_widget().pack( fill=BOTH, expand=1)
    # tifwin.get_tk_widget().pack(fill=BOTH, expand=1)

    # b = ds.GetRasterBand(1).ReadAsArray()
    # g = ds.GetRasterBand(2).ReadAsArray()
    # r = ds.GetRasterBand(3).ReadAsArray()
    # data = np.dstack((b, g, r))
    # a.imshow(data)
    # tifwin.draw()

    # # matplotlib的导航工具栏显示上来(默认是不会显示它的)
    # toolbar = NavigationToolbar2Tk(tifwin, rootframe)
    # toolbar.update()
    # # get_tk_widget()得到的就是_tkcanvas
    # tifwin._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)


def makemenu(parent):
    menubar = Frame(parent)                        # relief=RAISED, bd=2...
    menubar.pack(side=TOP, fill=X)

    fbutton = Menubutton(menubar, text='File')
    fbutton.pack(side=LEFT)
    file = Menu(fbutton)
    file.add_command(label='打开栅格文件',  command=openrasterfile,     underline=0)
    file.add_command(label='打开矢量文件',  command=openvectorfile,     underline=0)
    file.add_command(label='save', command=notdone,     underline=0)
    file.add_command(label='quit',    command=root.destroy, underline=0)
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
    toolbarframe.pack()#side="top"expand=1, fill=BOTH
    btaddtiffile = Button(toolbarframe, bg='gray',
                          text="showimg", command=showimg)
    btaddtiffile.pack(side="left")
    btaddvector = Button(toolbarframe, bg='gray',
                          text="showvector", command=vectorget)
    btaddvector.pack(side="left")

    rootframe = Frame(root, width=widd, height=500, bg='white')
    rootframe.pack(expand=1, fill=BOTH)

    # 创建图层操作frame
    layerframe = Frame(rootframe, width=400, height=500, bg='darkgray')
    #layerframe.pack(side="left", expand=0, fill=BOTH)
    layerframe.pack(side="left", expand=0, fill=BOTH)#

    canvasframe = Frame(rootframe, width=600, height=500, bg='white')
    canvasframe.pack(side="left", expand=1, fill=BOTH)

    #####开始了
    photo = PhotoImage(file="photos/road.gif")
    lb = Label(layerframe, width=400, height=500,bg="yellow", image=photo)#
    lb.pack(fill=BOTH,expand=1)
    #lb.grid(row=0, column=0, sticky=NSEW)

    Label(lb, text="请选择显示波段数").grid(row=0, column=0, sticky=NSEW)
    cv1 = StringVar()
    comb1 = ttk.Combobox(lb, textvariable=cv1)
    comb1.grid(row=1, column=0,sticky=NSEW)
    comb1["values"] = ("波段1(蓝)", "波段2(绿)", "波段3(红)",
                       "波段4", "波段5", "波段6", "波段7") 
    rasterbands = {"波段1(蓝)":1,"波段2(绿)":2, "波段3(红)":3}
    btlayerok = Button(lb,text="OK",command=affirmlayer)
    btlayerok.grid(row=1,column=1,sticky=NSEW)
    ##########

    Labelframe = Frame(root, width=widd, height=20, bg='gray')
    Labelframe.pack(expand=0, fill=BOTH)
    msg = Label(Labelframe, text='mouse location @ ',
                bg='gray')        # add something below
    msg.pack(side="left", expand=0, fill=BOTH)

    rfilename=None
    vfilename=None

    root.mainloop()


# add_separator  生成分割线
# underline 设定键盘快捷键
# tearoff = False 消除顶部的虚线