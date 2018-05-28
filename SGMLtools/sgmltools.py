##import openpyxl
##import xlrd
##import csv
from bs4 import BeautifulSoup
##from tabulate import tabulate
import re
import logging
import sys

class AMMtools:
    """Master class to work with Airbus SGML files"""

    def __init__(self, source_path, sourcefile="AMM.SGM", log_enable=False):
        """Load the source data"""
        self.log = logging
        self.source_path = source_path
        if log_enable == True:
            self.log.basicConfig(level=logging.DEBUG)
        else:
            self.log.basicConfig(level=logging.CRITICAL)
        try:
            with open(source_path+'AMM.SWE', 'r') as warning_file:
                warning_data = warning_file.readlines()
                self.warnings = self.buildEntityDict(warning_data)
                self.log.info('Warnings loaded')
        except FileNotFoundError:
            self.log.warning("Did not find the warnings file on path: {}".format(source_path))
        try:
            with open(source_path+'AMM.SCE', 'r') as warning_file:
                warning_data = warning_file.readlines()
                self.cautions = self.buildEntityDict(warning_data)
                self.log.info('Cautions loaded')
        except FileNotFoundError:
            self.log.warning("Did not find the cautions file on path: {}".format(source_path))
        self.log.info('Opening {}'.format(source_path+'AMM.SGM'))
        with open(source_path+sourcefile, 'r') as source_data:
            data = source_data.read()
            self.manual = BeautifulSoup(data, 'html.parser')
            self.log.debug('AMM Parsing succesful')            
        self.log.debug('Init OK')

    def findAllTasks(self, recurse_limit=None):
        """Searach the Manual for anything with a task tag

        Returns a list
        """
        return self.manual.find_all('task', limit=recurse_limit)

    def extractTaskInfo(self, task):
        """Get all info from a task"""
        taskcontent = dict()
        try:
            title = task.title.string
        except AttributeError:
            self.log.warning('Failed to extract a task here')
            return None
        self.log.info('TASK: {}'.format(title))
        self.zone_panHandler(task, "zone")
        self.zone_panHandler(task, "pan")
        self.toolHandler(task)
        refstring = self.__splitCode(task)
        self.log.info(refstring)
        topics = task.find_all("topic")
        for x in range(0, len(topics)):
            subtasks = topics[x].find_all("subtask")
            for y in range(0, len(subtasks)):
                subtask = dict()
##                subtasks[y].effect['effrg']
                try:
                    effec = subtasks[y].effect['effrg']
                except TypeError:
                    self.log.warning('TypeError on {}'.format(title))
                    continue
                except KeyError:
                    self.log.warning('KeyError on {}'.format(title))
##                self.log.debug("Effectivity: %s\nAccomplish A320 AMM %s Subtask %s: %s" % (effec,
##                                                                                           topics[x].title.string,
##                                                                                           self.__splitCode(subtasks[y]),
####                                                                                           subtask_string(subtasks[y]),
##                                                                                           subtasks[y].para.string))
                if subtasks[y].find('list1') is not None:
                    self.getTaskContent(subtasks[y].list1,1)
                if subtasks[y].find("cblst") != None:
                    cblst = True

    def findListObject(self, parent_obj):
        """Extract the lists"""
        recursion_level = 1
        listcaptureRE = re.compile('list(\d)', re.IGNORECASE)
        lists = parent_obj.find_all(listcaptureRE)
        for item in lists:
            matchobj = re.match(listcaptureRE, item.name)
            if matchobj is not None:
                if int(matchobj.group(1)) > recursion_level:
                    recursion_level = int(matchobj.group(1))
        return str(recursion_level)

    def getTaskContent(self, parent_obj, level):
        """Walk through the task and get the info"""
##        self.log.warning('LEVEL INPUT {}'.format(level))
        listcaptureRE = re.compile('list(\d)', re.IGNORECASE)
        list_items = parent_obj.find_all('l{}item'.format(level), recursive=False)
        for item in list_items:
##            self.log.debug('Para {}'.format(item.para.string))
            for nextitem in item:
##                self.log.debug('Parent:{} This:{} Content:{}'.format(nextitem.parent.name, nextitem.name, nextitem.string))
                if nextitem.para is None:
##                    self.log.debug("Childdata")
                    listitemcontent = list()
                    for space in range(int(level)):
                        listitemcontent.append(' ')
                    for child in nextitem.descendants:
##                        self.log.info('Parent:{} This:{} Content:{}'.format(child.parent.name, child.name, child.string))
                        if child.string is not None and child.name not in ['pan', 'con', 'std', 'stdname', 'cblst', 'refint', 'refext']:
                            string_ob = str(child.string).rstrip()
                            string_ob = string_ob.lstrip()
                            listitemcontent.append(string_ob)
                            if child.parent.name == 'note':
                                self.log.debug('NOTE: {}'.format(child.string))
##                            if child.parent.name == 'table':
##                                print("Found Table")
##                                tableHandler(child)                                                                
########################################################################################                            
##                            THis is only commented out to reduce debug clutter
##                        if child.parent.name == "cblst":
##                            self.cblstHandler(child.parent)
##                        if child.parent.name in ['warning', 'caution']:
##                            try:
##                                if child.string[1] == 'W':
##                                    self.log.debug(self.warnings[child.string[1:7]])
##                                elif child.string[1] == 'C':
##                                    self.log.debug(self.cautions[child.string[1:7]])
##                            except KeyError:
##                                self.log.warning('Unable to locate Warning/Caution {}'.format(child.string[1:7]))
########################################################################################                                
                    while '' in listitemcontent:
                        listitemcontent.remove('')
##                    self.log.info(' '.join(self.__fixPunctuation(listitemcontent)))
##                    print(listitemcontent)
##                elif nextitem.name == 'note':
##                    self.log.info(self.noteHandler(nextitem))
                elif nextitem.name == 'table':
                    self.log.debug(self.tableHandler(nextitem))
            if item.find(listcaptureRE) is not None:
                nextlevel = re.match(listcaptureRE, item.find(listcaptureRE).name)
                self.getTaskContent(item.find(listcaptureRE), nextlevel.group(1))

    def noteHandler(self, noteblock):
        """Extract a note"""
        
        def elementignore(parentlist):
            """"Sub routine to assist ignoring unlistitems"""
            ignorelist = ['refint',
                          'unlist',
                          'unlitem']
            for parent in parentlist:
                if parent.name in ignorelist:
                    return True
            return False
        
        whitelist = ['para',
                     'refblock',
                     'effect',
                     'note',
                     'stdname',
                     'grphcref',
                     'toolnbr',
                     'toolname',
                     'revst',
                     'refext'
                     ]
        notelist = list()
        skip = False
        if len(noteblock.find_all("para")) >= 1:
            for item in noteblock.descendants:
                if skip == True:
                    skip = False
                    continue
                if item.string is not None:
                    if elementignore(item.parents) is True:
                        pass
                    elif item.parent.name in whitelist:
                        notelist.append(item.string)
                    else:
                        self.log.warning("Unhandled element {} in note block".format(item.parent.name))
                        print(noteblock.prettify())
                    skip = True
                elif item.name == 'unlist':
                    notelist.append(self.__unlistHandler(item))
        return ' '.join(notelist)
            
        
    def __fixPunctuation(self, list_to_fix):
        """Private method to fix the punctuation"""
        punclist = ['.', ',']
        for punc in punclist:
            while punc in list_to_fix:
                try:
                    index_pos = list_to_fix.index(punc)
                except ValueError:
                    continue
                popped_item = list_to_fix.pop(index_pos)
                list_to_fix[index_pos - 1] = list_to_fix[index_pos - 1] + popped_item
        return list_to_fix
        
    def __splitCode(self, tag):
        """Private method to split the task code into into its major parts"""
        tagattrs = tag.attrs
        if 'varnbr' in tagattrs:
            var = tagattrs['varnbr']
        else:
            var = ''
        return '-'.join((tagattrs['chapnbr'],
                         tagattrs['sectnbr'],
                         tagattrs['subjnbr'],
                         tagattrs['func'],
                         tagattrs['seq'],
                         tagattrs['confltr']+var
                         ))

    def __unlistHandler(self, unlistblock):
        """Extract evey unlitem and return as ~ %TEXT\n"""
        returnstr = '\n'
        for unlitem in unlistblock.find_all("unlitem"):
            if len(unlitem.find_all("para")) != 1:
                self.log.warning("Found something other than a single PARA in a noteblock")
            else:
                returnstr = returnstr + '~ {}\n'.format(unlitem.para.string)
        return returnstr

    def cblstHandler(self, cblst_block):
        """Extract the Circuit Breaker data"""
        cb_sub_lists = cblst_block.find_all("cbsublst")
        cb_data_elements = ["effect", "cb", "cbname", "pan", "cbloc"]
        cb_lst_all = list()
        for cb_sub_list in cb_sub_lists:
            cb_data_dict = dict()
            if cb_sub_list.find("ein") is not None:
                ein_content = cb_sub_list.find("ein").string
                if cb_sub_list.find("equname") is not None:
                    equname_content = cb_sub_list.find("equname").string
                    self.log.debug("{} - {}".format(ein_content, equname_content))
                else:
                    self.log.debug(ein_content)
            cb_data_list = cb_sub_list.find_all("cbdata")
            for cb_data in cb_data_list:
                for element in cb_data_elements:
                    cb_data_dict[element] = cb_data.find(element).string
                cb_lst_all.append(cb_data_dict)
            self.log.debug(cb_lst_all)
        return cb_lst_all

    def zone_panHandler(self, taskblock, target):
        """Extract zones or panels from the pretopic.  

        Pass in the string "zone" or "panel" as the target argument
        """
        list_items = taskblock.list1.find_all("l1item")
        zone_pan_set = set()
        for item in list_items:
            if item.para.string != "Work Zones and Access Panels":
                continue
            else:
                zones_pans = item.find_all(target)
                if zones_pans is not None:
                    for zone_pan_obj in zones_pans:
                        zone_pan = zone_pan_obj.string.rstrip()
                        zone_pan_set.add(zone_pan)
        return zone_pan_set
##        self.log.debug('{}: {}'.format(target.upper(), zone_pan_set))

    def toolHandler(self, taskblock):
        """Get tool info from the task"""
        list_items = taskblock.list1.find_all("l1item")
        toollist = list()
        for item in list_items:
            this_string = item.para.string.lstrip().rstrip().replace('\n', '')
            if this_string != "Fixtures, Tools, Test and Support Equipment":
                continue
            else:

                rows = item.table.tgroup.tbody.find_all("row")
                for row in rows:
                    tool_obj = list()
                    if row.entry.para.toolnbr is not None:
                        tool_obj.append(row.entry.para.toolnbr.string)
                        tool_obj.append(row.entry.next_sibling.para.string)
                        tool_obj.append(row.entry.next_sibling.next_sibling.para.string)
                        toollist.append(tool_obj)
####Commented out for now.  It looks like this result is always a torque wrench.
##                    if row.entry.para.string == 'No specific' and len(row.find_all('entry')) == 2:
##                        tool_obj.append(row.entry.para.string)
##                        tool_obj.append(row.entry.next_sibling.para.string)
##                        print(row.entry.next_sibling.para.prettify())
##                        toollist.append(tool_obj)
        self.log.debug('Tooling: {}'.format(toollist))
        if len(toollist) > 0:
            self.log.debug('Tooling: {}'.format(toollist))
        return toollist

    def tableHandler(self, tableblock):
        """Extract information from a table element"""
        tabledict = dict()
        
        tablelist = list()
        tablegroups = tableblock.find_all("tgroup")
        if len(tableblock.find_all("title")) != 0:
            self.log.warning("An unhandled title element exists in TGROUP")
        for tgroup in tablegroups:
            headerlist = list()
            headerlist.append('HEADER')
            rowdict = dict()
            moop = tgroup.colspec
            for x in range(int(tgroup['cols'])):
                moop = moop.contents[0]
            if moop.spanspec is not None:
                thead = moop.spanspec.thead
            else:
                thead = moop.thead
            if thead is not None:
                for item in thead.row.find_all("entry"):
                    if item.string is not None:
                        headerstring = item.para.string.lstrip()
                        headerstring = headerstring.rstrip()
                        headerlist.append(headerstring.rstrip())
                    else:
                        headerlist.append('')
            tgroupkey = "tgroup"+str(tablegroups.index(tgroup))
            tabledict[tgroupkey] = headerlist
            self.log.debug(headerlist)
            tablelist.append(headerlist)
            for row in tgroup.tbody.find_all("row"):
                rowlist = list()
                entrycounter = 1
                for entry in row.find_all("entry"):
                    while len(rowlist) < int(entry["colname"][3:]):
                        rowlist.append('')
                        entrycounter += 1
                        continue                       
                    entrys = str()
                    entrycounter += 1
                    for para in entry.find_all("para"):
                        if para.string is not None:
                            parastring = para.string.lstrip()
                            parastring = parastring.rstrip()
                            entrys = entrys + parastring + ' '
                        else:
                            entrys = ''
                    rowlist.append(entrys.rstrip())
                while len(rowlist) < len(headerlist)-1:
                    rowlist.append('')
                self.log.debug(rowlist)
                tablelist.append(rowlist)
        return tablelist
            
    def buildEntityDict(self, warning_data):
        """Build a dictionary to reference Warnings/Cautions by their ID.


        """
        warning_dict = dict()
        opentagRE  = re.compile('"<PARA>.*')
        warncodeRE = re.compile('[WC]\..{4}')
        closetagRE = re.compile('<\/PARA>">')
        open_armed = True
        warningstring = str()
        for line in warning_data:
            if open_armed is True:
                code = warncodeRE.search(line)
                warningstring = line[opentagRE.search(line).start()+1:]
                open_armed = False
            else:
                if closetagRE.search(line) is None:
                    warningstring = warningstring + line
                else:
                    warningstring = warningstring+line[:closetagRE.search(line).end()-2]
                    open_armed = True
                    warning_dict[code.group(0)] = warningstring
                    warningstring = ''
        return warning_dict
   
    def grabTestData(self, block, name):
        """Used to extract and format a block for testing purposes"""
##        print(block.prettify())
        block = str(block[0])
        a = str()
        a = a + block.lstrip().rstrip().replace('\n', '')
        
        try:
            open(sys.path[0]+'/tests/test_data/'+name, 'r')
        except FileNotFoundError:
            with open(sys.path[0]+'/tests/test_data/'+name, 'w') as savefile:
                    savefile.write(a)
            pass
            
    
##    def getSteps(self, task, zone):
##        topics = task.find_all("topic")
##        print(task.title.string)
##        side = get_side(zone)
##        if side is not None:
##            print(side)
##    ##    subtasks = task.find_all("subtask")
##        for x in range(0, len(topics)):
##            subtasks = topics[x].find_all("subtask")
##            for y in range(0, len(subtasks)):
##                print("Effectivity: %s\nAccomplish A320 AMM %s Subtask %s: %s" % (subtasks[y].effect['effrg'], topics[x].title.string, subtask_string(subtasks[y]), subtasks[y].para.string))
##                if subtasks[y].find("cblst") != None:
##                    cblst = subtasks[y].find("cblst")
##                    cbdata = cblst.find_all("cbdata")
##                    hdrs = ["FIN", "Name", "Panel", "Location", "Effectivity"]
##                    listofbreakers = []
##                    for z in range(0, len(cbdata)):
##                        row = []
##                        row.append(cbdata[z].find("cb").string)
##                        row.append(cbdata[z].find("cbname").string)
##                        row.append(cbdata[z].find("pan").string)
##                        row.append(cbdata[z].find("cbloc").string)
##                        effect = cbdata[z].find("effect")
##                        row.append(effect.attrs['effrg'])
##                        listofbreakers.append(row)
##                    print(tabulate(listofbreakers, hdrs, tablefmt="grid"))
##    ##        print(topics[x].title.string)

    

if __name__ == '__main__':
    ddata = AMMtools('d:/Code/A320/Part_1/SGML_000042029356/SGML/', log_enable=True)
    boop = ddata.findAllTasks(recurse_limit=250)
    for things in boop:
        ddata.extractTaskInfo(things)



