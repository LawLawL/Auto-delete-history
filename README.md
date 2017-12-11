# Auto-delete-history

Both Google Chrome and Vivaldi (and I would assume all chromium-based browsers) use SQL tables to register history informations. 
The nice thing with using that format is that it is possible to tell the SQL tables that we want certain things not to be saved. 
We do that here using [check constraints](https://www.w3schools.com/sql/sql_check.asp): this program takes as input a list of keywords
and will set a constraint so that any url containing that constraint will not be saved. 

## Download

If you can open a terminal with bash then go for

`wget https://raw.githubusercontent.com/Magalame/Auto-delete-history/master/autodelete.py`

If you cannot but you still have python already installed then you can download the source file [here](https://github.com/Magalame/Auto-delete-history/raw/master/autodelete.zip)

If you also do not have python installed and you are on Windows then download the compiled program [here](https://github.com/Magalame/Auto-delete-history/raw/master/autodeletehistory.zip)

## Use

For now the scripts works only for Google Chrome and Vivaldo

### If you have downloaded the .py

Go where the file is, then execute 

`python3 autodelete.py -b the_name_of_your_browser_here -k a,comma,separated,list,of,keywords`

For the `-b` switch the accepted values are "chrome" or "vivaldi", unsurprisingly. 

### If you have downloaded the zip with the .exe inside

Open a terminal where the .exe is, then 

`autodelete.exe -b the_name_of_your_browser_here -k a,comma,separated,list,of,keywords`

## Todo

* implement a reset function for the tables

* allow for personalized installation folder for a browser
