#!/usr/bin/python
# -*- coding:UTF-8 -*-

import os
import sys
import json
from datetime import datetime, timedelta
from bunch import bunchify
from browser import DotProjectBot


def main():
    #print sys.argv
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

    

    #task_id = dpb.create_task("2", "taref3", "1", "", "201304151700", "201304261700", ["4","3"], "1,3,4", "2,5")

    #if task_id:
    #    print "task criado com sucesso"
    #else:
    #    print "task já existe"
    
    #log_task_flag = dpb.log_task("5", "taskLogTESTE2", "201304141005", ["60"], 30, "log task realizado")
    #if log_task_flag:
    #    print "task log criado com sucesso"
    #else:
    #    print "task log já existe"
    sair = False
    while(sair==False):

        sair, comando = ler_comando()
        if comando[0].startswith("cp"): #create_project
            
            name_project = comando[1] # segunda linha do comando eh o nome do projeto
            date = datetime.now()
            endDate = date + timedelta(days=10)
            project_id = dpb.create_project(name_project, "1", "1", date.strftime('%Y%m%d'), endDate.strftime('%Y%m%d'))
            if project_id:
                print "Projeto criado com sucesso\n"
            else:
                print "Projeto já existe\n"
                
def ler_comando():
    sys.stdout.write("\nInforme um comando:"+"\n") # \n no inicio garante a leitura de lixos no java sem atraplhar...
    sys.stdout.flush()
    comando = sys.stdin.readline()
    comandos = [ comando ]
    while not comando.startswith("FIMCOMANDO"):
        comando = sys.stdin.readline()
        comandos.append(comando)
    sys.stdout.write("EXECUTANDO COMANDO: %s" % comandos[0])
        
    if comandos[0].startswith("exit"):
        return True, comandos
    else:
        return False, comandos
    
    
def string256(s):
    caracter_extra = "_"* (255-len(s))
    return s+caracter_extra
if __name__ == '__main__':
    main()
    sys.exit(0)

