## Converter Guide


```sh
python3 TemplateConverter.py -p /path/to/templates -pc /path/to/convertedTemplates -pm /path/to/mannualConversions
```
* -p path to templates (.tmpl) 
* -pc path where converted templates (.html) will be saved
* -pm path to where information about failed conversions will be saved

After script is done (should not take more than few seconds) it should display information about templates that might need manual conversion.

##### API conversion for DAS:
In DAS/src/python/DAS/web/tools.py change:
```py
 def templatepage(self, ifile=None, *args, **kwargs):
        search_list = []
        if len(args) > 0:
            search_list.append(args)
        if len(kwargs) > 0:
            search_list.append(kwargs)
        templatefile = os.path.join(self.templatedir, ifile + '.tmpl')
        if os.path.exists(templatefile):
            # little workaround to fix '#include'
            search_list.append({'templatedir': self.templatedir})
            template = Template(file=templatefile, searchList=search_list)
            return template.respond()
```
To something like:
```py
 def templatepage(self, ifile=None, *args, **kwargs):
    env = Environment(loader=jinja2.FileSystemLoader(self.templatedir))
    for arg in args:
        kwargs.update(**arg)
    if os.path.exists(self.templatedir+ifile + '.html'):
        template = env.get_template(ifile + '.html')
        return template.render(kwargs)
```

Also should add all modules that used to be imported in cheeath:
```py
    kwargs.update(**{"json":json})
```

