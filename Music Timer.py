'''
This program generates a music playlist of a certain duration.
'''

from random import shuffle
from objc_util import *
from console import clear

length = '20:00'

# Margin of error, how far away the length of the 
# playlist created is allowed to be from the specified length
error = 2  

minSongs = 1
maxSongs = 5
include = ['Africa', 'Every Breath You Take']
artists = ['Toto', 'The Police', 'Def Leppard']
playlist = '80s'

TIME_DIGITS = 2
	
	
def getT(t):
	if t >= 3600:
		hours = int(t / 3600)
		minutes = int((t % 3600) / 60)
		seconds = int(t % 60)
		centiseconds = (t % 1) * (10 ** TIME_DIGITS)
		return ('%s:%02d:%02d.%0' + str(TIME_DIGITS) + 'd') % (hours, minutes, seconds, centiseconds)
	if t >= 60:
		minutes = int(t / 60)
		seconds = int(t % 60)
		centiseconds = (t % 1) * (10 ** TIME_DIGITS)
		return ('%s:%02d.%0' + str(TIME_DIGITS) + 'd') % (minutes, seconds, centiseconds)
	else:
		return ('%.0' + str(TIME_DIGITS) + 'f') % t
		
		
# Load the queey (list of available songs)
MPMediaQuery = ObjCClass('MPMediaQuery')

if playlist:
	playlistQuery = MPMediaQuery.playlistsQuery()
	for p in playlistQuery.collections():
		if str(p.valueForKey_('name')) == playlist:
			query = p
			break
			
	else:
		raise ValueError('Playlist %s was not found!' % playlist)
		
else:
	query = MPMediaQuery.songsQuery()
		
		
print('Generating playlist...')

# Change length and error to min and max length:
# Ex. if length = '10:00' and error = 5, make min = 595 and max = 605
l = 0
length = length.split(':')
assert len(length) < 4
for i in length:
	l *= 60
	l += int(i)
	
min = l - error
max = l + error

# Generate playlist
oldPlaylist = []
oldDuration = 0
oldItems = list(i for i in query.items())
for name in include:
	for song in oldItems:
		if str(song.valueForKey_('title')) == name:
			oldPlaylist.append(song)
			oldItems.remove(song)
			oldDuration += float(str(song.valueForKey_('playbackDuration')))
items = list(oldItems)
playlist = list(oldPlaylist)

duration = oldDuration
shuffle(items)
while duration < min or len(playlist) < minSongs:
	try:
		song = items.pop()
	except IndexError:
		raise ValueError('No songs match the requirements')
	if artists and str(song.valueForKey_('artist')) not in artists:
		continue
	playlist.append(song)
	duration += float(str(song.valueForKey_('playbackDuration')))
	if duration > max or len(playlist) > maxSongs:
		duration = oldDuration
		items = list(oldItems)
		playlist = list(oldPlaylist)
		shuffle(items)
		
shuffle(playlist)

# Display playlist
clear()
print('Generated playlist, %s length:' % getT(duration))
print('=' * 40)
for i, item in enumerate(playlist):
	print(str(i + 1) + '. ' + str(item.valueForKey_('title')) + ' - ' + str(item.valueForKey_('artist')) + ' (' + getT(float(str(item.valueForKey_('playbackDuration')))) + ')')
	

# Play the playlist with the help of the objc_util module
MPMediaItemCollection = ObjCClass('MPMediaItemCollection')
items = MPMediaItemCollection.collectionWithItems_(playlist)

MPMusicPlayerController = ObjCClass('MPMusicPlayerController')
musicPlayer = MPMusicPlayerController.iPodMusicPlayer()

musicPlayer.setShuffleMode(1)
musicPlayer.setQueueWithItemCollection_(items)
musicPlayer.play()
