#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
ALE网络运维工具包 - 邮件发送模块
使用.env文件配置邮件参数
"""

import os
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr

# 导入环境配置
try:
    from env_loader import get_email_config, validate_email_config
    ENV_AVAILABLE = True
except ImportError:
    ENV_AVAILABLE = False
    print("警告: env_loader.py不可用，使用默认配置")


def get_default_config():
    """获取默认邮件配置"""
    return {
        'smtp_server': 'smtp.163.com',
        'smtp_port': 587,
        'smtp_use_tls': True,
        'sender_email': '',
        'sender_password': '',
        'sender_name': 'ALE网络运维工具包',
        'receiver_email': '',
        'receiver_name': '系统管理员',
        'cc_emails': [],
        'bcc_emails': [],
        'subject_prefix': '[ALE运维]',
        'subject_template': '{prefix} {date} ALE设备运维报告',
        'email_template': 'html',
        'max_attachment_size': 25,
        'compress_attachments': True,
        'timeout': 30,
        'retry_count': 3,
        'retry_delay': 5,
    }


def create_email_body(success_devices, failed_devices, total_time=None, attachment_files=None):
    """创建邮件正文"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_body = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; }}
            .summary {{ margin: 20px 0; }}
            .success {{ color: #28a745; }}
            .failed {{ color: #dc3545; }}
            .device-list {{ margin: 10px 0; }}
            .device-item {{ margin: 5px 0; padding: 5px; background-color: #f8f9fa; border-radius: 3px; }}
            .footer {{ margin-top: 30px; padding: 15px; background-color: #e9ecef; border-radius: 5px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>🔍 ALE设备运维报告</h2>
            <p><strong>巡检时间:</strong> {current_time}</p>
        </div>

        <div class="summary">
            <h3>📊 运维汇总</h3>
            <ul>
                <li><strong>设备总数:</strong> {len(success_devices) + len(failed_devices)}</li>
                <li class="success"><strong>成功设备:</strong> {len(success_devices)}</li>
                <li class="failed"><strong>失败设备:</strong> {len(failed_devices)}</li>
                {f'<li><strong>总耗时:</strong> {total_time}</li>' if total_time else ''}
            </ul>
        </div>
    """

    if success_devices:
        html_body += """
        <div class="device-list">
            <h3 class="success">✅ 成功设备列表</h3>
        """
        for device in success_devices:
            html_body += f'<div class="device-item">✓ {device}</div>'
        html_body += "</div>"

    if failed_devices:
        html_body += """
        <div class="device-list">
            <h3 class="failed">❌ 失败设备列表</h3>
        """
        for device in failed_devices:
            html_body += f'<div class="device-item">✗ {device}</div>'
        html_body += "</div>"

    if attachment_files:
        html_body += """
        <div class="device-list">
            <h3>📎 附件文件</h3>
        """
        for file in attachment_files:
            file_size = os.path.getsize(file) / (1024 * 1024) if os.path.exists(file) else 0
            html_body += f'<div class="device-item">📄 {os.path.basename(file)} ({file_size:.2f} MB)</div>'
        html_body += "</div>"

    html_body += f"""
        <div class="footer">
            <p>此邮件由ALE网络运维工具包自动发送</p>
            <p>如有问题，请联系系统管理员</p>
            <p>发送时间: {current_time}</p>
        </div>
    </body>
    </html>
    """

    return html_body


def send_email(subject=None, body=None, attachment_files=None, success_devices=None, failed_devices=None, total_time=None):
    """发送邮件"""
    try:
        # 获取配置
        if ENV_AVAILABLE:
            config = get_email_config()
            is_valid, errors = validate_email_config()
            if not is_valid:
                print("邮件配置验证失败:")
                for error in errors:
                    print(f"  - {error}")
                return False
        else:
            config = get_default_config()
            print("使用默认配置，请在.env文件中配置邮件参数")

        # 检查必需参数
        if not config['sender_email'] or not config['sender_password']:
            print("错误: 缺少发送者邮箱或密码配置")
            print("请在.env文件中配置 SENDER_EMAIL 和 SENDER_PASSWORD")
            return False

        if not config['receiver_email']:
            print("错误: 缺少接收者邮箱配置")
            print("请在.env文件中配置 RECEIVER_EMAIL")
            return False

        # 生成邮件主题
        if not subject:
            current_date = datetime.now().strftime("%Y-%m-%d")
            subject = config['subject_template'].format(
                prefix=config['subject_prefix'],
                date=current_date
            )

        # 生成邮件正文
        if not body:
            if success_devices is not None or failed_devices is not None:
                success_devices = success_devices or []
                failed_devices = failed_devices or []
                body = create_email_body(success_devices, failed_devices, total_time, attachment_files)
            else:
                body = f"""
                <html>
                <body>
                    <h2>ALE设备运维完成</h2>
                    <p>运维时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    <p>详细结果请查看附件</p>
                </body>
                </html>
                """

        print(f"准备发送邮件...")
        print(f"发送者: {config['sender_email']}")
        print(f"接收者: {config['receiver_email']}")
        print(f"主题: {subject}")

        # 创建邮件对象
        message = MIMEMultipart()
        message['From'] = formataddr((config['sender_name'], config['sender_email']))
        message['To'] = formataddr((config['receiver_name'], config['receiver_email']))
        message['Subject'] = subject

        # 添加抄送
        if config['cc_emails']:
            message['Cc'] = ', '.join(config['cc_emails'])

        # 添加正文
        if config['email_template'] == 'html':
            body_part = MIMEText(body, 'html', 'utf-8')
        else:
            body_part = MIMEText(body, 'plain', 'utf-8')
        message.attach(body_part)

        # 添加附件
        if attachment_files:
            for file_path in attachment_files:
                if os.path.exists(file_path):
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

                    if file_size_mb > config['max_attachment_size']:
                        print(f"警告: 附件 {file_path} 大小 {file_size_mb:.2f}MB 超过限制 {config['max_attachment_size']}MB")
                        continue

                    try:
                        with open(file_path, 'rb') as f:
                            attachment_part = MIMEApplication(f.read())
                            attachment_part.add_header(
                                'Content-Disposition',
                                'attachment',
                                filename=os.path.basename(file_path)
                            )
                            message.attach(attachment_part)
                        print(f"添加附件: {file_path} ({file_size_mb:.2f}MB)")
                    except Exception as e:
                        print(f"添加附件失败 {file_path}: {e}")
                else:
                    print(f"附件文件不存在: {file_path}")

        # 发送邮件
        recipients = [config['receiver_email']]
        if config['cc_emails']:
            recipients.extend(config['cc_emails'])
        if config['bcc_emails']:
            recipients.extend(config['bcc_emails'])

        for attempt in range(config['retry_count']):
            try:
                print(f"尝试发送邮件 (第{attempt + 1}次)...")

                if config['smtp_use_tls']:
                    # 使用TLS
                    with smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=config['timeout']) as server:
                        server.starttls()
                        server.login(config['sender_email'], config['sender_password'])
                        server.sendmail(config['sender_email'], recipients, message.as_string())
                else:
                    # 使用SSL
                    with smtplib.SMTP_SSL(config['smtp_server'], config['smtp_port'], timeout=config['timeout']) as server:
                        server.login(config['sender_email'], config['sender_password'])
                        server.sendmail(config['sender_email'], recipients, message.as_string())

                print("✓ 邮件发送成功!")
                return True

            except Exception as e:
                print(f"✗ 邮件发送失败 (第{attempt + 1}次): {e}")
                if attempt < config['retry_count'] - 1:
                    print(f"等待 {config['retry_delay']} 秒后重试...")
                    time.sleep(config['retry_delay'])

        print(f"✗ 邮件发送最终失败，已重试 {config['retry_count']} 次")
        return False

    except Exception as e:
        print(f"邮件发送异常: {e}")
        return False


def send(attachment_path=None):
    """兼容原有接口的发送函数"""
    attachment_files = [attachment_path] if attachment_path and os.path.exists(attachment_path) else None
    return send_email(attachment_files=attachment_files)


def test_email_config():
    """测试邮件配置"""
    print("测试邮件配置")
    print("=" * 40)

    if ENV_AVAILABLE:
        config = get_email_config()
        is_valid, errors = validate_email_config()

        print("当前配置:")
        for key, value in config.items():
            if 'password' in key.lower():
                print(f"  {key}: {'*' * len(str(value)) if value else '(未配置)'}")
            else:
                print(f"  {key}: {value}")

        print(f"\n配置验证: {'✓ 通过' if is_valid else '✗ 失败'}")
        if not is_valid:
            for error in errors:
                print(f"  - {error}")

        return is_valid
    else:
        print("env_loader.py不可用，无法验证配置")
        return False


def main():
    """测试邮件发送功能"""
    print("邮件发送功能测试")
    print("=" * 40)

    # 测试配置
    if not test_email_config():
        print("\n请先配置.env文件中的邮件参数")
        return

    # 发送测试邮件
    choice = input("\n是否发送测试邮件? (y/n): ").lower().strip()
    if choice in ['y', 'yes', '是']:
        success = send_email(
            subject="[测试] ALE网络运维工具包邮件测试",
            success_devices=["192.168.1.1", "192.168.1.2"],
            failed_devices=["192.168.1.3"],
            total_time="30.5秒"
        )

        if success:
            print("✓ 测试邮件发送成功")
        else:
            print("✗ 测试邮件发送失败")


if __name__ == '__main__':
    main()