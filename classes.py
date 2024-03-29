############################################################
# classes.py 
# has the classes that the project utilizes, such as HTML/CSS elements,
# or elements that makes the project easier to manage, like buttons.
############################################################

# equivalent to a div in HTML, is essentially a rectangle
class Div(object):
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.cssClass = None
        self.childObjects = []
        self.static = False
        self.parentObject = None

# equivalent to span in HTML
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
        self.static = False
        self.parentObject = None

# equivalent to img in HTML
class Img(object):
    def __init__(self, x, y, scalingFactor, image, fullSize):
        self.x = x
        self.y = y
        self.scalingFactor = scalingFactor
        width, height = image.size
        self.height = height
        self.width = width
        self.image = image
        self.fullSize = fullSize
        self.static = False
        self.parentObject = None
        self.imgFormat = image.format

# keeps a list of classes so one isn't made more than once.
class CSSClass(object):
    pastClasses = set()
    classes = dict()
    def __init__(self, color=None, height=None, width=None, left=None, top=None, 
                        font_family=None, font_size=None, position="absolute", margin_left=None, margin_top=None):
        self.color = color
        self.height = height
        self.width = width
        self.left = left
        self.top = top
        self.font_family = font_family
        self.font_size = font_size
        self.position = position
        self.margin_left = margin_left
        self.margin_top = margin_top
        # self.display = "flex"
        if self not in CSSClass.pastClasses:
            CSSClass.pastClasses.add(self)
            newVal = "class" + str(len(CSSClass.classes))
            CSSClass.classes[self] = newVal
    # so that classes can be hashed
    def getImportantAttributes(self):
        return (self.color, self.height, self.width, self.left, self.top, self.margin_left, self.margin_top,)

    def __eq__(self, other):
        return (isinstance(other, CSSClass) and 
                self.getImportantAttributes() == other.getImportantAttributes())

    def __hash__(self):
        return hash(self.getImportantAttributes())

# makes life easier when drawing buttons and detecting its hitbox in main.py
class Button(object):
    def __init__(self, x, y, width, height, image, label, functionName, fill="white", textColor="black"):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.image = image
        self.label = label
        self.functionName = functionName
        self.fill = fill
        self.textColor = textColor
        self.fontSize = 20
    
    # checks if the button is hit
    def didHitButton(self, x, y):
        if ((x < self.x + self.width and x > self.x) and
            (y < self.y + self.height and y > self.y)):
            return True
        else:
            return False

# has two labels so it displays text within the buton
class TextButton(Button):
    def __init__(self, x, y, width, height, label1, label2, functionName, textSize=14, fill="white", textColor="black"):
        super().__init__(x, y, width, height, None, label2, functionName, fill, textColor)
        self.label1 = label1
        self.textSize = textSize

# color palette with no label
class ColorPalette(Button):
    def __init__(self, x, y, width, height, label, functionName, fill="white"):
        super().__init__(x, y, width, height, None, label, functionName, fill)