# TODO
# debug
# fix undo/redo
# add static to absolute parent objects such that they align at the top

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
#
# filechooser/error/colorchooser stuff from:
# https://runestone.academy/runestone/books/published/thinkcspy/GUIandEventDrivenProgramming/02_standard_dialog_boxes.html
############################################################

from modules.cmu_112_graphics import *
from exporter import *
from tkinter import *
from tkinter import colorchooser, messagebox, filedialog
from classes import *
from PIL import Image
import _pickle as pickle
import os

class MyApp(App):
    def setAlignButtons(self):
        self.aligns = {0: "left", 1: "center hori", 2: "right", 3: "top", 4: "center vert", 5: "bottom"}
        self.alignBarButtons = []
        x0 = 100
        buttonWidth = 32
        buttonHeight = 32
        margin = 50

        for align in self.aligns:
            url = f'assets/aligns/{align}.png'
            icon = self.loadImage(url)
            button = Button(x0, 0,buttonWidth, buttonHeight, icon, self.aligns[align], align)
            self.alignBarButtons.append(button)
            x0 += buttonWidth + margin
        self.setExportButtons()
        self.setTextButtons()

    def setExportButtons(self):
        buttonWidth = 130
        button1 = Button(self.width-buttonWidth, 0, buttonWidth, self.alignBarMargin, None, "Export HTML", "exportCanvas", fill="navy", textColor="white")
        button2 = Button(self.width-buttonWidth*2-10, 0, buttonWidth, self.alignBarMargin, None, "Save Canvas", "saveCanvas", fill="navy", textColor="white")
        button3 = Button(self.width-buttonWidth*3-20, 0, buttonWidth, self.alignBarMargin, None, "Import Canvas", "importCanvas", fill="navy", textColor="white")
        self.alignBarButtons.append(button1)
        self.alignBarButtons.append(button2)
        self.alignBarButtons.append(button3)

    def setTextButtons(self):
        width = 100
        textToolsLabels = ["Edit Text", "Font Size", "Font"]
        textToolFunctions = ["editText", "fontSize", "fontFamily"]
        self.textToolButtons = []
        x0 = 600
        i=0
        for tool in textToolsLabels:
            if tool == "Edit Text":
                button = TextButton(x0, 0, width, self.alignBarMargin, tool, None, textToolFunctions[i])
            else:
                button = TextButton(x0, 0, width, self.alignBarMargin, None, tool, textToolFunctions[i])
            self.textToolButtons.append(button)
            x0 += width + self.alignBarMargin
            i += 1
        self.setTextButtonsInfo()

    def setTextButtonsInfo(self):
        self.textToolButtons[1].label1 = self.curFontSize
        self.textToolButtons[2].label1 = self.curFont

    def setToolButtons(self):
        self.toolsDict = {0: "cursor", 1: "rectangle", 2: "text", 3: "image", 4: "fill bg"}
        self.toolsBar = []
        self.toolIcons = []
        newY = 100
        toolButtonHeight = 32
        for key in self.toolsDict:
            url = f'assets/tools/{key}.png'
            icon = None
            if os.path.isfile(url):
                icon = self.loadImage(url)
                self.toolIcons.append(icon)
            button = Button(0, newY, self.toolBarMargin, toolButtonHeight, icon, self.toolsDict[key], key)
            self.toolsBar.append(button)
            newY += 50
        makeStaticBtn = Button(0, 600, 50, 50, None, "Make\nStatic", "makeStatic")
        makeStaticBtn.fontSize = 14
        self.toolsBar.append(makeStaticBtn)
        makeAbsoluteBtn = Button(0, 675, 50, 50, None, "Make\nAbsolute", "makeAbsolute")
        makeAbsoluteBtn.fontSize = 14
        self.toolsBar.append(makeAbsoluteBtn)
        colorPalette = ColorPalette(0, 0, self.toolBarMargin, self.toolBarMargin, "Set\nColor", "colorPicker", self.curColor)
        self.toolsBar.append(colorPalette)

    def initTextProps(self):
        self.curFont = "Helvetica"
        self.curFontSize = 14

    # help from https://stackoverflow.com/questions/3142054/python-add-items-from-txt-file-into-a-list
    # and list of fonts with help from: 
    # https://stackoverflow.com/questions/39614027/list-available-font-families-in-tkinter
    def addTkinterFonts(self):
        with open('assets/tkinter_fonts.txt', 'r') as f:
            self.tkinterFonts = set([line.strip().lower() for line in f])

    def appStarted(self):
        self.toolBarMargin = 50
        self.alignBarMargin = 50
        self.curColor = "red"
        self.initTextProps()

        self.setToolButtons()
        self.setAlignButtons()

        self.addTkinterFonts()

        self.curTool = 0
        self.objects = []
        self.childObjects = []
        self.startX = 0
        self.startY = 0
        self.startItemXs = []
        self.startItemYs = []
        self.curDiv = None
        self.selectedObj = []
        self.bgColor = "white"
        self.shiftHeld = False
        self.selectedObjs = []
        self.moves = []
        self.nextMoves = []
        self.resizing = False
        self.mouseX = 0
        self.mouseY = 0

    def mouseMoved(self, event):
        self.updateMouse(event.x, event.y)

    def updateMouse(self, x, y):
        self.mouseX = x
        self.mouseY = y

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
            objX, objY = self.getCoordsOfImg(obj)
        else:
            objX, objY = obj.x, obj.y
        if type(obj) != Text:
            resizeClick = ((objX+obj.width-5 < x and objX+obj.width+5 > x) and (objY+obj.height-5 < y and objY+obj.height+5 > y))
            return resizeClick

    def checkObjectBounds(self, obj, x, y):
        if type(obj) == Img:
            objX, objY = self.getCoordsOfImg(obj)
        else:
            objX, objY = obj.x, obj.y
        return (((objX < x and (objX + obj.width) > x) or
                    (objX > x and (objX + obj.width) < x)) and
                    ((objY < y and (objY + obj.height) > y) or
                    (objY > y and (objY + obj.height) < y)))

    def addClickedObjects(self, obj, x, y):
        if self.checkObjectBounds(obj, x, y):
            if self.shiftHeld:
                self.selectedObjs.append(obj)
                return True
            else:
                self.selectedObjs = [obj]
                return True

    def findClickedObject(self, x, y):
        if len(self.selectedObjs) == 1 and type(self.selectedObjs[0]) != Text and self.detectResizeClick(x, y):
            self.resizing = True
            self.startX = x
            self.startY = y
        else:
            reversedObjects = list(reversed(self.objects))
            allObjects =  self.childObjects + reversedObjects
            for obj in allObjects:
                if self.addClickedObjects(obj, x, y):
                    break
            self.startItemXs = []
            self.startItemYs = []
            self.startX = x
            self.startY = y
            for obj in self.selectedObjs:
                self.startItemXs.append(obj.x)
                self.startItemYs.append(obj.y)

    def findSelectedTool(self, x, y):
        for button in self.toolsBar:
            if (button.didHitButton(x, y)):
                if type(button.functionName) == int:
                    self.curTool = button.functionName
                elif button.functionName == "colorPicker":
                    self.pickNewColor()
                elif button.functionName == "makeStatic":
                    self.makeComponentStatic()
                elif button.functionName == "makeAbsolute":
                    self.makeComponentAbsolute()

    def makeComponentAbsolute(self):
        if len(self.selectedObjs) == 1:
            if self.selectedObjs[0] in self.childObjects:
                childObj = self.selectedObjs[0]
                childObj.parentObject.childObjects.remove(childObj)    
                self.objects.add(childObj)
            self.selectedObjs[0].static = False

    def childrenShareSpace(self, childObj, parentObj):
        for child in parentObj.childObjects:
            if type(child) == Img:
                childX, childY = self.getCoordsOfImg(child)
            if type(childObj) == Img:
                childObjX, childObjY = self.getCoordsOfImg(childObj)
            if ((childX+child.width>childObjX or childX<childObjX+childObj.width) or
                (childY+child.height>childObjY or childY<childObjY+childObj.height)):
                return True
        return False

    def getCoordsOfImg(self, img):
        return (img.x-img.width/2, img.y-img.height/2)

    def makeComponentStatic(self):
        print(self.selectedHasDiv())
        if len(self.selectedObjs) == 1:
            self.selectedObjs[0].static = True
        elif len(self.selectedObjs) == 2 and self.selectedHasDiv():
            obj1 = self.selectedObjs[0]
            obj2 = self.selectedObjs[1]
            if ((obj2.x < obj1.x and obj2.y < obj1.y) and 
                (obj1.width < obj2.width and obj1.height < obj2.height) and 
                type(obj2) == Div):
                parentObj, childObj = obj2, obj1
            elif ((obj2.x > obj1.x and obj2.y > obj1.y) and
                    (obj1.width > obj2.width and obj1.height > obj2.height) and 
                    type(obj1) == Div):
                parentObj, childObj = obj1, obj2
            else:
                self.displayError("Not a valid placement of a child object")
                return
            if self.childrenShareSpace(childObj, parentObj):
                self.displayError("Not a valid placement of a child object")
                return
            parentObj.childObjects.append(childObj)
            childObj.parentObject = parentObj
            childObj.static = True
            self.childObjects.append(childObj)
            self.objects.remove(childObj)

    def pickNewColor(self):
        newColor = colorchooser.askcolor(initialcolor=self.curColor)
        if newColor != (None, None):
            self.curColor = newColor[-1]
        self.toolsBar[-1].fill = self.curColor

    def saveCanvas(self):
        filePath = filedialog.asksaveasfilename(initialdir=os.getcwd(),
                                      title="Please select a file name for saving:",
                                      filetypes=[("Object", "obj")])
        if filePath != None and filePath != "":
            f = open(filePath, "wb")
            pickle.dump(self.objects, f)

    def importCanvas(self):
        filePath = filedialog.askopenfilename(initialdir=os.getcwd(),
                                title="Please select a file name for saving:",
                                      filetypes=[("Object", "obj")])
        if os.path.isfile(filePath):
            f = open(filePath, "rb")
            self.objects = pickle.load(f)

    def findSelectedAlign(self, x, y):
        for button in self.alignBarButtons:
            if button.didHitButton(x, y):
                if type(button.functionName) == int:
                    self.alignSelectedObjects(button.functionName)
                elif button.functionName == "exportCanvas":
                    self.exportCanvas()
                elif button.functionName == "saveCanvas":
                    self.saveCanvas()
                elif button.functionName == "importCanvas":
                    self.importCanvas()
        for button in self.textToolButtons:
            if button.didHitButton(x, y):
                self.handleTextButtonPress(button.functionName)
                
    def updateFontFamily(self):
        newFont = self.getUserInput("What should the new font be?")
        if newFont.lower() in self.tkinterFonts:
            self.curFont = newFont
        else:
            self.displayError("Font not available")

    def updateFontSize(self):
        newFontSize = self.getUserInput("What should the new font size be?")
        if type(newFontSize) == int and newFontSize > 0:
            self.curFontSize = newFontSize
        else:
            self.displayError("Not a valid font size")

    def displayError(self, message):
        messagebox.showerror("Error", message)

    def handleTextButtonPress(self, functionName):
        if functionName == "fontFamily":
            self.updateFontFamily()
            self.updateSelected()
        elif functionName == "fontSize":
            self.updateFontSize()
            self.updateSelected()
        elif functionName == "editText":
            newText = self.getUserInput("New text?")
            if type(newText) :
                self.selectedObjs[0].content = newText
                self.selectedObjs[0].height = (newText.count("\n")+1)* self.selectedObjs[0].font_size/2
                self.selectedObjs[0].width = len(newText) * self.selectedObjs[0].font_size

    def updateSelected(self):
        for obj in self.selectedObjs:
            obj.font_family = self.curFont
            obj.font_size = self.curFontSize
        self.setTextButtonsInfo()

    def exportCanvas(self):
        fileName = self.getUserInput("Name of Site?")
        if fileName != None:
            self.convertToCSS()
            exportToHTML(fileName, self.objects)
            exportToCSS(self.bgColor, CSSClass.classes)

    def convertToCSS(self):
        for obj in self.objects:
            if obj.static:
                position = "static"
            else:
                position = "absolute"
            if type(obj) == Div and obj.childObjects != []:
                if obj.static:
                    self.convertToCSSStatic(obj)
                    self.convertChildrenToCSS(obj)
                else:
                    newClass = CSSClass(obj.color, obj.height, obj.width, position=position,
                                        left=obj.x-self.toolBarMargin, top=obj.y-self.alignBarMargin)
                    obj.cssClass = CSSClass.classes[newClass]
                    self.convertChildrenToCSS(obj)
            else:
                if obj.static:
                    self.convertToCSSStatic(obj)
                else:
                    self.convertToCSSAbsolute(obj)

    def convertChildrenToCSS(self, obj):
        if type(obj) != Div or obj.childObjects == []:
            if obj.static:
                self.convertToCSSStatic(obj)
            else:
                self.convertToCSSAbsolute(obj)
        else:
            for child in obj.childObjects:
                self.convertChildrenToCSS(child)

    def getMargins(self, obj):
        childObjects = obj.parentObject.childObjects
        if type(obj) == Img:
            leftEdge = obj.x - obj.width/2
            topEdge = obj.y - obj.height/2
        else:
            leftEdge = obj.x
            topEdge = obj.y
        smallestLeftMargin = leftEdge - obj.parentObject.x
        smallestTopMargin = topEdge - obj.parentObject.y
        for obj2 in childObjects:
            if type(obj2) == Img:
                leftEdge2 = obj.x - obj.width/2
                topEdge2 = obj.y - obj.height/2
            else:
                leftEdge2 = obj.x
                topEdge2 = obj.y
            if (leftEdge - leftEdge2 > 0) and (leftEdge - leftEdge2 < smallestLeftMargin):
                smallestLeftMargin = leftEdge - leftEdge2
            if (topEdge - topEdge2 > 0) and (topEdge - topEdge2 < smallestTopMargin):
                smallestTopMargin = topEdge - topEdge2
        return (smallestLeftMargin, smallestTopMargin)

    def convertToCSSStatic(self, obj):
        position="static"
        smallestLeftMargin, smallestTopMargin = self.getMargins(obj)
        if isinstance(obj, Div):
            newClass = CSSClass(obj.color, obj.height, obj.width, position=position,
                                margin_left=smallestLeftMargin, margin_top=smallestTopMargin)
            obj.cssClass = CSSClass.classes[newClass]
        elif isinstance(obj, Text):
            newClass = CSSClass(obj.color, margin_left=smallestLeftMargin, margin_top=smallestTopMargin, 
                            position=position, font_family=obj.font_family, font_size=obj.font_size)
            obj.cssClass = CSSClass.classes[newClass]
        elif isinstance(obj, Img):
            newClass = CSSClass(height=obj.height, width=obj.width, margin_left=smallestLeftMargin, 
                            margin_top=smallestTopMargin, position=position)
            obj.cssClass = CSSClass.classes[newClass]        

    def convertToCSSAbsolute(self, obj):
        position="absolute"
        if isinstance(obj, Div):
            newClass = CSSClass(obj.color, obj.height, obj.width, position=position,
                                left=obj.x-self.toolBarMargin, top=obj.y-self.alignBarMargin)
            obj.cssClass = CSSClass.classes[newClass]
        elif isinstance(obj, Text):
            newClass = CSSClass(obj.color, left=obj.x-self.toolBarMargin, top=obj.y-self.alignBarMargin, 
                    position=position, font_family=obj.font_family, font_size=obj.font_size)
            obj.cssClass = CSSClass.classes[newClass]
        elif isinstance(obj, Img):
            x0 = obj.x - obj.width//2 - self.toolBarMargin
            y0 = obj.y - obj.height//2 - self.alignBarMargin
            newClass = CSSClass(height=obj.height, width=obj.width, left=x0, top=y0, position=position)
            obj.cssClass = CSSClass.classes[newClass]

    def alignSelectedObjects(self, align):
        toAlignPositions = []
        newPosition = None # x coord or y coord, depending on which align was selected
        for obj in self.selectedObjs:
            if type(obj) == Img:
                if align == 0: 
                    obj.x = newPosition + obj.width/2
                elif align == 1:
                    obj.x = newPosition
                elif align == 2:
                    obj.x = newPosition - obj.width/2
                elif align == 3:
                    obj.y = newPosition + obj.width/2
                elif align == 4:
                    obj.y = newPosition
                else:
                    obj.y = newPosition - obj.height/2
            else:
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
        self.alignSelectedObjectPositions(newPosition, align)

    def alignSelectedObjectPositions(self, newPosition, align):
        for obj in self.selectedObjs:
            if type(obj) == Img:
                if align == 0: 
                    obj.x = newPosition + obj.width/2
                elif align == 1:
                    obj.x = newPosition
                elif align == 2:
                    obj.x = newPosition - obj.width/2
                elif align == 3:
                    obj.y = newPosition + obj.height/2
                elif align == 4:
                    obj.y = newPosition
                else:
                    obj.y = newPosition - obj.height/2
            else:
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
        self.resizing = False

    def deleteSelectedObject(self):
        for obj in self.selectedObjs:
            self.moves.append(("delete", obj))
            self.objects.remove(obj)
            self.clearSelection()

    def moveChildren(self, obj, dx, dy):
        if type(obj) != Div or obj.childObjects == []:
            obj.x += dx
            obj.y += dy
        else:
            for child in obj.childObjects:
                self.moveChildren(child, dx, dy)

    def moveSelectedObjects(self, x, y):
        dx = x - self.startX
        dy = y - self.startY
        for i in range(len(self.selectedObjs)):
            obj = self.selectedObjs[i]
            obj.x += dx
            obj.y += dy
            if type(obj) == Div and obj.childObjects != []:
                self.moveChildren(obj, dx, dy)
        self.startX = x
        self.startY = y

    def selectedHasText(self):
        for obj in self.selectedObjs:
            if type(obj) != Text:
                return False
        return True

    def selectedHasDiv(self):
        for obj in self.selectedObjs:
            if type(obj) == Div:
                return True
        return False

    def selectedHasStatic(self):
        for obj in self.selectedObjs:
            if obj.static:
                print("selected has static")
                return True
        return False

    def selectedObjectClicked(self, x, y):
        for obj in self.selectedObjs:
            if type(obj) == Img:
                objX, objY = self.getCoordsOfImg(obj)
            else:
                objX, objY = obj.x, obj.y
            if ((objX < x and objY < y) and
                (objX + obj.width > x and objY + obj.height > y)):
                return True
        return False

    def mousePressed(self, event):
        if event.x < self.toolBarMargin and event.x > 0:
            self.findSelectedTool(event.x, event.y)
        elif ((event.x > self.toolBarMargin and event.x <= self.width) and
                (event.y > 0 and event.y < self.alignBarMargin)):
            self.findSelectedAlign(event.x, event.y)
        elif self.curTool == 0 and not self.selectedObjectClicked(event.x, event.y):
            self.findClickedObject(event.x, event.y)
        elif self.curTool == 1:
            self.startX = event.x
            self.startY = event.y
            self.curDiv = Div(self.startX, self.startY, 0, 0, self.curColor)
        elif self.curTool == 2:
            content = self.getUserInput("Input text")
            if content != None:
                textHeight = self.curFontSize * (content.count("\n")+1)
                textWidth = self.curFontSize / 2 * len(content)
                newText = Text(event.x, event.y, textWidth, textHeight, content, self.curColor, self.curFont, self.curFontSize)
                self.objects.append(newText)
                self.moves.append(("add", newText))
        elif self.curTool == 3:
            self.placeImage(event.x, event.y)
        elif self.curTool == 4:
            self.moves.append(("change bg", self.bgColor, self.curColor))
            self.bgColor = self.curColor

    def placeImage(self, x, y):
        filetypes=[('JPEG', 'jpeg'), ('PNG', 'png')]
        imagePath = filedialog.askopenfilename( initialdir=os.getcwd(),
                                    title="Please select a file:",
                                    filetypes=filetypes)
        if os.path.isfile(imagePath):
                image = self.loadImage(imagePath)
                imgWidth, imgHeight = image.size
                newImage = self.scaleImage(image, 500/(max(imgWidth, imgHeight)))
                newImage.format = image.format
                newImg = Img(x, y, 500/(max(imgWidth, imgHeight)), newImage, image)
                self.objects.append(newImg)
                self.moves.append(("add", newImg))

    # add initial item dimensions of selected objects; if a violation occurs, reset to initial dimensions
    def resizeChildren(self, obj, dx, dy):
        if type(obj) == Img or (type(obj) == Div and obj.childObjects == []):
            obj.width +=  dx
            obj.height += dy
        elif type(obj) == Text:
            pass
        else:
            for child in obj.childObjects:
                self.resizeChildren(child, dx, dy)

    def resizeSelection(self, x, y):
        obj = self.selectedObjs[0]
        if not obj.static:
            if type(obj) != Img:
                dx = x - self.startX
                dy = y - self.startY 
                obj.width +=  dx
                obj.height += dy
                if type(obj) == Div and obj.childObjects != []:
                    self.resizeChildren(obj, dx, dy)
                self.startX = x
                self.startY = y
            else:
                width, height = obj.image.size
                dx = x - self.startX
                dy = y - self.startY
                oldFormat = obj.image.format
                if max(width, height) == height and (height+dy) > 5:
                    obj.image = self.scaleImage(obj.image, (obj.height+dy)/(obj.height))
                    obj.width = (obj.height+dy)/(obj.height)*width
                    obj.height += dy
                elif max(width, height) == width and (width+dx) > 5:
                    obj.image = self.scaleImage(obj.image, (obj.width+dx)/(obj.width))
                    obj.height = (obj.width+dx)/(obj.width)*height
                    obj.width += dx
                obj.image.format = oldFormat
                self.startX = x
                self.startY = y

    def mouseDragged(self, event):
        self.updateMouse(event.x, event.y)
        if self.curTool == 0 and self.resizing and len(self.selectedObjs) != 0:
            self.resizeSelection(event.x, event.y)
        elif (self.curTool == 0 and len(self.selectedObjs) != 0 and event.y > self.alignBarMargin
                    and not self.selectedHasStatic()):
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
                oldFormat = obj.image.format
                scaleFactor = max(obj.image.size)/max(obj.fullSize.size)
                obj.image = self.scaleImage(obj.fullSize, scaleFactor)
                obj.image.format = oldFormat
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

    def drawDiv(self, canvas, div):
        if type(div) == Div and div.childObjects == []:
            canvas.create_rectangle(div.x, div.y, div.x + div.width, div.y + div.height, fill=div.color)
        elif type(div) != Div:
            self.drawComponent(canvas, div)
        else:
            canvas.create_rectangle(div.x, div.y, div.x + div.width, div.y + div.height, fill=div.color)
            for obj in div.childObjects:
                self.drawDiv(canvas, obj)

    def drawObjects(self, canvas):
        for o in self.objects:
            self.drawComponent(canvas, o)
        if self.curDiv != None:
            canvas.create_rectangle(self.curDiv.x, self.curDiv.y, 
                        self.curDiv.x + self.curDiv.width, self.curDiv.y + self.curDiv.height, 
                        fill=self.curDiv.color)
    def drawComponent(self, canvas, o):
        if isinstance(o, Div):
            self.drawDiv(canvas, o)
        elif isinstance(o, Text):
            canvas.create_text(o.x, o.y, text=o.content, fill=o.color, anchor="nw", font=f"{o.font_family} {o.font_size}")
        elif isinstance(o, Img):
            canvas.create_image(o.x, o.y, image=ImageTk.PhotoImage(o.image))

    def drawToolbar(self, canvas):
        canvas.create_rectangle(0, 0, self.toolBarMargin, self.height, fill="gray", width=0)
        canvas.create_rectangle(1, 10, self.toolBarMargin, 40, fill=self.curColor)
        for button in self.toolsBar:
            self.drawButton(canvas, button)

    def drawButton(self, canvas, button):
        canvas.create_rectangle(button.x, button.y, button.x+button.width, button.y+button.height, fill=button.fill)
        if button.image != None:
            canvas.create_image(button.x+button.width/2, button.y+button.height/2, image=ImageTk.PhotoImage(button.image))
            canvas.create_text(button.x+button.width/2, button.y+button.height, text=button.label, anchor="n")
        elif type(button) == ColorPalette:
            canvas.create_rectangle(button.x, button.y, button.x+button.width, button.y+button.height, fill=button.fill)
            canvas.create_text(button.x+button.width/2, button.y+button.height, text=button.label, anchor="n")
        else:
            canvas.create_text(button.x+button.width/2, button.y+button.height/2, text=button.label, font=f"Helvetica {button.fontSize}", anchor="center", fill=button.textColor)

    def drawTextButton(self, canvas, button):
        canvas.create_rectangle(button.x, button.y, button.x+button.width, button.y+button.height-button.textSize, fill=button.fill)
        canvas.create_text(button.x+button.width/2, button.y, text=button.label1, anchor="n", fill=button.textColor)
        canvas.create_text(button.x+button.width/2, button.y+button.height, text=button.label, anchor="s", fill=button.textColor)

    def drawAlignBar(self, canvas):
        canvas.create_rectangle(self.toolBarMargin, 0, self.width, 50, fill="grey", width=0)
        for button in self.alignBarButtons:
            self.drawButton(canvas, button)
        if self.curTool == 2 or (self.curTool == 0 and self.selectedHasText()):
            self.drawTextTools(canvas)
    
    def drawTextTools(self, canvas):
        for button in self.textToolButtons:
            if button.functionName == "editText":
                if self.curTool == 0 and len(self.selectedObjs) == 1 and self.selectedHasText():
                    self.drawTextButton(canvas, button)
            else:
                self.drawTextButton(canvas, button)

    def drawHighlight(self, canvas):
        for obj in self.selectedObjs:
            if type(obj) == Img:
                x, y = self.getCoordsOfImg(obj)
            else:
                x, y = obj.x, obj.y
            height = obj.height
            width = obj.width
            canvas.create_rectangle(x, y, x+width, y+height, outline="black", width=5)
            if len(self.selectedObjs) == 1 and not self.selectedObjs[0].static:
                canvas.create_rectangle(x+width-5, y+height-5, x+width+5, y+height+5, fill="red")

    def drawBackground(self, canvas):
        if self.bgColor != None:
            canvas.create_rectangle(0, 0, self.width, self.height, fill=self.bgColor)
    
    def drawCursor(self, canvas):
        if self.curTool != 0:
            canvas.create_image(self.mouseX, self.mouseY, image=ImageTk.PhotoImage(self.toolIcons[self.curTool]))

    def redrawAll(self, canvas):
        self.drawBackground(canvas)
        self.drawObjects(canvas)
        self.drawHighlight(canvas)
        self.drawAlignBar(canvas)
        self.drawToolbar(canvas)
        self.drawCursor(canvas)
        canvas.create_text(self.width/2, 60, text=f"shift on?: {self.shiftHeld}")

MyApp(width=1500, height=1000)