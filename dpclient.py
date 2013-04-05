#!/usr/bin/python
import os
import sys
import json
from datetime import datetime
from bunch import bunchify
from browser import DotProjectBot


def main():
    dpb = DotProjectBot("http://localhost/~glaice/dotproject")
    dpb.login("admin", "passwd")
    dpb.create_project("testandoDPC", "1", "1", "15/04/2013", "20/04/2013")





if __name__ == '__main__':
    main()
