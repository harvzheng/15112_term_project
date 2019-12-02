# TODO
# 1.a. refactor for toolbar
# 3. add relative positioning (divs have children)
# 4. add error messages
# 5. add cursor
# 6. direct text entry onto canvas

############################################################
# Citations:
# cat.jpeg is under CC0 licences from unsplash.com.
#   link: https://unsplash.com/photos/9SWHIgu8A8k
# Graphics package provided by CMU's 15-112, which mainly uses
# TKinter and PIL.
#   link: https://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
# Icons used are designed by user "Kiranshastry" and are from Flaticon.com. 
# Name of the pack where the icons are from is "Alignment and Tools Icon Pack." 
#   link: https://www.flaticon.com/packs/alignment-and-tools
############################################################

from modules.cmu_112_graphics import *
from exporter import *
from tkinter import *
from tkinter import colorchooser
from classes import *
from PIL import Image
import os

class MyApp(App):

    def setAlignButtons(self):
        self.aligns = {0: "left", 1: "center hori", 2: "right", 3: "top", 4: "center vert", 5: "bottom"}
        self.alignButtons = []
        x0 = 100
        buttonWidth = 32
        buttonHeight = 32
        margin = 50

        for align in self.aligns:
            url = f'assets/aligns/{align}.png'
            icon = self.loadImage(url)
            button = Button(x0, 0,buttonWidth, buttonHeight, icon, self.aligns[align], align)
            self.alignButtons.append(button)
            x0 += buttonWidth + margin

    def setToolButtons(self):
        pass

    def appStarted(self):
        self.toolsDict = {0: "cursor", 1: "rectangle", 2: "text", 3: "image"}
        self.setAlignButtons()
        self.curTool = 0
        self.toolBarMargin = 50
        self.alignBarMargin = 50
        self.objects = []
        self.startX = 0
        self.startY = 0
        self.startItemXs = []
        self.startItemYs = []
        self.curDiv = None
        self.selectedObj = []
        self.curColor = "black"
        self.bgColor = "white"
        self.curFont = "Helvetica"
        self.curFontSize = 14
        self.shiftHeld = False
        self.selectedObjs = []
        self.moves = []
        self.nextMoves = []
        self.resizing = False

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
            self.shiftHeld = not self.shiftHeld
        elif event.key == "Z":
            self.undo()
        elif event.key == "Y":
            self.redo()
    
    # def keyReleased(self, event):
    #     if event.key == "s":
    #         self.shiftHeld = False

    def undo(self):
        if len(self.moves) == 0:
            return
        lastMove = self.moves.pop()
        self.nextMoves.append(lastMove)
        if lastMove[0] == "add":
            self.objects.remove(lastMove[1])
        elif lastMove[0] == "delete":
            self.objects.append(lastMove[1])
            print(f"undoing by adding{lastMove[1]}")
        elif lastMove[0] == "move":
            for move in lastMove[1:]:
                move[0].x = move[1][0]
                move[0].y = move[1][1]
        elif lastMove[0] == "change bg":
            self.bgColor = lastMove[1]

    def redo(self):
        if len(self.nextMoves) == 0:
            return
        nextMove = self.nextMoves.pop()
        self.moves.append(nextMove)
        if nextMove[0] == "add":
            self.objects.append(nextMove[1])
        elif nextMove[0] == "delete":
            self.objects.remove(nextMove[1])
        elif nextMove[0] == "move":
            for move in nextMove[1:]:
                move[0].x = move[2][0]
                move[0].y = move[2][1]
    
    def detectResizeClick(self, x, y):
        obj = self.selectedObjs[0]
        if type(obj) == Img:
            return ((obj.x+obj.width/2-5 < x and obj.x+obj.width/2+5 > x) and (obj.y+obj.height/2-5 < y and obj.y+obj.height/2+5 > y))
        else:
            return ((obj.x+obj.width-5 < x and obj.x+obj.width+5 > x) and (obj.y+obj.height-5 < y and obj.y+obj.height+5 > y))


    def findClickedObject(self, x, y):
        if len(self.selectedObjs) == 1 and type(self.selectedObjs[0]) != Text and self.detectResizeClick(x, y):
            self.resizing = True
            self.startX = x
            self.startY = y
        else:
            for obj in self.objects:
                if (((obj.x < x and (obj.x + obj.width) > x) or
                    (obj.x > x and (obj.x + obj.width) < x)) and
                    ((obj.y < y and (obj.y + obj.height) > y) or
                    (obj.y > y and (obj.y + obj.height) < y))
                    and type(obj) != Img):
                    if self.shiftHeld:
                        self.selectedObjs.append(obj)
                        break
                    else:
                        self.selectedObjs = [obj]
                elif (type(obj) == Img and 
                    (obj.y + obj.height/2 > y and obj.y - obj.height/2 < y) and
                    (obj.x + obj.width/2 > x and obj.x - obj.width/2 < x)):
                    if self.shiftHeld:
                        self.selectedObjs.append(obj)
                        break
                    else:
                        self.selectedObjs = [obj]
            self.startItemXs = []
            self.startItemYs = []
            self.startX = x
            self.startY = y
            for obj in self.selectedObjs:
                self.startItemXs.append(obj.x)
                self.startItemYs.append(obj.y)

    def findSelectedTool(self, x, y):
        if y <= 30 and y >= 0:
            newColor = colorchooser.askcolor(initialcolor=self.curColor)
            if newColor != (None, None):
                self.curColor = newColor[-1]
        elif y > 50 and y < 80:
            self.moves.append(("change bg", self.bgColor, self.curColor))
            self.bgColor = self.curColor
        initialY = 90
        for key in self.toolsDict:
            if (y >= initialY and y <= (initialY + 30)):
                self.curTool = key
            initialY += 50

    def findSelectedAlign(self, x, y):
        for button in self.alignButtons:
            if button.didHitButton(x, y):
                self.alignSelectedObjects(button.functionName)
        if x <= self.width and x >= self.width - 100:
            self.exportCanvas()
        elif x >= self.width - 200 and x <= self.width - 150:
            self.curFont = self.getUserInput("Font family?")
            self.updateSelected()
        elif x >= self.width - 300 and x <= self.width - 250:
            self.curFontSize = self.getUserInput("Font size?")
            self.updateSelected()
        elif x >= self.width - 400 and x <= self.width - 350 and len(self.selectedObjs) == 1:
            newText = self.getUserInput("New text?")
            self.selectedObjs[0].content = newText
            self.selectedObjs[0].height = (newText.count("\n")+1)* self.selectedObjs[0].font_size/2
            self.selectedObjs[0].width = len(newText) * self.selectedObjs[0].font_size

    def updateSelected(self):
        for obj in self.selectedObjs:
            obj.font_family = self.curFont
            obj.font_size = self.curFontSize

    def exportCanvas(self):
        fileName = self.getUserInput("Name of Site?")
        if fileName != None:
            self.convertToCSS()
            exportToHTML(fileName, self.objects)
            exportToCSS(self.bgColor, CSSClass.classes)

    def convertToCSS(self):
        for obj in self.objects:
            if isinstance(obj, Div):
                newClass = CSSClass(obj.color, obj.height, obj.width, 
                                    left=obj.x-self.toolBarMargin, top=obj.y-self.alignBarMargin)
                obj.cssClass = CSSClass.classes[newClass]
            elif isinstance(obj, Text):
                newClass = CSSClass(obj.color, left=obj.x-self.toolBarMargin, top=obj.y-self.alignBarMargin, 
                        font_family=obj.font_family, font_size=obj.font_size)
                obj.cssClass = CSSClass.classes[newClass]
            elif isinstance(obj, Img):
                x0 = obj.x - obj.width//2 - self.toolBarMargin
                y0 = obj.y - obj.height//2 - self.alignBarMargin
                newClass = CSSClass(height=obj.height, width=obj.width, left=x0, top=y0)
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
        self.resizing = True

    def deleteSelectedObject(self):
        for obj in self.selectedObjs:
            self.moves.append(("delete", obj))
            self.objects.remove(obj)
            self.clearSelection()

    def moveSelectedObjects(self, x, y):
        move = ["move"]
        for i in range(len(self.selectedObjs)):
            obj = self.selectedObjs[i]
            obj.x = self.startItemXs[i] + x - self.startX
            obj.y = self.startItemYs[i] + y - self.startY
        #     move.append((obj, (self.startItemXs[i], self.startItemYs[i]), (obj.x, obj.y)))
        # if len(self.moves) == 0 or self.moves[-1] != move:
        #     self.moves.append(move)

    def selectedHasText(self):
        for obj in self.selectedObjs:
            if type(obj) != Text:
                return False
        return True

    def mousePressed(self, event):
        if event.x < self.toolBarMargin and event.x > 0:
            self.findSelectedTool(event.x, event.y)
        elif ((event.x > self.toolBarMargin and event.x <= self.width) and
                (event.y > 0 and event.y < self.alignBarMargin)):
            self.findSelectedAlign(event.x, event.y)
        elif self.curTool == 0:
            self.findClickedObject(event.x, event.y)
        elif self.curTool == 1:
            self.startX = event.x
            self.startY = event.y
            self.curDiv = Div(self.startX, self.startY, 0, 0, self.curColor)
        elif self.curTool == 2:
            content = self.getUserInput("Input text")
            textHeight = self.curFontSize * (content.count("\n")+1)
            textWidth = self.curFontSize / 2 * len(content)
            newText = Text(event.x, event.y, textWidth, textHeight, content, self.curColor, self.curFont, self.curFontSize)
            self.objects.append(newText)
            self.moves.append(("add", newText))
        elif self.curTool == 3:
            imageName = self.getUserInput("Image path")
            if imageName != "":
                imagePath = os.getcwd() + '/' + imageName
                try:
                    image = self.loadImage(imagePath)
                    imgWidth, imgHeight = image.size
                    newImage = self.scaleImage(image, 500/(max(imgWidth, imgHeight)))
                    newImage.format = image.format
                    newImg = Img(event.x, event.y, 500/(max(imgWidth, imgHeight)), newImage, image)
                    self.objects.append(newImg)
                    self.moves.append(("add", newImg))
                except:
                    print(f"Path not valid: {imagePath}")

    def resizeSelection(self, x, y):
        obj = self.selectedObjs[0]
        if type(obj) != Img:
            width = x - self.startX
            height = y - self.startY 
            obj.width +=  width
            obj.height += height
            self.startX = x
            self.startY = y
        else:
            width, height = obj.image.size
            dx = x - self.startX
            dy = y - self.startY
            oldFormat = obj.image.format
            if max(width, height) == height and (height-dy) > 0:
                obj.image = self.scaleImage(obj.image, (obj.height+dy)/(obj.height))
                obj.width = (obj.height+dy)/(obj.height)*width
                obj.height += dy
            elif max(width, height) == width and (width-dx) > 0:
                obj.image = self.scaleImage(obj.image, (obj.width+dx)/(obj.width))
                obj.height = (obj.width+dx)/(obj.width)*height
                obj.width += dx
            obj.image.format = oldFormat
            self.startX = x
            self.startY = y

    def mouseDragged(self, event):
        if self.curTool == 0 and self.resizing and len(self.selectedObjs) != 0:
            self.resizeSelection(event.x, event.y)
        elif self.curTool == 0 and len(self.selectedObjs) != 0 and event.y > self.alignBarMargin:
            self.moveSelectedObjects(event.x, event.y)
        elif self.curTool == 1 and self.curDiv != None:
            width = event.x - self.startX
            height = event.y - self.startY
            self.curDiv.height = height
            self.curDiv.width = width

    def mouseReleased(self, event):
        if self.curTool == 0 and self.resizing:
            self.resizing = False
            if len(self.selectedObjs) > 0 and type(self.selectedObjs[0]) == Img:
                obj = self.selectedObjs[0]
                scaleFactor = max(obj.image.size)/max(obj.fullSize.size)
                obj.image = self.scaleImage(obj.fullSize, scaleFactor)
        elif self.curTool == 0 and len(self.selectedObjs) != 0:
            move = ["move"]
            for i in range(len(self.selectedObjs)):
                obj = self.selectedObjs[i]
                move.append((obj, (self.startItemXs[i], self.startItemYs[i]), (obj.x, obj.y)))
            if len(self.moves) == 0 or self.moves[-1] != move:
                self.moves.append(move)
        elif self.curTool == 1 and self.curDiv != None and self.curDiv.height > 5 and self.curDiv.width > 5:
            x0, y0 = self.curDiv.x, self.curDiv.y
            x1 = x0 + self.curDiv.width
            y1 = y0 + self.curDiv.height
            newDiv = Div(min(x0, x1), min(y0, y1), 
                            abs(self.curDiv.width), abs(self.curDiv.height), self.curColor)
            self.objects.append(newDiv)
            self.moves.append(("add", newDiv))
            self.curDiv = None

    def drawObjects(self, canvas):
        for o in self.objects:
            if isinstance(o, Div):
                canvas.create_rectangle(o.x, o.y, o.x + o.width, o.y + o.height, fill=o.color)
            elif isinstance(o, Text):
                canvas.create_text(o.x, o.y, text=o.content, fill=o.color, anchor="nw", font=f"{o.font_family} {o.font_size}")
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

    def drawButton(self, canvas, button):
        canvas.create_rectangle(button.x, button.y, button.x+button.width, button.y+button.height)
        canvas.create_image(button.x+button.width/2, button.y+button.height/2, image=ImageTk.PhotoImage(button.image))
        canvas.create_text(button.x+button.width/2, button.y+button.height, text=button.label, anchor="n")

    def drawAlignBar(self, canvas):
        canvas.create_rectangle(self.toolBarMargin, 0, self.width, 50, fill="grey", width=0)
        for button in self.alignButtons:
            self.drawButton(canvas, button)
        canvas.create_rectangle(self.width, 0, self.width-100, 50, fill="navy", width=0)
        canvas.create_text(self.width-50, 25, text="Export", anchor="center", fill="white", font="Helvetica 28" )
        if self.curTool == 2 or (self.curTool == 0 and self.selectedHasText()):
            self.drawTextTools(canvas)
    
    def drawTextTools(self, canvas):
        canvas.create_text(self.width - 150, 15, text=f"font family:\n{self.curFont}", anchor="e")
        canvas.create_text(self.width - 250, 15, text=f"font size:\n{self.curFontSize}", anchor="e")
        if len(self.selectedObjs) == 1:
            canvas.create_text(self.width - 350, 15, text=f"edit text", anchor="e")

    def drawHighlight(self, canvas):
        for obj in self.selectedObjs:
            x = obj.x
            y = obj.y
            height = obj.height
            width = obj.width
            if type(obj) == Img:
                canvas.create_rectangle(x-width/2, y-height/2, x+width/2, y+height/2, outline="red", width=5)
                if len(self.selectedObjs) == 1:
                    canvas.create_rectangle(x+width/2-5, y+height/2-5, x+width/2+5, y+height/2+5, fill="black")
            else:
                canvas.create_rectangle(x, y, x+width, y+height, outline="red", width=5)
                if len(self.selectedObjs) == 1:
                    canvas.create_rectangle(x+width-5, y+height-5, x+width+5, y+height+5, fill="black")


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