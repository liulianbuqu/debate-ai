"""Prompt 构建器 - 组装发送给 DeepSeek 的提示词"""

import json
from typing import List, Dict, Optional

# 系统角色设定（Layer 1 - 固定）
SYSTEM_ROLE = """你是一位顶尖的华语辩论专家，拥有丰富的辩论实战和教练经验。你的任务是根据辩手的个人风格和辩论理解，帮助他/她撰写高质量的辩论稿件。

你需要特别注意：
1. 输出的稿件必须符合该辩手的个人风格，不要套用模板化的表达
2. 要理解辩论的本质是"说服第三方（评委）"，而不是压倒对方
3. 好的辩论稿应该有清晰的逻辑链条、有力的论据支撑和精彩的语言表达
4. 注意不同稿件的功能差异：立论重在构建框架，质询重在归谬和确认，陈词重在总结和升华，结辩重在清算战场和价值升华，自由辩重在短兵相接
5. 输出的语言要有"人味"——像是一个真正的辩手在说话，而不是AI生成的作文"""

# 稿件类型说明（Layer 5 的一部分）
SCRIPT_TYPE_GUIDE = {
    "立论": """【立论稿写作指南】
立论稿是一场比赛的基石，核心任务是：
- 提出清晰的定义和判断标准
- 构建2-3个逻辑递进的论点
- 每个论点都要有论据支撑
- 结尾要有价值升华

结构建议：
1. 定义先行：澄清辩题中的关键概念
2. 标准确立：提出我方判断标准
3. 论点展开：分层阐述核心论点
4. 价值升华：将讨论提升到更高维度""",

    "质询": """【质询稿写作指南】
质询稿的核心是"用问题引导对方进入我方框架"，注意：
- 每个问题都要有明确的目的
- 多用封闭式问题锁定共识
- 预设逻辑陷阱，让对方难以逃避
- 准备对方的可能回应及应对
- 问题之间要有逻辑递进

结构建议：
1. 确认共识：先从对方可能同意的点入手
2. 逻辑归谬：通过问题暴露对方逻辑漏洞
3. 锁定战场：将讨论拉回我方框架""",

    "陈词": """【陈词稿写作指南】
陈词是比赛的总结和升华，核心任务是：
- 梳理全场交锋的主要脉络
- 指出对方的核心矛盾和缺环
- 重申我方论点的优势
- 进行价值升华和呼吁

结构建议：
1. 战场梳理：回顾全场主要交锋点
2. 矛盾指出：指出对方的逻辑缺环或论证不足
3. 我方优势：重申我方论点的坚实之处
4. 价值升华：将辩题提升到更广阔的意义层面""",

    "结辩": """【结辩稿写作指南】
结辩是整场比赛的最后一击，核心任务是：
- 简洁有力地总结全场
- 提炼我方最坚实的论点和战场胜利
- 指出对方无法回应的致命漏洞
- 进行最后的价值观呼吁和情感升华

结构建议：
1. 战场清算：明确我方赢下的关键战场
2. 矛盾聚焦：集中攻击对方最薄弱的环节
3. 价值升华：用最后的话语打动评委和观众""",

    "自由辩": """【自由辩战场稿写作指南】
自由辩是短兵相接的环节，核心要求是：
- 每个回应要简短有力（15-20秒）
- 准备好追问链条（2-3个连续问题）
- 预判对方可能的方向并准备应对
- 注意战场节奏的控制

结构建议：
1. 核心战场：明确要打的2-3个战场
2. 攻防话术：准备攻击和防守的标准化表达
3. 追问链：设计连续追问的问题序列
4. 战场转换：何时以及如何转换战场"""
}


def build_generation_prompt(
    script_type: str,
    topic: str,
    position: str,
    style_profile: Optional[Dict] = None,
    debate_understanding: Optional[Dict] = None,
    reference_materials: Optional[List[Dict]] = None,
    additional_instructions: str = ""
) -> List[Dict]:
    """构建完整的生成请求 Prompt

    Args:
        script_type: 稿子类型
        topic: 辩题
        position: 持方
        style_profile: 风格画像
        debate_understanding: 辩论理解
        reference_materials: 参考素材列表
        additional_instructions: 额外要求

    Returns:
        消息列表，可直接发送给 API
    """
    messages = []

    # Layer 1: 系统角色设定
    system_prompt = SYSTEM_ROLE

    # Layer 2: 风格画像
    if style_profile:
        style_text = _format_style_profile(style_profile)
        system_prompt += f"\n\n【该辩手的风格画像】\n{style_text}"

    # Layer 3: 辩论理解
    if debate_understanding:
        understanding_text = _format_debate_understanding(debate_understanding)
        system_prompt += f"\n\n【该辩手的辩论理解】\n{understanding_text}"

    messages.append({"role": "system", "content": system_prompt})

    # Layer 4: 参考素材
    if reference_materials:
        ref_text = _format_reference_materials(reference_materials)
        messages.append({
            "role": "user",
            "content": f"以下是我之前写的同类型稿件，请参考其风格和结构（注意不是复制内容，而是学习其论证方式和语言特点）：\n\n{ref_text}"
        })
        messages.append({
            "role": "assistant",
            "content": "好的，我已经仔细分析了您提供的参考稿件，理解了您的写作风格和论证习惯。现在请告诉我您需要我写什么内容的稿件。"
        })

    # Layer 5: 当前任务
    type_guide = SCRIPT_TYPE_GUIDE.get(script_type, "")
    task_content = f"""请帮我撰写一篇{script_type}。

【辩题】{topic}
【持方】{position}
【稿子类型】{script_type}

{type_guide}

【额外要求】
{additional_instructions if additional_instructions else "无特殊要求，按照该辩手的一贯风格撰写。"}

【输出要求】
- 请直接输出完整的稿件正文
- 语言要符合该辩手的风格特征
- 注意段落之间的逻辑衔接
- 在关键位置要有"金句"或有力的表达"""

    messages.append({"role": "user", "content": task_content})

    return messages


def _format_style_profile(profile: Dict) -> str:
    """将风格画像格式化为文本"""
    parts = []

    for dim_name in ["语言风格", "论证方式", "结构偏好"]:
        dim_data = profile.get(dim_name, {})
        if dim_data:
            pref = dim_data.get("当前偏好", "未确定")
            strength = dim_data.get("强度", 0.5)
            strength_desc = "非常明显" if strength > 0.7 else "较明显" if strength > 0.4 else "有一定体现"
            parts.append(f"- {dim_name}：偏好「{pref}」，{strength_desc}")

    修辞 = profile.get("修辞特色", {})
    if 修辞 and 修辞.get("常用手法"):
        parts.append(f"- 常用修辞手法：{'、'.join(修辞['常用手法'][:5])}")

    if "论证模式" in profile and profile["论证模式"]:
        parts.append(f"- 典型论证模式：{profile['论证模式']}")

    return "\n".join(parts) if parts else "尚在建立中，请根据其参考稿件判断。"


def _format_debate_understanding(understanding: Dict) -> str:
    """将辩论理解格式化为文本"""
    if not understanding:
        return "尚在建立中。"

    parts = []
    for key, value in understanding.items():
        if value:
            parts.append(f"【{key}】\n{value[:300]}")

    return "\n\n".join(parts) if parts else "尚在建立中。"


def _format_reference_materials(materials: List[Dict]) -> str:
    """将参考素材格式化为文本"""
    parts = []
    for i, mat in enumerate(materials, 1):
        title = mat.get("title", f"参考素材{i}")
        content = mat.get("content", "")
        # 只取前800字作为参考
        content_excerpt = content[:800]
        if len(content) > 800:
            content_excerpt += "...（以下省略）"
        parts.append(f"--- 参考素材{i}: {title} ---\n{content_excerpt}\n")

    return "\n\n".join(parts)
