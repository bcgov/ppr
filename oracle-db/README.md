# Oracle Database Server Docker Image Documentation
PPR uses an Oracle 12c database. Here are instructions on running a Docker Oracle 12c
database for local development. After starting the instance, see the scripts readme
to create the ppr_mgr schema.

Oracle Database Server 12c R2 is an industry leading relational database server. The Oracle Database Server Docker Image contains the Oracle Database Server 12.2.0.1 Enterprise Edition running on Oracle Linux 7. This image contains a default database in a multitenant configuration with one pdb.

For more information on Oracle Database Server 12c R2 refer to http://docs.oracle.com/en/database/

This directory includes an example start-ee.sh script for starting the image, as well as example ora.conf and tnsnames.ora configuration files.


## Accepting the terms of service

From the store.docker.com website accept Terms of Service for Oracle Database Enterprise Edition.

## Login to Docker Store

Login to Docker Store with your credentials

	$ docker login

## Get the image

	$ docker pull store/oracle/database-enterprise:12.2.0.1

## Starting an Oracle Database Server instance

Starting an Oracle database server instance is as simple as executing

	$ docker run -d -it --name <Oracle-DB> store/oracle/database-enterprise:12.2.0.1
	
	(optional - start it with a defined directory)
	
	$ docker run -d -it --name <Oracle-DB> -v /mnt/c/Users/username/Containers/bcregistry/oradata/OracleDBData:/ORCL store/oracle/database-enterprise:12.2.0.1

where <Oracle-DB> is the name of the container and 12.2.0.1 is the Docker image tag.

The database server is ready to use when the STATUS field shows (healthy) in the output of docker ps.


## Connecting to the Database Server Container

The default password to connect to the database with sys user is Oradoc_db1.

### Connecting from within the container

The database server can be connected to by executing SQL*Plus,

	$ docker exec -it <Oracle-DB> bash -c "source /home/oracle/.bashrc; sqlplus /nolog"


## Connecting from outside the container


The database server exposes port 1521 for Oracle client connections over SQLNet protocol and port 5500 for Oracle XML DB. SQLPlus or any JDBC client can be used to connect to the database server from outside the container.

To connect from outside the container start the container with -P or -p option as,

	$ docker run -d -it --name <Oracle-DB> -P store/oracle/database-enterprise:12.2.0.1

option -P indicates the ports are allocated by Docker. The mapped port can be discovered by executing

	$ docker port <Oracle-DB>

Using this <mapped host port> and <ip-address of host> create tnsnames.ora in the directory pointed to by environment variable TNS_ADMIN.

	ORCLCDB=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=<ip-address of host>)(PORT=<mapped host port>))
    		(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=ORCLCDB.localdomain)))
	ORCLPDB1=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=<ip-address> of host)(PORT=<mapped host port>))
    		(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=ORCLPDB1.localdomain)))

To connect from outside the container using SQL*Plus,

	$ sqlplus sys/Oradoc_db1@ORCLCDB as sysdba


## Custom Configurations

The Oracle database server container also provides custom configuration parameters for starting up the container. All the custom configuration parameters are optional. The following list of custom configuration parameters can be provided in the ENV file (ora.conf).

DB_SID

This parameter changes the ORACLE_SID of the database. The default value is set to ORCLCDB.

DB_PDB

This parameter modifies the name of the PDB. The default value is set to ORCLPDB1.

DB_MEMORY

This parameter sets the memory requirement for the Oracle server. This value determines the amount of memory to be allocated for SGA and PGA. The default value is set to 2GB.

DB_DOMAIN

This parameter sets the domain to be used for database server. The default value is localdomain.

To start an Oracle database server with custom configuration parameters

	$ docker run -d -it --name <Oracle-DB> -P --env-file ora.conf store/oracle/database-enterprise:12.2.0.1

Ensure custom values for DB_SID, DB_PDB and DB_DOMAIN are updated in the tnsnames.ora.


## Using host system directory for data volume

To use a directory on the host system for the data volume,

	$ docker run -d -it --name <Oracle-DB> -v /data/OracleDBData:/ORCL store/oracle/database-enterprise:12.2.0.1

where /data/OracleDBData is a directory in the host system.

