import plotly.graph_objects as go
import numpy as np
import pandas as pd
from IPython.display import HTML
import plotly.io as pio

fig = go.Figure()

# Ejemplo de matriz de datos
# data.shape = (81, 10) para 9x9 y 10 piezas
# data = np.random.uniform(-0.03, 0, (81,10))  # ejemplo

# Tu tabla
data = np.array([
[-0.024,-0.021,-0.020,-0.021,-0.025,-0.026,-0.022,-0.022,-0.024,-0.021],
[-0.026,-0.022,-0.021,-0.025,-0.027,-0.026,-0.024,-0.022,-0.025,-0.022],
[-0.028,-0.026,-0.022,-0.027,-0.029,-0.029,-0.029,-0.024,-0.027,-0.024],
[-0.016,-0.014,-0.009,-0.024,-0.017,-0.019,-0.020,-0.017,-0.020,-0.012],
[-0.012,-0.008,-0.006,-0.020,-0.012,-0.014,-0.016,-0.015,-0.018,-0.008],
[-0.008, 0.000,-0.003,-0.018,-0.008,-0.005,-0.012,-0.012,-0.016,-0.006],
[-0.013,-0.008,-0.004,-0.001,-0.015,-0.013,-0.006, 0.001,-0.011,-0.005],
[-0.017,-0.011,-0.006,-0.006,-0.018,-0.017,-0.013,-0.006,-0.012,-0.008],
[-0.020,-0.016,-0.011,-0.014,-0.022,-0.022,-0.018,-0.012,-0.017,-0.012],
[-0.026,-0.024,-0.023,-0.032,-0.028,-0.030,-0.030,-0.023,-0.030,-0.024],
[-0.025,-0.022,-0.022,-0.031,-0.025,-0.027,-0.028,-0.022,-0.029,-0.022],
[-0.021,-0.021,-0.021,-0.030,-0.024,-0.024,-0.024,-0.021,-0.027,-0.021]
])

machine_values = np.array([
-0.027,
-0.023,
-0.023,
-0.024,
-0.025,
-0.024,
-0.024,
-0.024,
-0.024,
-0.024
])

# Coordenadas 9x9
x = np.arange(-4,5)
y = np.arange(4,-5,-1)   # <- Y invertido coherente con tu decisión
X, Y = np.meshgrid(x,y)

def crear_cruz(valores):
    Z = np.full((9,9), np.nan)
    c = 4

    # Y+
    Z[c-4,c] = valores[0]
    Z[c-3,c] = valores[1]
    Z[c-2,c] = valores[2]

    # Y-
    Z[c+2,c] = valores[3]
    Z[c+3,c] = valores[4]
    Z[c+4,c] = valores[5]

    # X-
    Z[c,c-4] = valores[6]
    Z[c,c-3] = valores[7]
    Z[c,c-2] = valores[8]

    # X+
    Z[c,c+2] = valores[9]
    Z[c,c+3] = valores[10]
    Z[c,c+4] = valores[11]

    return Z

   # --- Creamos los 10 scatter3D ---
for pieza in range(10):
    Z = crear_cruz(data[:,pieza])

    points = []
    colors = []
    for i in range(9):
        for j in range(9):
            if not np.isnan(Z[i,j]):
                points.append([X[i,j], Y[i,j], Z[i,j]])
                colors.append(Z[i,j])

    points = np.array(points)
    colors = np.array(colors)

    fig.add_trace(go.Scatter3d(
        x=points[:,0],
        y=points[:,1],
        z=points[:,2],
        mode='markers',
        marker=dict(
            size=8,
            color=colors,
            colorscale=[
                [0.0,"red"],
                [0.05,"yellow"],
                [0.5,"green"],
                [0.95,"yellow"],
                [1.0,"red"],
            ],
            cmin=-0.03,
            cmax=0,
            colorbar=dict(title="Z")
        ),
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

# --- Dropdown ---
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

# --- Slider ---
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
        xaxis=dict(range=[-5,5]),
        yaxis=dict(range=[-5,5]),
        zaxis=dict(range=[-0.04,0.01]),
        aspectratio=dict(x=1,y=1,z=0.7)
    ),
    title="Pieza 1"
)

html_str = pio.to_html(fig, include_plotlyjs='cdn')
HTML(html_str)

pio.write_html(fig, "BushBallScatter.html","w", include_plotlyjs='include')
print("Archivo guardado como BushBallScatter.html")
