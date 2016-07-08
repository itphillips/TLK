These are the issues that need to get addressed in the refactoring.
The steps for completing each of these items will have corresponding issue tickets

***********************************************************************************
IMPLEMENT BOOTSTRAP

Need to make the templates jazzy.

***********************************************************************************
WORK THROUGH FUNCTIONS IN VIEWSTWO.PY TO REMOVE SQLALCHEMY, AND UPDATE VARIABLE PASSING,
TEMPLATES, AND MODELS

1. Write down what variables each function takes and where they come from
2. Write down how function transforms variables and passes them to db
3. Write down how function transforms variables and passes them to template
4. Go to corresponding template and update variable names and attributes
5. Write down what variables get passed back to views

***********************************************************************************
CONSOLIDATE DEVELOPMENT CYCLES 1 AND 2 (E.G., REPLACE ALL 'VIEWSTWO' WITH 'VIEWS', ETC.)

The second cycle of development was done on a duplicate set of files, named '...two' or '...2'.
In hindsight, this was a bad idea, and I need to clean this up so the TLK head folder contains
only the files that it uses. 
