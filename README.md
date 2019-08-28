# tradefeed_cmbhk
Convert Bloomberg trade file (export from AIM) to CMBHK trade file format, becasue CMBHK is the fund admin of 40017.



++++++++++++++
Database setup
++++++++++++++

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
