############################################################
# Citations:
# cat.jpeg is under CC0 licences from unsplash.com.
#   link: https://unsplash.com/photos/9SWHIgu8A8k
# Graphics package provided as a resource to be used as a part
# of the class.
############################################################
from modules.cmu_112_graphics import *
from exporter import *
from tkinter import *
from PIL import Image
import os

class Div(object):
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

class Text(object):
    def __init__(self, x, y, width, height, content, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.content = content
        self.color = color

class Img(object):
    def __init__(self, x, y, width, height, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image

class CSSClass(object):
    pastClasses = set()
    def __init__(self, color, height, width):
        self.color = color
        self.height = height
        self.width = width
    def getImportantAttributes(self):
        return (self.color, self.height, self.width)
    def __eq__(self, other):
        return (isinstance(other, CSSClass) and 
                self.getImportantAttributes() == other.getImportantAttributes())
    def __hash__(self):
        return hash(self.getImportantAttributes())

class MyApp(App):
    def appStarted(self):
        self.toolsDict = {0: "cursor", 1: "rectangle", 2: "text", 3: "image"}
        self.curTool = 0
        self.toolBarMargin = 30
        self.objects = []
        self.startX = 0
        self.startY = 0
        self.startItemX = 0
        self.startItemY = 0
        self.curDiv = None
        self.selectedObj = None
        self.curColor = "black"

    def keyPressed(self, event):
        if event.key == "c":
            self.curTool = 0
        elif event.key == "r":
            self.curTool = 1
        elif event.key == "t":
            self.curTool = 2
        elif event.key == "i":
            self.curTool = 3
        elif event.key == "Escape":
            self.selectedObj = None
        elif event.key == "Delete" and self.selectedObj != None:
            self.deleteSelectedObject()

    def findClickedObject(self, x, y):
        for obj in self.objects:
            if (((obj.x < x and (obj.x + obj.width) > x) or
                (obj.x > x and (obj.x + obj.width) < x)) and
                ((obj.y < y and (obj.y + obj.height) > y) or
                (obj.y > y and (obj.y + obj.height) < y))):
                self.selectedObj = obj

    def deleteSelectedObject(self):
        self.objects.remove(self.selectedObj)

    def mousePressed(self, event):
        if event.x < 30 and event.x > 0 and event.y > 10 and event.y < 40:
            self.curColor = self.getUserInput("Input a new color")
        elif self.curTool == 0:
            self.findClickedObject(event.x, event.y)
            if self.selectedObj != None:
                self.startItemX = self.selectedObj.x
                self.startItemY = self.selectedObj.y
                self.startX = event.x
                self.startY = event.y
        elif self.curTool == 1:
            self.startX = event.x
            self.startY = event.y
            self.curDiv = Div(self.startX, self.startY, 0, 0, self.curColor)
        elif self.curTool == 2:
            content = self.getUserInput("Input text")
            newText = Text(event.x, event.y, 300, 300, content, self.curColor)
            self.objects.append(newText)
        elif self.curTool == 3:
            imagePath = os.getcwd() + '/' + self.getUserInput("Image path")
            try:
                img = self.loadImage(imagePath)
                newImg = Img(event.x, event.y, 500, 500, img)
                self.objects.append(newImg)
            except:
                print(f"Path not valid: {imagePath}")

    def mouseDragged(self, event):
        if self.curTool == 0 and self.selectedObj != None:
            self.selectedObj.x = self.startItemX + event.x - self.startX
            self.selectedObj.y = self.startItemY + event.y - self.startY
        elif self.curTool == 1 and self.curDiv != None:
            width = event.x - self.startX
            height = event.y - self.startY
            self.curDiv.height = height
            self.curDiv.width = width

    def mouseReleased(self, event):
        if self.curTool == 1 and self.curDiv != None:
            self.objects.append(self.curDiv)
            self.curDiv = None

    def drawObjects(self, canvas):
        for o in self.objects:
            if isinstance(o, Div):
                canvas.create_rectangle(o.x, o.y, o.x + o.width, o.y + o.height, fill=o.color)
            elif isinstance(o, Text):
                canvas.create_text(o.x, o.y, text=o.content, fill=o.color)
            elif isinstance(o, Img):
                canvas.create_image(o.height, o.width, image=ImageTk.PhotoImage(o.image))
        if self.curDiv != None:
            canvas.create_rectangle(self.curDiv.x, self.curDiv.y, 
                        self.curDiv.x + self.curDiv.width, self.curDiv.y + self.curDiv.height, 
                        fill=self.curDiv.color)

    def drawToolbar(self, canvas):
        canvas.create_rectangle(0, 0, self.toolBarMargin, self.height, fill="gray")
        canvas.create_rectangle(0, 10, self.toolBarMargin, 40, fill=self.curColor)
        canvas.create_rectangle(0, 50, self.toolBarMargin, 80, fill="")
        canvas.create_text(0, 50, text="cursor", anchor="nw")

    def drawHighlight(self, canvas):
        if self.selectedObj != None:
            x = self.selectedObj.x
            y = self.selectedObj.y
            height = self.selectedObj.height
            width = self.selectedObj.width
            canvas.create_rectangle(x, y, x+width, y+height, outline="red", width=5)

    def redrawAll(self, canvas):
        self.drawObjects(canvas)
        self.drawToolbar(canvas)
        self.drawHighlight(canvas)
        canvas.create_text(self.width/2, 10, text=f"current tool: {self.toolsDict[self.curTool]}")

MyApp(width=1000, height=1000)