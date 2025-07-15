#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
TFTP文件下载工具
专门用于从ALE设备下载tech-support日志文件
"""

import os
import socket
import struct
import time
from datetime import datetime


class TFTPClient:
    """简单的TFTP客户端实现"""
    
    def __init__(self, server_ip, server_port=69):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = None
        
    def download_file(self, remote_filename, local_filename):
        """下载文件"""
        try:
            # 创建UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(10)  # 10秒超时
            
            # 构造读请求包 (RRQ)
            rrq_packet = self._build_rrq_packet(remote_filename)
            
            # 发送读请求
            self.socket.sendto(rrq_packet, (self.server_ip, self.server_port))
            
            # 接收文件数据
            file_data = b''
            block_number = 1
            server_addr = None
            
            while True:
                try:
                    data, addr = self.socket.recvfrom(516)  # TFTP数据包最大516字节
                    
                    if server_addr is None:
                        server_addr = addr
                    
                    # 解析数据包
                    opcode = struct.unpack('!H', data[:2])[0]
                    
                    if opcode == 3:  # DATA包
                        recv_block = struct.unpack('!H', data[2:4])[0]
                        
                        if recv_block == block_number:
                            file_data += data[4:]
                            
                            # 发送ACK
                            ack_packet = self._build_ack_packet(block_number)
                            self.socket.sendto(ack_packet, server_addr)
                            
                            block_number += 1
                            
                            # 如果数据包小于512字节，说明传输完成
                            if len(data) < 516:
                                break
                                
                    elif opcode == 5:  # ERROR包
                        error_code = struct.unpack('!H', data[2:4])[0]
                        error_msg = data[4:].decode('ascii', errors='ignore').rstrip('\x00')
                        raise Exception(f"TFTP错误 {error_code}: {error_msg}")
                        
                except socket.timeout:
                    raise Exception("TFTP传输超时")
            
            # 保存文件
            with open(local_filename, 'wb') as f:
                f.write(file_data)
            
            print(f"TFTP下载成功: {remote_filename} -> {local_filename}")
            return True
            
        except Exception as e:
            print(f"TFTP下载失败: {e}")
            return False
            
        finally:
            if self.socket:
                self.socket.close()
    
    def _build_rrq_packet(self, filename):
        """构造读请求包"""
        # RRQ格式: [2字节opcode][filename][0][mode][0]
        packet = struct.pack('!H', 1)  # opcode = 1 (RRQ)
        packet += filename.encode('ascii')
        packet += b'\x00'
        packet += b'octet'  # 二进制模式
        packet += b'\x00'
        return packet
    
    def _build_ack_packet(self, block_number):
        """构造ACK包"""
        # ACK格式: [2字节opcode][2字节block number]
        return struct.pack('!HH', 4, block_number)


def download_ale_tech_support_logs(device_ip, log_dir="LOG"):
    """下载ALE设备的tech-support日志文件"""
    
    # 需要下载的日志文件
    log_files = [
        "tech_support_layer3.log",
        "tech_support_layer2.log", 
        "tech_support.log"
    ]
    
    # 创建设备专用目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    device_log_dir = os.path.join(log_dir, f"{device_ip}_{timestamp}")
    if not os.path.exists(device_log_dir):
        os.makedirs(device_log_dir)
        print(f"创建目录: {device_log_dir}")
    
    # 创建TFTP客户端
    tftp_client = TFTPClient(device_ip)
    
    downloaded_files = []
    failed_files = []
    
    for log_file in log_files:
        print(f"尝试下载: {device_ip}:{log_file}")
        
        # 本地文件名包含设备IP
        local_filename = f"{device_ip}_{log_file}"
        local_path = os.path.join(device_log_dir, local_filename)
        
        # 尝试TFTP下载
        if tftp_client.download_file(log_file, local_path):
            downloaded_files.append(local_filename)
        else:
            failed_files.append(log_file)
            
            # 创建失败记录文件
            failed_path = os.path.join(device_log_dir, f"{local_filename}.failed")
            with open(failed_path, 'w', encoding='utf-8') as f:
                f.write(f"TFTP下载失败\n")
                f.write(f"设备IP: {device_ip}\n")
                f.write(f"文件名: {log_file}\n")
                f.write(f"时间: {datetime.now()}\n")
                f.write("可能原因:\n")
                f.write("1. TFTP服务未启用\n")
                f.write("2. 文件不存在\n")
                f.write("3. 网络连接问题\n")
                f.write("4. 权限问题\n")
    
    # 打印结果
    print(f"\n设备 {device_ip} 日志下载结果:")
    print(f"成功: {len(downloaded_files)} 个文件")
    print(f"失败: {len(failed_files)} 个文件")
    
    if downloaded_files:
        print("成功下载的文件:")
        for file in downloaded_files:
            print(f"  ✓ {file}")
    
    if failed_files:
        print("下载失败的文件:")
        for file in failed_files:
            print(f"  ✗ {file}")
    
    return len(downloaded_files) > 0


def test_tftp_connection(device_ip):
    """测试TFTP连接"""
    print(f"测试TFTP连接: {device_ip}")
    
    try:
        # 尝试连接TFTP端口
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        # 发送一个简单的请求测试连接
        test_packet = struct.pack('!H', 1) + b'test\x00octet\x00'
        sock.sendto(test_packet, (device_ip, 69))
        
        # 等待响应
        try:
            data, addr = sock.recvfrom(516)
            print(f"✓ TFTP服务响应: {device_ip}")
            return True
        except socket.timeout:
            print(f"✗ TFTP服务无响应: {device_ip}")
            return False
            
    except Exception as e:
        print(f"✗ TFTP连接测试失败: {device_ip} - {e}")
        return False
        
    finally:
        sock.close()


def main():
    """主函数 - 用于测试"""
    print("TFTP下载工具测试")
    print("=" * 40)
    
    # 测试设备IP
    test_ip = input("请输入ALE设备IP地址: ").strip()
    
    if not test_ip:
        print("未输入IP地址")
        return
    
    # 测试TFTP连接
    if test_tftp_connection(test_ip):
        print("TFTP连接正常，开始下载日志文件...")
        download_ale_tech_support_logs(test_ip)
    else:
        print("TFTP连接失败，请检查:")
        print("1. 设备IP地址是否正确")
        print("2. 设备TFTP服务是否启用")
        print("3. 网络连接是否正常")
        print("4. 防火墙设置是否允许TFTP")


if __name__ == '__main__':
    main()
