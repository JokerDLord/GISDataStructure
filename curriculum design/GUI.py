from tkinter import *                              # get widget classes
from tkinter.messagebox import *                   # get standard dialogs
from tkinter.filedialog import askopenfilename        # get standard dialogs

from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import *
from matplotlib.backend_bases import key_press_handler

# from RasterAnalysis import *


class GUI:
    def __init__(self):
        self.filename = None


def notdone():
    showerror('Not implemented', 'Not yet available')

# 打开文件操作


def openfile():
    global rfilename
    rfilename = askopenfilename()
    if rfilename:
        showinfo("openfile", "successfully loaded!!!")
    print(rfilename)

# 显示文件操作


def showimg():
    ds = gdal.Open(rfilename)
    print('bands=: '+np.str(ds.RasterCount))  # 波段数
    msg["text"] = 'mouse location @ ' + ('bands = '+np.str(ds.RasterCount))

    f = Figure(figsize=(5, 4), dpi=100)
    a = f.add_subplot(111)
    # 把绘制的图形显示到tkinter窗口上
    tifwin = FigureCanvasTkAgg(f, master=rootframe)
    # tifwin.show()
    # tifwin.get_tk_widget().pack( fill=BOTH, expand=1)
    tifwin.get_tk_widget().pack(fill=BOTH, expand=1)

    b = ds.GetRasterBand(1).ReadAsArray()
    g = ds.GetRasterBand(2).ReadAsArray()
    r = ds.GetRasterBand(3).ReadAsArray()
    data = np.dstack((b, g, r))
    a.imshow(data)
    tifwin.draw()

    # matplotlib的导航工具栏显示上来(默认是不会显示它的)
    toolbar = NavigationToolbar2Tk(tifwin, rootframe)
    toolbar.update()
    # get_tk_widget()得到的就是_tkcanvas
    tifwin._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)


def makemenu(parent):
    menubar = Frame(parent)                        # relief=RAISED, bd=2...
    menubar.pack(side=TOP, fill=X)

    fbutton = Menubutton(menubar, text='File')
    fbutton.pack(side=LEFT)
    file = Menu(fbutton)
    file.add_command(label='open',  command=openfile,     underline=0)
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

    root = Tk()
    root.geometry("1000x600")                      # or Toplevel()
    # root.resizable(0, 0)
    root.title('remote process')                   # set window-mgr info
    makemenu(root)                                     # associate a menu bar
    # add something below
    toolbarframe = Frame(root, width=1500, height=20, bg='gray')
    toolbarframe.pack(expand=1, fill=BOTH)
    btaddtiffile = Button(toolbarframe, bg='gray',
                          text="show", command=showimg)
    btaddtiffile.pack(side="left")

    rootframe = Frame(root, width=1000, height=500, bg='white')
    rootframe.pack(expand=1, fill=BOTH)

    # 创建图层操作frame
    layerframe = Frame(rootframe, width=400, height=500, bg='lightgray')
    layerframe.pack(side="left", expand=0, fill=BOTH)
    # 创建画布frame
    # canvasframe = Frame(rootframe, width=600, height=500, bg='lightblue')
    # canvasframe.grid(row=0,column=1,sticky=W+E+N+S, padx=2, pady=2)
    # tifwin = Canvas(canvasframe)
    # tifwin.pack(side="right", expand=1, fill=BOTH)
    # tifwin.config(relief=SUNKEN, width=800, height=400)
    #RELIEF=["flat", "raised", "sunken", "solid", "ridge", "groove"]

    Labelframe = Frame(root, width=1500, height=20, bg='gray')
    Labelframe.pack(expand=0, fill=BOTH)
    msg = Label(Labelframe, text='mouse location @ ',
                bg='gray')        # add something below
    msg.pack(side="left", expand=0, fill=BOTH)

    root.mainloop()


# add_separator  生成分割线
# underline 设定键盘快捷键
# tearoff = False 消除顶部的虚线
