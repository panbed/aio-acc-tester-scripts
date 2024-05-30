import sys
import os
import subprocess
from time import sleep
import json

print("Killing php (just in case!)")
phpKiller = subprocess.run(["killall", "php"])
if (phpKiller.returncode == 0):
	print("rip in peace php......")
else:
	print("php was already dead...")

if len(sys.argv) < 2:
	sys.exit("Usage: %s <path to folder with HTML files> [--dont-skip]" % sys.argv[0])

if len(sys.argv) == 3:
	if sys.argv[2] == "--dont-skip":
		print("⚠ Don't skip enabled!")
		dont_skip = True
else:
	dont_skip = False

def test_ibm(filename):
	print("⧗ Testing %s against IBM's Equal Access Checker..." % (filename))
	if os.path.isfile("output/ibm/localhost_8000/%s.json" % (filename)) and dont_skip == False:
		print("⚠ Found existing JSON output for %s! Skipping tests... (use --dont-skip if you want to bypass)" % (filename))
		return
	
	subprocess.run(["npx", "achecker", "--outputFormat", "json", "--outputFolder", "output/ibm", "http://localhost:8000/%s" % (filename)], stdout=subprocess.DEVNULL)
	print("✓ Done testing %s against IBM's Equal Access Checker!" % (filename))

def test_deque(filename):
	print("⧗ Testing %s against Deque's axe-core..." % (filename))
	if os.path.isfile("output/deque/%s.json" % (filename)) and dont_skip == False:
		print("⚠ Found existing JSON output for %s! Skipping tests... (use --dont-skip if you want to bypass)" % (filename))
		return
	
	subprocess.run(["npx", "axe", "-t", "wcag2a,wcag2aa,wcag21a,wcag21aa", "-d", "output/deque", "-s", "%s.json" % (filename), "--no-reporter", "http://localhost:8000/%s" % (filename)], stdout=subprocess.DEVNULL)
	# subprocess.run(["npx", "axe", "-d", "output/deque", "-s", "%s.json" % (filename), "--no-reporter", "http://localhost:8000/%s" % (filename)], stdout=subprocess.DEVNULL)
	print("✓ Done testing %s against Deque's axe-core!" % (filename))

def test_phpally(filename):
	print("⧗ Testing %s against Cidi Labs' PhpAlly..." % (filename))
	if os.path.isfile("output/phpally/%s.json" % (filename)) and dont_skip == False:
		print("⚠ Found existing JSON output for %s! Skipping tests... (use --dont-skip if you want to bypass)" % (filename))
		return
	
	subprocess.run(["php", "src/HtmlCheck.php", "http://localhost:8000/%s" % (filename)], cwd="phpally/", stdout=open("output/phpally/%s.json" % (filename), "w+"))
	print("✓ Done testing %s against Cidi Labs' PhpAlly!" % (filename))

# returns a dict with each pair in the form of "'{html_file_name}.html': {num}"
def compile_ibm_results(filenames):
	print("⧗ Compiling IBM's Equal Access Checker results...")
	results = dict.fromkeys(filenames)

	json_output_dir = "./output/ibm/localhost_8000"

	for json_filename in os.listdir(json_output_dir):
		if json_filename.endswith(".json"):
			json_data = json.load(open(os.path.join(json_output_dir, json_filename)))
			# im counting errors as either 'violation' 'potentialviolation', or 'recommendation'.
			# there's also 'potentialrecommendation' if you want that as well
			html_filename = os.path.splitext(json_filename)[0]
			total_errors = json_data["summary"]["counts"]["violation"] + json_data["summary"]["counts"]["potentialviolation"] + json_data["summary"]["counts"]["recommendation"]
			results[html_filename] = total_errors

	return results
	
def compile_deque_results(filenames):
	print("⧗ Compiling Deques's axe-core results...")
	results = dict.fromkeys(filenames)

	json_output_dir = "./output/deque/"

	for json_filename in os.listdir(json_output_dir):
		if json_filename.endswith(".json"):
			json_data = json.load(open(os.path.join(json_output_dir, json_filename)))
			html_filename = os.path.splitext(json_filename)[0]
			total_errors = len(json_data[0]["incomplete"]) + len(json_data[0]["violations"])
			results[html_filename] = total_errors

	return results

def compile_phpally_results(filenames):
	print("⧗ Compiling Cidi Labs' PhpAlly results...")
	results = dict.fromkeys(filenames)

	json_output_dir = "./output/phpally/"

	for json_filename in os.listdir(json_output_dir):
		if json_filename.endswith(".json"):
			json_data = json.load(open(os.path.join(json_output_dir, json_filename)))
			html_filename = os.path.splitext(json_filename)[0]
			total_errors = len(json_data["issues"])
			results[html_filename] = total_errors

	return results

def average(results):
	total_issues = 0
	for result in results:
		total_issues += results[result]

	return total_issues / len(results)

def results_printer(ibm, deque, phpally):
	# in theory they all should be the same length sooo
	results_length = len(ibm)
	for (k,v), (k2,v2), (k3,v3) in zip(ibm.items(), deque.items(), phpally.items()):
		print("%s:" % (k))
		print("IBM:\t%s" % (v))
		print("Deque:\t%s" % (v2))
		print("PhpA.:\t%s" % (v3))
		print()

# get directory from arg list
directory = sys.argv[1]

# create array that holds all the absolute file paths to the html files
html_file_paths = []
filenames = os.listdir(directory)

# start php server at localhost:8000 to serve all files, then wait a second just in case, lol
print('⧗ Starting PHP server at localhost:8000...')
php_server = subprocess.Popen(["php", "-S", "localhost:8000", "-t", directory])
sleep(1)

# ibm testing

for filename in filenames:
	test_ibm(filename)

# # axe-core testing
for filename in filenames:
	test_deque(filename)

# # phpally testing
for filename in filenames:
	test_phpally(filename)

ibm_results = compile_ibm_results(filenames)
print(ibm_results)

deque_results = compile_deque_results(filenames)
print(deque_results)

phpally_results = compile_phpally_results(filenames)
print(phpally_results)

results_printer(ibm_results, deque_results, phpally_results)

# cool printer thing lol
print("\n** We're just counting numbers here, please check the .json files to see if the issues caught actually make sense!!! **\n")
print("Statistics:")
print("Total files scanned:")
print("%d" % len(ibm_results))
print()
print("Averages:")
print("IBM:\t%.2f issues detected" % average(ibm_results))
print("Deque:\t%.2f issues detected" % average(deque_results))
print("PhpA.:\t%.2f issues detected" % average(phpally_results))

# sleep(5)
php_server.kill()

