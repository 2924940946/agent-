"""
会话数据模型

定义会话的生命周期、状态流转和核心属性。
会话是整个多智能体协作系统的核心上下文载体。
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class SessionStatus(str, Enum):
    """
    会话状态枚举

    定义会话在整个生命周期中可能处于的所有状态。
    状态流转由编排引擎（orchestrator）控制。
    """

    INIT = "init"  # 刚创建，等待用户输入目标
    PARSING = "parsing"  # 正在解析用户目标
    CLARIFYING = "clarifying"  # 澄清中（向用户提问）
    ANALYZING = "analyzing"  # 智能体分析中
    SHOWING_RESULTS = "showing_results"  # 展示结果，等待用户判断是否有分歧
    WAITING_USER_CHOICE = "waiting_user_choice"  # 等待用户做倾向性选择
    RE_ANALYZING = "re_analyzing"  # 基于用户选择重新分析中
    FINALIZING = "finalizing"  # 终审中
    FINISHED = "finished"  # 已完成
    RESET = "reset"  # 已重置

    @property
    def is_terminal(self) -> bool:
        """是否为终态（会话结束）"""
        return self in (SessionStatus.FINISHED, SessionStatus.RESET)

    @property
    def is_waiting_user(self) -> bool:
        """是否需要用户交互"""
        return self in (
            SessionStatus.CLARIFYING,
            SessionStatus.SHOWING_RESULTS,
            SessionStatus.WAITING_USER_CHOICE,
            SessionStatus.FINALIZING,
        )

    @property
    def is_processing(self) -> bool:
        """是否正在处理中（非等待用户状态）"""
        return self not in self.is_waiting_user and not self.is_terminal


class Session(BaseModel):
    """
    会话模型

    代表一次完整的分析会话，包含用户目标、当前状态、碰撞进度等。
    所有智能体分析、用户决策都围绕一个会话展开。

    Attributes:
        id: 会话唯一标识（UUID）
        goal: 用户输入的原始目标
        clarified_goal: 经过澄清后的目标（可选）
        status: 当前会话状态
        current_round: 当前已完成的碰撞轮次
        max_rounds: 最大允许的碰撞轮次
        created_at: 创建时间
        updated_at: 最后更新时间
        history: 操作历史记录
    """

    id: UUID = Field(
        default_factory=uuid4,
        description="会话唯一标识",
        examples=["f47ac10b-58cc-4372-a567-0e02b2c3d479"]
    )

    goal: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="用户输入的原始目标",
        examples=["我想做一个AI教育产品"]
    )

    clarified_goal: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="经过澄清后的目标",
        examples=["做一款面向K12的AI辅导产品，主打个性化学习"]
    )

    status: SessionStatus = Field(
        default=SessionStatus.INIT,
        description="当前会话状态"
    )

    current_round: int = Field(
        default=0,
        ge=0,
        le=10,
        description="当前碰撞轮次（0表示尚未开始）"
    )

    max_rounds: int = Field(
        default=3,
        ge=1,
        le=10,
        description="最大允许碰撞轮次"
    )

    created_at: datetime = Field(
        default_factory=datetime.now,
        description="会话创建时间"
    )

    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="最后更新时间"
    )

    history: List[str] = Field(
        default_factory=list,
        description="操作历史记录",
        examples=[["[2026-08-31T10:00:00] 会话创建", "[2026-08-31T10:05:00] 目标解析完成"]]
    )

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        },
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    # ==================== 公共方法 ====================

    def touch(self) -> None:
        """
        更新时间戳

        每次修改会话状态时调用，自动更新 updated_at。
        """
        self.updated_at = datetime.now()

    def add_history(self, event: str) -> None:
        """
        添加历史记录

        Args:
            event: 事件描述
        """
        timestamp = datetime.now().isoformat()
        self.history.append(f"[{timestamp}] {event}")
        self.touch()

    def can_continue_collision(self) -> bool:
        """
        判断是否还能继续碰撞

        Returns:
            True: 还可以继续碰撞
            False: 已达到最大轮次
        """
        return self.current_round < self.max_rounds

    def has_reached_max_rounds(self) -> bool:
        """
        判断是否已达到最大碰撞轮次

        Returns:
            True: 已达到或超过最大轮次
            False: 还可以继续
        """
        return self.current_round >= self.max_rounds

    def increment_round(self) -> int:
        """
        轮次加1，并更新状态

        Returns:
            增加后的轮次数
        """
        self.current_round += 1
        self.touch()
        return self.current_round

    def is_finished(self) -> bool:
        """判断会话是否已完成"""
        return self.status == SessionStatus.FINISHED

    def is_reset(self) -> bool:
        """判断会话是否已重置"""
        return self.status == SessionStatus.RESET

    def is_active(self) -> bool:
        """判断会话是否处于活跃状态（非终态）"""
        return not self.status.is_terminal

    def to_dict(self) -> dict:
        """
        转为字典（用于API响应）

        Returns:
            会话数据的字典表示
        """
        return self.model_dump(mode="json")

    def to_short_dict(self) -> dict:
        """
        转为精简字典（用于列表展示）

        Returns:
            包含核心字段的字典
        """
        return {
            "id": str(self.id),
            "goal": self.goal[:100] + ("..." if len(self.goal) > 100 else ""),
            "status": self.status.value,
            "current_round": self.current_round,
            "max_rounds": self.max_rounds,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ==================== 工厂方法 ====================

    @classmethod
    def create(cls, goal: str) -> "Session":
        """
        创建新会话的工厂方法

        Args:
            goal: 用户目标

        Returns:
            初始化的会话实例
        """
        session = cls(goal=goal)
        session.add_history("会话创建")
        return session

    # ==================== 魔法方法 ====================

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, status={self.status.value}, round={self.current_round})>"

    def __str__(self) -> str:
        return f"会话 {str(self.id)[:8]} | 状态: {self.status.value} | 轮次: {self.current_round}/{self.max_rounds}"