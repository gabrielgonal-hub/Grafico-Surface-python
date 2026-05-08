import numpy as np
from scipy.interpolate import griddata

# Tu tabla
data = np.array([
[-0.020,-0.023,-0.027,-0.022,-0.026,-0.023,-0.029,-0.024,-0.025,-0.024],
[-0.022,-0.024,-0.029,-0.024,-0.027,-0.025,-0.031,-0.026,-0.027,-0.024],
[-0.024,-0.033,-0.044,-0.017,-0.039,-0.027,-0.043,-0.038,-0.026,-0.020],
[-0.024,-0.033,-0.045,-0.015,-0.038,-0.026,-0.041,-0.039,-0.024,-0.017],
[-0.031,-0.031,-0.035,-0.022,-0.030,-0.020,-0.035,-0.035,-0.025,-0.027],
[-0.032,-0.031,-0.037,-0.024,-0.031,-0.022,-0.037,-0.036,-0.028,-0.027],
[-0.016,-0.026,-0.038,-0.022,-0.037,-0.030,-0.042,-0.030,-0.030,-0.022],
[-0.016,-0.027,-0.038,-0.020,-0.037,-0.030,-0.041,-0.030,-0.029,-0.020]
])

machine_values = np.array([
-0.015,
-0.022,
-0.013,
-0.023,
-0.021,
-0.021,
-0.021,
-0.014,
-0.022,
-0.014
])

x = np.arange(-6,7)
y = np.arange(6,-7,-1)   # <- Y invertido coherente con tu decisión
X, Y = np.meshgrid(x,y)

def crear_cruz(valores):
    Z = np.full((13,13), np.nan)
    c = 6

    # Y+
    # Z[c-5,c] = valores[]
    Z[c-4,c] = valores[0]
    Z[c-3,c] = valores[1]

    # Y-
    Z[c+3,c] = valores[2]
    Z[c+4,c] = valores[3]
    # Z[c+5,c] = valores[]

    # X-
    # Z[c,c-5] = valores[]
    Z[c,c-4] = valores[4]
    Z[c,c-3] = valores[5]

    # X+
    Z[c,c+3] = valores[6]
    Z[c,c+4] = valores[7]
    # Z[c,c+5] = valores[]

    return Z

import plotly.graph_objects as go
import numpy as np
from scipy.interpolate import griddata
import pandas as pd
from IPython.display import HTML
import plotly.io as pio

fig = go.Figure()

# Creamos todas las piezas
for pieza in range(10):
    valores = data[:,pieza]
    Z_base = crear_cruz(valores)

    points = np.array([
        (X[i,j],Y[i,j])
        for i in range(13)
        for j in range(13)
        if not np.isnan(Z_base[i,j])
    ])
    values = np.array([
        Z_base[i,j]
        for i in range(13)
        for j in range(13)
        if not np.isnan(Z_base[i,j])
    ])

    # Z_cubic = griddata(points, values, (X, Y), method='cubic')
    # Z_nearest = griddata(points, values, (X, Y), method='nearest')

    # Z_interp = np.where(np.isnan(Z_cubic), Z_nearest, Z_cubic)

    Z_interp = griddata(points, values, (X, Y), method='cubic')

    radius_exterior = 6
    radius_interior = 2
    R = np.sqrt(X**2 + Y**2)
    mask = (R > radius_exterior) | (R < radius_interior)
    Z_interp[mask] = np.nan

    rows, cols = Z_interp.shape
    vertices = []
    index_map = -np.ones_like(Z_interp, dtype=int)

    counter = 0
    for i in range(rows):
        for j in range(cols):
            if not np.isnan(Z_interp[i,j]):
                vertices.append([X[i,j], Y[i,j], Z_interp[i,j]])
                index_map[i,j] = counter
                counter += 1

    vertices = np.array(vertices)

    i_list, j_list, k_list = [], [], []

    for i in range(rows-1):
        for j in range(cols-1):
            idx0 = index_map[i,j]
            idx1 = index_map[i,j+1]
            idx2 = index_map[i+1,j]
            idx3 = index_map[i+1,j+1]

            if idx0>=0 and idx1>=0 and idx2>=0:
                i_list.append(idx0)
                j_list.append(idx1)
                k_list.append(idx2)
            if idx1>=0 and idx3>=0 and idx2>=0:
                i_list.append(idx1)
                j_list.append(idx3)
                k_list.append(idx2)
            else:
                if idx0>=0 and idx1>=0 and idx3>=0:
                    i_list.append(idx0)
                    j_list.append(idx1)
                    k_list.append(idx3)
                if idx0>=0 and idx3>=0 and idx2>=0:
                    i_list.append(idx0)
                    j_list.append(idx3)
                    k_list.append(idx2)
    
    fig.add_trace(go.Mesh3d(
        x=vertices[:,0],
        y=vertices[:,1],
        z=vertices[:,2],
        intensity=vertices[:,2],
        colorscale=[
            [0.0,"red"],
            [0.05,"yellow"],
            [0.5,"green"],
            [0.95,"yellow"],
            [1.0,"red"],
        ],
        cmin=-0.03,
        cmax=0,
        showscale=True,
        i=i_list,
        j=j_list,
        k=k_list,
        visible=(pieza==0),
        name=f"Pieza {pieza+1}"
    ))

    z_machine = machine_values[pieza]

    fig.add_trace(go.Mesh3d(
        x=[-5,5,5,-5],
        y=[-5,-5,5,5],
        z=[z_machine]*4,
        color='magenta',
        opacity=0.4,
        visible=(pieza==0),
        name=f"Máquina {pieza+1}"
    ))

# --- Creamos botones para dropdown ---
buttons = []
for i in range(10):
    visible_array = [False]*20
    
    visible_array[2*i] = True      # superficie
    visible_array[2*i+1] = True    # plano máquina

    buttons.append(
        dict(
            label=f"Pieza {i+1}",
            method="update",
            args=[{"visible": visible_array},
                  {"title": f"Pieza {i+1}"}]
        )
    )

# --- Creamos steps para slider (usando la misma lógica de visible que los botones) ---
steps = []
for i in range(10):

    visible_array = [False] * 20   # 2 traces × 10 piezas
    visible_array[2*i] = True      # superficie
    visible_array[2*i+1] = True    # plano máquina
    
    steps.append(dict(
        method="update",
        args=[{"visible": visible_array},
              {"title": f"Pieza {i+1}",
               # Esto sincroniza el dropdown visualmente
               "updatemenus":[{
                   "active": i,
                   "buttons": buttons,
                   "direction":"down",
                   "showactive":True,
                   "x":0.1,
                   "y":1.15
               }]}],
        label=f"{i+1}"
    ))

sliders = [dict(
    active=0,
    currentvalue={"prefix":"Pieza: "},
    pad={"t":50},
    steps=steps
)]

fig.update_layout(
    updatemenus=[dict(
        buttons=buttons,
        direction="down",
        showactive=True,
        x=0.1,
        y=1.15
    )],
    sliders=sliders,
    scene=dict(
        xaxis=dict(range=[-6,6]),
        yaxis=dict(range=[-6,6]),
        zaxis=dict(range=[-0.046,0.01]),
        aspectratio=dict(x=1,y=1,z=0.7)
    ),
    title="Pieza 1"
)

html_str = pio.to_html(fig, include_plotlyjs='cdn')
HTML(html_str)

pio.write_html(fig, "BushStopperSurface.html","w", include_plotlyjs='include')
print("Archivo guardado como BushStopperSurface.html")
