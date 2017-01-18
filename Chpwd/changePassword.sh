#Created by Bharath Srinivas on 28/11/2016

#!/bin/bash -e

export PYDEPENDENCY="$(python -c 'import pexpect' | wc -l)"
export PIPDEPENDENCY="$(which pip | wc -l)"
export PROGRAM="python changePassword.py"

export isSuccess=false

function checkDep() {
	isDone=false
	while ! $isDone; do
		if [[ $PYDEPENDENCY -eq 0 && $PIPDEPENDENCY -gt 0 ]]; then
			echo "Your system has all the dependencies installed to run this program."
			sleep 2
			echo "Now executing the program. Please wait..."
			sleep 2
			$PROGRAM
			isDone=true
			isSuccess=true

		elif [[ $PIPDEPENDENCY -gt 0 && $PYDEPENDENCY -gt 0 ]]; then
			echo "Your system is missing a required dependency. Do you want to install it now[Y/n]? "
			read choice
			if [[ ${choice,,} == "y" || $choice == '' ]]; then
				sudo pip install pexpect;
				sleep 2
				echo "The dependency has been successfully installed. Now executing the program..."
				sleep 2
				$PROGRAM
				isDone=true
				isSuccess=true
			elif [ ${choice,,} == 'n' ]; then
				echo "You've chosen not to install the dependencies which will make this program not executable in your system."
				isSuccess=false
				exit
			else
				echo "Please enter either Y or N."
			fi

		else
			echo "Your system doesn't have the required dependencies installed. Do you want to install them now[Y/n]? "
			read choice1
			if [[ ${choice1,,} == 'y' || $choice == '' ]]; then
				sudo apt-get install python-pip && sudo pip install pexpect;
				sleep 2
				echo "The dependencies has been successfully installed. Now executing the program..."
				sleep 2
				$PROGRAM
				isDone=true
				isSuccess=true
			elif [ ${choice1,,} == 'n' ]; then
				echo "You've chosen not to install the dependencies which will make this program not executable in your system."
				isSuccess=false
				exit
			else
				echo "Please enter either Y or N."
			fi
		fi
	done
}

function result() {
	if [ $isSuccess == true ]; then
		:
	else
		echo "The execution of the program has been stopped because of missing dependencies."
	fi
}

echo "Please wait while we check whether your system has the required dependencies installed to run this program"
sleep 2
trap result EXIT
checkDep
