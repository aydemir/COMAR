#!/usr/bin/python
# -*- coding: utf-8 -*-

import popen2
import os


class dialup:
	""" Dialup client functions for Hayes compatible modems, using pppd """

	tmpl_chat = """
TIMEOUT         5
ABORT           '\\nBUSY\\r'
ABORT           '\\nNO ANSWER\\r'
ABORT           '\\nNO CARRIER\\r'
ABORT           '\\nNO DIALTONE\\r'
ABORT           '\\nAccess denied\\r'
ABORT           '\\nInvalid\\r'
ABORT           '\\nVOICE\\r'
ABORT           '\\nRINGING\\r\\n\\r\\nRINGING\\r'
''              \\rAT
'OK-+++\c-OK'   ATH0
TIMEOUT         30
OK              ATDT%s
CONNECT         ''
"""
	
	tmpl_options = """
lock
modem
crtscts
noipdefault
defaultroute
noauth
usehostname
usepeerdns
user %s
"""

	def silentUnlink(self, path):
		""" Try to unlink a file, if exists """

		try:
			os.unlink(path)
		except:
			pass

	def capture(self, cmd):
		""" Run a command and capture the output """

		out = []
		a = popen2.Popen4(cmd)
		while 1:
			b = a.fromchild.readline()
			if b == None or b == "":
				break
			out.append(b)
		return (a.wait(), out)

	def sendCmd(self, cmd, dev):
		""" Send commands to dev """

		return result

	def isModem(self, dev):
		""" Check if dev is a modem """
		
		return True

	def getDNS(self):
		""" Try to get DNS server adress provided by remote peer """
		list = []

		try:
		    f = file("/etc/ppp/resolv.conf", "r")
		    for line in f.readlines():
		        if line.strip().startswith("nameserver"):
		            list.append(line[line.find("nameserver") + 10:].rstrip('\n').strip())
		    f.close()
		except IOError:
		    return None

		return list

	def createOptions(self, dev, user):
		""" Create options file for the desired device """

		self.silentUnlink("/etc/ppp/options." + dev)
		try:
			f = open("/etc/ppp/options." + dev, "w")
			f.write(self.tmpl_options % user)
			f.close()
		except:
			return True

		return None

	def createChatscript(self, dev, phone):
		""" Create a script to have a chat with the modem in the frame of respect and love """

		self.silentUnlink("/etc/ppp/chatscript." + dev)
		try:
			f = open("/etc/ppp/chatscript." + dev, "w")
			f.write(self.tmpl_chat % phone)
			f.close()
		except:
			return True

		return None


	def createSecrets(self, user, pwd):
		""" Create authentication files """

		try:
			# Ugly way to clean up secrets and recreate
			self.silentUnlink("/etc/ppp/pap-secrets")
			self.silentUnlink("/etc/ppp/chap-secrets")
			f = os.open("/etc/ppp/pap-secrets", os.O_CREAT, 0600)
			os.close(f)
			os.symlink("/etc/ppp/pap-secrets", "/etc/ppp/chap-secrets")
		except:
			return True
			
		f = open("/etc/ppp/pap-secrets", "w")
		data = "\"%s\" * \"%s\"\n" %(user, pwd)
		f.write(data)
		f.close()

		return None

	def runPPPD(self, dev):
		""" Run the PPP daemon """

		cmd = "/usr/sbin/pppd 115200 " + dev + " connect '/usr/sbin/chat -V -v -f /etc/ppp/chatscript." + dev + "'"
		i, output = self.capture(cmd)
		return output

	def dial(self, phone, user, pwd, dev = "modem"):
		""" Dial a server and try to login """
		
		if self.createSecrets(user, pwd) is True:
			return "Could not manage authentication files"

		if self.createOptions(dev, user) is True:
			return "Could not manage pppd parameters"

		if self.createChatscript(dev, phone) is True:
			return "Could not manage chat script"

		output = self.runPPPD(dev)
		return output

if __name__ == "__main__":
	dup = dialup()
	print dup.dial("145", "tatu@ttnet", "welovetox", "ttySHSF0")
