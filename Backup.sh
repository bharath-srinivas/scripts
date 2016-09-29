#!/bin/bash -e

export NOW="$(date +%d-%m-%Y)"
export DIRECTORY=$HOME/path/to/create/backup/directory/
export WEB_DIRECTORY=/path/to/wordpress/directory
export DB_FILE=File_name_"$NOW".sql
export WEB_FILE=File_name_"$NOW".tar.gz
export OLD_FILES="find "$DIRECTORY"/* -mtime +30 -print"
MYSQL_PASS=password
SYS_PASS=password

#Flag to find out whether the process has succeeded or not
export is_success=false
export is_deleted=false

function backup() {
	# Check if backup directory exists or create a new backup directory
	if [ -d "$DIRECTORY" ]; then
		:
	else
		mkdir -p "$DIRECTORY"
	fi

	# Traverse into the backup directory
	cd "$DIRECTORY"

	# Delete the backup files which are older than 2 months to clear up some space for newer 		backup
	yes y | find "$DIRECTORY"/* -mtime +30 -exec rm {} \;
	
	# Check whether the older backup files has been deleted
	for i in "$OLD_FILES"; do
		if [[ $i != "$DB_FILE" || $i != "$WEB_FILE" ]]; then
			is_deleted=true
		else
			:
		fi
	done

	# Tell the user whether the deletion proceess has succeeded or not
	if [ "$is_deleted" == true ]; then
		echo "Backup files that were older than 30 days has been deleted successfully"
	else
		echo "Deletion of older backup files failed"
	fi

	# Start the backup process of database inside the backup directory
	echo "Backup of Website's database started at $NOW"
	mysqldump -u root -p"$MYSQL_PASS" db_name > "$DB_FILE"

	# Start the backup process of website files 
	echo "Backup of Website files started at $NOW"
	echo "$SYS_PASS" | sudo tar -zcf "$WEB_FILE" "$WEB_DIRECTORY"

	# Check whether the files are created or not and update the flag accordingly
	if [[ -f "$DB_FILE"  && -f "$WEB_FILE" ]]; then
		is_success=true
	else
		:
	fi

	# Traverse back to the previous directory after completing the process
	cd -
}


before_exit() {
  if [ "$is_success" == true ]; then
    echo "Website Backup has been completed successfully";
  else
    echo "Website Backup script execution failed";
  fi
}

trap before_exit EXIT
backup
