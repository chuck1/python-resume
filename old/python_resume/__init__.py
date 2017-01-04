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

import python_resume.user

#from info import *

#def get_default_template_str(name, fmt):
#    with open(os.path.join(TEMPLATE_DIR, name+'.'+fmt), 'r') as f:
#        return f.read()



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
            versions = None,
            company = None,
            position = None,
            #overwrite = False,
            order = []):
        
        

        #self.path_to_data = path_to_data
        #self.output_dir = output_dir
        self.versions   = versions
        self.company    = company
        self.position   = position
        #self.overwrite = overwrite
        self.order = order

        if self.company is None:
            self.versions.append('nocompany')
        else:
            self.versions.append('company')

        self.loader = Loader()
        self.env = jinja2.Environment(loader=self.loader)

        self.output_dir = os.path.join(os.getcwd(), "output")

    def get_template(self, name):
        return self.env.get_template(name)

    def get_dir(self):
        if self.company is None:
            return os.path.join("_".join(self.versions))
        else:
            return os.path.join(
                    clean(self.company),
                    clean(self.position),
                    "_".join(self.versions))
    
    def get_dir_out(self):
        return os.path.join(self.output_dir, self.get_dir())

    def get_dir_in(self):
        return os.path.join('input', self.get_dir())

    def get_filename_out(self, pre, post):
        if self.company:
            return "{}{}".format(
                    "_".join([pre, clean(self.company), clean(self.position)]+self.versions),
                    post)
        else:
            return "{}{}".format(
                    "_".join([pre]+self.versions),
                    post)

    def get_path_out(self, pre, post):
        return os.path.join(
                self.get_dir_out(),
                self.get_filename_out(pre, post))

    def filt(self, sel_id=None):
        """
        remove json objects based on versions and selector values
        """
        self.user.info.filt(self.versions, sel_id)

    def render_string(self, template_name, context):
        temp = self.get_template(template_name)

        ret = render_string_2(temp, context)

        #print "RESULT"
        #print ret

        return ret

    def render_string_part(self, c):
        
        context = self.get_context()
       
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


    def get_context(self):
        d = {
                'company':  self.company,
                'position': self.position,
                'version':  self.versions,
                'info':     self.user.info,
                }
        return d

    def render_odt(self):

        engine = secretary.Renderer()
        result = engine.render("templates/resume.odt",
                version =   self.versions,
                info =      self.user.info,
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
                'version':  self.versions,
                'parts':    parts,
                'info':     self.user.info,
                #'args':  self.args,
                }

        obj = self.render_string("objective.html", context) 
  
        output = render_string_2(template, context)

        return output

    def render(self, filename):
        """
        for text files only
        render parts to variables, then render pre+post+'.in'
        """
   
        pre, post = os.path.splitext(filename)

        temp = self.get_template(pre+post)

        output = self.render_text_2(temp)
    
        fo = self.get_path_out(pre, post)
       
        try:
            os.makedirs(os.path.dirname(fo))
        except:
            pass

        with open(fo,"w") as f:
            f.write(output)

    def render_pdf(self, filename):
        """
        convert previously rendered html to pdf using linux tool 'wkhtmltopdf'
        """
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
        """
        
        h,t = os.path.splitext(filename)
        if t != '.html':
            raise ValueError()
        
        cmd = [
                'wkhtmltopdf',
                '-q',
                self.get_path_out(h,t),
                self.get_path_out(h,t+".pdf")
                ]
    
        print cmd

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




