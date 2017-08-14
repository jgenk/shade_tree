import database_setup
import sys

if __name__ == '__main__':
	print database_setup.make_database_csv(sys.argv[1])