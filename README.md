## DMWMPythonMigration

Main task: Porting Data & Workflow Management code to python 3

Supervisors: Eric Vaandering, Dirk Hufnagel

Description:
The WMAgent and Tier0 are responsible for submitting and managing tens of thousands or processing jobs on the Worldwide LHC Computing Grid. DAS and DBS are responsible for tracking data and meta-data of PB of files. This code is in production based on python 2.7. The candidate will work with the development teams to prepare this code for python 3.x, beginning with an audit of the suitability of the external software used and identifying replacements where needed. Automated tools will also be employed to help with this porting.


Everything is written in python 3.5

## Dependencies:
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



## Conversion:

Converts cheetah templates to Jinja2

**Example:**

Cheetah:
```HTML
#from DAS.web.utils import quote
#set item = $quote($item)
#set api = $quote($api)
<!-- sitedb.tmpl -->
#if $api == "sites"
<a href="/sitedb/prod/sites/$item">SiteDB</a>
#else if $api == "people"
<a href="/sitedb/prod/people/$item">SiteDB</a>
#end if
<!-- sitedb.tmpl -->
```
Jinja2:
```HTML
{% set item = quote(item) %}
{% set api = quote(api) %}
<!-- sitedb.tmpl -->
{% if api == "sites" %}
<a href="/sitedb/prod/sites/{{item}}">SiteDB</a>
{% elif api == "people" %}
<a href="/sitedb/prod/people/{{item}}">SiteDB</a>
{% endif %}
<!-- sitedb.tmpl -->
```	
	
To convert cheetah templates to Jina2 need to run script TemplateConverter.py with parameters:

* -p PATH            Directory of .tmpl files that needs to be converted
* -pc PATHCONVERTED  Path where converted templates should be saved
* -pm PATHMANUAL     Path where information about failed conversions should be saved

After conversions information about files that could not be converted will be saved in PATHMANUAL/manualConversions.txt

After conversions jinja2.Environment should be setup:
* Set prefix for line based comments (e.g. ####)
* Create methods and set them to substitute imported classes (e.g. quote)

