class Div(object):
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.cssClass = None

class Text(object):
    def __init__(self, x, y, width, height, content, color, font_family, font_size):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.content = content
        self.color = color
        self.font_family = font_family
        self.font_size = font_size

class Img(object):
    def __init__(self, x, y, scalingFactor, image):
        self.x = x
        self.y = y
        self.scalingFactor = scalingFactor
        width, height = image.size
        self.height = height
        self.width = width
        self.image = image

class CSSClass(object):
    pastClasses = set()
    classes = dict()
    def __init__(self, color=None, height=None, width=None, left=None, top=None, font_family=None, font_size=None):
        self.color = color
        self.height = height
        self.width = width
        self.left = left
        self.top = top
        self.font_family = font_family
        self.font_size = font_size
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

class Button(object):
    def __init__(self, x, y, height):
        self.x = x
        self.y = y
        self.height = height