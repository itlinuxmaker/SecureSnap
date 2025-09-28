
# SecureSnap Backup

SecureSnap Backup is used for automated backup of files and directories on Linux desktop systems or Linux servers. It supports full and incremental backups, backs up the installation state of the system and MySQL databases (optional). Furthermore, all steps are entered into a log file.

The configuration is done via a **YAML file** in which backup destinations, MySQL information and compression settings are specified.
## Features
- Full and incremental backups based on a configurable interval.
	+ Full backup with incremental backups.
	+ Full backups only.
	+ Incremental backups only.
- Backup of MySQL databases (optional).
- Compression of backups (gzip, bzip2, xz).
- Backup of installed packages on the server.
- Exclusion of files and directories.
- Specifies the number of backups.
- Delete old backups once the specified number of backups is reached.
- Logging backup results and errors to a log file.
- Simple structured configuration via a **YAML file**.

## Installation

### Requirements
- Python 3.x
- python3-yaml
- `mysqldump` (if MySQL databases are to be backed up)
- `tar` for archiving
- Compression tools (gzip, bzip2 oder xz)
- Optional: `pytest` for testing

### Install dependencies
To run the program, the following Python modules are installed with `apt install` to make them available system-wide for a cron job:

```bash
apt-get update
apt install python3 python3-yaml git
```

## Usage
### Manual installation
Clone the project onto your Linux system  
```Bash
git clone https://github.com/itlinuxmaker/SecureSnap.git  
```
Change to the project directory and follow these steps:
1.   Navigate to the securesnap directory:
```Bash  
 cd SecureSnap/src/securesnap  

```
2. Create the configuration directory as root:
 ```Bash  
 mkdir -p /opt/securesnap
 mkdir -p /opt/securesnap/etc  
 ```
3. Copy the configuration and script files to their locations:
```
 cp backup_config.yaml /opt/securesnap/etc/
 cp securesnap.py /opt/securesnap/
 ```
4. Edit the YAML configuration file to fit your backup requirements with your preferred text editor (vi, emacs, nano, etc.):
```
vi /opt/securesnap/etc/backup_config.yaml 
```
5. Run the backup script:
```
  python3 /opt/securesnap/securesnap.py
  ```
6. Set up a cron job as root to automate the backup process (optional):
```    
crontab -e
```
Add the following line to run the backup every Friday at 21:00 as example:
```
00 21 * * Fri python3 /opt/securesnap/securesnap.py
```
### Installation with setup script
1. Save the setup.sh in the same folder where you are working.
2. Make it executable:
```
chmod a+x setup.sh
```
3. Run it as root.
```
./setup.sh
```

4. Then continue with step 4 under "Manual Installation".

### Uninstall SecureSnap
To uninstall SecureSnap, use:
```
./setup.sh --uninstall
```

## License
The program is licensed under the GNU General Public License v3.0 or later in 2024.

## Disclaimer
IN NO EVENT WILL I BE LIABLE FOR ANY DAMAGES WHATSOEVER (INCLUDING, WITHOUT LIMITATION, THOSE RESULTING FROM LOST PROFITS, LOST DATA, LOST REVENUE OR BUSINESS INTERRUPTION) ARISING OUT OF THE USE, INABILITY TO USE, OR THE RESULTS OF USE OF, THIS PROGRAM. WITHOUT LIMITING THE FOREGOING, I SHALL NOT BE LIABLE FOR ANY SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES THAT MAY RESULT FROM THE USE OF THIS SCRIPT OR ANY PORTION THEREOF WHETHER ARISING UNDER CONTRACT, NEGLIGENCE, TORT OR ANY OTHER LAW OR CAUSE OF ACTION. I WILL ALSO PROVIDE NO SUPPORT WHATSOEVER, OTHER THAN ACCEPTING FIXES AND UPDATING THE SCRIPT AS IS DEEMED NECESSARY.