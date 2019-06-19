# Stargazing
This program searches for favorable stargazing conditions (including cloud coverage, humidity, darkness, and position of the moon)in a list of locations. If favorable conditions are found, it emails the user of the location and time.

The user will need to feed the program a credentials.json file which provides a username and password for a sender gmail account, as well as a receiving email account. The file credentials.json will be in the following format:
{"username": "sender@gmail.com", "password": "senderpassword", "to": "receiver@gmail.com"}

The user can personalize the program by modifying the cities list. The list is built of tuples in the format:
example_city = (latitiude-float , longtiude-float, cityname-string, timezone-string)
Where timezone must be selected from available timezones in pytz.

The user can also personalize the minimum acceptable conditions for stargazing in lines 9 and 10. Default conditions are:
cloud_max = 10 #percent cloud cover
humid_max = 60 #percent humidty

Finally, user can choose to accept conditions that ignore the position of the moon. Simply remove "...and not moon_up..." from line 76. Be aware that the moon can affect visibility of certain constellations. 
