CREATE SCHEMA `flights` ;



CREATE TABLE `flights`.`flights` (
  `id` INT NOT NULL,
  `Origin` VARCHAR(45) NOT NULL,
  `Destination` VARCHAR(45) NOT NULL,
  `Price` INT NOT NULL,
  `Date` DATE NOT NULL,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  PRIMARY KEY (`id`));

