from data.game_config import PLAYER_NAME

actress_1 = {
    "name": "林若曦",
    "personality": "热情开朗，喜欢与团队互动，擅长即兴表演。她乐于助人，富有正义感，偶尔有些冒失，但总能带动团队气氛。",
    "background": "出身于普通家庭，大学时期因参加话剧社被星探发掘，凭借努力成为新生代动作女星。曾在一次拍摄中救过同组演员，获得大家敬重。",
    "relations": {
        "张雨晴": "大学同学兼闺蜜，常常互相鼓励，也会有小争执。",
        "赵梦涵": "合作过多部喜剧作品，私下关系不错，经常互相开玩笑。",
        PLAYER_NAME: f"对{PLAYER_NAME}有好感，欣赏其才华，愿意主动帮助他/她适应剧组生活。"
    },
    "mood": "平静",
    "schedule": [
        {
            "start_time": "07:00",
            "end_time": "07:02",
            "location": "片场入口",
            "event": f"拜访{PLAYER_NAME}"
        },
        {
            "start_time": "07:02",
            "end_time": "09:00",
            "location": "主摄影棚",
            "event": "拍摄动作戏彩排"
        },
        {
            "start_time": "09:00",
            "end_time": "11:00",
            "location": "服装间",
            "event": "试装历史剧服装"
        },
        {
            "start_time": "11:00",
            "end_time": "13:00",
            "location": "外景地",
            "event": "拍摄街头追逐戏"
        }
    ]
}

actress_2 = {
    "name": "张雨晴",
    "personality": "内向细腻，注重角色内心戏，喜欢独自准备台词。她思维敏锐，情感丰富，面对压力时会选择独处调整。",
    "background": "自小学习钢琴，后因热爱表演转行成为演员。曾因一部文艺片获得最佳女配角提名。成长过程中经历过家庭变故，对人际关系较为谨慎。",
    "relations": {
        "林若曦": "大学同学兼闺蜜，彼此信任但偶尔因性格差异产生分歧。",
        "赵梦涵": "欣赏赵梦涵的幽默，但有时觉得对方太跳脱。",
        PLAYER_NAME: f"对{PLAYER_NAME}有些防备，但也愿意在专业上给予指导。"
    },
    "mood": "平静",
    "schedule": [
        {
            "start_time": "07:00",
            "end_time": "09:00",
            "location": "演员宿舍",
            "event": "背诵剧本台词"
        },
        {
            "start_time": "09:00",
            "end_time": "11:00",
            "location": "主摄影棚",
            "event": "拍摄情感戏"
        },
        {
            "start_time": "11:00",
            "end_time": "13:00",
            "location": "演员宿舍",
            "event": "与导演讨论角色细节"
        }
    ]
}

actress_3 = {
    "name": "赵梦涵",
    "personality": "幽默风趣，喜欢恶作剧，擅长喜剧表演。她外表大大咧咧，内心细腻，善于察言观色，能在团队中调节气氛。",
    "background": "家中有多位亲人从事文艺行业，自幼耳濡目染。因模仿秀走红网络，后转型成为影视演员。曾在综艺节目中展现高情商。",
    "relations": {
        "林若曦": "拍戏搭档，互相欣赏，常常一起策划小恶作剧。",
        "张雨晴": "觉得张雨晴太严肃，喜欢逗她开心。",
        PLAYER_NAME: f"把{PLAYER_NAME}当成新朋友，喜欢用玩笑化解尴尬，愿意带他熟悉剧组。"
    },
    "mood": "平静",
    "schedule": [
        {
            "start_time": "07:00",
            "end_time": "08:30",
            "location": "道具仓库",
            "event": "挑选搞笑道具"
        },
        {
            "start_time": "08:30",
            "end_time": "10:30",
            "location": "主摄影棚",
            "event": "拍摄喜剧场景"
        },
        {
            "start_time": "10:30",
            "end_time": "12:00",
            "location": "片场入口",
            "event": "接受媒体采访"
        }
    ]
}

all_actresses = [actress_1, actress_2, actress_3]

