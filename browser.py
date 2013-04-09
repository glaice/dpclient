#!/usr/bin/env python
# -*- coding: utf-8 -*-
# THIS CODE IS FROM https://github.com/nqnwebs/h2dp
# CREDIT TO THE ORIGINAL AUTHORS ON THAT PROJECT

import mechanize
import cookielib
import logging

# Browser
class Browser(mechanize.Browser):

    def __init__(self, *args, **kwargs):
        mechanize.Browser.__init__(self, *args, **kwargs)   #old style class
        cj = cookielib.LWPCookieJar()
        self.set_cookiejar(cj)

        # Browser options
        self.set_handle_equiv(True)
        self.set_handle_redirect(True)
        self.set_handle_referer(True)
        self.set_handle_robots(False)

        # Follows refresh 0 but not hangs on refresh > 0
        self.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        # Want debugging messages?
        #self.set_debug_http(True)
        #self.set_debug_redirects(True)
        #self.set_debug_responses(True)

        # User-Agent (this is cheating, ok?)
        ua = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:11.0) Gecko/20100101 Firefox/11.0'
        self.addheaders = [('User-agent', ua)]



class DotProjectBot(object):

    class LoginFailed(ValueError): pass
    class InvalidTask(ValueError): pass
    class LogFail(ValueError): pass


    def __init__(self, base_url):
        self.br = Browser()
        self.base_url = base_url
        if not self.base_url.endswith('/'):
            self.base_url += '/'


    def login(self, username, password):
        self.br.open(self.base_url)
        self.br.select_form(name="loginform")
        self.br['username'] = username
        self.br['password'] = password
        response = self.br.submit()

        if 'Login Failed' in response.read():
            raise DotProjectBot.LoginFailed('username and/or password are incorrect')
        else:
            logging.info("logged in")

    def log_task(self, dp_task_id, date, hours, description):
        url = self.base_url + 'index.php?m=tasks&a=view&task_id=%d&tab=1' % int(dp_task_id)
        response = self.br.open(url)
        if '<td class="error">Task ID is invalid' in response.read():
            raise DotProjectBot.InvalidTask("The task %d doesn't exists in" \
                    "dP or you don't have the permission to see it" % dp_task_id)

        self.br.select_form('editFrm')
        self.br.form.set_all_readonly(False)
        self.br['task_log_date'] = date.strftime('%Y%m%d')
        self.br['task_log_hours'] = str(hours)
        self.br['task_log_description'] = description
        response = self.br.submit()

        if not '<td class="message">Task Log inserted</td>' in response.read():
            raise DotProjectBot.LogFail('Something seems to be wrong. Please check %s' % url)
        else:
            msg = u"«%s (%s hs)» was logged succesfully" % (description, str(hours))
            logging.info(msg)

    def create_project(self, name, owner, company, startDate, endDate, status='0'):
        project_id = self.exist_project(name)
        if project_id:
            return 0
        url = self.base_url +  'index.php?m=projects&a=addedit'
        response = self.br.open(url)
        if 'name="project_name"' in response.read():
            self.br.select_form('editFrm') #formulário comum a todos
            
            # liberando con
            self.br.form.set_all_readonly(False) 
            c=self.br.form.find_control("start_date")
            c.disabled = False
            c=self.br.form.find_control("end_date")
            c.disabled = False
            #Adicionando valores aos campos do fomulario:
            self.br['project_name'] = name
            self.br['project_owner'] = [owner]
            self.br['project_company'] = [company]
            self.br['project_start_date'] = startDate
            self.br['project_end_date'] = endDate
            self.br['start_date'] = startDate
            self.br['end_date'] = endDate
            self.br['project_status'] = [status]
            
            #definindo valores padroes para campos obrigatorios:
            self.br['project_priority'] = ['0']
            self.br['project_short_name'] = name[:3]
            self.br['project_color_identifier'] = 'FFFFFF'
            self.br['project_type'] = ['0']
            
            response = self.br.submit()
            
            project_id=self.exist_project(name)
        
            return project_id
                
        
        else:
            raise DotProjectBot.LogFail('Não foi possível acessar o formulário de cadastro de projeto')


    def exist_project(self, project_name): 
        url = self.base_url +  'index.php?m=projects'
        self.br.open(url)
        
        my_link = "?m=projects&a=view&project_id="
        for link in self.br.links():
            if my_link in link.url and link.text == project_name:
                project_id = link.url.split("project_id=")[1]
                return project_id
        return 0

    def create_user(self, user_name, user_passwd, user_passwd_check, contact_first_name, contact_last_name, user_email):
        
        user_id = self.exist_user(user_name)
        if user_id:
            return 0
        
        url = self.base_url +  'index.php?m=admin&a=addedituser'
        self.br.open(url)
        self.br.select_form('editFrm') #formulário comum a todos
        # liberando con
        self.br.form.set_all_readonly(False) 
        #c=self.br.form.find_control("start_date")
        #c.disabled = False
        #c=self.br.form.find_control("end_date")
        #c.disabled = False
        #Adicionando valores aos campos do fomulario:
        self.br['user_username'] = user_name
        self.br['user_password'] = user_passwd
        self.br['password_check'] = user_passwd_check
        self.br['contact_first_name'] = contact_first_name
        self.br['contact_last_name'] = contact_last_name
        self.br['contact_email'] = user_email
        
        #definindo valores padroes para campos obrigatorios:
        self.br['user_type'] = ['5']
        self.br['user_role'] = ['14']
        
        self.br.submit()
        
        user_id=self.exist_user(user_name)
    
        return user_id


    def exist_user(self, user_name):
        url = self.base_url +  'index.php?m=admin&tab=0'
        self.br.open(url)
        
        my_link = "?m=admin&a=viewuser&user_id="
        for link in self.br.links():
            if my_link in link.url and link.text == user_name:
                user_id=link.url.split("user_id=")[1]
                return user_id
        return 0


