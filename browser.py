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
    
    def create_task(self, project_id, task_name, task_owner, task_parent, start_date, end_date, resources, resources_list):
        task_id = self.exist_task(task_name)
        if task_id:
            return 0
        print "passei pelo return"
        url = self.base_url +  'index.php?m=tasks&a=addedit&task_project='+project_id
        self.br.open(url)
        self.br.select_form('editFrm') #formulário comum a todos
        # liberando con
        self.br.form.set_all_readonly(False) 
        #c=self.br.form.find_control("start_date")
        #c.disabled = False
        #c=self.br.form.find_control("end_date")
        #c.disabled = False
        #Adicionando valores aos campos do fomulario:
        self.br['task_name'] = task_name
        #definindo valores padroes para campos obrigatorios:
        self.br['task_priority'] = ['0']
        

        
        #self.br.select_form('detailFrm')
        self.br.new_control('text', 'dept_ids', {'valor':["0"]})
        self.br.new_control('text', 'dosql', {'valor':"do_task_aed"})
        self.br.new_control('text',"email_comment",{'valor':""})
        self.br.new_control('text', "end_date", {'valor':"28/04/2013"})
        self.br.new_control('text', 'end_hour', {'valor':"17"})
        self.br.new_control('text', 'end_minute', {'valor':'00'})
        self.br.new_control('text','hassign',{'value': resources_list})
        self.br.new_control('text','hdependencies', {'valor':''})
        self.br.new_control('text','hperc_assign',{'value':"1=100;4=100;2=400;"})
        self.br.new_control('text','percentage_assignment',{'value':  "100"})
        self.br.new_control('text','resources',{'value': resources})
        self.br.new_control('text','start_date', {'valor':"13/04/2013"})
        self.br.new_control('text','start_hour', {'valor':'08'})
        self.br.new_control('text','start_minute',{'valor':'30'})
        self.br.new_control('text','task_minute', {'valor':'30'})
        self.br.new_control('text','task_access', {'valor':'0'})
        self.br.new_control('text','task_contacts', {'valor':''})
        self.br.new_control('text','task_description', {'valor':''})
        self.br.new_control('text','task_duration',{'valor':'1'})
        self.br.new_control('text','task_duration_type',{'valor':'1'})
        self.br.new_control('text','task_dynamic',{'valor': '0'})
        self.br.new_control('text','task_end_date',{ 'value':end_date})
        self.br.new_control('text','task_id', {'valor':'0'})
        self.br.new_control('text','task_owner',{'value':task_owner})
        self.br.new_control('text','task_parent',{ 'value': task_parent})
        self.br.new_control('text','task_percent_complete', {'valor':'0'})
        self.br.new_control('text','task_priority', {'valor':'0'})
        self.br.new_control('text','task_project', {'value':project_id})
        self.br.new_control('text','task_related_url', {'valor':''})
        self.br.new_control('text','task_start_date',{'value':start_date})
        self.br.new_control('text','task_status',{'value':'0'})
        self.br.new_control('text','task_target_budget',{'value':''})
        self.br.new_control('text','task_type',{'value':'0'})
        #self.br.select_form('datesFrm')
        #self.br.form.set_all_readonly(False)
        #c=self.br.form.find_control("start_date")
        #c.disabled = False
        #c=self.br.form.find_control("end_date")
        #c.disabled = False 
        #self.br['start_date'] = start_date
        #self.br['end_date'] = end_date
        
        #self.br.select_form('resourceFrm')
        #self.br.form.set_all_readonly(False)
        
        
        #self.br.select_form'editF')
        self.br.fixup()
        response = self.br.submit()
        
        #checar a resposta:
        #with open("resposta.html","w") as f:
        #   f.write(response.read())
        
        task_id=self.exist_task(task_name)
        print "id task_id="+str(task_id)
    
        return task_id
    
    def exist_task(self, task_name):
        url = self.base_url +  'index.php?m=tasks'
        self.br.open(url).read()
        
        my_link = "./index.php?m=tasks&a=view&task_id="
        for link in self.br.links():
            if my_link in link.url and link.text == task_name:
                task_id=link.url.split("task_id=")[1]
                return task_id
        return 0
