import tkinter as tk
from tkinter import ttk
import random
import math

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
    self.gridButton = tk.Button(root,text="GRID",command=self.gridButton_clicked)
    self.buttons.append(self.gridButton)
    self.labelButton = tk.Button(root,text="LABEL",command=self.labelButton_clicked)
    self.buttons.append(self.labelButton)
    self.rotateLeftButton = tk.Button(root,text="<--",command=self.rotateLeftButton_clicked)
    self.buttons.append(self.rotateLeftButton)
    self.rotateRightButton = tk.Button(root,text="-->",command=self.rotateRightButton_clicked)
    self.buttons.append(self.rotateRightButton)
    self.clearButton = tk.Button(root,text="CLEAR",command=self.clearButton_clicked)
    self.buttons.append(self.clearButton)
    for b in self.buttons:
      b.pack(side="left",expand=True,fill='y')
    # sliders
    self.dotSizeSlider = tk.Scale(root,from_=5, to=40,orient="horizontal")
    self.dotSizeSlider.set(20)
    self.dotSizeSlider.pack(side="bottom",fill='both')
    self.rotationSlider = tk.Scale(root,from_=-360, to=360,orient="horizontal")
    self.rotationSlider.set(0)
    self.rotationSlider.pack(side="bottom",fill="both")
    
    self.cutLine = None

    self.selectedDotToConnect = None
    self.selectedDotsToMove = []
    self.buttonOption = None
    self.currentlyTracking = None
    self.gridLines = []
    self.LINE_SPACING = 20
    self.snapping = False
    self.originCoords = None
    self.rotationPoint = None
    self.rotationSprite = None
    #self.nearCircle = self.canvas.create_oval(0,0,12,12,outline="red")
    self.rotation = 0

  
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
  
  def gridButton_clicked(self):
    self.toggleGrid()

  def clearButton_clicked(self):
    while len(self.dots) > 0:
      self.subDot(self.dots[0].coords)
    self.buttonOption = None
    self.raiseButtons()
    self.clearSelection()

  def labelButton_clicked(self):
    self.toggleLabels()
  
  def rotateLeftButton_clicked(self):
    self.rotate(math.radians(-22.5))
  
  def rotateRightButton_clicked(self):
    self.rotate(math.radians(22.5))

  def addDot(self,coords):
    if self.snapping == True:
      coords = self.getCloseCoords(coords,self.LINE_SPACING)
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
    self.canvas.delete(d.label)
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
    self.rotationPoint = None
    self.canvas.delete(self.rotationSprite)
    self.rotationSprite = None

  def connectDots(self,dotsToConnect):
    l = Line(self,dotsToConnect)
    self.lines.append(l)
  
  def place(self,dot,coords,selectedToFollow=True,snap=True):
    if self.snapping == True and snap==True:
      closeCoords = self.getCloseCoords(coords,self.LINE_SPACING)
      #print("Og coords: {}\tClose coords: {}\tDiff: {}".format(coords,closeCoords,difference))
      coords = closeCoords
    dot.coords = coords

    #print(coords)
    self.canvas.coords(dot.sprite,dot.getSpriteCoords(dot.coords))
    dot.updateLabel()
    for l in self.lines:
      if dot in l.dots:
        self.canvas.coords(l.sprite,l.dots[0].coords[0],l.dots[0].coords[1],l.dots[1].coords[0],l.dots[1].coords[1])
    if selectedToFollow == True:
      for d in self.selectedDotsToMove:
          d.coords = [dot.coords[0]+d.originDiff[0],dot.coords[1]+d.originDiff[1]]
          print(dot.coords,d.coords)
          self.canvas.coords(d.sprite,d.getSpriteCoords(d.coords))
          for l in self.lines:
            if d in l.dots:
              self.canvas.coords(l.sprite,l.dots[0].coords[0],l.dots[0].coords[1],l.dots[1].coords[0],l.dots[1].coords[1])
          d.updateLabel()
    
  def move(self,dot,coordChange):
    coords = [a + b for a, b in zip(dot.coords, coordChange)]
    dot.coords = coords
    self.place(dot,dot.coords)
  
  def toggleTracking(self,dot):
    if dot == None:
      self.currentlyTracking = None
      for d in self.selectedDotsToMove:
        d.originCoords = None
        if self.rotationSprite != None:
          rotX = 0
          rotY = 0
          for d in self.selectedDotsToMove:
            rotX += d.coords[0]
            rotY += d.coords[1]
          rotX = rotX/len(self.selectedDotsToMove)
          rotY = rotY/len(self.selectedDotsToMove)
          self.rotationPoint = [rotX,rotY]
          self.canvas.coords(self.rotationSprite,rotX-1,rotY-1,rotX+1,rotY+1)
    elif dot.tracking == True:
      dot.tracking = False
      self.currentlyTracking = None
      dot.originCoords = None
      dot.originDiff = None
      for d in self.selectedDotsToMove:
        d.originCoords = None
        if self.rotationSprite != None:
          rotX = 0
          rotY = 0
          for d in self.selectedDotsToMove:
            rotX += d.coords[0]
            rotY += d.coords[1]
          rotX = rotX/len(self.selectedDotsToMove)
          rotY = rotY/len(self.selectedDotsToMove)
          self.rotationPoint = [rotX,rotY]
          self.canvas.coords(self.rotationSprite,rotX-1,rotY-1,rotX+1,rotY+1)
    else:
      dot.tracking = True
      self.currentlyTracking = dot
      dot.originCoords = dot.coords
      dot.originDiff = [0,0]
      for d in self.selectedDotsToMove:
        d.originCoords = d.coords
        d.originDiff = [d.coords[0]-dot.coords[0],d.coords[1]-dot.coords[1]]
  
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
    if self.rotationPoint == None:
      self.rotationSprite = self.canvas.create_oval(dot.coords[0]-1,dot.coords[1]-1,dot.coords[0]+1,dot.coords[1]+1)
      self.rotationPoint = dot.coords
    else:
      rotX = 0
      rotY = 0
      for d in self.selectedDotsToMove:
        rotX += d.coords[0]
        rotY += d.coords[1]
      rotX = rotX/len(self.selectedDotsToMove)
      rotY = rotY/len(self.selectedDotsToMove)
      self.rotationPoint = [rotX,rotY]
      self.canvas.coords(self.rotationSprite,rotX-1,rotY-1,rotX+1,rotY+1)


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
      newLines = []
      for l in self.lines:
        if self.linesIntersect(self.cutLine,l):
          self.canvas.delete(l.sprite)
          
        else:
          newLines.append(l)
      self.canvas.delete(self.cutLine)
      self.cutLine = None
      self.lines = newLines

  def linesIntersect(self,l1,l2):
    TARGETING = False
    l1coords = self.canvas.coords(l1)
    l2coords = l2.getCoords()
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
    valid = True
    if l1coords[0] == l1coords[2] or l2coords[0] == l2coords[2]:
      if l1coords[0] == l1coords[2]:
        intersectx = l1coords[0]
        intersecty = l2slope*intersectx + l2yintercept
      else:
        intersectx = l2coords[0]
        intersecty = l1slope*intersectx + l1yintercept
    elif l1slope != l2slope:
      intersectx = (l2yintercept-l1yintercept)/(l1slope-l2slope)
      intersecty = l1slope*intersectx + l1yintercept
    else:
      valid = False
    if valid:
      print("Overlapping: {}".format(self.canvas.find_overlapping(intersectx-1,intersecty-1,intersectx+1,intersecty+1)))

      overlapObjs = self.canvas.find_overlapping(intersectx-1,intersecty-1,intersectx+1,intersecty+1)
      print("L1 ID: {}\tL2 ID: {}".format(l1,l2.sprite))
      if l1 in overlapObjs and l2.sprite in overlapObjs:
        intersecting = True
        if TARGETING == True:
          c = self.canvas.create_oval(intersectx-1,intersecty-1,intersectx+1,intersecty+1,outline="red",tags="target")
          targets.append(c)

      print(intersecting)
    
    print("Intersect coords: {},{}\tL1 coords: {}\tL2 coords: {}\tIntersecting: {}".format(intersectx,intersecty,l1coords,l2coords,intersecting))
    return intersecting
  
  def getCloseCoords(self,coords,interval):
    closeX = 0
    lowX = coords[0]
    while lowX > 0 and lowX % interval != 0:
      lowX -= 1
    highX = coords[0]
    while highX < self.size[0] and highX % interval != 0:
      highX += 1
    if abs(lowX-coords[0]) < abs(highX-coords[0]):
      closeX = lowX
    else:
      closeX = highX
    
    closeY = 0
    lowY = coords[1]
    while lowY > 0 and lowY % interval != 0:
      lowY -= 1
    highY = coords[1]
    while highY < self.size[1] and highY % interval != 0:
      highY += 1
    if abs(lowY-coords[1]) < abs(highY-coords[1]):
      closeY = lowY
    else:
      closeY = highY

    return [closeX,closeY]

  def mouseUpdate(self):
    #self.canvas.coords(dot.sprite,dot.getSpriteCoords(dot.coords))
    closeCoords = self.getCloseCoords(mouseCoords,self.LINE_SPACING)
    closeX = closeCoords[0]
    closeY = closeCoords[1]
    print(self.rotationSlider.get(),self.rotation)
    if self.rotationSlider.get() != self.rotation:
      self.rotate(self.rotate(math.radians(self.rotationSlider.get()-self.rotation)))
      self.rotation = self.rotationSlider.get()
    #self.canvas.coords(self.nearCircle,closeX-6,closeY-6,closeX + 6,closeY +6)
    try:
      if self.buttonOption == "cut":
        originCoords = self.canvas.coords(self.cutLine)
        self.canvas.coords(self.cutLine,originCoords[0],originCoords[1],mouseCoords[0],mouseCoords[1])
    except:
      return
  
  def toggleGrid(self):
    if self.snapping == False:
      self.snapping = True
      for x in range(0,self.size[0],self.LINE_SPACING):
        l = self.canvas.create_line(x,0,x,self.size[1],fill="gray")
        self.gridLines.append(l)
      for y in range(0,self.size[1],self.LINE_SPACING):
          l = self.canvas.create_line(0,y,self.size[0],y,fill="gray")
          self.gridLines.append(l)
    else:
      self.snapping = False
      for l in self.gridLines:
        self.canvas.delete(l)
      self.gridLines = []

  def toggleLabels(self):
    for d in self.dots:
      if self.canvas.itemcget(d.label,"state") == tk.HIDDEN:
        self.canvas.itemconfigure(d.label,state=tk.NORMAL)
      else:
        self.canvas.itemconfigure(d.label,state=tk.HIDDEN)

  def rotate(self,theta):
    #x2=cosβx1−sinβy1
    #y2=sinβx1+cosβy1
    print("Total rotation: {}".format(self.rotation))
    print ("Rotation point: {}".format(self.rotationPoint))
    for d in self.selectedDotsToMove:
      # x1 = d.coords[0] - self.rotationPoint[0]
      # y1 = d.coords[1] - self.rotationPoint[1]
      # x2 = (math.cos(math.degrees(theta)) * x1 - math.sin(math.degrees(theta)) * y1) + self.rotationPoint[0]
      # y2 = (math.sin(math.degrees(theta)) * x1 + math.cos(math.degrees(theta)) * y1) + self.rotationPoint[1]
      # print([x2,y2])
      # self.place(d,[x2,y2],selectedToFollow=False,snap=False)

      x1 = (d.coords[0] - self.rotationPoint[0]) * math.cos(theta) - (d.coords[1] - self.rotationPoint[1]) * math.sin(theta) + self.rotationPoint[0]
      y1 = (d.coords[0] - self.rotationPoint[0]) * math.sin(theta) + (d.coords[1] - self.rotationPoint[1]) * math.cos(theta) + self.rotationPoint[1]
      print([x1,y1])
      self.place(d,[x1,y1],selectedToFollow=False,snap=False)
class Dot():
  def __init__(self,coords,board):
    self.size = board.dotSizeSlider.get()
    self.coords = coords
    self.originCoords = None
    self.originDiff = None
    self.board = board
    self.canvas = board.canvas
    self.sprite = self.canvas.create_oval(coords[0]-self.size/2,coords[1]-self.size/2,coords[0]+self.size/2,coords[1]+self.size/2,tags=("dot"))
    self.label = self.canvas.create_text(coords[0]-self.size/2-5,coords[1]-self.size/2-5,text="[{}, {}]".format(round(self.coords[0]),round(self.coords[1])),font=['Helvetica',7])
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

  def updateLabel(self):
    self.canvas.coords(self.label,self.coords[0]-self.size/2-5,self.coords[1]-self.size/2-5)
    self.canvas.itemconfigure(self.label,text="[{}, {}]".format(round(self.coords[0]),round(self.coords[1])))

class Line():
  def __init__(self,board,dots):
    self.board = board
    self.canvas = self.board.canvas
    self.dots = dots
    
    self.sprite = self.canvas.create_line(self.dots[0].coords,self.dots[1].coords,tags=("line"),width=2)
    
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
    elif board.snapping == False and d.selectedToMove and board.currentlyTracking != None:
      coordChange = [mouseCoords[0]-oldMouseCoords[0],mouseCoords[1]-oldMouseCoords[1]]
      board.move(d,coordChange)



def leftClick(event):
  if board.buttonOption == "move":
    for d in board.dots:
      if d.withinBounds(mouseCoords):
        board.toggleTracking(d)
        return
    board.toggleTracking(None)
    
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
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 400
root.bind('<Motion>',motion)
root.bind('<Button-1>',leftClick)
root.bind('<Button-3>',rightClick)
root.bind('<ButtonRelease-1>',leftRelease)
mouseCoords=[]
board = Board(CANVAS_WIDTH,CANVAS_HEIGHT,root)
board.toggleGrid()

root.mainloop()

