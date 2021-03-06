import json
from mcdreforged.api.all import *
import os

# 插件基本信息
PLUGIN_METADATA = {
    'id': 'lazytp',
    'version': '1.1.0',
    'name': 'Lazy Teleport',
    'description': 'A express gateway between each dimensions.',
    'author': 'Ra1ny_Yuki',
    'link': 'https://github.com/ra1ny-yuki/lazytp/',
    'dependencies': {
        'mcdreforged': '>=1.0.0',
        'minecraft_data_api': '*',
    }
}
# 可修改内容开始 ========================================================

# 修改配置文件的位置，默认的相对路径是相对mcdr运行路径而言的
configFile = 'config/lazytp.json'

# 可修改内容结束，其他内容不动当然是坠吼的，除非你知道你在干嘛 ==============

# 不要改默认配置文件里的内容呀喂！要改去首次加载后生成的文件里改呀喂！
defaultConfig = '''
{
    "overworld_prefix": "!!overworld",
    "nether_prefix": "!!nether",
    "end_prefix": "!!end",
    "we_unstuck": true,
    "overworld_waypoints": {
        "default": "0 64 0",
        "example": "1 145 14"
    },
    "nether_waypoints": {
        "default": "0 64 0",
        "example": "19 198 10"
    },
    "end_waypoints": {
        "default": "100 51 0"
    }
}'''


# 获取插件配置文件
def get_config():  # 加载配置文件
    if not os.path.exists(configFile):  # 若文件不存在则写入默认值
        with open(configFile, 'w+', encoding='UTF-8') as f:
            f.write(defaultConfig)
    with open(configFile, 'r', encoding='UTF-8') as f:
        config = json.load(f, encoding='UTF-8')
    return config

# 打印和rtext执行指令函数从落息那抄的（逃）
def print_message(source: CommandSource, msg: str, tell = True, prefix = '[LazyTP] '):
    msg = prefix + msg
    if source.is_player and not tell:
        source.get_server().say(msg)
    else:
        source.reply(msg)

def command_run(message: str, text: str, command: str):
	return RText(message).set_hover_text(text).set_click_event(RAction.run_command, command)

def command_suggest(message: str, text: str, command: str):
	return RText(message).set_hover_text(text).set_click_event(RAction.suggest_command, command)

# 显示帮助信息，如果需要改命令前缀不用动这里只要改config文件就行了
def show_help(source: CommandSource):
    config = get_config()
    source.reply("""
------- MCDR {0} v{1} -------
快速地穿梭于各维度之间。
§d【对维度传送】§r
""".strip().format(PLUGIN_METADATA['name'], PLUGIN_METADATA['version']) + """
""" +
      command_suggest('§7' + config['overworld_prefix'] + '§r', '点击补全指令', config['overworld_prefix'] + ' ') + """ 传送到主世界对应坐标;
""" + command_suggest('§7' + config['nether_prefix'] + '§r', '点击补全指令', config['nether_prefix'] + ' ') + """ 传送到下界对应坐标;
""" + command_suggest('§7' + config['end_prefix'] + '§r', '点击补全指令', config['end_prefix'] + ' ') + """ 传送到末路之地默认导航点。
上述三条指令可用作本插件其他功能的指令前缀,
以下用§7<Prefix>§r替代上述三指令前缀。
§d【定点传送】§r
该条目下的功能无法点击建议指令, 可通过点击上方维度指令前缀补全,
不同维度的路径点名称可能重复, 故传送时§c须匹配其维度指令前缀§r。
§7<Prefix> §e<name>§r 传送到该维度的路径点§e<name>§r。
§7<Prefix> §e<x>§r §e<y>§r §e<z>§r 传送到对应维度的§e<x>§r,§e<y>§r,§e<z>§r处;
查询路径点名称请查阅下述§7list§r, §7listall§r参数功能。
§d【其他功能】§r
执行下述指令可用任意上述指令前缀替换§7<Prefix>§r, 效果相同。
""" + command_suggest('§7<Prefix> help§r', '点击补全指令', config['overworld_prefix'] + ' help') + """ 显示该帮助信息;
""" + command_suggest('§7<Prefix> list§r', '点击补全指令', config['overworld_prefix'] + ' list') + """ 显示管理员设定在该维度的所有路径点;
""" + command_suggest('§7<Prefix> listall§r', '点击补全指令', config['overworld_prefix'] + ' listall') + """ 显示服务器管理员设定的所有路径点。
        """
    )

# 执行tp
def tp(server: ServerInterface, source: CommandSource, coordinate: str, target_dim_id: int):
    target_dim = dim_id_to_dim(target_dim_id)
    server.execute('execute in ' + target_dim + ' run tp ' + source.player + ' ' + coordinate)
    unstuck = get_config()['we_unstuck']
    msg_done = '§a传送完成!§r'
    if unstuck:
        msg_done = msg_done + ' 若被困住, ' + command_run('§c点此§r', '点我传送到上方非实心位置', '/unstuck') + '脱困'
    print_message(source, msg_done)

def dim_id_to_dim(dim_id: int):
    if dim_id == 1:
        dim = 'minecraft:the_end'
    elif dim_id == 0:
        dim = 'minecraft:overworld'
    else:
        dim = 'minecraft:the_nether'
    return dim


# Minecraft Data API获取玩家维度
def fetch_dim(source: CommandSource):
    api = source.get_server().get_plugin_instance('minecraft_data_api')
    current_dim_id = api.get_player_dimension(source.player)
    return current_dim_id

# Minecraft Data API获取玩家坐标
def fetch_coordinate(source: CommandSource):
    api = source.get_server().get_plugin_instance('minecraft_data_api')
    current_coordinate = api.get_player_coordinate(source.player)
    return current_coordinate

# 维度ID转维度路径点列表
def wplist_convert(target_dim_id: int):
    config = get_config()
    if target_dim_id == 1:
        wplist = config['end_waypoints']
    elif target_dim_id == 0:
        wplist = config['overworld_waypoints']
    else:
        wplist = config['nether_waypoints']
    return wplist

# 计算坐标
def calculate_coordinate(original_coordinate, mutiply):
    if mutiply:
        x, y, z = original_coordinate.x * 8, original_coordinate.y, original_coordinate.z * 8
    else:
        x, y, z = original_coordinate.x / 8, original_coordinate.y, original_coordinate.z / 8
    target_coordinate = coordinate_to_str(x, y, z)
    return target_coordinate

# 通用浮点类包装
def general_to_float(general_object):
    return float(general_object)

# 坐标的字符类包装
def coordinate_to_str(x, y, z):
    output_string = '{0} {1} {2}'.format(str(x), str(y), str(z))
    return output_string

# 无参数指令统一判定
@new_thread(PLUGIN_METADATA['id'])
def tp_convert(server: ServerInterface, source: CommandSource, target_dim_id: int):
    current_dim_id = fetch_dim(source)
    if current_dim_id == target_dim_id:
            print_message(source, '§c你已经处于这个维度了!!§r')
            print_message(source, 
            command_run('>>>§6点击此处传送到该维度默认导航点§r<<<', wplist_convert(target_dim_id)['default'], dim_id_to_prefix(target_dim_id) + ' default'), 
            True, ' ')
    else:
        if target_dim_id == 1:
            tp(server, source, wplist_convert(target_dim_id = 1)['default'], target_dim_id)
        else:
            if current_dim_id == 1:
                tp(server, source, wplist_convert(target_dim_id)['default'], target_dim_id)
            else:
                original_coordinate = fetch_coordinate(source)
                if target_dim_id == 0:
                    target_coordinate = calculate_coordinate(original_coordinate, True)
                else:
                    target_coordinate = calculate_coordinate(original_coordinate, False)
                tp(server, source, target_coordinate, target_dim_id)

# 维度id转维度名称
def dim_id_to_dim_name(dim_id: int):
    if dim_id == 0:
        return '主世界'
    elif dim_id == 1:
        return '末地'
    else:
        return '下界'

# 维度id转前缀
def dim_id_to_prefix(dim_id: int):
    config = get_config()
    if dim_id == 0:
        return config['overworld_prefix']
    elif dim_id == 1:
        return config['end_prefix']
    else:
        return config['nether_prefix']

# 列出维度路径点
def list_wp(source: CommandSource, requested_dim_id: int):
    print_message(source, f'服务器管理员在§b{dim_id_to_dim_name(requested_dim_id)}§r设置了如下路径点：')
    print_wp(source, requested_dim_id)

# 执行显示路径点
def print_wp(source: CommandSource, requested_dim_id: int):
    wplist = wplist_convert(requested_dim_id)
    dim_prefix = dim_id_to_prefix(requested_dim_id)
    for i in wplist:
        print_message(source, command_run('§e' + i + '§r' + '  §a['+ wplist[i] + ']§r', '点击前往' + i, dim_prefix +' '+ i), True, '[' + dim_id_to_dim_name(requested_dim_id) + '] ')

# 列出全部维度路径点
def list_all_wp(source: CommandSource):
    print_message(source, '服务器管理员在§b所有维度§r设置了如下路径点：')
    print_wp(source, 0)
    print_wp(source, -1)
    print_wp(source, 1)

# 直接tp坐标点
def tp_direct(server: ServerInterface, source: CommandSource, x: float, y: float, z: float, target_dim_id: int):
    target_coordinate = coordinate_to_str(x, y, z)
    tp(server, source, target_coordinate, target_dim_id)

# 直接tp路径点
def tp_wp(server, source: CommandSource, wp_name: str, target_dim_id: int):
    wplist = wplist_convert(target_dim_id)
    config = get_config()
    try:
        tp(server, source, wplist[wp_name], target_dim_id)
    except:
        print_message(source, command_run('§c路径点名称无效!§r 点此查阅路径点列表', '查阅所有维度的路径点', config['overworld_prefix'] + ' listall'))

# 插件加载
def on_load(server: ServerInterface, old_inst):
    # 获取配置文件，热重载本插件配置文件请使用!!MCDR plg reload lazytp
    config = get_config()
    # 注册帮助信息
    server.register_help_message(config['overworld_prefix'], '传送到主世界')
    server.register_help_message(config['nether_prefix'], '传送到地狱')
    server.register_help_message(config['end_prefix'], '传送到末路之地')
    # 报错
    def print_error_msg(source: CommandSource):
        print_message(source, command_run('§c指令输入有误! §r点此显示插件帮助信息', '显示插件帮助信息', config['overworld_prefix'] + ' help'))
    # 注册主世界传送指令，默认!!overworld（请在配置文件中修改，切勿在此修改）
    server.register_command(
        Literal(config['overworld_prefix']).
        runs(lambda src: tp_convert(server, src, target_dim_id = 0)).
        then(Literal('help').
            runs(lambda src: show_help(src)).
            on_error(UnknownArgument, lambda src: print_error_msg(src), handled = False)
            ).
        then(Literal('list').
            runs(lambda src: list_wp(src, requested_dim_id = 0)).
            on_error(UnknownArgument, lambda src: print_error_msg(src), handled = False)
            ).
        then(Literal('listall').
            runs(lambda src: list_all_wp(src)).
            on_error(UnknownArgument, lambda src: print_error_msg(src), handled = False)
            ).
        then(QuotableText('name').
            runs(lambda src, ctx: tp_wp(server, src, ctx['name'], target_dim_id = 0)).
            then(Number('y').
                on_error(UnknownCommand, lambda src: print_error_msg(src), handled = False).
                on_error(InvalidNumber, lambda src: print_error_msg(src), handled = False).
            then(Number('z').
                runs(lambda src, ctx: tp_direct(server, src, ctx['name'], ctx['y'], ctx['z'], target_dim_id = 0)).
                on_error(InvalidNumber, lambda src: print_error_msg(src), handled = False).
                on_error(UnknownArgument, lambda src: print_error_msg(src), handled = False)
                )))
    )
    # 注册下界传送指令，默认!!nether（请在配置文件中修改，切勿在此修改）
    server.register_command(
        Literal(config['nether_prefix']).
        runs(lambda src: tp_convert(server, src, target_dim_id = -1)).
        then(Literal('help').
            runs(lambda src: show_help(src)).
            on_error(UnknownArgument, lambda src: print_error_msg(src), handled = False)
            ).
        then(Literal('list').
            runs(lambda src: list_wp(src, requested_dim_id = -1)).
            on_error(UnknownArgument, lambda src: print_error_msg(src), handled = False)
            ).
        then(Literal('listall').
            runs(lambda src: list_all_wp(src)).
            on_error(UnknownArgument, lambda src: print_error_msg(src), handled = False)
            ).
        then(QuotableText('name').
            runs(lambda src, ctx: tp_wp(server, src, ctx['name'], target_dim_id = -1)).
            then(Number('y').
                on_error(UnknownCommand, lambda src: print_error_msg(src), handled = False).
                on_error(InvalidNumber, lambda src: print_error_msg(src), handled = False).
            then(Number('z').
                runs(lambda src, ctx: tp_direct(server, src, ctx['name'], ctx['y'], ctx['z'], target_dim_id = -1)).
                on_error(InvalidNumber, lambda src: print_error_msg(src), handled = False).
                on_error(UnknownArgument, lambda src: print_error_msg(src), handled = False)
                )))
    )
    # 注册末路之地传送指令，默认!!end（请在配置文件中修改，切勿在此修改）
    server.register_command(
        Literal(config['end_prefix']).
        runs(lambda src: tp_convert(server, src, target_dim_id = 1)).
        then(Literal('help').
            runs(lambda src: show_help(src)).
            on_error(UnknownArgument, lambda src: print_error_msg(src), handled = False)
            ).
        then(Literal('list').
            runs(lambda src: list_wp(src, requested_dim_id = 1)).
            on_error(UnknownArgument, lambda src: print_error_msg(src), handled = False)
            ).
        then(Literal('listall').
            runs(lambda src: list_all_wp(src)).
            on_error(UnknownArgument, lambda src: print_error_msg(src), handled = False)
            ).
        then(QuotableText('name').
            runs(lambda src, ctx: tp_wp(server, src, ctx['name'], target_dim_id = 1)).
            then(Number('y').
                on_error(UnknownCommand, lambda src: print_error_msg(src), handled = False).
                on_error(InvalidNumber, lambda src: print_error_msg(src), handled = False).
            then(Number('z').
                runs(lambda src, ctx: tp_direct(server, src, ctx['name'], ctx['y'], ctx['z'], target_dim_id = 1)).
                on_error(InvalidNumber, lambda src: print_error_msg(src), handled = False).
                on_error(UnknownArgument, lambda src: print_error_msg(src), handled = False)
                )))
    )