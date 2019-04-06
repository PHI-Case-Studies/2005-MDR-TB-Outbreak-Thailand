from IPython.display import HTML, IFrame

import warnings

def style_notebook():
    style = open("./resources/style.css", "r").read()
    return HTML(style)

def show_video(url):
    return HTML('<iframe src="'+url+'?title=0&byline=0&portrait=0" width="700" height="394" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>')

def show_pdf(url,width,height):
    return HTML("<object data='"+url+"' width="+str(width)+" height="+str(height)+"></object>")

def play_mp3(file):
    return HTML('<audio src="'+file+'" controls><p>If you are reading this, it is because your browser does not support the audio element</p></audio>')

warnings.filterwarnings('ignore')