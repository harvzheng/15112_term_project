############################################################
# Citations:
# cat used from the help slides is from unsplash.com.
#   link: https://unsplash.com/photos/9SWHIgu8A8k
# dog used from the help slides and the video is from pexels.com.
#   link: https://www.pexels.com/photo/adorable-blur-breed-close-up-406014/
#
# Graphics package (cmu_112_graphics) provided by CMU's 15-112, 
# which mainly uses TKinter and PIL. Used to generate much of the
# app's features.
#   link: https://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
#
# Icons used (under assets/aligns and assets/tools) are designed by user 
# "Kiranshastry" and are from Flaticon.com. 
# Name of the pack where the icons are from is "Alignment and Tools Icon Pack." 
#   link: https://www.flaticon.com/packs/alignment-and-tools
############################################################
# main.py
# houses main logic for the editor component of the project, utilizing 
# 15-112's graphics package, as well as the graphical aspects and the model.
# also houses the overall modal app, including the splash screen, help screen
# and main editor.
############################################################

from modules.cmu_112_graphics import *
from exporter import *
from tkinter import *
from tkinter import colorchooser, messagebox, filedialog
from classes import *
from PIL import Image
import _pickle as pickle
import os

# help mode
class HelpMode(Mode):
    # gathers slides from assets for help
    def appStarted(mode):
        mode.count = 0
        mode.slides = []
        for imgName in sorted(os.listdir('assets/help')):
            url = 'assets/help/' + imgName
            img = mode.loadImage(url)
            mode.slides.append(img)

    # displays the images in order based on the count, which is manipulated with arrows
    def redrawAll(mode, canvas):
        canvas.create_image(mode.width/2, mode.height/2, image=ImageTk.PhotoImage(mode.slides[mode.count%len(mode.slides)]))

    # shifts count or changes screen
    def keyPressed(mode, event):
        if event.key == "Left":
            mode.count -= 1
        elif event.key == "Right":
            mode.count += 1
        else:
            mode.app.setActiveMode(mode.app.editorMode)

class SplashScreenMode(Mode):
    # displays simple info about the project
    def redrawAll(mode, canvas):
        canvas.create_text(mode.width/2, 50, text="WebSketch", font="Helvetica 72 italic", anchor="center")
        canvas.create_text(mode.width/2, 300, text="Press any key to get started.", font="Helvetica 48", anchor="center")
        canvas.create_text(mode.width/2, 500, text="Press h for help at any point.", font="Helvetica 48", anchor="center")

    # change to help screen or editor screen
    def keyPressed(mode, event):
        if event.key == "h":
            mode.app.setActiveMode(mode.app.helpMode)
        else:
            mode.app.setActiveMode(mode.app.editorMode)

class EditorMode(Mode):
    ######################################################
    # Model
    ######################################################
    # Setting Buttons

    # Creates buttons for alignments; includes icons from flaticon.com mentioned in citations
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

    # Creates buttons for exporting
    def setExportButtons(mode):
        buttonWidth = 130
        button1 = Button(mode.width-buttonWidth, 0, buttonWidth, mode.alignBarMargin, None, 
                        "Export HTML", "exportCanvas", fill="navy", textColor="white")
        button2 = Button(mode.width-buttonWidth*2-10, 0, buttonWidth, mode.alignBarMargin, None, 
                        "Save Canvas", "saveCanvas", fill="navy", textColor="white")
        button3 = Button(mode.width-buttonWidth*3-20, 0, buttonWidth, mode.alignBarMargin, None, 
                        "Import Canvas", "importCanvas", fill="navy", textColor="white")
        mode.alignBarButtons.append(button1)
        mode.alignBarButtons.append(button2)
        mode.alignBarButtons.append(button3)

    # Creates buttons for the text editing
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

    # for the two buttons, it helps it display the current font size and font family
    def setTextButtonsInfo(mode):
        mode.textToolButtons[1].label1 = mode.curFontSize
        mode.textToolButtons[2].label1 = mode.curFont

    # sets buttons for the tool bar (along the left side); includes icons from flaticon.com mentioned in citations
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

        makeLayerUp = Button(0, 450, mode.toolBarMargin, 50, None, "Layer\nUp", "moveLayerUp")
        makeLayerDown = Button(0, 525, mode.toolBarMargin, 50, None, "Layer\nDown", "moveLayerDown")
        makeLayerUp.fontSize = 14
        makeLayerDown.fontSize = 14
        mode.toolsBar.append(makeLayerUp)
        mode.toolsBar.append(makeLayerDown)
        makeStaticBtn = Button(0, 600, mode.toolBarMargin, 50, None, "Make\nStatic", "makeStatic")
        makeStaticBtn.fontSize = 14
        mode.toolsBar.append(makeStaticBtn)
        makeAbsoluteBtn = Button(0, 675, mode.toolBarMargin, 50, None, "Make\nAbsolute", "makeAbsolute")
        makeAbsoluteBtn.fontSize = 14
        mode.toolsBar.append(makeAbsoluteBtn)
        colorPalette = ColorPalette(0, 0, mode.toolBarMargin, mode.toolBarMargin, "Set\nColor", "colorPicker", mode.curColor)
        mode.toolsBar.append(colorPalette)

    # setting other stuff
    def initTextProps(mode):
        mode.curFont = "Helvetica"
        mode.curFontSize = 14

    # help from https://stackoverflow.com/questions/3142054/python-add-items-from-txt-file-into-a-list
    # and list of fonts with help from: 
    # https://stackoverflow.com/questions/39614027/list-available-font-families-in-tkinter
    # creates a list of tkinter supported fonts from a text file
    def addTkinterFonts(mode):
        with open('assets/tkinter_fonts.txt', 'r') as f:
            mode.tkinterFonts = set([line.strip().lower() for line in f])

    # generate overall structure for items by calling methods or setting default values
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
        mode.initialX = 0
        mode.initialY = 0
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

    ######################################################
    # Controller
    ######################################################
    # mouse functions

    # updates mouse for cursor
    def mouseMoved(mode, event):
        mode.updateMouse(event.x, event.y)

    # updates the mouse position in mode
    def updateMouse(mode, x, y):
        mode.mouseX = x
        mode.mouseY = y

    # checks to see where the mouse is pressed, and execute an action based on it.
    # if the mouse is pressed on the tool bar or align bar, it will find the tool or align.
    # if it clicked on an object, it will select the object.
    # otherwise, it will use the current selected tool.
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

    # updates mouse for cursor,
    # if the resize dot is hit, then the image will begin resizing.
    # if a rectangle is being created, its properties will be updated.
    # otherwise, if an image is selected, it will be moved
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

    # if the mouse is released, updates a resized object,
    # moves an object,
    # or appends a new rectangle to the canvas.
    def mouseReleased(mode, event):
        if mode.curTool == 0 and mode.resizing:
            mode.moves.append(("resize", mode.selectedObjs[0], (event.x - mode.initialX, event.y - mode.initialY)))
            mode.resizing = False
            if len(mode.selectedObjs) > 0 and type(mode.selectedObjs[0]) == Img:
                obj = mode.selectedObjs[0]
                oldFormat = obj.image.format
                scaleFactor = max(obj.image.size)/max(obj.fullSize.size)
                obj.image = mode.scaleImage(obj.fullSize, scaleFactor)
                obj.image.format = oldFormat
        elif mode.curTool == 0 and len(mode.selectedObjs) != 0:
            move = ("move", [], (event.x-mode.initialX, event.y-mode.initialY))
            for i in range(len(mode.selectedObjs)):
                obj = mode.selectedObjs[i]
                move[1].append(obj)
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

    # keyboard functions
    # just handles keyboard shortcuts
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
            mode.clearSelection()
            mode.undo()
        elif event.key == "Y":
            mode.clearSelection()
            mode.redo()
        elif event.key == "h":
            mode.app.setActiveMode(mode.app.helpMode)

    # undo/redo
    # the code keeps track of moves in mode.moves. in this rather long method,
    # actions can be undone based on the last move by resetting the last manipulated object
    # to its last state. pops off the move it undid to mode.nextMoves, which helps
    # redoing.
    def undo(mode):
        if len(mode.moves) == 0:
            return
        lastMove = mode.moves.pop()
        mode.nextMoves.append(lastMove)
        if lastMove[0] == "add":
            mode.objects.remove(lastMove[1])
        elif lastMove[0] == "delete":
            if lastMove[1] == 1: # 1 for child, 0 for nonchild
                mode.childObjects.append(lastMove[2])
            elif lastMove[1] == 0:
                mode.objects.append(lastMove[2])
        elif lastMove[0] == "move":
            for obj in lastMove[1]:
                obj.x -= lastMove[2][0]
                obj.y -= lastMove[2][1]
                if type(obj) == Div and obj.childObjects != []:
                    mode.moveChildren(obj, -lastMove[2][0], -lastMove[2][1])
        elif lastMove[0] == "change bg":
            mode.bgColor = lastMove[1]
        elif lastMove[0] == "resize":
            lastMove[1].width -= lastMove[2][0]
            lastMove[1].height -= lastMove[2][1]
            if type(lastMove[1]) == Div and lastMove[1].childObjects != []:
                mode.resizeChildren(lastMove[1], -lastMove[2][0], -lastMove[2][1])
        elif lastMove[0] == "static":
            mode.makeComponentAbsolute(lastMove[1][0])
        elif lastMove[0] == "absolute":
            if len(lastMove[1]) == 2:
                lastMove[1][1].childObjects.append(lastMove[1][0])
                lastMove[1][0].parentObject = lastMove[1][1]
            lastMove[1][0].static = True
            mode.childObjects.append(lastMove[1][0])
            mode.objects.remove(lastMove[1][0])
        elif lastMove[0] == "change font":
            for obj in lastMove[1]:
                obj.font_family = lastMove[2][0]
        elif lastMove[0] == "change font size":
            for obj in lastMove[1]:
                obj.font_size = lastMove[2][0]
                obj.height = lastMove[2][0] * (obj.content.count("\n")+1)
                obj.width = lastMove[2][0] / 2 * len(obj.content)
        elif lastMove[0] == "change text":
            newText = lastMove[2][0]
            lastMove[1].content = newText
            lastMove[1].height = (newText.count("\n")+1)* lastMove[1].font_size/2
            lastMove[1].width = len(newText) *lastMove[1].font_size
        elif lastMove[0] == "align":
            for i in range(len(lastMove[1])):
                lastMove[1][i].x = lastMove[2][0]
                lastMove[1][i].y = lastMove[2][1]
        elif lastMove[0] == "up layer":
            mode.moveLayerDown(lastMove[1])
        elif lastMove[0] == "down layer":
            mode.moveLayerUp(lastMove[1])

    # similar to undo, if someone tries do redo something,
    # it will check mode.nextMoves to see if there are any
    # moves to redo, and revert it to the new state.
    def redo(mode):
        if len(mode.nextMoves) == 0:
            return
        nextMove = mode.nextMoves.pop()
        mode.moves.append(nextMove)
        if nextMove[0] == "add":
            mode.objects.append(nextMove[1])
        elif nextMove[0] == "delete":
            if nextMove[1] == 1: # 1 for child, 0 for nonchild
                mode.childObjects.remove(nextMove[2])
            elif nextMove[1] == 0:
                mode.objects.remove(nextMove[2])
        elif nextMove[0] == "move":
            for obj in nextMove[1]:
                obj.x += nextMove[2][0]
                obj.y += nextMove[2][1]
                if type(obj) == Div and obj.childObjects != []:
                    mode.moveChildren(obj, nextMove[2][0], nextMove[2][1])
        elif nextMove[0] == "change bg":
            mode.bgColor = lastMove[2]
        elif nextMove[0] == "resize":
            nextMove[1].width += nextMove[2][0]
            nextMove[1].height += nextMove[2][1]
            if type(nextMove[1]) == Div and nextMove[1].childObjects != []:
                mode.resizeChildren(nextMove[1], nextMove[2][0], nextMove[2][1])
        elif nextMove[0] == "up layer":
            mode.moveLayerUp(nextMove[1])
        elif nextMove[0] == "down layer":
            mode.moveLayerDown(nextMove[1])
        elif nextMove[0] == "static":
            if len(nextMove[1]) == 2:
                nextMove[1][1].childObjects.append(nextMove[1][0])
                nextMove[1][0].parentObject = nextMove[1][1]
            nextMove[1][0].static = True
            mode.childObjects.append(nextMove[1][0])
            mode.objects.remove(nextMove[1][0])
        elif nextMove[0] == "absolute":
            mode.makeComponentAbsolute(nextMove[1][0])
        elif nextMove[0] == "change font":
            for obj in nextMove[1]:
                obj.font_family = nextMove[2][1]
        elif nextMove[0] == "change font size":
            for obj in nextMove[1]:
                obj.font_size = nextMove[2][1]
                obj.height = nextMove[2][1] * (obj.content.count("\n")+1)
                obj.width = nextMove[2][1] / 2 * len(obj.content)
        elif nextMove[0] == "change text":
            newText = nextMove[2][1]
            nextMove[1].content = newText
            nextMove[1].height = (newText.count("\n")+1)* nextMove[1].font_size/2
            nextMove[1].width = len(newText) *nextMove[1].font_size
        elif nextMove[0] == "align":
            for i in range(len(nextMove[1])):
                if type(nextMove[1][i]) == Img:
                    nextMove[1][i].x = nextMove[3][0] + nextMove[1][i].width/2
                    nextMove[1][i].y = nextMove[3][1] + nextMove[1][i].height/2
                else:
                    nextMove[1][i].x = nextMove[3][0]
                    nextMove[1][i].y = nextMove[3][1]

    # tool helper functions

    # learned to use color picker from:
    # https://runestone.academy/runestone/books/published/thinkcspy/GUIandEventDrivenProgramming/02_standard_dialog_boxes.html
    # allows user to select color and sets the palette to the color.
    def pickNewColor(mode):
        newColor = colorchooser.askcolor(initialcolor=mode.curColor)
        if newColor != (None, None):
            mode.curColor = newColor[-1]
        mode.toolsBar[-1].fill = mode.curColor

    # finds a selected button from the tool bar and executes the btuton's function accordingly.
    def findSelectedTool(mode, x, y):
        for button in mode.toolsBar:
            if (button.didHitButton(x, y)):
                if type(button.functionName) == int:
                    mode.curTool = button.functionName
                elif button.functionName == "colorPicker":
                    mode.pickNewColor()
                elif button.functionName == "makeStatic":
                    mode.makeComponentStatic()
                elif button.functionName == "makeAbsolute" and len(mode.selectedObjs) == 1:
                    obj = mode.selectedObjs[0]
                    if obj.parentObject != None:
                        mode.moves.append(("absolute", (obj, parentObject)))
                    else:
                        mode.moves.append(("absolute", (obj)))
                    mode.makeComponentAbsolute(obj)
                elif len(mode.selectedObjs) == 1 and button.functionName == "moveLayerUp":
                    mode.moveLayerUp(mode.selectedObjs[0])
                elif len(mode.selectedObjs) == 1 and button.functionName == "moveLayerDown":
                    mode.moveLayerDown(mode.selectedObjs[0])

    # detects if a click is within the 10x10 boundaries of the resize box, and only works
    # if it doesn't have text.
    def detectResizeClick(mode, x, y):
        obj = mode.selectedObjs[0]
        if type(obj) == Img:
            objX, objY = mode.getCoordsOfImg(obj)
        else:
            objX, objY = obj.x, obj.y
        if type(obj) != Text:
            resizeClick = ((objX+obj.width-5 < x and objX+obj.width+5 > x) and (objY+obj.height-5 < y and objY+obj.height+5 > y))
            return resizeClick

    # moves object a layer down in the canvas.
    def moveLayerDown(mode, obj):
        if obj in mode.objects:
            mode.moves.append(('down layer', obj))
            newIndex = mode.objects.index(obj) - 1
            if newIndex >= 0:
                mode.objects.remove(obj)
                mode.objects.insert(newIndex, obj)

    # moves object a layer up in the canvas.
    def moveLayerUp(mode, obj):
        if obj in mode.objects:
            mode.moves.append(('up layer', obj))
            newIndex = mode.objects.index(obj) + 1
            if len(mode.objects) > newIndex:
                mode.objects.remove(obj)
                mode.objects.insert(newIndex, obj)

    # selection helper functions
    # converts image x, y to upper left coordinates
    def getCoordsOfImg(mode, img):
        return (img.x-img.width/2, img.y-img.height/2)

    # adds clicked objects to be selected
    def addClickedObjects(mode, obj, x, y):
        if mode.checkObjectBounds(obj, x, y):
            if mode.shiftHeld:
                mode.selectedObjs.append(obj)
                return True
            else:
                mode.selectedObjs = [obj]
                return True

    # check if a click is within an object's bounds
    def checkObjectBounds(mode, obj, x, y):
        if type(obj) == Img:
            objX, objY = mode.getCoordsOfImg(obj)
        else:
            objX, objY = obj.x, obj.y
        return (((objX < x and (objX + obj.width) > x) or
                    (objX > x and (objX + obj.width) < x)) and
                    ((objY < y and (objY + obj.height) > y) or
                    (objY > y and (objY + obj.height) < y)))

    # finds clicked objects and selects them, unless it is resizing in which case 
    # it will start resizing.
    def findClickedObject(mode, x, y):
        mode.startX = x
        mode.startY = y
        mode.initialX = x
        mode.initialY = y
        if len(mode.selectedObjs) == 1 and type(mode.selectedObjs[0]) != Text and mode.detectResizeClick(x, y):
            mode.resizing = True
        else:
            reversedObjects = list(reversed(mode.objects))
            allObjects =  mode.childObjects + reversedObjects
            for obj in allObjects:
                if mode.addClickedObjects(obj, x, y):
                    break
            mode.startItemXs = []
            mode.startItemYs = []
            for obj in mode.selectedObjs:
                mode.startItemXs.append(obj.x)
                mode.startItemYs.append(obj.y)

    # clears selections
    def clearSelection(mode):
        mode.selectedObjs = []
        mode.startItemXs = []
        mode.startItemYs = []
        mode.resizing = False

    # recursively deletes children of a div
    def deleteChildren(mode, obj):
        if type(obj) != Div or obj.childObjects != [] and obj in mode.childObjects:
            mode.childObjects.remove(obj)
        else:
            for child in obj.childObjects:
                mode.deleteChildren(child)

    # deletes an object from the canvas.
    def deleteSelectedObject(mode):
        for obj in mode.selectedObjs:
            if obj in mode.objects:
                mode.moves.append(("delete", 0, obj))
                mode.objects.remove(obj)
                if type(obj) == Div and obj.childObjects != []:
                    mode.deleteChildren(obj)
                mode.clearSelection()
            elif obj in mode.childObjects:
                mode.moves.append(("delete", 1, obj))
                mode.childObjects.remove(obj)
                mode.clearSelection()

    # checks if the current selection has only text text objects.
    def selectedHasText(mode):
        for obj in mode.selectedObjs:
            if type(obj) != Text:
                return False
        return True

    # checks if the current selection has a rectangle object.
    def selectedHasDiv(mode):
        for obj in mode.selectedObjs:
            if type(obj) == Div:
                return True
        return False

    # checks if the current selection has a static object.
    def selectedHasStatic(mode):
        for obj in mode.selectedObjs:
            if obj.static:
                return True
        return False

    # checks if a mousepress clicked on an already selected object.
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

    # learned to use filedialog from:
    # https://runestone.academy/runestone/books/published/thinkcspy/GUIandEventDrivenProgramming/02_standard_dialog_boxes.html
    # gets the image from a file browser and places it, scaling it small at first.
    def placeImage(mode, x, y):
        filetypes=[('JPEG', 'jpeg'), ('JPG', 'jpg'), ('PNG', 'png')]
        imagePath = filedialog.askopenfilename( initialdir=os.getcwd(),
                                    title="Please select an image:",
                                    filetypes=filetypes)
        if os.path.isfile(imagePath):
            image = mode.loadImage(imagePath)
            imgWidth, imgHeight = image.size
            newImage = mode.scaleImage(image, 500/(max(imgWidth, imgHeight)))
            newImage.format = image.format
            newImg = Img(x, y, 500/(max(imgWidth, imgHeight)), newImage, image)
            mode.objects.append(newImg)
            mode.moves.append(("add", newImg))

    # move helper functions
    # moves the children of a parent object
    def moveChildren(mode, obj, dx, dy):
        if type(obj) != Div or obj.childObjects == []:
            obj.x += dx
            obj.y += dy
        else:
            for child in obj.childObjects:
                mode.moveChildren(child, dx, dy)

    # moves items
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

    # resize helper functions

    # resizes children of a parent recursively.
    def resizeChildren(mode, obj, dx, dy):
        if type(obj) == Img or (type(obj) == Div and obj.childObjects == []):
            obj.width +=  dx
            obj.height += dy
        elif type(obj) == Text:
            pass
        else:
            for child in obj.childObjects:
                mode.resizeChildren(child, dx, dy)

    # resizes the selected object
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

    # static/absolute helper functions

    # finds the parent object and child object. throws error if there are any
    # violations. once they are found, the child object is made a child of the parent object.
    def makeComponentStatic(mode):
        if len(mode.selectedObjs) == 1:
            mode.selectedObjs[0].static = True
            mode.moves.append(("static", (mode.selectedObjs[0])))
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
            mode.moves.append(("static", (childObj, parentObj)))
            parentObj.childObjects.append(childObj)
            childObj.parentObject = parentObj
            childObj.static = True
            mode.childObjects.append(childObj)
            mode.objects.remove(childObj)
        mode.selectedObjs = []

    # makes a component absolute by setting its static property to false, and removing it
    # from its parent if it has one.
    def makeComponentAbsolute(mode, obj):
        if obj in mode.childObjects:
            obj.parentObject.childObjects.remove(obj)    
            mode.objects.append(obj)
            mode.childObjects.remove(obj)
        obj.static = False

    # checks for collisions between potential children.
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

    # checks if the children are all in the same row.
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

    # align helper functions
    # helps align objects
    def alignSelectedObjects(mode, align):
        toAlignPositions = []
        newPosition = None # x coord or y coord, depending on which align was selected
        move = ("align", [], [], []) # move, objects, initialCoords, finalCoords
        for obj in mode.selectedObjs:
            move[1].append(obj)
            move[2].append((obj.x, obj.y))
            if type(obj) == Img:
                objX, objY = mode.getCoordsOfImg(obj)
            else:
                objX, objY = obj.x, obj.y
            if align == 0: 
                toAlignPositions.append(objX)
                newPosition = min(toAlignPositions)
            elif align == 1:
                toAlignPositions.append(objX + obj.width/2)
                newPosition = sum(toAlignPositions)/len(toAlignPositions)
            elif align == 2:
                toAlignPositions.append(objX + obj.width)
                newPosition = max(toAlignPositions)
            elif align == 3:
                toAlignPositions.append(objY)
                newPosition = min(toAlignPositions)
            elif align == 4:
                toAlignPositions.append(objY + obj.height/2)
                newPosition = sum(toAlignPositions)/len(toAlignPositions)
            else:
                toAlignPositions.append(objY + obj.height)
                newPosition = max(toAlignPositions)
            if align < 3:
                move[3].append((newPosition, objY))
            else:
                move[3].append((objX, newPosition))

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

    # finds button from align bar and performs the button's function accordingly.
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

    # export helper functions
    # learned how to use pickle for saveCanvas and importCanvas from:
    # https://www.thoughtco.com/using-pickle-to-save-objects-2813661
    # learned filedialog from:
    # https://runestone.academy/runestone/books/published/thinkcspy/GUIandEventDrivenProgramming/02_standard_dialog_boxes.html
    # saves canvas to a file (which can be rather big)
    def saveCanvas(mode):
        filePath = filedialog.asksaveasfilename(initialdir=os.getcwd(),
                                      title="Save canvas as:",
                                      filetypes=[("Object", "obj")])
        if filePath != None and filePath != "":
            f = open(filePath, "wb")
            pickle.dump(mode.objects, f)

    # imports the a previous canvas (.obj filetype)
    def importCanvas(mode):
        filePath = filedialog.askopenfilename(initialdir=os.getcwd(),
                                title="Import canvas from:",
                                      filetypes=[("Object", "obj")])
        if os.path.isfile(filePath):
            f = open(filePath, "rb")
            mode.objects = pickle.load(f)
            mode.selectedObjs = []

    # exports canvas by calling upon the exporter.
    def exportCanvas(mode):
        fileName = mode.getUserInput("Name of Site?")
        if fileName != None:
            mode.convertToCSS()
            exportToHTML(fileName, mode.objects)
            exportToCSS(mode.bgColor, CSSClass.classes)

    # converts to css
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

    # recursively converts a parent's children to css.
    def convertChildrenToCSS(mode, obj):
        if type(obj) != Div or obj.childObjects == []:
            if obj.static:
                mode.convertToCSSStatic(obj)
            else:
                mode.convertToCSSAbsolute(obj)
        else:
            for child in obj.childObjects:
                mode.convertChildrenToCSS(child)

    # gets the margins for a child object when converting to CSS.
    def getMargins(mode, obj):
        if obj.parentObject == None:
            if type(obj) == Img:
                objX, objY = mode.getCoordsOfImg(obj)
                return (objX-mode.toolBarMargin, objY-mode.alignBarMargin)
            else:
                return (obj.x-mode.toolBarMargin, obj.y-mode.alignBarMargin)
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
    
    # converts an object to css with static positioning
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

    # converts an object to css with absolute positioning
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

    # text helper methods
    # checks text buttons and changes properties accordingly
    def handleTextButtonPress(mode, functionName):
        if functionName == "fontFamily":
            mode.updateFontFamily()
        elif functionName == "fontSize":
            mode.updateFontSize()
        elif functionName == "editText":
            newText = mode.getUserInput("New text?")
            if type(newText) == str:
                mode.moves.append(("change text", mode.selectedObjs[0], (mode.selectedObjs[0].content, newText)))
                mode.selectedObjs[0].content = newText
                mode.selectedObjs[0].height = (newText.count("\n")+1)* mode.selectedObjs[0].font_size/2
                mode.selectedObjs[0].width = len(newText) * mode.selectedObjs[0].font_size

    # updates selected text based on the current selections.
    def updateSelected(mode):
        for obj in mode.selectedObjs:
            obj.font_family = mode.curFont
            obj.font_size = mode.curFontSize
            obj.height = mode.curFontSize * (obj.content.count("\n")+1)
            obj.width = mode.curFontSize / 2 * len(obj.content)
        mode.setTextButtonsInfo()

    # asks new font, and changes it. also changes font of all selected objects
    def updateFontFamily(mode):
        newFont = mode.getUserInput("What should the new font be?")
        if newFont.lower() in mode.tkinterFonts:
            move = ("change font", [], (mode.curFont, newFont))
            for obj in mode.selectedObjs:
                move[1].append(obj)
            mode.moves.append(move)
            mode.curFont = newFont
        else:
            mode.displayError("Font not available")
        mode.updateSelected()

    # asks new font size, and changes it. also changes font of all selected objects
    def updateFontSize(mode):
        newFontSize = mode.getUserInput("What should the new font size be?")
        if newFontSize.isdigit() and int(newFontSize) > 0:
            move = ("change font size", [], (mode.curFontSize, int(newFontSize)))
            for obj in mode.selectedObjs:
                move[1].append(obj)
            mode.moves.append(move)
            mode.curFontSize = int(newFontSize)
        else:
            mode.displayError("Not a valid font size")
        mode.updateSelected()

    # misc
    # learned to use messageboxfrom:
    # https://runestone.academy/runestone/books/published/thinkcspy/GUIandEventDrivenProgramming/02_standard_dialog_boxes.html
    # displays an error
    def displayError(mode, message):
        messagebox.showerror("Error", message)


######################################################
# Views
######################################################
    # draws a div; also draws children if they are not divs
    def drawDiv(mode, canvas, div):
        if type(div) == Div and div.childObjects == []:
            canvas.create_rectangle(div.x, div.y, div.x + div.width, div.y + div.height, fill=div.color)
        elif type(div) != Div:
            mode.drawComponent(canvas, div)
        else:
            canvas.create_rectangle(div.x, div.y, div.x + div.width, div.y + div.height, fill=div.color)
            for obj in div.childObjects:
                mode.drawDiv(canvas, obj)

    # draws objects on the canvas
    def drawObjects(mode, canvas):
        for o in mode.objects:
            mode.drawComponent(canvas, o)
        if mode.curDiv != None:
            canvas.create_rectangle(mode.curDiv.x, mode.curDiv.y, 
                        mode.curDiv.x + mode.curDiv.width, mode.curDiv.y + mode.curDiv.height, 
                        fill=mode.curDiv.color)

    # draws a component based on the type of object
    def drawComponent(mode, canvas, o):
        if isinstance(o, Div):
            mode.drawDiv(canvas, o)
        elif isinstance(o, Text):
            canvas.create_text(o.x, o.y, text=o.content, fill=o.color, anchor="nw", font=f"{o.font_family} {o.font_size}")
        elif isinstance(o, Img):
            canvas.create_image(o.x, o.y, image=ImageTk.PhotoImage(o.image))

    # draws the toolbar
    def drawToolbar(mode, canvas):
        canvas.create_rectangle(0, 0, mode.toolBarMargin, mode.height, fill="gray", width=0)
        canvas.create_rectangle(1, 10, mode.toolBarMargin, 40, fill=mode.curColor)
        for button in mode.toolsBar:
            if type(button.functionName) == str and button.functionName.startswith("moveLayer"):
                if len(mode.selectedObjs) == 1:    
                    mode.drawButton(canvas, button)
            else:
                mode.drawButton(canvas, button)

    # draws a button
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

    # draws a text button
    def drawTextButton(mode, canvas, button):
        canvas.create_rectangle(button.x, button.y, button.x+button.width, button.y+button.height-button.textSize, fill=button.fill)
        canvas.create_text(button.x+button.width/2, button.y, text=button.label1, anchor="n", fill=button.textColor)
        canvas.create_text(button.x+button.width/2, button.y+button.height, text=button.label, anchor="s", fill=button.textColor)

    # draws the align toolbar
    def drawAlignBar(mode, canvas):
        canvas.create_rectangle(mode.toolBarMargin, 0, mode.width, 50, fill="grey", width=0)
        for button in mode.alignBarButtons:
            mode.drawButton(canvas, button)
        if mode.curTool == 2 or (mode.curTool == 0 and mode.selectedHasText()):
            mode.drawTextTools(canvas)
    
    # draws text tools
    def drawTextTools(mode, canvas):
        for button in mode.textToolButtons:
            if button.functionName == "editText":
                if mode.curTool == 0 and len(mode.selectedObjs) == 1 and mode.selectedHasText():
                    mode.drawTextButton(canvas, button)
            else:
                mode.drawTextButton(canvas, button)

    #draws box around selected objects
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

    # draws background color
    def drawBackground(mode, canvas):
        if mode.bgColor != None:
            canvas.create_rectangle(0, 0, mode.width, mode.height, fill=mode.bgColor)
    
    # draws icon on cursor
    def drawCursor(mode, canvas):
        if mode.curTool != 0:
            canvas.create_image(mode.mouseX, mode.mouseY, image=ImageTk.PhotoImage(mode.toolIcons[mode.curTool]))

    # handles all drawing
    def redrawAll(mode, canvas):
        mode.drawBackground(canvas)
        mode.drawObjects(canvas)
        mode.drawHighlight(canvas)
        mode.drawAlignBar(canvas)
        mode.drawToolbar(canvas)
        mode.drawCursor(canvas)
        canvas.create_text(mode.width/2, 60, text=f"shift on?: {mode.shiftHeld}")

# modalApp built with reference to section 7 of these course notes:
# https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
# gathers all screens together
class MyModalApp(ModalApp):
    def appStarted(app):
        app.splashScreenMode = SplashScreenMode()
        app.editorMode = EditorMode()
        app.helpMode = HelpMode()
        app.setActiveMode(app.splashScreenMode)

if __name__ == "__main__":
    newApp = MyModalApp(width=1440, height=900)