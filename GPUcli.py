#!/usr/bin/python
import oauthlib, json, argparse, time, os
from requests_oauthlib import OAuth2Session

version = "1.0"

# Define client_id und client_secret created by the google api console.
client_id = ''
client_secret = ''

redirect_uri = 'https://localhost'

# Define the scope of this app.
scope = ['https://www.googleapis.com/auth/userinfo.email',
         'https://www.googleapis.com/auth/userinfo.profile',
         'https://www.googleapis.com/auth/photoslibrary']

# Function: Debug output.
def debug(message):
    debugmsg = "DEBUG: " + message

    if args.debug == True:
        try:
            f = open('debug.log', 'w')
            f.write(debugmsg)
            f.close()
        finally:
            print debugmsg

# Function: load token from file.
def load_token():
    try:
        f = open('token.dat', 'r')
        token = json.loads(f.read())
        f.close()
    except:
        token = ""

    debug("Token loaded from file: " + str(token))

    return token


# Function: save token to file.
def save_token(token):
    try:
        f = open('token.dat', 'w')
        f.write(json.dumps(token))
        f.close()
    except Exception, e:
        print "ERROR: Failed to save token data! " + str(e)
    debug("Token saved to file: " + str(token))


# Function: Check for expired access_token.
def check_token():
    unixtime = time.time()

    if(unixtime + 600 > oauth.token['expires_at']):
        debug('access_token expired. Refreshing...')
        refresh_token()

# Function: Authorize against google user account.
def auth_app():
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri,
                          scope=scope)
    authorization_url, state = oauth.authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        access_type="offline", prompt="consent")

    print "Please authorize access for this app at:"
    print
    print authorization_url
    print

    print 'Afterwards google will reqirect you to an URL.'
    authorization_response = raw_input('Please enter the full URL: ')

    try:
        token = oauth.fetch_token(
            'https://accounts.google.com/o/oauth2/token',
            authorization_response=authorization_response,
            client_secret=client_secret)
    except Exception, e:
        print "ERROR: Failed to fetch access token! " + str(e)
        exit(-1)

    # Save fetched token to data file for further use.
    save_token(token)

    return token

# Function: Refresh access_token
def refresh_token():
    extra = {
        'client_id': client_id,
        'client_secret': client_secret,
    }
    oauth.refresh_token('https://accounts.google.com/o/oauth2/token', **extra)
    save_token(oauth.token)

# Function: Check API result for critical error messages.
def checkAPIresult(apiresult, message):
    debug("API result: " + str(apiresult))

    if 'error' in apiresult:
        print "ERROR: " + message
        print apiresult['error']['status'] + ": " + apiresult['error']['message']
        print "Exiting..."
        print
        exit(-1)

    if 'message' in apiresult:
        print "ERROR: " + message
        print apiresult['message']
        print "Exiting..."
        print
        exit(-1)

# Function: Fetch user informations.
def getUserInfo():
    check_token()
    r = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo')
    return json.loads(r.text)

# Function: Create album
def g_createAlbum(title):
    album = {"album": {"title": title}}

    try:
        check_token()
        r = oauth.post('https://photoslibrary.googleapis.com/v1/albums', json=album)
        checkAPIresult(json.loads(r.text), 'Failed to create album!')
    except Exception, e:
        print "ERROR: Failed to create album! " + str(e)
        exit(-1)

    return json.loads(r.text)

# Function: Upload file to google photos.
def g_uploadMedia(file, filename):
    check_token()
    headers = {'Content-type': 'application/octet-stream',
               'X-Goog-Upload-File-Name': filename,
               'X-Goog-Upload-Protocol': 'raw'}

    try:
        debug("Uploading with set headers: " + str(headers))
        f = open(file, 'rb')
        r = oauth.post('https://photoslibrary.googleapis.com/v1/uploads', data=f.read(), headers=headers)
        f.close()
    except Exception,e :
        print "ERROR: Failed to upload file! " + str(e)
        exit(-1)

    try:
        checkAPIresult(json.loads(r.text), 'Failed to upload file!')
    finally:
        return r.text

# Function: Create mediaitem from uploaded file.
def g_createMediaItems(upload_list, albumid=None):
    check_token()
    media_list = []
    for media in upload_list:
        item = {'description': media.values()[0],
                'simpleMediaItem': {'uploadToken': media.keys()[0]}}
        media_list.append(item)

    if albumid is None:
        newmediaitems = {'newMediaItems': media_list}
    else:
        newmediaitems = {'albumId': albumid, 'newMediaItems': media_list}

    try:
        debug("Commit post: " + newmediaitems)
        r = oauth.post('https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate', json=newmediaitems)
        checkAPIresult(json.loads(r.text), 'Failed to commit mediaitems!')
    except Exception, e:
        print "ERROR: Failed to create mediaitem! " + str(e)
        exit(-1)

    apiresult = json.loads(r.text)
    if 'error' in apiresult:
        print "ERROR: Failed create media items!"
        print apiresult['error']['status'] + ": " + apiresult['error']['message']
        print "Exiting..."
        print
        exit(-1)

    return apiresult

########
# MAIN #
########
parser = argparse.ArgumentParser(
    description='Use GPUcli to upload media to google photos by command line.',
    epilog='ex. ./GPUcli.py <directory>')
parser.add_argument('directory', help='Directory to upload.')
parser.add_argument('-a', '--album', help='Create an album and add the uploaded. Album will be named by the <directory>.',
    action='store_const', const=True)
parser.add_argument('-d', '--debug', help='Enable the more verbose debug output.',
    action='store_const', const=True)
args = parser.parse_args()

debug('Starting main functions...')

# Recover token data from file.
token = load_token()

# Token data not found.
if token == "":
    token = auth_app()

# Start with a valid token.
debug("Creating OAuth2Session with access_token")
oauth = OAuth2Session(client_id, token=token)
check_token()

try:
    debug("Fetching userinformations using: getUserInfo()")
    userinfo = getUserInfo()
except Exception, e:
    print "ERROR: Failed to log in! " + str(e)
    exit(-1)

print "Google Photos Upload - CLI Script V" + version
print
print "Hi " + userinfo['given_name'] + ", we're successfully logged in! Starting your requested action!"
print

path = os.path.abspath(args.directory)

# Check the source directory.
if not os.path.isdir(path):
    print "ERROR: Source directory does not exist!"
    exit(-1)

# Find foldername of media.
folder = path.split(os.sep)[-1]
if folder == "":
    folder = "root"
print "Uploading pictures from directory: " + path
if args.album == True:
    print "Using this folder name for album creating: " + folder
print

# Look at directory and identify files to upload.
files = os.listdir(path)
uploads = []
for file in files:
    filepath = path + '/' + file

    debug("Checking if this file can be uploaded: " + file)
    if not os.path.isdir(filepath) and not file.startswith('.'):
        print "Uploading... " + filepath
        upload_token = g_uploadMedia(filepath, file)
        uploads.append({upload_token: file})

if len(uploads) > 0:
    debug('Media uploaded. Ready to commit the media.')
    albumid = None

    # Create album if commandline argument is given.
    if args.album == True:
        print "Creating album: " + folder
        albumid = g_createAlbum(folder)
        albumid = albumid['id']

    # Finally add commit uploads to google photos (max 50/commit)
    upload_ok = True
    item_count = 0
    sum_count = 0
    upload_charge = []
    for upload_item in uploads:
        upload_charge.append(upload_item)
        item_count = item_count + 1
        sum_count = sum_count + 1

        if item_count == 50 or sum_count == len(uploads):
            debug("Mediaobjects to commit: " + upload_charge)
            upload_results = g_createMediaItems(upload_charge, albumid)
            debug("Upload results: " + upload_results)
            for result in upload_results['newMediaItemResults']:
                if result['status']['message'] != "OK":
                    print result['mediaItem']['filename'] + ": " + result['status']['message']
                    upload_ok = False
            item_count = 0
            upload_charge = []

    if upload_ok == True:
        print "Media successfully uploaded!"
    else:
        print "Media could not be uploaded without errors! Failed!"
else:
    print "ERROR: No media uploaded!"
