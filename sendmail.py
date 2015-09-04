import sys
sys.path.append('/home/nikoulis/anaconda/lib/python2.7/site-packages')  # For Ubuntu
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os
import pdb
from diffs import *

#-----------------------------------------------
# Return a string representation of a text file
#-----------------------------------------------
def fileToStr(filename):
    f = open(filename)
    text = ''
    for line in f:
        text += line
    return text

#------------------------------------
# Create a PDF file from a text file
#------------------------------------
def createPdf(filename, outFilename):
    command = 'enscript -r -f Courier9 ' + filename + ' -o - | ps2pdf - ' + outFilename
    os.system(command)

#-----------------------
# Send a file via email
#-----------------------
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: sendmail.py <US/LSE> <yyyymmmdd>'
        sys.exit()

    market = sys.argv[1]
    dates = getDates(market)
    if len(sys.argv) >= 3:
        asofDate = sys.argv[2]
    else:
        # Use last date from file
        asofDate = dates[-1]

    currentDate = int(time.strftime('%Y%m%d'))

    hostname = 'mail.anthos-trading.com'
    password = 'ai024709th3669'
    sender = 'panos.nikoulis@anthos-trading.com'
    recipients = ['pnikoulis@yahoo.com']

    msg = MIMEMultipart()
    msg.set_charset("utf-8")
    msg['Subject'] = 'Artemis ' + market + ' ' + getMatchStr(str(currentDate))
    msg['From'] = sender
    msg['To'] = ','.join(recipients)

    # Text attachments are a bot garbled on iOS, so put in message body instead
    ATTACH = True
    if ATTACH:
        msg.attach(MIMEText(''))
        # Attach file
        filename = market + '-perf-' + str(asofDate) + '.txt'
        outFilename = market + '-perf-' + str(asofDate) + '.pdf'
        createPdf(filename, outFilename)
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(outFilename, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(outFilename))
        msg.attach(part)
    else:
        body = fileToStr(filename)
        msg.attach(MIMEText(body, 'plain'))

    # Send mail
    s = smtplib.SMTP_SSL(hostname)
    s.login(sender, password)
    s.sendmail(sender, [recipients], msg.as_string())
    s.quit()
