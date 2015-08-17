
import math
import datetime

EFACTOR_DEFAULT = 2.5
DEFAULT_Q = 4
STRING_TIME = "%d-%m-%Y"

def getEFactor(question, quality=DEFAULT_Q):
	print question
	if question.get('e-factor', None):
		if quality > 3:
			if question['e-factor'] >= 1.3:
				question['e-factor']=question['e-factor']+(0.1-(5-quality)*(0.08+(5-quality)*0.02))
	else:
		question['e-factor']=2.5
	print question['e-factor']
	return question['e-factor']

def getIInterval(question, quality=DEFAULT_Q):
	if question.get('i-interval', None)==None:
		question['i-interval']=1
	elif question['i-interval']==1:
		question['i-interval']=6
	else:
		question['i-interval']=int(math.ceil(question['i-interval']*question['e-factor']))
	if quality < 3:
		question['i-interval']=1
	return question['i-interval']

def getReplyAt(question, quality=DEFAULT_Q):
	if quality < 3:
		question['reply_at']=None
	else:
		question['reply_at']=datetime.date.today()+datetime.timedelta(days=int(float(question["i-interval"])))
		question['reply_at']=question['reply_at'].strftime(STRING_TIME)
	return question['reply_at']