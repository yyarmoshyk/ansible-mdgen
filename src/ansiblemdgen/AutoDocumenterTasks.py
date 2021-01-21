#!/usr/bin/env python3

from ansiblemdgen.Config import SingleConfig
import sys
import yaml
import os
from os import walk
from ansiblemdgen.Utils import SingleLog,FileUtils
from mdutils.mdutils import MdUtils

class TasksWriter:

    config = None
    tasks_dir = None
    handlers_dir = None

    def __init__(self):
        self.config = SingleConfig()
        self.log = SingleLog()

        self.tasks_dir = self.config.get_base_dir()+"/tasks"
        self.log.info("Tasks directory: "+self.tasks_dir)

        self.handlers_dir = self.config.get_base_dir()+"/handlers"
        self.log.info("Tasks directory: "+self.handlers_dir)

    def render(self):

        self.makeDocsTasksDir()

        if (self.config.tasks != None and self.config.tasks['combinations'] != None):
            self.iterateOnCombinations(self.config.get_base_dir(), self.config.tasks['combinations'], self.config.get_output_tasks_dir())
        else:
            self.iterateOnFilesAndDirectories(self.tasks_dir, self.config.get_output_tasks_dir())

        self.makeDocsHandlersDir()

        if (self.config.handlers != None and self.config.handlers['combinations'] != None):
            self.iterateOnCombinations(self.config.get_base_dir(), self.config.handlers['combinations'], self.config.get_output_handlers_dir())
        else:
            self.iterateOnFilesAndDirectories(self.handlers_dir,self.config.get_output_handlers_dir())


    def makeDocsTasksDir(self):
        output_tasks_directory = self.config.get_output_tasks_dir()
        self.log.debug("(makeDocsTasksDir) Output Directory: "+output_tasks_directory)
        if not os.path.exists(output_tasks_directory):
            os.makedirs(output_tasks_directory)
    
    def makeDocsHandlersDir(self):
        output_handlers_directory = self.config.get_output_handlers_dir()
        self.log.debug("(makeDocsTasksDir) Output Directory: "+output_handlers_directory)
        if not os.path.exists(output_handlers_directory):
            os.makedirs(output_handlers_directory)

    def iterateOnFilesAndDirectories(self, tasks_dir, output_directory):
        for (dirpath, dirnames, filenames) in walk(tasks_dir):

            for filename in filenames:
                if filename.endswith('.yml'):
                    self.createMDFile(dirpath, filename, output_directory)

            for dirname in dirnames:
                self.iterateOnFilesAndDirectories(dirpath+"/"+dirname, output_directory)

    def createMDFile(self, dirpath, filename, output_directory):

        self.log.info("(createMDFile) Create MD File")
        self.log.debug("(createMDFile) dirpath: "+dirpath)
        self.log.debug("(createMDFile) filename: "+filename)
        
        if output_directory == self.config.get_output_tasks_dir():
            docspath = dirpath.replace(self.tasks_dir,output_directory)
        else:
            docspath = dirpath.replace(self.handlers_dir,output_directory)
        self.log.debug("(createMDFile) docspath: "+docspath)

        if not os.path.exists(docspath):
            os.makedirs(docspath)

        mdFile = MdUtils(file_name=docspath+"/"+filename.replace('.yml',''))
        mdFile.new_header(level=1, title=filename) 
        self.addTasks(dirpath+"/"+filename, mdFile)

        mdFile.create_md_file()
        self.log.info("(createMDFile) Create MD File Complete")

    
    def addTasks(self, filename, mdFile):
        self.log.debug("(addTasks) Filename: "+filename)
        with open(filename, 'r') as stream:
            try:
                tasks = yaml.safe_load(stream)
                if tasks != None:
                    for task in tasks:
                        mdFile.new_paragraph('* '+task["name"])
            except yaml.YAMLError as exc:
                print(exc)

    def iterateOnCombinations(self, rolepath, combinations, output_directory):
        for combination in combinations:
            self.createMDCombinationFile(combination['filename'], combination['files_to_combine'], output_directory)

    def createMDCombinationFile(self, comboFilename, filenamesToCombine, output_directory):

        comboFilenameAbs = output_directory+"/"+comboFilename      
        comboFileDirectory = comboFilenameAbs[0:int(comboFilenameAbs.rfind('/'))]

        if not os.path.exists(comboFileDirectory):
            os.makedirs(comboFileDirectory)

        mdFile = MdUtils(file_name=comboFilenameAbs)

        mdFile.new_header(level=1, title='Tasks: '+comboFilename[comboFilename.rfind('/')+1:])
        mdFile.new_line("---")
        for filename in filenamesToCombine:
            mdFile.new_line("")
            mdFile.new_header(level=2, title=filename['name']) 

            self.addTasks(self.tasks_dir+"/"+filename['name'], mdFile)

        mdFile.create_md_file()