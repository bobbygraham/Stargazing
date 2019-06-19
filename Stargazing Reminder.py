import requests
from datetime import datetime
from pytz import timezone as tz
import astral
import ephem


#Ideal stargazing conditions
cloud_max = 10 #percent cloud cover
humid_max = 60 #percent humidty

#Stargazing destinations given as Lat/Long tuple
houston_tx = (29.7604, -95.3698, 'Houston, TX', 'US/Central')
weimar_tx = (29.7030, -96.7805, 'Weimar, TX', 'US/Central')
jasper_tx = (30.9202, -93.9966, 'Jasper, TX', 'US/Central')
fredricksburg_tx = (30.2752, -98.8720, 'Fredricksburg, TX', 'US/Central')
rapidcity_sd = (44.0805, -103.2310, 'Rapid City, SD', 'US/Mountain')
cities = [houston_tx, weimar_tx, jasper_tx, fredricksburg_tx, rapidcity_sd]

#Define function for converting Lat/Long from decimal to Deg/Min/Sec
def decdeg2dms(dd):
    mnt,sec = divmod(dd*3600,60)
    deg,mnt = divmod(mnt,60)
    return deg,mnt,sec

output = ''
lbreak = '\n'
any_conditions = False

#Loop will run for each stargazing destination
for j in range(0,len(cities)):

    #5-day forcast for destination
    api_address = 'http://api.openweathermap.org/data/2.5/forecast?APPID=5ad3dd984eddc1becd4d6b826eb0022c&units=imperial&lat='
    url = api_address + str(cities[j][0]) + '&lon=' + str(cities[j][1])
    json_data = requests.get(url).json()


    #Create astral location for stargazing destination
    #This will be used to determine daylight hours
    l = astral.Location((cities[j][2], 'region', cities[j][0], cities[j][1], 'US/Central', 0))
    #Location for ephem module
    location = ephem.Observer()
    location.pressure = 0
    location.lat, location.lon = str(cities[0][0]), str(cities[0][1])  #Handles degrees as string
    #Timezone for each city used to offset UTC time
    timezone = tz(cities[j][3])


    #Create a list for times when all conditions are met
    for i in range(0,39):
        #Pull weather info from json data
        cloud = (json_data['list'][i]['clouds']['all'])
        dt = (json_data['list'][i]['dt'])
        temp = (json_data['list'][i]['main']['temp'])
        humid = (json_data['list'][i]['main']['humidity'])
        #Solar info at dt time
        time = datetime.fromtimestamp(dt, timezone)
        sun = l.sun(time, local=True)
        #Check if it is daylight
        isdaylight = sun['dawn'] < time < sun['dusk']
        #Put datetime in format feed-able to ephem.Moon()
        location.date = datetime.utcfromtimestamp(dt).strftime('%Y/%m/%d %H:%M')
        #Use ephem.Moon() to find time of next moonrise and moonset
        next_moonrise = location.next_rising(ephem.Moon())
        next_moonset = location.next_setting(ephem.Moon())
        #Convert from ephem date to datetime
        next_moonrise = next_moonrise.datetime()
        next_moonset = next_moonset.datetime()
        #Add timezone to datetime
        next_moonrise = timezone.localize(next_moonrise)
        next_moonset = timezone.localize(next_moonset)
        #Check if moon is up
        moon_up = next_moonrise > next_moonset
        #Check if conditions at dt time are suitable for stargzing
        good_conditions = (cloud < cloud_max and humid < humid_max and not moon_up and not isdaylight) 
        if good_conditions:
            line1 = ('Stargazing conditions are ideal in ' + cities[j][2] + ' at ' + time.strftime('%m-%d-%Y %H:%M %Z') + '.')
            line2 = ('....Cloud Coverage will be ' + str(cloud) + '%.')
            line3 = ('....Temperature will be ' + str(temp) + 'F.')
            line4 = ('....Humidity will be ' + str(humid) + '%.')
            output = output + line1 + lbreak + line2 + lbreak + line3 + lbreak + line4 + lbreak
            any_conditions = True

if any_conditions:
    import smtplib
    import datetime
    from email.mime.text import MIMEText
    import json

    #reads credentials (i.e. gmail username and password) from local .json file
    credentials = open('credentials.json').read()
    credentials = json.loads(credentials)
    username = credentials['username']
    password = credentials['password']
    to  = credentials['to']
    header = 'Stargazing Report ' + datetime.datetime.now().strftime('%m-%d-%Y')
    output = header + lbreak + lbreak + output
    msg = MIMEText(output)
    msg['Subject'] = 'Stargazing Report ' + datetime.datetime.now().strftime('%m-%d-%Y')
    msg['From'] = username
    msg['To'] = to

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.ehlo()
    server.login(username, password)
    server.sendmail(username, to, msg.as_string())
    server.quit()
    print(output)
else:
    lasttime = datetime.fromtimestamp(dt, tz('US/Central')).strftime('%Y/%m/%d %H:%M %Z')
    print('No favorable stargazing conditions between now and ' + lasttime + '.')
