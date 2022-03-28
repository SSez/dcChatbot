SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

CREATE TABLE `discord` (
  `id` bigint(32) NOT NULL,
  `nickname` text NOT NULL,
  `user_id` text NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `patterns` (
  `id` bigint(32) NOT NULL,
  `tag_id` bigint(32) NOT NULL,
  `pattern` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `responses` (
  `id` bigint(32) NOT NULL,
  `tag_id` bigint(32) NOT NULL,
  `response` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `tags` (
  `id` bigint(32) NOT NULL,
  `context_tag` bigint(32) DEFAULT 0,
  `end` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `discord`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `patterns`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tag_id` (`tag_id`);

ALTER TABLE `responses`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tag_id` (`tag_id`);

ALTER TABLE `tags`
  ADD PRIMARY KEY (`id`),
  ADD KEY `context_tag` (`context_tag`) USING BTREE;

ALTER TABLE `discord`
  MODIFY `id` bigint(32) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

ALTER TABLE `patterns`
  MODIFY `id` bigint(32) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

ALTER TABLE `responses`
  MODIFY `id` bigint(32) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

ALTER TABLE `tags`
  MODIFY `id` bigint(32) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
COMMIT;
