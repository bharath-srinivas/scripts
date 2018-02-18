# Created by Bharath Srinivas on 17/11/2016

#!/bin/bash -e

# Declare the required variables
export SERV_USER="user"
export SERV_HOST="host"
export PRVT_KEY=$HOME/.ssh/private_key
export BCKP_DIR=$HOME/bck_dir
export OLD_FILES="find "${BCKP_DIR}"/* -mtime +60 -print"
export LINES=$(${OLD_FILES} | wc -l)
export NOW="$(date +%d-%m-%Y)"
export REMOTE_DIR="/home/user/bcp_dir"
export FILES=(DB_$NOW.sql Website_$NOW.tar.gz)

# Flag to check the successful execution of the script
export is_success=false
export is_deleted=false

# Check whether the backup directory exists else create one and traverse into that directory
if [[ -d "$BCKP_DIR" ]]; then
	cd "$BCKP_DIR"
else
	mkdir -p "$BCKP_DIR"
	cd "$BCKP_DIR"
fi

# Delete backup files which are 2 months old from the time of backup
yes y | find "$BCKP_DIR"/* -mtime +60 -exec rm {} \;

# Check whether the older files which are older than 2 months has been deleted
if [ "$LINES" -eq 0 ]; then
	is_deleted=true
fi

# Notify user that the older backup files were deleted
if [ "$is_deleted" == true ]; then
	echo "Backup files that were older than 60 days has been deleted successfully"
else
	echo "Deletion of older backup files failed"
fi

# Download the backup into the specified folder
function download() {
	# Download the website file
	for i in "${FILES[@]}"; do
		scp -i "$PRVT_KEY" "$SERV_USER"@"$SERV_HOST":/"$REMOTE_DIR"/"$i" .
	done

	# Check whether the backup has been downloaded successfully
	if [[ -f "Website_live_$NOW.tar.gz" && -f "Website_DB_$NOW.sql" ]]; then
		is_success=true
	fi

	# Move the new backup files to the root of website directory
	for j in "${FILES[@]}"; do
		echo "password" | sudo mv ${j} /var/www/website/website_bckps
	done
	echo "The new backup files has been successfully moved to website root"

	# Traverse back to the last working directory
	cd -
	
	# Remove the created backup directory
	rm -rf ${BCKP_DIR}
}


# Tell the user whether the download process has completed successfully or not and exit
function success() {
	if [ "$is_success" == true ]; then
		echo "The backup has been downloaded successfully"
	else
		echo "The download has failed."
	fi
}

trap success EXIT
download
