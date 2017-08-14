import psycopg2 as p2
import csv
import data_dump_parser as ddp

DB_NAME = "shadetreept"
PT_DEMO_TABLE_NM = "ptdem"
PT_MEDS_TABLE_NM = "ptmeds"
USER = "postgres"
PASSWORD = "123"
MRN_FIELD_NM = "PtMRN"
DEMO_FIELD_TYPES = {"PtAge" : "REAL",
								   "PtSex" : "CHAR(1)"}
MED_FIELD_DEF =  {"medtxt": "TEXT",
								   "name": "TEXT",
									"strength": "TEXT",
									"PAP_appr":"TEXT",
									"PAP_date":"date",
									"Disp_daycnt":"INT",
									"Disp_date":"date"
									}


def get_filename() :
	filename = input('Enter full path to data file:')
	return filename

def make_database_csv(csv_filename):
	#create a patient database from a data dump file with med list (:PRLISTMED)
	#		return True if successful, otherwise False
	return make_database_ptList(ddp.buildPatientList(csv_filename))


def make_database_ptList(patient_list):


	if not len(patient_list) > 0 : return False

	#connect to databases
	conn = p2.connect("dbname=" + DB_NAME + " user=" + USER + " password=" + PASSWORD)
	cur = conn.cursor()

	#drop and recreate the patient databases each time
	cur.execute("DROP TABLE IF EXISTS " + PT_DEMO_TABLE_NM + ", " + PT_MEDS_TABLE_NM + ";")
	cur.execute(create_demo_table_comm(patient_list))
	cur.execute(create_med_table_comm())

	#populate tables
	for pt in patient_list :
		populate_pt_demo(pt,cur)
		populate_pt_meds(pt,cur)


	conn.commit()
	cur.close()
	conn.close()

	return True

def create_demo_table_comm(patient_list):

	# CREATE TABLE <table_name> (
	# 		MRN			TEXT		PRIMARY KEY		NOT NULL,
	# 		<attr1>		TEXT,
	# 		...
	# );

	command = "CREATE TABLE " + PT_DEMO_TABLE_NM + "("
	command += MRN_FIELD_NM + " TEXT PRIMARY KEY NOT NULL, "

	#create schema for table (all string, assume that each patient has all attributes)
	pt = patient_list[0]
	command += ", ".join(format_field_defintion(field_name) for field_name in pt.attributeList.keys()) + ");"

	return command

def format_field_defintion(field_name):
	return field_name + " " + DEMO_FIELD_TYPES.get(field_name, "TEXT")

def create_med_table_comm():

	# CREATE TABLE <table_name> (
	# 		MRN			TEXT		PRIMARY KEY		NOT NULL,
	# 		<attr1>		TEXT,
	# 		...
	# );


	command = "CREATE TABLE " + PT_MEDS_TABLE_NM + "("
	command += MRN_FIELD_NM + " TEXT NOT NULL, "
	command += ", ".join((header + " " + type) for header, type in MED_FIELD_DEF.iteritems())
	command += ");"


	return command

def populate_pt_meds(pt, cur):
	insert = "INSERT INTO " + PT_MEDS_TABLE_NM + "(" + MRN_FIELD_NM +", " + ", ".join(MED_FIELD_DEF.keys()) + ") "
	insert += "VALUES (" + "%s, "*len(MED_FIELD_DEF) + "%s)"


	for med in pt.getMedList():
		cur.execute(insert, (pt.mrn,
									 med.strength,
									 med.name,
									 med.PAPexpirationDate,
									 med.PAPstatus,
									 med.dispensedDate,
									 med.dispensedDuration,
									 med.medText))

	return

def populate_pt_demo(pt, cur):
	insert = "INSERT INTO " + PT_DEMO_TABLE_NM + "(" + MRN_FIELD_NM +", " + ", ".join(pt.attributeList.keys()) + ") "
	insert += "VALUES (" + "%s, "*len(pt.attributeList) + "%s)"


	list = ["".join(attr) for attr in pt.attributeList.values()]
	list.insert(0, pt.mrn)


	cur.execute(insert, list)

	return

if __name__ == "__main__":
	reader = init_csv_reader(get_filename())
	make_database(reader)
