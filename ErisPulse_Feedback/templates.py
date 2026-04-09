from datetime import datetime
import json
from typing import Dict, List, Optional


class FeedbackTemplates:
    
    # 固定的状态映射
    STATUS_MAP = {
        "pending": "待处理",
        "processing": "处理中",
        "completed": "已完成",
        "rejected": "搁置"
    }
    
    # 固定的状态颜色
    STATUS_COLORS = {
        "pending": "rgba(255, 167, 38, 0.2)",
        "processing": "rgba(33, 150, 243, 0.2)",
        "completed": "rgba(76, 175, 80, 0.2)",
        "rejected": "rgba(158, 158, 158, 0.2)"
    }
    
    # 固定的类别颜色
    CATEGORY_COLORS = {
        "功能": "rgba(156, 39, 176, 0.2)",
        "优化": "rgba(255, 152, 0, 0.2)",
        "建议": "rgba(3, 169, 244, 0.2)",
        "bug": "rgba(244, 67, 54, 0.2)"
    }
    
    @classmethod
    def _format_time(cls, timestamp):
        """格式化时间戳"""
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
    
    @classmethod
    def _get_status_text(cls, status):
        """获取状态文本"""
        return cls.STATUS_MAP.get(status, status)
    
    @classmethod
    def _get_status_color(cls, status):
        """获取状态背景色"""
        return cls.STATUS_COLORS.get(status, "rgba(158, 158, 158, 0.2)")
    
    @classmethod
    def _get_category_color(cls, category):
        """获取类别背景色"""
        return cls.CATEGORY_COLORS.get(category, "rgba(158, 158, 158, 0.2)")
    
    # ==================== 反馈组管理模板 ====================
    
    @classmethod
    def build_group_created(cls, group_id: str, group_name: str):
        """构建反馈组创建成功消息"""
        html = f"""
<div style="padding: 16px; border-radius: 8px; text-align: center;">
    <div style="color: #2e7d32; font-size: 18px; font-weight: bold; margin-bottom: 12px;">反馈组创建成功</div>
    <div style="font-size: 14px; margin-bottom: 8px;">
        组ID: {group_id}<br>
        组名: {group_name}
    </div>
</div>"""
        
        markdown = f"**反馈组创建成功**\n\n组ID: {group_id}\n组名: {group_name}"
        
        text = f"反馈组创建成功\n\n组ID: {group_id}\n组名: {group_name}"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    # ==================== 解散反馈组模板 ====================
    
    @classmethod
    def build_dissolve_confirm(cls, group_name: str, group_id: str):
        """构建解散确认消息"""
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 14px; font-weight: bold; margin-bottom: 8px;">确认解散反馈组</div>
    <div style="font-size: 13px; margin-bottom: 8px;">
        你确定要解散反馈组 <strong>{group_name}</strong> ({group_id}) 吗？
    </div>
    <div style="padding: 10px; background: rgba(183, 28, 28, 0.1); border-radius: 6px; margin-bottom: 8px;">
        <div style="color: #b71c1c; font-size: 12px;">⚠️ 警告</div>
        <div style="font-size: 12px;">解散后，所有反馈数据将被永久删除，无法恢复！</div>
    </div>
    <div style="font-size: 12px;">回复 '是' 或 '否' (30秒内有效)</div>
</div>"""
        
        markdown = f"""**确认解散反馈组**

你确定要解散反馈组 **{group_name}** ({group_id}) 吗？

⚠️ **警告**
解散后，所有反馈数据将被永久删除，无法恢复！

回复 '是' 或 '否' (30秒内有效)"""
        
        text = f"""确认解散反馈组

你确定要解散反馈组 {group_name} ({group_id}) 吗？

⚠️ 警告
解散后，所有反馈数据将被永久删除，无法恢复！

回复 '是' 或 '否' (30秒内有效)"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_group_dissolved(cls, group_id: str, group_name: str):
        """构建解散成功消息"""
        html = f"""
<div style="padding: 16px; border-radius: 8px; text-align: center;">
    <div style="color: #2e7d32; font-size: 16px; font-weight: bold; margin-bottom: 12px;">反馈组已解散</div>
    <div style="font-size: 14px; margin-bottom: 8px;">
        组ID: {group_id}<br>
        组名: {group_name}
    </div>
    <div style="padding: 10px; background: rgba(76, 175, 80, 0.1); border-radius: 6px;">
        <div style="font-size: 12px;">所有反馈数据已删除</div>
    </div>
</div>"""
        
        markdown = f"""**反馈组已解散**

组ID: {group_id}
组名: {group_name}

所有反馈数据已删除"""
        
        text = f"""反馈组已解散

组ID: {group_id}
组名: {group_name}

所有反馈数据已删除"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_exit_confirm(cls, group_name: str, group_id: str):
        """构建退出反馈组确认消息"""
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #e65100; font-size: 14px; font-weight: bold; margin-bottom: 8px;">确认退出反馈组</div>
    <div style="font-size: 13px; margin-bottom: 8px;">
        确认要退出反馈组 <strong>{group_name}</strong> ({group_id}) 吗？
    </div>
    <div style="font-size: 12px;">回复 '是' 或 '否' (30秒内有效)</div>
</div>"""
        
        markdown = f"""**确认退出反馈组**

确认要退出反馈组 **{group_name}** ({group_id}) 吗？

回复 '是' 或 '否' (30秒内有效)"""
        
        text = f"""确认退出反馈组

确认要退出反馈组 {group_name} ({group_id}) 吗？

回复 '是' 或 '否' (30秒内有效)"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_group_exited(cls, group_name: str, group_id: str):
        """构建退出成功消息"""
        html = f"""
<div style="padding: 16px; border-radius: 8px; text-align: center;">
    <div style="color: #2e7d32; font-size: 16px; font-weight: bold; margin-bottom: 12px;">已退出反馈组</div>
    <div style="font-size: 14px; margin-bottom: 8px;">
        已退出反馈组: {group_name} ({group_id})
    </div>
</div>"""
        
        markdown = f"""**已退出反馈组**

已退出反馈组: {group_name} ({group_id})"""
        
        text = f"""已退出反馈组

已退出反馈组: {group_name} ({group_id})"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    # ==================== 全局管理员模板 ====================
    
    @classmethod
    def build_global_admin_menu(cls):
        """构建全局管理员菜单"""
        html = """
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 16px; font-weight: bold; margin-bottom: 12px;">全局管理员菜单</div>
    
    <div style="padding: 10px; background: rgba(183, 28, 28, 0.1); border-radius: 6px; margin-bottom: 12px;">
        <div style="color: #b71c1c; font-size: 13px;">⚠️ 管理员权限</div>
        <div style="font-size: 12px;">此菜单仅限全局管理员使用，请谨慎操作</div>
    </div>
    
    <div style="font-size: 13px; margin-bottom: 8px;">请选择操作：</div>
    <div style="font-size: 13px; border: 1px solid #e0e0e0; padding: 10px; border-radius: 6px;">
        1. 列出所有反馈组
        2. 重新设定组管理员
        3. 解散反馈组
    </div>
    <div style="font-size: 12px; margin-top: 8px;">回复序号选择操作（60秒内有效）</div>
</div>"""
        
        markdown = """**全局管理员菜单**

⚠️ **管理员权限**
此菜单仅限全局管理员使用，请谨慎操作

请选择操作：

1. 列出所有反馈组
2. 重新设定组管理员
3. 解散反馈组

回复序号选择操作（60秒内有效）"""
        
        text = """全局管理员菜单

⚠️ 管理员权限
此菜单仅限全局管理员使用，请谨慎操作

请选择操作：

1. 列出所有反馈组
2. 重新设定组管理员
3. 解散反馈组

回复序号选择操作（60秒内有效）"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_all_groups_list(cls, groups: List[Dict]):
        """构建所有反馈组列表"""
        groups_html = ""
        for i, group in enumerate(groups, 1):
            created_time = cls._format_time(group["created_at"])
            admins = ", ".join(group["admin_ids"][:2])  # 只显示前2个管理员
            
            groups_html += f"""
<div style="padding: 10px; border: 1px solid #e0e0e0; border-radius: 6px; margin-bottom: 8px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <strong style="font-size: 14px;">{i}. {group['name']}</strong>
        <div style="padding: 4px 8px; background: rgba(21, 101, 192, 0.15); border-radius: 4px; font-size: 12px; color: #1565c0;">
            {group['id']}
        </div>
    </div>
    <div style="font-size: 12px; margin-bottom: 4px;">创建者: {group['admin_ids'][0] if group['admin_ids'] else 'N/A'}</div>
    <div style="font-size: 12px; margin-bottom: 4px;">管理员: {admins}</div>
    <div style="font-size: 12px;">关联群聊数: {len(group.get('allowed_groups', []))}</div>
    <div style="font-size: 11px; color: #666; margin-top: 4px;">创建时间: {created_time}</div>
</div>"""
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 16px; font-weight: bold; margin-bottom: 12px;">所有反馈组</div>
    <div style="padding: 8px; background: rgba(76, 175, 80, 0.1); border-radius: 6px; margin-bottom: 12px;">
        <div style="font-size: 13px;">共 {len(groups)} 个反馈组</div>
    </div>
    {groups_html}
</div>"""
        
        groups_md = ""
        for i, group in enumerate(groups, 1):
            created_time = cls._format_time(group["created_at"])
            admins = ", ".join(group["admin_ids"][:2])
            groups_md += f"""**{i}. {group['name']}** ({group['id']})
创建者: {group['admin_ids'][0] if group['admin_ids'] else 'N/A'}
管理员: {admins}
关联群聊数: {len(group.get('allowed_groups', []))}
创建时间: {created_time}

"""
        
        markdown = f"""**所有反馈组**

共 {len(groups)} 个反馈组

{groups_md}"""
        
        groups_text = ""
        for i, group in enumerate(groups, 1):
            created_time = cls._format_time(group["created_at"])
            admins = ", ".join(group["admin_ids"][:2])
            groups_text += f"""{i}. {group['name']} ({group['id']})
创建者: {group['admin_ids'][0] if group['admin_ids'] else 'N/A'}
管理员: {admins}
关联群聊数: {len(group.get('allowed_groups', []))}
创建时间: {created_time}

"""
        
        text = f"""所有反馈组

共 {len(groups)} 个反馈组

{groups_text}"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_current_admins(cls, group_id: str, group_name: str, current_admins: List[str]):
        """构建当前管理员信息"""
        admins_text = "\n".join([f"- {admin}" for admin in current_admins])
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">反馈组: {group_name} ({group_id})</div>
    
    <div style="padding: 10px; background: rgba(21, 101, 192, 0.05); border-radius: 6px;">
        <div style="font-size: 13px; margin-bottom: 6px;">当前管理员列表：</div>
        <div style="font-size: 12px;">{admins_text}</div>
    </div>
    
    <div style="font-size: 12px; color: #666; margin-top: 8px;">创建者: {current_admins[0] if current_admins else 'N/A'}</div>
</div>"""
        
        markdown = f"""**反馈组:** {group_name} ({group_id})

**当前管理员列表：**
{admins_text}

创建者: {current_admins[0] if current_admins else 'N/A'}"""
        
        text = f"""反馈组: {group_name} ({group_id})

当前管理员列表：
{admins_text}

创建者: {current_admins[0] if current_admins else 'N/A'}"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_admins_updated(cls, group_id: str, new_admins: List[str]):
        """构建管理员更新成功消息"""
        admins_text = ", ".join(new_admins[:3])  # 只显示前3个
        if len(new_admins) > 3:
            admins_text += f" 等{len(new_admins)}个"
        
        html = f"""
<div style="padding: 16px; border-radius: 8px; text-align: center;">
    <div style="color: #2e7d32; font-size: 16px; font-weight: bold; margin-bottom: 12px;">管理员已更新</div>
    <div style="font-size: 14px; margin-bottom: 8px;">
        反馈组: {group_id}
    </div>
    <div style="font-size: 14px;">
        新管理员: {admins_text}
    </div>
    <div style="font-size: 12px; color: #666; margin-top: 8px;">创建者: {new_admins[0]}</div>
</div>"""
        
        markdown = f"""**管理员已更新**

反馈组: {group_id}

新管理员: {admins_text}

创建者: {new_admins[0]}"""
        
        text = f"""管理员已更新

反馈组: {group_id}

新管理员: {admins_text}

创建者: {new_admins[0]}"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_input_prompt(cls, message: str):
        """构建输入提示"""
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="font-size: 13px;">{message}</div>
    <div style="font-size: 12px;">回复取消可终止操作（60秒内有效）</div>
</div>"""
        
        markdown = f"{message}\n\n回复取消可终止操作（60秒内有效）"
        
        text = f"{message}\n\n回复取消可终止操作（60秒内有效）"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_group_joined(cls, group_id: str, group_name: str):
        """构建加入反馈组成功消息"""
        html = f"""
<div style="padding: 16px; border-radius: 8px; text-align: center;">
    <div style="color: #2e7d32; font-size: 16px; font-weight: bold; margin-bottom: 12px;">成功加入反馈组</div>
    <div style="font-size: 14px; margin-bottom: 8px;">
        组ID: {group_id}<br>
        组名: {group_name}
    </div>
</div>"""
        
        markdown = f"**成功加入反馈组**\n\n组ID: {group_id}\n组名: {group_name}"
        
        text = f"成功加入反馈组\n\n组ID: {group_id}\n组名: {group_name}"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_group_info(cls, group_data: Dict):
        """构建反馈组信息"""
        created_time = cls._format_time(group_data["created_at"])
        admins = ", ".join(group_data["admin_ids"])
        groups = ", ".join(group_data["allowed_groups"])
        config = group_data["config"]
        categories = ", ".join(config.get("categories", []))
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 16px; font-weight: bold; margin-bottom: 12px;">反馈组信息</div>
    
    <div style="margin-bottom: 12px; border: 1px solid #e0e0e0; padding: 12px; border-radius: 6px;">
        <div style="margin-bottom: 8px;"><strong>组ID:</strong> {group_data['id']}</div>
        <div style="margin-bottom: 8px;"><strong>组名:</strong> {group_data['name']}</div>
        <div style="margin-bottom: 8px;"><strong>管理员:</strong> {admins}</div>
        <div style="margin-bottom: 8px;"><strong>关联群聊:</strong> {groups}</div>
        <div style="margin-bottom: 8px;"><strong>创建时间:</strong> {created_time}</div>
    </div>
    
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">配置</div>
    <div style="border: 1px solid #e0e0e0; padding: 12px; border-radius: 6px;">
        <div style="margin-bottom: 8px;"><strong>类别:</strong> {categories}</div>
        <div style="margin-bottom: 8px;"><strong>超时时间:</strong> {config.get('timeout', 60)}秒</div>
        <div style="margin-bottom: 8px;"><strong>内容最大长度:</strong> {config.get('max_content_length', 500)}字</div>
        <div><strong>反馈ID前缀:</strong> {config.get('id_prefix', '#')}</div>
    </div>
</div>"""
        
        markdown = f"""**反馈组信息**

**基本信息**
组ID: {group_data['id']}
组名: {group_data['name']}
管理员: {admins}
关联群聊: {groups}
创建时间: {created_time}

**配置**
类别: {categories}
超时时间: {config.get('timeout', 60)}秒
内容最大长度: {config.get('max_content_length', 500)}字
反馈ID前缀: {config.get('id_prefix', '#')}"""
        
        text = f"""反馈组信息

基本信息
组ID: {group_data['id']}
组名: {group_data['name']}
管理员: {admins}
关联群聊: {groups}
创建时间: {created_time}

配置
类别: {categories}
超时时间: {config.get('timeout', 60)}秒
内容最大长度: {config.get('max_content_length', 500)}字
反馈ID前缀: {config.get('id_prefix', '#')}"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_no_feedback_group(cls):
        """构建无反馈组消息"""
        html = """
<div style="padding: 30px; border-radius: 8px; text-align: center;">
    <div style="color: #666; font-size: 16px; font-weight: bold; margin-bottom: 8px;">当前群聊未设置反馈组</div>
    <div style="color: #999; font-size: 14px;">
        请使用 <strong>/设置反馈组</strong> 命令创建新的反馈组
    </div>
</div>"""
        
        markdown = """**当前群聊未设置反馈组**

请管理员使用 `/设置反馈组` 命令创建新的反馈组"""
        
        text = """当前群聊未设置反馈组

请管理员使用 /设置反馈组 命令创建新的反馈组"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_config_updated(cls):
        """构建配置更新成功消息"""
        html = """
<div style="padding: 16px; border-radius: 8px; text-align: center;">
    <div style="color: #2e7d32; font-size: 16px; font-weight: bold;">配置已更新</div>
</div>"""
        
        markdown = "**配置已更新**"
        
        text = "配置已更新"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    # ==================== 提交反馈相关模板 ====================
    
    @classmethod
    def build_category_selection(cls, categories: List[str]):
        """构建类别选择提示"""
        categories_menu = "\n".join([f"{i+1}. {cat}" for i, cat in enumerate(categories)])
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">提交反馈</div>
    <div style="font-size: 13px; margin-bottom: 8px;">请选择反馈类别：</div>
    <div style="font-size: 13px; border: 1px solid #e0e0e0; padding: 10px; border-radius: 6px;">
        {categories_menu}
    </div>
    <div style="font-size: 12px; margin-top: 8px;">回复序号或类别名称（60秒内有效）</div>
</div>"""
        
        markdown = f"**提交反馈**\n\n请选择反馈类别：\n\n```\n{categories_menu}\n```\n\n回复序号或类别名称（60秒内有效）"
        
        text = f"提交反馈\n\n请选择反馈类别：\n{categories_menu}\n\n回复序号或类别名称（60秒内有效）"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_content_prompt(cls, category: str, max_length: int):
        """构建内容输入提示"""
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">已选择类别：{category}</div>
    <div style="font-size: 13px; margin-bottom: 8px;">请输入反馈内容（{max_length}字以内）：</div>
    <div style="font-size: 12px;">回复取消可终止提交（120秒内有效）</div>
</div>"""
        
        markdown = f"**已选择类别：** {category}\n\n请输入反馈内容（{max_length}字以内）：\n\n回复取消可终止提交（120秒内有效）"
        
        text = f"已选择类别：{category}\n\n请输入反馈内容（{max_length}字以内）：\n\n回复取消可终止提交（120秒内有效）"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_success(cls, feedback_id: str, category: str):
        """构建提交成功消息"""
        html = f"""
<div style="padding: 16px; border-radius: 8px; text-align: center;">
    <div style="color: #2e7d32; font-size: 18px; font-weight: bold; margin-bottom: 12px;">反馈已提交成功</div>
    <div style="font-size: 14px; margin-bottom: 8px;">
        编号: {feedback_id}<br>
        类别: {category}<br>
        状态: 待处理
    </div>
</div>"""
        
        markdown = f"**反馈已提交成功**\n\n编号: {feedback_id}\n类别: {category}\n状态: 待处理"
        
        text = f"反馈已提交成功\n\n编号: {feedback_id}\n类别: {category}\n状态: 待处理"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    # ==================== 反馈列表相关模板 ====================
    
    @classmethod
    def build_feedback_list(cls, feedbacks: List[Dict], categories: List[str], show_status: Optional[str] = None):
        """构建反馈列表"""
        # 按状态分组
        status_feedbacks = {
            "pending": [],
            "processing": [],
            "completed": [],
            "rejected": []
        }
        
        for feedback in feedbacks:
            status_feedbacks[feedback["status"]].append(feedback)
        
        # 按类别分组统计
        category_stats = {}
        for category in categories:
            category_feedbacks = [f for f in feedbacks if f["category"] == category]
            category_stats[category] = {
                "total": len(category_feedbacks),
                "pending": sum(1 for f in category_feedbacks if f["status"] == "pending"),
                "processing": sum(1 for f in category_feedbacks if f["status"] == "processing"),
                "completed": sum(1 for f in category_feedbacks if f["status"] == "completed")
            }
        
        # 整体统计
        total_stats = {
            "total": len(feedbacks),
            "pending": sum(1 for f in feedbacks if f["status"] == "pending"),
            "processing": sum(1 for f in feedbacks if f["status"] == "processing"),
            "completed": sum(1 for f in feedbacks if f["status"] == "completed")
        }
        
        # 构建HTML
        categories_html = ""
        for category in categories:
            stats = category_stats[category]
            categories_html += f"""
<div style="padding: 10px; border: 1px solid #e0e0e0; border-radius: 6px; margin-bottom: 8px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <strong style="font-size: 14px;">{category}</strong>
        <span style="font-size: 12px;">共 {stats['total']} 条</span>
    </div>
    <div style="display: flex; gap: 8px;">
        <div style="flex: 1; padding: 6px; background: rgba(255, 167, 38, 0.15); border-radius: 4px; text-align: center;">
            <div style="font-size: 14px; font-weight: bold; color: #e65100;">{stats['pending']}</div>
            <div style="font-size: 10px; color: #bf360c;">待处理</div>
        </div>
        <div style="flex: 1; padding: 6px; background: rgba(33, 150, 243, 0.15); border-radius: 4px; text-align: center;">
            <div style="font-size: 14px; font-weight: bold; color: #1565c0;">{stats['processing']}</div>
            <div style="font-size: 10px; color: #0d47a1;">处理中</div>
        </div>
        <div style="flex: 1; padding: 6px; background: rgba(76, 175, 80, 0.15); border-radius: 4px; text-align: center;">
            <div style="font-size: 14px; font-weight: bold; color: #2e7d32;">{stats['completed']}</div>
            <div style="font-size: 10px; color: #1b5e20;">已完成</div>
        </div>
    </div>
</div>"""
        
        # 构建HTML展开菜单
        accordion_html = ""
        for status_key, status_text in [("pending", "待处理"), ("processing", "处理中"), ("completed", "已完成")]:
            feedbacks_in_status = status_feedbacks[status_key]
            if not feedbacks_in_status:
                continue
            
            status_color = {
                "pending": "#e65100",
                "processing": "#1565c0",
                "completed": "#2e7d32"
            }[status_key]
            
            items_html = ""
            for feedback in feedbacks_in_status:
                items_html += cls.build_single_feedback_item(feedback)
            
            accordion_html += f"""
<div style="margin-bottom: 8px; border: 1px solid #e0e0e0; border-radius: 6px; overflow: hidden;">
    <details>
        <summary style="padding: 10px 12px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; background: rgba(21, 101, 192, 0.05);">
            <span style="font-weight: bold; color: {status_color};">{status_text} ({len(feedbacks_in_status)}条)</span>
        </summary>
        <div style="padding: 10px;">
            {items_html}
        </div>
    </details>
</div>"""
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 16px; font-weight: bold; margin-bottom: 12px;">反馈列表</div>

    <div style="display: flex; gap: 10px; margin-bottom: 12px;">
        <div style="flex: 1; padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; text-align: center;">
            <div style="font-size: 18px; font-weight: bold;">{total_stats['total']}</div>
            <div style="font-size: 11px;">总计</div>
        </div>
        <div style="flex: 1; padding: 8px; background: rgba(255, 167, 38, 0.15); border-radius: 6px; text-align: center;">
            <div style="font-size: 18px; font-weight: bold; color: #e65100;">{total_stats['pending']}</div>
            <div style="font-size: 11px; color: #bf360c;">待处理</div>
        </div>
        <div style="flex: 1; padding: 8px; background: rgba(33, 150, 243, 0.15); border-radius: 6px; text-align: center;">
            <div style="font-size: 18px; font-weight: bold; color: #1565c0;">{total_stats['processing']}</div>
            <div style="font-size: 11px; color: #0d47a1;">处理中</div>
        </div>
        <div style="flex: 1; padding: 8px; background: rgba(76, 175, 80, 0.15); border-radius: 6px; text-align: center;">
            <div style="font-size: 18px; font-weight: bold; color: #2e7d32;">{total_stats['completed']}</div>
            <div style="font-size: 11px; color: #1b5e20;">已完成</div>
        </div>
    </div>

    <div style="margin-bottom: 12px;">
        <details>
            <summary style="cursor: pointer; font-size: 13px; font-weight: bold; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
                <span>按类别统计</span>
            </summary>
            {categories_html}
        </details>
    </div>

    <div style="font-size: 13px; margin-bottom: 8px; font-weight: bold;">详细反馈</div>
    {accordion_html}
</div>"""
        
        # 过滤反馈列表（Markdown和Text默认不显示已完成，除非指定）
        if show_status:
            filtered_feedbacks = [f for f in feedbacks if f["status"] == show_status]
        else:
            # 默认只显示待处理和处理中
            filtered_feedbacks = [f for f in feedbacks if f["status"] in ["pending", "processing"]]
        
        # 构建Markdown
        md_categories = ""
        for category in categories:
            stats = category_stats[category]
            md_categories += f"**{category}** (共{stats['total']}条): 待处理{stats['pending']} | 处理中{stats['processing']} | 已完成{stats['completed']}\n\n"
        
        md_feedbacks = ""
        for feedback in filtered_feedbacks:
            md_feedbacks += cls.build_single_feedback_item_markdown(feedback) + "\n\n"
        
        # 如果过滤后有内容，添加提示
        if show_status:
            status_text = cls._get_status_text(show_status)
            markdown = f"""**反馈列表**（仅显示{status_text}）

**统计:** 总计{total_stats['total']} | 待处理{total_stats['pending']} | 处理中{total_stats['processing']} | 已完成{total_stats['completed']}

**按类别统计:**
{md_categories}
**详细反馈:**
{md_feedbacks}"""
        else:
            markdown = f"""**反馈列表**

**统计:** 总计{total_stats['total']} | 待处理{total_stats['pending']} | 处理中{total_stats['processing']} | 已完成{total_stats['completed']}

**按类别统计:**
{md_categories}
**详细反馈:**
{md_feedbacks}"""
        
        # 构建Text
        text_categories = ""
        for category in categories:
            stats = category_stats[category]
            text_categories += f"{category} (共{stats['total']}条): 待处理{stats['pending']} | 处理中{stats['processing']} | 已完成{stats['completed']}\n"
        
        text_feedbacks = ""
        for feedback in filtered_feedbacks:
            text_feedbacks += cls.build_single_feedback_item_text(feedback) + "\n\n"
        
        # 如果过滤后有内容，添加提示
        if show_status:
            status_text = cls._get_status_text(show_status)
            text = f"""反馈列表（仅显示{status_text}）

统计: 总计{total_stats['total']} | 待处理{total_stats['pending']} | 处理中{total_stats['processing']} | 已完成{total_stats['completed']}

按类别统计:
{text_categories}
详细反馈:
{text_feedbacks}"""
        else:
            text = f"""反馈列表

统计: 总计{total_stats['total']} | 待处理{total_stats['pending']} | 处理中{total_stats['processing']} | 已完成{total_stats['completed']}

按类别统计:
{text_categories}
详细反馈:
{text_feedbacks}"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_single_feedback_item(cls, feedback: Dict):
        """构建单条反馈HTML"""
        time_str = cls._format_time(feedback["timestamp"])
        status_text = cls._get_status_text(feedback["status"])
        status_bg = cls._get_status_color(feedback["status"])
        category_bg = cls._get_category_color(feedback["category"])
        
        html = f"""
<div style="padding: 10px; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 10px;">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; margin-bottom: 8px; gap: 8px;">
        <div>
            <strong style="font-size: 14px;">{feedback['user_nickname']}</strong>
        </div>
        <div style="display: flex; gap: 12px; align-items: center;">
            <small style="font-size: 12px;">ID: {feedback['user_id']}</small>
            <small style="font-size: 12px;">{time_str}</small>
        </div>
    </div>

    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <div style="display: flex; gap: 6px;">
            <div style="padding: 4px 8px; background-color: {category_bg}; font-size: 12px; border-radius: 4px;">
                {feedback['category']}
            </div>
            <div style="padding: 4px 8px; background-color: {status_bg}; font-size: 12px; border-radius: 4px;">
                {status_text}
            </div>
        </div>
    </div>

    <div style="padding: 10px; border: 1px solid #e0e0e0; border-radius: 6px;">
        <div style="font-size: 12px; margin-bottom: 6px;">{feedback['id']}</div>
        <div style="line-height: 1.6; font-size: 14px;">
            {feedback['content']}
        </div>
    </div>
</div>"""
        return html
    
    @classmethod
    def build_single_feedback_item_markdown(cls, feedback: Dict):
        """构建单条反馈Markdown"""
        time_str = cls._format_time(feedback["timestamp"])
        status_text = cls._get_status_text(feedback["status"])
        
        return f"""**{feedback['user_nickname']}** (ID: {feedback['user_id']}) - {time_str}

{feedback['id']} | {feedback['category']} | {status_text}

{feedback['content']}"""
    
    @classmethod
    def build_single_feedback_item_text(cls, feedback: Dict):
        """构建单条反馈Text"""
        time_str = cls._format_time(feedback["timestamp"])
        status_text = cls._get_status_text(feedback["status"])
        
        return f"""{feedback['user_nickname']} (ID: {feedback['user_id']}) - {time_str}

{feedback['id']} | {feedback['category']} | {status_text}

{feedback['content']}"""
    
    @classmethod
    def build_quick_feedback_selection(cls, pending_items: List[Dict], processing_items: List[Dict], 
                                  id_prefix: str):
        """构建快速反馈选择（待处理+处理中各2条）"""
        items = []
        
        # 待处理前2条
        for i, item in enumerate(pending_items[:2], 1):
            items.append({
                "index": i,
                "id": item['id'],
                "preview": f"{item['content'][:30]}..." if len(item['content']) > 30 else item['content'],
                "status": "待处理"
            })
        
        # 处理中前2条
        for i, item in enumerate(processing_items[:2], len(pending_items[:2]) + 1):
            items.append({
                "index": i,
                "id": item['id'],
                "preview": f"{item['content'][:30]}..." if len(item['content']) > 30 else item['content'],
                "status": "处理中"
            })
        
        # 构建HTML
        items_html = ""
        for item in items:
            status_color = "#e65100" if item["status"] == "待处理" else "#1565c0"
            items_html += f"""
<div style="padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; margin-bottom: 6px;">
    <div style="display: flex; align-items: center;">
        <div style="width: 40px; height: 40px; min-width: 40px; background: rgba(21, 101, 192, 0.15); border-radius: 50%; text-align: center; line-height: 40px; font-weight: bold; font-size: 14px; color: #1565c0; flex-shrink: 0;">
            {item['index']}
        </div>
        <div style="flex: 1; margin-left: 10px; min-width: 0;">
            <div style="font-size: 12px;">{item['id']}</div>
            <div style="font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{item['preview']}</div>
        </div>
        <div style="padding: 2px 8px; background: rgba(255, 167, 38, 0.15); border-radius: 4px; font-size: 11px; color: {status_color}; margin-left: 8px; flex-shrink: 0; white-space: nowrap;">
            {item['status']}
        </div>
    </div>
</div>"""
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">修改反馈状态</div>
    <div style="font-size: 13px; margin-bottom: 10px;">
        选择要修改的反馈（输入序号1-4），或直接输入反馈ID（如 {id_prefix}1）：
    </div>
    {items_html}
    <div style="font-size: 12px; margin-top: 8px;">回复序号或反馈ID（60秒内有效）</div>
</div>"""
        
        # 构建Markdown
        md_items = ""
        for item in items:
            md_items += f"{item['index']}. **{item['id']}** - {item['preview']} ({item['status']})\n"
        
        markdown = f"""**修改反馈状态**

选择要修改的反馈（输入序号1-4），或直接输入反馈ID（如 {id_prefix}1）：

{md_items}
回复序号或反馈ID（60秒内有效）"""
        
        # 构建Text
        text_items = ""
        for item in items:
            text_items += f"{item['index']}. {item['id']} - {item['preview']} ({item['status']})\n"
        
        text = f"""修改反馈状态

选择要修改的反馈（输入序号1-4），或直接输入反馈ID（如 {id_prefix}1）：

{text_items}
回复序号或反馈ID（60秒内有效）"""
        
        return {"html": html, "markdown": markdown, "text": text, "items": items}
    
    @classmethod
    def build_feedback_detail_for_status(cls, feedback_data: Dict):
        """构建反馈详情（用于状态修改前显示）"""
        time_str = cls._format_time(feedback_data["timestamp"])
        current_status = feedback_data["status"]
        current_status_text = cls._get_status_text(current_status)
        status_bg = cls._get_status_color(current_status)
        category_bg = cls._get_category_color(feedback_data["category"])
        
        html = f"""
<div style="padding: 12px; border-radius: 8px; margin-bottom: 10px;">
    <div style="color: #1565c0; font-size: 16px; font-weight: bold; margin-bottom: 12px;">反馈详情</div>

    <div style="border: 1px solid #e0e0e0; padding: 12px; border-radius: 6px; margin-bottom: 10px;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; margin-bottom: 8px; gap: 8px;">
            <div>
                <strong style="font-size: 14px;">{feedback_data['user_nickname']}</strong>
            </div>
            <div style="display: flex; gap: 12px; align-items: center;">
                <small style="font-size: 12px;">ID: {feedback_data['user_id']}</small>
                <small style="font-size: 12px;">{time_str}</small>
            </div>
        </div>

        <div style="display: flex; gap: 6px; margin-bottom: 10px;">
            <div style="padding: 4px 8px; background-color: {category_bg}; font-size: 12px; border-radius: 4px;">
                {feedback_data['category']}
            </div>
            <div style="padding: 4px 8px; background-color: {status_bg}; font-size: 12px; border-radius: 4px;">
                {current_status_text}
            </div>
        </div>

        <div style="font-size: 12px; margin-bottom: 6px;">{feedback_data['id']}</div>
        <div style="line-height: 1.6; font-size: 14px; border: 1px solid #e0e0e0; padding: 10px; border-radius: 4px;">
            {feedback_data['content']}
        </div>
    </div>

    <div style="padding: 8px; background: rgba(255, 167, 38, 0.2); border-radius: 6px; margin-bottom: 12px;">
        <div style="color: #e65100; font-size: 12px; margin-bottom: 4px;">当前状态</div>
        <div style="font-size: 14px; font-weight: bold;">{current_status_text}</div>
    </div>
</div>"""
        
        markdown = f"""**反馈详情**

**{feedback_data['user_nickname']}** (ID: {feedback_data['user_id']}) - {time_str}

{feedback_data['id']} | {feedback_data['category']} | {current_status_text}

{feedback_data['content']}

**当前状态:** {current_status_text}"""
        
        text = f"""反馈详情

{feedback_data['user_nickname']} (ID: {feedback_data['user_id']}) - {time_str}

{feedback_data['id']} | {feedback_data['category']} | {current_status_text}

{feedback_data['content']}

当前状态: {current_status_text}"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_status_selection(cls):
        """构建状态选择提示"""
        status_menu = "1. 待处理\n2. 处理中\n3. 已完成\n4. 搁置"
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="font-size: 13px; margin-bottom: 8px;">请选择新状态：</div>
    <div style="font-size: 13px; border: 1px solid #e0e0e0; padding: 10px; border-radius: 6px;">
        {status_menu}
    </div>
    <div style="font-size: 12px; margin-top: 8px;">输入序号或状态名称（60秒内有效）</div>
</div>"""
        
        markdown = f"请选择新状态：\n\n```\n{status_menu}\n```\n\n输入序号或状态名称（60秒内有效）"
        
        text = f"请选择新状态：\n\n{status_menu}\n\n输入序号或状态名称（60秒内有效）"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_status_confirm(cls, feedback_id: str, old_status_text: str, new_status_text: str):
        """构建状态修改确认"""
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">确认操作</div>
    <div style="font-size: 13px; margin-bottom: 8px;">
        确认将反馈 {feedback_id} 的状态从 {old_status_text} 改为 {new_status_text} 吗？
    </div>
    <div style="font-size: 12px;">回复 '是' 或 '否' (30秒内有效)</div>
</div>"""
        
        markdown = f"**确认操作**\n\n确认将反馈 {feedback_id} 的状态从 {old_status_text} 改为 {new_status_text} 吗？\n\n回复 '是' 或 '否' (30秒内有效)"
        
        text = f"确认操作\n\n确认将反馈 {feedback_id} 的状态从 {old_status_text} 改为 {new_status_text} 吗？\n\n回复 '是' 或 '否' (30秒内有效)"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_status_update_success(cls, feedback_id: str, old_status: str, new_status: str):
        """构建状态更新成功消息（不显示详情）"""
        old_status_text = cls._get_status_text(old_status)
        new_status_text = cls._get_status_text(new_status)
        
        html = f"""
<div style="padding: 16px; border-radius: 8px; text-align: center;">
    <div style="color: #2e7d32; font-size: 16px; font-weight: bold; margin-bottom: 12px;">反馈状态已更新</div>
    <div style="font-size: 14px; margin-bottom: 8px;">
        反馈编号: {feedback_id}
    </div>
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 12px;">
        <span style="border: 1px solid #e0e0e0; padding: 4px 10px; border-radius: 4px; font-size: 13px;">{old_status_text}</span>
        <span style="font-size: 16px;">→</span>
        <span style="background: rgba(76, 175, 80, 0.2); padding: 4px 10px; border-radius: 4px; font-size: 13px; font-weight: bold;">{new_status_text}</span>
    </div>
</div>"""
        
        markdown = f"""**反馈状态已更新**

反馈编号: {feedback_id}

{old_status_text} → **{new_status_text}**"""
        
        text = f"""反馈状态已更新

反馈编号: {feedback_id}

{old_status_text} → {new_status_text}"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    # ==================== 通用消息模板 ====================
    
    @classmethod
    def build_timeout(cls, message: str = "操作超时，已取消操作"):
        """构建超时消息"""
        html = f"""
<div style="padding: 12px; border-radius: 8px; text-align: center;">
    <div style="color: #e65100; font-size: 14px;">{message}</div>
</div>"""
        
        markdown = f"**{message}**"
        
        text = message
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_error(cls, title: str, message: str):
        """构建错误消息"""
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 14px; font-weight: bold; margin-bottom: 8px;">{title}</div>
    <div style="font-size: 13px;">{message}</div>
</div>"""
        
        markdown = f"**{title}**\n\n{message}"
        
        text = f"{title}\n\n{message}"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_cancel(cls):
        """构建取消消息"""
        html = """
<div style="padding: 12px; border-radius: 8px; text-align: center;">
    <div style="color: #666; font-size: 14px;">操作已取消</div>
</div>"""
        
        markdown = "**操作已取消**"
        
        text = "操作已取消"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_no_change(cls):
        """构建无变化消息"""
        html = """
<div style="padding: 12px; border-radius: 8px; text-align: center;">
    <div style="color: #666; font-size: 14px;">状态未发生变化</div>
</div>"""
        
        markdown = "**状态未发生变化**"
        
        text = "状态未发生变化"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    # ==================== 交互式管理命令模板 ====================
    
    @classmethod
    def build_manage_menu(cls, has_group: bool, group_name: Optional[str] = None):
        """构建管理菜单"""
        display_name = group_name if group_name else "无"
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 16px; font-weight: bold; margin-bottom: 12px;">设置反馈组</div>
"""
        
        if has_group and group_name:
            html += f"""
    <div style="padding: 10px; background: rgba(76, 175, 80, 0.1); border-radius: 6px; margin-bottom: 12px;">
        <div style="color: #2e7d32; font-size: 13px; margin-bottom: 4px;">当前反馈组</div>
        <div style="font-size: 14px; font-weight: bold;">{group_name}</div>
    </div>
"""
        
        html += """
    <div style="font-size: 13px; margin-bottom: 8px;">请选择操作：</div>
    <div style="font-size: 13px; border: 1px solid #e0e0e0; padding: 10px; border-radius: 6px;">
        1. 创建新的反馈组
        2. 加入现有反馈组
        3. 查看反馈组信息
        4. 配置反馈组
        5. 退出反馈组
        6. 解散反馈组
    </div>
    <div style="font-size: 12px; margin-top: 8px;">回复序号选择操作（60秒内有效）</div>
</div>"""
        
        markdown = f"""**设置反馈组**

"""
        if has_group and group_name:
            markdown += f"""**当前反馈组:** {group_name}

"""
        
        markdown += """请选择操作：

1. 创建新的反馈组
2. 加入现有反馈组
3. 查看反馈组信息
4. 配置反馈组
5. 退出反馈组
6. 解散反馈组

回复序号选择操作（60秒内有效）"""
        
        text = f"""设置反馈组

"""
        if has_group and group_name:
            text += f"""当前反馈组: {group_name}

"""
        
        text += """请选择操作：

1. 创建新的反馈组
2. 加入现有反馈组
3. 查看反馈组信息
4. 配置反馈组
5. 退出反馈组
6. 解散反馈组

回复序号选择操作（60秒内有效）"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_create_group_prompt(cls):
        """构建创建反馈组输入提示"""
        html = """
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">创建新的反馈组</div>
    <div style="font-size: 13px; margin-bottom: 8px;">请输入反馈组名称：</div>
    <div style="font-size: 12px;">回复取消可终止创建（60秒内有效）</div>
</div>"""
        
        markdown = "**创建新的反馈组**\n\n请输入反馈组名称：\n\n回复取消可终止创建（60秒内有效）"
        
        text = "创建新的反馈组\n\n请输入反馈组名称：\n\n回复取消可终止创建（60秒内有效）"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_join_group_prompt(cls):
        """构建加入反馈组输入提示"""
        html = """
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">加入现有反馈组</div>
    <div style="font-size: 13px; margin-bottom: 8px;">请输入要加入的反馈组ID：</div>
    <div style="font-size: 12px;">提示：必须由反馈组创建者添加才能加入（60秒内有效）</div>
</div>"""
        
        markdown = "**加入现有反馈组**\n\n请输入要加入的反馈组ID：\n\n提示：必须由反馈组创建者添加才能加入（60秒内有效）"
        
        text = "加入现有反馈组\n\n请输入要加入的反馈组ID：\n\n提示：必须由反馈组创建者添加才能加入（60秒内有效）"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_config_menu(cls, group_data: Dict):
        """构建配置菜单"""
        config = group_data["config"]
        creator_id = group_data.get("creator_id", "")
        admin_ids = group_data.get("admin_ids", [])
        maintainer_ids = group_data.get("maintainer_ids", [])
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 16px; font-weight: bold; margin-bottom: 12px;">配置反馈组</div>
    
    <div style="padding: 10px; background: rgba(21, 101, 192, 0.05); border-radius: 6px; margin-bottom: 12px;">
        <div style="color: #1565c0; font-size: 13px; margin-bottom: 4px;">反馈组: {group_data['name']}</div>
        <div style="font-size: 12px; color: #666;">创建者: {creator_id}</div>
        <div style="font-size: 12px; color: #666;">管理员: {len(admin_ids)}人</div>
        <div style="font-size: 12px; color: #666;">维护者: {len(maintainer_ids)}人</div>
    </div>
    
    <div style="font-size: 13px; margin-bottom: 8px;">请选择要配置的项：</div>
    <div style="font-size: 13px; border: 1px solid #e0e0e0; padding: 10px; border-radius: 6px;">
        1. 反馈类别 (当前: {', '.join(config.get('categories', []))})
        2. 超时时间 (当前: {config.get('timeout', 60)}秒)
        3. 内容最大长度 (当前: {config.get('max_content_length', 500)}字)
        4. 反馈ID前缀 (当前: {config.get('id_prefix', '#')})
        5. 成员管理（添加/移除管理员或维护者）
    </div>
    <div style="font-size: 12px; margin-top: 8px;">回复序号选择要配置的项（60秒内有效）</div>
</div>"""
        
        markdown = f"""**配置反馈组**

反馈组: {group_data['name']}
创建者: {creator_id}
管理员: {len(admin_ids)}人
维护者: {len(maintainer_ids)}人

请选择要配置的项：

1. 反馈类别 (当前: {', '.join(config.get('categories', []))})
2. 超时时间 (当前: {config.get('timeout', 60)}秒)
3. 内容最大长度 (当前: {config.get('max_content_length', 500)}字)
4. 反馈ID前缀 (当前: {config.get('id_prefix', '#')})
5. 成员管理（添加/移除管理员或维护者）

回复序号选择要配置的项（60秒内有效）"""
        
        text = f"""配置反馈组

反馈组: {group_data['name']}
创建者: {creator_id}
管理员: {len(admin_ids)}人
维护者: {len(maintainer_ids)}人

请选择要配置的项：

1. 反馈类别 (当前: {', '.join(config.get('categories', []))})
2. 超时时间 (当前: {config.get('timeout', 60)}秒)
3. 内容最大长度 (当前: {config.get('max_content_length', 500)}字)
4. 反馈ID前缀 (当前: {config.get('id_prefix', '#')})
5. 成员管理（添加/移除管理员或维护者）

回复序号选择要配置的项（60秒内有效）"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_member_management_menu(cls):
        """构建成员管理菜单"""
        html = """
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 16px; font-weight: bold; margin-bottom: 12px;">成员管理</div>
    
    <div style="font-size: 13px; margin-bottom: 8px;">请选择操作：</div>
    <div style="font-size: 13px; border: 1px solid #e0e0e0; padding: 10px; border-radius: 6px;">
        1. 添加管理员
        2. 移除管理员
        3. 添加维护者
        4. 移除维护者
        5. 查看成员列表
    </div>
    <div style="font-size: 12px; margin-top: 8px;">回复序号选择操作（60秒内有效）</div>
</div>"""
        
        markdown = """**成员管理**

请选择操作：

1. 添加管理员
2. 移除管理员
3. 添加维护者
4. 移除维护者
5. 查看成员列表

回复序号选择操作（60秒内有效）"""
        
        text = """成员管理

请选择操作：

1. 添加管理员
2. 移除管理员
3. 添加维护者
4. 移除维护者
5. 查看成员列表

回复序号选择操作（60秒内有效）"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_member_list(cls, group_data: Dict):
        """构建成员列表"""
        creator_id = group_data.get("creator_id", "无")
        admin_ids = group_data.get("admin_ids", [])
        maintainer_ids = group_data.get("maintainer_ids", [])
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 16px; font-weight: bold; margin-bottom: 12px;">成员列表</div>
    
    <div style="margin-bottom: 10px; padding: 10px; background: rgba(183, 28, 28, 0.1); border-radius: 6px;">
        <div style="font-size: 13px; font-weight: bold; margin-bottom: 4px;">创建者</div>
        <div style="font-size: 14px;">{creator_id}</div>
    </div>
    
    <div style="margin-bottom: 10px; padding: 10px; background: rgba(21, 101, 192, 0.1); border-radius: 6px;">
        <div style="font-size: 13px; font-weight: bold; margin-bottom: 4px;">管理员 ({len(admin_ids)}人)</div>
        {"<br>".join([f'<div style="font-size: 14px;">{aid}</div>' for aid in admin_ids]) if admin_ids else '<div style="font-size: 14px; color: #666;">无</div>'}
    </div>
    
    <div style="margin-bottom: 10px; padding: 10px; background: rgba(76, 175, 80, 0.1); border-radius: 6px;">
        <div style="font-size: 13px; font-weight: bold; margin-bottom: 4px;">维护者 ({len(maintainer_ids)}人)</div>
        {"<br>".join([f'<div style="font-size: 14px;">{mid}</div>' for mid in maintainer_ids]) if maintainer_ids else '<div style="font-size: 14px; color: #666;">无</div>'}
    </div>
</div>"""
        
        admin_list = "\n".join([f"- {aid}" for aid in admin_ids]) if admin_ids else "无"
        maintainer_list = "\n".join([f"- {mid}" for mid in maintainer_ids]) if maintainer_ids else "无"
        
        markdown = f"""**成员列表**

**创建者**
{creator_id}

**管理员** ({len(admin_ids)}人)
{admin_list}

**维护者** ({len(maintainer_ids)}人)
{maintainer_list}"""
        
        text = f"""成员列表

创建者
{creator_id}

管理员 ({len(admin_ids)}人)
{admin_list}

维护者 ({len(maintainer_ids)}人)
{maintainer_list}"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_add_member_prompt(cls, member_type: str):
        """构建添加成员输入提示"""
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">添加{member_type}</div>
    <div style="font-size: 13px; margin-bottom: 8px;">请输入要添加的用户ID：</div>
    <div style="font-size: 12px;">回复取消可终止操作（60秒内有效）</div>
</div>"""
        
        markdown = f"""**添加{member_type}**

请输入要添加的用户ID：

回复取消可终止操作（60秒内有效）"""
        
        text = f"""添加{member_type}

请输入要添加的用户ID：

回复取消可终止操作（60秒内有效）"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_remove_member_prompt(cls, member_type: str, members: List[str]):
        """构建移除成员选择提示"""
        items_html = ""
        for i, mid in enumerate(members, 1):
            items_html += f'<div style="padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; margin-bottom: 6px;">{i}. {mid}</div>'
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 14px; font-weight: bold; margin-bottom: 8px;">移除{member_type}</div>
    <div style="font-size: 13px; margin-bottom: 8px;">请选择要移除的用户（输入序号）：</div>
    {items_html if items_html else '<div style="font-size: 13px; color: #666;">无{member_type}可移除</div>'}
    <div style="font-size: 12px; margin-top: 8px;">回复序号选择（60秒内有效）</div>
</div>"""
        
        md_items = "\n".join([f"{i}. {mid}" for i, mid in enumerate(members, 1)]) if members else f"无{member_type}可移除"
        
        markdown = f"""**移除{member_type}**

请选择要移除的用户（输入序号）：

{md_items}

回复序号选择（60秒内有效）"""
        
        text = f"""移除{member_type}

请选择要移除的用户（输入序号）：

{md_items}

回复序号选择（60秒内有效）"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_member_added(cls, member_type: str, user_id: str):
        """构建成员添加成功消息"""
        html = f"""
<div style="padding: 16px; border-radius: 8px; text-align: center;">
    <div style="color: #2e7d32; font-size: 16px; font-weight: bold; margin-bottom: 12px;">成功添加{member_type}</div>
    <div style="font-size: 14px;">
        用户ID: {user_id}
    </div>
</div>"""
        
        markdown = f"""**成功添加{member_type}**

用户ID: {user_id}"""
        
        text = f"""成功添加{member_type}

用户ID: {user_id}"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_member_removed(cls, member_type: str, user_id: str):
        """构建成员移除成功消息"""
        html = f"""
<div style="padding: 16px; border-radius: 8px; text-align: center;">
    <div style="color: #2e7d32; font-size: 16px; font-weight: bold; margin-bottom: 12px;">成功移除{member_type}</div>
    <div style="font-size: 14px;">
        用户ID: {user_id}
    </div>
</div>"""
        
        markdown = f"""**成功移除{member_type}**

用户ID: {user_id}"""
        
        text = f"""成功移除{member_type}

用户ID: {user_id}"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_config_input_prompt(cls, config_type: str, current_value):
        """构建配置输入提示"""
        prompts = {
            "类别": ("请输入新的反馈类别（用逗号分隔）:", "如: 功能,优化,建议,bug"),
            "超时": ("请输入新的超时时间（秒，10-300）:", "当前超时: {}秒".format(current_value)),
            "长度": ("请输入新的内容最大长度（字，10-2000）:", "当前限制: {}字".format(current_value)),
            "前缀": ("请输入新的反馈ID前缀:", "当前前缀: {}".format(current_value))
        }
        
        title, hint = prompts.get(config_type, ("请输入新值:", ""))
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">配置{config_type}</div>
    <div style="font-size: 13px; margin-bottom: 8px;">{title}</div>
    <div style="font-size: 12px;">{hint}</div>
</div>"""
        
        markdown = f"**配置{config_type}**\n\n{title}\n\n{hint}"
        
        text = f"配置{config_type}\n\n{title}\n\n{hint}"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    # ==================== 通用消息模板 ====================
    
    @classmethod
    def build_help(cls, commands: Dict, categories: List[str]):
        """构建帮助信息"""
        categories_text = "、".join(categories)
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="margin-bottom: 12px;">
        <strong style="font-size: 14px;">提交反馈</strong>
        <div style="font-size: 13px; margin-top: 4px;">
            用法: /{commands['submit']}
        </div>
        <div style="font-size: 12px; margin-top: 4px;">
            按提示选择类别并输入内容
        </div>
    </div>
    
    <div style="margin-bottom: 12px;">
        <strong style="font-size: 14px;">查看列表</strong>
        <div style="font-size: 13px; margin-top: 4px;">
            用法: /{commands['list']}
        </div>
        <div style="font-size: 12px; margin-top: 4px;">
            查看所有反馈及统计信息
        </div>
    </div>
    
    <div style="margin-bottom: 12px;">
        <strong style="font-size: 14px;">修改状态</strong>
        <div style="font-size: 13px; margin-top: 4px;">
            用法: /{commands['status']}
        </div>
        <div style="font-size: 12px; margin-top: 4px;">
            快速选择反馈或输入ID修改状态
        </div>
    </div>
    
    <div style="margin-bottom: 12px;">
        <strong style="font-size: 14px;">设置反馈组</strong>
        <div style="font-size: 13px; margin-top: 4px;">
            用法: /{commands['manage']}
        </div>
        <div style="font-size: 12px; margin-top: 4px;">
            管理员专用：创建/加入/配置反馈组
        </div>
    </div>
    
    <div style="margin-bottom: 12px;">
        <strong style="font-size: 14px;">支持的类别</strong>
        <div style="font-size: 13px; margin-top: 4px;">
            {categories_text}
        </div>
    </div>
    
    <div>
        <strong style="font-size: 14px;">支持的状态</strong>
        <div style="font-size: 13px; margin-top: 4px;">
            <span style="background: rgba(255, 167, 38, 0.15); padding: 2px 6px; border-radius: 4px; margin-right: 4px;">待处理</span>
            <span style="background: rgba(33, 150, 243, 0.15); padding: 2px 6px; border-radius: 4px; margin-right: 4px;">处理中</span>
            <span style="background: rgba(76, 175, 80, 0.15); padding: 2px 6px; border-radius: 4px; margin-right: 4px;">已完成</span>
            <span style="background: rgba(158, 158, 158, 0.15); padding: 2px 6px; border-radius: 4px;">搁置</span>
        </div>
    </div>
</div>"""
        
        markdown = f"""**提交反馈**
用法: /{commands['submit']}
按提示选择类别并输入内容

**查看列表**
用法: /{commands['list']}
查看所有反馈及统计信息

**修改状态**
用法: /{commands['status']}
快速选择反馈或输入ID修改状态

        **设置反馈组**
用法: /{commands['manage']}
管理员专用：创建/加入/配置反馈组

**支持的类别**
{categories_text}

        **支持的状态**
        待处理 | 处理中 | 已完成 | 搁置"""
        
        text = f"""提交反馈
用法: /{commands['submit']}
按提示选择类别并输入内容

查看列表
用法: /{commands['list']}
查看所有反馈及统计信息

修改状态
用法: /{commands['status']}
快速选择反馈或输入ID修改状态

设置反馈组
用法: /{commands['manage']}
管理员专用：创建/加入/配置反馈组

支持的类别
{categories_text}

        支持的状态
        待处理 | 处理中 | 已完成 | 搁置"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    # ==================== 导出和导入相关模板 ====================
    
    @classmethod
    def build_export_data(cls, group_data: Dict, feedbacks: List[Dict]):
        from datetime import datetime
        
        # 构建导出数据结构
        export_data = {
            "feedback_group": {
                "id": group_data["id"],
                "name": group_data["name"],
                "admin_ids": group_data["admin_ids"],
                "created_at": group_data["created_at"],
                "config": group_data["config"]
            },
            "feedbacks": feedbacks,
            "exported_at": int(datetime.now().timestamp()),
            "version": "1.0"
        }
        
        return json.dumps(export_data, ensure_ascii=False, indent=2)
    
    @classmethod
    def build_import_prompt(cls):
        html = """
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">导入反馈数据</div>
    <div style="font-size: 13px; margin-bottom: 8px;">请粘贴之前导出的 JSON 数据：</div>
    <div style="padding: 10px; background: rgba(21, 101, 192, 0.05); border-radius: 6px; margin-bottom: 8px;">
        <div style="font-size: 12px; margin-bottom: 4px;">提示</div>
        <div style="font-size: 12px;">可以直接粘贴之前用"导出数据"命令导出的完整 JSON 数据</div>
    </div>
    <div style="font-size: 12px;">回复取消可终止导入（120秒内有效）</div>
</div>"""
        
        markdown = """**导入反馈数据**

请粘贴之前导出的 JSON 数据：

**提示**
可以直接粘贴之前用"导出数据"命令导出的完整 JSON 数据

回复取消可终止导入（120秒内有效）"""
        
        text = """导入反馈数据

请粘贴之前导出的 JSON 数据：

提示
可以直接粘贴之前用"导出数据"命令导出的完整 JSON 数据

回复取消可终止导入（120秒内有效）"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_import_mode_selection(cls):
        html = """
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">选择导入模式</div>
    <div style="font-size: 13px; margin-bottom: 8px;">请选择导入方式：</div>
    <div style="font-size: 13px; border: 1px solid #e0e0e0; padding: 10px; border-radius: 6px; margin-bottom: 8px;">
        <div style="margin-bottom: 6px;"><strong>1. 覆盖模式</strong></div>
        <div style="font-size: 12px; color: #b71c1c; margin-bottom: 8px;">⚠️ 清空所有现有反馈，完全使用导入的数据</div>
        <div style="margin-bottom: 6px;"><strong>2. 合并模式</strong></div>
        <div style="font-size: 12px; color: #2e7d32;">保留现有反馈，跳过重复ID的反馈</div>
    </div>
    <div style="font-size: 12px;">回复序号选择模式（60秒内有效）</div>
</div>"""
        
        markdown = """**选择导入模式**

请选择导入方式：

**1. 覆盖模式**
⚠️ **清空所有现有反馈，完全使用导入的数据**

**2. 合并模式**
**保留现有反馈，跳过重复ID的反馈**

回复序号选择模式（60秒内有效）"""
        
        text = """选择导入模式

请选择导入方式：

1. 覆盖模式
⚠️ 清空所有现有反馈，完全使用导入的数据

2. 合并模式
保留现有反馈，跳过重复ID的反馈

回复序号选择模式（60秒内有效）"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_import_confirm(cls, mode: str, feedback_count: int):
        mode_text = "覆盖模式" if mode == "overwrite" else "合并模式"
        warning_text = "⚠️ 此操作将清空所有现有反馈数据！" if mode == "overwrite" else "ℹ️ 将保留现有反馈，跳过重复ID"
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 14px; font-weight: bold; margin-bottom: 8px;">确认导入</div>
    <div style="font-size: 13px; margin-bottom: 8px;">
        模式: <strong>{mode_text}</strong><br>
        数据量: {feedback_count} 条反馈
    </div>
    <div style="padding: 10px; background: rgba(183, 28, 28, 0.1); border-radius: 6px; margin-bottom: 8px;">
        <div style="color: #b71c1c; font-size: 12px;">{warning_text}</div>
    </div>
    <div style="font-size: 12px;">回复 '是' 或 '否' (30秒内有效)</div>
</div>"""
        
        markdown = f"""**确认导入**

模式: **{mode_text}**
数据量: {feedback_count} 条反馈

{warning_text}

回复 '是' 或 '否' (30秒内有效)"""
        
        text = f"""确认导入

模式: {mode_text}
数据量: {feedback_count} 条反馈

{warning_text}

回复 '是' 或 '否' (30秒内有效)"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_import_success(cls, imported_count: int, mode: str):
        mode_text = "覆盖" if mode == "overwrite" else "合并"
        
        html = f"""
<div style="padding: 16px; border-radius: 8px; text-align: center;">
    <div style="color: #2e7d32; font-size: 16px; font-weight: bold; margin-bottom: 12px;">数据导入成功</div>
    <div style="font-size: 14px; margin-bottom: 8px;">
        导入模式: {mode_text}<br>
        导入数量: {imported_count} 条
    </div>
</div>"""
        
        markdown = f"""**数据导入成功**

导入模式: {mode_text}
导入数量: {imported_count} 条"""
        
        text = f"""数据导入成功

导入模式: {mode_text}
导入数量: {imported_count} 条"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_import_error(cls, error_msg: str):
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #b71c1c; font-size: 14px; font-weight: bold; margin-bottom: 8px;">导入失败</div>
    <div style="font-size: 13px;">{error_msg}</div>
</div>"""
        
        markdown = f"**导入失败**\n\n{error_msg}"
        
        text = f"导入失败\n\n{error_msg}"
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_status_change_notification(cls, feedback_data: Dict, old_status: str, 
                                   new_status: str, operator_nickname: str):
        old_status_text = cls._get_status_text(old_status)
        new_status_text = cls._get_status_text(new_status)
        new_status_color = cls._get_status_color(new_status)
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="padding: 10px; background: rgba(21, 101, 192, 0.1); border-radius: 6px; margin-bottom: 10px;">
        <div style="color: #1565c0; font-size: 16px; font-weight: bold; margin-bottom: 4px;">📢 反馈状态更新</div>
        <div style="font-size: 12px; color: #666;">这个反馈有了新进展</div>
    </div>
    
    <div style="margin-bottom: 8px;">
        <div style="font-size: 13px; margin-bottom: 4px;"><strong>反馈编号:</strong></div>
        <div style="padding: 6px; background: rgba(21, 101, 192, 0.05); border-radius: 4px; font-size: 14px;">{feedback_data['id']}</div>
    </div>
    
    <div style="margin-bottom: 8px;">
        <div style="font-size: 13px; margin-bottom: 4px;"><strong>原始内容:</strong></div>
        <div style="padding: 8px; border: 1px solid #e0e0e0; border-radius: 4px; font-size: 14px;">{feedback_data['content'][:100]}{'...' if len(feedback_data['content']) > 100 else ''}</div>
    </div>
    
    <div style="margin-bottom: 8px;">
        <div style="font-size: 13px; margin-bottom: 4px;"><strong>状态变更:</strong></div>
        <div style="display: flex; align-items: center; gap: 8px; font-size: 14px;">
            <span style="border: 1px solid #e0e0e0; padding: 4px 8px; border-radius: 4px;">{old_status_text}</span>
            <span style="font-size: 18px;">→</span>
            <span style="background: {new_status_color}; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{new_status_text}</span>
        </div>
    </div>
    
    <div style="margin-bottom: 10px;">
        <div style="font-size: 13px; margin-bottom: 4px;"><strong>操作者:</strong></div>
        <div style="font-size: 14px;">{operator_nickname}</div>
    </div>
    
    <div style="padding: 8px; background: rgba(76, 175, 80, 0.1); border-radius: 6px; text-align: center;">
        <div style="color: #2e7d32; font-size: 13px; font-weight: bold;">感谢你的反馈！</div>
    </div>
</div>"""
        
        markdown = f"""📢 **反馈状态更新**

这个反馈有了新进展

**反馈编号:** {feedback_data['id']}

**原始内容:**
{feedback_data['content'][:100]}{'...' if len(feedback_data['content']) > 100 else ''}

**状态变更:**
{old_status_text} → **{new_status_text}**

**操作者:** {operator_nickname}

---

*感谢你的反馈！*"""
        
        text = f"""【反馈状态更新】
这个反馈有了新进展

反馈编号: {feedback_data['id']}

原始内容:
{feedback_data['content'][:100]}{'...' if len(feedback_data['content']) > 100 else ''}

状态变更:
{old_status_text} → {new_status_text}

操作者: {operator_nickname}

        感谢你的反馈！"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_user_feedback_list(cls, feedbacks: List[Dict]):
        """构建用户的反馈列表"""
        items_html = ""
        for i, fb in enumerate(feedbacks, 1):
            status_text = cls._get_status_text(fb["status"])
            status_bg = cls._get_status_color(fb["status"])
            time_str = cls._format_time(fb["timestamp"])
            content_preview = fb["content"][:50] + "..." if len(fb["content"]) > 50 else fb["content"]
            
            items_html += f"""
<div style="padding: 10px; border: 1px solid #e0e0e0; border-radius: 6px; margin-bottom: 8px;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
        <span style="font-weight: bold; font-size: 14px;">{i}. {fb['id']}</span>
        <span style="padding: 2px 8px; background: {status_bg}; font-size: 12px; border-radius: 4px;">{status_text}</span>
    </div>
    <div style="font-size: 12px; color: #666; margin-bottom: 4px;">类别: {fb['category']} | {time_str}</div>
    <div style="font-size: 13px;">{content_preview}</div>
</div>"""
        
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #1565c0; font-size: 16px; font-weight: bold; margin-bottom: 12px;">我的反馈</div>
    <div style="font-size: 13px; margin-bottom: 10px;">请选择要编辑的反馈（输入序号）：</div>
    {items_html}
    <div style="font-size: 12px; margin-top: 8px;">回复序号选择反馈（60秒内有效）</div>
</div>"""
        
        md_items = ""
        for i, fb in enumerate(feedbacks, 1):
            status_text = cls._get_status_text(fb["status"])
            content_preview = fb["content"][:50] + "..." if len(fb["content"]) > 50 else fb["content"]
            md_items += f"{i}. **{fb['id']}** - {fb['category']} | {status_text}\n   {content_preview}\n\n"
        
        markdown = f"""**我的反馈**

请选择要编辑的反馈（输入序号）：

{md_items}回复序号选择反馈（60秒内有效）"""
        
        text_items = ""
        for i, fb in enumerate(feedbacks, 1):
            status_text = cls._get_status_text(fb["status"])
            content_preview = fb["content"][:50] + "..." if len(fb["content"]) > 50 else fb["content"]
            text_items += f"{i}. {fb['id']} - {fb['category']} | {status_text}\n   {content_preview}\n\n"
        
        text = f"""我的反馈

请选择要编辑的反馈（输入序号）：

{text_items}回复序号选择反馈（60秒内有效）"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_feedback_detail_for_edit(cls, feedback_data: Dict):
        """构建用于编辑的反馈详情"""
        time_str = cls._format_time(feedback_data["timestamp"])
        current_status = feedback_data["status"]
        current_status_text = cls._get_status_text(current_status)
        status_bg = cls._get_status_color(current_status)
        category_bg = cls._get_category_color(feedback_data["category"])
        
        html = f"""
<div style="padding: 12px; border-radius: 8px; margin-bottom: 10px;">
    <div style="color: #1565c0; font-size: 16px; font-weight: bold; margin-bottom: 12px;">反馈详情</div>
    
    <div style="border: 1px solid #e0e0e0; padding: 12px; border-radius: 6px; margin-bottom: 10px;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; margin-bottom: 8px; gap: 8px;">
            <div>
                <strong style="font-size: 14px;">{feedback_data['user_nickname']}</strong>
            </div>
            <div style="display: flex; gap: 12px; align-items: center;">
                <small style="font-size: 12px;">ID: {feedback_data['user_id']}</small>
                <small style="font-size: 12px;">{time_str}</small>
            </div>
        </div>

        <div style="display: flex; gap: 6px; margin-bottom: 10px;">
            <div style="padding: 4px 8px; background-color: {category_bg}; font-size: 12px; border-radius: 4px;">
                {feedback_data['category']}
            </div>
            <div style="padding: 4px 8px; background-color: {status_bg}; font-size: 12px; border-radius: 4px;">
                {current_status_text}
            </div>
        </div>

        <div style="font-size: 12px; margin-bottom: 6px;">{feedback_data['id']}</div>
        <div style="line-height: 1.6; font-size: 14px; border: 1px solid #e0e0e0; padding: 10px; border-radius: 4px;">
            {feedback_data['content']}
        </div>
    </div>
</div>"""
        
        markdown = f"""**反馈详情**

**{feedback_data['user_nickname']}** (ID: {feedback_data['user_id']}) - {time_str}

**反馈ID:** {feedback_data['id']}
**类别:** {feedback_data['category']}
**状态:** {current_status_text}

**内容:**
{feedback_data['content']}"""
        
        text = f"""反馈详情

{feedback_data['user_nickname']} (ID: {feedback_data['user_id']}) - {time_str}

反馈ID: {feedback_data['id']}
类别: {feedback_data['category']}
状态: {current_status_text}

内容:
{feedback_data['content']}"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_edit_choice(cls):
        """构建编辑选择菜单"""
        html = """
<div style="padding: 12px; border-radius: 8px;">
    <div style="font-size: 13px; margin-bottom: 8px;">请选择要编辑的内容：</div>
    <div style="font-size: 13px; border: 1px solid #e0e0e0; padding: 10px; border-radius: 6px;">
        1. 类别和内容（一起修改）
        2. 仅修改内容
    </div>
    <div style="font-size: 12px; margin-top: 8px;">回复序号选择（60秒内有效）</div>
</div>"""
        
        markdown = """请选择要编辑的内容：

1. 类别和内容（一起修改）
2. 仅修改内容

回复序号选择（60秒内有效）"""
        
        text = """请选择要编辑的内容：

1. 类别和内容（一起修改）
2. 仅修改内容

回复序号选择（60秒内有效）"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_edit_content_prompt(cls, current_content: str = ""):
        """构建编辑内容提示"""
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="font-size: 13px; margin-bottom: 8px;">请输入新的反馈内容：</div>
    <div style="font-size: 12px; margin-bottom: 8px; color: #666;">当前内容预览：{current_content[:100]}{'...' if len(current_content) > 100 else ''}</div>
    <div style="font-size: 12px;">回复取消可终止编辑（120秒内有效）</div>
</div>"""
        
        markdown = f"""请输入新的反馈内容：

当前内容预览：
{current_content[:100]}{'...' if len(current_content) > 100 else ''}

回复取消可终止编辑（120秒内有效）"""
        
        text = f"""请输入新的反馈内容：

当前内容预览：
{current_content[:100]}{'...' if len(current_content) > 100 else ''}

回复取消可终止编辑（120秒内有效）"""
        
        return {"html": html, "markdown": markdown, "text": text}
    
    @classmethod
    def build_edit_success(cls, feedback_id: str):
        """构建编辑成功消息"""
        html = f"""
<div style="padding: 16px; border-radius: 8px; text-align: center;">
    <div style="color: #2e7d32; font-size: 16px; font-weight: bold; margin-bottom: 12px;">反馈已更新</div>
    <div style="font-size: 14px;">
        反馈编号: {feedback_id}
    </div>
</div>"""
        
        markdown = f"""**反馈已更新**

反馈编号: {feedback_id}"""
        
        text = f"""反馈已更新

反馈编号: {feedback_id}"""
        
        return {"html": html, "markdown": markdown, "text": text}
