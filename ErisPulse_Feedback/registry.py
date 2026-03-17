from ErisPulse.Core.Event import command
from .templates import FeedbackTemplates
import json


class FeedbackCommandRegistry:
    
    def __init__(self, logic):
        self.logic = logic
        self.templates = FeedbackTemplates()
        self.quick_selection_items = {}
        
        # 从配置获取命令
        config_commands = self.logic.config.get("commands", ["提交反馈", "反馈列表", "修改状态", "反馈帮助", "设置反馈组", "导出数据", "导入数据"])
        self.commands = {
            "submit": config_commands[0],
            "list": config_commands[1],
            "status": config_commands[2],
            "help": config_commands[3],
            "manage": config_commands[4],
            "export": config_commands[5] if len(config_commands) > 5 else "导出数据",
            "import": config_commands[6] if len(config_commands) > 6 else "导入数据"
        }
        
        # 固定的关键词
        self.cancel_keywords = ["取消", "cancel", "exit"]
        self.confirm_keywords = ["是", "yes", "y"]
        
        # 状态映射
        self.status_map = {
            "1": "pending",
            "待处理": "pending",
            "2": "processing",
            "处理中": "processing",
            "3": "completed",
            "已完成": "completed"
        }
    
    async def send_message(self, event, message_dict, fallback="html"):
        platform = event.get_platform()
        supported_methods = self.logic.sdk.adapter.list_sends(platform)
        
        if "Html" in supported_methods and "html" in message_dict:
            await event.reply(message_dict["html"], method="Html")
        elif "Markdown" in supported_methods and "markdown" in message_dict:
            await event.reply(message_dict["markdown"], method="Markdown")
        else:
            # 纯文本模式
            text = message_dict.get("text", message_dict.get("html", message_dict.get("markdown", "")))
            await event.reply(text, method="Text")
    
    def _get_group_config(self, group_data):
        if not group_data:
            return self._get_default_config()
        
        return group_data.get("config", self._get_default_config())
    
    def _get_default_config(self):
        return {
            "categories": self.logic.config.get("default_categories", ["功能", "优化", "建议", "bug"]),
            "timeout": self.logic.config.get("timeout", 60),
            "max_content_length": self.logic.config.get("max_content_length", 500),
            "id_prefix": self.logic.config.get("id_prefix", "#")
        }
    
    def _check_group(self, source_group_id):
        group_data = self.logic.group_manager.get_group_by_source(source_group_id)
        if not group_data:
            return None, self.templates.build_no_feedback_group()
        return group_data, None
    
    def _check_permission(self, group_data, user_id):
        if self.logic.is_global_admin(user_id):
            return True, None
        
        if self.logic.is_group_admin(group_data, user_id):
            return True, None
        
        return False, self.templates.build_error("权限不足", "只有管理员可以执行此操作")
    
    async def _send_status_notification(self, feedback_data: dict, old_status: str, new_status: str, operator_event):
        # 检查是否有平台信息和源群聊ID
        source_platform = feedback_data.get("platform")
        source_group_id = feedback_data.get("source_group_id")
        
        if not source_platform or not source_group_id:
            self.logic.logger.warning(
                f"无法发送状态变更通知：缺少平台信息或群聊ID "
                f"(platform={source_platform}, source_group_id={source_group_id})"
            )
            return
        
        try:
            # 获取目标平台的适配器
            adapter = self.logic.sdk.adapter.get(source_platform)
            
            if not adapter:
                self.logic.logger.warning(f"无法获取平台适配器: {source_platform}")
                return
            
            # 生成通知消息
            operator_nickname = operator_event.get_user_nickname() or "管理员"
            notification_msg = self.templates.build_status_change_notification(
                feedback_data, old_status, new_status, operator_nickname
            )
            
            # 根据平台支持的发送方法选择
            supported_methods = self.logic.sdk.adapter.list_sends(source_platform)
            
            # 优先使用 Html，然后 Markdown，最后 Text
            if "Html" in supported_methods and "html" in notification_msg:
                await adapter.Send.To("group", source_group_id).Html(notification_msg["html"])
            elif "Markdown" in supported_methods and "markdown" in notification_msg:
                await adapter.Send.To("group", source_group_id).Markdown(notification_msg["markdown"])
            else:
                # 使用纯文本
                text = notification_msg.get("text", notification_msg.get("html", notification_msg.get("markdown", "")))
                await adapter.Send.To("group", source_group_id).Text(text)
            
            self.logic.logger.info(
                f"已发送状态变更通知到 {source_platform} 平台群聊 {source_group_id} "
                f"(反馈: {feedback_data['id']}, {old_status} -> {new_status})"
            )
            
        except Exception as e:
            self.logic.logger.error(
                f"发送状态变更通知失败: {e}",
                exc_info=True
            )
    
    async def register_commands(self):
        
        # ==================== 用户命令 ====================
        
        @command(self.commands["submit"], help="提交反馈")
        async def feedback_command(event):
            # 检查群聊是否有反馈组
            group_data, error_msg = self._check_group(event.get_group_id())
            if error_msg:
                await self.send_message(event, error_msg)
                return
            
            config = self._get_group_config(group_data)
            feedback_group_id = group_data["id"]
            
            # 第一步：选择类别
            categories = config["categories"]
            msg = self.templates.build_category_selection(categories)
            await self.send_message(event, msg)
            
            # 等待用户选择类别
            category_reply = await event.wait_reply(timeout=config["timeout"])
            if not category_reply:
                msg = self.templates.build_timeout("操作超时，已取消提交")
                await self.send_message(event, msg)
                return
            
            category_input = category_reply.get_text().strip()
            
            # 解析类别选择
            category = None
            try:
                index = int(category_input) - 1
                if 0 <= index < len(categories):
                    category = categories[index]
            except ValueError:
                if category_input in categories:
                    category = category_input
            
            if not category:
                msg = self.templates.build_error("无效的类别", f"请重新使用 /{self.commands['submit']} 命令提交")
                await self.send_message(event, msg)
                return
            
            # 第二步：输入内容
            msg = self.templates.build_content_prompt(category, config["max_content_length"])
            await self.send_message(event, msg)
            
            # 等待用户输入内容
            content_reply = await event.wait_reply(timeout=120)
            if not content_reply:
                msg = self.templates.build_timeout("操作超时，已取消提交")
                await self.send_message(event, msg)
                return
            
            content = content_reply.get_text().strip()
            
            # 检查是否取消
            if content.lower() in self.cancel_keywords:
                msg = self.templates.build_cancel()
                await self.send_message(event, msg)
                return
            
            # 验证内容长度
            if len(content) > config["max_content_length"]:
                msg = self.templates.build_error("内容过长", f"反馈内容不能超过{config['max_content_length']}字，请重新使用 /{self.commands['submit']} 命令提交")
                await self.send_message(event, msg)
                return
            
            if not content:
                msg = self.templates.build_error("内容为空", "请输入反馈内容，请重新使用 /{self.commands['submit']} 命令提交")
                await self.send_message(event, msg)
                return
            
            # 提交反馈
            feedback_manager = self.logic.get_feedback_manager(feedback_group_id)
            success, result = feedback_manager.submit_feedback(
                feedback_group_id,
                event.get_group_id(),
                event.get_user_id(),
                event.get_user_nickname() or "未知用户",
                category,
                content,
                config,
                event.get_platform()
            )
            
            if not success:
                msg = self.templates.build_error("提交失败", result)
                await self.send_message(event, msg)
                return
            
            # 发送成功消息
            msg = self.templates.build_success(result, category)
            await self.send_message(event, msg)
        
        @command(self.commands["list"], help="查看反馈列表")
        async def feedback_list_command(event):
            # 检查群聊是否有反馈组
            group_data, error_msg = self._check_group(event.get_group_id())
            if error_msg:
                await self.send_message(event, error_msg)
                return
            
            config = self._get_group_config(group_data)
            feedback_group_id = group_data["id"]
            
            # 获取所有反馈
            feedback_manager = self.logic.get_feedback_manager(feedback_group_id)
            all_feedbacks = feedback_manager.list_all_feedbacks(feedback_group_id)
            
            if not all_feedbacks:
                msg = {
                    "html": """
<div style="padding: 30px; border-radius: 8px; text-align: center;">
    <div style="color: #333; font-size: 16px; font-weight: bold; margin-bottom: 8px;">暂无反馈</div>
    <div style="color: #666; font-size: 14px;">还没有任何反馈提交</div>
</div>""",
                    "markdown": "**暂无反馈**\n\n还没有任何反馈提交",
                    "text": "暂无反馈\n\n还没有任何反馈提交"
                }
                await self.send_message(event, msg)
                return
            
            # 构建列表消息
            msg = self.templates.build_feedback_list(all_feedbacks, config["categories"])
            await self.send_message(event, msg)
        
        @command(self.commands["status"], help="修改反馈状态（提交者或管理员）")
        async def feedback_status_command(event):
            user_id = event.get_user_id()
            
            # 检查群聊是否有反馈组
            group_data, error_msg = self._check_group(event.get_group_id())
            if error_msg:
                await self.send_message(event, error_msg)
                return
            
            config = self._get_group_config(group_data)
            feedback_group_id = group_data["id"]
            feedback_manager = self.logic.get_feedback_manager(feedback_group_id)
            
            # 获取待处理和处理中的反馈
            all_feedbacks = feedback_manager.list_all_feedbacks(feedback_group_id)
            pending_items = [f for f in all_feedbacks if f["status"] == "pending"]
            processing_items = [f for f in all_feedbacks if f["status"] == "processing"]
            
            # 如果没有可以修改的反馈
            if not pending_items and not processing_items:
                msg = {
                    "html": """
<div style="padding: 12px; border-radius: 8px; text-align: center;">
    <div style="color: #666; font-size: 14px;">暂无待处理或处理中的反馈</div>
</div>""",
                    "markdown": "**暂无待处理或处理中的反馈**",
                    "text": "暂无待处理或处理中的反馈"
                }
                await self.send_message(event, msg)
                return
            
            # 构建快速选择菜单
            id_prefix = config["id_prefix"]
            msg = self.templates.build_quick_feedback_selection(pending_items, processing_items, id_prefix)
            await self.send_message(event, msg)
            
            # 存储快速选择项供后续使用
            self.quick_selection_items[user_id] = msg.get("items", [])
            
            # 等待用户输入
            input_reply = await event.wait_reply(timeout=config["timeout"])
            if not input_reply:
                msg = self.templates.build_timeout("操作超时，已取消操作")
                await self.send_message(event, msg)
                return
            
            user_input = input_reply.get_text().strip()
            
            # 解析输入
            feedback_id = None
            
            # 尝试解析为数字（快速选择）
            try:
                index = int(user_input)
                if 1 <= index <= 4 and user_id in self.quick_selection_items:
                    selected_item = self.quick_selection_items[user_id][index - 1]
                    feedback_id = selected_item["id"]
            except ValueError:
                # 尝试解析为反馈ID
                feedback_id = user_input
            
            if not feedback_id:
                msg = self.templates.build_error("无效的输入", "请输入1-4的序号或反馈ID")
                await self.send_message(event, msg)
                return
            
            # 验证反馈是否存在
            feedback_data = feedback_manager.get_feedback(feedback_group_id, feedback_id)
            if not feedback_data:
                msg = self.templates.build_error("找不到反馈", f"反馈编号 {feedback_id} 不存在")
                await self.send_message(event, msg)
                return
            
            # 验证权限
            if not (user_id == feedback_data["user_id"] or 
                    self.logic.is_group_admin(group_data, user_id) or 
                    self.logic.is_global_admin(user_id)):
                msg = self.templates.build_error("权限不足", "仅提交者或管理员可修改")
                await self.send_message(event, msg)
                return
            
            # 显示当前反馈的详细信息
            msg = self.templates.build_feedback_detail_for_status(feedback_data)
            await self.send_message(event, msg)
            
            # 第二步：选择新状态
            msg = self.templates.build_status_selection()
            await self.send_message(event, msg)
            
            # 等待用户选择状态
            status_reply = await event.wait_reply(timeout=config["timeout"])
            if not status_reply:
                msg = self.templates.build_timeout("操作超时，已取消操作")
                await self.send_message(event, msg)
                return
            
            status_input = status_reply.get_text().strip()
            
            # 解析状态选择
            new_status = self.status_map.get(status_input)
            if not new_status or new_status not in ["pending", "processing", "completed"]:
                msg = self.templates.build_error("无效的状态", f"请重新使用 /{self.commands['status']} 命令操作")
                await self.send_message(event, msg)
                return
            
            current_status = feedback_data["status"]
            
            # 如果状态没有改变
            if new_status == current_status:
                msg = self.templates.build_no_change()
                await self.send_message(event, msg)
                return
            
            # 第三步：确认操作
            current_status_text = self.templates.STATUS_MAP.get(current_status, current_status)
            new_status_text = self.templates.STATUS_MAP.get(new_status, new_status)
            msg = self.templates.build_status_confirm(feedback_id, current_status_text, new_status_text)
            await self.send_message(event, msg)
            
            # 等待确认
            confirm_reply = await event.wait_reply(timeout=30)
            if confirm_reply and confirm_reply.get_text().lower() in self.confirm_keywords:
                update_result = feedback_manager.update_feedback_status(feedback_group_id, feedback_id, new_status)
                if update_result:
                    old_status, feedback_data = update_result
                    # 更新成功，不显示详情
                    msg = self.templates.build_status_update_success(feedback_id, old_status, new_status)
                    await self.send_message(event, msg)
                    
                    # 发送通知到原始群聊（跨平台推送）
                    await self._send_status_notification(feedback_data, old_status, new_status, input_reply)
            else:
                msg = self.templates.build_cancel()
                await self.send_message(event, msg)
        
        @command(self.commands["help"], help="查看反馈系统帮助")
        async def feedback_help_command(event):
            msg = self.templates.build_help(self.commands, 
                self.logic.config.get("default_categories", ["功能", "优化", "建议", "bug"]))
            await self.send_message(event, msg)
        
        @command(self.commands["manage"], help="设置反馈组")
        async def manage_feedback_group_command(event):
            user_id = event.get_user_id()
            source_group_id = event.get_group_id()
            
            # 检查当前群是否有反馈组
            group_data = self.logic.group_manager.get_group_by_source(source_group_id)
            has_group = group_data is not None
            group_name = group_data["name"] if has_group else None
            
            # 显示管理菜单
            msg = self.templates.build_manage_menu(has_group, group_name)
            await self.send_message(event, msg)
            
            # 等待用户选择操作
            reply = await event.wait_reply(timeout=60)
            if not reply:
                msg = self.templates.build_timeout("操作超时，已取消操作")
                await self.send_message(event, msg)
                return
            
            choice = reply.get_text().strip()
            
            # 操作1: 创建新的反馈组
            if choice == "1":
                await self._handle_create_group(event, user_id, source_group_id)
            
            # 操作2: 加入现有反馈组
            elif choice == "2":
                await self._handle_join_group(event, user_id, source_group_id)
            
            # 操作3: 查看反馈组信息
            elif choice == "3":
                await self._handle_view_group_info(event, source_group_id)
            
            # 操作4: 配置反馈组
            elif choice == "4":
                await self._handle_configure_group(event, user_id, source_group_id)
            
            # 操作5: 解散反馈组
            elif choice == "5":
                await self._handle_dissolve_group(event, user_id, source_group_id)
            
            else:
                msg = self.templates.build_error("无效的选择", "请输入1-5的数字")
                await self.send_message(event, msg)
        
        @command(self.commands["export"], help="导出反馈数据")
        async def export_data_command(event):
            # 检查群聊是否有反馈组
            group_data, error_msg = self._check_group(event.get_group_id())
            if error_msg:
                await self.send_message(event, error_msg)
                return
            
            feedback_group_id = group_data["id"]
            
            # 获取所有反馈
            feedback_manager = self.logic.get_feedback_manager(feedback_group_id)
            all_feedbacks = feedback_manager.list_all_feedbacks(feedback_group_id)
            
            # 构建JSON数据
            json_data = self.templates.build_export_data(group_data, all_feedbacks)
            
            # 先发送提示消息
            html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: #2e7d32; font-size: 16px; font-weight: bold; margin-bottom: 8px;">数据导出成功</div>
    <div style="font-size: 13px; margin-bottom: 8px;">
        反馈组: {group_data['name']}<br>
        反馈数量: {len(all_feedbacks)} 条
    </div>
    <div style="padding: 10px; background: rgba(76, 175, 80, 0.1); border-radius: 6px;">
        <div style="font-size: 12px; margin-bottom: 4px;">JSON 数据</div>
        <div style="font-size: 11px; color: #666;">下一条消息包含完整的JSON数据，请保存好用于后续导入</div>
    </div>
</div>"""
            
            markdown = f"""**数据导出成功**

反馈组: {group_data['name']}
反馈数量: {len(all_feedbacks)} 条

**JSON 数据**
下一条消息包含完整的JSON数据，请保存好用于后续导入"""
            
            text = f"""数据导出成功

反馈组: {group_data['name']}
反馈数量: {len(all_feedbacks)} 条

JSON 数据
下一条消息包含完整的JSON数据，请保存好用于后续导入"""
            
            await self.send_message(event, {"html": html, "markdown": markdown, "text": text})
            
            # 发送JSON数据（使用纯文本方式）
            await event.reply(json_data, method="Text")
        
        @command(self.commands["import"], help="导入反馈数据（仅管理员）")
        async def import_data_command(event):
            user_id = event.get_user_id()
            
            # 检查群聊是否有反馈组
            group_data, error_msg = self._check_group(event.get_group_id())
            if error_msg:
                await self.send_message(event, error_msg)
                return
            
            # 检查权限（只有管理员可以导入）
            has_permission, error_msg = self._check_permission(group_data, user_id)
            if not has_permission:
                await self.send_message(event, error_msg)
                return
            
            feedback_group_id = group_data["id"]
            feedback_manager = self.logic.get_feedback_manager(feedback_group_id)
            
            # 第一步：提示输入JSON数据
            msg = self.templates.build_import_prompt()
            await self.send_message(event, msg)
            
            # 等待用户输入JSON数据
            json_reply = await event.wait_reply(timeout=120)
            if not json_reply:
                msg = self.templates.build_timeout("操作超时，已取消导入")
                await self.send_message(event, msg)
                return
            
            json_text = json_reply.get_text().strip()
            
            # 检查是否取消
            if json_text.lower() in self.cancel_keywords:
                msg = self.templates.build_cancel()
                await self.send_message(event, msg)
                return
            
            # 解析JSON
            try:
                import_data = json.loads(json_text)
                
                # 验证数据格式
                if "feedbacks" not in import_data:
                    msg = self.templates.build_import_error("无效的数据格式：缺少 feedbacks 字段")
                    await self.send_message(event, msg)
                    return
                
                feedbacks_to_import = import_data["feedbacks"]
                if not isinstance(feedbacks_to_import, list):
                    msg = self.templates.build_import_error("无效的数据格式：feedbacks 必须是数组")
                    await self.send_message(event, msg)
                    return
                
                if len(feedbacks_to_import) == 0:
                    msg = self.templates.build_import_error("导入数据为空")
                    await self.send_message(event, msg)
                    return
                
            except json.JSONDecodeError as e:
                msg = self.templates.build_import_error(f"JSON解析失败: {str(e)}")
                await self.send_message(event, msg)
                return
            
            # 第二步：选择导入模式
            msg = self.templates.build_import_mode_selection()
            await self.send_message(event, msg)
            
            # 等待用户选择模式
            mode_reply = await event.wait_reply(timeout=60)
            if not mode_reply:
                msg = self.templates.build_timeout("操作超时，已取消导入")
                await self.send_message(event, msg)
                return
            
            mode_choice = mode_reply.get_text().strip()
            
            # 解析模式选择
            if mode_choice == "1":
                import_mode = "overwrite"
            elif mode_choice == "2":
                import_mode = "merge"
            else:
                msg = self.templates.build_error("无效的选择", "请输入1-2的数字")
                await self.send_message(event, msg)
                return
            
            # 第三步：确认导入
            msg = self.templates.build_import_confirm(import_mode, len(feedbacks_to_import))
            await self.send_message(event, msg)
            
            # 等待确认
            confirm_reply = await event.wait_reply(timeout=30)
            if confirm_reply and confirm_reply.get_text().lower() in self.confirm_keywords:
                # 执行导入
                success, message, imported_count = feedback_manager.import_feedbacks(
                    feedback_group_id,
                    feedbacks_to_import,
                    import_mode
                )
                
                if not success:
                    msg = self.templates.build_import_error(message)
                    await self.send_message(event, msg)
                    return
                
                # 导入成功
                msg = self.templates.build_import_success(imported_count, import_mode)
                await self.send_message(event, msg)
            else:
                msg = self.templates.build_cancel()
                await self.send_message(event, msg)
        
        # 注册全局管理员命令
        await self.register_global_admin_commands()
    
    async def _handle_create_group(self, event, user_id, source_group_id):
        # 检查当前群是否已有反馈组
        existing_group = self.logic.group_manager.get_group_by_source(source_group_id)
        if existing_group:
            msg = self.templates.build_error("反馈组已存在", 
                f"当前群已加入反馈组: {existing_group['name']}。如需更换，请先联系管理员")
            await self.send_message(event, msg)
            return
        
        # 提示输入组名
        msg = self.templates.build_create_group_prompt()
        await self.send_message(event, msg)
        
        # 等待用户输入组名
        reply = await event.wait_reply(timeout=60)
        if not reply:
            msg = self.templates.build_timeout("操作超时，已取消创建")
            await self.send_message(event, msg)
            return
        
        group_name = reply.get_text().strip()
        
        # 检查是否取消
        if group_name.lower() in self.cancel_keywords:
            msg = self.templates.build_cancel()
            await self.send_message(event, msg)
            return
        
        if not group_name:
            msg = self.templates.build_error("名称为空", "请输入有效的反馈组名称")
            await self.send_message(event, msg)
            return
        
        # 创建反馈组
        default_config = self._get_default_config()
        group_id = self.logic.group_manager.create_group(
            group_name,
            [user_id],  # 创建者自动成为管理员
            source_group_id,
            default_config
        )
        
        msg = self.templates.build_group_created(group_id, group_name)
        await self.send_message(event, msg)
    
    async def _handle_join_group(self, event, user_id, source_group_id):
        # 检查当前群是否已有反馈组
        existing_group = self.logic.group_manager.get_group_by_source(source_group_id)
        if existing_group:
            msg = self.templates.build_error("反馈组已存在", 
                f"当前群已加入反馈组: {existing_group['name']}")
            await self.send_message(event, msg)
            return
        
        # 提示输入反馈组ID
        msg = self.templates.build_join_group_prompt()
        await self.send_message(event, msg)
        
        # 等待用户输入反馈组ID
        reply = await event.wait_reply(timeout=60)
        if not reply:
            msg = self.templates.build_timeout("操作超时，已取消操作")
            await self.send_message(event, msg)
            return
        
        target_group_id = reply.get_text().strip()
        
        # 检查反馈组是否存在
        group_data = self.logic.group_manager.get_group(target_group_id)
        if not group_data:
            msg = self.templates.build_error("反馈组不存在", f"反馈组 {target_group_id} 不存在")
            await self.send_message(event, msg)
            return
        
        # 检查权限：只有反馈组的创建者可以添加群聊
        if user_id != group_data["admin_ids"][0]:
            msg = self.templates.build_error("权限不足", 
                "只有反馈组的创建者才能添加群聊。请联系反馈组创建者添加此群。")
            await self.send_message(event, msg)
            return
        
        # 添加群聊到反馈组
        success, message = self.logic.group_manager.add_group_to_feedback_group(
            target_group_id,
            source_group_id,
            user_id
        )
        
        if not success:
            msg = self.templates.build_error("操作失败", message)
            await self.send_message(event, msg)
            return
        
        msg = self.templates.build_group_joined(target_group_id, group_data["name"])
        await self.send_message(event, msg)
    
    async def _handle_view_group_info(self, event, source_group_id):
        group_data = self.logic.group_manager.get_group_by_source(source_group_id)
        
        if not group_data:
            msg = self.templates.build_error("无反馈组", "当前群未加入任何反馈组")
            await self.send_message(event, msg)
            return
        
        msg = self.templates.build_group_info(group_data)
        await self.send_message(event, msg)
    
    async def _handle_configure_group(self, event, user_id, source_group_id):
        group_data = self.logic.group_manager.get_group_by_source(source_group_id)
        
        if not group_data:
            msg = self.templates.build_error("无反馈组", "当前群未加入任何反馈组")
            await self.send_message(event, msg)
            return
        
        # 检查权限：只有反馈组创建者可以配置
        if user_id != group_data["admin_ids"][0]:
            msg = self.templates.build_error("权限不足", 
                "只有反馈组的创建者才能配置反馈组")
            await self.send_message(event, msg)
            return
        
        # 显示配置菜单
        msg = self.templates.build_config_menu(group_data)
        await self.send_message(event, msg)
        
        # 等待用户选择配置项
        reply = await event.wait_reply(timeout=60)
        if not reply:
            msg = self.templates.build_timeout("操作超时，已取消操作")
            await self.send_message(event, msg)
            return
        
        choice = reply.get_text().strip()
        
        # 映射选择到配置类型
        config_map = {
            "1": "类别",
            "2": "超时",
            "3": "长度",
            "4": "前缀"
        }
        
        config_type = config_map.get(choice)
        if not config_type:
            msg = self.templates.build_error("无效的选择", "请输入1-4的数字")
            await self.send_message(event, msg)
            return
        
        # 获取当前值
        current_value = group_data["config"].get({
            "类别": "categories",
            "超时": "timeout",
            "长度": "max_content_length",
            "前缀": "id_prefix"
        }[config_type])
        
        # 提示输入新值
        msg = self.templates.build_config_input_prompt(config_type, current_value)
        await self.send_message(event, msg)
        
        # 等待用户输入新值
        reply = await event.wait_reply(timeout=60)
        if not reply:
            msg = self.templates.build_timeout("操作超时，已取消操作")
            await self.send_message(event, msg)
            return
        
        new_value = reply.get_text().strip()
        
        # 处理配置更新
        config_updates = {}
        
        if config_type == "类别":
            categories = [cat.strip() for cat in new_value.split(",")]
            if not categories:
                msg = self.templates.build_error("参数错误", "请至少提供一个类别")
                await self.send_message(event, msg)
                return
            config_updates["categories"] = categories
        
        elif config_type == "超时":
            try:
                timeout = int(new_value)
                if timeout < 10 or timeout > 300:
                    msg = self.templates.build_error("参数错误", "超时时间必须在10-300秒之间")
                    await self.send_message(event, msg)
                    return
                config_updates["timeout"] = timeout
            except ValueError:
                msg = self.templates.build_error("参数错误", "超时时间必须是数字")
                await self.send_message(event, msg)
                return
        
        elif config_type == "长度":
            try:
                max_length = int(new_value)
                if max_length < 10 or max_length > 2000:
                    msg = self.templates.build_error("参数错误", "内容长度必须在10-2000字之间")
                    await self.send_message(event, msg)
                    return
                config_updates["max_content_length"] = max_length
            except ValueError:
                msg = self.templates.build_error("参数错误", "内容长度必须是数字")
                await self.send_message(event, msg)
                return
        
        elif config_type == "前缀":
            if not new_value:
                msg = self.templates.build_error("参数错误", "请提供反馈ID前缀")
                await self.send_message(event, msg)
                return
            config_updates["id_prefix"] = new_value
        
        # 更新配置
        success, message = self.logic.group_manager.update_group_config(
            group_data["id"],
            config_updates,
            user_id
        )
        
        if not success:
            msg = self.templates.build_error("操作失败", message)
            await self.send_message(event, msg)
            return
        
        msg = self.templates.build_config_updated()
        await self.send_message(event, msg)
    
    async def _handle_dissolve_group(self, event, user_id, source_group_id):
        group_data = self.logic.group_manager.get_group_by_source(source_group_id)
        
        if not group_data:
            msg = self.templates.build_error("无反馈组", "当前群未加入任何反馈组")
            await self.send_message(event, msg)
            return
        
        # 检查权限：必须是创建者
        creator_id = group_data["admin_ids"][0]
        if user_id != creator_id:
            msg = self.templates.build_error("权限不足", 
                "只有反馈组创建者才能解散反馈组")
            await self.send_message(event, msg)
            return
        
        # 显示确认信息
        msg = self.templates.build_dissolve_confirm(group_data["name"], group_data["id"])
        await self.send_message(event, msg)
        
        # 等待确认
        confirm_reply = await event.wait_reply(timeout=30)
        if confirm_reply and confirm_reply.get_text().lower() in self.confirm_keywords:
            success, message = self.logic.group_manager.dissolve_group(
                group_data["id"],
                user_id
            )
            
            if not success:
                msg = self.templates.build_error("操作失败", message)
                await self.send_message(event, msg)
                return
            
            msg = self.templates.build_group_dissolved(group_data["id"], group_data["name"])
            await self.send_message(event, msg)
        else:
            msg = self.templates.build_cancel()
            await self.send_message(event, msg)
    
    async def register_global_admin_commands(self):
        
        @command("反馈全局管理", help="全局管理员命令", hidden=True)
        async def global_admin_command(event):
            user_id = event.get_user_id()
            
            # 检查是否为全局管理员
            if not self.logic.is_global_admin(user_id):
                msg = self.templates.build_error("权限不足", 
                    "此命令仅限全局管理员使用")
                await self.send_message(event, msg)
                return
            
            # 显示全局管理员菜单
            msg = self.templates.build_global_admin_menu()
            await self.send_message(event, msg)
            
            # 等待用户选择操作
            reply = await event.wait_reply(timeout=60)
            if not reply:
                msg = self.templates.build_timeout("操作超时，已取消操作")
                await self.send_message(event, msg)
                return
            
            choice = reply.get_text().strip()
            
            # 操作1: 列出所有反馈组
            if choice == "1":
                await self._handle_list_all_groups(event)
            
            # 操作2: 重新设定组管理员
            elif choice == "2":
                await self._handle_reset_group_admin(event, user_id)
            
            # 操作3: 解散反馈组
            elif choice == "3":
                await self._handle_global_dissolve_group(event, user_id)
            
            else:
                msg = self.templates.build_error("无效的选择", "请输入1-3的数字")
                await self.send_message(event, msg)
    
    async def _handle_list_all_groups(self, event):
        all_groups = self.logic.group_manager.list_all_groups()
        
        if not all_groups:
            msg = self.templates.build_error("无反馈组", "当前没有任何反馈组")
            await self.send_message(event, msg)
            return
        
        msg = self.templates.build_all_groups_list(all_groups)
        await self.send_message(event, msg)
    
    async def _handle_reset_group_admin(self, event, user_id):
        # 提示输入反馈组ID
        msg = self.templates.build_input_prompt("请输入要修改的反馈组ID:")
        await self.send_message(event, msg)
        
        # 等待用户输入反馈组ID
        reply = await event.wait_reply(timeout=60)
        if not reply:
            msg = self.templates.build_timeout("操作超时，已取消操作")
            await self.send_message(event, msg)
            return
        
        group_id = reply.get_text().strip()
        
        # 检查反馈组是否存在
        group_data = self.logic.group_manager.get_group(group_id)
        if not group_data:
            msg = self.templates.build_error("反馈组不存在", f"反馈组 {group_id} 不存在")
            await self.send_message(event, msg)
            return
        
        # 显示当前管理员
        current_admins = group_data["admin_ids"]
        msg = self.templates.build_current_admins(group_id, group_data["name"], current_admins)
        await self.send_message(event, msg)
        
        # 提示输入新的管理员ID（用逗号分隔）
        msg = self.templates.build_input_prompt(
            "请输入新的管理员ID列表（用逗号分隔，第一个ID将成为创建者）:")
        await self.send_message(event, msg)
        
        # 等待用户输入新的管理员ID
        reply = await event.wait_reply(timeout=60)
        if not reply:
            msg = self.templates.build_timeout("操作超时，已取消操作")
            await self.send_message(event, msg)
            return
        
        new_admins = [admin.strip() for admin in reply.get_text().split(",")]
        
        if not new_admins:
            msg = self.templates.build_error("参数错误", "请至少提供一个管理员ID")
            await self.send_message(event, msg)
            return
        
        # 更新管理员列表
        success, message = self.logic.group_manager.update_group_admins(
            group_id,
            new_admins,
            user_id
        )
        
        if not success:
            msg = self.templates.build_error("操作失败", message)
            await self.send_message(event, msg)
            return
        
        msg = self.templates.build_admins_updated(group_id, new_admins)
        await self.send_message(event, msg)
    
    async def _handle_global_dissolve_group(self, event, user_id):
        # 提示输入反馈组ID
        msg = self.templates.build_input_prompt("请输入要解散的反馈组ID:")
        await self.send_message(event, msg)
        
        # 等待用户输入反馈组ID
        reply = await event.wait_reply(timeout=60)
        if not reply:
            msg = self.templates.build_timeout("操作超时，已取消操作")
            await self.send_message(event, msg)
            return
        
        group_id = reply.get_text().strip()
        
        # 检查反馈组是否存在
        group_data = self.logic.group_manager.get_group(group_id)
        if not group_data:
            msg = self.templates.build_error("反馈组不存在", f"反馈组 {group_id} 不存在")
            await self.send_message(event, msg)
            return
        
        # 显示确认信息
        msg = self.templates.build_dissolve_confirm(group_data["name"], group_id)
        await self.send_message(event, msg)
        
        # 等待确认
        confirm_reply = await event.wait_reply(timeout=30)
        if confirm_reply and confirm_reply.get_text().lower() in self.confirm_keywords:
            success, message = self.logic.group_manager.dissolve_group(
                group_id,
                user_id
            )
            
            if not success:
                msg = self.templates.build_error("操作失败", message)
                await self.send_message(event, msg)
                return
            
            msg = self.templates.build_group_dissolved(group_id, group_data["name"])
            await self.send_message(event, msg)
        else:
            msg = self.templates.build_cancel()
            await self.send_message(event, msg)
