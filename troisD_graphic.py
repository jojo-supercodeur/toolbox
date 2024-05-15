import gpxpy
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from PIL import Image
from scipy.interpolate import interp1d

# Load the image
img_path = "logo_enduraw.png"

def parse_gpx(file_path):
    # Parse the GPX file
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    data = {
        'latitude': [],
        'longitude': [],
        'elevation': [],
        'distance': [],
        'gradient': []
    }

    # Extract data
    prev_elev = 0
    min_elev = 5000
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data['latitude'].append(point.latitude)
                data['longitude'].append(point.longitude)
                data['elevation'].append(point.elevation)
                diff_elev = point.elevation - prev_elev
                prev_elev = point.elevation
                min_elev = min(min_elev, point.elevation)
                if len(data['distance']) == 0:
                    data['distance'].append(0)
                    data['gradient'].append(0)
                else:
                    prev_point = segment.points[len(data['distance']) - 1]
                    dist = point.distance_3d(prev_point)
                    if dist != 0:
                        data['gradient'].append(diff_elev / dist)
                    else:
                        data['gradient'].append(0)
                    data['distance'].append(data['distance'][-1] + dist)

    df = pd.DataFrame(data)

    # Interpolate to smooth the gradients
    num_points = 100
    distance_interp = np.linspace(df['distance'].min(), df['distance'].max(), num_points)
    latitude_interp = interp1d(df['distance'], df['latitude'], kind='linear')(distance_interp)
    longitude_interp = interp1d(df['distance'], df['longitude'], kind='linear')(distance_interp)
    elevation_interp = interp1d(df['distance'], df['elevation'], kind='linear')(distance_interp)
    gradient_interp = interp1d(df['distance'], df['gradient'], kind='linear')(distance_interp)

    smoothed_data = {
        'latitude': latitude_interp,
        'longitude': longitude_interp,
        'elevation': elevation_interp,
        'distance': distance_interp,
        'gradient': gradient_interp
    }

    return pd.DataFrame(smoothed_data), min_elev

def create_3d_plot(gpx_file_path, rotation_speed=10, axis='z', angle_rot = 15):
    df, min_elev = parse_gpx(gpx_file_path)
    fig = go.Figure()

    # Custom colorscale for elevation
    custom_colorscale = [
        [0, 'green'],    # Descents
        [0.25, 'yellow'], # Flat
        [0.5, 'orange'],  # Gentle climbs
        [0.75, 'red'],   # Steep climbs
        [1, 'black']     # Very steep climbs
    ]

    # Add the main track line
    fig.add_trace(go.Scatter3d(
        x=df['longitude'],
        y=df['latitude'],
        z=df['elevation'],
        mode='lines',
        line=dict(
            color=df['elevation'],
            colorscale='Viridis',
            width=2
        ),
        name='Track'
    ))

    # Add the "walls" to the base (altitude 0)
    fig.add_trace(go.Mesh3d(
        x=df['longitude'].tolist() + df['longitude'].tolist(),
        y=df['latitude'].tolist() + df['latitude'].tolist(),
        z=df['elevation'].tolist() + [min_elev - 10]*len(df),
        i=list(range(len(df)-1)) + list(range(len(df), 2*len(df)-1)),
        j=list(range(1, len(df))) + list(range(len(df)+1, 2*len(df))),
        k=list(range(len(df), 2*len(df)-1)) + list(range(1, len(df))),
        intensity=df['gradient'].tolist() + df['gradient'].tolist(),
        colorscale=custom_colorscale,
        opacity=0.5,
        name='Walls'
    ))

    # Add the background image as a surface
    img = Image.open(img_path)
    img = img.resize((2, 2))  # Resize to match the plot grid
    img = np.array(img)

    altitude = min_elev - 10
    fig.add_trace(go.Surface(
        x=[[df['longitude'].min(), df['longitude'].max()], [df['longitude'].min(), df['longitude'].max()]],
        y=[[df['latitude'].min(), df['latitude'].min()], [df['latitude'].max(), df['latitude'].max()]],
        z=[[altitude, altitude], [altitude, altitude]],
        surfacecolor=img[:, :, 0],  # Assuming the image is grayscale; for RGB use a different approach
        cmin=0,
        cmax=255,
        colorscale='gray',
        showscale=False,
        opacity=1
    ))

    # Define animation steps for rotation
    frames = []
    for angle in range(0, 360, rotation_speed):
        if axis == 'x':
            eye = dict(x=2*np.cos(np.radians(angle)), y=0, z=2*np.sin(np.radians(angle)))
        elif axis == 'y':
            eye = dict(x=0, y=2*np.cos(np.radians(angle)), z=2*np.sin(np.radians(angle)))
        else:             
            eye = dict(x=2*np.cos(np.radians(angle)), y=2*np.sin(np.radians(angle)),  z=2*np.sin(np.radians(angle_rot)))
           # eye = dict(x=0, y=2*np.cos(np.radians(angle)), z=2*np.sin(np.radians(angle)))
        frames.append(go.Frame(layout=dict(scene_camera_eye=eye)))

    fig.update_layout(
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            buttons=[dict(label='Play',
                          method='animate',
                          args=[None, dict(frame=dict(duration=100, redraw=True), fromcurrent=True, mode='immediate')])]
        )],
        images=[dict(
            source=img_path,
            xref="paper", yref="paper",
            x=0, y=1,
            sizex=1, sizey=1,
            sizing="stretch",
            opacity=1,
            layer="below"
        )],
        scene=dict(
            xaxis=dict(title='', showbackground=False, showspikes=False, spikesides=False, showticklabels=False, visible = False),
            yaxis=dict(title='', showbackground=False, showspikes=False, spikesides=False, showticklabels=False, visible = False),
            zaxis=dict(title='', nticks=10, range=[min_elev - 10, df['elevation'].max()], showbackground=False, showspikes=False, spikesides=False, showticklabels=False)
        ),
        title='3D Course Profile',
        margin=dict(l=0, r=0, b=0, t=50)
    )

    fig.frames = frames

    #return fig
    fig.show() # for testing

    #©©Cfig.show()

# Example usage
gpx_file_path = 'gpx_race/UTMB.gpx'  # Replace with your GPX file path

create_3d_plot(gpx_file_path, rotation_speed=5, axis='z')
