import smtplib
import html2text
import os
import pyodbc
import __main__ as main
from simple_salesforce import Salesforce
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

config = {}
execfile('/etc/py.conf', config)   # contains all the passwords, etc

def testconfig():
    print config['sqluser_qas']

def alert(toAddr, subject, body, fromAddr = 'KNG Automation <automation@kng.com>', showOriginProgram = True):
    """Quick send email method.
    
    In a lot of programs, if something goes bad, I just want to fire off a quick email.  It's hard to remember all of the function arguments
    The downside is I forget which program is send which email, so I add the program's name at the bottom
    """

    msg = MIMEMultipart('alternative')

    msg['Subject'] = subject
    msg['From'] = fromAddr
    msg['To'] = toAddr

    if showOriginProgram:
        body += '<p><small>Sent from <b>' + main.__file__ + '</b></small></p>'
    
    part1 = MIMEText(html2text.html2text(body), 'plain')
    part2 = MIMEText(body, 'html')    

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('10.0.0.16')
    s.sendmail(fromAddr, [toAddr], msg.as_string())
    s.quit()
    
    return True
    
class MSSQL:
    """Helper class to do queries in MSSQL.  
    
    Python default methods were tedious to type every time
    """
    def __init__(self, system='qas'):
        self.system = system
        dsn = ''
        if system == 'qas':
            self.conn = pyodbc.connect("DSN=sapdev;UID=" + config["sqluser_qas"] + ";PWD=" + config["sqlpass_qas"]   + ";DATABASE=QAS")
        elif system == 'prd':
            self.conn = pyodbc.connect("DSN=sapprd;UID=" + config["sqluser_prd"] + ";PWD=" + config["sqlpass_prd"]   + ";DATABASE=PRD")
        else :
            print "System not recognized"
            exit(1)
            
        
        self.cursor = self.conn.cursor()
        
    def do_query(self, query_str):
        self.cursor.execute(query_str)
        data = self.cursor.fetchall()
        headerArr = [x[0] for x in self.cursor.description]
        ret_list = list()
        for x in data:
                ret_list.append({headerArr[i]:str(j).strip() for (i,j) in enumerate(list(x))})
        return ret_list


class SF:
    """Helper class to grab/manipulate SF data from Python.  Mostly using simple_salesforce module
    
    Mostly used for query, but could be expanded
    """
    def __init__(self, system='qas'):
        if system == 'qas':
            self.sf = Salesforce(username=config["sf_user_qas"], password=config["sf_pass_qas"], security_token=config["sf_token_qas"], sandbox=True)
        elif system == 'prd':
            self.sf = Salesforce(username=config["sf_user_prd"], password=config["sf_pass_prd"], security_token=config["sf_token_prd"], sandbox=False)
        else :
            self.sf = Salesforce(username=config["sf_user_qas"], password=config["sf_pass_qas"], security_token=config["sf_token_qas"], sandbox=True)
            
    def do_query(self, query_str):
        """Take a standard SOQL query and return a list of dictionary results

        It should nest any subqueries
        """

        recs = self.sf.query_all(query_str)

        retlist = []
        for rec in recs['records']:
            cur_ret_dict = {}
            for field in rec:
                if type(rec[field]) != unicode and rec[field] != None:

                    curfield = rec[field]
                    if 'records' in rec[field]:
                        #subdict = {}
                        sublist = []
                        for  subrec in rec[field]['records']:
                            curtmpdict = {}
                            for subfield in subrec:
                                cursubfield = subrec[subfield]
                                if type(subrec[subfield]) == unicode:
                                    curtmpdict[subfield] = subrec[subfield]
                            sublist.append(curtmpdict)
                        cur_ret_dict[field] = sublist

                elif type(rec[field]) == unicode:
                    cur_ret_dict[field] = rec[field]
                else:
                    pass
            cur_ret_dict['Id'] = rec['attributes']['url'][-18:]
            retlist.append(cur_ret_dict)

        return retlist

    def unstack_query(self, stacked_list):
        """Function to put a nested SF query result into a "flatter" table that's easier to use in an easier use in Pandas
        
        """    
        retlist = []        
        for head_rec in stacked_list:
            subrec_list = []
            main_currec_dict = {}
            for field in head_rec:
                if type(head_rec[field]) == list:
                    for cur_subrec in head_rec[field]:
                        prefixed_names_dict = {}
                        for regular_field_name in cur_subrec:
                            prefixed_field_name = field + u'_' + regular_field_name
                            prefixed_names_dict[prefixed_field_name] = cur_subrec[regular_field_name]
                        subrec_list.append(prefixed_names_dict)
                else:
                    main_currec_dict[field] = head_rec[field]

            for cur_subrec in subrec_list:
                for cur_main_field in main_currec_dict:
                    cur_subrec[cur_main_field] = main_currec_dict[cur_main_field]
                retlist.append(cur_subrec)
        return retlist


    
        
        


