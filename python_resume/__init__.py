#!/usr/bin/env python
import logging
import jinja2
import os
import sys
import argparse
import subprocess
import datetime
import locale
import json
import locale
import datetime
import secretary

#from info import *

#def get_default_template_str(name, fmt):
#    with open(os.path.join(TEMPLATE_DIR, name+'.'+fmt), 'r') as f:
#        return f.read()

def filter_json(j, versions):
    #print "filer_json:",versions
    versions_set = set(versions)

    def test(x):
        if isinstance(x, dict):
            if x.has_key('version'):
                vs = set(x['version'])
                #print "comparing", vs, versions_set
                if not vs.issubset(versions_set):
                    return False
        return True
    
    for k,v in j.items():
        #print " ",k,v
        if isinstance(v, list):

            c_old = len(v)

            #setattr(j, k, list(x for x in v if test(x)))
            j[k] = list(x for x in v if test(x))

            c_new = len(v)

            if c_old != c_new:
                #print "  removed {} elements".format(c_old-c_new)
                pass

            for l in v:
                if isinstance(l, dict):
                    filter_json(l, versions)
        
        elif isinstance(v, dict):
            filter_json(v, versions)

class Class:
    """
    convert json dict to python class
    """
    def __init__(self, name, j):
        if not isinstance(j, dict):
            raise ValueError('must be dict')

        self.name = name

        if name == '_selector':
            self.j = j
        else:
            for k,v in j.items():
                setattr(self, k, Class.value_or_class(k,v))

    def filt(self, versions, sel_id):
        #print "Class.filt", versions
        versions_set = set(versions)

        def test(x):
            if not isinstance(x, Class):
                return True
                
            if hasattr(x, 'version'):
                vs = set(x.version)
                #print "comparing", vs, versions_set
                if not vs.issubset(versions_set):
                    return False

            if hasattr(x, '_selector'):
                #print "has _selector"
                #print x._selector.j
                try:
                    o = x._selector.j[str(sel_id)]
                except:
                    pass
                else:
                    #print "_selector[{}] = {}".format(sel_id, o)
                    if not o:
                        return False

            return True
        
        for k,v in self.__dict__.items():
            #print " ",k,v
            if isinstance(v, list):
                setattr(self, k, list(x for x in v if test(x)))

                for l in v:
                    if isinstance(l, Class):
                        l.filt(versions, sel_id)
            
            elif isinstance(v, Class):
                v.filt(versions, sel_id)
                

    @staticmethod
    def value_or_class(k,v):
        if isinstance(v, dict):
            return Class(k,v)
        elif isinstance(v, list):
            return list(Class.value_or_class('',l) for l in v)
        else:
            if k.startswith("date_"):
                locale.setlocale(locale.LC_ALL, 'en_US.utf8')
                return datetime.datetime.strptime(v, "%x")
            else:
                return v



def clean(s):
    if s is None:
        return None
    else:
        s = s.replace(' ','_')
        s = s.lower()
        return s

def get_element_by_version(e, t, versions):
    logging.debug("get_element_by_version")
    logging.debug(versions)

    for v in versions:
        for child in e.iter(t):
            if not 'version' in child.attrib:
                return child
        
            if child.attrib['version'] == v:
                return child

    logging.debug(None)

    return None

def findall_by_version(e, t, versions):

    for child in e.iter(t):
        
        if not 'version' in child.attrib:
            yield child
            continue
        
        for v in versions:
            if child.attrib['version'] == v:
                yield child
 

def render_string(filename, context):
    """
    using jinja2, double render template at filename+'.in' with context and return output
    """
    
    with open(filename + ".in") as f:
        return render_string_2(f.read(), context)
   
def render_string_2(temp, context):

    output = temp.render(context)

    temp = jinja2.Template(output)
    
    output = temp.render(context)

    return output

class Generator:
    def __init__(
            self,
            #path_to_data,
            #output_dir = '',
            version = None,
            company = None,
            position = None,
            #overwrite = False,
            order = []):
        
        

        #self.path_to_data = path_to_data
        #self.output_dir = output_dir
        self.version = version
        self.company = company
        self.position = position
        #self.overwrite = overwrite
        self.order = order

        self.loader = Loader()
        self.env = jinja2.Environment(loader=self.loader)

        self.output_dir = "output"

    def get_template(self, name):
        return self.env.get_template(name)

    def get_dir(self):
        if self.company is None:
            return os.path.join("_".join(self.version))
        else:
            return os.path.join(
                    clean(self.company),
                    clean(self.position),
                    "_".join(self.version))

    def get_dir_out(self):
        return os.path.join(self.output_dir, self.get_dir())

    def get_dir_in(self):
        return os.path.join('input', self.get_dir())


    def filt(self, versions, sel_id):
        """
        remove json objects based on versions and selector values
        """
        self.info.filt(versions, sel_id)

    def render_string(self, template_name, context):
        temp = self.get_template(template_name)

        ret = render_string_2(temp, context)

        #print "RESULT"
        #print ret

        return ret

    def render_string_part(self, c):
        
        context = {
                'position': self.position,
                'company': self.company,
                'info':    self.info,
                'version': self.version,
                #'args':  self.args,
                }
       
        if c == 'a':
            return self.render_string("education.html", context)
        elif c == 'b':
            return self.render_string("employment.html", context)
        elif c == 'c':
            return self.render_string("skills.html", context)
        elif c == 'd':
            return self.render_string("projects.html", context)
        else:
            raise ValueError("Invalid part code: {}".format(c))

    def get_filename_out(self, pre, post):
        if self.company:
            return "{}_{}_{}{}".format(pre, clean(self.company), clean(self.position), post)
        else:
            return "{}{}".format(pre, post)

    def get_path_out(self, pre, post):
        return os.path.join(
                self.get_dir_out(),
                self.get_filename_out(pre, post))

    def render_odt(self):

        engine = secretary.Renderer()
        result = engine.render("templates/resume.odt",
                info=self.info,
                version=self.version,
                #args=self.args
                )
        
        po = self.get_path_out('resume', '.odt')

        with open(po,'wb') as f:
            f.write(result)


    def render_text(self, temp=None, name=None, fmt=None):
        if temp is None:
            temp = self.get_template(name+fmt)
        
        return self.render_text_2(temp)
        
    def render_text_2(self, template):
        """
        for text files only
        render parts to variables, then render together, then return
        """
        
        parts = []
        for c in self.order:
            #print "part",c
            parts.append(self.render_string_part(c))
        
        context = {
                'company':  self.company,
                'position': self.position,
                'version':  self.version,
                'parts':    parts,
                'info':     self.user.info,
                #'args':  self.args,
                }

        obj = self.render_string("objective.html", context) 
  
        output = render_string_2(template, context)

        return output

    def render(self, pre, post):
        """
        for text files only
        render parts to variables, then render pre+post+'.in'
        """
   

        temp = self.get_template(pre+post)

        output = self.render_text_2(temp)
    
        fo = self.get_path_out(pre, post)
       
        try:
            os.makedirs(os.path.dirname(fo))
        except:
            pass

        with open(fo,"w") as f:
            f.write(output)

    def render_pdf(self):
        """
        convert previously rendered html to pdf using linux tool 'wkhtmltopdf'
        """

        for s in ["resume", "cover_letter", ]:

            cmd = [
                    'wkhtmltopdf',
                    '-q',
                    self.get_path_out(s, ".html"),
                    self.get_path_out(s, ".pdf")
                    ]
    
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    
            output = p.communicate()

    def render_html(self):
        for s in ["resume", "cover_letter", ]:
            self.render(s, ".html")


    def write(self):
        out_dir = self.get_dir_out()

        try:
            os.makedirs(out_dir)
        except OSError:
            if self.overwrite:
                self.dowrite(out_dir)
            else:
                print "{} already exists. use -f to overwrite.".format(repr(out_dir))
        else:

            self.dowrite(out_dir)

class Loader(jinja2.BaseLoader):
    def __init__(self):#, path):
        #self.path = path
        self.path = '/usr/local/python_resume/templates'

        self.stored_templates = {}

    def store_template(self, template, s):
        self.stored_templates['template'] = s

    def get_source(self, environment, template):
       
        #print "looking for template",template

        # look for stored template
        try:
            source = self.stored_templates['template']
        except:
            pass
        else:
            source = source.decode('uft-8')
            return source, '', True
        
        
        # look for default file
        path = os.path.join(self.path, template)
        if not os.path.exists(path):
            raise jinja2.TemplateNotFound(template)
        
        mtime = os.path.getmtime(path)
        with file(path) as f:
            source = f.read().decode('utf-8')
        
        return source, path, lambda: mtime == os.path.getmtime(path)




