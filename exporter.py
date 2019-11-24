import os
from classes import *

def exportToHTML(fileName, listOfObjects):
    cleanFiles()
    os.mkdir("export")
    html = open(f"export/{fileName}.html", "w")
    initialHTML = getInitialHTML(fileName)
    html.write(initialHTML)
    for obj in listOfObjects:
        if isinstance(obj, Div):
            newDiv = f'<div class={obj.cssClass}></div>'
            html.write(newDiv)
    finalHTML = getFinalHTML()
    html.write(finalHTML)
    html.close()

def exportToCSS(backgroundColor, dictOfClasses):
    css = open("export/style.css", "w")
    bgColor = "body { background-color: " + backgroundColor + "}"
    css.write(bgColor)
    for cssClass in dictOfClasses:
        cssCode = getCSSDivCode(cssClass, dictOfClasses[cssClass])
        css.write(cssCode)
    css.close()

def getCSSDivCode(cssClass, cssClassName):
    cssCode = f'.{cssClassName} {{\n'
    cssCode += '\tposition: absolute;\n'
    for prop in cssClass.__dict__:
        value = cssClass.__dict__[prop]
        if prop == "color":
            cssCode += f'\tbackground-color: {value};\n'
        elif type(value) == int:
            cssCode += f'\t{prop}: {value}px;\n'
        elif value != None:
            cssCode += f'\t{prop}: {value};\n'
    cssCode += '}'
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