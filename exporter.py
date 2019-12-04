import os
from classes import *
from PIL import Image

def exportToHTML(fileName, listOfObjects):
    cleanFiles()
    os.mkdir("export")
    html = open(f"export/index.html", "w")
    initialHTML = getInitialHTML(fileName)
    html.write(initialHTML)
    numImg = 0
    for obj in listOfObjects:
        if isinstance(obj, Div):
            newDiv = f'\t<div class={obj.cssClass}></div>\n'
            html.write(newDiv)
        elif isinstance(obj, Text):
            newSpan = f'\t<p class={obj.cssClass}>{obj.content}</p>\n'
            html.write(newSpan)
        elif isinstance(obj, Img):
            imagePath = f'image{numImg}.{obj.image.format}'
            obj.image.save('export/' + imagePath)
            newImg = f'\t<img class={obj.cssClass} src="{imagePath}"/>\n'
            html.write(newImg)
            numImg += 1
    finalHTML = getFinalHTML()
    html.write(finalHTML)
    html.close()

def exportToCSS(backgroundColor, dictOfClasses):
    css = open("export/style.css", "w")
    bgColor = "body {\n\tbackground-color: " + backgroundColor + ";\n}\n"
    initialP = "p {\n\tmargin: 0;\n}\n"
    css.write(bgColor)
    css.write(initialP)
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
            elif type(value) == int or type(value)= = float:
                cssCode += f'\t{prop}: {int(value)}px;\n'
            else:
                cssCode += f'\t{prop}: {value};\n'
    cssCode += '}\n'
    return cssCode

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

def getCSSImgCode(cssClass, cssClassName):
    cssCode = f'\n.{cssClassName} {{\n'
    for prop in cssClass.__dict__:
        value = cssClass.__dict__[prop]
        if value != None:
            if type(value) == int or type(value) == float:
                cssCode += f'\t{prop}: {int(value)}px;\n'
            elif type(prop) == str and prop.startswith("margin"):
                newProp = '-'.join(prop.split('_'))
                cssCode += f'\t{newProp}: {int(value)}px;\n'
            else:
                cssCode += f'\t{prop}: {value};\n'
    cssCode += '}\n'
    return cssCode

def getInitialHTML(fileName):
    initialHTML = f'''
<!DOCTYPE html>
<html>
    <link rel="stylesheet" type="text/css" href="style.css"/>
    <head>
        <title>{fileName}</title>
    <head>
    <body>
'''
    return initialHTML

def cleanFiles():
    if os.path.isdir('export'):
        for filename in os.listdir('export'):
            if os.path.isfile('export/' + filename):
                os.remove('export/' + filename)
        os.rmdir('export')

def getFinalHTML():
    finalHTML = '''
    </body>
</html>
'''
    return finalHTML