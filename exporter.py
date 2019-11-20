def exportToHTML(fileName, listOfObjects):
    html = open(f"{fileName}.html")
    for obj in listOfObjects:
        html.write(f"{type(obj)} located at {obj.x}, {obj.y}")
    html.close()

def exportToCSS(fileName, listOfObjects):
    pass

def exportObjects(fileName, listOfObjects):
    pass