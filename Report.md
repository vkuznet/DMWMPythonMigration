## Report

Week 1:
- Created Dependencies tree
- Tested a bit how DAS works
- Read documentation for Cheetah, Jinja, created some notes. 
- Started to work on Cheetah - > Jinja2 template conversion.
- Created VM - still having some problems

Week2:
- Refactored Dependencies tree
- Created fileWriter/Reader
- Added comments, other fixes after review
- Converted main cheetah expressions to jinja2
- Testing

Week3:
- Testing
- Rewrote placeholder conversion
- Read about regex(recursive, conditionals etc.) - tested them out
- Created IrrevertableData to store info about cheetah expressions that can't be converted
- Fixed some minor bugs(search for expr. end till the end of file, continue and etc.)

Week4:
- Reconfigured VM. Fixed the problems I had before. It's up and running.
- Added more documentation for template converter.
- Created scrip that analyzes any python project and returns unsupported modules/libs.
- Some bug fixes (changed how comments are handled, new line removal and etc.).

Week5-6:  
- Fixed manualResults output for Converter.
- Updated scipt that analyzes any python project (Uses requests now)
- Analyzed all projects in DMWM
- Made list of python modules that need to be ported
- Read https://twiki.cern.ch/twiki/bin/viewauth/CMS/DMWM
- Researched possible libraries for migration
- Wrote some small scripts for research (https://github.com/SaltumDis/conversions)

Week7:  
- Finalized report for migrations
- Small fixes for conversions cheetah > Jinja2
- Started migrating mox. Found out that the code that imports it is obsolete.
- Started to research obsolete code (wrote some scripts for files comparison)

Week8:  
- Added unittest for converted