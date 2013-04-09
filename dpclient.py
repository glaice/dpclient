#!/usr/bin/python
# -*- coding:UTF-8 -*-

import os
import sys
import json
from datetime import datetime
from bunch import bunchify
from browser import DotProjectBot


def main():
    dpb = DotProjectBot("http://localhost/~glaice/dotproject")
    dpb.login("admin", "passwd")
    project_id = dpb.create_project("testan", "1", "1", "20130415", "20130420")
    
    if project_id:
        print "Projeto criado com sucesso"
    else:
        print "Projeto já existe"




if __name__ == '__main__':
    main()

