from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import folium
import contextily
import geopandas as gpd
import pandas as pd
import io
from flask import Flask, render_template, send_file, make_response, url_for, Response, request, redirect
app = Flask(__name__)
import re


lakes = gpd.read_file('zip/lakes.zip')
province = gpd.read_file('zip/Province.zip').to_crs(epsg=4326)
regioni = gpd.read_file('zip/Regioni.zip').to_crs(epsg=4326)
quartieri = gpd.read_file('zip/quartieri_milano.zip')
data = pd.read_excel('dati2021.xlsx')




@app.route('/', methods=['GET'])
def home():
    
    return render_template('home.html', data = data.to_html())

@app.route('/risp', methods=['GET'])
def risp():
  if request.args['sel'] == 'nluoghigiud':
    return redirect(url_for("nluoghigiudizio"))
  if request.args['sel'] == 'nluoghigiudper':
    return redirect(url_for("nluoghigiudizioper"))
  if request.args['sel'] == 'nluoghigiudgrafico':
    return redirect(url_for("nluoghigiudiziografico"))
  if request.args['sel'] == 'luoghispiaggia':
    return redirect(url_for("luoghispiaggia"))
  if request.args['sel'] == 'mappalombpunti':
    return redirect(url_for("mappa"))
  if request.args['sel'] == 'mappalombpuntigiud':
    return redirect(url_for("mappagiudizio"))
  if request.args['sel'] == 'mappautente':
    return redirect(url_for("mappautente"))
  if request.args['sel'] == 'laghiutente':
    return redirect(url_for("laghiutente"))
  if request.args['sel'] == 'legenda':
    return redirect(url_for("test"))
  return render_template(home.html)



@app.route('/nluoghigiudizio', methods=['GET'])
def nluoghigiudizio():
  data2 = pd.DataFrame(data.groupby("giudizio")["punto"].count().sort_values(ascending = False))
  return render_template('result.html' , data2=data2.to_html())


@app.route('/nluoghigiudizioper', methods=['GET'])
def nluoghigiudizioper():
  data2 = pd.DataFrame(data.groupby("giudizio")["punto"].count().sort_values(ascending = False))
  data2 = pd.DataFrame(100 * data2['punto'].count() / data2.groupby('giudizio')['punto'].transform('sum'))
  return render_template('result.html' , data2=data2.to_html())

@app.route('/nluoghigiudiziografico', methods=['GET'])
def nluoghigiudiziografico():

  fig, ax = plt.subplots(figsize = (12,8))
  fig = plt.figure(figsize = (12,12))
  ax = plt.axes()
  plt.rcParams.update({"font.size" : 13})
  ax.pie(data.groupby("giudizio")['punto'].count(), labels = data["giudizio"], autopct = "%.1f%%", startangle = 90)
  #ax.pie(df5.values, labels = df5.index, autopct = "%.1f%%", startangle = 90) #se non si usa as_index nel df5
  plt.show()
  contextily.add_basemap(ax=ax)
  output = io.BytesIO()
  FigureCanvas(fig).print_png(output)
  return Response(output.getvalue(), mimetype='image/png')



@app.route('/luoghispiaggia', methods=['GET'])
def luoghispiaggia():
  data2 = pd.DataFrame(data[data['punto'].str.contains('spiaggia', flags=re.IGNORECASE, regex=True)]['punto'])
  return render_template('result.html' , data2=data2.to_html())


data = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.longitude, data.latitude))
data['latitude'] = data['geometry'].x
data['longitude'] = data['geometry'].y
regionic = regioni[regioni['DEN_REG']== 'Lombardia']
datac = pd.DataFrame(data[data.intersects(regionic.unary_union)])
@app.route('/mappa', methods=['GET'])
def mappa():
  m = folium.Map(location=[45.46220047218434, 9.191121737490482],zoom_start=8, tiles='openstreetmap')  # CartoDB positron
  
  for _, row in datac.iterrows():
            folium.Marker(
                location=[row["longitude"], row["latitude"]],
                popup=row['punto'],
                icon=folium.map.Icon(color='green')
            ).add_to(m)
  for _, r in regioni[regioni['DEN_REG']=='Lombardia'].iterrows():
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {'fillColor': 'blue'})
    folium.Popup(r['DEN_REG']).add_to(geo_j)
    geo_j.add_to(m)
  return render_template('result.html',  map=m._repr_html_())


@app.route('/mappagiudizio', methods=['GET'])
def mappagiudizio():
  m = folium.Map(location=[45.46220047218434, 9.191121737490482],zoom_start=8, tiles='openstreetmap')  # CartoDB positron
  
  for _, row in datac.iterrows():
            folium.Marker(
                location=[row["longitude"], row["latitude"]],
                popup=row['giudizio'],
                icon=folium.map.Icon(color='green')
            ).add_to(m)
  for _, r in regioni[regioni['DEN_REG']=='Lombardia'].iterrows():
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {'fillColor': 'blue'})
    folium.Popup(r['DEN_REG']).add_to(geo_j)
    geo_j.add_to(m)
  return render_template('result.html',  map=m._repr_html_())

@app.route('/mappautente', methods=['GET'])
def mappautente():
  
  return render_template('mappautente.html', regioni=regioni['DEN_REG'])



@app.route('/rispmappautente', methods=['GET'])
def rispmappautente():
  m = folium.Map(location=[43.049849, 12.452571],zoom_start=6, tiles='openstreetmap')  # CartoDB positron
  regioniu = regioni[regioni['DEN_REG']== request.args['regione']]
  datac = pd.DataFrame(data[data.intersects(regioniu.unary_union)])
  for _, row in datac.iterrows():
            folium.Marker(
                location=[row["longitude"], row["latitude"]],
                popup=row['giudizio'],
                icon=folium.map.Icon(color='green')
            ).add_to(m)
  for _, r in regioniu.iterrows():
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {'fillColor': 'blue'})
    folium.Popup(r['DEN_REG']).add_to(geo_j)
    geo_j.add_to(m)
  return render_template('result.html', map=m._repr_html_())

lakesc = lakes[lakes.intersects(regioni.unary_union)]
@app.route('/laghiutente', methods=['GET'])
def laghiutente():
  
  return render_template('laghiutente.html', lakesc=lakesc['LAKE_NAME'])




@app.route('/risplaghiutente', methods=['GET'])
def risplaghiutente():
  m = folium.Map(location=[43.049849, 12.452571],zoom_start=6, tiles='openstreetmap')  # CartoDB positron

  lakesc = lakes[lakes.intersects(regioni.unary_union)]
  lakesc = lakesc[lakesc['LAKE_NAME']== request.args['lago']]
  
  for _, r in lakesc.iterrows():
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {'fillColor': 'blue'})
    folium.Popup(r['LAKE_NAME']).add_to(geo_j)
    geo_j.add_to(m)
  pointlakes = pd.DataFrame(data[data.intersects(lakesc.unary_union)])
  for _, row in pointlakes.iterrows():
            folium.Marker(
                location=[row["longitude"], row["latitude"]],
                popup=row['giudizio'],
                icon=folium.map.Icon(color='green')
            ).add_to(m)
  return render_template('result.html', map=m._repr_html_())



@app.route('/test', methods=['GET'])
def test():
  ax = province[province.intersects(data.unary_union)].to_crs(3857).plot(figsize=(20,20),edgecolor='k', column='geometry',legend=True, alpha=0.5, cmap='OrRd')
  ctx.add_basemap(ax)
  output = io.BytesIO()
  FigureCanvas(fig).print_png(output)
  return Response(output.getvalue(), mimetype='image/png')
  #return render_template('result.html',  map=m._repr_html_())


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)