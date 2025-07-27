from flask import Flask, render_template, request, jsonify
import re
import string
# 从自定义绕过生成器模块导入所需功能
from bypass_generator import generate_bypass_commands, generate_bypass, get_alternatives, analyze_characters

# 初始化Flask应用
app = Flask(__name__)

# 路由
# 路由：首页
@app.route('/')
def index():
    # 渲染主页面模板
    return render_template('index.html')

# 路由：分析字符禁用情况 (POST请求)
@app.route('/analyze', methods=['POST'])
def analyze():
    # 从请求中获取正则表达式
    regex = request.json.get('regex', '')
    if not regex:
        # 如果未提供正则表达式，返回错误信息
        return jsonify({'error': '请输入正则表达式'}), 400
    
    try:
        # 构建完整的正则表达式模式（精确匹配）
        regex_pattern = f'^{regex}$'
        # 调用字符分析函数
        chars = analyze_characters(regex_pattern)
        # 返回分析结果
        return jsonify({
            'banned_chars': chars['banned'],
            'allowed_chars': chars['allowed']
        })
    except Exception as e:
        # 处理正则表达式无效的情况
        return jsonify({'error': f'无效的正则表达式: {str(e)}'}), 400

@app.route('/generate-commands', methods=['POST'])
def generate_commands():
    regex = request.json.get('regex', '')
    if not regex:
        return jsonify({'error': '请输入正则表达式'}), 400
    
    try:
        regex_pattern = f'^{regex}$'
        commands = generate_bypass_commands(regex_pattern)
        return jsonify(commands)
    except Exception as e:
        return jsonify({'error': f'生成命令失败: {str(e)}'}), 400

# 路由：生成自定义命令绕过方案 (POST请求)
@app.route('/generate-custom', methods=['POST'])
def generate_custom():
    # 从请求中获取正则表达式和自定义命令
    regex = request.json.get('regex', '')
    cmd = request.json.get('cmd', '')
    if not regex or not cmd:
        # 如果缺少参数，返回错误信息
        return jsonify({'error': '请输入正则表达式和命令'}), 400
    
    try:
        # 构建完整的正则表达式模式
        regex_pattern = f'^{regex}$'
        regex_obj = re.compile(regex_pattern)
        
        # 检查原始命令是否有效
        original_valid = all(not regex_obj.match(char) for char in cmd)
        bypasses = []
        if original_valid:
            bypasses.append(f'原始命令 (有效): {cmd}')
        
        # 生成绕过命令
        bypass = generate_bypass(cmd, regex_obj)
        if bypass:
            bypasses.append(f'替换绕过: {bypass}')
        
        # 生成替代命令
        alternatives = get_alternatives(cmd)
        for alt in alternatives:
            if all(not regex_obj.match(char) for char in alt):
                bypasses.append(f'替代命令: {alt}')
        
        # 返回生成的绕过方案
        return jsonify({'bypasses': bypasses if bypasses else ['未找到可用的绕过方案']})
    except Exception as e:
        # 处理生成过程中的错误
        return jsonify({'error': f'生成自定义命令失败: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=True)