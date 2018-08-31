This folder contains Python PeakQL client examples.

To load PeakQL, you can follow EITHER way below:
a) Add PeakQL python distribution path, which includes PeakQL.py, _PeakQL.pyd and other required dlls, (for example, C:\PeakAddins\Peak64\20161221348_031134) to PYTHONPATH;
b) Copy the file PeakQL.pth to YourPythonPath\Lib\site-packages, and update the path in this file if needed.

Data types: Peak data types are defined in PeakQL_dll_interface.i. For example,
	%template(Str_Vec)std::vector<std::string>;
	You will use PeakQL.Str_Vec where string vectors are used in the C++ interface.
	Dates are passed as PeakQL.PkInt.

Default parameters: Use PeakQL.PK_NULL_DATE etc. to fill in default parameters. Python "None" usually won't work.
    PK_NULL_BOOL = -1L
    PK_NULL_DATE = -2147483646L
    PK_NULL_DOUBLE = -9.9e+39
    PK_NULL_INT = -2147483645L
    PK_NULL_LONG = -2147483647L
    PK_NULL_STR = ''

SWIG Python document: http://www.swig.org/Doc3.0/Python.html

Please add your tips to this document. Thanks!
