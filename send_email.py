import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send():
    # 配置邮件信息
    sender = '发送者邮箱'
    receiver = '接受者邮箱'
    subject = '标题'
    attachment_path = '附件'

    # 构造邮件对象
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject

    # 添加正文
    body = MIMEText('正文')
    message.attach(body)

    # 添加附件
    with open(attachment_path, 'rb') as attachment:
        attachment_part = MIMEApplication(attachment.read())
        attachment_part.add_header('Content-Disposition', 'attachment', filename='附件')
        message.attach(attachment_part)

    # 发送邮件



    with smtplib.SMTP_SSL('smtp.qq.com',465) as server:
        server.ehlo()
        server.set_debuglevel(1)
        server.login('用户名', '授权码')
        server.sendmail(sender, receiver, message.as_string())

        server.quit()

if __name__ == '__main__':
    send()