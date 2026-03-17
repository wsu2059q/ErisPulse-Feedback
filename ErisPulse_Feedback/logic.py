import time
import json
from typing import Optional, List, Dict, Tuple


class FeedbackGroupManager:
    
    def __init__(self, storage, logger):
        self.storage = storage
        self.logger = logger
        self.group_index_key = "fb_group_index"
        self.mapping_prefix = "fb_mapping:"
        self.group_prefix = "fb_group:"
    
    def create_group(self, group_name: str, admin_ids: List[str], 
                    source_group_id: str, config: Dict) -> str:
        # 生成反馈组ID
        group_id = self._generate_group_id()
        
        # 创建反馈组数据
        group_data = {
            "id": group_id,
            "name": group_name,
            "admin_ids": admin_ids,
            "allowed_groups": [source_group_id],
            "config": config,
            "created_at": int(time.time())
        }
        
        # 保存反馈组
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        
        # 映射群聊到反馈组
        self.storage.set(f"{self.mapping_prefix}{source_group_id}", group_id)
        
        # 更新反馈组索引
        group_index = self.storage.get(self.group_index_key, [])
        group_index.append(group_id)
        self.storage.set(self.group_index_key, group_index)
        
        self.logger.info(f"创建反馈组: {group_id} ({group_name}) by {admin_ids}")
        return group_id
    
    def add_group_to_feedback_group(self, group_id: str, source_group_id: str, 
                                 operator_id: str) -> Tuple[bool, str]:
        # 获取反馈组
        group_data = self.storage.get(f"{self.group_prefix}{group_id}")
        if not group_data:
            return False, "反馈组不存在"
        
        # 检查权限
        if operator_id not in group_data["admin_ids"]:
            return False, "无权限操作此反馈组"
        
        # 检查群聊是否已加入
        if source_group_id in group_data["allowed_groups"]:
            return False, "群聊已在此反馈组中"
        
        # 添加群聊
        group_data["allowed_groups"].append(source_group_id)
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        
        # 映射群聊到反馈组
        self.storage.set(f"{self.mapping_prefix}{source_group_id}", group_id)
        
        self.logger.info(f"群聊 {source_group_id} 加入反馈组 {group_id} by {operator_id}")
        return True, "成功"
    
    def get_group_by_source(self, source_group_id: str) -> Optional[Dict]:
        group_id = self.storage.get(f"{self.mapping_prefix}{source_group_id}")
        if not group_id:
            return None
        
        return self.storage.get(f"{self.group_prefix}{group_id}")
    
    def get_group(self, group_id: str) -> Optional[Dict]:
        return self.storage.get(f"{self.group_prefix}{group_id}")
    
    def update_group_config(self, group_id: str, config: Dict, 
                         operator_id: str) -> Tuple[bool, str]:
        group_data = self.storage.get(f"{self.group_prefix}{group_id}")
        if not group_data:
            return False, "反馈组不存在"
        
        if operator_id not in group_data["admin_ids"]:
            return False, "无权限操作此反馈组"
        
        group_data["config"].update(config)
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        
        self.logger.info(f"更新反馈组 {group_id} 配置 by {operator_id}")
        return True, "成功"
    
    def dissolve_group(self, group_id: str, operator_id: str) -> Tuple[bool, str]:
        # 获取反馈组
        group_data = self.storage.get(f"{self.group_prefix}{group_id}")
        if not group_data:
            return False, "反馈组不存在"
        
        # 检查权限：必须是创建者（admin_ids的第一个元素）
        if not group_data["admin_ids"]:
            return False, "反馈组数据异常"
        
        creator_id = group_data["admin_ids"][0]
        if operator_id != creator_id:
            return False, "只有反馈组创建者才能解散反馈组"
        
        # 删除所有群聊映射
        for source_group_id in group_data["allowed_groups"]:
            self.storage.delete(f"{self.mapping_prefix}{source_group_id}")
        
        # 删除所有反馈数据
        feedback_index = self.storage.get(f"fb_feedback_index:{group_id}", [])
        for feedback_id in feedback_index:
            self.storage.delete(f"fb_feedback:{group_id}:{feedback_id}")
        
        # 删除反馈索引
        self.storage.delete(f"fb_feedback_index:{group_id}")
        
        # 删除反馈组
        self.storage.delete(f"{self.group_prefix}{group_id}")
        
        # 从索引中移除
        group_index = self.storage.get(self.group_index_key, [])
        if group_id in group_index:
            group_index.remove(group_id)
            self.storage.set(self.group_index_key, group_index)
        
        self.logger.info(f"反馈组已解散: {group_id} ({group_data['name']}) by {operator_id}")
        return True, "反馈组已解散"
    
    def list_all_groups(self) -> List[Dict]:
        group_index = self.storage.get(self.group_index_key, [])
        groups = []
        
        for group_id in group_index:
            group_data = self.storage.get(f"{self.group_prefix}{group_id}")
            if group_data:
                groups.append(group_data)
        
        return groups
    
    def update_group_admins(self, group_id: str, new_admin_ids: List[str],
                          operator_id: str) -> Tuple[bool, str]:
        # 获取反馈组
        group_data = self.storage.get(f"{self.group_prefix}{group_id}")
        if not group_data:
            return False, "反馈组不存在"
        
        # 更新管理员列表
        group_data["admin_ids"] = new_admin_ids
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        
        self.logger.info(f"更新反馈组 {group_id} 管理员 by {operator_id}: {new_admin_ids}")
        return True, "成功"
    
    def _generate_group_id(self) -> str:
        key = "fb_group_next_id"
        next_id = self.storage.get(key, 1)
        group_id = f"group_{next_id}"
        self.storage.set(key, next_id + 1)
        return group_id


class FeedbackManager:
    
    def __init__(self, storage, logger, storage_prefix="fb_"):
        self.storage = storage
        self.logger = logger
        self.storage_prefix = storage_prefix
        self.feedback_prefix = f"{storage_prefix}feedback:"
        self.index_prefix = f"{storage_prefix}feedback_index:"
    
    def submit_feedback(self, feedback_group_id: str, source_group_id: str,
                      user_id: str, nickname: str, category: str, 
                      content: str, config: Dict, platform: str = "") -> Tuple[bool, str]:
        # 验证类别
        if category not in config.get("categories", []):
            categories = ", ".join(config["categories"])
            return False, f"无效的类别。请使用: {categories}"
        
        # 生成反馈ID
        feedback_id = self._generate_feedback_id(feedback_group_id)
        
        # 创建反馈数据
        feedback_data = {
            "id": feedback_id,
            "group_id": feedback_group_id,
            "source_group_id": source_group_id,
            "platform": platform,
            "user_id": user_id,
            "user_nickname": nickname,
            "category": category,
            "content": content,
            "status": "pending",
            "timestamp": int(time.time())
        }
        
        # 保存反馈
        storage_key = f"{self.feedback_prefix}{feedback_group_id}:{feedback_id}"
        self.storage.set(storage_key, feedback_data)
        
        # 更新索引
        index_key = f"{self.index_prefix}{feedback_group_id}"
        feedback_index = self.storage.get(index_key, [])
        feedback_index.append(feedback_id)
        self.storage.set(index_key, feedback_index)
        
        self.logger.info(f"反馈已提交: {feedback_id} (组: {feedback_group_id}) by {user_id}")
        return True, feedback_id
    
    def get_feedback(self, feedback_group_id: str, feedback_id: str) -> Optional[Dict]:
        storage_key = f"{self.feedback_prefix}{feedback_group_id}:{feedback_id}"
        return self.storage.get(storage_key)
    
    def update_feedback_status(self, feedback_group_id: str, feedback_id: str,
                             new_status: str) -> Optional[Tuple[str, Dict]]:
        storage_key = f"{self.feedback_prefix}{feedback_group_id}:{feedback_id}"
        feedback_data = self.storage.get(storage_key)
        if not feedback_data:
            return None
        
        old_status = feedback_data["status"]
        feedback_data["status"] = new_status
        self.storage.set(storage_key, feedback_data)
        
        self.logger.info(f"反馈状态更新: {feedback_id} {old_status} -> {new_status}")
        return old_status, feedback_data
    
    def list_all_feedbacks(self, feedback_group_id: str) -> List[Dict]:
        feedbacks = []
        
        # 使用索引获取所有反馈ID
        index_key = f"{self.index_prefix}{feedback_group_id}"
        feedback_ids = self.storage.get(index_key, [])
        
        for feedback_id in feedback_ids:
            data = self.storage.get(f"{self.feedback_prefix}{feedback_group_id}:{feedback_id}")
            if data:
                feedbacks.append(data)
        
        return feedbacks
    
    def list_feedbacks_filtered(self, feedback_group_id: str, category: Optional[str] = None,
                              status: Optional[str] = None, limit: int = 20) -> List[Dict]:
        all_feedbacks = self.list_all_feedbacks(feedback_group_id)
        
        # 筛选
        filtered = []
        for feedback in all_feedbacks:
            if category and feedback["category"] != category:
                continue
            
            if status and feedback["status"] != status:
                continue
            
            filtered.append(feedback)
        
        # 按时间排序（最新的在前）
        filtered.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return filtered[:limit]
    
    def _generate_feedback_id(self, feedback_group_id: str) -> str:
        key = f"{self.feedback_prefix}{feedback_group_id}:next_id"
        next_id = self.storage.get(key, 1)
        id_prefix = self.storage.get(f"fb_group:{feedback_group_id}.config.id_prefix", "#")
        feedback_id = f"{id_prefix}{next_id}"
        self.storage.set(key, next_id + 1)
        return feedback_id
    
    def import_feedbacks(self, feedback_group_id: str, feedbacks_data: List[Dict], 
                        mode: str = "merge") -> Tuple[bool, str, int]:
        if mode == "overwrite":
            # 覆盖模式：先清空现有数据
            self._clear_all_feedbacks(feedback_group_id)
        
        # 获取当前索引
        index_key = f"{self.index_prefix}{feedback_group_id}"
        feedback_index = self.storage.get(index_key, [])
        
        imported_count = 0
        skipped_count = 0
        
        for feedback_data in feedbacks_data:
            feedback_id = feedback_data.get("id")
            
            # 检查必要字段
            required_fields = ["id", "user_id", "user_nickname", "category", "content", "status"]
            if not all(field in feedback_data for field in required_fields):
                self.logger.warning(f"跳过不完整的反馈数据: {feedback_id}")
                skipped_count += 1
                continue
            
            # 合并模式：检查ID是否已存在
            if mode == "merge":
                if feedback_id in feedback_index:
                    skipped_count += 1
                    continue
            
            # 保存反馈
            storage_key = f"{self.feedback_prefix}{feedback_group_id}:{feedback_id}"
            
            # 确保数据包含必要的字段
            full_data = {
                "id": feedback_data["id"],
                "group_id": feedback_group_id,
                "source_group_id": feedback_data.get("source_group_id", ""),
                "platform": feedback_data.get("platform", ""),
                "user_id": feedback_data["user_id"],
                "user_nickname": feedback_data["user_nickname"],
                "category": feedback_data["category"],
                "content": feedback_data["content"],
                "status": feedback_data["status"],
                "timestamp": feedback_data.get("timestamp", int(time.time()))
            }
            
            self.storage.set(storage_key, full_data)
            
            # 更新索引
            if feedback_id not in feedback_index:
                feedback_index.append(feedback_id)
            
            imported_count += 1
        
        # 保存更新后的索引
        self.storage.set(index_key, feedback_index)
        
        # 更新反馈ID计数器（避免ID冲突）
        if imported_count > 0:
            self._update_feedback_id_counter(feedback_group_id, feedback_index)
        
        message = f"成功导入 {imported_count} 条反馈"
        if skipped_count > 0:
            message += f"，跳过 {skipped_count} 条"
        
        self.logger.info(f"反馈数据导入完成: 组{feedback_group_id}, 导入{imported_count}条, 跳过{skipped_count}条")
        return True, message, imported_count
    
    def _clear_all_feedbacks(self, feedback_group_id: str):
        index_key = f"{self.index_prefix}{feedback_group_id}"
        feedback_ids = self.storage.get(index_key, [])
        
        # 删除所有反馈
        for feedback_id in feedback_ids:
            storage_key = f"{self.feedback_prefix}{feedback_group_id}:{feedback_id}"
            self.storage.delete(storage_key)
        
        # 清空索引
        self.storage.delete(index_key)
        
        self.logger.info(f"已清空反馈组 {feedback_group_id} 的所有反馈数据")
    
    def _update_feedback_id_counter(self, feedback_group_id: str, feedback_index: List[str]):
        if not feedback_index:
            return
        
        # 提取所有ID中的数字部分
        max_num = 0
        for feedback_id in feedback_index:
            # 去除前缀后提取数字
            import re
            match = re.search(r'\d+', feedback_id)
            if match:
                num = int(match.group())
                if num > max_num:
                    max_num = num
        
        # 更新计数器
        key = f"{self.feedback_prefix}{feedback_group_id}:next_id"
        self.storage.set(key, max_num + 1)
        
        self.logger.info(f"更新反馈组 {feedback_group_id} 的ID计数器到 {max_num + 1}")


class FeedbackLogic:
    
    def __init__(self, sdk, config: Dict):
        self.sdk = sdk
        self.storage = sdk.storage
        self.logger = sdk.logger.get_child("FeedbackLogic")
        self.config = config
        
        # 初始化管理器
        self.group_manager = FeedbackGroupManager(self.storage, self.logger)
    
    def get_feedback_manager(self, feedback_group_id: str) -> FeedbackManager:
        return FeedbackManager(self.storage, self.logger, self.config.get("storage_prefix", "fb_"))
    
    def is_global_admin(self, user_id: str) -> bool:
        global_admins = self.config.get("global_admins", [])
        return user_id in global_admins
    
    def is_group_admin(self, group_data: Dict, user_id: str) -> bool:
        """
        检查是否为反馈组创建者
        """
        if not group_data:
            return False
        return user_id in group_data.get("admin_ids", [])
