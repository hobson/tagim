#!/usr/bin/env python
# Filename: mail.py
"""Send an email using gmail as the smtp server

Example:
	import tg.send_email
	tg.send_email.sendMail()

Depends On:
	os
	smtplib
	mimetypes
	email.MIMEMultipart .MIMEMultipart
	email.MIMEBase  MIMEBase
	email.MIMEText .MIMEText
	email.MIMEAudio .MIMEAudio
	email.MIMEImage .MIMEImage
	email.Encoders .encode_base64
	
TODO:
	Add a functions to e-mail, blog, or web2.0 share an image file.
	Eliminate model_byline variable and content before release!!!

CREDITS:
	Thanks to...
		http://stackoverflow.com/questions/5622660/attaching-file-to-an-email-in-python-leads-to-a-blank-file-name
		http://snippets.dzone.com/posts/show/2038

"""

# eliminates insidious integer division errors, otherwise '(1.0 + 2/3)' gives 1.0 (in python <3.0)
from __future__ import division

version = '0.7'

import os
import warnings
import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.Encoders import encode_base64

def send(subject = "(No Subject)", text = "(No Body)", to = 'knowledge@totalgood.com',
	     from_addr = 'knowledge@totalgood.com', user = 'hobsonlane@gmail.com', server='smtp.gmail.com', password = '', attachments=[],
	     size = None, wrap_html = False, html_format = False):
	from os import error
	#print "Using tg.mail to send e-mail"
	if not from_addr:
		from_addr = user

	if not password or not user or not server or not to:
		raise(RuntimeError("SMTP server, user, recipient (to), or password not specified. Can't log onto server to send e-mail"))
		return False

	html = ''
	if wrap_html:
		html_format = True
		html =  '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
		html += '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml">'
		html += '<body style="font-size:11px;font-family:Verdana">'
		html += 'Automatic delivery from <strong>tagim</strong>.'

	html += text

	if wrap_html:
		html += "</body></html>"

	msg = MIMEMultipart()
	msg['Subject'] = subject
	msg['From'] = user
	if type(to) == type([]):
		msg['To'] = ', '.join(to)
	else:
		msg['To'] = to

	if html_format:
		msg.attach(MIMEText(html,'html'))
	else:
		msg.attach(MIMEText(text))

	# create a separate "fileMsg" attachment
#	fileMsg = MIMEBase('application','vnd.ms-excel')
#	fileMsg.set_payload(file('2009_butter.xls').read())
#	encode_base64(fileMsg)
#	fileMsg.add_header('Content-Disposition','attachment;filename=anExcelFile.xls')
#	msg.attach(fileMsg)

	if not len(attachments)>0:
		warnings.warn("No attachments were received by tg.mail.send()")
	if not size:
		(attachments,size) = optimize_size(attachments)
	if type(attachments) == type([]):
		for attachmentPath in attachments:
			print attachmentPath
			msg.attach(getAttachment(attachmentPath,size))
	elif type(attachments) == type((str,'')):
		msg.attach(getAttachment(attachments,size))
	else:
		warnings.warn("Attachments parameter was of invalid type: ",type(attachments))

	mailServer = smtplib.SMTP(server, 587)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(user, password)
	mailServer.sendmail(user, to, msg.as_string())
	mailServer.close()

	print('Successflly sent email titled {subject} to {to}'.format(subject=subject,to=to))

def getAttachment(attachmentFilePath,size):
	if isinstance(size,str):
		size=int(size)
	if not os.path.exists(attachmentFilePath):
		warn('Attachment path is invalid: '+attachmentFilePath)

	contentType, encoding = mimetypes.guess_type(attachmentFilePath)
	print "ContentType:",contentType,"\n  encoding:",encoding,"\n  path:",attachmentFilePath

	if contentType is None or encoding is not None:
		print "Doing the octet stream encoding."
		contentType = 'application/octet-stream'

	mainType, subType = contentType.split('/', 1)
	fp = open(attachmentFilePath, 'rb')

	if mainType == 'text':
		attachment = MIMEText(fp.read())
	elif mainType == 'message':
		attachment = email.message_from_file(fp)
# these produce an empty attachment"
	elif mainType == 'image':
		# this corrupts the image that is ultimately sent out
		# attachment = MIMEImage(fp.read(),_subType=subType)
		if size:
			fp.close()
			newAttachmentFilePath = resize_image(attachmentFilePath,max_dimension = size)
			fp = open(newAttachmentFilePath, 'rb')
#	elif mainType == 'audio':
#		attachment = MIMEAudio(fp.read(),_subType=subType)
		attachment = MIMEBase(mainType, subType)
	else:
		attachment = MIMEBase(mainType, subType)
	attachment.set_payload(fp.read())
	encode_base64(attachment)

	fp.close()

	attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachmentFilePath))
	return attachment

# TODO: 
def get_size(attachmentFilePaths):
	import Image
	size = None
	pass
	return size
# TODO: 
def optimize_size(attachmentFilePaths):
	pass
	size = get_size(attachmentFilePaths)
	return (attachmentFilePaths, size)


def resize_image(attachmentFilePath, max_dimension=None, width=None, height=None):
	import tempfile, Image
	(image_name,image_ext) =  os.path.splitext(os.path.basename(attachmentFilePath))
	newAttachmentFilePath = tempfile.mktemp(suffix=image_ext, prefix=image_name+'_sm')
	img = Image.open(attachmentFilePath)
	(width0,height0)=img.size;
	max_dimension0  =max([width0,height0])
	if max_dimension0<=0:
		pass
	elif max_dimension and type(max_dimension)==type(int):
		scalefactor = max_dimension/max_dimension0
	elif (width and type(width)==type(int)) or (height and type(height)==type(int)):
		sf = [1,1];
		if width and width0>0:
			sf[0] = width/width0
		if height and height0>0:
			sf[1] = height/height0
		# so if only height or width are given the scaling will be half as "powerful" as intended due to averaging with 1
		scale_factor =  max(min((sf[0]+sf[1])/2,1.0),0.001) # prevent extrapolation (scaling >1) or extreme shrinking
		width1 = max(round(scale_factor*width0),1)
		height1 = max(round(scale_factor*height0),1)
		img = img.resize((width1, height1), Image.BILINEAR)
	img.save(newAttachmentFilePath)
	return newAttachmentFilePath

	
