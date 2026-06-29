"""风格分析引擎 - 从用户素材中提取风格特征"""

import json
import re
from typing import Dict, List, Any

# 风格维度定义
STYLE_DIMENSIONS = {
    "语言风格": {
        "维度": ["平实", "华丽", "犀利", "幽默", "学院派"],
        "描述": "语言的整体风格倾向"
    },
    "论证方式": {
        "维度": ["逻辑推演", "案例驱动", "情感共鸣", "数据论证", "哲理思辨"],
        "描述": "主要的论证方法"
    },
    "结构偏好": {
        "维度": ["总分总", "层层递进", "并列展开", "破立结合", "问题导向"],
        "描述": "文章的结构组织方式"
    },
    "修辞特色": {
        "维度": ["比喻", "排比", "反问", "设问", "对比", "引用", "拟人", "夸张"],
        "描述": "常用的修辞手法"
    }
}

# 分析提示词
ANALYSIS_PROMPT_TEMPLATE = """你是一位专业的辩论稿件分析专家。请分析以下辩论稿件的风格特征。

【稿件类型】：{material_type}
【稿件标题】：{title}
【稿件内容】：
{content}

请从以下维度分析这篇稿件的风格特征，以JSON格式返回（不要包含其他文字）：

{{
    "语言风格": {{
        "偏好": "平实/华丽/犀利/幽默/学院派 中最符合的一个",
        "强度": 0.0-1.0 之间的数值,
        "依据": "简要说明判断依据"
    }},
    "论证方式": {{
        "偏好": "逻辑推演/案例驱动/情感共鸣/数据论证/哲理思辨 中最符合的一个",
        "强度": 0.0-1.0,
        "依据": "简要说明判断依据"
    }},
    "结构偏好": {{
        "偏好": "总分总/层层递进/并列展开/破立结合/问题导向 中最符合的一个",
        "强度": 0.0-1.0,
        "依据": "简要说明判断依据"
    }},
    "修辞特色": {{
        "常用手法": ["手法1", "手法2", ...],
        "依据": "使用了哪些修辞"
    }},
    "关键论点": ["论点1", "论点2", ...],
    "金句摘录": ["金句1", "金句2", ...],
    "论证模式": "描述该稿件的典型论证模式"
}}
"""


async def analyze_material(content: str, material_type: str, title: str,
                           deepseek_client=None) -> Dict[str, Any]:
    """分析一篇素材的风格特征

    如果提供了 deepseek_client，使用 AI 进行分析；
    否则使用基于规则的简单分析。
    """
    if deepseek_client and deepseek_client.is_configured():
        return await _ai_analysis(content, material_type, title, deepseek_client)
    else:
        return rule_based_analysis(content, material_type)


async def _ai_analysis(content: str, material_type: str, title: str,
                        client) -> Dict[str, Any]:
    """使用 AI 进行风格分析"""
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        material_type=material_type,
        title=title,
        content=content[:3000]  # 限制长度
    )

    messages = [
        {"role": "system", "content": "你是一名专业的辩论稿件分析专家。请严格按照要求输出JSON。"},
        {"role": "user", "content": prompt}
    ]

    response = await client.chat(messages=messages, temperature=0.1, max_tokens=2048)
    result_text = client.extract_content(response)

    # 尝试从回复中提取 JSON
    try:
        # 查找 JSON 部分（可能在 ```json 代码块中）
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', result_text)
        if json_match:
            return json.loads(json_match.group(1))
        else:
            return json.loads(result_text)
    except (json.JSONDecodeError, KeyError):
        return rule_based_analysis(content, material_type)


def rule_based_analysis(content: str, material_type: str) -> Dict[str, Any]:
    """基于规则的简单风格分析（返回自然语言描述）"""
    word_count = len(content)
    sentences = re.split(r'[。！？；\n]', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    avg_sentence_len = word_count / max(len(sentences), 1)

    exclamation_count = content.count('！')
    question_count = content.count('？')

    rhetoric_check = {
        "比喻": len(re.findall(r'像|如|仿佛|好似|如同', content)),
        "排比": len(re.findall(r'(是|有|要|能|让)[^，。！？]{2,10}(?:，|；)[^，。！？]*?\1', content)),
        "反问": len(re.findall(r'难道|岂不是|何尝|怎能', content)),
        "设问": len(re.findall(r'[。！？]?(什么|为什么|如何)[^。！？]*\?', content)),
        "对比": len(re.findall(r'而|但|却|然而|反之|与此不同', content)),
    }
    active_rhetoric = [k for k, v in rhetoric_check.items() if v > 2]

    # 生成自然语言描述
    type_names = {"立论": "立论稿", "质询": "质询稿", "陈词": "陈词稿", "结辩": "结辩稿", "自由辩": "自由辩战场稿"}
    type_name = type_names.get(material_type, material_type)

    # 语言风格描述
    if exclamation_count > word_count * 0.02:
        lang_desc = "语言风格偏向犀利，善于使用感叹句增强语气，情感饱满、有感染力"
    elif avg_sentence_len > 40:
        lang_desc = f"语言风格偏学院派，句子较长（平均{avg_sentence_len:.0f}字），信息密度高，逻辑严谨"
    elif rhetoric_check["比喻"] > 3:
        lang_desc = "语言风格偏向华丽，善于使用比喻等修辞手法，表达富有文学色彩"
    else:
        lang_desc = "语言风格平实朴素，句子简洁明了（平均句长" + f"{avg_sentence_len:.0f}字），易于理解，注重说理而非辞藻"

    # 论证方式描述
    if question_count > word_count * 0.01:
        arg_desc = "论证方式以提问引导为主，通过设问和反问推动论证，引导听众跟随思路"
    elif rhetoric_check["对比"] > 5:
        arg_desc = "论证方式偏好对比论证，善于在对比中凸显观点，使立场更加鲜明"
    else:
        arg_desc = "论证以逻辑推演为主要方式，注重概念定义和逻辑链条的搭建"

    # 结构描述
    if material_type == "立论":
        struct_desc = "结构上遵循「定义—标准—论点—升华」的经典立论框架，层次分明"
    elif material_type == "质询":
        struct_desc = "以问题链驱动，问题之间具有逻辑递进关系，逐步引导对方进入预设框架"
    elif material_type == "自由辩":
        struct_desc = "以短句和快速攻防为主，节奏紧凑，适合短兵相接的战场环境"
    else:
        struct_desc = "结构完整，起承转合清晰，论述有层次感"

    # 修辞描述
    if active_rhetoric:
        rhetoric_desc = "修辞手法上，使用了" + "、".join(active_rhetoric) + "等技巧"
        if "比喻" in active_rhetoric:
            rhetoric_desc += "，比喻使抽象概念具象化"
        if "排比" in active_rhetoric:
            rhetoric_desc += "，排比增强了语言的节奏感和气势"
        if "反问" in active_rhetoric:
            rhetoric_desc += "，反问加强了说服力和代入感"
    else:
        rhetoric_desc = "修辞手法使用较为克制，以清晰表达观点为首要目标"

    # 字数评估
    if word_count < 300:
        length_desc = f"全文约{word_count}字，篇幅较短，适合质询或自由辩等快节奏环节"
    elif word_count < 800:
        length_desc = f"全文约{word_count}字，篇幅适中，信息密度合理"
    else:
        length_desc = f"全文约{word_count}字，篇幅较长，内容充实"

    # 整体评价
    summary = f"这是一篇{type_name}，{lang_desc}。{arg_desc}。{struct_desc}。{rhetoric_desc}。{length_desc}。"

    return {
        "整体评价": summary,
        "语言风格": lang_desc + "。",
        "论证方式": arg_desc + "。",
        "结构特点": struct_desc + "。",
        "修辞手法": rhetoric_desc + "。",
        "篇幅说明": length_desc + "。",
        "分析版本": "v2-natural"
    }


def merge_analysis_into_profile(existing_profile: Dict,
                                 new_analysis: Dict,
                                 material_type: str = None) -> Dict:
    """将新的分析结果合并到现有风格画像中——按素材类型聚合"""
    profile = existing_profile.copy() if existing_profile else {
        "累计分析": 0,
        "素材分析": {},       # { type: { "整体评价": ..., "语言风格": ..., ... } }
        "素材类型分布": {}
    }

    profile["累计分析"] = (profile.get("累计分析", 0) or 0) + 1

    # 按素材类型存储分析结果（每个类型只保留最新一条）
    if material_type:
        if "素材分析" not in profile:
            profile["素材分析"] = {}
        # 只提取关键描述字段
        type_analysis = {}
        for key in ["整体评价", "语言风格", "论证方式", "结构特点", "修辞手法", "篇幅说明"]:
            if key in new_analysis:
                type_analysis[key] = new_analysis[key]
        profile["素材分析"][material_type] = type_analysis

        # 统计素材类型分布
        if "素材类型分布" not in profile:
            profile["素材类型分布"] = {}
        profile["素材类型分布"][material_type] = profile["素材类型分布"].get(material_type, 0) + 1

    return profile
