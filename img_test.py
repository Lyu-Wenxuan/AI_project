import image_utils
from stylize import Stylizer

# stylizer = Stylizer('models/style3.pt')
stylizer = Stylizer('models/mystyle1/step_25.pt')
image = image_utils.load('images/content/1.jpg')
stylized = stylizer.stylize(image)
image_utils.save(stylized, f'style_6.jpg')