#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
ALE设备专用巡检程序
支持ALE设备的tech-support命令和TFTP文件传输
"""

import os
import sys
import ftplib
import time
from datetime import datetime
from netmiko import ConnectHandler
from openpyxl.reader.excel import load_workbook
from multiprocessing.pool import ThreadPool

# 导入配置
try:
    from ale_config import get_device_credentials, get_download_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("警告: ale_config.py不可用，使用默认配置")


class ALEInspection:
    """ALE设备巡检类"""
    
    def __init__(self):
        self.device_file = "template.xlsx"  # 使用现有的xlsx文件
        self.pool = ThreadPool(10)
        self.success = []
        self.fail = []
        self.log_dir = "LOG"
        self.logtime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # 创建LOG目录
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"创建LOG目录: {self.log_dir}")
    
    def load_excel(self):
        """加载Excel文件"""
        try:
            wb = load_workbook(self.device_file)
            return wb
        except FileNotFoundError:
            print(f"Excel文件不存在: {self.device_file}")
            return None
    
    def get_device_info(self):
        """获取设备信息"""
        try:
            wb = self.load_excel()
            if not wb:
                return
                
            ws1 = wb[wb.sheetnames[0]]
            for row in ws1.iter_rows(min_row=2, max_col=9):
                if str(row[1].value).strip() == '#':
                    continue
                    
                device_type = str(row[8].value) if row[8].value else ""
                info_dict = {
                    'ip': row[2].value,
                    'protocol': row[3].value,
                    'port': row[4].value,
                    'username': row[5].value,
                    'password': row[6].value,
                    'secret': row[7].value,
                    'device_type': device_type,
                    'cmd_list': self.get_cmd_info(wb[device_type.lower().strip()]) if device_type else []
                }
                yield info_dict
                
        except Exception as e:
            print(f"读取设备信息错误: {e}")
    
    def get_cmd_info(self, cmd_sheet):
        """获取命令信息"""
        cmd_list = []
        try:
            for row in cmd_sheet.iter_rows(min_row=2, max_col=2):
                if str(row[0].value).strip() != "#" and row[1].value:
                    cmd_list.append(row[1].value.strip())
            return cmd_list
        except Exception as e:
            print(f"读取命令信息错误: {e}")
            return []
    
    def connect_device(self, host):
        """连接设备"""
        try:
            if host['protocol'].lower().strip() == 'ssh':
                host['port'] = host['port'] if (host['port'] not in [22, None]) else 22
            elif host['protocol'].lower().strip() == 'telnet':
                host['port'] = host['port'] if (host['port'] not in [23, None]) else 23
                host['device_type'] = host['device_type'] + '_telnet'
            
            # 移除不需要的参数
            connect_params = {
                'device_type': host['device_type'],
                'host': host['ip'],
                'username': host['username'],
                'password': host['password'],
                'port': host['port']
            }
            
            if host['secret']:
                connect_params['secret'] = host['secret']
            
            if 'huawei' in host['device_type']:
                connect_params['conn_timeout'] = 15
            
            connect = ConnectHandler(**connect_params)
            return connect
            
        except Exception as e:
            print(f"连接设备失败 {host['ip']}: {e}")
            self.fail.append(host['ip'])
            return None
    
    def execute_ale_tech_support(self, connection, device_ip, username=None, password=None):
        """执行ALE设备的tech-support命令并下载日志文件"""
        try:
            print(f"开始执行ALE设备 {device_ip} 的tech-support命令...")

            # 执行tech-support命令
            output = connection.send_command("show tech-support", delay_factor=2)
            print(f"tech-support命令执行完成: {device_ip}")

            # 获取配置信息
            if CONFIG_AVAILABLE:
                config = get_download_config()
                wait_time = config['files']['wait_time_after_tech_support']
                log_files = config['files']['tech_support_files']
                # 获取设备认证信息
                download_username, download_password = get_device_credentials(device_ip, username, password)
            else:
                wait_time = 10
                log_files = ["tech_support_layer3.log", "tech_support_layer2.log", "tech_support.log"]
                download_username, download_password = username, password

            # 等待文件生成
            print(f"等待日志文件生成: {wait_time}秒")
            time.sleep(wait_time)

            print(f"使用认证信息下载文件: 用户={download_username}")

            # 下载日志文件
            downloaded_files = []
            for log_file in log_files:
                if self.download_file_via_tftp(device_ip, log_file, download_username, download_password):
                    downloaded_files.append(log_file)
            
            if downloaded_files:
                print(f"成功下载 {device_ip} 的日志文件: {downloaded_files}")
                return True
            else:
                print(f"未能下载 {device_ip} 的任何日志文件")
                return False
                
        except Exception as e:
            print(f"执行tech-support失败 {device_ip}: {e}")
            return False
    
    def download_file_via_tftp(self, device_ip, filename, username=None, password=None):
        """尝试多种方式下载文件"""
        print(f"开始下载文件: {device_ip}:{filename}")

        # 方式1: 尝试SCP下载（推荐）
        if username and password:
            print("尝试方式1: SCP下载")
            if self.download_file_via_scp(device_ip, filename, username, password):
                return True

        # 方式2: 尝试FTP下载
        print("尝试方式2: FTP下载")
        if self.download_file_via_ftp(device_ip, filename, username, password):
            return True

        # 方式3: 尝试TFTP下载（如果有TFTP客户端）
        print("尝试方式3: TFTP下载")
        try:
            from tftp_downloader import TFTPClient
            tftp_client = TFTPClient(device_ip)

            device_log_dir = os.path.join(self.log_dir, f"{device_ip}_{self.logtime}")
            if not os.path.exists(device_log_dir):
                os.makedirs(device_log_dir)

            local_filename = f"{device_ip}_{filename}"
            local_path = os.path.join(device_log_dir, local_filename)

            if tftp_client.download_file(filename, local_path):
                print(f"✓ TFTP下载成功: {local_path}")
                return True

        except Exception as e:
            print(f"✗ TFTP下载失败: {e}")

        # 所有方式都失败，创建备用记录
        print(f"所有下载方式都失败，创建备用记录: {filename}")
        self.create_backup_record(device_ip, filename, "所有下载方式(SCP/FTP/TFTP)都失败")
        return False
    
    def download_file_via_netmiko(self, connection, device_ip, filename):
        """通过netmiko连接下载文件（使用设备命令）"""
        try:
            print(f"尝试通过设备命令获取文件内容: {device_ip}:{filename}")

            # 创建设备专用目录
            device_log_dir = os.path.join(self.log_dir, f"{device_ip}_{self.logtime}")
            if not os.path.exists(device_log_dir):
                os.makedirs(device_log_dir)

            # 本地文件名包含设备IP
            local_filename = f"{device_ip}_{filename}"
            local_path = os.path.join(device_log_dir, local_filename)

            # 尝试使用ALE设备的文件查看命令
            file_commands = [
                f"more {filename}",
                f"cat {filename}",
                f"show file {filename}",
                f"file show {filename}"
            ]

            file_content = None
            successful_command = None

            for cmd in file_commands:
                try:
                    print(f"  尝试命令: {cmd}")
                    output = connection.send_command(cmd, delay_factor=2)

                    # 检查输出是否包含有效内容
                    if output and len(output) > 50 and "No such file" not in output and "not found" not in output.lower():
                        file_content = output
                        successful_command = cmd
                        break

                except Exception as e:
                    print(f"  命令失败: {cmd} - {e}")
                    continue

            if file_content:
                # 保存文件内容
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(f"# ALE设备文件内容\n")
                    f.write(f"# 设备IP: {device_ip}\n")
                    f.write(f"# 文件名: {filename}\n")
                    f.write(f"# 获取命令: {successful_command}\n")
                    f.write(f"# 获取时间: {datetime.now()}\n")
                    f.write("# " + "=" * 50 + "\n\n")
                    f.write(file_content)

                print(f"✓ 文件内容获取成功: {local_path}")
                return True
            else:
                print(f"✗ 无法获取文件内容: {filename}")
                return False

        except Exception as e:
            print(f"✗ 文件获取失败 {device_ip}/{filename}: {e}")
            return False

    def download_file_via_scp(self, device_ip, filename, username, password):
        """通过SCP下载文件（需要paramiko）"""
        try:
            import paramiko

            print(f"尝试SCP下载: {device_ip}:{filename}")

            # 创建设备专用目录
            device_log_dir = os.path.join(self.log_dir, f"{device_ip}_{self.logtime}")
            if not os.path.exists(device_log_dir):
                os.makedirs(device_log_dir)

            # 本地文件名包含设备IP
            local_filename = f"{device_ip}_{filename}"
            local_path = os.path.join(device_log_dir, local_filename)

            # 创建SSH连接
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(device_ip, username=username, password=password)

            # 创建SCP客户端
            scp = ssh.open_sftp()

            # 下载文件
            remote_path = f"/{filename}"  # ALE设备根目录
            scp.get(remote_path, local_path)

            scp.close()
            ssh.close()

            print(f"✓ SCP下载成功: {local_path}")
            return True

        except ImportError:
            print(f"✗ SCP下载需要paramiko模块: pip install paramiko")
            return False
        except Exception as e:
            print(f"✗ SCP下载失败 {device_ip}/{filename}: {e}")
            return False

    def download_file_via_ftp(self, device_ip, filename, username=None, password=None):
        """通过FTP下载文件（备用方案）"""
        try:
            # 使用传入的认证信息
            ftp_server = device_ip
            ftp_user = username if username else "admin"
            ftp_password = password if password else "password"

            print(f"尝试FTP连接: {ftp_server} (用户: {ftp_user})")

            # 创建设备专用目录
            device_log_dir = os.path.join(self.log_dir, f"{device_ip}_{self.logtime}")
            if not os.path.exists(device_log_dir):
                os.makedirs(device_log_dir)

            # 本地文件名包含设备IP
            local_filename = f"{device_ip}_{filename}"
            local_path = os.path.join(device_log_dir, local_filename)

            # 尝试FTP下载
            with ftplib.FTP(ftp_server) as ftp:
                ftp.login(ftp_user, ftp_password)
                with open(local_path, 'wb') as local_file:
                    ftp.retrbinary(f'RETR {filename}', local_file.write)

            print(f"✓ FTP下载成功: {local_path}")
            return True

        except Exception as e:
            print(f"✗ FTP下载失败 {device_ip}/{filename}: {e}")
            return False

    def create_backup_record(self, device_ip, filename, error_msg):
        """创建备用记录文件"""
        try:
            device_log_dir = os.path.join(self.log_dir, f"{device_ip}_{self.logtime}")
            if not os.path.exists(device_log_dir):
                os.makedirs(device_log_dir)

            backup_file = os.path.join(device_log_dir, f"{device_ip}_{filename}.failed")
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(f"ALE设备日志文件下载失败记录\n")
                f.write(f"设备IP: {device_ip}\n")
                f.write(f"文件名: {filename}\n")
                f.write(f"时间: {datetime.now()}\n")
                f.write(f"错误信息: {error_msg}\n")
                f.write("=" * 50 + "\n")
                f.write("可能的解决方案:\n")
                f.write("1. 检查设备FTP/SCP服务是否启用\n")
                f.write("2. 确认用户名密码正确\n")
                f.write("3. 检查文件是否存在于设备根目录\n")
                f.write("4. 手动从设备下载文件\n")
                f.write("5. 检查网络连接和防火墙设置\n")

            print(f"创建备用记录: {backup_file}")
            return True

        except Exception as e:
            print(f"创建备用记录失败: {e}")
            return False
    
    def execute_regular_commands(self, connection, device_ip, cmd_list):
        """执行常规巡检命令"""
        try:
            device_log_dir = os.path.join(self.log_dir, f"{device_ip}_{self.logtime}")
            if not os.path.exists(device_log_dir):
                os.makedirs(device_log_dir)
            
            for cmd in cmd_list:
                try:
                    output = connection.send_command(cmd)
                    
                    # 保存命令输出
                    cmd_filename = cmd.replace(' ', '_').replace('/', '_') + '.txt'
                    cmd_file_path = os.path.join(device_log_dir, f"{device_ip}_{cmd_filename}")
                    
                    with open(cmd_file_path, 'w', encoding='utf-8') as f:
                        f.write(f"命令: {cmd}\n")
                        f.write(f"设备: {device_ip}\n")
                        f.write(f"时间: {datetime.now()}\n")
                        f.write("=" * 50 + "\n")
                        f.write(output)
                    
                    print(f"命令执行完成: {device_ip} - {cmd}")
                    
                except Exception as e:
                    print(f"命令执行失败: {device_ip} - {cmd} - {e}")
            
            return True
            
        except Exception as e:
            print(f"执行常规命令失败 {device_ip}: {e}")
            return False
    
    def inspect_device(self, host):
        """巡检单个设备"""
        device_ip = host['ip']
        device_type = host['device_type'].lower()
        
        print(f"开始巡检设备: {device_ip} ({device_type})")
        
        # 连接设备
        connection = self.connect_device(host)
        if not connection:
            return
        
        try:
            # 如果是ALE设备，先执行tech-support
            if 'alcatel' in device_type or 'ale' in device_type:
                print(f"检测到ALE设备: {device_ip}")

                # 执行tech-support并下载日志，使用设备的认证信息
                tech_support_success = self.execute_ale_tech_support(
                    connection, device_ip, host['username'], host['password']
                )
                
                if tech_support_success:
                    print(f"ALE设备 {device_ip} tech-support处理完成")
                else:
                    print(f"ALE设备 {device_ip} tech-support处理失败")
            
            # 执行常规巡检命令
            if host['cmd_list']:
                regular_success = self.execute_regular_commands(connection, device_ip, host['cmd_list'])
                if regular_success:
                    print(f"设备 {device_ip} 常规命令执行完成")
            
            # 记录成功
            self.success.append(device_ip)
            print(f"设备巡检完成: {device_ip}")
            
        except Exception as e:
            print(f"设备巡检失败: {device_ip} - {e}")
            self.fail.append(device_ip)
            
        finally:
            connection.disconnect()
    
    def run_inspection(self):
        """运行完整巡检流程"""
        print("=" * 60)
        print("开始网络设备巡检")
        print(f"时间: {self.logtime}")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # 获取设备列表并执行巡检
        devices = list(self.get_device_info())
        if not devices:
            print("没有找到设备配置")
            return
        
        print(f"发现 {len(devices)} 个设备")
        
        # 并发执行巡检
        for host in devices:
            self.pool.apply_async(self.inspect_device, args=(host,))
        
        self.pool.close()
        self.pool.join()
        
        end_time = datetime.now()
        
        # 打印结果
        print("\n" + "=" * 60)
        print("巡检完成")
        print("=" * 60)
        print(f"总设备数: {len(devices)}")
        print(f"成功设备: {len(self.success)}")
        print(f"失败设备: {len(self.fail)}")
        print(f"耗时: {(end_time - start_time).total_seconds():.2f}秒")
        
        if self.success:
            print("\n成功设备:")
            for device in self.success:
                print(f"  ✓ {device}")
        
        if self.fail:
            print("\n失败设备:")
            for device in self.fail:
                print(f"  ✗ {device}")
        
        # 压缩LOG文件夹
        self.compress_and_email()
    
    def compress_and_email(self):
        """压缩LOG文件夹并发送邮件"""
        try:
            from zip_file import compress_zip
            
            zip_filename = f"inspection_results_{self.logtime}.zip"
            
            if compress_zip(self.log_dir, zip_filename):
                print(f"\n✓ 巡检结果已压缩: {zip_filename}")
                
                # 发送邮件
                try:
                    from send_email import send_email
                    print("准备发送邮件...")

                    # 发送邮件，包含巡检结果
                    success = send_email(
                        attachment_files=[zip_filename],
                        success_devices=self.success,
                        failed_devices=self.fail,
                        total_time=f"{len(self.success + self.fail)} 个设备"
                    )

                    if success:
                        print("✓ 邮件发送成功!")
                    else:
                        print("✗ 邮件发送失败")

                except Exception as e:
                    print(f"邮件发送失败: {e}")
            else:
                print("✗ 压缩失败")
                
        except Exception as e:
            print(f"压缩和邮件发送失败: {e}")


def main():
    """主函数"""
    print("ALE设备专用巡检程序")
    print("支持tech-support命令和日志文件下载")
    print("=" * 60)
    
    # 检查Excel文件
    if not os.path.exists("template.xlsx"):
        print("错误: template.xlsx文件不存在")
        print("请确保Excel配置文件存在")
        return
    
    # 创建巡检实例并运行
    inspector = ALEInspection()
    inspector.run_inspection()


if __name__ == '__main__':
    main()
