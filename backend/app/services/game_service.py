from typing import List, Dict, Any, Optional
import uuid
from enum import Enum

class GameState(str, Enum):
    INTRO = "intro"
    PLAYING = "playing"
    CHOICE = "choice"
    RESULT = "result"
    END = "end"

class GameService:
    """音频探险游戏服务 - 支持5-10轮的游戏深度"""

    def __init__(self):
        self.games = self._create_games()
        self.active_sessions: Dict[str, Dict] = {}

    def _create_games(self) -> Dict[str, Dict]:
        """创建游戏场景 - 根据难度设置不同深度"""
        return {
            # 简单模式：5轮
            "forest_adventure": {
                "id": "forest_adventure",
                "title": "森林探险",
                "description": "你醒来发现自己身处一片神秘的森林，需要找到出路...",
                "difficulty": "easy",
                "scenes": self._create_forest_scenes()
            },
            # 中等模式：7轮
            "space_station": {
                "id": "space_station",
                "title": "太空站危机",
                "description": "你在一座废弃的太空站醒来，氧气供应正在减少...",
                "difficulty": "medium",
                "scenes": self._create_space_scenes()
            },
            # 困难模式：10轮
            "detective": {
                "id": "detective",
                "title": "午夜侦探",
                "description": "一封神秘信件邀请你来到一座古堡，揭开尘封的秘密...",
                "difficulty": "hard",
                "scenes": self._create_detective_scenes()
            }
        }

    def _create_forest_scenes(self) -> Dict[str, Dict]:
        """创建森林探险场景 - 5轮深度"""
        return {
            # 第1轮
            "start": {
                "id": "start", "round": 1,
                "narration": "你醒来发现自己身处一片神秘的森林。阳光透过树叶洒下斑驳的光影。你听到远处传来潺潺的流水声，身后则是一条蜿蜒的小路。",
                "choices": [
                    {"key": "1", "text": "走向流水声", "next": "river"},
                    {"key": "2", "text": "沿着小路前进", "next": "path"},
                    {"key": "3", "text": "在原地寻找线索", "next": "search"},
                    {"key": "4", "text": "大声呼救", "next": "shout"}
                ]
            },
            # 第2轮
            "river": {
                "id": "river", "round": 2,
                "narration": "你来到一条清澈的小河边。河水不深，可以涉水过河。河对岸似乎有一座小木屋。岸边还有一只小船系在树旁。",
                "choices": [
                    {"key": "1", "text": "涉水过河", "next": "cross_shallow"},
                    {"key": "2", "text": "使用小船", "next": "boat_cross"},
                    {"key": "3", "text": "沿着河岸走", "next": "river_walk"},
                    {"key": "4", "text": "返回原地", "next": "start"}
                ]
            },
            "path": {
                "id": "path", "round": 2,
                "narration": "你沿着小路走了大约十分钟，发现前方有一个岔路口。左边通向一座古老的石桥，右边则是一片开阔的草地，远处有炊烟升起。",
                "choices": [
                    {"key": "1", "text": "走向石桥", "next": "bridge"},
                    {"key": "2", "text": "走向草地", "next": "meadow"},
                    {"key": "3", "text": "仔细观察地面", "next": "examine_ground"},
                    {"key": "4", "text": "返回", "next": "start"}
                ]
            },
            "search": {
                "id": "search", "round": 2,
                "narration": "你在周围仔细寻找。在树根下，你发现了一个旧背包。背包里有一张泛黄的地图、一个指南针和一些干粮。",
                "choices": [
                    {"key": "1", "text": "查看地图", "next": "check_map"},
                    {"key": "2", "text": "带上背包继续前进", "next": "with_backpack"},
                    {"key": "3", "text": "只拿指南针", "next": "take_compass"},
                    {"key": "4", "text": "放下背包", "next": "start"}
                ]
            },
            "shout": {
                "id": "shout", "round": 2,
                "narration": "你大声呼救。远处传来回声，但没有回应。突然，一群鸟从树上飞起，你注意到它们飞向的方向有一条隐藏的小径。",
                "choices": [
                    {"key": "1", "text": "跟随鸟的方向", "next": "bird_path"},
                    {"key": "2", "text": "继续呼喊", "next": "keep_shouting"},
                    {"key": "3", "text": "放弃呼救，自己探索", "next": "start"},
                    {"key": "4", "text": "爬上树观察", "next": "climb_tree"}
                ]
            },
            # 第3轮
            "cross_shallow": {
                "id": "cross_shallow", "round": 3,
                "narration": "你小心翼翼地涉水过河。河水冰凉但清澈见底。走到河中央时，你发现水里闪烁着金光，原来是几枚古老的硬币。",
                "choices": [
                    {"key": "1", "text": "继续过河", "next": "reach_cabin"},
                    {"key": "2", "text": "弯腰捡起硬币", "next": "get_coins"},
                    {"key": "3", "text": "观察周围", "next": "look_around"},
                    {"key": "4", "text": "返回岸边", "next": "river"}
                ]
            },
            "boat_cross": {
                "id": "boat_cross", "round": 3,
                "narration": "你解开小船，轻轻划向对岸。船身有些破旧但还算稳固。在河中央，你看到水面上漂浮着一个木盒。",
                "choices": [
                    {"key": "1", "text": "继续划向对岸", "next": "reach_cabin"},
                    {"key": "2", "text": "捞起木盒查看", "next": "open_box"},
                    {"key": "3", "text": "仔细观察小船", "next": "examine_boat"},
                    {"key": "4", "text": "返回岸边", "next": "river"}
                ]
            },
            "bridge": {
                "id": "bridge", "round": 3,
                "narration": "古老的石桥看起来有些年代了，但结构依然坚固。桥下是清澈的溪流。穿过石桥，你看到远处有炊烟升起，似乎是一个村庄的方向。",
                "choices": [
                    {"key": "1", "text": "过桥向炊烟方向走", "next": "village_path"},
                    {"key": "2", "text": "在桥边休息一下", "next": "rest_bridge"},
                    {"key": "3", "text": "下到溪流边查看", "next": "stream_side"},
                    {"key": "4", "text": "返回岔路口", "next": "path"}
                ]
            },
            "check_map": {
                "id": "check_map", "round": 3,
                "narration": "地图显示这片森林的北方有一个村庄，东方有一座古老的寺庙，南方则是森林的边缘。你现在的位置在森林中央，地图上标着几个安全路线。",
                "choices": [
                    {"key": "1", "text": "向北去村庄", "next": "north_path"},
                    {"key": "2", "text": "向东去寺庙", "next": "east_path"},
                    {"key": "3", "text": "向南走森林边缘", "next": "south_path"},
                    {"key": "4", "text": "收起地图自己探索", "next": "start"}
                ]
            },
            # 第4轮
            "reach_cabin": {
                "id": "reach_cabin", "round": 4,
                "narration": "你成功到达对岸。小木屋看起来很旧，门虚掩着。透过窗户，你看到里面有一个人影在移动。烟囱冒着烟。",
                "choices": [
                    {"key": "1", "text": "敲门询问", "next": "knock_door"},
                    {"key": "2", "text": "大声喊话", "next": "call_out"},
                    {"key": "3", "text": "悄悄观察", "next": "observe_cabin"},
                    {"key": "4", "text": "绕过木屋继续走", "next": "bypass_cabin"}
                ]
            },
            "village_path": {
                "id": "village_path", "round": 4,
                "narration": "你沿着炊烟的方向前进。路越来越宽，最后变成了一条土路。远处，你看到了几间农舍，还有一个正在田里工作的农民。",
                "choices": [
                    {"key": "1", "text": "走向农民求助", "next": "ask_farmer"},
                    {"key": "2", "text": "自己走向村庄", "next": "walk_to_village"},
                    {"key": "3", "text": "先观察一下", "next": "observe_village"},
                    {"key": "4", "text": "返回石桥", "next": "bridge"}
                ]
            },
            "north_path": {
                "id": "north_path", "round": 4,
                "narration": "你按照地图向北方前进。路途中，你遇到了一条分岔的小径，地图上没有标注。主路继续向北，小径则通向未知的方向。",
                "choices": [
                    {"key": "1", "text": "继续沿主路向北", "next": "main_road_north"},
                    {"key": "2", "text": "探索小径", "next": "small_path"},
                    {"key": "3", "text": "用指南针确认方向", "next": "check_direction"},
                    {"key": "4", "text": "返回原地", "next": "check_map"}
                ]
            },
            # 第5轮 - 结局
            "knock_door": {
                "id": "knock_door", "round": 5,
                "narration": "你敲了敲门。门开了，一位和蔼的老人出现在门口。他看到你后微笑着说：又是迷路的人啊，进来休息一下吧。他给了你食物和水，并指引你走出了森林。恭喜你完成了探险！",
                "choices": [], "is_end": True, "result": "success"
            },
            "ask_farmer": {
                "id": "ask_farmer", "round": 5,
                "narration": "农民看到你很惊讶，但很快露出友善的笑容。他告诉你这里离最近的城镇只有两公里，并主动带你走出了森林。恭喜你成功完成探险！",
                "choices": [], "is_end": True, "result": "success"
            },
            "main_road_north": {
                "id": "main_road_north", "round": 5,
                "narration": "你沿着主路继续向北。大约走了二十分钟，森林变得越来越稀疏。最终，你走出了森林，看到了一条公路。你成功脱险了！恭喜完成探险！",
                "choices": [], "is_end": True, "result": "success"
            },
            # 失败场景
            "get_coins": {
                "id": "get_coins", "round": 3,
                "narration": "你弯腰去捡硬币，脚下一滑，摔倒在河里。虽然最终爬上了岸，但你浑身湿透，需要找地方烘干衣服。你失去了宝贵的时间。",
                "choices": [
                    {"key": "1", "text": "继续前进", "next": "reach_cabin"},
                    {"key": "2", "text": "返回晒太阳", "next": "river"}
                ]
            },
            "open_box": {
                "id": "open_box", "round": 3,
                "narration": "木盒里有一张纸条，上面写着：真正的出路在北方。这是之前有人留下的提示！你感到信心倍增。",
                "choices": [
                    {"key": "1", "text": "继续划向对岸", "next": "reach_cabin"},
                    {"key": "2", "text": "返回重新规划路线", "next": "start"}
                ]
            },
            "call_out": {
                "id": "call_out", "round": 4,
                "narration": "你大声喊话。门开了，一位老人走了出来，手里拿着猎枪。但在看清你只是迷路的旅行者后，他放下了枪，邀请你进屋休息。",
                "choices": [
                    {"key": "1", "text": "进屋休息", "next": "knock_door"},
                    {"key": "2", "text": "问路后离开", "next": "bypass_cabin"}
                ]
            },
            "observe_cabin": {
                "id": "observe_cabin", "round": 4,
                "narration": "你悄悄观察了一会儿。看起来里面住着一个普通的人家，烟囱冒着炊烟，院子里还晾着衣服。",
                "choices": [
                    {"key": "1", "text": "敲门求助", "next": "knock_door"},
                    {"key": "2", "text": "绕过木屋", "next": "bypass_cabin"}
                ]
            },
            "bypass_cabin": {
                "id": "bypass_cabin", "round": 5,
                "narration": "你绕过木屋继续前进。走了大约半小时，你发现森林变得越来越稀疏。最终，你找到了一条通往外界的路。恭喜完成探险！",
                "choices": [], "is_end": True, "result": "success"
            },
            "walk_to_village": {
                "id": "walk_to_village", "round": 5,
                "narration": "你自己走向村庄。村民们都很友善，有人给你指了通往最近城镇的路。你成功走出了森林！恭喜完成探险！",
                "choices": [], "is_end": True, "result": "success"
            },
            "small_path": {
                "id": "small_path", "round": 5,
                "narration": "你决定探索小径。走了大约十五分钟，你惊喜地发现这条小径是通往森林边缘的捷径！你成功脱险了！恭喜完成探险！",
                "choices": [], "is_end": True, "result": "success"
            },
            "bird_path": {
                "id": "bird_path", "round": 3,
                "narration": "你沿着鸟飞的方向前进，发现了一条隐藏的小径。小径的入口处有人工留下的标记，似乎是一条老路。",
                "choices": [
                    {"key": "1", "text": "沿着小径前进", "next": "small_path"},
                    {"key": "2", "text": "返回原地", "next": "start"}
                ]
            },
            "climb_tree": {
                "id": "climb_tree", "round": 3,
                "narration": "你爬上一棵大树，从高处看到森林的北方有房屋和炊烟。你记下方向后爬下树，准备向北前进。",
                "choices": [
                    {"key": "1", "text": "向北前进", "next": "north_path"},
                    {"key": "2", "text": "返回原地", "next": "start"}
                ]
            },
            # 更多辅助场景
            "river_walk": {
                "id": "river_walk", "round": 3,
                "narration": "你沿着河岸走了大约二十分钟，发现了一个渡口。附近有渔民正在修理渔网。",
                "choices": [
                    {"key": "1", "text": "向渔民求助", "next": "ask_farmer"},
                    {"key": "2", "text": "自己过河", "next": "cross_shallow"},
                    {"key": "3", "text": "返回河边", "next": "river"}
                ]
            },
            "meadow": {
                "id": "meadow", "round": 3,
                "narration": "开阔的草地上开满了野花。远处有一群鹿在悠闲地吃草。草地尽头有一条通往森林边缘的小路。",
                "choices": [
                    {"key": "1", "text": "穿过草地走向边缘", "next": "small_path"},
                    {"key": "2", "text": "跟随鹿群", "next": "follow_deer"},
                    {"key": "3", "text": "返回岔路口", "next": "path"}
                ]
            },
            "follow_deer": {
                "id": "follow_deer", "round": 4,
                "narration": "鹿群带你来到了一处水源，旁边有一条通往外界的路。你成功找到了出路！",
                "choices": [], "is_end": True, "result": "success"
            },
            "with_backpack": {
                "id": "with_backpack", "round": 3,
                "narration": "你背上背包，感觉安心了许多。地图和指南针将帮助你找到正确的方向。",
                "choices": [
                    {"key": "1", "text": "向北走", "next": "north_path"},
                    {"key": "2", "text": "向东走", "next": "east_path"},
                    {"key": "3", "text": "自己判断方向", "next": "start"}
                ]
            },
            "east_path": {
                "id": "east_path", "round": 4,
                "narration": "你向东方前进，来到了一座古老的寺庙。寺庙里有一位智慧的长者，他热情地招待了你，并告诉你通往最近城镇的路。",
                "choices": [], "is_end": True, "result": "success"
            },
            "south_path": {
                "id": "south_path", "round": 4,
                "narration": "你向南方走，很快就来到了森林的边缘。一条大路通向外界，你成功脱险了！",
                "choices": [], "is_end": True, "result": "success"
            },
            "take_compass": {
                "id": "take_compass", "round": 3,
                "narration": "你只拿了指南针。它帮助你确定方向。你决定向北走，那是地图上标示有村庄的方向。",
                "choices": [
                    {"key": "1", "text": "向北走", "next": "north_path"},
                    {"key": "2", "text": "返回拿背包", "next": "search"}
                ]
            },
            "keep_shouting": {
                "id": "keep_shouting", "round": 3,
                "narration": "你继续呼喊。终于，远处传来了回应！有人正在向你走来！",
                "choices": [
                    {"key": "1", "text": "等待救援", "next": "rescue"},
                    {"key": "2", "text": "迎向声音", "next": "meet_rescuer"}
                ]
            },
            "rescue": {
                "id": "rescue", "round": 4,
                "narration": "几分钟后，一位护林员出现在你面前。他带你走出了森林。你成功获救了！",
                "choices": [], "is_end": True, "result": "success"
            },
            "meet_rescuer": {
                "id": "meet_rescuer", "round": 4,
                "narration": "你迎向声音的方向，遇到了一位正在巡逻的护林员。他带你走出了森林。恭喜完成探险！",
                "choices": [], "is_end": True, "result": "success"
            }
        }

    def _create_space_scenes(self) -> Dict[str, Dict]:
        """创建太空站场景 - 7轮深度"""
        return {
            # 第1轮
            "start": {
                "id": "start", "round": 1,
                "narration": "警报声将你从休眠舱中唤醒。太空站的氧气系统出现故障，剩余氧气只够30分钟。你需要尽快找到逃生舱或修复氧气系统。控制室在走廊尽头，逃生舱在左边通道。",
                "choices": [
                    {"key": "1", "text": "前往控制室查看系统状态", "next": "control_room"},
                    {"key": "2", "text": "寻找最近的逃生舱", "next": "escape_pod"},
                    {"key": "3", "text": "检查休眠舱的紧急物资", "next": "check_supplies"},
                    {"key": "4", "text": "用通讯设备求救", "next": "radio"}
                ]
            },
            # 第2轮
            "control_room": {
                "id": "control_room", "round": 2,
                "narration": "控制室的屏幕显示氧气泄漏在C区。你可以尝试远程关闭C区的气闸，或者直接前往修复。系统也显示有一艘补给船将在20分钟后对接，D区有备用逃生舱。",
                "choices": [
                    {"key": "1", "text": "远程关闭C区气闸", "next": "close_airlock"},
                    {"key": "2", "text": "前往C区修复", "next": "repair_c"},
                    {"key": "3", "text": "等待补给船", "next": "wait_ship"},
                    {"key": "4", "text": "去D区逃生舱", "next": "escape_pod_d"}
                ]
            },
            "escape_pod": {
                "id": "escape_pod", "round": 2,
                "narration": "你找到了最近的逃生舱，但它需要启动密码。墙上有模糊的数字痕迹，似乎是7开头的四位数。控制面板上有数字键盘。",
                "choices": [
                    {"key": "1", "text": "尝试常见密码", "next": "try_password"},
                    {"key": "2", "text": "寻找密码线索", "next": "find_clue"},
                    {"key": "3", "text": "放弃逃生舱，去控制室", "next": "control_room"},
                    {"key": "4", "text": "尝试破解系统", "next": "hack_system"}
                ]
            },
            "check_supplies": {
                "id": "check_supplies", "round": 2,
                "narration": "休眠舱附近有一个紧急物资柜。里面有氧气瓶、手电筒和一本操作手册。氧气瓶可以延长你的生存时间约15分钟。",
                "choices": [
                    {"key": "1", "text": "带上氧气瓶去控制室", "next": "control_room_with_o2"},
                    {"key": "2", "text": "查看操作手册", "next": "read_manual"},
                    {"key": "3", "text": "寻找逃生舱", "next": "escape_pod"},
                    {"key": "4", "text": "用通讯设备求救", "next": "radio"}
                ]
            },
            "radio": {
                "id": "radio", "round": 2,
                "narration": "你打开通讯设备，发出求救信号。几分钟后，收到了补给船的回复：他们正在接近，预计10分钟后对接。但同时，C区的氧气泄漏速度在加快。",
                "choices": [
                    {"key": "1", "text": "等待补给船对接", "next": "wait_rescue_ship"},
                    {"key": "2", "text": "去控制室关闭气闸", "next": "control_room"},
                    {"key": "3", "text": "同时准备逃生舱", "next": "escape_pod"},
                    {"key": "4", "text": "检查氧气泄漏源头", "next": "repair_c"}
                ]
            },
            # 第3轮
            "close_airlock": {
                "id": "close_airlock", "round": 3,
                "narration": "你尝试远程关闭C区气闸。系统提示需要管理员授权。你发现日志中有一条记录：紧急情况下可使用空间站编号作为密码。",
                "choices": [
                    {"key": "1", "text": "查找空间站编号", "next": "find_station_id"},
                    {"key": "2", "text": "尝试常见编号", "next": "try_common_id"},
                    {"key": "3", "text": "手动前往C区关闭", "next": "repair_c"},
                    {"key": "4", "text": "放弃，寻找其他方案", "next": "escape_pod"}
                ]
            },
            "repair_c": {
                "id": "repair_c", "round": 3,
                "narration": "你前往C区。走廊里的氧气浓度明显降低。你发现泄漏点是一个松动的阀门，需要专用工具拧紧。墙上有一个工具箱。",
                "choices": [
                    {"key": "1", "text": "从工具箱找工具", "next": "get_tools"},
                    {"key": "2", "text": "尝试用手拧紧", "next": "hand_tighten"},
                    {"key": "3", "text": "寻找其他泄漏点", "next": "find_other_leaks"},
                    {"key": "4", "text": "返回控制室", "next": "control_room"}
                ]
            },
            "escape_pod_d": {
                "id": "escape_pod_d", "round": 3,
                "narration": "你来到D区。这里的逃生舱看起来更新，但也需要密码。旁边有一张便条，上面写着：安全第一，密码是船长的生日，查看员工档案。",
                "choices": [
                    {"key": "1", "text": "查找员工档案", "next": "find_records"},
                    {"key": "2", "text": "返回A区逃生舱", "next": "escape_pod"},
                    {"key": "3", "text": "尝试破解", "next": "hack_pod_d"},
                    {"key": "4", "text": "去控制室", "next": "control_room"}
                ]
            },
            # 第4轮
            "find_station_id": {
                "id": "find_station_id", "round": 4,
                "narration": "你在控制台上找到了空间站的铭牌：太空站编号SS-2077。你尝试输入这个编号作为授权密码。",
                "choices": [
                    {"key": "1", "text": "确认输入", "next": "authorize_success"},
                    {"key": "2", "text": "再检查一遍", "next": "verify_id"}
                ]
            },
            "get_tools": {
                "id": "get_tools", "round": 4,
                "narration": "工具箱里有扳手、螺丝刀和胶带。你用扳手尝试拧紧阀门，但阀门已经锈蚀，需要更多力气。",
                "choices": [
                    {"key": "1", "text": "用力拧紧", "next": "force_tighten"},
                    {"key": "2", "text": "用胶带临时封堵", "next": "tape_fix"},
                    {"key": "3", "text": "寻找帮助", "next": "radio"}
                ]
            },
            "find_records": {
                "id": "find_records", "round": 4,
                "narration": "你在附近的终端机上找到了员工档案。船长名叫约翰·陈，生日是2077年3月15日。密码可能是0315或031577。",
                "choices": [
                    {"key": "1", "text": "尝试0315", "next": "try_password_1"},
                    {"key": "2", "text": "尝试031577", "next": "try_password_2"},
                    {"key": "3", "text": "尝试20770315", "next": "try_password_3"}
                ]
            },
            # 第5轮
            "authorize_success": {
                "id": "authorize_success", "round": 5,
                "narration": "密码正确！气闸开始关闭。系统显示氧气水平正在恢复。但与此同时，你注意到补给船发来消息：对接可能需要额外5分钟，请耐心等待。",
                "choices": [
                    {"key": "1", "text": "等待补给船", "next": "wait_for_docking"},
                    {"key": "2", "text": "准备备用逃生舱", "next": "escape_pod_d"},
                    {"key": "3", "text": "检查其他系统", "next": "check_systems"}
                ]
            },
            "force_tighten": {
                "id": "force_tighten", "round": 5,
                "narration": "你用尽全力，终于拧紧了阀门！氧气泄漏停止了。但你的氧气瓶储量已经很低，需要尽快撤离。",
                "choices": [
                    {"key": "1", "text": "返回控制室", "next": "return_to_control"},
                    {"key": "2", "text": "去最近的逃生舱", "next": "escape_pod"}
                ]
            },
            "try_password_1": {
                "id": "try_password_1", "round": 5,
                "narration": "输入0315...系统显示密码错误。还剩两次尝试机会。",
                "choices": [
                    {"key": "1", "text": "尝试031577", "next": "password_success"},
                    {"key": "2", "text": "尝试20770315", "next": "password_fail"}
                ]
            },
            "try_password_2": {
                "id": "try_password_2", "round": 5,
                "narration": "输入031577...密码正确！逃生舱门打开了。系统提示：逃生舱燃料充足，可以返回地球。",
                "choices": [
                    {"key": "1", "text": "立即发射", "next": "launch_pod"}
                ]
            },
            # 第6轮
            "wait_for_docking": {
                "id": "wait_for_docking", "round": 6,
                "narration": "你耐心等待。5分钟后，补给船成功对接！你被安全转移到补给船上。船员告诉你，空间站的修复需要专业人员，你及时获救是正确的选择。",
                "choices": [], "is_end": True, "result": "success"
            },
            "return_to_control": {
                "id": "return_to_control", "round": 6,
                "narration": "你返回控制室，发现补给船已经对接成功。你成功获救了！",
                "choices": [], "is_end": True, "result": "success"
            },
            "password_success": {
                "id": "password_success", "round": 6,
                "narration": "密码正确！逃生舱启动程序开始运行。倒计时10秒后发射。系好安全带！",
                "choices": [
                    {"key": "1", "text": "确认发射", "next": "launch_success"}
                ]
            },
            # 第7轮 - 结局
            "launch_pod": {
                "id": "launch_pod", "round": 7,
                "narration": "逃生舱发射！你感到强烈的推力将你推向座椅。几分钟后，你进入了安全轨道。地球的蓝色弧线出现在窗外。救援队已经在途中。恭喜你成功逃生！",
                "choices": [], "is_end": True, "result": "success"
            },
            "launch_success": {
                "id": "launch_success", "round": 7,
                "narration": "逃生舱成功发射！你穿过了大气层，降落伞打开了。几小时后，你在太平洋上被救援队找到。恭喜你完成了这次惊险的太空逃生！",
                "choices": [], "is_end": True, "result": "success"
            },
            "check_systems": {
                "id": "check_systems", "round": 6,
                "narration": "你检查了其他系统，发现通讯设备还在工作。你联系上了补给船，他们确认会在5分钟后对接。你成功获救了！",
                "choices": [], "is_end": True, "result": "success"
            },
            # 辅助场景
            "control_room_with_o2": {
                "id": "control_room_with_o2", "round": 3,
                "narration": "额外的氧气让你有更多时间。在控制室，你发现了一条之前忽略的信息：备用逃生舱在D区，状态良好。",
                "choices": [
                    {"key": "1", "text": "去D区逃生舱", "next": "escape_pod_d"},
                    {"key": "2", "text": "尝试关闭气闸", "next": "close_airlock"}
                ]
            },
            "read_manual": {
                "id": "read_manual", "round": 3,
                "narration": "操作手册上有紧急流程：1.关闭C区气闸；2.使用D区逃生舱；3.密码在船长室档案中。",
                "choices": [
                    {"key": "1", "text": "去控制室关闭气闸", "next": "control_room"},
                    {"key": "2", "text": "去D区逃生舱", "next": "escape_pod_d"}
                ]
            },
            "find_clue": {
                "id": "find_clue", "round": 3,
                "narration": "你在附近柜子里找到了一本日志。最后一页写着：'为了安全，逃生舱密码统一设为发射年份：2077'",
                "choices": [
                    {"key": "1", "text": "输入2077", "next": "password_2077"},
                    {"key": "2", "text": "查找更多信息", "next": "search_more"}
                ]
            },
            "password_2077": {
                "id": "password_2077", "round": 4,
                "narration": "输入2077...密码正确！逃生舱门打开了。但系统显示逃生舱燃料只够飞到最近的补给站，需要等待对接。",
                "choices": [
                    {"key": "1", "text": "等待补给船对接", "next": "wait_for_docking"},
                    {"key": "2", "text": "立即发射", "next": "launch_pod"}
                ]
            },
            "tape_fix": {
                "id": "tape_fix", "round": 5,
                "narration": "胶带临时封住了泄漏。虽然不是长久之计，但氧气水平暂时稳定了。你有更多时间寻找逃生方案。",
                "choices": [
                    {"key": "1", "text": "返回控制室", "next": "return_to_control"},
                    {"key": "2", "text": "等待补给船", "next": "wait_for_docking"}
                ]
            },
            "try_common_id": {
                "id": "try_common_id", "round": 4,
                "narration": "你尝试了几个常见编号，但都不对。时间在流逝，你需要做出选择。",
                "choices": [
                    {"key": "1", "text": "继续查找编号", "next": "find_station_id"},
                    {"key": "2", "text": "改为手动修复", "next": "repair_c"}
                ]
            },
            "hand_tighten": {
                "id": "hand_tighten", "round": 4,
                "narration": "你试图用手拧紧，但阀门太烫了。你需要工具。",
                "choices": [
                    {"key": "1", "text": "从工具箱找工具", "next": "get_tools"},
                    {"key": "2", "text": "返回寻找其他方案", "next": "control_room"}
                ]
            },
            "hack_system": {
                "id": "hack_system", "round": 3,
                "narration": "你尝试破解系统，但触发了安全警报。系统被临时锁定，需要重启才能使用。",
                "choices": [
                    {"key": "1", "text": "等待系统重启", "next": "wait_restart"},
                    {"key": "2", "text": "去其他逃生舱", "next": "escape_pod_d"}
                ]
            },
            "wait_restart": {
                "id": "wait_restart", "round": 4,
                "narration": "系统重启完成。你再次尝试，这次系统显示了提示：密码与太空站发射年份有关。",
                "choices": [
                    {"key": "1", "text": "输入2077", "next": "password_2077"}
                ]
            },
            "try_password": {
                "id": "try_password", "round": 3,
                "narration": "你尝试了1234、0000、1111...都不对。最后你想到太空站的建造年份是2077，尝试输入后果然成功了！",
                "choices": [
                    {"key": "1", "text": "发射逃生舱", "next": "launch_pod"}
                ]
            },
            "hack_pod_d": {
                "id": "hack_pod_d", "round": 4,
                "narration": "你尝试破解D区逃生舱。系统比预期更复杂，但你发现了一个后门程序，成功启动了逃生舱！",
                "choices": [
                    {"key": "1", "text": "立即发射", "next": "launch_pod"}
                ]
            },
            "password_fail": {
                "id": "password_fail", "round": 6,
                "narration": "密码错误三次，系统被锁定。你只能选择其他方案——等待补给船救援。",
                "choices": [
                    {"key": "1", "text": "等待补给船", "next": "wait_for_docking"}
                ]
            },
            "wait_rescue_ship": {
                "id": "wait_rescue_ship", "round": 3,
                "narration": "你耐心等待。10分钟后，补给船成功对接！你安全获救了！",
                "choices": [], "is_end": True, "result": "success"
            },
            "search_more": {
                "id": "search_more", "round": 4,
                "narration": "你继续搜索，发现了更多线索：密码可能是太空站的发射年份。",
                "choices": [
                    {"key": "1", "text": "输入2077", "next": "password_2077"}
                ]
            },
            "find_other_leaks": {
                "id": "find_other_leaks", "round": 4,
                "narration": "你检查了周围，发现只有一个主要泄漏点。修复这个应该就够了。",
                "choices": [
                    {"key": "1", "text": "从工具箱找工具", "next": "get_tools"},
                    {"key": "2", "text": "返回控制室", "next": "control_room"}
                ]
            },
            "verify_id": {
                "id": "verify_id", "round": 5,
                "narration": "你再次确认：编号确实是SS-2077。现在尝试使用它作为授权密码。",
                "choices": [
                    {"key": "1", "text": "确认输入", "next": "authorize_success"}
                ]
            }
        }

    def _create_detective_scenes(self) -> Dict[str, Dict]:
        """创建侦探场景 - 10轮深度"""
        return {
            # 第1轮
            "start": {
                "id": "start", "round": 1,
                "narration": "午夜时分，你按照神秘信件的邀请来到这座古堡。大门敞开着，里面一片漆黑。你的手电筒照亮了一条通往大厅的走廊。信中提到的证人应该已经去世三年了，这究竟是怎么回事？",
                "choices": [
                    {"key": "1", "text": "直接进入大厅", "next": "main_hall"},
                    {"key": "2", "text": "先观察周围环境", "next": "observe"},
                    {"key": "3", "text": "大声询问是否有人", "next": "call_out"},
                    {"key": "4", "text": "检查信件内容", "next": "check_letter"}
                ]
            },
            # 第2轮
            "main_hall": {
                "id": "main_hall", "round": 2,
                "narration": "大厅中央有一张长桌，桌上摆放着七份餐具，其中一份明显比其他更新。墙上挂着一幅奇怪的画像，画中人的眼睛似乎在跟着你移动。楼梯通向二楼。",
                "choices": [
                    {"key": "1", "text": "检查桌上的物品", "next": "check_table"},
                    {"key": "2", "text": "仔细观察画像", "next": "examine_painting"},
                    {"key": "3", "text": "上楼查看", "next": "upstairs"},
                    {"key": "4", "text": "寻找其他房间", "next": "explore_rooms"}
                ]
            },
            "observe": {
                "id": "observe", "round": 2,
                "narration": "你仔细观察周围。古堡似乎有人维护，地面很干净。门口的尘土上有两组脚印：一组进来的，另一组...似乎是三天前的。信件上的邮戳显示它是在一周前寄出的。",
                "choices": [
                    {"key": "1", "text": "跟踪新脚印进入大厅", "next": "main_hall"},
                    {"key": "2", "text": "检查旧脚印的方向", "next": "follow_old_tracks"},
                    {"key": "3", "text": "在门口设置陷阱", "next": "set_trap"},
                    {"key": "4", "text": "返回检查信件", "next": "check_letter"}
                ]
            },
            "check_letter": {
                "id": "check_letter", "round": 2,
                "narration": "信件上写着：'亲爱的侦探，我知道真相。午夜古堡，不见不散。'署名是'林晓薇'——三年前那起案件的关键证人。她应该在保护证人程序中，或者...已经死了？",
                "choices": [
                    {"key": "1", "text": "这可能是个陷阱，离开", "next": "leave"},
                    {"key": "2", "text": "继续探索，寻找真相", "next": "main_hall"},
                    {"key": "3", "text": "拍照记录证据", "next": "take_photo"},
                    {"key": "4", "text": "拨打以前的案件档案电话", "next": "call_archive"}
                ]
            },
            "call_out": {
                "id": "call_out", "round": 2,
                "narration": "你的声音在空荡的大厅里回响。几秒钟后，你听到二楼传来轻微的脚步声，然后是一片寂静。有人——或有什么东西——在这里。",
                "choices": [
                    {"key": "1", "text": "立刻上楼", "next": "upstairs"},
                    {"key": "2", "text": "保持安静，暗中观察", "next": "wait_and_watch"},
                    {"key": "3", "text": "进入大厅寻找掩护", "next": "main_hall"},
                    {"key": "4", "text": "离开古堡", "next": "leave"}
                ]
            },
            # 第3轮
            "check_table": {
                "id": "check_table", "round": 3,
                "narration": "桌上有一份餐具明显是新放置的，下面压着一张纸条：'欢迎你，侦探。真相在画像背后。'纸条的笔迹与信件相同。",
                "choices": [
                    {"key": "1", "text": "立刻检查画像", "next": "examine_painting"},
                    {"key": "2", "text": "检查其他餐具", "next": "check_other_items"},
                    {"key": "3", "text": "保留纸条作为证据", "next": "keep_note"},
                    {"key": "4", "text": "这是陷阱，小心行事", "next": "be_cautious"}
                ]
            },
            "examine_painting": {
                "id": "examine_painting", "round": 3,
                "narration": "你走近画像。画中是一位年轻女子，正是三年前的证人林晓薇。你注意到画框右侧有一个几乎看不见的开关。按下后，画像向左移动，露出一个保险箱。",
                "choices": [
                    {"key": "1", "text": "尝试打开保险箱", "next": "open_safe"},
                    {"key": "2", "text": "先记录这个发现", "next": "record_discovery"},
                    {"key": "3", "text": "检查是否有陷阱", "next": "check_trap"},
                    {"key": "4", "text": "寻找密码线索", "next": "find_code"}
                ]
            },
            "upstairs": {
                "id": "upstairs", "round": 3,
                "narration": "你走上楼梯。二楼走廊两侧有几扇门，其中一扇门缝下透出微弱的光。你听到里面传来翻动纸张的声音。",
                "choices": [
                    {"key": "1", "text": "直接推门进入", "next": "enter_room"},
                    {"key": "2", "text": "先敲敲门", "next": "knock_door"},
                    {"key": "3", "text": "从门缝偷看", "next": "peek_through"},
                    {"key": "4", "text": "检查其他房间", "next": "check_other_rooms"}
                ]
            },
            # 第4轮
            "open_safe": {
                "id": "open_safe", "round": 4,
                "narration": "保险箱需要四位密码。你想起三年前的案件档案编号是7315，尝试输入后，保险箱打开了！里面有一份文件、一张照片和一把钥匙。",
                "choices": [
                    {"key": "1", "text": "阅读文件", "next": "read_document"},
                    {"key": "2", "text": "检查照片", "next": "check_photo"},
                    {"key": "3", "text": "拿走钥匙", "next": "take_key"},
                    {"key": "4", "text": "全部拿走", "next": "take_all"}
                ]
            },
            "enter_room": {
                "id": "enter_room", "round": 4,
                "narration": "你推门而入。房间里有一个人影，背对着你站在窗边。当你进入时，人影缓缓转过身——是林晓薇，三年前的证人！她看起来苍老了许多，但确实还活着。",
                "choices": [
                    {"key": "1", "text": "质问她为何假死", "next": "confront_her"},
                    {"key": "2", "text": "保持警惕，观察情况", "next": "stay_alert"},
                    {"key": "3", "text": "询问真相是什么", "next": "ask_truth"},
                    {"key": "4", "text": "准备逮捕她", "next": "prepare_arrest"}
                ]
            },
            "find_code": {
                "id": "find_code", "round": 4,
                "narration": "你在画像底座发现刻着一行小字：'真相永不灭'。这可能是密码提示。案件档案编号是7315，尝试输入后保险箱打开了。",
                "choices": [
                    {"key": "1", "text": "检查保险箱内容", "next": "open_safe"}
                ]
            },
            # 第5轮
            "read_document": {
                "id": "read_document", "round": 5,
                "narration": "文件揭示了真相：三年前那起案件的真正凶手是一个有权势的人，林晓薇被迫假死以保护自己。这份文件是所有证据的汇总，足以让真凶伏法。但文件最后警告：真凶的人正在接近古堡。",
                "choices": [
                    {"key": "1", "text": "立即离开古堡", "next": "quick_escape"},
                    {"key": "2", "text": "寻找其他出口", "next": "find_exit"},
                    {"key": "3", "text": "设置防御措施", "next": "set_defense"},
                    {"key": "4", "text": "联系警方", "next": "call_police"}
                ]
            },
            "confront_her": {
                "id": "confront_her", "round": 5,
                "narration": "林晓薇叹了口气：'我没有选择。那个人有权有势，我只有假死才能保护自己和家人。我邀请你来，是因为只有你能帮我揭露真相。'她递给你一份文件。",
                "choices": [
                    {"key": "1", "text": "阅读文件", "next": "read_document"},
                    {"key": "2", "text": "询问具体计划", "next": "ask_plan"},
                    {"key": "3", "text": "表示怀疑", "next": "express_doubt"}
                ]
            },
            "check_photo": {
                "id": "check_photo", "round": 5,
                "narration": "照片上是三年前案件的真正凶手——一个你认识的人，市检察长的儿子。照片背面写着：'他已经知道你在这里了。'",
                "choices": [
                    {"key": "1", "text": "立即阅读文件", "next": "read_document"},
                    {"key": "2", "text": "寻找林晓薇", "next": "upstairs"}
                ]
            },
            # 第6轮
            "ask_plan": {
                "id": "ask_plan", "round": 6,
                "narration": "林晓薇说：'我有全部证据，包括录音和文件。只要你把这些交给可靠的人，真相就能大白。但他已经派人来了，我们需要在十分钟内离开。'",
                "choices": [
                    {"key": "1", "text": "跟她一起离开", "next": "escape_together"},
                    {"key": "2", "text": "分开行动更安全", "next": "separate_escape"},
                    {"key": "3", "text": "先拿到所有证据", "next": "get_all_evidence"}
                ]
            },
            "quick_escape": {
                "id": "quick_escape", "round": 6,
                "narration": "你冲向大门，但发现外面有几辆车正在接近。前门已经不安全了，你需要寻找其他出口。",
                "choices": [
                    {"key": "1", "text": "寻找后门", "next": "find_back_door"},
                    {"key": "2", "text": "从二楼窗户逃生", "next": "window_escape"},
                    {"key": "3", "text": "躲藏在古堡内", "next": "hide_inside"}
                ]
            },
            "call_police": {
                "id": "call_police", "round": 6,
                "narration": "你拨打了老搭档的电话，告诉他你的位置和情况。他说二十分钟内能赶到，但你发现窗外已经有人在靠近古堡。",
                "choices": [
                    {"key": "1", "text": "在警方到达前躲好", "next": "hide_evidence"},
                    {"key": "2", "text": "尝试突围", "next": "breakout"},
                    {"key": "3", "text": "设置拖延陷阱", "next": "delay_tactics"}
                ]
            },
            # 第7轮
            "escape_together": {
                "id": "escape_together", "round": 7,
                "narration": "你跟着林晓薇穿过一条秘密通道，来到古堡后面的树林。她说：'我的车在五百米外，我们可以直接去警察局。'但就在这时，你听到身后有脚步声。",
                "choices": [
                    {"key": "1", "text": "加快速度奔跑", "next": "run_faster"},
                    {"key": "2", "text": "设置绊脚陷阱", "next": "set_trip_trap"},
                    {"key": "3", "text": "分散逃跑", "next": "split_up"}
                ]
            },
            "find_back_door": {
                "id": "find_back_door", "round": 7,
                "narration": "你在厨房后面找到了一扇小门。门外是一片树林，黑暗中传来汽车引擎的声音。你有两个选择：冒险穿过树林，或者等待支援。",
                "choices": [
                    {"key": "1", "text": "快速穿过树林", "next": "through_woods"},
                    {"key": "2", "text": "躲藏等待时机", "next": "wait_for_chance"},
                    {"key": "3", "text": "设置假线索", "next": "fake_trail"}
                ]
            },
            "hide_evidence": {
                "id": "hide_evidence", "round": 7,
                "narration": "你找到一个隐蔽的地方，把证据藏好，并用手机拍下了位置。即使被抓，证据也能在之后被发现。",
                "choices": [
                    {"key": "1", "text": "主动出去面对", "next": "face_them"},
                    {"key": "2", "text": "继续躲藏", "next": "keep_hiding"},
                    {"key": "3", "text": "寻找武器自卫", "next": "find_weapon"}
                ]
            },
            # 第8轮
            "run_faster": {
                "id": "run_faster", "round": 8,
                "narration": "你和林晓薇拼命奔跑，身后的脚步声越来越近。突然，前方出现了车灯——是林晓薇的车！你们冲进车里，林晓薇发动引擎，车子冲出树林。",
                "choices": [
                    {"key": "1", "text": "直接去警察局", "next": "to_police"},
                    {"key": "2", "text": "先去安全屋", "next": "safe_house"}
                ]
            },
            "through_woods": {
                "id": "through_woods", "round": 8,
                "narration": "你在黑暗中穿梭于树林间，身后偶尔传来搜索的声音。二十分钟后，你看到了公路，一辆路过的卡车愿意载你一程。你成功脱险了！",
                "choices": [
                    {"key": "1", "text": "让卡车司机载你去警察局", "next": "to_police"}
                ]
            },
            "face_them": {
                "id": "face_them", "round": 8,
                "narration": "你主动走出来，面对那几个人。你冷静地说：'证据已经发给了警方，你们来晚了。'他们面面相觑，最终在警笛声中仓皇逃走。",
                "choices": [
                    {"key": "1", "text": "向赶到的警方说明情况", "next": "explain_to_police"}
                ]
            },
            # 第9轮
            "to_police": {
                "id": "to_police", "round": 9,
                "narration": "你到达警察局，向值班警官展示了所有证据。他立刻联系了检察长，整个案件被重新审理。真正的凶手——检察长的儿子——在证据面前无法狡辩，最终被逮捕。",
                "choices": [
                    {"key": "1", "text": "配合调查，完成笔录", "next": "final_statement"}
                ]
            },
            "explain_to_police": {
                "id": "explain_to_police", "round": 9,
                "narration": "你向警方详细说明了整个情况。证据被立即封存，案件重新启动调查。三天后，真正的凶手被绳之以法，林晓薇的冤屈得以洗清。",
                "choices": [
                    {"key": "1", "text": "等待案件结束", "next": "final_statement"}
                ]
            },
            "safe_house": {
                "id": "safe_house", "round": 9,
                "narration": "你们到达安全屋，联系了可靠的朋友。在确保安全后，你将证据交给了值得信任的检察官。真正的凶手最终落网，正义得以伸张。",
                "choices": [
                    {"key": "1", "text": "完成最后的任务", "next": "final_statement"}
                ]
            },
            # 第10轮 - 结局
            "final_statement": {
                "id": "final_statement", "round": 10,
                "narration": "案件尘埃落定。林晓薇得以恢复真实身份，与家人团聚。你收到了她的一封信：'谢谢你还我真相。世界因为有你这样的侦探，才不会陷入黑暗。'恭喜你完成了这次惊心动魄的调查！",
                "choices": [], "is_end": True, "result": "success"
            },
            # 辅助场景
            "check_other_items": {
                "id": "check_other_items", "round": 4,
                "narration": "其他餐具下没有发现线索。但餐桌中央的花瓶下压着一张卡片，上面写着：'画像背后有答案。'",
                "choices": [
                    {"key": "1", "text": "检查画像", "next": "examine_painting"}
                ]
            },
            "keep_note": {
                "id": "keep_note", "round": 4,
                "narration": "你小心地收起纸条。这可能是重要的证据。然后你走向画像，准备查看背后的秘密。",
                "choices": [
                    {"key": "1", "text": "检查画像", "next": "examine_painting"}
                ]
            },
            "be_cautious": {
                "id": "be_cautious", "round": 4,
                "narration": "你决定更加小心。先观察一下周围的环境，确保没有陷阱后再行动。你的谨慎是对的——画像附近有一个不易察觉的触发装置。",
                "choices": [
                    {"key": "1", "text": "解除陷阱", "next": "disarm_trap"},
                    {"key": "2", "text": "绕过陷阱", "next": "examine_painting"}
                ]
            },
            "disarm_trap": {
                "id": "disarm_trap", "round": 5,
                "narration": "你小心地解除了陷阱。这是一个报警装置，如果触发就会提醒设下陷阱的人。现在你可以安全地检查画像了。",
                "choices": [
                    {"key": "1", "text": "检查画像", "next": "examine_painting"}
                ]
            },
            "record_discovery": {
                "id": "record_discovery", "round": 4,
                "narration": "你用手机拍下了保险箱和开关的位置。这些记录可能在之后派上用场。",
                "choices": [
                    {"key": "1", "text": "尝试打开保险箱", "next": "open_safe"}
                ]
            },
            "check_trap": {
                "id": "check_trap", "round": 4,
                "narration": "你仔细检查，发现保险箱上方有一个小型摄像头。看来有人想记录谁打开了保险箱。你用胶带挡住了摄像头。",
                "choices": [
                    {"key": "1", "text": "打开保险箱", "next": "open_safe"}
                ]
            },
            "take_key": {
                "id": "take_key", "round": 5,
                "narration": "钥匙上刻着一个地址。你想起那是市郊的一处废弃仓库，可能与案件有关。你决定在离开古堡后去看看。",
                "choices": [
                    {"key": "1", "text": "阅读文件", "next": "read_document"},
                    {"key": "2", "text": "检查照片", "next": "check_photo"}
                ]
            },
            "take_all": {
                "id": "take_all", "round": 5,
                "narration": "你把所有证据都装进口袋。这些证据足以扭转整个案件。现在你需要安全离开古堡。",
                "choices": [
                    {"key": "1", "text": "快速离开", "next": "quick_escape"},
                    {"key": "2", "text": "寻找林晓薇", "next": "upstairs"}
                ]
            },
            "leave": {
                "id": "leave", "round": 3,
                "narration": "你转身离开，但在门口发现有人已经把你的车轮胎刺破了。看来你确实被盯上了。你必须留在古堡找出真相。",
                "choices": [
                    {"key": "1", "text": "返回大厅", "next": "main_hall"}
                ]
            },
            "take_photo": {
                "id": "take_photo", "round": 3,
                "narration": "你拍下了信件、邮戳和古堡的照片。这些可能是有用的证据。然后你进入大厅继续调查。",
                "choices": [
                    {"key": "1", "text": "进入大厅", "next": "main_hall"}
                ]
            },
            "call_archive": {
                "id": "call_archive", "round": 3,
                "narration": "档案室的朋友告诉你，林晓薇的死亡证明存在疑点——没有尸体，只有一纸证明。这证实了她可能还活着的猜测。",
                "choices": [
                    {"key": "1", "text": "进入大厅调查", "next": "main_hall"}
                ]
            },
            "explore_rooms": {
                "id": "explore_rooms", "round": 3,
                "narration": "你发现了一间书房。书桌上有一些法律文件和一本日记。日记记录了林晓薇这三年的隐藏生活。",
                "choices": [
                    {"key": "1", "text": "阅读日记", "next": "read_diary"},
                    {"key": "2", "text": "检查文件", "next": "check_files"},
                    {"key": "3", "text": "返回大厅", "next": "main_hall"}
                ]
            },
            "read_diary": {
                "id": "read_diary", "round": 4,
                "narration": "日记详细记录了三年前案件的真相：检察长的儿子才是真正的凶手，林晓薇被迫假死以躲避他的追杀。",
                "choices": [
                    {"key": "1", "text": "拿走日记作为证据", "next": "take_diary"},
                    {"key": "2", "text": "检查其他文件", "next": "check_files"}
                ]
            },
            "take_diary": {
                "id": "take_diary", "round": 5,
                "narration": "你将日记收入口袋。这将是重要的证据。现在你有了足够的线索，是时候找到林晓薇了。",
                "choices": [
                    {"key": "1", "text": "上楼找人", "next": "upstairs"}
                ]
            },
            "check_files": {
                "id": "check_files", "round": 5,
                "narration": "法律文件揭示了检察长的儿子曾多次使用权力掩盖自己的罪行。这是一份完整的犯罪记录！",
                "choices": [
                    {"key": "1", "text": "拿走文件", "next": "take_diary"},
                    {"key": "2", "text": "上楼找人", "next": "upstairs"}
                ]
            },
            "follow_old_tracks": {
                "id": "follow_old_tracks", "round": 3,
                "narration": "旧脚印通向古堡后面的一间小屋。屋内有生活用品，看起来有人最近住过这里。",
                "choices": [
                    {"key": "1", "text": "搜索小屋", "next": "search_cabin"},
                    {"key": "2", "text": "返回正门", "next": "main_hall"}
                ]
            },
            "search_cabin": {
                "id": "search_cabin", "round": 4,
                "narration": "小屋里有一张地图，标注了古堡的秘密通道。还有一张纸条：'我在二楼等你。'",
                "choices": [
                    {"key": "1", "text": "从秘密通道进入", "next": "secret_entrance"},
                    {"key": "2", "text": "走正门", "next": "main_hall"}
                ]
            },
            "secret_entrance": {
                "id": "secret_entrance", "round": 5,
                "narration": "秘密通道直通二楼。你在出口处看到了微弱的灯光，那是林晓薇等待的房间。",
                "choices": [
                    {"key": "1", "text": "进入房间", "next": "enter_room"}
                ]
            },
            "set_trap": {
                "id": "set_trap", "round": 3,
                "narration": "你在门口设置了一个简单的报警装置，一旦有人进入就会发出响声。这样你可以专心在古堡内调查。",
                "choices": [
                    {"key": "1", "text": "进入大厅", "next": "main_hall"}
                ]
            },
            "knock_door": {
                "id": "knock_door", "round": 4,
                "narration": "你敲了敲门。里面的声音停了，然后传来一个女人的声音：'是你吗，侦探？请进来。'",
                "choices": [
                    {"key": "1", "text": "推门进入", "next": "enter_room"}
                ]
            },
            "peek_through": {
                "id": "peek_through", "round": 4,
                "narration": "你从门缝偷看。房间里有一个女人在整理文件，她看起来很紧张，不时看向窗外。",
                "choices": [
                    {"key": "1", "text": "推门进入", "next": "enter_room"},
                    {"key": "2", "text": "先敲敲门", "next": "knock_door"}
                ]
            },
            "check_other_rooms": {
                "id": "check_other_rooms", "round": 4,
                "narration": "你检查了其他房间，发现了一间书房。书桌上有一本日记，记录了林晓薇这三年的经历。",
                "choices": [
                    {"key": "1", "text": "阅读日记", "next": "read_diary"}
                ]
            },
            "wait_and_watch": {
                "id": "wait_and_watch", "round": 3,
                "narration": "你静静地等待。几分钟后，你看到一个女人的影子出现在楼梯口，似乎在观察你。",
                "choices": [
                    {"key": "1", "text": "主动打招呼", "next": "greet_her"},
                    {"key": "2", "text": "假装没看见", "next": "pretend"}
                ]
            },
            "greet_her": {
                "id": "greet_her", "round": 4,
                "narration": "你抬头说：'林小姐，我们可以谈谈吗？'她犹豫了一下，然后慢慢走下楼梯。",
                "choices": [
                    {"key": "1", "text": "开始对话", "next": "confront_her"}
                ]
            },
            "pretend": {
                "id": "pretend", "round": 4,
                "narration": "你假装在检查大厅，实际上在观察她。她最终鼓起勇气下来，说：'你终于来了，侦探。'",
                "choices": [
                    {"key": "1", "text": "开始对话", "next": "confront_her"}
                ]
            },
            "stay_alert": {
                "id": "stay_alert", "round": 5,
                "narration": "你保持警惕，但林晓薇的痛苦表情看起来很真实。她说：'我知道你有很多问题，但时间不多了。他们已经在路上了。'",
                "choices": [
                    {"key": "1", "text": "让她解释", "next": "ask_plan"}
                ]
            },
            "ask_truth": {
                "id": "ask_truth", "round": 5,
                "narration": "林晓薇说：'真正的凶手是检察长的儿子。我有所有证据，但需要一个值得信任的人帮我公开它们。那个人就是你。'",
                "choices": [
                    {"key": "1", "text": "看看证据", "next": "read_document"}
                ]
            },
            "prepare_arrest": {
                "id": "prepare_arrest", "round": 5,
                "narration": "你正准备行动，但林晓薇说：'等等！我没有犯罪，我只是想活下去。听我解释，真相在文件里。'",
                "choices": [
                    {"key": "1", "text": "听她解释", "next": "ask_plan"}
                ]
            },
            "express_doubt": {
                "id": "express_doubt", "round": 6,
                "narration": "林晓薇理解你的怀疑。她拿出了一份DNA检测报告：'这是我活着的证明。还有这些文件——它们证明了真正的凶手是谁。'",
                "choices": [
                    {"key": "1", "text": "检查文件", "next": "read_document"}
                ]
            },
            "set_defense": {
                "id": "set_defense", "round": 6,
                "narration": "你利用古堡的结构设置了几个陷阱和障碍。这些可以为你们争取时间。",
                "choices": [
                    {"key": "1", "text": "联系警方", "next": "call_police"},
                    {"key": "2", "text": "寻找出口", "next": "find_exit"}
                ]
            },
            "find_exit": {
                "id": "find_exit", "round": 7,
                "narration": "你在古堡后面发现了一个地窖入口，通向树林。这是一条安全的逃生路线。",
                "choices": [
                    {"key": "1", "text": "准备撤离", "next": "escape_together"}
                ]
            },
            "get_all_evidence": {
                "id": "get_all_evidence", "round": 7,
                "narration": "你确保拿到所有证据的副本，用手机拍照备份。这样即使原件丢失，真相也能被揭露。",
                "choices": [
                    {"key": "1", "text": "开始撤离", "next": "escape_together"}
                ]
            },
            "separate_escape": {
                "id": "separate_escape", "round": 7,
                "narration": "你们决定分开走。林晓薇从后门离开，你从前门引开追兵。十分钟后，你们在镇上的警察局汇合。",
                "choices": [
                    {"key": "1", "text": "执行计划", "next": "execute_plan"}
                ]
            },
            "execute_plan": {
                "id": "execute_plan", "round": 8,
                "narration": "计划成功了！追兵被你引开后，林晓薇安全到达了警察局。你们一起将证据交给了警方。",
                "choices": [
                    {"key": "1", "text": "配合调查", "next": "to_police"}
                ]
            },
            "window_escape": {
                "id": "window_escape", "round": 7,
                "narration": "你从二楼的窗户爬出，顺着藤蔓滑到地面。外面的追兵还没发现这边。",
                "choices": [
                    {"key": "1", "text": "快速穿过树林", "next": "through_woods"}
                ]
            },
            "hide_inside": {
                "id": "hide_inside", "round": 7,
                "narration": "你找到了一个隐蔽的密室，里面有足够的食物和水。你可以在这里等待警方支援。",
                "choices": [
                    {"key": "1", "text": "等待警方", "next": "call_police"}
                ]
            },
            "delay_tactics": {
                "id": "delay_tactics", "round": 7,
                "narration": "你设置了几个假线索，让追兵分头搜索。这为你争取了宝贵的时间。",
                "choices": [
                    {"key": "1", "text": "趁机撤离", "next": "find_back_door"}
                ]
            },
            "set_trip_trap": {
                "id": "set_trip_trap", "round": 8,
                "narration": "你用树枝设置了一个绊脚陷阱。身后的脚步声越来越近，然后是一声摔倒的闷响。陷阱奏效了！",
                "choices": [
                    {"key": "1", "text": "趁机逃跑", "next": "run_faster"}
                ]
            },
            "split_up": {
                "id": "split_up", "round": 8,
                "narration": "你和林晓薇分头逃跑。追兵不知道该追谁，只能分散力量。最终你们在安全屋汇合。",
                "choices": [
                    {"key": "1", "text": "前往安全屋", "next": "safe_house"}
                ]
            },
            "wait_for_chance": {
                "id": "wait_for_chance", "round": 8,
                "narration": "你躲在树丛中等待。追兵搜索了十分钟，然后离开了。你抓住机会逃出了包围圈。",
                "choices": [
                    {"key": "1", "text": "前往安全地点", "next": "through_woods"}
                ]
            },
            "fake_trail": {
                "id": "fake_trail", "round": 8,
                "narration": "你制造了一些假脚印通向错误的方向。追兵跟着假线索追了很远，为你争取了时间。",
                "choices": [
                    {"key": "1", "text": "趁机逃离", "next": "through_woods"}
                ]
            },
            "keep_hiding": {
                "id": "keep_hiding", "round": 8,
                "narration": "你保持隐蔽。二十分钟后，警笛声响起，追兵仓皇逃离。你成功获救了！",
                "choices": [
                    {"key": "1", "text": "向警方说明情况", "next": "explain_to_police"}
                ]
            },
            "find_weapon": {
                "id": "find_weapon", "round": 8,
                "narration": "你在厨房找到了一把水果刀，作为最后的自卫手段。但你希望不需要用到它。",
                "choices": [
                    {"key": "1", "text": "继续躲藏", "next": "keep_hiding"}
                ]
            },
            "breakout": {
                "id": "breakout", "round": 8,
                "narration": "你决定主动出击。利用你对古堡的了解，你成功避开了追兵，从后门逃出。",
                "choices": [
                    {"key": "1", "text": "前往安全地点", "next": "through_woods"}
                ]
            }
        }

    def get_game_list(self) -> List[Dict[str, Any]]:
        """获取所有游戏列表"""
        return [
            {
                "id": game["id"],
                "title": game["title"],
                "description": game["description"],
                "difficulty": game["difficulty"]
            }
            for game in self.games.values()
        ]

    def start_game(self, game_id: str) -> Dict[str, Any]:
        """开始新游戏"""
        if game_id not in self.games:
            return {"error": "Game not found"}

        game = self.games[game_id]
        session_id = str(uuid.uuid4())[:8]

        self.active_sessions[session_id] = {
            "game_id": game_id,
            "current_scene": "start",
            "history": [],
            "inventory": [],
            "start_time": None
        }

        first_scene = game["scenes"]["start"]

        return {
            "session_id": session_id,
            "game_id": game_id,
            "title": game["title"],
            "scene_id": first_scene["id"],
            "round": first_scene.get("round", 1),
            "narration": first_scene["narration"],
            "choices": first_scene["choices"],
            "is_end": first_scene.get("is_end", False),
            "result": first_scene.get("result")
        }

    def make_choice(self, session_id: str, choice_key: str) -> Dict[str, Any]:
        """做出选择"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]
        game = self.games[session["game_id"]]
        current_scene = game["scenes"][session["current_scene"]]

        # Find the chosen option
        chosen = None
        for choice in current_scene["choices"]:
            if choice["key"] == choice_key:
                chosen = choice
                break

        if not chosen:
            return {"error": "Invalid choice"}

        # Update session
        session["history"].append({
            "from": session["current_scene"],
            "choice": choice_key
        })
        session["current_scene"] = chosen["next"]

        # Get next scene
        next_scene = game["scenes"].get(chosen["next"])

        if not next_scene:
            return {"error": "Scene not found"}

        return {
            "session_id": session_id,
            "game_id": session["game_id"],
            "title": game["title"],
            "scene_id": next_scene["id"],
            "round": next_scene.get("round", session["history"][-1].get("round", 1) + 1 if session["history"] else 2),
            "narration": next_scene["narration"],
            "choices": next_scene["choices"],
            "is_end": next_scene.get("is_end", False),
            "result": next_scene.get("result"),
            "history": session["history"]
        }

    def get_scene(self, session_id: str) -> Dict[str, Any]:
        """获取当前场景"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]
        game = self.games[session["game_id"]]
        scene = game["scenes"][session["current_scene"]]

        return {
            "session_id": session_id,
            "game_id": session["game_id"],
            "title": game["title"],
            "scene_id": scene["id"],
            "round": scene.get("round", 1),
            "narration": scene["narration"],
            "choices": scene["choices"],
            "is_end": scene.get("is_end", False),
            "result": scene.get("result")
        }

    def end_game(self, session_id: str) -> Dict[str, Any]:
        """结束游戏"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        return {"message": "Game ended"}

game_service = GameService()
