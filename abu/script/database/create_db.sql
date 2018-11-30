drop table daily_tbl;
CREATE TABLE IF NOT EXISTS `daily_tbl`(
   `id` INT UNSIGNED AUTO_INCREMENT,
   `date` INT  NOT NULL,
   `open` FLOAT NOT NULL,
   `high` FLOAT NOT NULL,
   `low` FLOAT NOT NULL,
   `close` FLOAT NOT NULL,
   `volume` BIGINT NOT NULL,
   `count` FLOAT NOT NULL,
   PRIMARY KEY ( `id` )
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
