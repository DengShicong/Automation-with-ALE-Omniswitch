from netmiko import ConnectHandler
def ssh_device():

    S2 = {'device_type':'alcatel_aos/cisco_ios/...',
          'ip':'IP地址',
          'username':'用户名',
          'password':'密码'}

    connect = ConnectHandler(**S2)
    print('已经成功登陆交换机' + S2['ip'])

    print('\n=================================\n')

    commands = 'show system'
    result=connect.send_command(commands)

    print('输入的命令：',commands)
    print('\n=================================\n')
    print(result)


if __name__ == '__main__':
    ssh_device()
