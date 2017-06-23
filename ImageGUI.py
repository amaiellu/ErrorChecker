'''
Created on Jun 8, 2017

@author: amschaef
'''
import tkinter as tk
from tkinter import filedialog
from tkinter import *
from skimage.io import imread,imsave
from numpy import *
from PIL import Image,ImageTk,ImageEnhance
import pandas as pd



def _create_circle(self, x, y, r, id, **kwargs):
    #tag_bind(id,'<ButtonPress-1>',onCircleClick)
    
    return self.create_oval(x-r, y-r, x+r, y+r, tags=id, **kwargs)
tk.Canvas.create_circle = _create_circle
  

  

def LoadData(): 

    trackername=filedialog.askopenfilename()
    data=pd.read_excel(trackername,index_col=None,header=None,skiprows=[0],names=['particle','frame','x','y'],sheetname='Sheet3')
    return data
    
def OpenVidFile(): 
    global myCanvas,data
    vidname = filedialog.askopenfilename()
    im=imread(vidname)
    
    data=LoadData()
    num_frames=im.shape[0]  # find number of rames to split into
    im_frames=array_split(im,num_frames,axis=0) #split stack into individual frames
    flat_frame=[y/15 for x in im_frames[0] for y in x] # flatten first image for use, y/4 to bring values into range for tkinter?? 
    flat_frame=Image.fromarray(asarray(flat_frame))# turn into array, and then into PIL image object 
    photo=ImageTk.PhotoImage(flat_frame)
    
    
    def get_photo(x):
        global photo
        currframe=frame_number.get()
        flat_frame=[y/15 for x in im_frames[currframe] for y in x]
        flat_frame=Image.fromarray(asarray(flat_frame))
        mode_frame=flat_frame.convert('L') 
        brightenhance=brightness.get()
        contrastenhance=contrast.get()
        brightenhancer=ImageEnhance.Brightness(mode_frame)
        brightphoto=brightenhancer.enhance(brightenhance)
        contrastenhancer=ImageEnhance.Contrast(brightphoto)
        contrastphoto=contrastenhancer.enhance(contrastenhance)
        photo=ImageTk.PhotoImage(contrastphoto)
        
        
        myCanvas.create_image(myCanvas.winfo_reqwidth()/2,myCanvas.winfo_reqheight()/2,anchor='center',image=photo)
        frame_data=data[data['frame']==currframe+1]
        frame_data.groupby('particle').apply(lambda p: myCanvas.create_circle(p.x.values[0],p.y.values[0],10,p.particle.values[0],outline='red',width=3))
            
    
    
    
    myFrame = tk.Frame(root)
    myFrame.grid(column=0,row=0)
    

    myCanvas = tk.Canvas(myFrame, width=512, height=512,highlightthickness=0)
    
    editvalue=tk.IntVar()
    a=Radiobutton(variable=editvalue,value=0,text='Delete Trace')
    a.grid(column=10,row=0)
    b=Radiobutton(variable=editvalue,value=1,text='Delete Position')
    b.grid(column=10,row=1)
    c=Radiobutton(variable=editvalue,value=2,text='Unlink From Next Frame')
    c.grid(column=10,row=2)
    
    
    def onclick(event,data):
        
        item = myCanvas.find_closest(event.x, event.y)
        id=myCanvas.itemcget(item,'tags')
        id=id.replace('current','')
        id=int(id)
        state=editvalue.get()
        if state==0: 
            data=data[data['particle']!=id]
            myCanvas.delete(item)
            
        elif state==1:
            row=data.loc[(data['frame']==frame_number.get()) & (data['particle']==id)]
            data=data.drop(row)
            myCanvas.delete(item)
        elif state==2:
            maxparticle=data['particle'].max()
            current_frame=frame_number.get()
            frame_data=data[data['frame']==current_frame]
            end_frame=frame_data['frame'].max()
            rowstart=data.loc[(data['frame']==current_frame) & (data['particle']==id)]
            rowend=data.loc[(data['frame']==current_frame) & (data['particle']==id)]
            data['particle'].loc[rowstart:rowend]=maxparticle+1
            
    myCanvas.grid(column=1,row=1,columnspan=6,rowspan=6)
    myCanvas.bind('<Button-1>',lambda event, arg=data: onclick(event,arg))
    
    frame_number=tk.IntVar()
  
    frameslider=tk.Scale(root,variable=frame_number,from_=0,to=num_frames-1,orient='horizontal',command=get_photo)
    frameslider.grid(column=0,row=4,rowspan=3)
    
    
    framelabel=tk.Label(text='Frame Number')
    framelabel.grid(column=0,row=3)
    
    brightness=tk.IntVar()
    contrast=tk.IntVar()
    brightslider=tk.Scale(root,variable=brightness,from_=0,to=8,resolution=.1,length=100,orient='horizontal',command=get_photo)
    contrastslider=tk.Scale(root,variable=contrast,from_=0,to=8,resolution=.1,length=100,orient='horizontal',command=get_photo)
    brightlabel=tk.Label(text='Brightness')
    brightslider.set(1)
    contrastslider.set(1)
    contrastlabel=tk.Label(text='Contrast')
    brightlabel.grid(column=10,row=3)
    contrastlabel.grid(column=10,row=4)
    brightslider.grid(column=11,row=3,columnspan=2)
    contrastslider.grid(column=11,row=4,columnspan=2)
    
   
    
    get_photo(1)  
    
    
   
         
         

root=tk.Tk()
menu=tk.Menu(root)
root.config(menu=menu)
filemenu = tk.Menu(menu)
menu.add_cascade(label="Load Files", menu=filemenu)

filemenu.add_command(label="Load Video", command=OpenVidFile)
#filemenu.add_command(label='Load Tracking Data', command=LoadData)

root.mainloop()