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
    
    def _ensure_group_schema(self, group_data):
        if not group_data:
            return group_data
        if "creator_id" not in group_data:
            admin_ids = group_data.get("admin_ids", [])
            group_data["creator_id"] = admin_ids[0] if admin_ids else ""
            group_data["admin_ids"] = admin_ids[1:] if len(admin_ids) > 1 else []
            if "maintainer_ids" not in group_data:
                group_data["maintainer_ids"] = []
            self.storage.set(f"{self.group_prefix}{group_data['id']}", group_data)
            self.logger.info(f"已迁移反馈组 {group_data['id']} 到新的权限格式")
        return group_data
    
    def create_group(self, group_name: str, creator_id: str,
                     source_group_id: str, config: Dict) -> str:
        group_id = self._generate_group_id()
        
        group_data = {
            "id": group_id,
            "name": group_name,
            "creator_id": creator_id,
            "admin_ids": [],
            "maintainer_ids": [],
            "allowed_groups": [source_group_id],
            "config": config,
            "created_at": int(time.time())
        }
        
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        self.storage.set(f"{self.mapping_prefix}{source_group_id}", group_id)
        
        group_index = self.storage.get(self.group_index_key, [])
        group_index.append(group_id)
        self.storage.set(self.group_index_key, group_index)
        
        self.logger.info(f"创建反馈组: {group_id} ({group_name}) by {creator_id}")
        return group_id
    
    def add_group_to_feedback_group(self, group_id: str, source_group_id: str,
                                    operator_id: str) -> Tuple[bool, str]:
        group_data = self.get_group(group_id)
        if not group_data:
            return False, "反馈组不存在"
        
        if operator_id != group_data["creator_id"] and operator_id not in group_data["admin_ids"]:
            return False, "无权限操作此反馈组（需要管理员权限）"
        
        if source_group_id in group_data["allowed_groups"]:
            return False, "群聊已在此反馈组中"
        
        group_data["allowed_groups"].append(source_group_id)
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        
        self.storage.set(f"{self.mapping_prefix}{source_group_id}", group_id)
        
        self.logger.info(f"群聊 {source_group_id} 加入反馈组 {group_id} by {operator_id}")
        return True, "成功"
    
    def remove_group_from_feedback_group(self, group_id: str,
                                         source_group_id: str) -> Tuple[bool, str]:
        group_data = self.get_group(group_id)
        if not group_data:
            return False, "反馈组不存在"
        
        if source_group_id not in group_data["allowed_groups"]:
            return False, "此群聊不在该反馈组中"
        
        if len(group_data["allowed_groups"]) <= 1:
            return False, "这是反馈组中唯一的群聊，无法退出。如需解散请联系创建者"
        
        group_data["allowed_groups"].remove(source_group_id)
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        self.storage.delete(f"{self.mapping_prefix}{source_group_id}")
        
        self.logger.info(f"群聊 {source_group_id} 退出反馈组 {group_id}")
        return True, "成功退出反馈组"
    
    def get_group_by_source(self, source_group_id: str) -> Optional[Dict]:
        group_id = self.storage.get(f"{self.mapping_prefix}{source_group_id}")
        if not group_id:
            return None
        return self._ensure_group_schema(
            self.storage.get(f"{self.group_prefix}{group_id}")
        )
    
    def get_group(self, group_id: str) -> Optional[Dict]:
        return self._ensure_group_schema(
            self.storage.get(f"{self.group_prefix}{group_id}")
        )
    
    def update_group_config(self, group_id: str, config: Dict,
                            operator_id: str) -> Tuple[bool, str]:
        group_data = self.get_group(group_id)
        if not group_data:
            return False, "反馈组不存在"
        
        if operator_id != group_data["creator_id"] and operator_id not in group_data["admin_ids"]:
            return False, "无权限操作此反馈组（需要管理员权限）"
        
        group_data["config"].update(config)
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        
        self.logger.info(f"更新反馈组 {group_id} 配置 by {operator_id}")
        return True, "成功"
    
    def dissolve_group(self, group_id: str, operator_id: str) -> Tuple[bool, str]:
        group_data = self.get_group(group_id)
        if not group_data:
            return False, "反馈组不存在"
        
        if not group_data["creator_id"]:
            return False, "反馈组数据异常"
        
        if operator_id != group_data["creator_id"]:
            return False, "只有反馈组创建者才能解散反馈组"
        
        for source_group_id in group_data["allowed_groups"]:
            self.storage.delete(f"{self.mapping_prefix}{source_group_id}")
        
        feedback_index = self.storage.get(f"fb_feedback_index:{group_id}", [])
        for feedback_id in feedback_index:
            self.storage.delete(f"fb_feedback:{group_id}:{feedback_id}")
        
        self.storage.delete(f"fb_feedback_index:{group_id}")
        self.storage.delete(f"{self.group_prefix}{group_id}")
        
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
            group_data = self.get_group(group_id)
            if group_data:
                groups.append(group_data)
        
        return groups
    
    def update_group_admins(self, group_id: str, new_admin_ids: List[str],
                            operator_id: str) -> Tuple[bool, str]:
        group_data = self.get_group(group_id)
        if not group_data:
            return False, "反馈组不存在"
        
        group_data["admin_ids"] = new_admin_ids
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        
        self.logger.info(f"更新反馈组 {group_id} 管理员 by {operator_id}: {new_admin_ids}")
        return True, "成功"
    
    def update_group_creator(self, group_id: str, new_creator_id: str,
                             operator_id: str) -> Tuple[bool, str]:
        group_data = self.get_group(group_id)
        if not group_data:
            return False, "反馈组不存在"
        
        group_data["creator_id"] = new_creator_id
        if new_creator_id in group_data["admin_ids"]:
            group_data["admin_ids"].remove(new_creator_id)
        if new_creator_id in group_data.get("maintainer_ids", []):
            group_data["maintainer_ids"].remove(new_creator_id)
        
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        
        self.logger.info(f"更新反馈组 {group_id} 创建者 by {operator_id}: {new_creator_id}")
        return True, "成功"
    
    def add_admin(self, group_id: str, user_id: str) -> Tuple[bool, str]:
        group_data = self.get_group(group_id)
        if not group_data:
            return False, "反馈组不存在"
        if user_id == group_data["creator_id"]:
            return False, "该用户是创建者，无法设为管理员"
        if user_id in group_data["admin_ids"]:
            return False, "该用户已是管理员"
        if user_id in group_data.get("maintainer_ids", []):
            group_data["maintainer_ids"].remove(user_id)
        group_data["admin_ids"].append(user_id)
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        self.logger.info(f"反馈组 {group_id} 添加管理员: {user_id}")
        return True, "成功"
    
    def remove_admin(self, group_id: str, user_id: str) -> Tuple[bool, str]:
        group_data = self.get_group(group_id)
        if not group_data:
            return False, "反馈组不存在"
        if user_id not in group_data["admin_ids"]:
            return False, "该用户不是管理员"
        group_data["admin_ids"].remove(user_id)
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        self.logger.info(f"反馈组 {group_id} 移除管理员: {user_id}")
        return True, "成功"
    
    def add_maintainer(self, group_id: str, user_id: str) -> Tuple[bool, str]:
        group_data = self.get_group(group_id)
        if not group_data:
            return False, "反馈组不存在"
        if user_id == group_data["creator_id"]:
            return False, "该用户是创建者"
        if user_id in group_data["admin_ids"]:
            return False, "该用户已是管理员，无需添加为维护者"
        if user_id in group_data.get("maintainer_ids", []):
            return False, "该用户已是维护者"
        group_data.setdefault("maintainer_ids", []).append(user_id)
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        self.logger.info(f"反馈组 {group_id} 添加维护者: {user_id}")
        return True, "成功"
    
    def remove_maintainer(self, group_id: str, user_id: str) -> Tuple[bool, str]:
        group_data = self.get_group(group_id)
        if not group_data:
            return False, "反馈组不存在"
        if user_id not in group_data.get("maintainer_ids", []):
            return False, "该用户不是维护者"
        group_data["maintainer_ids"].remove(user_id)
        self.storage.set(f"{self.group_prefix}{group_id}", group_data)
        self.logger.info(f"反馈组 {group_id} 移除维护者: {user_id}")
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
        if category not in config.get("categories", []):
            categories = ", ".join(config["categories"])
            return False, f"无效的类别。请使用: {categories}"
        
        feedback_id = self._generate_feedback_id(feedback_group_id)
        
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
        
        storage_key = f"{self.feedback_prefix}{feedback_group_id}:{feedback_id}"
        self.storage.set(storage_key, feedback_data)
        
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
    
    def update_feedback(self, feedback_group_id: str, feedback_id: str,
                        updates: Dict) -> Optional[Dict]:
        storage_key = f"{self.feedback_prefix}{feedback_group_id}:{feedback_id}"
        feedback_data = self.storage.get(storage_key)
        if not feedback_data:
            return None
        
        if "category" in updates:
            feedback_data["category"] = updates["category"]
        if "content" in updates:
            feedback_data["content"] = updates["content"]
        
        self.storage.set(storage_key, feedback_data)
        self.logger.info(f"反馈已更新: {feedback_id}")
        return feedback_data
    
    def list_all_feedbacks(self, feedback_group_id: str) -> List[Dict]:
        feedbacks = []
        
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
        
        filtered = []
        for feedback in all_feedbacks:
            if category and feedback["category"] != category:
                continue
            if status and feedback["status"] != status:
                continue
            filtered.append(feedback)
        
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
            self._clear_all_feedbacks(feedback_group_id)
        
        index_key = f"{self.index_prefix}{feedback_group_id}"
        feedback_index = self.storage.get(index_key, [])
        
        imported_count = 0
        skipped_count = 0
        
        for feedback_data in feedbacks_data:
            feedback_id = feedback_data.get("id")
            
            required_fields = ["id", "user_id", "user_nickname", "category", "content", "status"]
            if not all(field in feedback_data for field in required_fields):
                self.logger.warning(f"跳过不完整的反馈数据: {feedback_id}")
                skipped_count += 1
                continue
            
            if mode == "merge":
                if feedback_id in feedback_index:
                    skipped_count += 1
                    continue
            
            storage_key = f"{self.feedback_prefix}{feedback_group_id}:{feedback_id}"
            
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
            
            if feedback_id not in feedback_index:
                feedback_index.append(feedback_id)
            
            imported_count += 1
        
        self.storage.set(index_key, feedback_index)
        
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
        
        for feedback_id in feedback_ids:
            storage_key = f"{self.feedback_prefix}{feedback_group_id}:{feedback_id}"
            self.storage.delete(storage_key)
        
        self.storage.delete(index_key)
        self.logger.info(f"已清空反馈组 {feedback_group_id} 的所有反馈数据")
    
    def _update_feedback_id_counter(self, feedback_group_id: str, feedback_index: List[str]):
        if not feedback_index:
            return
        
        max_num = 0
        for feedback_id in feedback_index:
            import re
            match = re.search(r'\d+', feedback_id)
            if match:
                num = int(match.group())
                if num > max_num:
                    max_num = num
        
        key = f"{self.feedback_prefix}{feedback_group_id}:next_id"
        self.storage.set(key, max_num + 1)
        self.logger.info(f"更新反馈组 {feedback_group_id} 的ID计数器到 {max_num + 1}")


class FeedbackLogic:
    
    def __init__(self, sdk, config: Dict):
        self.sdk = sdk
        self.storage = sdk.storage
        self.logger = sdk.logger.get_child("FeedbackLogic")
        self.config = config
        
        self.group_manager = FeedbackGroupManager(self.storage, self.logger)
    
    def get_feedback_manager(self, feedback_group_id: str) -> FeedbackManager:
        return FeedbackManager(self.storage, self.logger, self.config.get("storage_prefix", "fb_"))
    
    def is_global_admin(self, user_id: str) -> bool:
        global_admins = self.config.get("global_admins", [])
        return user_id in global_admins
    
    def get_user_role(self, group_data: Dict, user_id: str) -> Optional[str]:
        if not group_data:
            return None
        if user_id == group_data.get("creator_id"):
            return "creator"
        if user_id in group_data.get("admin_ids", []):
            return "admin"
        if user_id in group_data.get("maintainer_ids", []):
            return "maintainer"
        return None
    
    def get_role_display_name(self, role: str) -> str:
        names = {"creator": "创建者", "admin": "管理员", "maintainer": "维护者"}
        return names.get(role, "未知")
    
    def has_permission(self, group_data: Dict, user_id: str, required_level: str) -> bool:
        if self.is_global_admin(user_id):
            return True
        role = self.get_user_role(group_data, user_id)
        if role is None:
            return False
        hierarchy = {"creator": 3, "admin": 2, "maintainer": 1}
        return hierarchy.get(role, 0) >= hierarchy.get(required_level, 0)
    
    def can_edit_feedback(self, group_data: Dict, user_id: str, feedback_data: Dict) -> bool:
        if self.is_global_admin(user_id):
            return True
        role = self.get_user_role(group_data, user_id)
        if role in ["creator", "admin", "maintainer"]:
            return True
        return user_id == feedback_data.get("user_id")
    
    def can_modify_status(self, group_data: Dict, user_id: str) -> bool:
        if self.is_global_admin(user_id):
            return True
        role = self.get_user_role(group_data, user_id)
        return role in ["creator", "admin", "maintainer"]
    
    def is_group_admin(self, group_data: Dict, user_id: str) -> bool:
        return self.has_permission(group_data, user_id, "admin")
