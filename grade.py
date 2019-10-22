"""
Autograding script. 
- Should be run from the evaluation directory. 
- All statistics will be dumped there.
python grade.py -r ../../inlab4_grading -l roll_list.txt -e inlab4 -o question
"""

import os
from os import path
import shutil
import subprocess
import glob
import argparse

parser = argparse.ArgumentParser(description="The autograder! Fill the values in the script and run! It will run all scripts from current directory. So, copy all your autograding script(s) and testcases into the current directory before running it. I know, it needs some work :'(")
parser.add_argument('-r', '--root', default='')
parser.add_argument('-l', '--roll_list', default='roll_list.tsv', help='list of students to grade')
parser.add_argument('-m', '--marks', default='marks.tsv', help='marks of students')
parser.add_argument('-e', '--extract_dir', default='inlab4', help='locations of student submissions')
parser.add_argument('-o', '--order', default='student', help='order or grading. one of: "student" or "question"')
args = parser.parse_args()

ROLL_LIST = path.join(args.root, args.roll_list)    # List of students to grade
SRC_DIR   = path.join(args.root, args.extract_dir)  # Locations of student submissions

###############################################################################
#                          Question specific details                          #
###############################################################################

# Name of the question(s) to be evaluated
# QUESTIONS = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
QUESTIONS = ['Q2', 'Q4', 'Q4_last', 'Q5']

# check mask. If it's false, then the corresponding question won't be checked
MASK = [True, True, False, False]

# Name of file(s) to be copied from the students directory to ours for 
# evaluation. Should be a list of strings for each question. Wildcard (*)
# entries supported. Eg. '*.pdf', '*.txt', etc.
#
# CAUTION: Don't use wildcard for the extensions of files important for testing
#          Example, *.py. This is because an intermediate _remove_files step 
#          will delete all files matching the wildcard, that might include some
#          important files too.
#
# examples: 
# FILES = [['inlab4_tasks.py'] for _ in range(5)]
FILES = [['task2/utils.py', 'task2/task2.py'], ['task4/task4.py', 'task4/driver.py'], ['task4/task4.py', 'task4/driver.py'], ['task5/task5.py']]

# Name of file(s) to be copied from ours to students directory for manual
# evaluation. Should be a list of strings for each question. Wildcard (*)
# entries supported. Eg. '*.pdf', '*.txt', etc.
BACK_FILES = [[], [], ['clean_sin.png', 'dirty_sin.png', 'cleaned_sin.png'], ['instance{}.png'.format(i) for i in range(1, 4)]]

# destinations of the files back to students' directory
BACK_FILES_DEST = ['', '', 'task4', 'task5']

# Commmand to be executed, one for each question. The command should terminate 
# after printing just the marks obtained, if AUTOGRADE = True for that question.
# examples: 
# COMMANDS = ['python autograder_task2.py', 'python autograder_task4.py']
COMMANDS = ['python autograder_t24.py --task {} --tcdir testcases --mass_grade True'.format(i) for i in [2,4]] + ['python auto24/t24_man_ag.py', 'python ag_t5.py']

# Locations of autograders and related files. Student's files will be copied to
# these locations and then commands will be executed
LOCATIONS = ['auto24', 'auto24', 'auto24', 'auto5']

# Whether to automatically grade the question, or prompt the examiner to enter 
# marks manually.
AUTOGRADE = [True, True, False, False]

# Allowed imports for the files. Should be a list of the same length as FILES, 
# with elements as list of list of allowed imports for those questions' files.
# ALLOWED_IMPORTS = [[['import numpy as np']], [[]]]

# Whether to do question-wise (useful for automatic evaluation) or student-wise
# (useful for manual evaluation)
ORDER = args.order # 'student'

###############################################################################
############################ DO NOT EDIT BELOW ################################
###############################################################################

# Check that arguments above are filled correctly.
assert len(QUESTIONS) == len(FILES)
assert len(QUESTIONS) == len(COMMANDS)
assert len(QUESTIONS) == len(AUTOGRADE)
assert ORDER in ['question', 'student'], ("${}#".format(ORDER), ORDER == 'question')

###############################################################################
#                             Helper functions                                #
###############################################################################

def _change_prefix(files_, prefix=''):
	return [os.path.join(prefix, os.path.basename(file_)) for file_ in files_]

def _execute(command, autograde=True, wd=None):
	try:
		# print ("wd: ", wd)
		# print ("command:", command)
		result = subprocess.run(
			command,
			shell=True,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			cwd=wd)
		if result.returncode == 0 and autograde:
			# print('#'*40)
			# print("marks: {}".format(result.stdout.decode('utf-8')))
			# print("result", result)
			# print('#'*40)
			return float(result.stdout.decode('utf-8')), 'NA'
		elif result.returncode == 0 and not autograde:
			return 0., 'NA'
		else:
			return 0., result.stderr.decode('utf-8').strip().split('\n')[-1]
	except Exception:
		return 0., 'execution error'

def _copy_files(src_dir, dest_dir, files):
	try:
		for f in files:
			for f_ in glob.glob(os.path.join(src_dir, f)):
				try:
					shutil.copy(f_, dest_dir)
					# print("copied {} to {}".format(f_, dest_dir))
				except Exception:
					continue
		return True
	except Exception:
		return False

def _remove_files(files):
	try:
		# input(" delete files: {}".format(files))
		for f in files:
			for f_ in glob.glob(f):
				os.remove(f_)
		# 		print("removed {}".format(f_))
		# # print("\ncwd: ", os.getcwd())
		# input(" files: {}\tproceed?".format(files))
		return True
	except Exception:
		return False

###############################################################################
#                                Start grading                                #
###############################################################################

if __name__ == '__main__':
	# Read roll numbers to grade
	with open(ROLL_LIST, 'r', encoding='utf-8') as f:
		my_roll_numbers = f.read().split('\n')
	print("total teams: {}".format(len(my_roll_numbers)))
	# Placeholder for question statistics
	qstats = {}
	for r in my_roll_numbers:
		qstats[r] = {}
		for q in QUESTIONS:
			qstats[r][q] = {'marks': 0, 'comments': 'NA'}

	# Evaluate
	if ORDER == 'question':
		for i, q in enumerate(QUESTIONS):
			if MASK[i] is False:
				continue
			for r in os.listdir(SRC_DIR):
				if r not in qstats:
					continue
				evaluate = True
				# print("r: ", r)

				if not _copy_files(os.path.join(SRC_DIR, r), LOCATIONS[i], FILES[i]):
				# if not _copy_files(os.path.join(SRC_DIR, r), '.', FILES[i]):
					qstats[r][q]['comments'] = 'file(s) missing'
					evaluate = False
					continue

				if evaluate:
					m, c = _execute(COMMANDS[i], AUTOGRADE[i], LOCATIONS[i])
					_copy_files(LOCATIONS[i], os.path.join(SRC_DIR, r, BACK_FILES_DEST[i]), BACK_FILES[i])
					print("{}:{} checked".format(r, q))
					if AUTOGRADE[i]:
						qstats[r][q]['marks'] = m
						qstats[r][q]['comments'] = c
					else:
						if c != 'NA':
							print('Error: %s' % c)
						print('Enter marks for [%s][%s]: ' % (r, q), end='')
						qstats[r][q]['marks'] = float(input())
						print('Enter comments for [%s][%s]: ' % (r, q), end='')
						qstats[r][q]['comments'] = input()
				_remove_files(_change_prefix(FILES[i], prefix=LOCATIONS[i]))
				_remove_files([os.path.join(LOCATIONS[i], bf) for bf in BACK_FILES[i]])
	else:
		for r in os.listdir(SRC_DIR):
			if r not in qstats:
				continue
			# print("r: ", r)
			for i, q in enumerate(QUESTIONS):
				if MASK[i] is False:
					continue
				evaluate = True

				if not _copy_files(os.path.join(SRC_DIR, r), LOCATIONS[i], FILES[i]):
				# if not _copy_files(os.path.join(SRC_DIR, r), '.', FILES[i]):
					qstats[r][q]['comments'] = 'file(s) missing'
					evaluate = False
					break

				if evaluate:
					m, c = _execute(COMMANDS[i], AUTOGRADE[i])
					_copy_files(LOCATIONS[i], os.path.join(SRC_DIR, r, BACK_FILES_DEST[i]), BACK_FILES[i])
					print("\r{}:{} checked".format(r, q), end='')
					if AUTOGRADE[i]:
						qstats[r][q]['marks'] = m
						qstats[r][q]['comments'] = c
					else:
						if c != 'NA':
							print('Error: %s' % c)
						print('Enter marks for [%s][%s]: ' % (r, q), end='')
						qstats[r][q]['marks'] = float(input())
						print('Enter comments for [%s][%s]: ' % (r, q), end='')
						qstats[r][q]['comments'] = input()
					_remove_files(_change_prefix(FILES[i], prefix=LOCATIONS[i]))
					_remove_files([os.path.join(LOCATIONS[i], bf) for bf in BACK_FILES[i]])

	# Dump results to a tsv file
	with open(args.marks, 'w', encoding='utf-8') as f:
		header = ['ID']
		# header += QUESTIONS
		header += [q for q, q_mask in zip(QUESTIONS, MASK) if q_mask]
		header += ['Comments']
		f.write('\t'.join(header) + '\n')
		
		for r in my_roll_numbers:
			line = [r]
			line += [str(qstats[r][q]['marks']) for qidx, q in enumerate(QUESTIONS) if MASK[qidx]]
			line += [', '.join([qstats[r][q]['comments']  for qidx, q in enumerate(QUESTIONS) if MASK[qidx]])]
			f.write('\t'.join(line) + '\n')
