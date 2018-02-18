#!/usr/bin/env python

import getpass
import signal
import socket
import string
import sys
import time
from base64 import b64decode

import pexpect

__author__ = 'Bharath Srinivas'
created_on = '24/11/2016'


def is_yes():
    return change_password(username)


def is_no():
    return 'Bye.'


def default():
    return 'Please enter either Y or N.'


options = {
    'y': is_yes,
    '': is_yes,
    'n': is_no,
    'default': default,
}


def old_pass():
    old_password = None

    valid = False
    while not valid:
        old_password = getpass.getpass('Please enter your current password: ')
        if old_password is '':
            print '\nNo input received.'
        else:
            valid = True
    return old_password


def new_pass(user_name):
    new_password = None

    is_complex = False
    lowers = string.ascii_lowercase
    uppers = string.ascii_uppercase
    digits = string.digits
    specials = string.punctuation
    while not is_complex:
        new_password = getpass.getpass('Please enter the new password for {}: '.format(user_name))
        if new_password is '':
            print '\nNo input received.'
        elif len(set(lowers).intersection(new_password) and set(uppers).intersection(new_password) and
                 set(digits).intersection(new_password) and set(specials).intersection(new_password)) < 1:
            print '\nYour new password is not complex enough. Please try again.'
        elif len(new_password) > 15 or len(new_password) < 8:
            print '\nYour new password should not be less than 8 characters and not more than 15 characters in length.'
        else:
            is_complex = True
    return new_password


def change_password(user_name):
    old_password = old_pass()
    print '\nPlease wait while we login to the server...'
    time.sleep(2)

    user = 'user'
    host = 'host'
    password = 'bWFnaWNzM3J2M3I='

    ssh = pexpect.spawn('ssh {}@{}'.format(user, host))
    try:
        ssh.expect('user.*: ')
    except:
        return '\nProcess timed out while waiting for the password prompt. Please check your internet connection ' \
               'or the server.'
    ssh.sendline(b64decode(password))
    login = ssh.expect(['dc1.* ', pexpect.TIMEOUT])
    if login is 0:
        print '\nChecking whether the password of {} has expired. Please wait...'.format(user_name)
        time.sleep(2)
        ssh.sendline('kinit {}'.format(user_name))
        pre = ssh.expect(['Password.* ', 'not found.* '])
        if pre is 0:
            ssh.sendline(old_password)
        if pre is 1:
            ssh.sendline('exit')
            return '\nThe user does not exist in the domain. Please check the username you entered.'
    if login is 1:
        ssh.close()
        return '\nLogin process has timed out. Please try again.'

    r = ssh.expect([pexpect.TIMEOUT, 'kinit:.* ', 'Password.* ', 'Warning.* ', 'dc1.* '])

    if r is 0:
        ssh.close()
        return '\nProcess failed due to timeout while checking the expiry status.'

    if r is 1:
        ssh.sendline('exit')
        return '\nProcess failed due to wrong password.'

    if r is 2:
        print '\nIt seems your password has expired.'
        new_password = new_pass(user_name)

        is_same = True
        while is_same:
            if new_password == old_password:
                print 'Your new password should not be the same as the old one.'
            else:
                is_same = False

        try:
            ssh.expect('Enter.* ')
            ssh.sendline(new_password)
        except:
            return False
        try:
            ssh.expect('again.* ')
            ssh.sendline(new_password)
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
            return '\nAn error occurred while changing the password.'

    if r is 3:
        ssh.sendline('exit')
        return '\nPassword unchanged as your password did not expire.'

    if r is 4:
        ssh.sendline('exit')
        return '\nIt might be possible that this user is a god as his password is immortal.'


def signal_handler(signal, handler):
    print '\nYou pressed Ctrl+C!'
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    try:
        answer = None
        username = None

        is_valid = False
        is_invalid = True

        invalid_chars = set(string.punctuation.replace(".", ""))

        while not is_valid:
            username = raw_input('Please enter the username: ').lower()
            if username == '':
                print '\nNo input received.'
            elif any(unicode(char).isnumeric() for char in username) or any(char in invalid_chars for char in username):
                print '\nPlease enter a valid name.'
            elif len(username) < 3:
                print '\nPlease enter valid number of input.'
            else:
                is_valid = True

        print 'The entered username is: ' + username

        while is_invalid:
            print 'Is this correct? [Y/n]'
            answer = raw_input().lower()
            if answer not in 'y n':
                print options['default']()
            else:
                is_invalid = False

        print options[answer]()
    except (socket.error, EOFError):
        print '\nYou pressed Ctrl+D!'
        sys.exit(0)
