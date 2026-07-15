-- 提示词模板表
CREATE TABLE `prompt_template` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID自增',
  `title` varchar(200) NOT NULL COMMENT '提示词标题',
  `content` text NOT NULL COMMENT '提示词内容',
  `category` varchar(50) DEFAULT '通用' COMMENT '分类',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='提示词模板表';

-- AI评测记录表
CREATE TABLE `ai_eval_record` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID，自增',
  `prompt_id` int DEFAULT NULL COMMENT '关联的提示词ID',
  `input_content` text NOT NULL COMMENT '输入内容',
  `eval_result` text COMMENT 'AI评测结果',
  `score` decimal(3,1) DEFAULT NULL COMMENT '评分',
  `eval_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '评测时间',
  `record_type` varchar(20) DEFAULT 'chat' COMMENT '记录类型：chat对话/evaluate评测',
  PRIMARY KEY (`id`),
  KEY `prompt_id` (`prompt_id`),
  CONSTRAINT `ai_eval_record_ibfk_1` FOREIGN KEY (`prompt_id`) REFERENCES `prompt_template` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='AI评测记录表';