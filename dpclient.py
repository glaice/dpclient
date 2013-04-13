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
    
    
    #user_id = dpb.create_user("unam", "user_passwd", "user_passwd_check", "contact_first_name", "contact_last_name", "user_email")
    
    #if user_id:
    #   print "Usuário criado com sucesso"
    #else:
    #   print "Usuário já existe"
        
    
    #project_id = dpb.create_project("tstan", "1", "1", "20130415", "20130420")
        
    #if project_id:
    #   print "Projeto criado com sucesso"
    #else:
    #   print "Projeto já existe"

    

    task_id = dpb.create_task("2", "tmjjjj", "1", "", "201304121700", "201304261700", "3", "1, 4, 2")

    if task_id:
        print "task criado com sucesso"
    else:
        print "task já existe"


if __name__ == '__main__':
    main()

