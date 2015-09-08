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

from info import *


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
 


