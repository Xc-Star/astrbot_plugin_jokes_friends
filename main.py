from typing import List, Dict, Optional
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import random


@register("astrbot_plugin_jokes_friends", "Xc_Star", "当群里某个人说话，概率触发自定义回复", "2.0.0")
class JokesFriends(Star):
    """群成员概率触发自定义回复插件"""

    def __init__(self, context: Context, config: dict):
        """初始化插件配置"""
        super().__init__(context)

        # 读取配置
        self.config = config
        self.enable_groups: List[str] = config.get("enable_groups", [])
        self.reply_template: List[str] = config.get("reply_template", [])
        self.reply_probability: float = float(config.get("reply_probability", 0.1))

        # 初始化用户列表和回复映射
        self.user_list: List[str] = []
        self.reply_map: Dict[str, List[str]] = {}

        # 解析回复模板
        self._parse_reply_templates()

        logger.info(f"插件初始化完成，已加载 {len(self.user_list)} 个用户的回复配置")

    def _parse_reply_templates(self) -> None:
        """解析回复模板配置，格式：用户ID|回复内容1|回复内容2|..."""
        for template in self.reply_template:
            parts = str(template).split("|")
            if len(parts) <= 1:
                logger.warning(f"无效的回复模板配置: {template}，已跳过")
                continue

            user_id = parts[0].strip()
            if not user_id:
                logger.warning(f"用户ID为空，已跳过: {template}")
                continue

            # 获取该用户的回复列表（排除第一项用户ID）
            replies = [part.strip() for part in parts[1:] if part.strip()]

            if not replies:
                logger.warning(f"用户 {user_id} 没有配置回复内容，已跳过")
                continue

            self.user_list.append(user_id)
            self.reply_map[user_id] = replies
            logger.debug(f"已加载用户 {user_id} 的 {len(replies)} 条回复")

    async def initialize(self) -> None:
        """异步插件初始化方法（可选实现）"""
        logger.info("插件开始初始化...")
        # 可以在此添加额外的初始化逻辑

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def jokes_friends(self, event: AstrMessageEvent):
        """处理消息事件"""
        # 检查是否在启用的群组中
        group_id = event.get_group_id()
        if group_id not in self.enable_groups:
            return

        # 概率触发
        if random.random() >= self.reply_probability:
            return

        # 检查发送者是否在配置列表中
        user_id = event.get_sender_id()
        if user_id not in self.user_list:
            return

        # 随机选择一条回复并发送
        reply_text = random.choice(self.reply_map[user_id])
        logger.info(f"用户 {user_id} 触发回复: {reply_text}")

        yield event.plain_result(reply_text)

    async def terminate(self) -> None:
        """插件销毁时调用（可选实现）"""
        logger.info("插件正在卸载...")
        # 可以在此添加清理逻辑