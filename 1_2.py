from numpy import mean,std
'''
def storage():
    
    lst = input("请输入1978-2018改革开放40周年来的GDP数据（空格分隔）").split()
    if len(lst) is not 40:
        print("输入错误,请重新输入数据")
        return storage()
    
    
    max_gdp = max(lst)
    min_gdp = min(lst)
    CV = std(lst)/mean(lst) #计算变异系数
    return max_gdp,min_gdp,CV

if __name__=="__main__":
    storage()
'''

with open("gdp.txt","r") as f:
    gdps = []
    for row in f:
        year,GDP = row.split(",")
        gdps.append([year,float(GDP)])

gdps.sort(key=lambda x:x[0],reverse=True)
print('GDP最大值年份 year=',gdps[0][0],'GDP=',gdps[0][1])
print('GDP最小值年份 year=',gdps[len(gdps)-1][0],'GDP=',gdps[len(gdps)-1][1])

gdp = []
for i in gdps:
    gdp.append(i[1])
CV = std(gdp)/mean(gdp) #计算变异系数
print("平均值为{}".format(mean(gdp)))
print('C.V=',CV)