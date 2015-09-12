#!/usr/bin/env python

import argparse

import python_resume
import python_resume.user


u = python_resume.user.User()
u.load_json_file('/www-share/charlesrymal_gmail_com.json')

#u.print_text()

g = python_resume.Generator(versions=['private','me'])

g.user = u

g.filt()

#print g.user.info.objective[0].text

g.render(       "resume2.html")
g.render_pdf(   "resume2.html")
g.render(       "cover_letter_no_company.html")
g.render_pdf(   "cover_letter_no_company.html")


u = python_resume.user.User()
u.load_json_file('/www-share/charlesrymal_gmail_com.json')

g = python_resume.Generator(versions=['private','cs'])

g.user = u
g.filt()

g.render(       "resume2.html")
g.render_pdf(   "resume2.html")
g.render(       "cover_letter_no_company.html")
g.render_pdf(   "cover_letter_no_company.html")


