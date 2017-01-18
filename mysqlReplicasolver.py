#!/usr/bin/env python

Author = 'Bharath Srinivas'
CreatedOn = '30/11/2016'

import MySQLdb, smtplib, socket
from itertools import izip
from base64 import b64decode

class ReplicaSolver(object): 
	def __init__(self):
		self.sysID = socket.gethostname()
		self.host = 'localhost'
		self.user = 'user'
		self.db = 'db'
		self.conn = MySQLdb.Connection(db=self.db, host=self.host, user=self.user)
		self.mysql = self.conn.cursor()

	def getReplicationStatus(self):
		query = 'SHOW SLAVE STATUS'
		self.mysql.execute(query)
		status = self.mysql.fetchone()
		heading = [desc[0] for desc in self.mysql.description] 
		return dict(izip(heading, status))

	def checkCurrStatus(self):
		try:
			result = self.getReplicationStatus()
		except Exception, e:
			error = {'Slave_Connection_Error' : e}
			return None, error

		slave_io_state = result['Slave_IO_Running']
		slave_sql_state = result['Slave_SQL_Running']
		last_sql_errno = result['Last_SQL_Errno']
		last_sql_err = result['Last_SQL_Error']
		secs_behind_master = result['Seconds_Behind_Master']

		if slave_sql_state == 'No':
			if last_sql_errno == 1062:
				return self.dupEntryError()
		else:
			return self.sendMail(False)
	
	def dupEntryError(self):
		isError = True
		while isError:
			self.mysql.execute('stop slave')
			self.mysql.execute('set global sql_slave_skip_counter=1')
			self.mysql.execute('start slave')
			getStatus = self.getReplicationStatus()
			if (getStatus['Slave_IO_Running'] and getStatus['Slave_SQL_Running']) is 'Yes':
				self.mysql.execute('stop slave')
				self.mysql.execute('set global sql_slave_skip_counter=0')
				self.mysql.execute('start slave')
				isError = False
		return self.sendMail('Duplicate Entry Issue', isError)

	def sendMail(self, *args):
		inputs = []
		for arg in args:
			inputs.append(arg)
		gmailUsr = b64decode('dXNlcg==')
		gmailPwd = b64decode('cGFzc3dvcmQ=')
		sender = gmailUsr
		receivers = gmailUsr
		
		if len(inputs) is 2:	
			if inputs[1] == False:
				message = """From: {}
				To: {}
				Subject: The {} has been resolved on host {}.

				Hi Bharath,

				The {} has been resolved and the replication is working without any issue now.

				""".format(sender, receivers, inputs[0], self.sysID, inputs[0])

			elif inputs[1] == True:
				message = """From: {}
				To: {}
				Subject: Couldn\'t resolve the {} on host {}.

				Hi Bharath,

				Couldn't solve the {} and it needs your attention.

				""".format(sender, receivers, inputs[0], self.sysID, inputs[0])

		else:
			message = """From: {}
			To: {}
			Subject: No replication issue on host {}.

			Hi Bharath,

			There's no issue and everything's working fine as it should be.

			""".format(sender, receivers, self.sysID)
	
		try:
			mailServer = smtplib.SMTP('smtp.gmail.com:587')
			mailServer.ehlo()
			mailServer.starttls()
			mailServer.login(gmailUsr, gmailPwd)
			mailServer.sendmail(sender, receivers, message)
			mailServer.quit()
			print 'The email has been sent successfully.'
		except SMTPException:
			print 'Error: unable to send mail.'

if __name__ == '__main__':
	handler = ReplicaSolver()
	handler.checkCurrStatus()
