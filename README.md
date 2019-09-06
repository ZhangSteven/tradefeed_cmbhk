# tradefeed_cmbhk
Convert Bloomberg trade file (export from AIM) to CMBHK trade file format, becasue CMBHK is the fund admin of 40017.



++++++++++++++
How It Works
++++++++++++++
The program searches for "TDxxx.xlsx" file in the input directory (specified in the configuration file), convert it to the new format, then send notification via email.

If there are none or more than files found in the input directory, an error will occur and conversion won't happen.

After successful processing, the input file will be moved to another directory.



++++++++++++++
Database setup
++++++++++++++
For database server location, check the configuration file.

mysql> CREATE TABLE trades (
    -> tradeid int NOT NULL AUTO_INCREMENT,
    -> hash varchar(255) NOT NULL,
    -> PRIMARY KEY (tradeid)
    -> );

mysql> describe trades;
+---------+--------------+------+-----+---------+----------------+
| Field   | Type         | Null | Key | Default | Extra          |
+---------+--------------+------+-----+---------+----------------+
| tradeid | int(11)      | NO   | PRI | NULL    | auto_increment |
| hash    | varchar(255) | NO   |     | NULL    |                |
+---------+--------------+------+-----+---------+----------------+
