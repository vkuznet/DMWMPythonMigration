#DMWMPythonMigration

Main task: Porting Data & Workflow Management code to python 3

Supervisors: Eric Vaandering, Dirk Hufnagel

Description:
The WMAgent and Tier0 are responsible for submitting and managing tens of thousands or processing jobs on the Worldwide LHC Computing Grid. DAS and DBS are responsible for tracking data and meta-data of PB of files. This code is in production based on python 2.7. The candidate will work with the development teams to prepare this code for python 3.x, beginning with an audit of the suitability of the external software used and identifying replacements where needed. Automated tools will also be employed to help with this porting.


Everything is written in python 3.5

Dependencies:
Can be used to make a dependencies tree from *.spec files in chosen directory. 
In tree graph:
-Ok means that library is supported in python3
-No means that it isn't

Contains 2 files: 

dependencyWriter.py and node.py

dependencyWriter.py Has one required argument: -path 

And two optional: -rName and -tName

For more info run:

python3 dependencyWriter.py -h

results.txt - list of dependencies with annotations if they are supported in python3
python3AvailableLibs.txt - available python3 libraries
tree.txt- dependencies tree graph

Example:
```
'dependencies'
  -|'sitedb.spec- no'
  -|  -|'cherrypy- ok'
  -|  -|  -|'python- no'
  -|  -|  -|  -|'expat- no'
```



Conversion:

Converts cheetah templates to Jinja2