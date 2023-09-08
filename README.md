# Automation-with-ALE-Omniswitch

Use Openpyxl to read the basic information of the network device in the asset table, connect to the network device through Netmiko to automatically write CLI commands, and save the display information to the LOG folder, use the Paramiko library SFTP to download the configuration file of the network device and save it, and then after completing the connection operation, compress and pack up the LOG folder and send out the logs automatically by e-mail to the operation and maintenance staff (netmiko supports a variety of vendors, including virtual environments is also applicable). To the operation and maintenance staff (netmiko supports a variety of vendors equipment, including virtual environments are also applicable, you can use EVE-NG directly for testing.)



## Test environment:

![1694090216090](https://github.com/DengShicong/Auto-inspection/blob/main/images/1.jpg)



## effects：

![1694084210259](https://github.com/DengShicong/Auto-inspection/blob/main/images/1694084210259.jpg)

![1694084308122](https://github.com/DengShicong/Auto-inspection/blob/main/images/1694084308122.jpg)



## Automation process

![1694084457172](https://github.com/DengShicong/Auto-inspection/blob/main/images/1694084457172.jpg)

| 1    | Define the asset table, set up the basic connection information of the network device in the Excel sheet, execute the CLI commands, etc. |
| ---- | ------------------------------------------------------------ |
| 2    | **Read basic information, device type, etc. from asset table (Excel sheet) via Python** |
| 3    | **Use Netmiko to establish an SSH connection to a network device** |
| 4    | **Execute the CLI commands obtained from the form within the network device.** |
| 5    | **Collects and saves the displayed information in date and command format to a customized folder.** |
| 6    | **Download target files (e.g. configuration files) via SMTP to be saved in the LOG folder** |
| 7    | **Compressed and packed LOG folder.**                        |
| 8    | **Realize log mail auto-push**                               |

## Asset table setup

The Asset Sheet is used as a template to define the basic information of the network equipment, the Sheet name can be customized, the table width is A-I, and the name of the basic information of the network equipment is set within the header row 1, which can be customized but needs to be modified within the code to correspond to it.

![1694084712822](https://github.com/DengShicong/Auto-inspection/blob/main/images/1694084712822.jpg)

## Command Line Template Settings 

Name the corresponding sheet according to device_type to set the inspection command. Title name comment, cmd_list can be customized, must be in the code change corresponding. 

![1694084793414](https://github.com/DengShicong/Auto-inspection/blob/main/images/1694084793414.jpg)

## Introduction to py files：

**SSH.py** is a connection test using netmiko.

**connect.py** contains openpyxl to read the asset table information, netmiko to connect to the network device, execute CLI commands and display the information back.

**send_email.py** contains SMTP to send emails automatically, you need to configure the SMTP server.

**zip_file.py** is the compression and packaging method.

**requirements.txt** is the development environment information.



Note: By combining the above scripts and writing the display information into the LOG folder, you can realize the network automation patrol, and directly use connect.py to meet the automation of connecting devices to write CLI commands and output display information.
