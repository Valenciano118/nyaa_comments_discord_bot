CREATE DATABASE IF NOT EXISTS `nyaa_comments_discord_bot` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `nyaa_comments_discord_bot`;

CREATE TABLE IF NOT EXISTS `torrents` (
  `torrent_id` int NOT NULL,
  `user_id` int NOT NULL,
  `comment_id` int NOT NULL,
  `author` varchar(100) NOT NULL,
  `date` timestamp NOT NULL,
  `content` text NOT NULL,
  `image` mediumblob NOT NULL,
  PRIMARY KEY (`torrent_id`,`user_id`,`comment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `users` (
  `user_id` int NOT NULL,
  `url` varchar(500) NOT NULL,
  `comm_enabled` tinyint(1) NOT NULL DEFAULT (0),
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
