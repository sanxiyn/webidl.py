import sys
import lxml.html

def idls_of_url(url):
    tree = lxml.html.parse(url)
    root = tree.getroot()
    idls = root.cssselect('pre.idl')
    for idl in idls:
        yield idl.text_content()

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print 'Usage: get_idls.py URL'
        sys.exit()
    url = args[0]
    for idl in idls_of_url(url):
        print idl
