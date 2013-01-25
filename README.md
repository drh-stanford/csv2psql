To try it out:

	% python setup.py install
	% csv2psql --schema=public --key=student_id,class_id example/enrolled.csv > enrolled.sql
	% psql -f enrolled.sql
