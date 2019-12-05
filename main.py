# TODO
# debug
# fix undo/redo
# fix selected object move
# add help screen

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

class HelpMode(Mode):
    def appStarted(mode):
        self.count = 0
    def redrawAll(mode, canvas):
        pass
    def keyPressed(mode, event):
        if event.key == "Left":
            self.count -= 1
        elif event.key == "Right":
            self.count += 1
        else:
            mode.app.setActiveMode(mode.app.editorMode)

class SplashScreenMode(Mode):
    def redrawAll(mode, canvas):
        pass
    def keyPressed(mode, event):
        if event.key == "h":
            mode.app.setActiveMode(mode.app.helpMode)
        else:
            mode.app.setActiveMode(mode.app.editorMode)

class EditorMode(Mode):
    def setAlignButtons(mode):
        mode.aligns = {0: "left", 1: "center hori", 2: "right", 3: "top", 4: "center vert", 5: "bottom"}
        mode.alignBarButtons = []
        x0 = 100
        buttonWidth = 32
        buttonHeight = 32
        margin = 50

        for align in mode.aligns:
            url = f'assets/aligns/{align}.png'
            icon = mode.loadImage(url)
            button = Button(x0, 0,buttonWidth, buttonHeight, icon, mode.aligns[align], align)
            mode.alignBarButtons.append(button)
            x0 += buttonWidth + margin
        mode.setExportButtons()
        mode.setTextButtons()

    def setExportButtons(mode):
        buttonWidth = 130
        button1 = Button(mode.width-buttonWidth, 0, buttonWidth, mode.alignBarMargin, None, "Export HTML", "exportCanvas", fill="navy", textColor="white")
        button2 = Button(mode.width-buttonWidth*2-10, 0, buttonWidth, mode.alignBarMargin, None, "Save Canvas", "saveCanvas", fill="navy", textColor="white")
        button3 = Button(mode.width-buttonWidth*3-20, 0, buttonWidth, mode.alignBarMargin, None, "Import Canvas", "importCanvas", fill="navy", textColor="white")
        mode.alignBarButtons.append(button1)
        mode.alignBarButtons.append(button2)
        mode.alignBarButtons.append(button3)

    def setTextButtons(mode):
        width = 100
        textToolsLabels = ["Edit Text", "Font Size", "Font"]
        textToolFunctions = ["editText", "fontSize", "fontFamily"]
        mode.textToolButtons = []
        x0 = 600
        i=0
        for tool in textToolsLabels:
            if tool == "Edit Text":
                button = TextButton(x0, 0, width, mode.alignBarMargin, tool, None, textToolFunctions[i])
            else:
                button = TextButton(x0, 0, width, mode.alignBarMargin, None, tool, textToolFunctions[i])
            mode.textToolButtons.append(button)
            x0 += width + mode.alignBarMargin
            i += 1
        mode.setTextButtonsInfo()

    def setTextButtonsInfo(mode):
        mode.textToolButtons[1].label1 = mode.curFontSize
        mode.textToolButtons[2].label1 = mode.curFont

    def setToolButtons(mode):
        mode.toolsDict = {0: "cursor", 1: "rectangle", 2: "text", 3: "image", 4: "fill bg"}
        mode.toolsBar = []
        mode.toolIcons = []
        newY = 100
        toolButtonHeight = 32
        for key in mode.toolsDict:
            url = f'assets/tools/{key}.png'
            icon = None
            if os.path.isfile(url):
                icon = mode.loadImage(url)
                mode.toolIcons.append(icon)
            button = Button(0, newY, mode.toolBarMargin, toolButtonHeight, icon, mode.toolsDict[key], key)
            mode.toolsBar.append(button)
            newY += 50
        makeStaticBtn = Button(0, 600, 50, 50, None, "Make\nStatic", "makeStatic")
        makeStaticBtn.fontSize = 14
        mode.toolsBar.append(makeStaticBtn)
        makeAbsoluteBtn = Button(0, 675, 50, 50, None, "Make\nAbsolute", "makeAbsolute")
        makeAbsoluteBtn.fontSize = 14
        mode.toolsBar.append(makeAbsoluteBtn)
        colorPalette = ColorPalette(0, 0, mode.toolBarMargin, mode.toolBarMargin, "Set\nColor", "colorPicker", mode.curColor)
        mode.toolsBar.append(colorPalette)

    def initTextProps(mode):
        mode.curFont = "Helvetica"
        mode.curFontSize = 14

    # help from https://stackoverflow.com/questions/3142054/python-add-items-from-txt-file-into-a-list
    # and list of fonts with help from: 
    # https://stackoverflow.com/questions/39614027/list-available-font-families-in-tkinter
    def addTkinterFonts(mode):
        with open('assets/tkinter_fonts.txt', 'r') as f:
            mode.tkinterFonts = set([line.strip().lower() for line in f])

    def appStarted(mode):
        mode.toolBarMargin = 50
        mode.alignBarMargin = 50
        mode.curColor = "red"
        mode.initTextProps()

        mode.setToolButtons()
        mode.setAlignButtons()

        mode.addTkinterFonts()

        mode.curTool = 0
        mode.objects = []
        mode.childObjects = []
        mode.startX = 0
        mode.startY = 0
        mode.startItemXs = []
        mode.startItemYs = []
        mode.curDiv = None
        mode.selectedObj = []
        mode.bgColor = "white"
        mode.shiftHeld = False
        mode.selectedObjs = []
        mode.moves = []
        mode.nextMoves = []
        mode.resizing = False
        mode.mouseX = 0
        mode.mouseY = 0

    def mouseMoved(mode, event):
        mode.updateMouse(event.x, event.y)

    def updateMouse(mode, x, y):
        mode.mouseX = x
        mode.mouseY = y

    def keyPressed(mode, event):
        if event.key == "c":
            mode.curTool = 0
        elif event.key == "r":
            mode.curTool = 1
        elif event.key == "t":
            mode.curTool = 2
        elif event.key == "i":
            mode.curTool = 3
        elif event.key == "Escape":
            mode.clearSelection()
        elif event.key == "Delete" and mode.selectedObj != None:
            mode.deleteSelectedObject()
        elif event.key == "s":
            mode.shiftHeld = not mode.shiftHeld
        elif event.key == "Z":
            mode.undo()
        elif event.key == "Y":
            mode.redo()
        elif event.key == "h":
            mode.app.setActiveMode(mode.app.helpMode)

    def undo(mode):
        if len(mode.moves) == 0:
            return
        lastMove = mode.moves.pop()
        mode.nextMoves.append(lastMove)
        if lastMove[0] == "add":
            mode.objects.remove(lastMove[1])
        elif lastMove[0] == "delete":
            mode.objects.append(lastMove[1])
        elif lastMove[0] == "move":
            for move in lastMove[1:]:
                move[0].x = move[1][0]
                move[0].y = move[1][1]
        elif lastMove[0] == "change bg":
            mode.bgColor = lastMove[1]

    def redo(mode):
        if len(mode.nextMoves) == 0:
            return
        nextMove = mode.nextMoves.pop()
        mode.moves.append(nextMove)
        if nextMove[0] == "add":
            mode.objects.append(nextMove[1])
        elif nextMove[0] == "delete":
            mode.objects.remove(nextMove[1])
        elif nextMove[0] == "move":
            for move in nextMove[1:]:
                move[0].x = move[2][0]
                move[0].y = move[2][1]
    
    def detectResizeClick(mode, x, y):
        obj = mode.selectedObjs[0]
        if type(obj) == Img:
            objX, objY = mode.getCoordsOfImg(obj)
        else:
            objX, objY = obj.x, obj.y
        if type(obj) != Text:
            resizeClick = ((objX+obj.width-5 < x and objX+obj.width+5 > x) and (objY+obj.height-5 < y and objY+obj.height+5 > y))
            return resizeClick

    def checkObjectBounds(mode, obj, x, y):
        if type(obj) == Img:
            objX, objY = mode.getCoordsOfImg(obj)
        else:
            objX, objY = obj.x, obj.y
        return (((objX < x and (objX + obj.width) > x) or
                    (objX > x and (objX + obj.width) < x)) and
                    ((objY < y and (objY + obj.height) > y) or
                    (objY > y and (objY + obj.height) < y)))

    def addClickedObjects(mode, obj, x, y):
        if mode.checkObjectBounds(obj, x, y):
            if mode.shiftHeld:
                mode.selectedObjs.append(obj)
                return True
            else:
                mode.selectedObjs = [obj]
                return True

    def findClickedObject(mode, x, y):
        if len(mode.selectedObjs) == 1 and type(mode.selectedObjs[0]) != Text and mode.detectResizeClick(x, y):
            mode.resizing = True
            mode.startX = x
            mode.startY = y
        else:
            reversedObjects = list(reversed(mode.objects))
            allObjects =  mode.childObjects + reversedObjects
            for obj in allObjects:
                if mode.addClickedObjects(obj, x, y):
                    break
            mode.startItemXs = []
            mode.startItemYs = []
            mode.startX = x
            mode.startY = y
            for obj in mode.selectedObjs:
                mode.startItemXs.append(obj.x)
                mode.startItemYs.append(obj.y)

    def findSelectedTool(mode, x, y):
        for button in mode.toolsBar:
            if (button.didHitButton(x, y)):
                if type(button.functionName) == int:
                    mode.curTool = button.functionName
                elif button.functionName == "colorPicker":
                    mode.pickNewColor()
                elif button.functionName == "makeStatic":
                    mode.makeComponentStatic()
                elif button.functionName == "makeAbsolute":
                    mode.makeComponentAbsolute()

    def makeComponentAbsolute(mode):
        if len(mode.selectedObjs) == 1:
            if mode.selectedObjs[0] in mode.childObjects:
                childObj = mode.selectedObjs[0]
                childObj.parentObject.childObjects.remove(childObj)    
                mode.objects.add(childObj)
            mode.selectedObjs[0].static = False



    def childrenShareSpace(mode, childObj, parentObj):
        for child in parentObj.childObjects:
            if type(child) == Img:
                childX, childY = mode.getCoordsOfImg(child)
            else:
                childX, childY = child.x, child.y
            if type(childObj) == Img:
                childObjX, childObjY = mode.getCoordsOfImg(childObj)
            else:
                childObjX, childObjY = childObj.x, childObj.y

            if ((childObjX<childX+child.width) and
                (childObjX+childObj.width>childX) and
                (childObjY<childY+child.height) and 
                (childObjY+childObj.height>childY)):
                # checking for collisions
                return True
        return False

    def checkInChildRow(mode, childObj, parentObj):
        for child in parentObj.childObjects:
            if type(child) == Img:
                childY = mode.getCoordsOfImg(child)[1]
            else:
                childY = child.y
            if type(childObj) == Img:
                childObjY = mode.getCoordsOfImg(childObj)[1]
            else:
                childObjY = childObj.y
            if (childY+child.height<childObjY or
                  childY > childObjY + childObj.height):
                # checking to see if all children are in the same row
                return True
        return False
    def getCoordsOfImg(mode, img):
        return (img.x-img.width/2, img.y-img.height/2)

    def makeComponentStatic(mode):
        if len(mode.selectedObjs) == 1:
            mode.selectedObjs[0].static = True
        elif len(mode.selectedObjs) == 2 and mode.selectedHasDiv():
            obj1 = mode.selectedObjs[0]
            obj2 = mode.selectedObjs[1]
            if ((obj2.x < obj1.x and obj2.y < obj1.y) and 
                (obj1.width < obj2.width and obj1.height < obj2.height) and 
                type(obj2) == Div):
                parentObj, childObj = obj2, obj1
            elif ((obj2.x > obj1.x and obj2.y > obj1.y) and
                    (obj1.width > obj2.width and obj1.height > obj2.height) and 
                    type(obj1) == Div):
                parentObj, childObj = obj1, obj2
            else:
                mode.displayError("Not a valid placement of a child object:\nChild is not fully within the parent.")
                return
            if mode.childrenShareSpace(childObj, parentObj):
                mode.displayError("Not a valid placement of a child object:\nChild overlaps an already existing child.")
                return
            elif mode.checkInChildRow(childObj, parentObj):
                mode.displayError("Not a valid placement of a child object:\nNot along the same row as other children.")
            parentObj.childObjects.append(childObj)
            childObj.parentObject = parentObj
            childObj.static = True
            mode.childObjects.append(childObj)
            mode.objects.remove(childObj)
        mode.selectedObjs = []

    def pickNewColor(mode):
        newColor = colorchooser.askcolor(initialcolor=mode.curColor)
        if newColor != (None, None):
            mode.curColor = newColor[-1]
        mode.toolsBar[-1].fill = mode.curColor

    def saveCanvas(mode):
        filePath = filedialog.asksaveasfilename(initialdir=os.getcwd(),
                                      title="Please select a file name for saving:",
                                      filetypes=[("Object", "obj")])
        if filePath != None and filePath != "":
            f = open(filePath, "wb")
            pickle.dump(mode.objects, f)

    def importCanvas(mode):
        filePath = filedialog.askopenfilename(initialdir=os.getcwd(),
                                title="Please select a file name for saving:",
                                      filetypes=[("Object", "obj")])
        if os.path.isfile(filePath):
            f = open(filePath, "rb")
            mode.objects = pickle.load(f)
            mode.selectedObjs = []

    def findSelectedAlign(mode, x, y):
        for button in mode.alignBarButtons:
            if button.didHitButton(x, y):
                if type(button.functionName) == int:
                    mode.alignSelectedObjects(button.functionName)
                elif button.functionName == "exportCanvas":
                    mode.exportCanvas()
                elif button.functionName == "saveCanvas":
                    mode.saveCanvas()
                elif button.functionName == "importCanvas":
                    mode.importCanvas()
        for button in mode.textToolButtons:
            if button.didHitButton(x, y):
                mode.handleTextButtonPress(button.functionName)
                
    def updateFontFamily(mode):
        newFont = mode.getUserInput("What should the new font be?")
        if newFont.lower() in mode.tkinterFonts:
            mode.curFont = newFont
        else:
            mode.displayError("Font not available")

    def updateFontSize(mode):
        newFontSize = mode.getUserInput("What should the new font size be?")
        if type(newFontSize) == int and newFontSize > 0:
            mode.curFontSize = newFontSize
        else:
            mode.displayError("Not a valid font size")

    def displayError(mode, message):
        messagebox.showerror("Error", message)

    def handleTextButtonPress(mode, functionName):
        if functionName == "fontFamily":
            mode.updateFontFamily()
            mode.updateSelected()
        elif functionName == "fontSize":
            mode.updateFontSize()
            mode.updateSelected()
        elif functionName == "editText":
            newText = mode.getUserInput("New text?")
            if type(newText) :
                mode.selectedObjs[0].content = newText
                mode.selectedObjs[0].height = (newText.count("\n")+1)* mode.selectedObjs[0].font_size/2
                mode.selectedObjs[0].width = len(newText) * mode.selectedObjs[0].font_size

    def updateSelected(mode):
        for obj in mode.selectedObjs:
            obj.font_family = mode.curFont
            obj.font_size = mode.curFontSize
        mode.setTextButtonsInfo()

    def exportCanvas(mode):
        fileName = mode.getUserInput("Name of Site?")
        if fileName != None:
            mode.convertToCSS()
            exportToHTML(fileName, mode.objects)
            exportToCSS(mode.bgColor, CSSClass.classes)

    def convertToCSS(mode):
        for obj in mode.objects:
            if obj.static:
                position = "static"
            else:
                position = "absolute"
            if type(obj) == Div and obj.childObjects != []:
                if obj.static:
                    mode.convertToCSSStatic(obj)
                    mode.convertChildrenToCSS(obj)
                else:
                    mode.convertToCSSAbsolute(obj)
                    mode.convertChildrenToCSS(obj)
            else:
                if obj.static:
                    mode.convertToCSSStatic(obj)
                else:
                    mode.convertToCSSAbsolute(obj)

    def convertChildrenToCSS(mode, obj):
        if type(obj) != Div or obj.childObjects == []:
            if obj.static:
                mode.convertToCSSStatic(obj)
            else:
                mode.convertToCSSAbsolute(obj)
        else:
            for child in obj.childObjects:
                mode.convertChildrenToCSS(child)

    def getMargins(mode, obj):
        if obj.parentObject == None:
            if type(obj) == Img:
                return mode.getCoordsOfImg(obj)
            else:
                return (obj.x, obj.y)
        else:
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
                if obj != obj2:
                    if type(obj2) == Img:
                        rightEdge2 = obj2.x + obj2.width/2
                        botEdge2 = obj2.y + obj2.height/2
                    else:
                        rightEdge2 = obj2.x + obj2.width
                        botEdge2 = obj2.y + obj2.height
                    if (leftEdge > rightEdge2) and (leftEdge - rightEdge2 < smallestLeftMargin):
                        smallestLeftMargin =  leftEdge - rightEdge2
                    if (topEdge > botEdge2) and (topEdge - botEdge2 < smallestTopMargin):
                        smallestTopMargin =  topEdge - botEdge2 
            return (smallestLeftMargin, smallestTopMargin)

    def convertToCSSStatic(mode, obj):
        position="static"
        smallestLeftMargin, smallestTopMargin = mode.getMargins(obj)
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

    def convertToCSSAbsolute(mode, obj):
        position="absolute"
        if isinstance(obj, Div):
            newClass = CSSClass(obj.color, obj.height, obj.width, position=position,
                                left=obj.x-mode.toolBarMargin, top=obj.y-mode.alignBarMargin)
            obj.cssClass = CSSClass.classes[newClass]
        elif isinstance(obj, Text):
            newClass = CSSClass(obj.color, left=obj.x-mode.toolBarMargin, top=obj.y-mode.alignBarMargin, 
                    position=position, font_family=obj.font_family, font_size=obj.font_size)
            obj.cssClass = CSSClass.classes[newClass]
        elif isinstance(obj, Img):
            x0 = obj.x - obj.width//2 - mode.toolBarMargin
            y0 = obj.y - obj.height//2 - mode.alignBarMargin
            newClass = CSSClass(height=obj.height, width=obj.width, left=x0, top=y0, position=position)
            obj.cssClass = CSSClass.classes[newClass]

    def alignSelectedObjects(mode, align):
        toAlignPositions = []
        newPosition = None # x coord or y coord, depending on which align was selected
        for obj in mode.selectedObjs:
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
        mode.alignSelectedObjectPositions(newPosition, align)

    def alignSelectedObjectPositions(mode, newPosition, align):
        for obj in mode.selectedObjs:
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

    def clearSelection(mode):
        mode.selectedObjs = []
        mode.startItemXs = []
        mode.startItemYs = []
        mode.resizing = False

    def deleteSelectedObject(mode):
        for obj in mode.selectedObjs:
            mode.moves.append(("delete", obj))
            mode.objects.remove(obj)
            mode.clearSelection()

    def moveChildren(mode, obj, dx, dy):
        if type(obj) != Div or obj.childObjects == []:
            obj.x += dx
            obj.y += dy
        else:
            for child in obj.childObjects:
                mode.moveChildren(child, dx, dy)

    def moveSelectedObjects(mode, x, y):
        dx = x - mode.startX
        dy = y - mode.startY
        for i in range(len(mode.selectedObjs)):
            obj = mode.selectedObjs[i]
            obj.x += dx
            obj.y += dy
            if type(obj) == Div and obj.childObjects != []:
                mode.moveChildren(obj, dx, dy)
        mode.startX = x
        mode.startY = y

    def selectedHasText(mode):
        for obj in mode.selectedObjs:
            if type(obj) != Text:
                return False
        return True

    def selectedHasDiv(mode):
        for obj in mode.selectedObjs:
            if type(obj) == Div:
                return True
        return False

    def selectedHasStatic(mode):
        for obj in mode.selectedObjs:
            if obj.static:
                return True
        return False

    def selectedObjectClicked(mode, x, y):
        for obj in mode.selectedObjs:
            if type(obj) == Img:
                objX, objY = mode.getCoordsOfImg(obj)
            else:
                objX, objY = obj.x, obj.y
            if ((objX < x and objY < y) and
                (objX + obj.width > x and objY + obj.height > y)):
                return True
        return False

    def mousePressed(mode, event):
        if event.x < mode.toolBarMargin and event.x > 0:
            mode.findSelectedTool(event.x, event.y)
        elif ((event.x > mode.toolBarMargin and event.x <= mode.width) and
                (event.y > 0 and event.y < mode.alignBarMargin)):
            mode.findSelectedAlign(event.x, event.y)
        elif mode.curTool == 0 and not mode.selectedObjectClicked(event.x, event.y):
            mode.findClickedObject(event.x, event.y)
        elif mode.curTool == 1:
            mode.startX = event.x
            mode.startY = event.y
            mode.curDiv = Div(mode.startX, mode.startY, 0, 0, mode.curColor)
        elif mode.curTool == 2:
            content = mode.getUserInput("Input text")
            if content != None:
                textHeight = mode.curFontSize * (content.count("\n")+1)
                textWidth = mode.curFontSize / 2 * len(content)
                newText = Text(event.x, event.y, textWidth, textHeight, content, mode.curColor, mode.curFont, mode.curFontSize)
                mode.objects.append(newText)
                mode.moves.append(("add", newText))
        elif mode.curTool == 3:
            mode.placeImage(event.x, event.y)
        elif mode.curTool == 4:
            mode.moves.append(("change bg", mode.bgColor, mode.curColor))
            mode.bgColor = mode.curColor

    def placeImage(mode, x, y):
        filetypes=[('JPEG', 'jpeg'), ('PNG', 'png')]
        imagePath = filedialog.askopenfilename( initialdir=os.getcwd(),
                                    title="Please select a file:",
                                    filetypes=filetypes)
        if os.path.isfile(imagePath):
                image = mode.loadImage(imagePath)
                imgWidth, imgHeight = image.size
                newImage = mode.scaleImage(image, 500/(max(imgWidth, imgHeight)))
                newImage.format = image.format
                newImg = Img(x, y, 500/(max(imgWidth, imgHeight)), newImage, image)
                mode.objects.append(newImg)
                mode.moves.append(("add", newImg))

    # add initial item dimensions of selected objects; if a violation occurs, reset to initial dimensions
    def resizeChildren(mode, obj, dx, dy):
        if type(obj) == Img or (type(obj) == Div and obj.childObjects == []):
            obj.width +=  dx
            obj.height += dy
        elif type(obj) == Text:
            pass
        else:
            for child in obj.childObjects:
                mode.resizeChildren(child, dx, dy)

    def resizeSelection(mode, x, y):
        obj = mode.selectedObjs[0]
        if not obj.static:
            if type(obj) != Img:
                dx = x - mode.startX
                dy = y - mode.startY 
                obj.width +=  dx
                obj.height += dy
                if type(obj) == Div and obj.childObjects != []:
                    mode.resizeChildren(obj, dx, dy)
                mode.startX = x
                mode.startY = y
            else:
                width, height = obj.image.size
                dx = x - mode.startX
                dy = y - mode.startY
                oldFormat = obj.image.format
                if max(width, height) == height and (height+dy) > 5:
                    obj.image = mode.scaleImage(obj.image, (obj.height+dy)/(obj.height))
                    obj.width = (obj.height+dy)/(obj.height)*width
                    obj.height += dy
                elif max(width, height) == width and (width+dx) > 5:
                    obj.image = mode.scaleImage(obj.image, (obj.width+dx)/(obj.width))
                    obj.height = (obj.width+dx)/(obj.width)*height
                    obj.width += dx
                obj.image.format = oldFormat
                mode.startX = x
                mode.startY = y

    def mouseDragged(mode, event):
        mode.updateMouse(event.x, event.y)
        if mode.curTool == 0 and mode.resizing and len(mode.selectedObjs) != 0:
            mode.resizeSelection(event.x, event.y)
        elif (mode.curTool == 0 and len(mode.selectedObjs) != 0 and event.y > mode.alignBarMargin
                    and not mode.selectedHasStatic()):
            mode.moveSelectedObjects(event.x, event.y)
        elif mode.curTool == 1 and mode.curDiv != None:
            width = event.x - mode.startX
            height = event.y - mode.startY
            mode.curDiv.height = height
            mode.curDiv.width = width

    def mouseReleased(mode, event):
        if mode.curTool == 0 and mode.resizing:
            mode.resizing = False
            if len(mode.selectedObjs) > 0 and type(mode.selectedObjs[0]) == Img:
                obj = mode.selectedObjs[0]
                oldFormat = obj.image.format
                scaleFactor = max(obj.image.size)/max(obj.fullSize.size)
                obj.image = mode.scaleImage(obj.fullSize, scaleFactor)
                obj.image.format = oldFormat
        elif mode.curTool == 0 and len(mode.selectedObjs) != 0:
            move = ["move"]
            for i in range(len(mode.selectedObjs)):
                obj = mode.selectedObjs[i]
                move.append((obj, (mode.startItemXs[i], mode.startItemYs[i]), (obj.x, obj.y)))
            if len(mode.moves) == 0 or mode.moves[-1] != move:
                mode.moves.append(move)
        elif mode.curTool == 1 and mode.curDiv != None and mode.curDiv.height > 5 and mode.curDiv.width > 5:
            x0, y0 = mode.curDiv.x, mode.curDiv.y
            x1 = x0 + mode.curDiv.width
            y1 = y0 + mode.curDiv.height
            newDiv = Div(min(x0, x1), min(y0, y1), 
                            abs(mode.curDiv.width), abs(mode.curDiv.height), mode.curColor)
            mode.objects.append(newDiv)
            mode.moves.append(("add", newDiv))
            mode.curDiv = None

    def drawDiv(mode, canvas, div):
        if type(div) == Div and div.childObjects == []:
            canvas.create_rectangle(div.x, div.y, div.x + div.width, div.y + div.height, fill=div.color)
        elif type(div) != Div:
            mode.drawComponent(canvas, div)
        else:
            canvas.create_rectangle(div.x, div.y, div.x + div.width, div.y + div.height, fill=div.color)
            for obj in div.childObjects:
                mode.drawDiv(canvas, obj)

    def drawObjects(mode, canvas):
        for o in mode.objects:
            mode.drawComponent(canvas, o)
        if mode.curDiv != None:
            canvas.create_rectangle(mode.curDiv.x, mode.curDiv.y, 
                        mode.curDiv.x + mode.curDiv.width, mode.curDiv.y + mode.curDiv.height, 
                        fill=mode.curDiv.color)
    def drawComponent(mode, canvas, o):
        if isinstance(o, Div):
            mode.drawDiv(canvas, o)
        elif isinstance(o, Text):
            canvas.create_text(o.x, o.y, text=o.content, fill=o.color, anchor="nw", font=f"{o.font_family} {o.font_size}")
        elif isinstance(o, Img):
            canvas.create_image(o.x, o.y, image=ImageTk.PhotoImage(o.image))

    def drawToolbar(mode, canvas):
        canvas.create_rectangle(0, 0, mode.toolBarMargin, mode.height, fill="gray", width=0)
        canvas.create_rectangle(1, 10, mode.toolBarMargin, 40, fill=mode.curColor)
        for button in mode.toolsBar:
            mode.drawButton(canvas, button)

    def drawButton(mode, canvas, button):
        canvas.create_rectangle(button.x, button.y, button.x+button.width, button.y+button.height, fill=button.fill)
        if button.image != None:
            canvas.create_image(button.x+button.width/2, button.y+button.height/2, image=ImageTk.PhotoImage(button.image))
            canvas.create_text(button.x+button.width/2, button.y+button.height, text=button.label, anchor="n")
        elif type(button) == ColorPalette:
            canvas.create_rectangle(button.x, button.y, button.x+button.width, button.y+button.height, fill=button.fill)
            canvas.create_text(button.x+button.width/2, button.y+button.height, text=button.label, anchor="n")
        else:
            canvas.create_text(button.x+button.width/2, button.y+button.height/2, text=button.label, font=f"Helvetica {button.fontSize}", anchor="center", fill=button.textColor)

    def drawTextButton(mode, canvas, button):
        canvas.create_rectangle(button.x, button.y, button.x+button.width, button.y+button.height-button.textSize, fill=button.fill)
        canvas.create_text(button.x+button.width/2, button.y, text=button.label1, anchor="n", fill=button.textColor)
        canvas.create_text(button.x+button.width/2, button.y+button.height, text=button.label, anchor="s", fill=button.textColor)

    def drawAlignBar(mode, canvas):
        canvas.create_rectangle(mode.toolBarMargin, 0, mode.width, 50, fill="grey", width=0)
        for button in mode.alignBarButtons:
            mode.drawButton(canvas, button)
        if mode.curTool == 2 or (mode.curTool == 0 and mode.selectedHasText()):
            mode.drawTextTools(canvas)
    
    def drawTextTools(mode, canvas):
        for button in mode.textToolButtons:
            if button.functionName == "editText":
                if mode.curTool == 0 and len(mode.selectedObjs) == 1 and mode.selectedHasText():
                    mode.drawTextButton(canvas, button)
            else:
                mode.drawTextButton(canvas, button)

    def drawHighlight(mode, canvas):
        for obj in mode.selectedObjs:
            if type(obj) == Img:
                x, y = mode.getCoordsOfImg(obj)
            else:
                x, y = obj.x, obj.y
            height = obj.height
            width = obj.width
            canvas.create_rectangle(x, y, x+width, y+height, outline="black", width=5)
            if len(mode.selectedObjs) == 1 and not mode.selectedObjs[0].static:
                canvas.create_rectangle(x+width-5, y+height-5, x+width+5, y+height+5, fill="red")

    def drawBackground(mode, canvas):
        if mode.bgColor != None:
            canvas.create_rectangle(0, 0, mode.width, mode.height, fill=mode.bgColor)
    
    def drawCursor(mode, canvas):
        if mode.curTool != 0:
            canvas.create_image(mode.mouseX, mode.mouseY, image=ImageTk.PhotoImage(mode.toolIcons[mode.curTool]))

    def redrawAll(mode, canvas):
        mode.drawBackground(canvas)
        mode.drawObjects(canvas)
        mode.drawHighlight(canvas)
        mode.drawAlignBar(canvas)
        mode.drawToolbar(canvas)
        mode.drawCursor(canvas)
        canvas.create_text(mode.width/2, 60, text=f"shift on?: {mode.shiftHeld}")

class MyModalApp(ModalApp):
    def appStarted(app):
        app.splashScreenMode = SplashScreenMode()
        app.editorMode = EditorMode()
        app.helpMode = HelpMode()
        app.setActiveMode(app.editorMode)

newApp = MyModalApp(width=1440, height=900)