############################################################
# exporter.py
# exports the python objects into HTML and CSS with a lot
# of file i/o and string manipulation.
############################################################
import os
from classes import *
from PIL import Image

# deletes any existing export and rewrites HTML, getting line by line
# via the list of objects.
def exportToHTML(fileName, listOfObjects):
    cleanFiles()
    os.mkdir("export")
    html = ""
    initialHTML = getInitialHTML(fileName)
    html += initialHTML + '\n'
    for obj in listOfObjects:
        if type(obj) == Div and obj.childObjects != []:
            html += '\t' + getPartialHTMLLine(obj)
            html += exportChildHTML(obj)
        else:
            html += getHTMLLine(obj)
            
    html += getFinalHTML()
    html = closeTags(html)
    f = open("export/index.html", "w")
    f.write(html)
    f.close()

# for a parent tag, recursively adds child tags.
def exportChildHTML(obj, level=1):
    if type(obj) != Div or obj.childObjects == []:
        newHTML = getPartialHTMLLine(obj)
        return '\t'*level+newHTML
    else:
        html = ""
        for child in obj.childObjects:
            html += exportChildHTML(child, level+1)
        return html

# closes all unclosed divs.
def closeTags(html):
    newHTML = ""
    prevNumTabs = 0
    yetToClose = []
    for l in html.splitlines():
        numTabs = l.count("\t")
        line = l.strip()
        tag = line[1:(line.find(' '))]
        if numTabs > prevNumTabs and l.count('<') > 0 and l.count('/') == 0:
            yetToClose.append((tag, numTabs))
        if numTabs < prevNumTabs:
            while(len(yetToClose) > 0):
                tagToClose = yetToClose.pop()
                newHTML += '\t'*tagToClose[1] + '</' + tagToClose[0] + '>\n'
        newHTML += l + '\n'
        prevNumTabs = numTabs
    return newHTML

# returns a partial HTMl line for parents and children.
def getPartialHTMLLine(obj):
    if isinstance(obj, Div):
        newHTML = f'\t<div class={obj.cssClass}>\n'
    elif isinstance(obj, Text):
        newHTML = f'\t<span class={obj.cssClass}>{obj.content}</span>\n'
    elif isinstance(obj, Img):
        numImg = countImages() + 1
        imagePath = f'image{numImg}.{obj.imgFormat}'
        obj.image.save('export/' + imagePath)
        newHTML = f'\t<img class={obj.cssClass} src="{imagePath}"/>\n'
    return newHTML

# returns a regular HTML line.
def getHTMLLine(obj):
    if isinstance(obj, Div):
        newDiv = f'\t\t<div class={obj.cssClass}></div>\n'
        return newDiv
    elif isinstance(obj, Text):
        newP = f'\t\t<span class={obj.cssClass}>{obj.content}</span>\n'
        return newP
    elif isinstance(obj, Img):
        numImg = countImages() + 1
        imagePath = f'image{numImg}.{obj.imgFormat}'
        obj.image.save('export/' + imagePath)
        newImg = f'\t\t<img class={obj.cssClass} src="{imagePath}"/>\n'
        return newImg

# counts the number of images in a directory so the images don't overwrite each other.
def countImages():
    numImages = 0
    if os.path.isdir('export'):
        for filename in os.listdir('export'):
            filename = filename.lower()
            if filename.endswith('jpg') or filename.endswith('png') or filename.endswith('jpeg'):
                numImages += 1
    return numImages

# converts the cssclasses into actual css
def exportToCSS(backgroundColor, dictOfClasses):
    css = open("export/style.css", "w")
    bgColor = "body {\n\tbackground-color: " + backgroundColor + ";\n}\n"
    initialSpan = "span {\n\tdisplay: inline-block;\n}\n"
    css.write(bgColor)
    css.write(initialSpan)
    for cssClass in dictOfClasses:
        cssCode = ""
        if cssClass.color != None and cssClass.height != None:
            # for divs
            cssCode = getCSSDivCode(cssClass, dictOfClasses[cssClass])
        elif cssClass.height == None:
            # for text
            cssCode = getCSSTextCode(cssClass, dictOfClasses[cssClass])
        else:
            # for imgs
            cssCode = getCSSImgCode(cssClass, dictOfClasses[cssClass])
        css.write(cssCode)
    css.close()

# returns css for divs based on its properties
def getCSSDivCode(cssClass, cssClassName):
    cssCode = f'\n.{cssClassName} {{\n'
    for prop in cssClass.__dict__:
        value = cssClass.__dict__[prop]
        if value != None:
            if prop == "color":
                cssCode += f'\tbackground-color: {value};\n'
            elif type(prop) == str and prop.startswith("margin"):
                newProp = '-'.join(prop.split('_'))
                cssCode += f'\t{newProp}: {int(value)}px;\n'
            elif type(value) == int or type(value) == float:
                cssCode += f'\t{prop}: {int(value)}px;\n'
            else:
                cssCode += f'\t{prop}: {value};\n'
    cssCode += '\tdisplay:flex\n}\n'
    return cssCode

# returns css for spans based on its properties
def getCSSTextCode(cssClass, cssClassName):
    cssCode = f'\n.{cssClassName} {{\n'
    for prop in cssClass.__dict__:
        value = cssClass.__dict__[prop]
        if value != None:
            if prop == "color":
                cssCode += f'\tcolor: {value};\n'
            elif type(prop) == str and prop.startswith("margin"):
                newProp = '-'.join(prop.split('_'))
                cssCode += f'\t{newProp}: {int(value)}px;\n'
            elif type(prop) == str and prop.startswith("font"):
                newProp = '-'.join(prop.split('_'))
                if newProp.endswith('size'):
                    cssCode += f'\t{newProp}: {value}px;\n'
                else:
                    cssCode += f'\t{newProp}: {value};\n'
            elif type(value) == int or type(value) == float:
                cssCode += f'\t{prop}: {int(value)}px;\n'
            else:
                cssCode += f'\t{prop}: {value};\n'
    cssCode += '}\n'
    return cssCode

# returns css for img based on its properties
def getCSSImgCode(cssClass, cssClassName):
    cssCode = f'\n.{cssClassName} {{\n'
    for prop in cssClass.__dict__:
        value = cssClass.__dict__[prop]
        if value != None:
            if type(prop) == str and prop.startswith("margin"):
                newProp = '-'.join(prop.split('_'))
                cssCode += f'\t{newProp}: {int(value)}px;\n'
            elif type(value) == int or type(value) == float:
                cssCode += f'\t{prop}: {int(value)}px;\n'
            else:
                cssCode += f'\t{prop}: {value};\n'
    cssCode += '}\n'
    return cssCode

# initial html code that most html documents will have.
def getInitialHTML(fileName):
    initialHTML = f'''
<!DOCTYPE html>
<html>
    <link rel="stylesheet" type="text/css" href="style.css"/>
    <head>
        <title>{fileName}</title>
    </head>
    <body>
'''
    return initialHTML

# removes the export folder.
def cleanFiles():
    if os.path.isdir('export'):
        for filename in os.listdir('export'):
            if os.path.isfile('export/' + filename):
                os.remove('export/' + filename)
        os.rmdir('export')

# returns the final HTML.
def getFinalHTML():
    finalHTML = '''
    </body>
</html>
'''
    return finalHTML