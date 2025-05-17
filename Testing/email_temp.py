import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
import time

own = "mtranquoc77@gmail.com"
target = "tranquocminh11g2004@gmail.com"

msg = MIMEMultipart('alternative')
msg['Subject'] = "link"
msg["FROM"] = own
msg["To"] = target

text = f"Greeting !!!, {target}"
html = '''
<html>
  <head></head>
  <body>
    <p>Hi!<br>
       This is your official Salary for this month<br>
       Salary of Month: 4.000.000
       Deductions: 150.000
       netSalary: 3.850.000

       IF YOU HAVE ANY QUESTIONS, CONTACT TO HR TO HAVE SOME CRITICAL ANSWERS

       
      
    </p>
  </body>

'''
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

msg.attach(part1)
msg.attach(part2)
print("Attach mail...")
time.sleep(3)
send = smtplib.SMTP('smtp.gmail.com', 587)
send.starttls()
send.login(own, password="xkfvaaaxminlxkme")
print(f"Wrapping content and Sending to {target} ...")
time.sleep(3)

send.sendmail(own, target, msg.as_string())
send.quit()
print("Completed !!!")