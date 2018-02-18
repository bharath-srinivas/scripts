# Created by Bharath Srinivas on 08/12/2016

#!/bin/bash -e

export USR='user'
export RHOST='host'
export LOG=$HOME/sync.log
export ID_FILE=$HOME/.ssh/private_key_file
export isSuccess=false

function sync()	{
	if [ -f ${LOG} ]; then
		:
	else
		touch ${LOG}
	fi
	rsync -azq -e --delete --rsh="ssh -i $ID_FILE" $HOME/directory/ ${USR}@${RHOST}:/home/${USR}/directory 2>&1 >> ${LOG};
	result="$?"
	if [ ${result} -eq 0 ]; then
		isSuccess=true
	fi
}

function success() {
	if [ ${isSuccess} == true ]; then
		echo "The sync process has completed successfully."
	else
		echo "The sync process has failed."
	fi
}

trap success EXIT
sync

