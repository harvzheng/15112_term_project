# TODO
# 3.b. get select working with multiple objects if shift is being held
# 5. export to absolute positions in HTML/CSS
# 6. undo/redo commands (keep a list of max 5 of objects and moves; a function will handle where to place stuff)

# DONE
# 1. place and moveimages
# 2. set background color
# 3. toolbar
# 3.a. refactor code so that top left is always x and y values
# 4. align elements/align bar

############################################################
# Citations:
# cat.jpeg is under CC0 licences from unsplash.com.
#   link: https://unsplash.com/photos/9SWHIgu8A8k
# Graphics package provided by CMU's 15-112, which mainly uses
# TKinter and PIL.
#   link: https://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
############################################################
from modules.cmu_112_graphics import *
from exporter import *
from tkinter import *
from classes import *
from PIL import Image
import os

class MyApp(App):
    def appStarted(self):
        self.toolsDict = {0: "cursor", 1: "rectangle", 2: "text", 3: "image"}
        self.aligns = {0: "left", 1: "center\nhori", 2: "right", 3: "top", 4: "center\nvert", 5: "bottom"}
        self.curTool = 0
        self.toolBarMargin = 50
        self.objects = []
        self.startX = 0
        self.startY = 0
        self.startItemXs = []
        self.startItemYs = []
        self.curDiv = None
        self.selectedObj = []
        self.curColor = "black"
        self.bgColor = "white"
        self.shiftHeld = False
        self.selectedObjs = []

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
            self.clearSelection()
        elif event.key == "Delete" and self.selectedObj != None:
            self.deleteSelectedObject()
        elif event.key == "s":
            self.shiftHeld = True
    
    def keyReleased(self, event):
        if event.key == "s":
            self.shiftHeld = False

    def findClickedObject(self, x, y):
        for obj in self.objects:
            if (((obj.x < x and (obj.x + obj.width) > x) or
                (obj.x > x and (obj.x + obj.width) < x)) and
                ((obj.y < y and (obj.y + obj.height) > y) or
                (obj.y > y and (obj.y + obj.height) < y))):
                if self.shiftHeld:
                    self.selectedObjs.append(obj)
                    break
                else:
                    self.selectedObjs = [obj]
        self.startX = x
        self.startY = y
        for obj in self.selectedObjs:
            self.startItemXs.append(obj.x)
            self.startItemYs.append(obj.y)

    def findSelectedTool(self, x, y):
        if y <= 30 and y >= 0:
            self.curColor = self.getUserInput("Input a new color")
        elif y > 50 and y < 80:
            self.bgColor = self.curColor
        initialY = 90
        for key in self.toolsDict:
            if (y >= initialY and y <= (initialY + 30)):
                self.curTool = key
                break
            initialY += 50

    def findSelectedAlign(self, x, y):
        x0 = self.toolBarMargin * 2
        for align in self.aligns:
            if x >= x0 and x <= x0+50:
                self.alignSelectedObjects(align)
                break
            x0 += 60
        if x <= self.width and x >= self.width - 100:
            self.exportCanvas()

    def exportCanvas(self):
        fileName = self.getUserInput("Name of HTML File?")
        if fileName != None:
            self.convertToCSS()
            exportToHTML(fileName, self.objects)
            exportToCSS(self.bgColor, CSSClass.classes)

    def convertToCSS(self):
        for obj in self.objects:
            if isinstance(obj, Div):
                newClass = CSSClass(obj.color, obj.height, obj.width, left=obj.x, top=obj.y)
                obj.cssClass = CSSClass.classes[newClass]
                

    def alignSelectedObjects(self, align):
        toAlignPositions = []
        newPosition = None # x coord or y coord, depending on which align was selected
        for obj in self.selectedObjs:
            if align == 0: 
                toAlignPositions.append(obj.x)
                newPosition = min(toAlignPositions)
            elif align == 1:
                toAlignPositions.append(obj.x + obj.width/2)
                newPosition = sum(toAlignPositions)/len(toAlignPositions)
            elif align == 2:
                toAlignPositions.append(obj.x + obj.width)
                newPosition = max(toAlignPositions)
            elif align == 3:
                toAlignPositions.append(obj.y)
                newPosition = min(toAlignPositions)
            elif align == 4:
                toAlignPositions.append(obj.y + obj.height/2)
                newPosition = sum(toAlignPositions)/len(toAlignPositions)
            else:
                toAlignPositions.append(obj.y + obj.height)
                newPosition = max(toAlignPositions)
        for obj in self.selectedObjs:
            if align == 0: 
                obj.x = newPosition
            elif align == 1:
                obj.x = newPosition - obj.width/2
            elif align == 2:
                obj.x = newPosition - obj.width
            elif align == 3:
                obj.y = newPosition
            elif align == 4:
                obj.y = newPosition - obj.height/2
            else:
                obj.y = newPosition - obj.height


    def clearSelection(self):
        self.selectedObjs = []
        self.startItemXs = []
        self.startItemYs = []

    def deleteSelectedObject(self):
        for obj in self.selectedObjs:
            self.objects.remove(obj)
            self.clearSelection()

    def moveSelectedObjects(self, x, y):
        for i in range(len(self.selectedObjs)):
            obj = self.selectedObjs[i]
            obj.x = self.startItemXs[i] + x - self.startX
            obj.y = self.startItemYs[i] + y - self.startY

    def mousePressed(self, event):
        if event.x < self.toolBarMargin and event.x > 0:
            self.findSelectedTool(event.x, event.y)
        elif ((event.x > self.toolBarMargin and event.x <= self.width) and
                (event.y > 0 and event.y < 50)):
            self.findSelectedAlign(event.x, event.y)
        elif self.curTool == 0:
            self.findClickedObject(event.x, event.y)
        elif self.curTool == 1:
            self.startX = event.x
            self.startY = event.y
            self.curDiv = Div(self.startX, self.startY, 0, 0, self.curColor)
        elif self.curTool == 2:
            content = self.getUserInput("Input text")
            newText = Text(event.x, event.y, 300, 300, content, self.curColor)
            self.objects.append(newText)
        elif self.curTool == 3:
            imageName = self.getUserInput("Image path")
            if imageName != "":
                imagePath = os.getcwd() + '/' + imageName
                try:
                    img = self.loadImage(imagePath)
                    imgWidth, imgHeight = img.size
                    img = self.scaleImage(img, 500/(max(imgWidth, imgHeight)))

                    newImg = Img(event.x, event.y, 500/(max(imgWidth, imgHeight)), img)
                    self.objects.append(newImg)
                except:
                    print(f"Path not valid: {imagePath}")

    def mouseDragged(self, event):
        if self.curTool == 0 and len(self.selectedObjs) != 0:
            self.moveSelectedObjects(event.x, event.y)
        elif self.curTool == 1 and self.curDiv != None:
            width = event.x - self.startX
            height = event.y - self.startY
            self.curDiv.height = height
            self.curDiv.width = width

    def mouseReleased(self, event):
        if self.curTool == 1 and self.curDiv != None:
            x0, y0 = self.curDiv.x, self.curDiv.y
            x1 = x0 + self.curDiv.width
            y1 = y0 + self.curDiv.height
            self.objects.append(Div(min(x0, x1), min(y0, y1), 
                            abs(self.curDiv.width), abs(self.curDiv.height), self.curColor))
            self.curDiv = None

    def drawObjects(self, canvas):
        for o in self.objects:
            if isinstance(o, Div):
                canvas.create_rectangle(o.x, o.y, o.x + o.width, o.y + o.height, fill=o.color)
            elif isinstance(o, Text):
                canvas.create_text(o.x, o.y, text=o.content, fill=o.color, anchor="nw")
            elif isinstance(o, Img):
                canvas.create_image(o.x, o.y, image=ImageTk.PhotoImage(o.image))
        if self.curDiv != None:
            canvas.create_rectangle(self.curDiv.x, self.curDiv.y, 
                        self.curDiv.x + self.curDiv.width, self.curDiv.y + self.curDiv.height, 
                        fill=self.curDiv.color)

    def drawToolbar(self, canvas):
        canvas.create_rectangle(0, 0, self.toolBarMargin, self.height, fill="gray", width=0)
        canvas.create_rectangle(1, 10, self.toolBarMargin, 40, fill=self.curColor)
        canvas.create_rectangle(1, 50, self.toolBarMargin, 80, fill="")
        canvas.create_text(self.toolBarMargin/2, 80, text="set bg\ncolor", anchor="center")
        newY = 90
        for key in self.toolsDict:
            canvas.create_rectangle(0, newY, self.toolBarMargin, newY + 30)
            canvas.create_text(self.toolBarMargin/2, newY + 35, text=self.toolsDict[key], anchor="center")
            newY += 50

    def drawAlignBar(self, canvas):
        canvas.create_rectangle(self.toolBarMargin, 0, self.width, 50, fill="grey", width=0)
        x0 = self.toolBarMargin * 2
        for align in self.aligns:
            canvas.create_rectangle(x0, 0, x0+50, 50)
            canvas.create_text(x0, 0, text=self.aligns[align], anchor="nw")
            x0 += 60
        canvas.create_rectangle(self.width, 0, self.width-100, 50, fill="navy", width=0)
        canvas.create_text(self.width-50, 25, text="Export", anchor="center", fill="white", font="Helvetica 28" )

    def drawHighlight(self, canvas):
        for obj in self.selectedObjs:
            x = obj.x
            y = obj.y
            height = obj.height
            width = obj.width
            canvas.create_rectangle(x, y, x+width, y+height, outline="red", width=5)

    def drawBackground(self, canvas):
        if self.bgColor != None:
            canvas.create_rectangle(0, 0, self.width, self.height, fill=self.bgColor)
    
    # to be implemented later
    # will draw current tool on top of cursor
    def drawCursor(self, canvas):
        pass

    def redrawAll(self, canvas):
        self.drawBackground(canvas)
        self.drawObjects(canvas)
        self.drawHighlight(canvas)
        self.drawAlignBar(canvas)
        self.drawToolbar(canvas)
        canvas.create_text(self.width/2, 60, text=f"current tool: {self.toolsDict[self.curTool]}")

MyApp(width=1000, height=1000)