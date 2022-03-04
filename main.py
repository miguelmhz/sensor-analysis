from flask import Flask, render_template, request, redirect, url_for
import os
from os.path import join, dirname, realpath

app = Flask(__name__)

# enable debugging mode
app.config["DEBUG"] = True

# Upload folder
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER


# Root URL
@app.route('/')
def index():
     # Set The upload HTML template '\templates\index.html'
    return render_template('index.html')


def analisis(path):
    import pandas as pd
    import math
    # SCD30_Rpi1
    # Aranet4
    data = pd.read_csv(path)
    if "_id" in data:
        data.pop('_id') 
    if "Sensor" in data:
        data.pop('Sensor') 
    data = data.rename(columns={'Temp_C': 'Temperature(°C)', 'HR_%': 'Relative humidity(%)', 'Tiempo': 'Time','CO2(PPM)':'Carbon dioxide(ppm)', 'Temp_C':'Temperature(°C)' })

    if (type(data['Time'][1]) == str ):
        data['Time'] = pd.to_datetime(data['Time'])
    else:
        data['Time'] = pd.to_datetime(data['Time'], unit='ms')

    res = {}
    res['day']= []
    res['hour_by_day'] = []
    for day in range(31):
        for hour in range(24):
            dayData = {}

            mean = data[  (data['Time'].dt.day == day) & (data['Time'].dt.hour == hour)  ].mean().to_dict()
            sd = data[(data['Time'].dt.day == day) & (data['Time'].dt.hour == hour) ].std().to_dict()
            max = data[(data['Time'].dt.day == day) & (data['Time'].dt.hour == hour) ].max().to_dict()
            min = data[(data['Time'].dt.day == day) & (data['Time'].dt.hour == hour) ].min().to_dict()
            if "Time" in mean:
                mean.pop('Time') 
            if "Time" in sd:
                sd.pop('Time') 
            if "Time" in max:
                max.pop('Time') 
            if "Time" in min:
                min.pop('Time') 
                
            

            if ( math.isnan(mean['Carbon dioxide(ppm)'])  ):
                continue
            else:
                for key in max:

                    dayData['day']=day
                    dayData['hour']=hour
                    dayData['max'+'-'+key]=max[key]
                    dayData['min'+'-'+key]=min[key]
                    dayData['mean'+'-'+key]=mean[key]
                    dayData['sd'+'-'+key]=sd[key]
                
                res['hour_by_day'].append(dayData)
                
    #print(res['day'])
    import csv
    keys = res['hour_by_day'][0].keys()
    path = os.path.join(app.config['UPLOAD_FOLDER'] , 'by_hours.csv')
    with open(path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(res['hour_by_day'])

    for day in range(31):
        dayData = {}
        mean = data[(data['Time'].dt.day == day) ].mean()
        mean = data[(data['Time'].dt.day == day) ].mean().to_dict()
        sd = data[(data['Time'].dt.day == day) ].std().to_dict()
        max = data[(data['Time'].dt.day == day) ].max().to_dict()
        min = data[(data['Time'].dt.day == day) ].min().to_dict()
        if "Time" in mean:
                mean.pop('Time') 
        if "Time" in sd:
            sd.pop('Time') 
        if "Time" in max:
            max.pop('Time') 
        if "Time" in min:
            min.pop('Time') 
        if ( math.isnan(mean['Carbon dioxide(ppm)'])  ):
            continue
        else:
            for key in max:
                dayData['day']=day
                dayData['max'+'-'+key]=max[key]
                dayData['min'+'-'+key]=min[key]
                dayData['mean'+'-'+key]=mean[key]
                dayData['sd'+'-'+key]=sd[key] 

            res['day'].append(dayData)

    keys = res['day'][0].keys()
    path = os.path.join(app.config['UPLOAD_FOLDER'] , 'days.csv')
    with open(path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(res['day'])
    #print( type(res) )
    return res


# Get the uploaded files
@app.route("/", methods=['POST'])
def uploadFiles():
      # get the uploaded file
      uploaded_file = request.files['file']
      if uploaded_file.filename != '':
           file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
          # set the file path
           uploaded_file.save(file_path)
          # save the file
           data = analisis(file_path)
    
      
      #return data
      return render_template('index.html', data=data, files=True)
      #return redirect(url_for('index'))

if (__name__ == "__main__"):
     app.run(port = 5001)
