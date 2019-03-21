# Import dependencies.
import os
import re
import subprocess
import time
import twitter
import mysql.connector
import sentry_sdk
# No private keys or anything, just error reporting.
sentry_sdk.init("https://f2cf247f01154197b525f2130804a7b4@sentry.io/1420501")

try:
    # Configure settings.
    debug = True
    tweet = True
    database = True
    paid_download = 300.0
    paid_upload = 25.0
    paid_location = "INSERT_HERE"
    output_file = 'speedtest.csv'

    # Run speedtest and pipe out results.
    response = subprocess.Popen('speedtest-cli --simple', shell=True, stdout=subprocess.PIPE).stdout.read()

    # Get all necessary data into variables that we can use.
    # Process results using regrex.
    ping = re.findall('Ping:\s(.*?)\s', response, re.MULTILINE)
    download = re.findall('Download:\s(.*?)\s', response, re.MULTILINE)
    upload = re.findall('Upload:\s(.*?)\s', response, re.MULTILINE)
    ping[0] = ping[0].replace(',', '.')
    download[0] = download[0].replace(',', '.')
    upload[0] = upload[0].replace(',', '.')

    # Put information into list.
    data = []
    data.append(str(ping[0]))
    data.append(str(download[0]))
    data.append(str(float(download[0])/8))
    data.append(str(upload[0]))
    data.append(str(float(upload[0])/8))
    if debug:
        print('Ping: ', data[0])
        print('Download (Mbps): ', data[1])
        print('Download (MB/s): ', data[2])
        print('Upload(Mbps): ', data[3])
        print('Upload(MB/s): ', data[4])    

    current_date = time.strftime('%m/%d/%Y')
    current_time = time.strftime('%H:%M:%S')
    rounded_download = round(float(data[1]), 2)
    rounded_upload = round(float(data[3]), 2)
    payment_percentage_sub = ((float(data[2])/int(paid_download))*100)*10
    payment_percentage = round(payment_percentage_sub, 2)

    # Tweet if speeds are not met.
    if tweet:
        api = twitter.Api(consumer_key='INSERT_HERE',
                        consumer_secret='INSERT_HERE',
                        access_token_key='INSERT_HERE',
                        access_token_secret='INSERT_HERE')
        update = "@GetSpectrum @Ask_Spectrum - I'm paying for " + str(int(paid_download)) + "/" + str(int(paid_upload)) + " but I'm only getting " + str(rounded_download) +"/" + str(rounded_upload) + " right now in " + str(paid_location) + ". What if I only pay " + str(payment_percentage) + " percent of my bill this month and see how you like it?"
        if debug:
            print('Tweet:', update)
        status = api.PostUpdate(update)

    # Write data to database.
    if database:
        mydb = mysql.connector.connect(
        host="INSERT_HERE",
        user="INSERT_HERE",
        passwd="INSERT_HERE",
        database="INSERT_HERE"
        )
        mycursor = mydb.cursor()
        sql = "INSERT INTO speeds (date, time, ping, download_mbps, download_real, upload_mbps, upload_real) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (current_date, current_time, data[0], data[1], data[2], data[3], data[4])
        mycursor.execute(sql, val)
        mydb.commit()
        if debug:
            records = str(mycursor.rowcount)
            print("Database:", "" + records + " record inserted!")
except Exception as e:
    sentry_sdk.capture_exception(e)