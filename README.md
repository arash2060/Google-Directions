# Google Directions GUI
This is a tkinter GUI to download the directions between two addresses, business-name-address combinations, or lat-long using Google Maps API.

The user needs to provide their own Google Maps API key.
The current version reads an excel file and outputs another excel file. You can choose the business name, address, city, zipcode, ... fields.

Two levels of output are saved.

## Possible imporvements:
(1)
A lot of errors/exceptions haven't been workout yet.

Example: If user chooses a date, say two years from now, Google throws an error and program stops. 

(2)
Multithreading the tasks will keep the application responsive when the API queries run. However, this reformatting the program into a python class ... I'll know better next time.
