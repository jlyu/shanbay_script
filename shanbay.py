# -*- coding: utf-8 -*-
import sys
type = sys.getfilesystemencoding()
import urllib,urllib2
import cookielib
import re
import sched
import time

domin_url=r'http://www.shanbay.com'
CHECK_IN_POINT=7
CHECK_IN_RATE=75
ELIMINATE_RATE=3
SAVE_PATH="C:\\Python27\\shanbay\\"

s = sched.scheduler(time.time, time.sleep)

headers = { 
		'(Request-Line)':'POST /accounts/login/ HTTP/1.1',
		'Host':'www.shanbay.com',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language':'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
		#'Accept-Encoding':'gzip, deflate',
		'Connection':'keep-alive',
		'Referer':'http://www.shanbay.com/accounts/login/',
		'Cookie':'csrftoken=cd854e88ca2c4b55dee261daa58e7545; __utma=183787513.439679500.1332726535.1332726535.1332726535.1; \
					__utmb=183787513.12.9.1332727075064; __utmz=183787513.1332726535.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); \
					csrftoken=cd854e88ca2c4b55dee261daa58e7545; sessionid=8b8cacdd15063df5e40210fc0dccbfb6; \
					base_domain_c382b335ef05427a82a8d8cf07aa6261=shanbay.com; __utmc=183787513; \
					xnsetting_c382b335ef05427a82a8d8cf07aa6261=%7B%22connectState%22%3A2%2C%22oneLineStorySetting%22%3A3%2C%22shortStorySetting%22%3A3%2C%22shareAuth%22%3Anull%7D',
		'Content-Type':'application/x-www-form-urlencoded',
		'Content-Length':'121'
		} 
postdata=urllib.urlencode({
		'csrfmiddlewaretoken':'cd854e88ca2c4b55dee261daa58e7545',
		'username':'************',
		'password':'************',
		'login':'',
		'continue':'home',
		'u':'1',
		'next':'',
		})
		
class UserInfo:
	def __init__(self, rank, name, value, age, index, rate, commend, kickurl):
		self.rank=rank
		self.name=name
		self.value=value
		self.age=age
		self.index=index
		self.rate=rate
		self.commend=commend
		self.kickurl=kickurl
	
	def __unicode__(self):
		return u'%s %s' % (self.name, self.rate)

class MembershipManagement:
	def __init__(self, UserInfoList):
		self.UserInfoList=UserInfoList
		
	def Run(self):
		self.age2day()
		self.CalculateCheckinRate()
		self.SetCommand()
		self.SortUserInfo()
		self.PlayEliminationSystem()
		self.CalculateRank()
		#self.KickOffMember()
		
	
	def age2day(self):
		for i in xrange(len(self.UserInfoList)):
			user_age=self.UserInfoList[i].age
			month=re.findall(ur'''(\d+) 月'''.encode('utf-8'),user_age)
			week=re.findall(ur'''(\d+) 星期'''.encode('utf-8'),user_age)  
			day =re.findall(ur'''(\d+) 天'''.encode('utf-8'),user_age)
			user_days=0
			if month:user_days+=int(month[0])*30
			if week:user_days+=int(week[0])*7
			if day: user_days+=int(day[0])
			self.UserInfoList[i].age=str(user_days)
			
	def CalculateCheckinRate(self):
		print 'start CalculateCheckinRate--------->'
		for i in xrange(len(self.UserInfoList)):
			user_value=self.UserInfoList[i].value
			user_days=self.UserInfoList[i].age
			total_value=(int(user_days))*CHECK_IN_POINT
			try:
				check_in_rate=int(user_value)*100/total_value
				#print 'fore:'+str(check_in_rate)
				if check_in_rate!=100: #补偿一天
					check_in_rate=(int(user_value)+7)*100/total_value
					#print 'after:'+str(check_in_rate)
				self.UserInfoList[i].rate=str(check_in_rate)
			except:
				self.UserInfoList[i].rate='0'
				print 'except:('
	
	def CalculateRank(self):
		user_num=len(self.UserInfoList)
		current_rank=1
		print 'start CalculateRank.. total: '+str(user_num)
		try:
			current_rate=self.UserInfoList[0].rate
			for i in xrange(user_num):
				if self.UserInfoList[i].rate==current_rate:
					self.UserInfoList[i].rank=str(current_rank)
				else:
					current_rate=self.UserInfoList[i].rate
					self.UserInfoList[i].rank=str(i+1)
					current_rank=i+1
		except:
			print 'error! rank'
	
	def SetCommand(self):
		for i in xrange(len(self.UserInfoList)):
			user_check_in_rate = int(self.UserInfoList[i].rate)
			if user_check_in_rate>=100:
				self.UserInfoList[i].commend='模范组员'
			elif 90<=user_check_in_rate<100:
				self.UserInfoList[i].commend='★★★'
			elif 80<=user_check_in_rate<90:
				self.UserInfoList[i].commend='★★'
			elif CHECK_IN_RATE<=user_check_in_rate<80:
				self.UserInfoList[i].commend='★'
			else:
				self.UserInfoList[i].commend='已低于标准值'
	
	def SortUserInfo(self):
		self.UserInfoList = sorted(self.UserInfoList, key=lambda user:int(user.rate),reverse=True)
		
	def PlayEliminationSystem(self):
		eliminate_num = -len(self.UserInfoList)*ELIMINATE_RATE/100
		print 'eliminate_num:'+str(eliminate_num)
		for i in xrange(-1,eliminate_num-1,-1):
			if int(self.UserInfoList[i].rate)<CHECK_IN_RATE:
				self.UserInfoList[i].commend='踢除'
	
	def KickOffMember(self):
		f=open(SAVE_PATH+'KickOffList.txt','w')
		for i in xrange(len(self.UserInfoList)):
			user_name =self.UserInfoList[i].name
			user_index=self.UserInfoList[i].index
			user_kickurl=self.UserInfoList[i].kickurl
			if self.UserInfoList[i].commend=='踢除':
				content = urllib2.urlopen(user_kickurl).read()
				print content.decode('utf-8').encode(type)
				repo = "组员["+user_name+"]已被踢除，个人主页："+user_index
				f.write(repo+'\r\n')
			f.close()

	def PrintReport(self):
		f=open(SAVE_PATH+'CheckinReport.txt','w')
	
		for i in xrange(len(self.UserInfoList)):
			user_rank =self.UserInfoList[i].rank
			user_name =self.UserInfoList[i].name#.decode('utf-8').encode(type)
			user_value=self.UserInfoList[i].value#.decode('utf-8').encode(type)
			user_age  =self.UserInfoList[i].age#.decode('utf-8').encode(type)
			user_index=self.UserInfoList[i].index#.decode('utf-8').encode(type)
			user_check_in_rate=self.UserInfoList[i].rate
			user_commend=self.UserInfoList[i].commend
			repo="No."+user_rank+" 组员["+user_name+"]的贡献值("+user_value+"),入组天数{"+user_age+"} 个人打卡率："+user_check_in_rate+'%，评价【'+user_commend+'】'
			#print repo
			f.write(repo+'\r\n')
		f.close()
	
	
def Login():
		print "Start to Login..."
		cj=cookielib.CookieJar()
		cookie_support= urllib2.HTTPCookieProcessor(cj)
		opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
		urllib2.install_opener(opener)
		req = urllib2.Request(url=r'http://www.shanbay.com/accounts/login/',
								data=postdata,
								headers = headers)
		content = urllib2.urlopen(req).read()
		print "Login OK!"

def GetPages(url):
	pages=1
	content=GetPageSource(url)
	#<span class="number">291 / 300</span>
	p = re.findall(ur'''class="number">(\d+)\s''',content)
	assert(len(p)==1)
	pages=int(p[0])
	return pages
	
def GetPageSource(url):
	req = urllib2.Request(url,data=postdata,)
	print "browse:"+url
	content = urllib2.urlopen(req).read()
	return content

def GetPageUserInfo(content):
	users_info=[]
	user_name=re.findall(ur'''<a\s*[^>]*/user/list/[^>]*>([^<]*)<\/a>''',content)
	
	user_points=re.findall(ur'''<td\s*[^>]*[^>]*>([^<]*)<\/td>''',content)          
	user_value=[user_points[i] for i in range(len(user_points)) if not i%2] 		 
	user_age=[user_points[i] for i in range(len(user_points)) if i%2]
	
	user_index=re.findall(ur'''/user/list/([^<]*)">''',content)
	user_index=[r'''http://www.shanbay.com/user/list/'''+user_index[i] for i in range(len(user_index)) if i%2]
	
	user_memberid=re.findall(ur'''member_id="(\d+)"''',content)
	user_kickurl=[r'''http://www.shanbay.com/team/dismiss/?dismiss_member_ids='''+user_memberid[i]+r'&team_id=16'\
					for i in range(len(user_memberid))]
	#print user_kickurl
	
#test
	len_user_name=len(user_name)
	len_user_value=len(user_value)
	len_user_age=len(user_age)
	len_user_index=len(user_index)
	len_user_kickurl=len(user_kickurl)
	#print len_user_name,len_user_value,len_user_age,len_user_index
	assert(len_user_name==len_user_value==len_user_age==len_user_index==len_user_kickurl) 
	
	for i in xrange(len_user_name):
		user=UserInfo('',user_name[i],user_value[i],user_age[i],user_index[i],'','',user_kickurl[i])
		users_info.append(user)
	#print "Got user info!"
	return users_info

def GetAllUserInfo(url,pages):
	if pages%10!=0:
		page = pages//10+1
	else:
		page = pages//10
		
	all_users_info=[]
	for index in xrange(1,page+1):#pages+1):
		query_url=re.sub(ur"{index}",str(index),url)
		content=GetPageSource(query_url)
		page_users_info=GetPageUserInfo(content)
		all_users_info.extend(page_users_info)
		
	mm=MembershipManagement(all_users_info)
	return mm


	
def Main():
	Login()
	
	group_index=domain_url+r"/team/detail/16/"
	pages=GetPages(group_index)
	print 'group member:' + str(pages)
	url=domain_url+r'/team/show_dismiss/16/?page={index}'
	
	membershipManagement=GetAllUserInfo(url,pages)
	membershipManagement.Run()
	
	s.enter(86400, 1, Main, ()) # 每天查询一次
	s.run()
	
	
if __name__=='__main__':
	Main()
	