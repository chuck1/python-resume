#!/usr/bin/env python

import argparse

import python_resume
import python_resume.user

parser = argparse.ArgumentParser()
parser.add_argument("FILE", nargs=1)
args = parser.parse_args()



u = python_resume.user.User()

u.load_json_file(args.FILE[0])

#u.print_text()

g = python_resume.Generator(version=['public'])

g.user = u

g.render("resume2",".html")

