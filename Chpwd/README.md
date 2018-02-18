# Chpwd
This is python script I wrote for changing the password of an Active Directory user without the need for AD UI. The
AD DC (Domain Controller) was Samba 4.1 on a Ubuntu server and uses kerberos protocol for authentication of users.

## Usage
To use this script, just invoke the script using the following command:

```bash
$ ./changePassword.sh
```

This will check for the dependencies required by the python script to execute and if they're not present then it'll
prompt you to install them and once successfully installed, it'll invoke the program automatically.

##### Note:
If you run the above command, it'll try to install the python packages globally. The recommended way to do it is use a
`virtualenv` for installing the dependencies.