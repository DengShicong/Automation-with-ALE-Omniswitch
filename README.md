# Auto-inspection

使用Openpyxl读取资产表内的网络设备基础信息，通过Netmiko连接网络设备自动写入CLI命令，并将回显信息保存到LOG文件夹内，使用Paramiko库SFTP下载网络设备内的配置文件并保存，完成连接操作后对LOG文件夹进行压缩打包并自动发送日志邮件推送给运维工作人员（netmiko支持多种厂商设备，包括虚拟环境同样适用，可直接使用EVE-NG进行测试。）

## 测试环境：



## 效果：

![1694084210259](https://github.com/DengShicong/Auto-inspection/blob/main/images/1694084210259.jpg)

![1694084308122](https://github.com/DengShicong/Auto-inspection/blob/main/images/1694084308122.jpg)



## 自动化巡检流程

![1694084457172](https://github.com/DengShicong/Auto-inspection/blob/main/images/1694084457172.jpg)

| 1    | 定义资产表，在Excel表格设置好网络设备的基础连接信息，   执行的CLI命令等 |
| ---- | ------------------------------------------------------------ |
| 2    | 通过Python读取资产表（Excel表格）内的基本信息，设备类型等    |
| 3    | 使用Netmiko建立SSH连接，连接网络设备                         |
| 4    | 在网络设备内执行表格内所获取的CLI命令                        |
| 5    | 将回显的信息进行收集并以日期，命令的格式保存到自定义的文件夹 |
| 6    | 通过SMTP下载目标文件（如配置文件）保存在LOG文件夹内          |
| 7    | 压缩打包LOG文件夹，                                          |
| 8    | 实现日志邮件自动推送                                         |

## 资产表设置

资产表作为模板，定义网络设备的基础信息，Sheet名称可自定义，表格宽度为A-I，标题行1内设置网络设备基本信息名称，可自定义但在代码内需修改相对应。

![1694084712822](https://github.com/DengShicong/Auto-inspection/blob/main/images/1694084712822.jpg)

## 命令行模板设置 

根据device_type来命名相应的sheet，设置巡检命令。标题名称comment、cmd_list可自定义，须在代码更改相对应。 

![1694084793414](https://github.com/DengShicong/Auto-inspection/blob/main/images/1694084793414.jpg)

## py文件介绍：

SSH.py是使用netmiko进行连接测试

connect.py内包含有openpyxl读取资产表信息，netmiko连接网络设备，执行CLI命令并回显信息。

send_email.py内是SMTP自动发送邮件，需要配置SMTP服务器

zip_file内是压缩打包方法

requirements.txt是开发运行环境信息，



备注：通过将上述各脚本组合再配合将回显信息写入LOG文件夹内便可实现网络自动化巡检，直接使用connect.py可满足自动化连接设备写入CLI命令并输出回显信息。
