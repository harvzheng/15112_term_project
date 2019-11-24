class Div(object):
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.cssClass = None

class Text(object):
    def __init__(self, x, y, width, height, content, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.content = content
        self.color = color

class Img(object):
    def __init__(self, x, y, scalingFactor, image):
        self.x = x
        self.y = y
        self.scalingFactor = scalingFactor
        height, width = image.size
        self.height = height * self.scalingFactor
        self.width = width * self.scalingFactor
        self.image = image

class CSSClass(object):
    pastClasses = set()
    classes = dict()
    def __init__(self, color, height, width, left=None, top=None):
        self.color = color
        self.height = height
        self.width = width
        self.left = left
        self.top = top
        if self not in CSSClass.pastClasses:
            CSSClass.pastClasses.add(self)
            newVal = "class" + str(len(CSSClass.classes))
            CSSClass.classes[self] = newVal

    def getImportantAttributes(self):
        return (self.color, self.height, self.width, self.left, self.top)

    def __eq__(self, other):
        return (isinstance(other, CSSClass) and 
                self.getImportantAttributes() == other.getImportantAttributes())

    def __hash__(self):
        return hash(self.getImportantAttributes())