import os
import subprocess
import yaml
from datetime import datetime, timedelta
import shutil

"""
secureSnap
Version: 1.0.0
Author: Andreas Günther, github@it-linuxmaker.com
License: GNU General Public License v3.0 or later
"""

# Path to the configuration file in /etc/securesnap/
CONFIG_FILE = '/etc/securesnap/backup_config.yaml'

# Function to load the YAML configuration
def load_config(config_file=CONFIG_FILE):
    """
    Loads and parses the given YAML configuration file into a Python dictionary.

    Args:
        config_file (str): The path to the YAML configuration file. Defaults to the global CONFIG_FILE.

    Returns:
        dict: A dictionary representing the contents of the YAML file.

    Raises:
        FileNotFoundError: If the specified config file is not found.
        yaml.YAMLError: If the YAML file contains syntax errors or is not valid.
    """
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

# Function to write log messages
"""
    Appends a log message to the specified log file with a timestamp.

    Args:
        log_file (str): The path to the log file where the message will be written.
        message (str): The log message to be written to the file.
"""
def write_log(log_file, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a') as log:
        log.write(f"{timestamp} - {message}\n")

# Function to back up installed packages
"""
    Backs up the list of installed packages to a specified directory.

    The function checks for the presence of either the `dpkg` or `rpm` package manager.
    It saves the list of installed packages to a file named `installed_packages.txt` in the
    specified backup directory. Log messages are written during the process, indicating success or failure.

    Args:
        backup_dir (str): The directory where the list of installed packages will be saved.
        log_file (str): The path to the log file where the log messages will be recorded.

    Raises:
        OSError: If an error occurs when writing to the backup file.
        Exception: If any other error occurs during the process.
"""
def backup_installed_packages(backup_dir, log_file):
    package_list_file = os.path.join(backup_dir, "installed_packages.txt")
    try:
        write_log(log_file, "Securing installed packages...")
        with open(package_list_file, 'w') as f:
            if shutil.which("dpkg"):
                result = subprocess.run(["dpkg", "--get-selections"], stdout=subprocess.PIPE)
                f.write(result.stdout.decode('utf-8'))
                write_log(log_file, f"Installed packages were successfully saved to {package_list_file}.")
            elif shutil.which("rpm"):
                result = subprocess.run(["rpm", "-qa"], stdout=subprocess.PIPE)
                f.write(result.stdout.decode('utf-8'))
                write_log(log_file, f"Installed packages were successfully saved to {package_list_file}.")
            else:
                write_log(log_file, "No supported package manager (dpkg or rpm) found.")
    except Exception as e:
        write_log(log_file, f"Error saving installed packages: {e}")

# Function to back up MySQL databases (only if enabled)
"""
    Backs up specified MySQL databases if MySQL backup is enabled in the configuration.

    This function checks if MySQL backup is enabled in the provided configuration. If enabled, 
    it iterates over the list of databases and performs a mysqldump for each, saving the dumps to the specified directory. 
    Log messages are written during the backup process to indicate progress and any errors encountered.

    Args:
        config (dict): The configuration dictionary containing MySQL backup settings, including:
            - user (str): MySQL user with backup privileges.
            - password (str): Password for the MySQL user.
            - databases (list): A list of database names to back up.
            - enabled (bool): Flag indicating whether MySQL backup is enabled.
        backup_dir (str): The directory where the backup files will be saved.
        log_file (str): The path to the log file where the log messages will be recorded.

    Raises:
        subprocess.CalledProcessError: If the mysqldump command fails.
        Exception: For any other errors encountered during the process.
"""
def backup_mysql_databases(config, backup_dir, log_file):
    write_log(log_file, "Starting MySQL backup.")
    if not config['backup']['mysql'].get('enabled', False):
        write_log(log_file, "MySQL backup is disabled.")
        return

    mysql_user = config['backup']['mysql']['user']
    mysql_password = config['backup']['mysql']['password']
    databases = config['backup']['mysql']['databases']

    for db in databases:
        write_log(log_file, f"Securing database {db}.")
        db_backup_file = os.path.join(backup_dir, f"{db}_backup.sql")
        try:
            dump_command = f"mysqldump -u {mysql_user} -p{mysql_password} {db} > {db_backup_file}"
            subprocess.run(dump_command, shell=True)
            write_log(log_file, f"The database {db} was successfully backed up to {db_backup_file}.")
        except Exception as e:
            write_log(log_file, f"Error saving database {db}: {e}")

# Function to perform a backup
"""
    Performs a full or incremental backup based on the provided configuration.

    This function initiates the backup process by:
    - Logging the start of the backup.
    - Retrieving the hostname of the system.
    - Creating a directory for the backup, named by the current date.
    - Determining the backup type (full or incremental) based on the configuration settings.
    - Applying compression if specified (tar, gzip, bzip2, xz, etc.).

    Args:
        config (dict): The configuration dictionary containing backup settings, including:
            - log_file (str): Path to the log file for recording backup progress.
            - backup_dir (str): Directory where backups will be saved.
            - full_backup_interval (int): Interval (in days) for performing full backups.
            - compression (str, optional): The compression method to use for the backup (default: 'tar').

    Raises:
        OSError: If there is an issue with creating the backup directory or file system access.
        Exception: For any other errors encountered during the backup process.
"""
def create_backup(config):
    log_file = config['backup']['log_file']
    
    write_log(log_file, "Starting backup process...")
    
    try:
        # Get hostname
        hostname = subprocess.getoutput('hostname')
        write_log(log_file, f"Hostname: {hostname}")

        # Get date
        date_str = datetime.now().strftime('%Y-%m-%d')
        backup_dir = os.path.join(config['backup']['backup_dir'], date_str)
        write_log(log_file, f"Backup directory: {backup_dir}")

        full_backup_interval = config['backup']['full_backup_interval']
        compression = config['backup'].get('compression', 'tar')  # Compression from the YAML file (gzip, bzip2, xz)

        # Check backup directory and create if necessary
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            write_log(log_file, f"Backup directory {backup_dir} was created.")
        else:
            write_log(log_file, f"Backup directory {backup_dir} already exists.")

        # Perform backup for each target
        for destination in config['backup']['destinations']:
            path_to_backup = destination['path']
            archive_name = f"{hostname}_{destination['archive']}_"
            backup_type = destination['type']

            # Prepare snapshot file
            snapshot_file = os.path.join(config['backup']['backup_dir'], f"snapshot_{destination['archive']}.snar")
            
            write_log(log_file, f"Processing destination: {path_to_backup}")

            # Counter file for the target
            count_file = os.path.join(config['backup']['backup_dir'], f"incremental_count_{destination['archive']}.txt")

            # Check or create counter
            if not os.path.exists(count_file):
                with open(count_file, 'w') as f:
                    f.write('0')
            with open(count_file, 'r') as f:
                incremental_count = int(f.read())

            write_log(log_file, f"Incremental counter for {destination['archive']}: {incremental_count}")

            # Determine backup type (full, full-single or incremental)
            if backup_type == 'incremental':
                if incremental_count >= full_backup_interval or not os.path.exists(snapshot_file):
                    # Full backup if either the counter has reached the limit or the snapshot file is missing
                    archive_name += f"full-{incremental_count}.tar"
                    tar_command = ["tar", "-cf", "-", "-g", snapshot_file]  # "-" outputs tar to stdout
                    write_log(log_file, f"Snapshot file not found or counter reached. Perform full backup for {destination['archive']}.")
                    incremental_count = 0  # Reset counter after full backup
                else:
                    # Incremental backup if the snapshot file exists and the counter is smaller than the interval
                    archive_name += f"incremental-{incremental_count}.tar"
                    tar_command = ["tar", "-cf", "-", "-g", snapshot_file]
                    write_log(log_file, f"Incremental backup is performed using snapshot file {snapshot_file}.")
            elif backup_type == 'full-single':
                # If full-single, always create a full backup, but without incremental backups
                archive_name += f"full-single-{incremental_count}.tar"
                tar_command = ["tar", "-cf", "-"]
                write_log(log_file, f"Perform full-single backup for {destination['archive']}.")
            else:
                # Always create a full backup if the type is "full"
                archive_name += f"full-{incremental_count}.tar"
                tar_command = ["tar", "-cf", "-", "-g", snapshot_file]
                write_log(log_file, f"Perform full backup for {destination['archive']} and create snapshot file {snapshot_file}.")

            # Create exclude options
            exclude_opts = []
            for exclude_item in destination.get('exclude', []):
                exclude_opts.append(f"--exclude={exclude_item}")

            # Apply compression if defined in config
            if compression == "gzip":
                compression_command = ["gzip"]
                archive_name += ".gz"
            elif compression == "bzip2":
                compression_command = ["bzip2"]
                archive_name += ".bz2"
            elif compression == "xz":
                compression_command = ["xz"]
                archive_name += ".xz"
            else:
                compression_command = []  # No compression

            # Combine tar and compression
            tar_command += exclude_opts + [path_to_backup]
            try:
                with open(os.path.join(backup_dir, archive_name), 'wb') as f_out:
                    tar_process = subprocess.Popen(tar_command, stdout=subprocess.PIPE)
                    if compression_command:
                        compression_process = subprocess.Popen(compression_command, stdin=tar_process.stdout, stdout=f_out)
                        tar_process.stdout.close()  # Allow tar to receive a SIGPIPE if compression_process exits
                        compression_process.communicate()
                    else:
                        shutil.copyfileobj(tar_process.stdout, f_out)
                        tar_process.communicate()

                write_log(log_file, f"Archive successfully created: {os.path.join(backup_dir, archive_name)}")

            except Exception as e:
                write_log(log_file, f"Error creating archive for {path_to_backup}: {e}")
                return  # Consider backup as failed

            # Save counter (only for full and incremental)
            if backup_type in ['full', 'incremental']:
                incremental_count += 1
                with open(count_file, 'w') as f:
                    f.write(str(incremental_count))
                    write_log(log_file, f"Incremental counter for {destination['archive']} updated: {incremental_count}")

        # Back up installed packages
        backup_installed_packages(backup_dir, log_file)

        # Back up MySQL databases (if enabled)
        backup_mysql_databases(config, backup_dir, log_file)

        # Delete old backups after retention time
        clean_old_backups(config)

        # Report successful backup
        write_log(log_file, f"Backup of {date_str} completed successfully.")

    except Exception as e:
        write_log(log_file, f"Backup error: {e}")

# Function to delete old backups based on retention time
"""
    Deletes old backups from the backup directory based on the retention time.

    This function scans the backup directory and deletes any backups older than the specified
    retention time (in days). If retention time is set to `False`, no backups are deleted.

    Args:
        config (dict): The configuration dictionary containing backup settings, including:
            - backup_dir (str): The directory where backups are stored.
            - log_file (str): Path to the log file for recording progress.
            - retention_time (int, optional): The number of days to keep backups. If `False`, no backups are deleted.

    Raises:
        FileNotFoundError: If the backup directory does not exist.
        OSError: If there is an issue accessing or deleting files.
"""
def clean_old_backups(config):
    backup_base_dir = config['backup']['backup_dir']
    log_file = config['backup']['log_file']
    retention_time = config['backup'].get('retention_time', False)

    # Get list of backup directories with their modification times
    backups = [(d, os.path.join(backup_base_dir, d)) for d in os.listdir(backup_base_dir) if os.path.isdir(os.path.join(backup_base_dir, d))]

    if not backups:
        write_log(log_file, "No backups found to delete.")
        return

    if retention_time:
        # Use retention_time to delete backups older than the retention time in days
        retention_period = timedelta(days=retention_time)
        current_time = datetime.now()
        
        for backup, backup_path in backups:
            backup_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
            if current_time - backup_time >= retention_period:
                shutil.rmtree(backup_path)
                write_log(log_file, f"Backup {backup} was deleted due to retention time (older than {retention_time} days).")

    else:
        write_log(log_file, "Retention time is false, no old backups are deleted.")

# Main function
"""
    Main entry point for the backup script.

    This section loads the configuration, performs a backup, and then cleans up old backups based on the retention policy.
    
    Steps:
    1. Load the configuration from a YAML file or other defined source.
    2. Create a backup using the settings provided in the configuration.
    3. Clean up old backups that exceed the retention time defined in the configuration.

    Raises:
        FileNotFoundError: If the configuration file cannot be found.
        yaml.YAMLError: If there is an issue parsing the configuration file.
        Exception: For any errors during backup creation or cleanup.
    """
if __name__ == "__main__":
    config = load_config()
    create_backup(config)
    clean_old_backups(config)
