-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: mydb
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts` (
  `account_id` int NOT NULL AUTO_INCREMENT,
  `account_name` varchar(45) NOT NULL,
  `current_balance` decimal(10,0) NOT NULL,
  `Customers_customer_id` int NOT NULL,
  PRIMARY KEY (`account_id`),
  KEY `fk_Accounts_Customers_idx` (`Customers_customer_id`),
  CONSTRAINT `fk_Accounts_Customers` FOREIGN KEY (`Customers_customer_id`) REFERENCES `customers` (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts`
--

LOCK TABLES `accounts` WRITE;
/*!40000 ALTER TABLE `accounts` DISABLE KEYS */;
INSERT INTO `accounts` VALUES (1,'david_lee',56435,1),(2,'jane_mith',45634,2),(3,'emily_johnson',23456,3),(4,'michael_brown',54323,4),(5,'sarah_wilson',32456,5),(13,'jessica_taylor',134256,10),(15,'natalie_green',43780,12),(16,'anthony_scott',324591,13),(17,'chris_harris',158746,11),(18,'ashley_adams',75984,14),(19,'joshua_nelson',67239,15),(20,'olivia_carter',140892,16),(21,'daniel_evans',45820,17),(22,'isabella_moore',276514,18),(23,'ethan_clark',183700,19),(24,'mia_walker',56289,20),(25,'james_king',89103,21),(26,'lily_mitchell',489231,22),(27,'benjamin_perez',12645,23),(28,'sophia_harris',98670,24),(29,'samuel_roberts',309850,25),(30,'victoria_adams',74530,26),(31,'alexander_mitchell',58040,27),(32,'grace_robinson',39012,28),(33,'lucas_white',278463,29);
/*!40000 ALTER TABLE `accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `customer_id` int NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(45) NOT NULL,
  `customer_phone` int NOT NULL,
  `customer_email` varchar(45) NOT NULL,
  `customer_street` varchar(45) DEFAULT NULL,
  `customer_municipality` varchar(45) NOT NULL,
  `customer_city` varchar(45) NOT NULL,
  `customer_province` varchar(45) NOT NULL,
  `customer_zipcode` int NOT NULL,
  PRIMARY KEY (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (1,'David Lee',6789012,'davidlee@example.com','Elm Street','Greenfield','Calgary','Alberta',67890),(2,'Jane Smith',2345678,'janesmith@example.com','Pine Road','Birchwood','Riverton','Quebec',23456),(3,'Emily Johnson',3456789,'emilyjohnson@example.com','Maple Avenue','Forest Hill','Alexandria','Alberta',34567),(4,'Michael Brown',4567890,'michaelbrown@example.com','Birch Lane','Silver Valley','Hamilton','British Columbia',45678),(5,'Sarah Wilson',5678901,'sarahwilson@example.com','Cedar Drive','Pinehill','Toronto','Ontario',56789),(10,'Jessica Taylor',7890123,'jessicataylor@example.com','Maple Crescent','Willow Grove','Vancouver','British Columbia',78901),(11,'Christopher Harris',8901234,'christopherharris@example.com','Pine Ridge','Westside','Edmonton','Alberta',89012),(12,'Natalie Green',9012345,'nataliegreen@example.com','Oak Drive','Riverdale','Montreal','Quebec',90123),(13,'Anthony Scott',1123456,'anthonyscott@example.com','Cedar Lane','Brooksville','Ottawa','Ontario',11234),(14,'Ashley Adams',2234567,'ashleyadams@example.com','Birch Street','Highwood','Toronto','Ontario',22345),(15,'Joshua Nelson',3345678,'joshuanelson@example.com','Maple Road','Fairview','Calgary','Alberta',33456),(16,'Olivia Carter',4456789,'oliviacarter@example.com','Oak Ridge','Lakewood','Vancouver','British Columbia',44567),(17,'Daniel Evans',5567890,'danielevans@example.com','Elm Road','Eastpoint','Montreal','Quebec',55678),(18,'Isabella Moore',6678901,'isabellamoore@example.com','Cedar Avenue','Greenwood','Edmonton','Alberta',66789),(19,'Ethan Clark',7789012,'ethanclark@example.com','Pine Trail','Hillside','Hamilton','Ontario',77890),(20,'Mia Walker',8890123,'miawalker@example.com','Maple Park','Riverstone','Ottawa','Ontario',88901),(21,'James King',9901234,'jamesking@example.com','Birch Boulevard','Oakview','Calgary','Alberta',99012),(22,'Lily Mitchell',1012345,'lilymitchell@example.com','Cedar Grove','Pinewood','Vancouver','British Columbia',10123),(23,'Benjamin Perez',2123456,'benjaminperez@example.com','Oak Crescent','Silverwood','Montreal','Quebec',21234),(24,'Sophia Harris',3234567,'sopiaharris@example.com','Elm Crescent','Hilltop','Toronto','Ontario',32345),(25,'Samuel Roberts',4345678,'samuelroberts@example.com','Pinehill Avenue','Westwood','Edmonton','Alberta',43456),(26,'Victoria Adams',5456789,'victoriaadams@example.com','Birch Ridge','Riverside','Vancouver','British Columbia',54567),(27,'Alexander Mitchell',6567890,'alexandermitchell@example.com','Cedar Park','Greenlake','Montreal','Quebec',65678),(28,'Grace Robinson',7678901,'gracerobinson@example.com','Maple Grove','Pinehill','Calgary','Alberta',76789),(29,'Lucas White',8789012,'lucaswhite@example.com','Oak Trail','Riverbend','Hamilton','Ontario',87890);
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `merchants`
--

DROP TABLE IF EXISTS `merchants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `merchants` (
  `merchant_id` int NOT NULL AUTO_INCREMENT,
  `merchant_name` varchar(45) NOT NULL,
  `merchant_email` varchar(45) NOT NULL,
  PRIMARY KEY (`merchant_id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `merchants`
--

LOCK TABLES `merchants` WRITE;
/*!40000 ALTER TABLE `merchants` DISABLE KEYS */;
INSERT INTO `merchants` VALUES (1,'Golden Bloom Co.','goldenbloom@merchants.com'),(2,'The Market Maven','marketmaven@storefronts.net'),(3,'Eco Haven','ecohaven@sustainableshop.org'),(4,'Digital Bazaar','contact@digitalbazaar.com'),(5,'Urban Threads','support@urbanthreads.shop'),(6,'Tasteful Treats','orders@tastefultreats.io'),(7,'Peak Gear','info@peakgear.net'),(8,'Smart Luxe','hello@smartluxe.co'),(9,'Trendy Trails','inquiry@trendytrails.shop'),(10,'The Artisan’s Nook','artisansnook@crafts.org'),(11,'Global Grocers','sales@globalgrocers.com'),(12,'Sunrise Stationery','sunrise.stationery@supplies.co'),(13,'Pixel Provisions','pixelprovisions@graphics.net'),(14,'Fusion Boutique','info@fusionboutique.shop'),(15,'Crafty Corner','craftycorner@handmade.com'),(16,'Luxury Lane','contact@luxurylane.io'),(17,'Breeze Outdoors',' inquiries@breezeoutdoors.net'),(18,'Sweet Slice Bakery ','orders@sweetslicebakery.org'),(19,'Nova Gadgets','support@novagadgets.store'),(20,'The Green Shelf','greenshelf@eco.shop'),(21,'Bold Apparel','boldapparel@fashion.net'),(22,'Gadget Genie','hello@gadgetgenie.com'),(23,'Fresh Flavors','freshflavors@culinary.net'),(24,'Pinnacle Picks ','info@pinnaclepicks.shop'),(25,'Glow & Glam','glownglam@beautyhub.org'),(26,'Greenfield Stationery','contact@greenfieldstationery.com');
/*!40000 ALTER TABLE `merchants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `transaction_type_description` varchar(45) NOT NULL,
  `amount` decimal(10,0) NOT NULL,
  `date_of_transaction` datetime NOT NULL,
  `balance` decimal(10,0) NOT NULL,
  `Accounts_account_id` int NOT NULL,
  `Merchants_merchant_id` int NOT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `fk_Transactions_Accounts1_idx` (`Accounts_account_id`),
  KEY `fk_Transactions_Merchants1_idx` (`Merchants_merchant_id`),
  CONSTRAINT `fk_Transactions_Accounts1` FOREIGN KEY (`Accounts_account_id`) REFERENCES `accounts` (`account_id`),
  CONSTRAINT `fk_Transactions_Merchants1` FOREIGN KEY (`Merchants_merchant_id`) REFERENCES `merchants` (`merchant_id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
INSERT INTO `transactions` VALUES (1,'Withdrawal',6600,'2024-12-10 00:00:00',83000,1,1),(2,'Deposit',27500,'2024-12-09 00:00:00',89500,2,2),(3,'Transfer',13250,'2024-12-08 00:00:00',69250,3,3),(4,'Withdrawal',4125,'2024-12-07 00:00:00',64875,4,4),(6,'Deposit',56890,'2024-12-14 00:00:00',56342,5,5),(7,'Transfer',76453,'2024-12-15 00:00:00',145362,13,7),(8,'Withdrawal',6600,'2024-12-10 00:00:00',83000,15,8),(9,'Deposit',27500,'2024-12-09 00:00:00',89500,16,9),(10,'Transfer',13250,'2024-12-08 00:00:00',69250,17,10),(11,'Withdrawal',4125,'2024-12-07 00:00:00',64875,18,11),(12,'Deposit',10000,'2024-12-06 00:00:00',74875,19,12),(13,'Balance Inquiry',0,'2024-12-05 00:00:00',74875,20,13),(14,'Withdrawal',15000,'2024-12-04 00:00:00',59875,21,14),(15,'Transfer',22500,'2024-12-03 00:00:00',37375,22,15),(16,'Deposit',50000,'2024-12-02 00:00:00',87375,23,16),(17,'Withdrawal',4400,'2024-12-01 00:00:00',82975,24,17),(18,'Deposit',22500,'2024-11-30 00:00:00',110475,25,18),(19,'Transfer',8250,'2024-11-29 00:00:00',102225,26,19),(20,'Withdrawal',3300,'2024-11-28 00:00:00',98925,27,20),(21,'Balance Inquiry',0,'2024-11-27 00:00:00',98925,28,21),(22,'Deposit',60000,'2024-11-26 00:00:00',158925,29,22),(23,'Withdrawal',22000,'2024-11-25 00:00:00',136925,30,23),(24,'Transfer',17500,'2024-11-24 00:00:00',119425,31,24),(25,'Deposit',40000,'2024-11-23 00:00:00',159425,32,25),(26,'Withdrawal',5000,'2024-11-22 00:00:00',154425,33,26);
/*!40000 ALTER TABLE `transactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'mrkalilano','scrypt:32768:8:1$Po7eek5IE7XZkdKl$d0589d2a98eb685ec0d148bb42635d4c27adf741ce731a8ce1d2643754748941022114ba707f928f08579d1cbe595151fca0883766310e070481b92bc87f5723','alilano@example.com','admin','2024-12-11 14:10:50'),(2,'testuser','scrypt:32768:8:1$bdR9QlkTuNZwPOXj$f408f079372fd2b9720b9062ae816148dc1444061a912bceaaaf4a963f13a0076604a3cf76f64f37871cbc59385df2f8b3df7f5f1cc4f58c81d117f94a39ba45','testuser@example.com','admin','2024-12-11 14:44:33'),(3,'testuser2','scrypt:32768:8:1$tIZRIElisaObQUGS$f520e7c3b3fce2b36aa14fc72620c8712d941df87ea0c21cf807b5bfa345640c31b3c948d3c522f1530a8d030475d6abd379c3ad686672602f343b0a334b5655','example@gmai.com','admin','2024-12-11 14:59:04'),(4,'testuser4','scrypt:32768:8:1$9sE5mRsHCgXbFgws$5d302b7c76eb4f4d95ecc674ca1ca642e1b62724718e81ff3830c3a3f6acdf3b44d7d43af40e689e09321e059511f4e70d5c38d0de3c7c0a06ca4700a179d008','example2@gmail.com','manager','2024-12-11 15:05:48'),(5,'test101','scrypt:32768:8:1$y4U2kmhbyazZJtfn$cf17301194e38572e6e9b0e25920dd3dbb3871a4107f37ddd67bb14b7849c3de5a54e275ff599f254eb9bef9d116f071748d18193f75a91bbb8bd7e91a2738a0','test@gmail.com','user','2024-12-11 15:54:46'),(6,'test102','scrypt:32768:8:1$jOjCp2qoyJfTKHl6$57f8348e8cf82c26c4c16cebf09c16604dd36b403fd2f64de180bb07f16ac7c316260549ac7df2552c87bf548e9f0850b72354d747463c3c5189e523e5fc83ff','test102@example.com','admin','2024-12-11 16:28:17'),(7,'test104','scrypt:32768:8:1$sicszcWiUssuyIxK$2bcc00ac3607be1de096795b50c70a8c4b51573f5d4298bf2a77db416d0210f6fd12d43d0849e5d21d218e430f7d5ca489c6bd8b8f6a92f97eeed0924dfb8001','michael@example.com','admin','2024-12-12 05:54:09'),(8,'mark123','scrypt:32768:8:1$KHWlotb9wOLE2Kd9$dc74963b6ddfa65dc7b26073faa1f992e1f18be38d2370c14dcc19eca7ffe00b255e950a79a4dd14c93c10ca4d6c3580cc7784cb3379505f8b881af1cbcd04c1','mark@example.com','admin','2024-12-12 09:14:42'),(9,'kram123','scrypt:32768:8:1$GEuGW8MzTDs6JLXY$ec89b2247ac42a559867a53046eae95b0815823867875db6b7bee59bb78244ccacd3370e3b824bb3fdfd55082273ba5a7d46ed89889b2676a049d8021e426b44','markalilano@example.com','admin','2024-12-12 09:58:40'),(10,'markkk123','scrypt:32768:8:1$0UPN4idFIdbjYZ8U$ae36f309faf277f9ede767ce31e4400f8649e4296d1760bc817e27759a7195b3c89a5047013843a91d3eccfc00a55d907100daa9c239c8d12e966766a430c749','markk@example.com','admin','2024-12-12 11:18:13');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-12 22:29:08
