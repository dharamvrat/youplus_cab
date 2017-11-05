Created 2 database tables:

1. Driver:
          - It has two columns, id and name which are self explanatory
          - Query:
                    CREATE TABLE 'DRIVER' (
                      'id' int(11) unsigned NOT NULL AUTO_INCREMENT,
                      'name' varchar(30) DEFAULT NULL,
                      PRIMARY KEY ('id')
                    )
          - Inserted 5 entries for each driver

2. Booking:
          - It has multiple columns as mentioned in below create query.
          - Query:
                    CREATE TABLE 'BOOKING' (
                      'id' int(11) unsigned NOT NULL AUTO_INCREMENT,
                      'customer_id' int(11) unsigned NOT NULL,
                      'driver_id' int(11) unsigned DEFAULT NULL,
                      'created_at' datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      'pickup_at' datetime DEFAULT NULL,
                      'completed_at' datetime DEFAULT NULL,
                      'status' enum('ONGOING','WAITING','COMPLETED') NOT NULL DEFAULT 'WAITING',
                      PRIMARY KEY ('id'),
                      KEY 'customer_id' ('customer_id'),
                      KEY 'driver_id' ('driver_id'),
                      CONSTRAINT 'booking_ibfk_2' FOREIGN KEY ('driver_id') REFERENCES 'DRIVER' ('id')
                    )
           - Foreign key is the primary key ('id') of table 'Driver'

3. Customer<Not created>:
          - Did not create this table as we do not need it at this point of time. If required, this table can be added later.
