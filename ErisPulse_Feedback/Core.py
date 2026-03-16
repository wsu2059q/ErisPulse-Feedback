from ErisPulse import sdk
from ErisPulse.Core.Bases import BaseModule
from .logic import FeedbackLogic
from .registry import FeedbackCommandRegistry


class Main(BaseModule):
    
    def __init__(self):
        self.sdk = sdk
        self.logger = sdk.logger.get_child("Feedback")
        self.config = self._load_config()
        
        # 初始化逻辑和命令注册
        self.logic = None
        self.registry = None
    
    @staticmethod
    def get_load_strategy():
        from ErisPulse.loaders import ModuleLoadStrategy
        return ModuleLoadStrategy(
            lazy_load=False,
            priority=0
        )
    
    async def on_load(self, event):
        self.logger.info("正在加载反馈系统模块...")
        
        # 初始化业务逻辑
        self.logic = FeedbackLogic(self.sdk, self.config)
        
        # 初始化命令注册
        self.registry = FeedbackCommandRegistry(self.logic)
        await self.registry.register_commands()
        
        self.logger.info("反馈系统模块加载完成")
        self.logger.info(f"命令: {self.registry.commands}")
        self.logger.info(f"默认类别: {self.config.get('default_categories', [])}")
    
    async def on_unload(self, event):
        self.logger.info("反馈系统模块正在卸载...")
        self.registry = None
        self.logic = None
        self.logger.info("反馈系统模块卸载完成")
    
    def _load_config(self):
        config = self.sdk.config.getConfig("Feedback", {})
        
        if not config:
            # 设置默认配置
            default_config = {
                # 命令配置
                "commands": ["提交反馈", "反馈列表", "修改状态", "反馈帮助", "设置反馈组", "导出数据", "导入数据"],
                
                # 全局管理员ID列表
                "global_admins": [],
                
                # 反馈类别
                "default_categories": ["功能", "优化", "建议", "bug"],
                
                # 超时时间（秒）
                "timeout": 60,
                
                # 内容最大长度
                "max_content_length": 500,
                
                # 反馈ID前缀
                "id_prefix": "#",
                
                # 存储前缀
                "storage_prefix": "fb_"
            }
            
            self.sdk.config.setConfig("Feedback", default_config)
            self.logger.info("已创建默认配置")
            return default_config
        
        # 验证并补充配置
        default_config = {
            "commands": ["提交反馈", "反馈列表", "修改状态", "反馈帮助", "设置反馈组", "导出数据", "导入数据"],
            "default_categories": ["功能", "优化", "建议", "bug"],
            "timeout": 60,
            "max_content_length": 500,
            "id_prefix": "#",
            "storage_prefix": "fb_"
        }
        
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
                self.logger.warning(f"配置项 {key} 未设置，使用默认值: {value}")
        
        # 保存更新后的配置
        self.sdk.config.setConfig("Feedback", config)
        
        self.logger.info("配置加载完成")
        return config