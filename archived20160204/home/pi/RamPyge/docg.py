import os, re

"""
HTML DOCUMENTATION GENERATOR
========= 14/07/15 =========
SRT

Run this script to turn the marked comments (###) in the modules
into nice formatted HTML documentation!
The generated documentation is stored in the docs folder.
The docs folder will be created if it does not exist, so feel free to
delete it if you want a clean set. This is necessary if you remove or
refactor modules.

When writing the comments, use html tags within them to format
the end result. The important (and supported) places to put comments
are before your class definitions, and before each method definition.
Write a detailed description of what your function does, then, using
a new line for each, list your parameters and their purposes, in this format:
### paramname -> description of purpose (type)
Follow these with a line for your return value if one exists, like this:
### returns => description of return value (type)

Following this format when writing your own functions and modules will
make your code easy to read, and save you time in making documentation later!

"""

xf = None

def findScripts(dirName):
    #Create index page
    global xf
    if not os.path.exists("docs/"):
        os.makedirs("docs")
    xf = open("docs/index.html", 'w')
    writeline(xf, "<html>")
    writeline(xf, "<head><title>RamPyge Documentation</title></head>")
    writeline(xf, "<body>")
    writeline(xf, "<h1>RamPyging Chariots</h1><hr />")
    writeline(xf, "<h3>Getting Started</h3>")
    guide = """<p>Before you can run a script using RamPyge, you need to provide the
            right conditions on the pi.</p>
            <p>You will need: <ul>
            <li><a href='http://abelectronics.co.uk/i2c-raspbian-wheezy/info.aspx'>i2c-tools</a></li>
            <li><a href='http://abelectronics.co.uk/i2c-raspbian-wheezy/info.aspx'>To unblacklist loading of i2c-dev at boot.</a></li>
            <li><a href='http://abelectronics.co.uk/i2c-raspbian-wheezy/info.aspx'>python-smbus</a></li>
            </ul></p>
            <p>When you start out, try running Main.py. This is where you
            should experiment with the commands that are carried out when the
            chariot is in autonomous mode. </p>
            """
    writeline(xf, guide)
    writeline(xf, "<h3>Reference</h3>")
    writeline(xf, "<ul>")
    
    for dirName, subdirList, fileList in os.walk("{}/{}".format(os.getcwd(),dirName)):
        for fname in fileList:
            if fname.endswith('.py') and not '__init__' in fname and not 'docg' in fname:
                makedoc(dirName, fname)

def writeline(file, content):
    file.write("{}\n".format(content))

def makedoc(dirName, filename):
    global xf
    fn = re.search('\w+(?=.py)', filename).group(0)
    d = re.search('((?<=RamPyge/)((/)?\w+)+)',dirName)
    if d is None:
        d = ""
    else:
        d = d.group(0) + '/'

    if not os.path.exists("docs/{}/".format(d)):
        os.makedirs("docs/{}/".format(d))
        
    df = open("docs/{}/{}.html".format(d,fn), 'w')
    dl= " rampyge.{}".format(".".join(d.split('/')))

    commentbuffer = ""
    rvbuffer = ""
    argbuffer = []

    writeline(df, "<html>")
    writeline(df, "<head><title>{} Class</title></head>".format(filename))
    writeline(df, "<body>")

    with open("{}{}.py".format(d,fn)) as s:
        for i, line in enumerate(s.readlines()):
            if '###' in line:
                if '->' not in line:
                    if '=>' not in line:
                        try:
                            if not line.endswith('\s'):
                                line += '\s'
                            commentbuffer += (re.search('(?<=### ).*',line).group(0))
                        except:
                            pass
                    else:
                        rvbuffer = re.search('(?<=\=\> ).*',line).group(0)
                else:
                    argbuffer.append(re.search('(?<=### ).*',line).group(0))


            else:
                result = re.search('(?<=class ).+(?=:)', line)
                if result is not None:
                    writeline(df, "<h1 style='display:inline'>{}</h1>".format(result.group(0)))
                    writeline(df, "<h3 style='display:inline'>{}{}</h3>".format(dl,fn))
                    writeline(df, "<hr />")
                    writeline(df, commentbuffer)
                    commentbuffer = ""
                    writeline(df, "<br /><br />")
                    writeline(df, "<h2>Methods</h2>")
                    writeline(df, "<hr />")

                result = re.search('(?<=def )\w+(?=\()',line)
                if result is not None:
                    writeline(df, "<h3>{}".format(result.group(0)))
                    result = re.search('\(.*\)',line)
                    result = re.sub("(self, )|(self)","",result.group(0))
                    writeline(df, "<span style='font-size:80%'>{}</span></h3>".format(result))
                    writeline(df, "<p>{}</p>".format(commentbuffer))
                    commentbuffer = ""
                    if argbuffer != []:
                        for arg in argbuffer:
                            writeline(df, "{}<br />".format(arg))
                    argbuffer = []
                    if rvbuffer != "":
                        writeline(df, "<b>Return value:</b>{}".format(rvbuffer))
                        rvbuffer = ""
                        writeline(df, "<br />")
                    writeline(df, "<br/>")
                    

    writeline(df, "</body>")
    writeline(df, "</html>")

    df.close()

    #Create a hyperlink to the new file in the index
    writeline(xf, "<li><a href='{}{}.html'>{}{}</a></li>".format(d,fn,dl,fn))
    
    print "{} - Done.".format(filename)

if __name__ == '__main__':
        findScripts("")
        writeline(xf, "</ul>")
        writeline(xf, "</body>")
        writeline(xf, "</html>")
        xf.close()
        

