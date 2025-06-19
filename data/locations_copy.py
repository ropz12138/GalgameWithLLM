from data.game_config import PLAYER_NAME, PLAYER_ROOM_NAME, PLAYER_ROOM_EN_NAME

studio_entrance = {
    "name": "片场入口",
    "en_name": "studio_entrance",
    "description": "一个热闹的入口，周围是高大的摄影棚和忙碌的工作人员。空气中弥漫着咖啡和道具涂料的气味。"
}

main_studio = {
    "name": "主摄影棚",
    "en_name": "main_studio",
    "description": "宽敞的摄影棚，巨大的绿幕墙和耀眼的灯光设备占据空间。地上散落着电缆和标记带。"
}

prop_warehouse = {
    "name": "道具仓库",
    "en_name": "prop_warehouse",
    "description": "堆满奇异道具的昏暗仓库，从仿古宝剑到科幻装置应有尽有。空气中飘着灰尘和旧木头的味道。"
}

costume_room = {
    "name": "服装间",
    "en_name": "costume_room",
    "description": "挂满各式戏服的房间，从宫廷礼服到太空服一应俱全。镜子旁堆放着化妆箱和假发。"
}

actor_dorm = {
    "name": "演员宿舍",
    "en_name": "actor_dorm",
    "description": "舒适的休息区域，摆放着沙发和床铺，墙上贴满剧本和角色海报。桌上放着零食和水瓶。"
}

outdoor_set = {
    "name": "外景地",
    "en_name": "outdoor_set",
    "description": "一片开阔区域，搭建着仿古街道布景。远处传来模拟爆炸声，演员在彩排动作戏。"
}

# 新增角色房间
lin_ruoxi_room = {
    "name": "林若曦的房间",
    "en_name": "lin_ruoxi_room",
    "description": "林若曦的个人房间，布置得温馨而充满活力，有一些健身器材和动作电影海报。"
}

zhang_yuqing_room = {
    "name": "张雨晴的房间",
    "en_name": "zhang_yuqing_room",
    "description": "张雨晴的个人房间，安静雅致，书架上摆满了书籍和剧本，窗边有舒适的阅读角。"
}

zhao_menghan_room = {
    "name": "赵梦涵的房间",
    "en_name": "zhao_menghan_room",
    "description": "赵梦涵的个人房间，色彩明快，有不少搞怪有趣的装饰品和小道具。"
}

user_room = {
    "name": PLAYER_ROOM_NAME,
    "en_name": PLAYER_ROOM_EN_NAME,
    "description": f"{PLAYER_NAME}的个人房间，布置得简洁而舒适，有一些游戏机和电影海报。"
}

all_locations_data = {
    "studio_entrance": studio_entrance,
    "main_studio": main_studio,
    "prop_warehouse": prop_warehouse,
    "costume_room": costume_room,
    "actor_dorm": actor_dorm,
    "outdoor_set": outdoor_set,
    "lin_ruoxi_room": lin_ruoxi_room,
    "zhang_yuqing_room": zhang_yuqing_room,
    "zhao_menghan_room": zhao_menghan_room,
    "user_room": user_room
}

# 新增：中英文名称到key的映射
location_name_map = {}
for key, loc in all_locations_data.items():
    location_name_map[key] = key
    location_name_map[loc["name"]] = key
    if "en_name" in loc:
        location_name_map[loc["en_name"]] = key

location_connections = {
    "studio_entrance": ["main_studio", "outdoor_set"],
    "main_studio": ["studio_entrance", "prop_warehouse", "costume_room"],
    "prop_warehouse": ["main_studio", "actor_dorm"],
    "costume_room": ["main_studio"],
    "actor_dorm": ["prop_warehouse", "lin_ruoxi_room", "zhang_yuqing_room", "zhao_menghan_room"],
    "outdoor_set": ["studio_entrance"],
    "lin_ruoxi_room": ["actor_dorm"],
    "zhang_yuqing_room": ["actor_dorm"],
    "zhao_menghan_room": ["actor_dorm"],
    "user_room": ["actor_dorm"]
}

