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
        for i in range(7):
            self.canvas.create_line((i + 1) * (CANVAS_WIDTH / 8), 0, (i + 1) * (CANVAS_WIDTH / 8), CANVAS_HIGHT)
            self.canvas.create_line(0,(i + 1) * (CANVAS_HIGHT / 8),CANVAS_WIDTH,(i + 1) * (CANVAS_HIGHT / 8))
        self.canvas.pack()
        self.idlist=[[0 for x in range(8)] for y in range(8)]
        for i in range(8):
            for j in range(8):
                self.idlist[i][j]=self.canvas.create_oval(i*CANVAS_WIDTH/8+1, 1+j*CANVAS_HIGHT/8+1,
                                                     (i+1)*CANVAS_WIDTH/8-1, (j+1)*CANVAS_HIGHT/8-1,
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
        for i in range(8):
            for j in range(8):
                self.setStone(i,j,self.env.state[i][j])
        self.master.lift()
        self.master.after(300, self.updateStone)


if __name__ =="__main__":
    root=tk.Tk()
    environment=environment.Environment()
    app=EnvGUI(master=root,env=environment)

    app.mainloop()