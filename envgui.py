import tkinter as tk
import numpy as np
import environment
WINDOW_WIDTH=WINDOW_HIGHT=CANVAS_WIDTH=CANVAS_HIGHT=400
BLANK = 0  # 石が空：0
BLACK = 1  # 石が黒：1
WHITE = -1  # 石が白：-1
class EnvGUI(tk.Frame):
    def __init__(self,env,master):
        super().__init__(master)
        self.master.geometry("400x400+200+200")
        self.env=env
        self.canvas= tk.Canvas(master, bg = "green"
                               ,width=CANVAS_WIDTH,height=CANVAS_HIGHT)
        self.size=env.size
        for i in range(self.size-1):
            self.canvas.create_line((i + 1) * (CANVAS_WIDTH / self.size), 0, (i + 1) * (CANVAS_WIDTH / self.size), CANVAS_HIGHT)
            self.canvas.create_line(0,(i + 1) * (CANVAS_HIGHT / self.size),CANVAS_WIDTH,(i + 1) * (CANVAS_HIGHT / self.size))
        self.canvas.pack()
        self.idlist=[[0 for x in range(self.size)] for y in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                self.idlist[i][j]=self.canvas.create_oval(i*CANVAS_WIDTH/self.size+1, 1+j*CANVAS_HIGHT/self.size+1,
                                                     (i+1)*CANVAS_WIDTH/self.size-1, (j+1)*CANVAS_HIGHT/self.size-1,
                                                     fill='green',outline='green')
        self.updateStone()
        self.mainloop()
    def setStone(self,x,y,color:int):
        if color==BLANK:
            self.canvas.itemconfig(tagOrId=self.idlist[x][y],fill='green',outline='green')
        elif color==BLACK:
            self.canvas.itemconfig(tagOrId=self.idlist[x][y], fill='black', outline='black')
        elif color==WHITE:
            self.canvas.itemconfig(tagOrId=self.idlist[x][y], fill='white', outline='white')
        self.canvas.update()
    def updateStone(self):
        for i in range(self.size):
            for j in range(self.size):
                self.setStone(i,j,self.env.state[i][j])
        self.master.lift()
        self.master.after(300, self.updateStone)


if __name__ =="__main__":
    root=tk.Tk()
    environment=environment.Environment()
    app=EnvGUI(master=root,env=environment)

    app.mainloop()