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

    def print_text(self, indent=""):
        
        for k,v in self.__dict__.items():
            print indent+k
            if isinstance(v,list):
                for i in v:
                    if isinstance(i,Class):
                        i.print_text(indent+"  ")
                    else:
                        print indent+"  "+str(i)
            else:
                if isinstance(v,Class):
                    v.print_text(indent+"  ")
                else:
                    print indent+"  "+str(v)

    def filt(self, versions, sel_id=None):
        """
        remove irrelevant items from data
        """
        #print "Class.filt", versions
        versions_set = set(versions)

        def test(x):
            """
            return true is item should be kept
            """
            if not isinstance(x, Class):
                return True
                
            if hasattr(x, 'version'):
                vs = set(x.version)
                #print "comparing", vs, versions_set
                if not vs.issubset(versions_set):
                    print "{} is not subset of {}".format(vs, versions_set)
                    return False

            if sel_id:
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

class User(object):
    def __init__(self):
        pass

    def load_json_file(self, filename):
        """
        load json file
        """

        with open(filename, 'r') as f:
            s = f.read()
        
        j = json.loads(s)

        self.load_json(j)
        
    def load_json(self, j):
        """
        load json object
        """

        c = Class("",j)
        
        self.info = c

    def print_text(self):
        self.info.print_text()

