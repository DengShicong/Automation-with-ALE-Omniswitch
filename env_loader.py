#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
环境变量加载器
用于加载.env文件中的配置
"""

import os
from typing import Dict, Any, Optional


class EnvLoader:
    """环境变量加载器"""
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
        self.env_vars: Dict[str, str] = {}
        self.load_env_file()
    
    def load_env_file(self):
        """加载.env文件"""
        if not os.path.exists(self.env_file):
            print(f"警告: 环境配置文件 {self.env_file} 不存在")
            return
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # 跳过空行和注释行
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析键值对
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 移除值两端的引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        self.env_vars[key] = value
                        
                        # 同时设置到系统环境变量
                        os.environ[key] = value
                    else:
                        print(f"警告: .env文件第{line_num}行格式错误: {line}")
            
            print(f"成功加载环境配置文件: {self.env_file}")
            
        except Exception as e:
            print(f"加载环境配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取环境变量值"""
        # 优先从系统环境变量获取
        value = os.environ.get(key)
        if value is not None:
            return self._convert_value(value)
        
        # 从.env文件获取
        value = self.env_vars.get(key)
        if value is not None:
            return self._convert_value(value)
        
        return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔值"""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'on', 'enabled')
        return bool(value)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数值"""
        value = self.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """获取浮点数值"""
        value = self.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_list(self, key: str, separator: str = ',', default: Optional[list] = None) -> list:
        """获取列表值"""
        if default is None:
            default = []
        
        value = self.get(key, '')
        if not value:
            return default
        
        return [item.strip() for item in value.split(separator) if item.strip()]
    
    def _convert_value(self, value: str) -> Any:
        """转换值类型"""
        if not isinstance(value, str):
            return value
        
        # 尝试转换为数字
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # 尝试转换为布尔值
        if value.lower() in ('true', 'false', 'yes', 'no', 'on', 'off', 'enabled', 'disabled'):
            return value.lower() in ('true', 'yes', 'on', 'enabled')
        
        return value
    
    def set(self, key: str, value: Any):
        """设置环境变量"""
        str_value = str(value)
        self.env_vars[key] = str_value
        os.environ[key] = str_value
    
    def get_all(self) -> Dict[str, str]:
        """获取所有环境变量"""
        return self.env_vars.copy()
    
    def print_config(self, mask_passwords: bool = True):
        """打印配置信息"""
        print("当前环境配置:")
        print("=" * 50)
        
        for key, value in sorted(self.env_vars.items()):
            # 隐藏密码类字段
            if mask_passwords and any(pwd_key in key.lower() for pwd_key in ['password', 'pass', 'secret', 'key']):
                display_value = '*' * len(value) if value else ''
            else:
                display_value = value
            
            print(f"{key}: {display_value}")


# 全局环境加载器实例
env = EnvLoader()


def get_email_config() -> Dict[str, Any]:
    """获取邮件配置"""
    return {
        # SMTP配置
        'smtp_server': env.get('SMTP_SERVER', 'smtp.163.com'),
        'smtp_port': env.get_int('SMTP_PORT', 587),
        'smtp_use_tls': env.get_bool('SMTP_USE_TLS', True),
        
        # 发送者配置
        'sender_email': env.get('SENDER_EMAIL', ''),
        'sender_password': env.get('SENDER_PASSWORD', ''),
        'sender_name': env.get('SENDER_NAME', '网络巡检系统'),
        
        # 接收者配置
        'receiver_email': env.get('RECEIVER_EMAIL', ''),
        'receiver_name': env.get('RECEIVER_NAME', '系统管理员'),
        
        # 抄送和密送
        'cc_emails': env.get_list('CC_EMAILS'),
        'bcc_emails': env.get_list('BCC_EMAILS'),
        
        # 邮件主题和内容
        'subject_prefix': env.get('EMAIL_SUBJECT_PREFIX', '[网络巡检]'),
        'subject_template': env.get('EMAIL_SUBJECT_TEMPLATE', '{prefix} {date} ALE设备巡检报告'),
        'email_template': env.get('EMAIL_TEMPLATE', 'html'),
        
        # 附件配置
        'max_attachment_size': env.get_int('MAX_ATTACHMENT_SIZE', 25),
        'compress_attachments': env.get_bool('COMPRESS_ATTACHMENTS', True),
        
        # 其他配置
        'timeout': env.get_int('EMAIL_TIMEOUT', 30),
        'retry_count': env.get_int('EMAIL_RETRY_COUNT', 3),
        'retry_delay': env.get_int('EMAIL_RETRY_DELAY', 5),
    }


def validate_email_config() -> tuple[bool, list]:
    """验证邮件配置"""
    config = get_email_config()
    errors = []
    
    # 检查必需字段
    required_fields = [
        ('sender_email', '发送者邮箱'),
        ('sender_password', '发送者密码'),
        ('receiver_email', '接收者邮箱'),
        ('smtp_server', 'SMTP服务器'),
    ]
    
    for field, name in required_fields:
        if not config.get(field):
            errors.append(f"缺少{name}配置: {field}")
    
    # 检查邮箱格式
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if config['sender_email'] and not re.match(email_pattern, config['sender_email']):
        errors.append(f"发送者邮箱格式错误: {config['sender_email']}")
    
    if config['receiver_email'] and not re.match(email_pattern, config['receiver_email']):
        errors.append(f"接收者邮箱格式错误: {config['receiver_email']}")
    
    return len(errors) == 0, errors


def main():
    """测试环境加载器"""
    print("环境变量加载器测试")
    print("=" * 40)
    
    # 打印配置
    env.print_config()
    
    print("\n邮件配置:")
    print("=" * 40)
    config = get_email_config()
    for key, value in config.items():
        if 'password' in key.lower():
            print(f"{key}: {'*' * len(str(value)) if value else ''}")
        else:
            print(f"{key}: {value}")
    
    print("\n配置验证:")
    print("=" * 40)
    is_valid, errors = validate_email_config()
    if is_valid:
        print("✓ 邮件配置验证通过")
    else:
        print("✗ 邮件配置验证失败:")
        for error in errors:
            print(f"  - {error}")


if __name__ == '__main__':
    main()
