import sys
import os
from PIL import Image,ImageTk
#====================================================================================
#生成资源文件目录访问路径
def resource_path(relative_path):
    if getattr(sys, 'frozen', False): #是否Bundle Resource，查看sys中是否有frozen这变量
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")#返回绝对路径
    return os.path.join(base_path, relative_path)#把路径和文件名组合再返回
#程序打包成exe的时，会将一个变量frozen注入到sys中，
# 这里使用判断，检测sys是否有frozen这个变量，
# 如果有，就使用sys._MEIPASS访问临时文件夹路径，
# 如果没有，就使用当前路径，
# 当程序不管是以PyInstaller打包后形式运行，还是本地测试，都能找到正确的资源路径。
#====================================================================================

#====================================================================================
#背景图片
#重置图片大小自适应label大小
def re_imagesize(w_label,h_label,bg_image):
    w,h=bg_image.size
    f1=1.0*w_label/w
    f2=1.0*h_label/h
    factor=min([f1,f2])
    re_width=int(factor*w)
    re_high=int(factor*h)
    #重置后的图片size
    return bg_image.resize((re_width,re_high),Image.ANTIALIAS)
    #resize函数是pil库中的改变图片size的函数，ANTIALIAS是返回高质量图片

#====================================================================================
