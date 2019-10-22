import os
from os import path
import shutil
import re
import argparse

parser = argparse.ArgumentParser(description='Takes the zip file downloaded from moodle and uncompresses the submission directories named as student\'s roll numbers. You can also provide it a list of roll numbers and it will extract only those roll numbers. It extracts the roll number from SUBMISSION_NAME variable defined in the script')
parser.add_argument('-r', '--root', default='', help="the root directory. If it's supplied, all other paths are relative to this directory")
parser.add_argument('-s', '--all_subm', help="path to zip file downloaded by moodle, relative to root argument (if it's provided)")
# parser.add_argument('-s', '--all_subm', default='CS 251-2019-1-Inlab 4-84778.zip', help="path to zip file downloaded by moodle, relative to root argument (if it's provided)")
parser.add_argument('-l', '--roll_list', help='path of the list of roll numbers which need to be graded')
parser.add_argument('-e', '--extract_dir', help='place where all files will be extracted')
parser.add_argument('-a', '--grade_all', default="False", help="If True, it will extract all files, else, it will extract all files and populate roll_list")
parser.add_argument('--err', default='err.txt', help='it will write all the extraction errors in this file')
args = parser.parse_args()
# Variables
ALL_SUBMISSIONS = path.join(args.root, args.all_subm)
ROLL_LIST		= path.join(args.root, args.roll_list)
EXTRACT_DIR		= path.join(args.root, args.extract_dir)
SUBM_STAT		= path.join(args.root, 'submission_status.tsv')
ERR_LOG		= path.join(args.root, args.err)

# Name of submission archive
# Keep as generic as possible unless strictly specified beforehand
# ?: is for not capturing that bracket as a group
SUBMISSION_NAME = re.compile('(?:outlab4|outlab4)-(.+)\.(zip|tar\.gz|tgz|tar\.xz)', re.IGNORECASE)
# SUBMISSION_NAME = re.compile('(?:inlab4|inlab4)-([a-zA-Z0-9]+)\.(zip|tar\.gz|tgz|tar\.xz)', re.IGNORECASE)
# SUBMISSION_NAME = re.compile('(?:la2|lab2)-([a-zA-Z0-9]+)\.(zip|tar\.gz|tgz)', re.IGNORECASE)

grade_all = args.grade_all.lower() == 'true'
errlogfile = open(ERR_LOG, 'w')

def unpack_arch(filename, extract_dir='.'):
	try:
		shutil.unpack_archive(filename=filename, extract_dir=extract_dir)
	except shutil.ReadError:
		success = False
		for format_ in [x[0] for x in shutil.get_archive_formats()]:
			try:
				shutil.unpack_archive(filename=filename, extract_dir=extract_dir, format=format_)
				success = True
			except Exception:
				pass
			if success:
				break
		if not success:
			raise shutil.ReadError

if __name__ == '__main__':
	# Read roll numbers to grade
	if not grade_all:
		with open(ROLL_LIST, 'r') as f:
			temp = f.readlines()
			my_roll_numbers = [r.strip() for r in temp]
	else:
		rl_file = open(ROLL_LIST,'w')
		my_roll_numbers = []

	# Unpack submissions in EXTRACT_DIR
	unpack_arch(filename=ALL_SUBMISSIONS, extract_dir=EXTRACT_DIR)

	# Convert folder names to roll-no
	for stud_dir in os.listdir(EXTRACT_DIR):
		stud_dir_joined = path.join(EXTRACT_DIR, stud_dir)
		if not os.path.isdir(stud_dir_joined):
			errs = "{} is not a directory. ignoring!\n".format(stud_dir_joined)
			errlogfile.write(errs)
			print("\n{}".format(errs))
			continue
		for file in os.listdir(stud_dir_joined):
			m = SUBMISSION_NAME.match(file)
			if m is None:
				continue
			
			roll_no = m.group(1)
			
			if grade_all or roll_no in my_roll_numbers:
				if grade_all:
					try:
						rns = roll_no.strip()
						rl_file.write('{}\n'.format(rns))
					except Exception:
						print("\n"+"#"*20+"\n"+"theculpritis:\n{}\n".format(stud_dir))
						continue
				my_roll_numbers.append(roll_no.strip())
				try:
					unpack_arch(
						filename=path.join(stud_dir_joined, file),
						extract_dir=EXTRACT_DIR
					)
					shutil.move(
						src=path.join(EXTRACT_DIR, file.split('.')[0]),
						dst=path.join(EXTRACT_DIR, roll_no)
					)
					sucs = 'Name: %s,\tRoll no.: %s,\tSUCCESS in unpacking/moving' % \
				      (stud_dir.split('_')[0], roll_no)
					print('\r{}'.format(sucs), end='')
				except Exception as e:
					errs = 'Name: {},\tRoll no.: {},\tERROR in unpacking/moving. \t\t err: {}'\
						.format(stud_dir.split('_')[0], roll_no, e)
					errlogfile.write("{}\n".format(errs))
					print('\r{}'.format(errs), end='')
			break
		shutil.rmtree(stud_dir_joined)

	# Write submission status to TSV
	# By default assumes wrong submission name as no submission
	# In such a case, manually change this TSV later
	with open(SUBM_STAT, 'w') as f:
		f.write('ID\tWrong Submission\n')
		for r in my_roll_numbers:
			f.write('%s\t%d\n' % (r, 0))
errlogfile.close()

"""
python prepare_data.py -r ../../inlab4_grading -l roll_list.txt
"""
