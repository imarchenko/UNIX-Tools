#!/usr/bin/python
#
# Script to automatically download, build, and configure the nginx web server
#
# Written by Igor Marchenko <imarchen@gmail.com> on March 27, 2014
#

import os
import sys
import shutil
import subprocess
import urllib
import re

### Configuration ###

install_config = {
	# Define the package name
	'package': "nginx",

	# Define the version of nginx you would like to install
	'version': "1.4.7",

	# Define the port that you would like nginx to listen to
	'port': "8080",

	# Define the working directory for the build and installation
	'working_directory': os.path.join(os.environ['HOME'], "nginx")
}

#####################

def main():
	# Initialize the package
	packages = {
        'nginx': Nginx147Package()
	}

	# Run the pre-build tasks
	packages['nginx'].preBuild()

	# Compile the source code
	packages['nginx'].build()

	# Install the package
	packages['nginx'].install()

	# Run the post-installation tasks
	packages['nginx'].postInstall()

###

class InstallPackage:
	def __init__(self, name, version, file, url = None):
		self.name = name
		self.version = version
		self.workspace = install_config['working_directory']
		self.installPath = os.path.join(self.workspace, "build")
		self.depends = dict()

	# Function to create the workspace for downloading, building, and installing this package
	def createWorkspace(self):
		self.printMsg("creating workspace...")

		# Try to create the working directory
		if (not os.path.isdir(self.workspace)):
			try:
				os.makedirs(self.workspace)
			except Exception as inst:
				self.printErr("could not create the working directory '" + self.workspace + "'", inst)
		# Check that we can write to the working directory
		else:
			try:
				tmpFileName = "tmpFile"
				tmpFile = os.path.join(self.workspace, tmpFileName)
				f = open(tmpFile, 'w')
				f.close()
				os.remove(tmpFile)
			except Exception as inst:
				self.printErr("could not write to the working directory '" + self.workspace + "'", inst)
		
	# Function to check all dependencies for this package
	def checkDeps(self):
		self.printMsg("checking dependencies...")

		for key in self.depends:
			if (self.depends[key]['type'] == "executable"):
				if (not os.access(self.depends[key]['path'], os.X_OK)):
					self.printErr("dependency not a valid executable or may not exist '" + key + "'")
			elif (self.depends[key]['type'] == "file"):
				if (not os.access(self.depends[key]['path'], os.R_OK)):
					self.printErr("dependency not readable or may not exist '" + key + "'")


	# Function to download a file from a URL (using urllib)
	def getData(self, file, url):
		file_basename = os.path.basename(file)

		# Check if file exists
		if (not os.path.exists(file)):
			if (url == None):
				self.printErr("could not download '" + file_basename + "' because no URL was provided")
			else:
				try:
					self.printMsg("started downloading file '" + file_basename + "'")
					urllib.urlretrieve(url, file, self.getWatch)
					self.printMsg("finished downloading file '" + file_basename + "'")
				except Exception as inst:
					self.printErr("could not download the file '" + file_basename + "'", inst)

	# Function to watch the progress of a download (supports urllib.urlretrieve)
	def getWatch(self, blocks, blockSize, totalSize):
		# Only show download status every 25%
		p = (float(blocks * blockSize) / totalSize)
		if ((round(p, 2) % .25) == 0):
			self.printMsg("downloading file... (" + str(blocks * blockSize) + " / " + str(totalSize) + " bytes)")

	# Function to perform the pre-build process
	def preBuild(self):
		if (os.path.exists(self.installPath)):
			try:
				os.removedirs(self.installPath)
			except Exception as inst:
				self.printErr("exiting installation because '" + self.installPath + "' is not empty. This may mean that a previous installation has been successful.", inst)

		self.clean()
		self.createWorkspace()

		# Download any files that need to be downloaded
		for key in self.depends:
			if (self.depends[key]['url'] != None):
				self.getData(self.depends[key]['path'], self.depends[key]['url'])

		self.checkDeps()

	# Function to perform the build process (compiling and linking)
	def build(self):
		return None

	# Function to perform the installation process
	def install(self, path = None):
		return None

	# Function to clean-up the workspace
	def clean(self):
		if (os.path.exists(self.workspace)):
			self.printMsg("removing old workspace")
			shutil.rmtree(self.workspace)

	# Function perform any post-installation tasks (such as cleanup)
	def postInstall(self):
		return None

	# Function to print a message to STDOUT
	def printMsg(self, msg):
		print "Package Installer [" + self.name + "]: " + msg

	# Function to print an error message to STDOUT
	def printErr(self, msg, e = None):
		print "Package Installer [" + self.name + "]: " + msg
		if (e != None):
			print e
		sys.exit(-1)

	# Function that determines the full path of a command
	def which(self, file):
		for path in os.environ["PATH"].split(":"):
			p = os.path.join(path, file)
			if os.path.exists(p):
				return p

		return ""

###

class Nginx147Package(InstallPackage):
	def __init__(self):
		self.name = "nginx"
		self.version = "1.4.7"
		self.workspace = install_config['working_directory']
		self.installPath = os.path.join(self.workspace, 'httpd')
		self.depends = {
			'tar': {
				'type': "executable",
				'file': "tar",
				'path': self.which("tar"),
				'url': None
			},
			'make': {
				'type': "executable",
				'file': "make",
				'path': self.which("make"),
				'url': None
			},
			'g++': {
				'type': "executable",
				'file': "g++",
				'path': self.which("g++"),
				'url': None
			},
			'source': {
				'type': "file",
				'file': "nginx-1.4.7.tar.gz",
				'path': os.path.join(self.workspace, "nginx-1.4.7.tar.gz"),
				'url': "http://nginx.org/download/nginx-1.4.7.tar.gz"
			},
			'data': {
				'type': "file",
				'file': "index.html",
				'path': os.path.join(self.workspace, "index.html"),
				'url': "http://www.wikihow.com/images/sampledocs/7/Simple-Webpage.txt"
			}
		}

	def build(self):
		tar=self.depends['tar']['path']
		make=self.depends['make']['path']

		os.chdir(self.workspace)

		# Extract the tar.gz file
		self.printMsg("extracting '" + os.path.basename(self.depends['source']['path']) + "'")
		try:
			FNULL = open(os.devnull, 'w')
			subprocess.check_call([tar, "zxvf", self.depends['source']['path']], stdout=FNULL, stderr=subprocess.STDOUT)
			FNULL.close()
		except subprocess.CalledProcessError as inst:
			self.printErr("problem extracting '" + self.depends['source']['path'] + "'", inst)

		# Change to the extracted directory
		os.chdir(os.path.join(self.workspace, os.path.splitext(os.path.splitext(os.path.basename(self.depends['source']['path']))[0])[0]))

		# Run configure script
		self.printMsg("running configure script")
		try:
			FNULL = open(os.devnull, 'w')
			subprocess.check_call([os.path.join(os.getcwd(), "configure"), "--without-mail_smtp_module", "--without-mail_imap_module", "--without-mail_pop3_module", "--without-http_rewrite_module", "--without-http_gzip_module"], stdout=FNULL, stderr=subprocess.STDOUT)
			FNULL.close()
		except subprocess.CalledProcessError as inst:
			self.printErr("problem running configure script", inst)

		# Execute the build proces
		self.printMsg("building the package (this may take awhile)...")
		try:
			FNULL = open(os.devnull, 'w')
			subprocess.check_call(make, stdout=FNULL, stderr=subprocess.STDOUT)
			FNULL.close()
		except subprocess.CalledProcessError as inst:
			self.printErr("problem during the source code build", inst)

	# Function to install the package on the system
	# By default, this installs to the workspace/httpd directory
	def install(self, path = None):
		make=self.depends['make']['path']

		if (path != None):
			self.installPath = path

		self.printMsg("installing the package to '" + self.installPath + "'")
		installCmd = [make, "DESTDIR=" + self.installPath, "install"]

		# Create the installation directory if it does not exist
		if (not os.path.exists(self.installPath)):
			try:
				os.makedirs(self.installPath)
			except Exception as inst:
				self.printErr("could not create the installation directory '" + self.installPath + "'", inst)

		# Change to the extracted directory
		os.chdir(os.path.join(self.workspace, os.path.splitext(os.path.splitext(os.path.basename(self.depends['source']['path']))[0])[0]))

		# Execute the installation process
		try:
			FNULL = open(os.devnull, 'w')
			subprocess.check_call(installCmd, stdout=FNULL, stderr=subprocess.STDOUT)
			FNULL.close()
		except subprocess.CalledProcessError as inst:
			self.printErr("problem during the installation", inst)

		self.printMsg("finished the installation to '" + self.installPath + "'")

	# Function to run post-installation activities, such as software configuration and importing data files
	def postInstall(self):
		self.printMsg("running post-installation tasks...")
		
		# Move the data file to the correct directory
		destPath = os.path.join(self.installPath, "usr/local/nginx/html")
		try:
			os.rename(self.depends['data']['path'], os.path.join(destPath, self.depends['data']['file']))
		except Exception as inst:
			self.printErr("could not move file '" + self.depends['data']['path'] + "' to " + destPath, inst)

		# Modify the configuration file to run the server on the correct port
		confFile = os.path.join(self.installPath, "usr/local/nginx/conf/nginx.conf")
		reListenLine = re.compile("^\s*listen\s+80;$")

		fr = open(confFile, 'r')
		fw = open(confFile + '.new', 'w')

		for line in fr:
			if (reListenLine.match(line)):
				fw.write(re.sub("80", install_config['port'], line))
			else:
				fw.write(line)

		fr.close()
		fw.close()

		# Overwrite the old configuration file with the new one
		try:
			os.rename(confFile + ".new", confFile)
		except Exception as inst:
			self.printErr("could not overwrite the old nginx configuration file", inst)

		self.printMsg("package installation and configuration is complete")
		self.printMsg("nginx can be executed by running '" + os.path.join(self.installPath, "usr/local/nginx/sbin/nginx") + " -c " + os.path.join(self.installPath, "usr/local/nginx/conf/nginx.conf") + " -p " + os.path.join(self.installPath, "usr/local/nginx") + "' from the command line")


if __name__ == "__main__":
    main()

