import tkinter as tk
from tkinter import ttk
import random

class Board():
  def __init__(self,canvas_width,canvas_height,root):
    self.size = [canvas_width,canvas_height]
    self.root = root
    self.dots = []
    self.lines = []
    self.canvas = tk.Canvas(root,bg="white",height=canvas_height,width=canvas_width)
    self.canvas.pack()

    # buttons
    self.buttons = []
    self.moveButton = tk.Button(root,text="MOVE",command=self.moveButton_clicked)
    self.buttons.append(self.moveButton)
    self.selectButton = tk.Button(root,text="SELECT",command=self.selectButton_clicked)
    self.buttons.append(self.selectButton)
    self.addButton = tk.Button(root,text="+",command=self.addButton_clicked)
    self.buttons.append(self.addButton)
    self.subButton = tk.Button(root,text="-",command=self.subButton_clicked)
    self.buttons.append(self.subButton)
    self.cutButton = tk.Button(root,text="CUT",command=self.cutButton_clicked)
    self.buttons.append(self.cutButton)
    self.clearButton = tk.Button(root,text="CLEAR",command=self.clearButton_clicked)
    self.buttons.append(self.clearButton)
    for b in self.buttons:
      b.pack(side="left",expand=True,fill='y')
    # sliders
    self.dotSizeSlider = tk.Scale(root,from_=5, to=40,orient="horizontal")
    self.dotSizeSlider.set(20)
    self.dotSizeSlider.pack(side="bottom",fill='both')

    self.cutLine = None

    self.selectedDotToConnect = None
    self.selectedDotsToMove = []
    self.buttonOption = None
    self.currentlyTracking = None
    self.gridLines = []

  def raiseButtons(self):
    buttonsToIgnore = [self.selectButton]
    for b in self.buttons:
      if b not in buttonsToIgnore:
        b.config(relief="raised")

  def moveButton_clicked(self):
    self.raiseButtons()
    if self.buttonOption != "move":
      self.buttonOption = "move"
      self.moveButton.config(relief="sunken")
    else:
      self.buttonOption = None

  def selectButton_clicked(self):
    if self.selectButton.cget("relief") == "sunken":
      self.clearSelection()
      self.selectButton.config(relief="raised")
      if self.buttonOption == "select":
        self.buttonOption = None
    else:
      self.raiseButtons()
      self.selectButton.config(relief="sunken")
      self.buttonOption = "select"

  def addButton_clicked(self):
    self.raiseButtons()
    if self.buttonOption != "add":
      self.buttonOption = "add"
      self.addButton.config(relief="sunken")
    else:
      self.buttonOption = None

  def subButton_clicked(self):
    self.raiseButtons()
    if self.buttonOption != "sub":
      self.buttonOption = "sub"
      self.subButton.config(relief="sunken")
    else:
      self.buttonOption = None

  def cutButton_clicked(self):
    self.raiseButtons()
    if self.buttonOption != "cut":
      self.buttonOption = "cut"
      self.cutButton.config(relief="sunken")
    else:
      self.buttonOption = None
  def clearButton_clicked(self):
    while len(self.dots) > 0:
      self.subDot(self.dots[0].coords)
    self.buttonOption = None
    self.raiseButtons()

  def addDot(self,coords):
    d = Dot(coords,self)
    self.dots.append(d)

  def subDot(self,coords):
    d = None
    for dot in self.dots:
      if dot.withinBounds(coords):
        d = dot
    if d == None:
      return
    newLines = []
    for l in self.lines:
      if d in l.dots:
        self.canvas.delete(l.sprite)
      else:
        newLines.append(l)
    self.lines = newLines
    self.dots.remove(d)
    self.canvas.delete(d.sprite)

  def selectDot(self,coords):
    d = None
    for dot in self.dots:
      if dot.withinBounds(coords):
        d = dot
    if d == None:
      return
    self.toggleSelectToMove(d)

  def clearSelection(self):
    for d in self.dots:
      self.canvas.itemconfigure(d.sprite,outline="black")
      d.selectedToMove = False
    self.selectedDotsToMove = []

  def connectDots(self,dotsToConnect):
    l = Line(self,dotsToConnect)
    self.lines.append(l)

  def place(self,dot,coords):
    dot.coords = coords

    #print(coords)
    self.canvas.coords(dot.sprite,dot.getSpriteCoords(dot.coords))
    for l in self.lines:
      if dot in l.dots:
        self.canvas.coords(l.sprite,l.dots[0].coords[0],l.dots[0].coords[1],l.dots[1].coords[0],l.dots[1].coords[1])

  def move(self,dot,coordChange):
    dot.coords = [a + b for a, b in zip(dot.coords, coordChange)]
    self.place(dot,dot.coords)

  def toggleTracking(self,dot):
    if dot.tracking == True:
      dot.tracking = False
      self.currentlyTracking = None
    else:
      dot.tracking = True
      self.currentlyTracking = dot

  def toggleSelectToConnect(self,dot):
    if dot.selectedToConnect == True:
      dot.selectedToConnect = False
      self.canvas.itemconfig(dot.sprite,dash=())
    else:
      dot.selectedToConnect = True
      self.canvas.itemconfig(dot.sprite,dash=5)

  def toggleSelectToMove(self,dot):
    outlineColor = self.canvas.itemconfig(dot.sprite)["outline"][-1]
    if outlineColor == "black":
      self.canvas.itemconfig(dot.sprite,outline="red")
      self.selectedDotsToMove.append(dot)
      dot.selectedToMove = True
    else:
      self.canvas.itemconfig(dot.sprite,outline="black")
      self.selectedDotsToMove.remove(dot)
      dot.selectedToMove = False

  def disconnectDots(self,dotsToDisconnect):
    lineToDelete = None
    for l in self.lines:
      if dotsToDisconnect[0] in l.dots and dotsToDisconnect[1] in l.dots:
        lineToDelete = l

    self.canvas.delete(lineToDelete.sprite)
    self.lines.remove(lineToDelete)

  def isConnected(self,dotsToCheck):
    if dotsToCheck[0] == dotsToCheck[1]:
      return False
    for l in self.lines:
      if dotsToCheck[0] in l.dots and dotsToCheck[1] in l.dots:
        return True
    return False

  def startCut(self):
    self.buttonOption = "cut"
    self.cutLine = self.canvas.create_line(mouseCoords[0],mouseCoords[1],mouseCoords[0],mouseCoords[1],tag="line")

  def endCut(self):
    if self.buttonOption == "cut" and self.cutLine != None:
      cutLineCoords = self.canvas.coords(self.cutLine)
      newLines = []
      for l in self.lines:
        if self.linesIntersect(cutLineCoords,l.getCoords()):
          #self.canvas.delete(l.sprite)
          True == True
        else:
          newLines.append(l)
      #self.canvas.delete(self.cutLine)
      self.cutLine = None
      self.lines = newLines

  def linesIntersect(self,l1coords,l2coords):

    l1slope = 0
    l2slope = 0
    if l1coords[0] != l1coords[2]:
      l1slope = (l1coords[3]-l1coords[1])/(l1coords[2]-l1coords[0])
    if l2coords[0] != l2coords[2]:
      l2slope = (l2coords[3]-l2coords[1])/(l2coords[2]-l2coords[0])

    l1yintercept = l1coords[0]*-1*l1slope+l1coords[1]
    l2yintercept = l2coords[0]*-1*l2slope+l2coords[1]

    intersectx = 0
    intersecty = 0
    intersecting = False
    targets = []
    if l1slope != l2slope:
      intersectx = (l2yintercept-l1yintercept)/(l1slope-l2slope)
      intersecty = l1slope*intersectx + l1yintercept

      print(self.canvas.find_overlapping(intersectx-1,intersecty-1,intersectx+1,intersecty+1))

      if min(l1coords[0],l1coords[2]) < intersectx and intersectx < max(l1coords[0],l1coords[2]) and min(l1coords[1],l1coords[3]) < intersecty and intersecty < max(l1coords[1],l1coords[3]):
        intersecting = True
        c = self.canvas.create_oval(intersectx-1,intersecty-1,intersectx+1,intersecty+1,outline="red",tags="target")
        targets.append(c)

    print("Intersect coords: {},{}\tL1 coords: {}\tL2 coords: {}\tIntersecting: {}".format(intersectx,intersecty,l1coords,l2coords,intersecting))
    return intersecting


  def mouseUpdate(self):
    #self.canvas.coords(dot.sprite,dot.getSpriteCoords(dot.coords))
    try:
      if self.buttonOption == "cut":
        originCoords = self.canvas.coords(self.cutLine)
        self.canvas.coords(self.cutLine,originCoords[0],originCoords[1],mouseCoords[0],mouseCoords[1])
    except:
      return

  def showGrid(self):
    LINE_SPACING = 10
    for x in range(0,self.size[0],LINE_SPACING):
      l = self.canvas.create_line(x,0,x,self.size[1],fill="gray")
      self.gridLines.append(l)
    for y in range(0,self.size[1],LINE_SPACING):
        l = self.canvas.create_line(0,y,self.size[0],y,fill="gray")
        self.gridLines.append(l)

class Dot():
  def __init__(self,coords,board):
    self.size = board.dotSizeSlider.get()
    self.coords = coords
    self.board = board
    self.canvas = board.canvas
    self.sprite = self.canvas.create_oval(coords[0]-self.size/2,coords[1]-self.size/2,coords[0]+self.size/2,coords[1]+self.size/2,tags=("dot"))
    self.tracking = False
    self.trackingOffset = [0,0]
    self.selectedToConnect = False
    self.selectedToMove = False

  def getSpriteCoords(self, coords):
    return[coords[0]-self.size/2,coords[1]-self.size/2,coords[0]+self.size/2,coords[1]+self.size/2]

  def withinBounds(self,coords):
    bounds = self.getSpriteCoords(self.coords)
    if bounds[0] < coords[0] and coords[0] < bounds[2] and bounds[1] < coords[1] and coords[1] < bounds[3]:
      return True
    return False

class Line():
  def __init__(self,board,dots):
    self.board = board
    self.canvas = self.board.canvas
    self.dots = dots

    self.sprite = self.canvas.create_line(self.dots[0].coords,self.dots[1].coords,tags=("line"))

  def getCoords(self):
    coords = []
    for d in self.dots:
      for c in d.coords:
        coords.append(c)
    return coords


def motion(event):
  global dotsToTrack, mouseCoords
  oldMouseCoords = mouseCoords
  mouseCoords = [event.x, event.y]
  #print("{}\t{}".format(mouseCoords,event.widget))
  board.mouseUpdate()
  for d in board.dots:
    if d.tracking:
      coords = mouseCoords
      board.place(d,coords)
    elif d.selectedToMove and board.currentlyTracking != None:
      coordChange = [mouseCoords[0]-oldMouseCoords[0],mouseCoords[1]-oldMouseCoords[1]]
      board.move(d,coordChange)



def leftClick(event):
  if board.buttonOption == "move":
    for d in board.dots:
      if d.withinBounds(mouseCoords):
        board.toggleTracking(d)
        return

  elif board.buttonOption == "add":
    if event.widget == board.canvas:
      board.addDot(mouseCoords)
  elif board.buttonOption == "sub":
    if event.widget == board.canvas:
      board.subDot(mouseCoords)
  elif board.buttonOption == "select":
    if event.widget == board.canvas:
      board.selectDot(mouseCoords)
  elif board.buttonOption == "cut":
    if event.widget == board.canvas:
      board.startCut()

def rightClick(event):
  for d in board.dots:
    if d.withinBounds(mouseCoords):
      if board.selectedDotToConnect == None:
        board.selectedDotToConnect = d
        board.toggleSelectToConnect(d)
      elif d != board.selectedDotToConnect:
        if board.isConnected([d,board.selectedDotToConnect]) == False:
          board.connectDots([d,board.selectedDotToConnect])
        else:
          board.disconnectDots([d,board.selectedDotToConnect])
        board.toggleSelectToConnect(board.selectedDotToConnect)
        board.selectedDotToConnect = None
      else:
        board.toggleSelectToConnect(board.selectedDotToConnect)
        board.selectedDotToConnect = None
      return
  if board.selectedDotToConnect != None:
    board.toggleSelectToConnect(board.selectedDotToConnect)
    board.selectedDotToConnect = None

def leftRelease(event):
  board.endCut()



root = tk.Tk()
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
root.bind('<Motion>',motion)
root.bind('<Button-1>',leftClick)
root.bind('<Button-3>',rightClick)
root.bind('<ButtonRelease-1>',leftRelease)
mouseCoords=[]
board = Board(CANVAS_WIDTH,CANVAS_HEIGHT,root)
board.linesIntersect([0,0,4,4],[2,4,3,1])
board.linesIntersect([6,8,7,5],[7,4,11,8])
board.showGrid()

#d = Dot([100,100],canvas)
#d2 = Dot([200,200],canvas)
#d3 = Dot([250,250],canvas)
#d4 = Dot([20,20],canvas)
#d.connectDot(d2)
#d2.connectDot(d3)
#d3.connectDot(d4)
#d4.connectDot(d)
#d2.connectDot(d4)
#dots.append(d)
#dots.append(d2)
#dots.append(d3)
#dots.append(d4)
#d.place([50,50])
#input()
#d.place([170,120])
#input()
#d.move([-10,-10])

root.mainloop()
