.PHONY : all clean reset

all : springerbk.sqlite

springerbk.sqlite : .local/database/names.csv ; python database.py

clean : ; rm -f springerbk.sqlite
reset : | clean ;
