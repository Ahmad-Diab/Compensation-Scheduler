-- MySQL dump 10.13  Distrib 8.0.15, for macos10.14 (x86_64)
--
-- Host: localhost    Database: GUCDataBase
-- ------------------------------------------------------
-- Server version	8.0.16

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Calendar`
--

DROP TABLE IF EXISTS `Calendar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `Calendar` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `event_name` varchar(45) NOT NULL,
  `date` date NOT NULL,
  `type` varchar(45) DEFAULT NULL,
  `day` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Calendar`
--

LOCK TABLES `Calendar` WRITE;
/*!40000 ALTER TABLE `Calendar` DISABLE KEYS */;
/*!40000 ALTER TABLE `Calendar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Compensations`
--

DROP TABLE IF EXISTS `Compensations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `Compensations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `meeting_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `day` varchar(45) NOT NULL,
  `slot` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `room_id_fk_idx` (`room_id`),
  KEY `meeting_id_idx` (`meeting_id`),
  CONSTRAINT `meeting_id` FOREIGN KEY (`meeting_id`) REFERENCES `course_meetings` (`id`),
  CONSTRAINT `room_id_fk` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Compensations`
--

LOCK TABLES `Compensations` WRITE;
/*!40000 ALTER TABLE `Compensations` DISABLE KEYS */;
/*!40000 ALTER TABLE `Compensations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Course_Meetings`
--

DROP TABLE IF EXISTS `Course_Meetings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `Course_Meetings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `course_id` int(11) NOT NULL,
  `staff_member_id` int(11) NOT NULL,
  `day` varchar(45) NOT NULL,
  `slot` int(11) NOT NULL,
  `lecture_group_id` int(11) NOT NULL,
  `tutorial_group_id` int(11) DEFAULT NULL,
  `room_id` int(11) NOT NULL,
  `slot_type` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `staff_member_has_one_slot` (`staff_member_id`,`day`,`slot`),
  UNIQUE KEY `tutorial_has_one_slot` (`day`,`slot`,`lecture_group_id`,`tutorial_group_id`),
  KEY `course_id_idx` (`course_id`),
  KEY `staff_member_id_idx` (`staff_member_id`),
  KEY `lecture_group_id_idx` (`lecture_group_id`),
  KEY `tutorial_group_id_idx` (`tutorial_group_id`),
  KEY `room_id_idx` (`room_id`),
  CONSTRAINT `course_id` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `lecture_group_id_fk` FOREIGN KEY (`lecture_group_id`) REFERENCES `lecture_groups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `room_id` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `staff_member_id` FOREIGN KEY (`staff_member_id`) REFERENCES `staff_members` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tutorial_group_id` FOREIGN KEY (`tutorial_group_id`) REFERENCES `tutorial_groups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Course_Meetings`
--

LOCK TABLES `Course_Meetings` WRITE;
/*!40000 ALTER TABLE `Course_Meetings` DISABLE KEYS */;
/*!40000 ALTER TABLE `Course_Meetings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Courses`
--

DROP TABLE IF EXISTS `Courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `Courses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Courses`
--

LOCK TABLES `Courses` WRITE;
/*!40000 ALTER TABLE `Courses` DISABLE KEYS */;
/*!40000 ALTER TABLE `Courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Lecture_Groups`
--

DROP TABLE IF EXISTS `Lecture_Groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `Lecture_Groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lecture_group_name` varchar(45) NOT NULL,
  `is_newcomer` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `lecture_group_UNIQUE` (`lecture_group_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Lecture_Groups`
--

LOCK TABLES `Lecture_Groups` WRITE;
/*!40000 ALTER TABLE `Lecture_Groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `Lecture_Groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Rooms`
--

DROP TABLE IF EXISTS `Rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `Rooms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `room_name` varchar(45) NOT NULL,
  `room_type` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `room_name_UNIQUE` (`room_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Rooms`
--

LOCK TABLES `Rooms` WRITE;
/*!40000 ALTER TABLE `Rooms` DISABLE KEYS */;
/*!40000 ALTER TABLE `Rooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Staff_Members`
--

DROP TABLE IF EXISTS `Staff_Members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `Staff_Members` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Staff_Members`
--

LOCK TABLES `Staff_Members` WRITE;
/*!40000 ALTER TABLE `Staff_Members` DISABLE KEYS */;
/*!40000 ALTER TABLE `Staff_Members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Tutorial_Groups`
--

DROP TABLE IF EXISTS `Tutorial_Groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `Tutorial_Groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tutorial_group_name` varchar(45) NOT NULL,
  `lecture_group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `lecture_group_id_idx` (`lecture_group_id`),
  CONSTRAINT `lecture_group_id` FOREIGN KEY (`lecture_group_id`) REFERENCES `lecture_groups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Tutorial_Groups`
--

LOCK TABLES `Tutorial_Groups` WRITE;
/*!40000 ALTER TABLE `Tutorial_Groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `Tutorial_Groups` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-12-01 14:46:50
