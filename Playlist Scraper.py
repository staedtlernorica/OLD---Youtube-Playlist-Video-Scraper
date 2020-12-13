#START HERE
#https://www.youtube.com/watch?v=th5_9woFJmk
from googleapiclient.discovery import build

#----------------------------------------------------------------------------
api_key = 'Put Your Youtube API Key Here'

#Watch first couple minutes to get your own API key
#https://www.youtube.com/watch?v=th5_9woFJmk
#----------------------------------------------------------------------------

youtube = build('youtube', 'v3', developerKey = api_key)

#some sample playlist
zp = 'PLAbMhAYRuCUhawCEV2oXZGrienoKTN16X'
dope_tech = 'PLBsP89CPrMePWBCMIp0naluIz67UwRX9B'
eh = 'PLhyKYa0YJ_5Aq7g4bil7bnGi0A8gTsawu'


#----------------------------------------------------------------------------
#MANUAL ENTRY HERE, PROGRAM WILL DO THE REST
#----------------------------------------------------------------------------
#NEED TO MANUALLY SET TO 1 IF FIRST VID IN PLAYLIST IS PREMIUM
#NEED TO MANUALLY SET TO 1 IF FIRST VID IN PLAYLIST IS PREMIUM
#0 = no (like Extra History), 1 = yes (like Zero Punctuation)
premiumVid = 1
#NEED TO MANUALLY SET ID OF PLAYLIST TO BE SCRAPED
#NEED TO MANUALLY SET ID OF PLAYLIST TO BE SCRAPED
#NEED TO MANUALLY SET ID OF PLAYLIST TO BE SCRAPED
#SO DONT HAVE TO CHANGE A BUNCH OF PLAYLIST ID VARIABLE
scrapedPlaylistId = eh
#SET NAME OF DESIRED CSV
#SET NAME OF DESIRED CSV
#SET NAME OF DESIRED CSV
csvName = 'Extra History Playlist Video Data'+".csv"
#----------------------------------------------------------------------------

#take snippets from a playlist
def callYoutube(token='', desiredPlaylistId = ''):
	return youtube.playlistItems().list(
		part='snippet',
		playlistId = desiredPlaylistId,
		maxResults = 50,
		pageToken = token
		)

#calculate how many tokens will be needed/the amount of time to
#run the get token loop
def numTokensNeeded(desiredPlaylistId = ''):
	totalVidRequest = youtube.playlistItems().list(
			part='snippet',
			playlistId = desiredPlaylistId,
			)
	response = totalVidRequest.execute()

	#get total number of videos in the playlist
	numVidsInPlaylist = response['pageInfo']['totalResults']   
	numTokensNeeded = 0

	if numVidsInPlaylist%50 == 0:			#calculation formulas
		return numVidsInPlaylist/50 - 1
	else: 
		return divmod(numVidsInPlaylist, 50)[0] 
		#remember first 50 vids dont need/have nextPageToken


totalNumTokensNeeded = numTokensNeeded(scrapedPlaylistId)
i = tokens_used = 0
allNextToken = ['']

#run loop to get all nextPageToken, to crawl through the entire 
#playlist 50 vids at a time
#(totalNumTokensNeeded + 1) parameter is only for maxResults = 50
while len(allNextToken) != totalNumTokensNeeded + 1:
	extractNextToken = callYoutube(allNextToken[i], scrapedPlaylistId).execute()
	allNextToken.append(extractNextToken['nextPageToken'])
	i=i+1


#scrape items gotten with callYoutube function
def scrapePlayListItems(playListItemsDict={}):
	tempList = []
	o = 1

	for i in playListItemsDict["items"]:		
		vidId = i['snippet']['resourceId']['videoId']
#		print(o, vidId)	
		tempList.append(vidId)

		#can turn on to print video title, for easy track keeping
		# vidTitle = i['snippet']['title']
		# tempList.append((vidTitle, vidId))
		# print(o,(vidTitle, vidId))	
		o=o+1
	return tempList


#each element is a list containing 50 video ids
playlistIds = []

for token in allNextToken:
	youtubeDictObject = callYoutube(token,scrapedPlaylistId).execute()
	tempList = scrapePlayListItems(youtubeDictObject)
	playlistIds.append(tempList)


#turn [['a','b','c'], ['c','d']] into ['a,b,c', 'c,d']
# eg     3 strings    2 string          1 str   1 str
def oneLongString(vidIdsList=[]):

	idsList = vidIdsList
	tempString = ''

	for id in idsList:
		tempString = tempString + id +','

	#[:-1] b/c want to remove unwanted comma from last entry
	#or will cause error with nextPageToken
	return tempString[:-1]


stringedPlaylistIds = []

#apply oneLongString methods to each of the id list in playListIds
for i in playlistIds:
	stringedPlaylistIds.append(oneLongString(i))


def getYoutubeVideosStats(vidIds = ''):
	return youtube.videos().list(
    part="snippet,statistics",
    id= vidIds
    )

rawYoutubeStatsDict = []

for i in stringedPlaylistIds:
	x = getYoutubeVideosStats(i).execute() 
	rawYoutubeStatsDict.append(x)


#turn on/off as needed, if premium vid also appear first in playlist
if premiumVid == 1:
	del rawYoutubeStatsDict[0]['items'][0]
#ie remove data of the first scrapedPlaylistId video, which is for premium  
#subscribers only with no dict key 'viewCount', which will throw error
#can ignore private vids, bc wont throw up errors


def scrapeYoutubeVidStats(statDictObj = {}):

	tempDict = statDictObj
	tempList = []

	for i in tempDict['items']:

		vidTitle = i['snippet']['title']
		vidDate = i['snippet']['publishedAt'][:10]
		#[:10] bc only care about dates, not hour	
		vidViews = i['statistics']['viewCount']
		vidLikes = i['statistics']['likeCount']
		vidDislikes = i['statistics']['dislikeCount']
		vidComments = i['statistics']['commentCount']

		tempList.append((vidTitle, vidDate, vidViews,
			vidLikes, vidDislikes, vidComments))

	return tempList


finalPlaylistStats = []

for i in rawYoutubeStatsDict:
	x = scrapeYoutubeVidStats(i)
	finalPlaylistStats.append(x)


#[title, date, views, likes, dislikes, comments] format
polishedPlaylistStatsInfo = []

#make finalPlaylistStats, [[a,b,c], [d,e,f], [g]] 
#into [a,b,c,d,e,f,g]
for i in finalPlaylistStats:
	for o in i:
		polishedPlaylistStatsInfo.append(o)


for i in polishedPlaylistStatsInfo:
	print(polishedPlaylistStatsInfo.index(i)+1 ,i)


import csv
#path = '/Users/Work/Desktop/csv test printing/'	#print to folder on Desktop 
path = '/Users/Work/Desktop/'						#print to Desktop	
#newline='' helps prevent line skipping when printing entry
#https://stackoverflow.com/questions/3348460/csv-file-written-with-python-has-blank-lines-between-each-row
#-------------------------------------------------------------------------------------
#encoding='UTF-8' o/w will run into UnicodeEncodeError, eg with EH episode
#♫ Admiral Yi: Drums of War - Sean and Dean Kiner - Extra History Music
#https://stackoverflow.com/questions/37490428/unicodeencodeerror-with-csv-writer
with open(path+csvName, 'w', newline='',encoding='UTF-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    for currentRow in polishedPlaylistStatsInfo:
        csvwriter.writerow(currentRow)
        print(currentRow)
