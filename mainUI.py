# -- coding: utf-8 --
from email.mime import image
import requests
import json
import tkinter as tk
import re
from tkinter import scrolledtext
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
import pymysql as py
from PIL import Image,ImageTk
import os
from mutagen.mp3 import MP3
import pygame as pg
from glob import glob
from repath import resource_path,re_imagesize
from urllib.request import urlretrieve
from urllib.request import urlretrieve
from urllib.parse import quote
#---
#图片资源路径
rep1=resource_path(os.path.join("image","主页面图标.ico"))
rep2=resource_path(os.path.join("image","设置图标.ico"))
rep3=resource_path(os.path.join("image","壁纸.jpg"))
rep4=resource_path(os.path.join("image","封面.jpg"))
rep5=resource_path(os.path.join("image","播放.png"))
rep6=resource_path(os.path.join("image","上一首.png"))
rep7=resource_path(os.path.join("image","下一首.png"))
rep8=resource_path(os.path.join("image","音乐.ico"))
rep9=resource_path(os.path.join("image","视频.ico"))
rep10=resource_path(os.path.join("image","错过的烟火.jpg"))
rep12=resource_path(os.path.join("image","播放器背景4.jpg"))
#全局变量
m_bg2=None
fun2_bg2=None
photo1=None
photo2=None
photo3=None
count=0
tempcount=0
flag=False
loopplay=-1
nextplay=0
paused=False
play=-1
ischanged=False
rids=list()    # 存储歌曲rid的列表
musicNames=list()   # 歌曲名称的列表,list()将元组转换为列表
musicPic=[]#存储歌曲封面的列表
video_list=[]
url_list=[]#两个列表用来存储视频名称和视频对应url
url=None
sreach_pf=None
#主页面窗口
main_window=tk.Tk()
width = 1280
heigh = 800
screenwidth = main_window.winfo_screenwidth()
screenheight = main_window.winfo_screenheight()#获取屏幕宽高
main_window.geometry('%dx%d+%d+%d'%(width, heigh, (screenwidth-width)/2, (screenheight-heigh)/2))
main_window.resizable(0,0)
main_window.title('控制中心')
main_window.iconbitmap(rep1)#设置图标
main_window.config(bg='pink')
main_text=tk.Label(main_window,bg='pink',text='技术宅拯救世界',font=('楷体',60))
main_text.place(relx=0.35,rely=0.3,relwidth=0.5,relheight=0.2)
#====================================================================================






#功能区自定义函数区
#====================================================================================
#功能一frame和label框架
def fun1_change_frame():
    fun1_frame=tk.Frame(main_window)
    fun1_frame.place(relx=0.2,rely=0,relheight=1,relwidth=0.8)
    #rep3=Image.open(rep3)
    #fun1_bg_image=ImageTk.PhotoImage(re_imagesize(1280*0.8,800,rep3))
    fun1_label=tk.Label(fun1_frame,bg='#0c212b')
    fun1_label.place(relx=0,rely=0,relheight=1,relwidth=1)
    #音乐爬取toplevel窗口
    #====================================================================================
    def get_music_tl():
        def sreach():
            global rids,musicNames,url,musicPic
            musicName=entry.get()
            encodName=quote(musicName)#将单个字符串编码转化为 %xx 的形式
            #利用网站歌曲搜索框查找含歌名特定字段的网页地址
            url='https://www.kuwo.cn/api/www/search/searchMusicBykeyWord?key={}&pn=1&rn=30&httpsStatus=1'.format(encodName)
            #这里其实是寻找searchMusicBykeyword，也就是根据关键词查找的意思，说明这是对应搜索框url。reqId是可变的，所以删掉，保留有用的
            #'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='是网易云的搜索url,但是负载数据是变化的，所以没法通过搜索进行爬取
            #网易云的音频格式是m4a的，要自己用ffmpeg库转换
            referer='https://www.kuwo.cn/search/list?key={}'.format(encodName)
            # 请求头
            headers = {
                "Cookie": "_ga=GA1.2.843450869.1625216560; _gid=GA1.2.1174274874.1658845221; Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1658845221,1658891019; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1658891037; kw_token=MFJUKGMR3UC",
                "csrf": "MFJUKGMR3UC",
                "Referer": "{}".format(referer),
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71",
            }
            response=requests.get(url=url,headers=headers)#对服务器发送请求，并将返回结果赋予response上
            music_list=json.loads(response.text)#字符串转换为python对象
            misicInfo=[]
            misicInfo=music_list['data']['list']  #获取歌曲信息的列表
            musicNames=[]
            rids=[]
            musicPic=[]#把歌名、rid和封面列表重置
            text.delete(1.0,'end')
            for i in range(len(misicInfo)):#list下的每一段关键信息取出
                name=misicInfo[i]['name']+'-'+misicInfo[i]['artist']
                musicNames.append(name)
                rids.append(misicInfo[i]['rid'])
                musicPic.append(misicInfo[i]['pic'])#封面url放入列表
                mp=misicInfo[i]['pic']
                print('【{}】->>>{} {}'.format(i+1,name,mp))
                text.insert(tk.INSERT,'\n【{}】->>>{}\n'.format(i+1,name))#歌曲信息显示在列表内
        def save_music_mp3():
            global rids,musicNames,url,musicPic
            id=int(rid_entry.get())
            musicRid=rids[id-1]
            #通过歌曲rid搜索歌曲地址
            url2='http://www.kuwo.cn/api/v1/www/music/playUrl?mid={}&type=convert_url3&httpstatus=1&br=320kmp3'.format(musicRid)
            #真正的歌曲地址
            headers2={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
            response2=requests.get(url=url2,headers=headers2)
            print(response2)#<Response [200]>就是请求成功
            dict1=json.loads(response2.text)#转换为python对象
            downloadUrl=dict1['data']['url']#歌曲下载地址
            downloadPicUrl=musicPic[id-1]#从封面url列表取出需要下载的歌曲封面url
            dirname=os.path.dirname(os.path.realpath(__file__))
            file_list = glob('music/*.mp3') #从当前目录得到一个音乐资源列表
            print(file_list)
            music_list=[]
            music_list.extend(file_list)#资源文件拼接至播放列表
            music_exist=0#检查歌曲是否已存在
            for i in range(len(music_list)):
                if  'music\\'+musicNames[id-1]+'.mp3'==music_list[i]:
                    showerror('提示','歌曲已存在！')
                    music_exist=1
            if music_exist==0:
                urlretrieve(url=downloadUrl,filename=dirname+'/music/{}.mp3'.format(musicNames[id-1]))  # 下载歌曲
                urlretrieve(url=downloadPicUrl,filename=dirname+'/musicPic/{}.jpg'.format(musicNames[id-1]))  #下载歌曲封面
                print('下载完成')
                showinfo('提示','下载完成！')
            fun1_frame_tl.deiconify()
        # 爬取音乐主窗口
        fun1_frame_tl=tk.Toplevel()
        fun1_frame_tl.title('音乐爬取')
        fun1_frame_tl.geometry('%dx%d+%d+%d'%(500,500,(screenwidth-500)/2, (screenheight-500)/2))
        fun1_frame_tl.resizable(0,0)
        fun1_frame_tl.iconbitmap(rep8)
        # 标签组件
        label = tk.Label(fun1_frame_tl,text="请输入要查找的歌曲名:",font=('楷体',15))
        label.place(relx=0,rely=0,relheight=0.1,relwidth=0.4)
        rid_label = tk.Label(fun1_frame_tl,text="请输入要下载的歌曲序号:",font=('楷体',15))
        rid_label.place(relx=0,rely=0.1,relheight=0.1,relwidth=0.4)
        # 输入框组件
        entry = tk.Entry(fun1_frame_tl,font=('宋体',12))
        entry.place(relx=0.4,rely=0,relheight=0.1,relwidth=0.6)
        rid_entry = tk.Entry(fun1_frame_tl,font=('宋体',12))
        rid_entry.place(relx=0.4,rely=0.1,relheight=0.1,relwidth=0.6)
        # 歌曲列表框
        text = scrolledtext.ScrolledText(fun1_frame_tl,font=('楷体',16))
        text.place(relx=0,rely=0.2,relwidth=1,relheight=0.4)
        # 搜索按钮
        music_search=tk.Button(fun1_frame_tl,text='搜索',font=('楷体',15),command=sreach)
        music_search.place(relx=0.9,rely=0,relheight=0.1,relwidth=0.1)
        # 下载按钮
        button1 = tk.Button(fun1_frame_tl,text='开始下载',font=('楷体',15),command=save_music_mp3)
        button1.place(relx=0,rely=0.6,relwidth=1,relheight=0.2)
        #tips框
        tips=tk.Label(fun1_frame_tl,text='tips：下载后的音乐可在播放器或music文件夹查看\n如果下载后遇到歌曲无法切换等问题，可以重启再试\n 还有什么问题可以询问作者')
        tips.place(relx=0,rely=0.8,relheight=0.2,relwidth=1)
    #====================================================================================

    #资源爬取功能主页面
    #====================================================================================
    global rep4,im2
    im1=Image.open(rep4)
    im1=im1.resize((400,400))
    im2=ImageTk.PhotoImage(im1)
    text_label=tk.Label(fun1_frame,text='音乐爬取窗口(请点击图片)')
    text_label.place(relx=0.4,rely=0.1,relwidth=0.2,relheight=0.1)
    b_music_tl=tk.Button(fun1_frame,image=im2,width=400,height=400,command=get_music_tl)
    b_music_tl.place(relx=0.3,rely=0.2)





#功能二frame和label框架
def fun2_change_frame():
    global rep8,fun2_bg2
    fun2_frame=tk.Frame(main_window)
    fun2_frame.place(relx=0.2,rely=0,relheight=1,relwidth=0.8)
    fun2_bg=Image.open(rep12)
    fun2_bg1=fun2_bg.resize((1024,800))
    fun2_bg2=ImageTk.PhotoImage(fun2_bg1)
    fun2_label=tk.Label(fun2_frame,bg='black',image=fun2_bg2)
    fun2_label.place(relx=0,rely=0,relheight=1,relwidth=1)

    
    #播放列表
    dirname=os.path.dirname(os.path.realpath(__file__))#获取当前文件所在文件夹路径
    file_list = glob('music/*.mp3') #从当前目录得到一个音乐资源列表
    music_list=[]
    music_list.extend(file_list)#资源文件拼接至播放列表

    #音乐时长列表
    music_len=[]
    for tik in range(len(music_list)): #range(播放列表长度)代表从0到第x首音乐的序号
        music = MP3(music_list[tik])  #把第x首音乐转为MP3格式
        music_len.append(music.info.length)

    #播放列表可视化
    scr1 = scrolledtext.ScrolledText(fun2_frame, bg="#CCCCFF", width=18, height=15,font=("经典雅黑",10))
    #滚动文本框（宽，高（这里的高应该是以行数为单位），字体样式）
    scr1.insert(tk.INSERT, '播放列表:\n'  )
    scr1.place(relx=0.8,rely=0.2,relheight=0.3,relwidth=0.15) #滚动文本框在页面的位置
    for num in range(len(music_list)):
        scr1.insert(tk.INSERT, '\n%d. %s (%d秒)\n' % (num+1, music_list[num],music_len[num]))
    scr2 = scrolledtext.ScrolledText(fun2_frame, bg="#CCCCFF", font=("经典雅黑",10))
    scr2.insert(tk.INSERT, '播放记录:\n'  )
    scr2.place(relx=0.02,rely=0.2,relheight=0.3,relwidth=0.15)
    
    #列表下拉选项
    cmb = ttk.Combobox(fun2_frame)
    cmb['value'] = music_list
    cmb.current(0)
    cmb.place(relx=0.8,rely=0.1,relwidth=0.15)

    #列表歌曲选中
    def sel_t():
        global count
        pg.mixer.init()#初始化播放组件
        for num in range(len(music_list)):
            if cmb.get() == music_list[num]:
                count = num   
    #实现轮回切歌
    def last_one():
        global count
        global flag
        if count != 0:
            count -= 1
            flag = False
            replay()
        else:
            flag = False
            count = len(music_list)-1
            replay()
    def next_one():
        global count
        global flag
        if count != len(music_list)-1:
            count += 1
            flag = False
            replay()
        else:
            flag = False
            count = 0
            replay()

    #单曲循环函数
    def set_loopplay():
        global play
        play=loopplay
    #轮换播放函数
    def set_nextplay():
        global play
        play=nextplay

    #封面切换
    def changePic(count):
        global rep10,bgpic2
        musicPic_list=glob('musicPic/*.jpg')
        rep10=musicPic_list[count]
        bgpic1=Image.open(rep10)
        bgpic1=bgpic1.resize((400,400))
        bgpic2=ImageTk.PhotoImage(bgpic1)
        m_bg_label.config(image=bgpic2)
    #播放主功能函数
    def replay():
        pg.mixer.init() # 初始化
        global play,paused,flag,tempcount,count,rep10
        if (pg.mixer.music.get_busy()==False and flag!=True) or tempcount!=count:
            flag = True
            tempcount=count
            pg.mixer.music.load(music_list[count])
            pg.mixer.music.set_volume(((scale2.get())/100))
            pg.mixer.music.play(play, 0.3)
            # 播放  第一个是播放值 -1代表当前单曲循环播放，第二个参数代表开始播放的时间
            scr2.insert(tk.INSERT, '%s\n\n' % music_list[count])
            print("正在播放：", music_list[count])
            changePic(count)
        elif pg.mixer.music.get_busy()==True and tempcount==count:
            pg.mixer.music.pause()
            paused=True         
        elif pg.mixer.music.get_busy()==True and tempcount!=count:
            flag = True
            tempcount=count
            pg.mixer.music.load(music_list[count])
            pg.mixer.music.set_volume(((scale2.get())/100))
            pg.mixer.music.play(play, 0.3)
            scr2.insert(tk.INSERT, '%s\n\n' % music_list[count])
            print("正在播放：", music_list[count])
        elif pg.mixer.music.get_busy()==False and tempcount!=count:
            flag = True
            tempcount=count
            pg.mixer.music.load(music_list[count])
            pg.mixer.music.set_volume(((scale2.get())/100))
            pg.mixer.music.play(play, 0.3)
            scr2.insert(tk.INSERT, '%s\n\n' % music_list[count])
            print("正在播放：", music_list[count])
        elif pg.mixer.music.get_busy()==False and flag==True and tempcount==count:
            pg.mixer.music.unpause()#继续播放
            paused=False
            print("继续播放：", music_list[count])
    #播放器进度条
    def jump_to1(self):
        #这里给一个参数是因为不给的话程序会自动传一个self参数给此函数，所以会报错：takes 0 positional arguments but 1 was given
        global count,ischanged,flag
        if flag==True:#有歌曲正在进行中
            if pg.mixer.music.get_busy()==False:#暂停状态
                pg.mixer.music.unpause()
            pg.mixer.music.set_pos(scale1.get())        
    scale1 = tk.Scale(fun2_frame, from_=0, to=int(max(music_len)),activebackground='#145b7d',cursor='fleur',
    bg='#CCCCFF' ,orient='horizonta', showvalue=False, command=jump_to1)
    scale1.place(relwidth=0.4,relheight=0.03,relx=0.3,rely=0.72)
    #播放器音量条
    def set_voice(self):
        pg.mixer.music.set_volume(((scale2.get())/100))
    scale2=tk.Scale(fun2_frame,from_=100,to=0,orient='vertical',activebackground='#145b7d',cursor='fleur',
    bg='#CCCCFF',showvalue=False,command=set_voice)
    scale2.place(relx=0.7,rely=0.55,relheight=0.2,relwidth=0.02)
    #插画
    global m_bg2#必须声明全局变量，否则不显示
    m_bg=Image.open(rep10)
    m_bg1=m_bg.resize((400,400))
    m_bg2=ImageTk.PhotoImage(m_bg1)
    m_bg_label=tk.Label(fun2_frame,image=m_bg2,width=405,height=400)
    m_bg_label.config(image=m_bg2)
    m_bg_label.place(relx=0.3,rely=0.2)

         

    #按钮布局
    global photo1,photo2,photo3
    im_play=Image.open(rep5)
    im_play=im_play.resize((50,40))
    photo1 = ImageTk.PhotoImage(im_play)
    btn1 = tk.Button(fun2_frame, text="播放",image=photo1,font = ("经典雅黑", 12),width=50,height=40,command = replay)
    btn1.place(relx=0.48,rely=0.77)

    im_last=Image.open(rep6)
    im_last=im_last.resize((50,40))
    photo2 = ImageTk.PhotoImage(im_last)
    btn2 = tk.Button(fun2_frame, text="上一首",image = photo2,height=40, width=50,  command = last_one)
    btn2.place(relx=0.4,rely=0.77)

    im_next=Image.open(rep7)
    im_next=im_next.resize((50,40))
    photo3 = ImageTk.PhotoImage(im_next)
    btn3 = tk.Button(fun2_frame, text="下一首",image = photo3,height=40, width=50,command = next_one)
    btn3.place(relx=0.56,rely=0.77)

    btn6 = tk.Button(fun2_frame, text="选择", font = ("经典雅黑", 10),  bg="#CCCCFF", command =sel_t)
    btn6.place(relx=0.75,rely=0.1,relwidth=0.03,relheight=0.03)
    btn7 = tk.Button(fun2_frame, text="单曲循环", font = ("经典雅黑", 10),  bg="#CCCCFF", command =set_loopplay)
    btn7.place(relheight=0.05,relwidth=0.05,rely=0.7,relx=0.8)
    btn8 = tk.Button(fun2_frame, text="播放一次", font = ("经典雅黑", 10),  bg="#CCCCFF", command =set_nextplay)
    btn8.place(relheight=0.05,relwidth=0.05,rely=0.7,relx=0.9)
    #btn9 = tk.Button(fun2_frame, text="刷新播放进度", font = ("经典雅黑", 10), height=1, width=7, bg="#CCCCFF", command =set_scale)
    #btn9.place(x=50,y=515)


#功能三frame和label框架
#====================================================================================







#菜单栏自定义函数区
#====================================================================================
#toplevel窗口
def about_author():
    author=tk.Toplevel()
    author.title('关于作者')
    author.geometry('500x500+%d+%d'%((screenwidth-500)/2, (screenheight-500)/2))
    author.iconbitmap(rep1)
    text=tk.Label(author,text='作者联系方式：qq2419452155\n本产品目前应该不会再继续更新，更多功能可能需要以后才会添加\n'
    '对于python，作者只是入门水平，所以有什么高见欢迎指导\n本产品严谨用于盈利，严禁私自随意传播，仅供个人学习娱乐\n'
    '如果歌曲无法爬取了，有可能是歌曲爬取的源网站发生了变化,\n请联系作者进行修复',font=('楷体',12))
    text.place(relx=0,rely=0,relwidth=1,relheight=1)
def about_help():
    help=tk.Toplevel()
    help.title('常见问题')
    help.geometry('500x500+%d+%d'%((screenwidth-500)/2, (screenheight-500)/2))
    help.iconbitmap(rep1)
    text=tk.Label(help,text='1.爬取工具使用时请输入歌曲名称或歌手名称\n2.播放器暂不支持列表循环播放\n'
    '3.页面切换后会自动刷新，不影响使用\n4.播放歌曲请一定要在右上角点击选择后再按播放按钮进行播放！'
    '\n5.万事皆可重启程序\n6.还不行就找作者！',font=('楷体',12))
    text.place(relx=0,rely=0,relwidth=1,relheight=1)
def about_set():
    set=tk.Toplevel()
    set.title('设置')
    set.geometry('500x500+%d+%d'%((screenwidth-500)/2, (screenheight-500)/2))
    set.iconbitmap(rep2)
    #toplevel设置窗口
    #====================================================================================
    l_set=tk.Label(set,bg='#464547')
    l_set_font=tk.Label(set,bg='#464547',text='设置',fg='white',font=('黑体',12))
    l_set_font.place(relx=0,rely=0,relheight=0.1,relwidth=0.2)
    l_set.place(relx=0,rely=0,relwidth=0.2,relheight=1)
    #主窗口透明度设置
    #左侧导航按钮
    b_set_alp=tk.Button(set,text='透明度',font=('黑体',12),bg='#464547',fg='white')
    b_set_alp.place(relx=0,rely=0.1,relheight=0.1,relwidth=0.2)
    #右侧界面框架
    set_alp=tk.Frame(set,bg='#0c212b')
    set_alp.place(relx=0.2,rely=0,relheight=1,relwidth=0.8)
    #调节主窗口透明度函数
    def set_alphanums(self):
        alphanums=1.1-(e_alp.get()/100)
        main_window.attributes('-alpha',alphanums)
    #透明度调节条
    e_alp=tk.Scale(set_alp, from_=0, to=100,activebackground='#145b7d',cursor='fleur',
    bg='#CCCCFF' ,orient='horizonta', showvalue=False ,command=set_alphanums)
    e_alp.place(relx=0.4,rely=0.11,relheight=0.04,relwidth=0.4)
    e_alp_text=tk.Label(set_alp,text='主窗口透明度',bg='#0c212b',fg='white',font=('黑体',15))
    e_alp_text.place(relx=0.05,rely=0.1,relheight=0.05,relwidth=0.35)
    #透明度调节提示
    tip_alp=tk.Label(set_alp,text='tip：向右调节可透明化',bg='#0c212b',font=('黑体',10),fg='white')
    tip_alp.place(relx=0.05,rely=0.15,relheight=0.05,relwidth=0.75)
    #====================================================================================

#====================================================================================








#对窗口进行布局
#====================================================================================
#左侧功能区
l_fun=tk.Label(main_window,bg='#464547')
l_fun.place(relx=0,rely=0,relwidth=0.2,relheight=1)
l_fun_text=tk.Label(main_window,text='功能区',bg='#464547',fg='white',font=('黑体',15))
l_fun_text.place(relx=0,rely=0,relwidth=0.2,relheight=0.1)
#功能一
b_fun1=tk.Button(main_window,text='资源爬取',activebackground='#4f5555',activeforeground='white',
bg='#464547',fg='white',font=('黑体',15),relief=tk.RAISED,command=fun1_change_frame)
b_fun1.place(relx=0,rely=0.1,relwidth=0.2,relheight=0.1)
#功能二
b_fun2=tk.Button(main_window,text='音乐播放器',activebackground='#4f5555',activeforeground='white',
bg='#464547',fg='white',font=('黑体',15),relief=tk.RAISED,command=fun2_change_frame)
b_fun2.place(relx=0,rely=0.2,relwidth=0.2,relheight=0.1)
#功能三

#====================================================================================
#====================================================================================
#菜单栏
#工具菜单子菜单
tool_menu_son=tk.Menu(main_window,tearoff=0,activebackground='black',activeborderwidth='5',bg='#72777b',fg='white')
tool_menu_son.add_command(label='敬请期待')
tool_menu_son.add_command(label='设置',underline=0,command=about_set)
#帮助菜单子菜单
help_menu_son=tk.Menu(main_window,tearoff=0,activebackground='black',activeborderwidth='5',bg='#72777b',fg='white')
help_menu_son.add_command(label='常见问题',underline=0,command=about_help)
help_menu_son.add_command(label='关于作者',underline=0,command=about_author)
#主菜单
menu=tk.Menu(main_window)
menu.add_cascade(label='工具',menu=tool_menu_son)
menu.add_cascade(label='帮助',menu=help_menu_son)
main_window.config(menu=menu)
#====================================================================================






main_window.mainloop()