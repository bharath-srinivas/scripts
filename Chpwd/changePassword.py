#!/usr/bin/env python

author = 'Bharath'
CreatedOn = '24/11/2016'

import sys, time, string, getpass
import signal, socket
import pexpect
from base64 import b64decode


def isYes():
	return changePassword(username)

def isNo():
	return 'Bye.'

def default():
	return 'Please enter either Y or N.'

options = {
	'y': isYes,
	'': isYes,
	'n': isNo,	
	'def': default,
	}

def changePassword(username):
	oldpass = oldPass()
	print '\nPlease wait while we login to the server...'
	time.sleep(2)

	user = 'user'
	host = 'host'
	password = 'bWFnaWNzM3J2M3I='

	ssh = pexpect.spawn('ssh {}@{}'.format(user, host))
	try:
		ssh.expect('user.*: ')
	except:
		return '\nProcess timedout while waiting for the password prompt. Please check your internet connection or the server.'
	ssh.sendline(b64decode(password))
	login = ssh.expect(['dc1.* ', pexpect.TIMEOUT])
	if login is 0:
		print '\nChecking whether the password of {} has expired. Please wait...'.format(username)
		time.sleep(2)
		ssh.sendline('kinit {}'.format(username))
		pre = ssh.expect(['Password.* ', 'not found.* '])
		if pre is 0:
			ssh.sendline(oldpass)
		if pre is 1:
			ssh.sendline('exit')
			return '\nThe user does not exist in the domain. Please check the username you entered.'
	if login is 1:
		ssh.close()
		return '\nLogin process has timedout. Please try again.'	

	r = ssh.expect([pexpect.TIMEOUT, 'kinit:.* ', 'Password.* ', 'Warning.* ', 'dc1.* '])

	if r is 0:
		ssh.close()
		return '\nProcess failed due to timeout while checking the expiry status.'

	if r is 1:
		ssh.sendline('exit')
		return '\nProcess failed due to wrong password.'

	if r is 2:
		print '\nIt seems your password has expired.'
		newpass = newPass(username)

		isSame = True
		while isSame:
			if newpass == oldpass:
				print 'Your new password shouldn\'t be the same as the old one.'
			else:
				isSame = False

		try:		
			ssh.expect('Enter.* ') 
			ssh.sendline(newpass)
		except:
			return False
		try:
			ssh.expect('again.* ')
			ssh.sendline(newpass)
		except:
			return False

		post = ssh.expect(['Warning.* ', pexpect.TIMEOUT])
		
		if post is 0:
			ssh.sendline('exit')
			return '\nPassword has been successfully changed.'
		if post is 1:
			ssh.close()
			return '\nProcess has timed out while changing password.'
		else:
			ssh.sendline('exit')
			return '\nAn error occured while changing the password.'

	if r is 3:
		ssh.sendline('exit')
		return '\nPassword unchanged as your password didn\'t expire.'

	if r is 4:
		ssh.sendline('exit')
		return '\nIt might be possible that this user is a god as his password is immortal.'

def signalHandler(signal, handler):
	print '\nYou pressed Ctrl+C!'
	sys.exit(0)

def oldPass():
	Valid = False
	while not Valid:
		oldPassword = getpass.getpass('Please enter your current password: ')
		if oldPassword is '':
			print '\nNo input received.'
		else:
			Valid = True
	return oldPassword

def newPass(username):
	Complex = False
	lowers = string.ascii_lowercase
	uppers = string.ascii_uppercase
	digits = string.digits
	specials = string.punctuation
	while not Complex:
		newPassword = getpass.getpass('Please enter the new password for {}: '.format(username))
		if newPassword is '':
			print '\nNo input received.'
		elif len(set(lowers).intersection(newPassword) and set(uppers).intersection(newPassword) and set(digits).intersection(newPassword) and set(specials).intersection(newPassword)) < 1:
			print '\nYour new password is not complex enough. Please try again.'
		elif len(newPassword) > 15 or len(newPassword) < 8:
			print '\nYour new password shouldn\'t be less than 8 characters and not more than 15 characters in length.'
		else:
			Complex = True
	return newPassword

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signalHandler)
	try:
		isValid = False
		isInvalid = True

		invalidChars = set(string.punctuation.replace(".", ""))

		while not isValid:	
			username = raw_input('Please enter the username: ').lower()
			if username == '':
				print '\nNo input received.'		
			elif any(unicode(char).isnumeric() for char in username) or any(char in invalidChars for char in username):
				print '\nPlease enter a valid name.'
			elif len(username) < 3:
				print  '\nPlease enter valid number of input.'
			else:
				isValid = True

		print 'The entered username is: ' + username

		while isInvalid:
			print 'Is this correct? [Y/n]'
			answer = raw_input().lower()
			if answer not in 'y n':
				print options['def']()
			else:
				isInvalid = False

		print options[answer]()
	except (socket.error, EOFError):
		print '\nYou pressed Ctrl+D!'
		sys.exit(0)
