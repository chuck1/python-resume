#!/usr/bin/env python
import logging
import jinja2
import os
import sys
import argparse
import xml.etree.ElementTree as ET
import subprocess
import datetime
import locale

from pyres.xml_tools import *

class Emp: pass
class Info2: pass
class Contact:
    def __init__(self):
        pass

    def load_xml(self, e, v):
        self.address = Address(e.find('address'))
        self.phone = e.find('phone').text
        self.email = e.find('email').text
        self.webpage = e.find('webpage').text

class Address:
    lines = []
    def __init__(self, e):
        for child in e:
            self.lines.append(child.text)
       
        self.line0 = self.lines[0]
        self.line1 = self.lines[1]

    def __str__(self):
        return "\n".join(l for l in self.lines)

class Objective:
    def __init__(self, e, v = None):
        item = get_element_by_version(e, "item", v)
        self.text = item.text

class Employment:
    def __init__(self, e, v = None):
        logging.debug(e.tag)
        
        self.title = e.find('title').text
        self.employer = e.find('employer').text
        self.location = e.find('location').text
        self.duration = e.find('duration').text

        d = e.find('desc')

        self.desc = list(e.text for e in findall_by_version(d, 'item', v))

        logging.debug(self.desc)

class Skills:
    lst = []
    table = []

    def __init__(self):
        pass
    def load_xml(self, e, v):
        #print "Skills"
        #print v

        l = e.find('list')
        if l is not None:
            for child in findall_by_version(l, 'item', v):
                self.lst.append(child.text)

        t = e.find('table')

        for child in findall_by_version(t, 'item', v):
            self.table.append(list(c.text for c in child.findall('col')))

class Course:
    def __init__(self, e, v):
        self.text = e.text

class Education:
    def __init__(self, e, v):
        
        self.degree     = e.find('degree').text
        self.major      = e.find('major').text
        self.focus      = e.find('focus').text

        self.element_honors = e.find('honors')
        if self.element_honors is not None:
            self.honors = self.element_honors.text

        self.school     = e.find('school').text
        self.location   = e.find('location').text

        print repr(e.find('start').text)
        print repr(e.find('end').text)

        locale.setlocale(locale.LC_ALL, '')

        self.start      = datetime.datetime.strptime(e.find('start').text, '%x')
        self.end        = datetime.datetime.strptime(e.find('end').text, '%x')

        self.start_str = self.start.strftime('%B %Y')
        self.end_str   = self.end.strftime('%B %Y')

        self.gpa        = e.find('gpa').text

        self.courses = []
        c = e.find('courses')
        if c is not None:
            for child in findall_by_version(c, 'item', v):
                self.courses.append(Course(child, v))

class Project:
    def __init__(self, e, v):
        self.text = e.find('text').text
        self.link = e.find('link').text


class Info:
    """
    
    """
    employment = []
    education = []
    projects = []

    def __init__(self):
        self.skills = Skills()
        pass
    def load_xml(self, e, v):
        self.name = get_element_by_version(e, 'name', v).text
        
        self.contact = Contact()
        self.contact.load_xml(e.find('contact'), v)

        self.objective = Objective(e.find('objective'), v)

        for child in e.find('education').findall('item'):
            self.education.append(Education(child, v))

        for child in e.find('employment').findall('item'):
            self.employment.append(Employment(child, v))

        self.skills.load_xml(e.find('skills'), v)
        
        for child in findall_by_version(e.find('projects'), 'item', v):
            self.projects.append(Project(child, v))





