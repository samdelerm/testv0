from src.geometry_utils import *
from math import atan2, cos, sin, sqrt
import rsk

def draw_static_elements(canvas):
    """Dessine les éléments statiques du terrain de football."""
    canvas.delete("static")
    # Lignes du terrain
    canvas.create_line(convert_coords(-1, -0.6, canvas, True), convert_coords(1, -0.6, canvas, True), fill="white", width=5, tags="static")
    canvas.create_line(convert_coords(-1, 0.6, canvas, True), convert_coords(1, 0.6, canvas, True), fill="white", width=5, tags="static")
    canvas.create_line(convert_coords(-1, -0.6, canvas, True), convert_coords(-1, 0.6, canvas, True), fill="white", width=5, tags="static")
    canvas.create_line(convert_coords(1, -0.6, canvas, True), convert_coords(1, 0.6, canvas, True), fill="white", width=5, tags="static")

    # Draw the goals
    canvas.create_line(convert_coords(-1, -0.3, canvas, True), convert_coords(-1, 0.3, canvas, True), fill="white", width=5, tags="static")
    canvas.create_line(convert_coords(1, -0.3, canvas, True), convert_coords(1, 0.3, canvas, True), fill="white", width=5, tags="static")

    # Draw the center circle
    draw_circle(canvas, x=0, y=0, r=0.3, color="black", fill=False, tag="static")

    # Draw additional static elements
    draw_graduations(canvas)

def draw_half_line_from_green1_to_ball(client,canvas, green1_position, ball_position, blue_positions, tolerance=0.1):
    """
    Trace une demi-droite depuis le robot green1 passant par la balle,
    tout en s'arrêtant si elle croise la position d'un robot adverse
    avec une tolérance de 0.1 unités.
    """
    x_green1, y_green1 = green1_position
    x_ball, y_ball = ball_position

    # Calcul de l'angle entre green1 et la balle
    angle = atan2(y_ball - y_green1, x_ball - x_green1)
    
    # Fixer une longueur arbitraire pour la demi-droite
    length = 2  # longueur de la demi-droite (par exemple 2 unités sur le terrain)
    
    # Parcourir chaque petit segment de la demi-droite pour vérifier les intersections
    step_size = 0.01  # Taille des pas pour parcourir la demi-droite
    for t in range(int(length / step_size)):
        # Calculer la position actuelle sur la demi-droite
        x_current = x_green1 + t * step_size * cos(angle)
        y_current = y_green1 + t * step_size * sin(angle)

        # Vérifier si la position actuelle croise un robot adverse
        for blue_pos in blue_positions:
            x_blue, y_blue = blue_pos
            distance_to_blue = sqrt((x_current - x_blue) ** 2 + (y_current - y_blue) ** 2)
            if distance_to_blue <= tolerance:
                # Si la demi-droite passe trop près d'un robot adverse, arrêter ici
                x_end = x_current
                y_end = y_current
                
                break
        else:
            # Si aucun robot n'est croisé, continuer
            continue
        # Si un robot est croisé, sortir des boucles
        break
    else:
        # Si aucun robot n'est croisé, la demi-droite atteint sa longueur maximale
        x_end = x_green1 + length * cos(angle)
        y_end = x_green1 + length * sin(angle)

    # Convertir les coordonnées pour le canvas
    x1_canvas, y1_canvas = convert_coords(x_green1, y_green1, canvas, True)
    x2_canvas, y2_canvas = convert_coords(x_end, y_end, canvas, True)
    if does_half_line_cross_x(client.green1.position, ball_position, -0.9):
        for blue_pos in blue_positions:
            x_blue, y_blue = blue_pos
            distance_to_blue = sqrt((x_current - x_blue) ** 2 + (y_current - y_blue) ** 2)
            if distance_to_blue >= tolerance:
                #draw_circle(canvas, x=-0.3, y=0.8, r=0.02, color="red", fill=True, tag="dynamic")
                canvas.create_text(convert_coords(-0.3, 0.8, canvas, True), text="But Vert", fill="red", tags="dynamic",font=("Arial",15))
    if does_half_line_cross_x(client.blue1.position, ball_position, 0.9):
        for blue_pos in blue_positions:
            x_blue, y_blue = blue_pos
            distance_to_blue = sqrt((x_current - x_blue) ** 2 + (y_current - y_blue) ** 2)
            if distance_to_blue >= tolerance:
                #draw_circle(canvas, x=0.3, y=0.8, r=0.02, color="blue", fill=True, tag="dynamic")
                canvas.create_text(convert_coords(0.3, 0.8, canvas, True), text="But Bleu", fill="blue", tags="dynamic",font=("Arial",15))
    # Tracer la demi-droite
    canvas.create_line(x1_canvas, y1_canvas, x2_canvas, y2_canvas, fill="red", width=2, tags="dynamic")


def draw_dynamic_elements(canvas, client):
    """Dessine les éléments dynamiques (robots, ballon, etc.)"""
    canvas.delete("dynamic")
    
    ball_position = client.ball
    robots = [client.robot['green'][1], client.robot['green'][2], client.robot['blue'][1], client.robot['blue'][2]]
    
    # Dessin des éléments dynamiques
    for robot in robots:
        color = "green" if robot.color == "green" else "blue"
        fill = "#00FF10" if color == "green" else "blue"
        if color == "green":
            fill = "#7CFC00"  # Lighter green color
        outline = "black" if color == "green" else "white"
        
        x, y = robot.pose[:2]
        robot_radius = rsk.constants.robot_radius
        canvas.create_oval(convert_coords(x - robot_radius, y - robot_radius, canvas, True), 
                           convert_coords(x + robot_radius, y + robot_radius, canvas, True), 
                           outline = outline, fill = fill, tags = "dynamic")
        
        # Dessin du trait devant le robot suivant son orientation
        orientation = robot.pose[2]
        line_length = 0.1  # Longueur du trait devant le robot
        x_end = x + line_length * cos(orientation)
        y_end = y + line_length * sin(orientation)
        canvas.create_line(convert_coords(x, y, canvas, True), 
                           convert_coords(x_end, y_end, canvas, True), 
                           fill = "#FF69B4", width = 2, tags = "dynamic")  # Couleur rose fluo

    # Dessin de la balle
    x, y = ball_position
    ball_radius = rsk.constants.ball_radius
    canvas.create_oval(convert_coords(x - ball_radius, y - ball_radius, canvas, True), 
                       convert_coords(x + ball_radius, y + ball_radius, canvas, True), 
                       outline = "orange", fill = "orange", tags = "dynamic")
    
    # Dessin de la demi-droite
    draw_half_line_from_green1_to_ball(client, canvas, client.robot['green'][1].pose[:2], ball_position, [client.robot['blue'][1].pose[:2], client.robot['blue'][2].pose[:2]])
    draw_half_line_from_green1_to_ball(client, canvas, client.robot['blue'][1].pose[:2], ball_position, [client.robot['green'][1].pose[:2], client.robot['green'][2].pose[:2]])

def draw_field():
    """Renders the soccer field and returns the drawing as a string (SVG)."""
    svg_elements = []

    # Draw field boundaries
    svg_elements.append('<rect x="-1" y="-0.6" width="2" height="1.2" fill="none" stroke="white" stroke-width="0.02"/>')

    # Draw center circle
    svg_elements.append('<circle cx="0" cy="0" r="0.3" fill="none" stroke="black" stroke-width="0.02"/>')

    # Draw goals
    svg_elements.append('<rect x="-1" y="-0.4" width="0.4" height="0.8" fill="none" stroke="black" stroke-width="0.02"/>')
    svg_elements.append('<rect x="0.6" y="-0.4" width="0.4" height="0.8" fill="none" stroke="black" stroke-width="0.02"/>')

    # Draw additional static elements
    svg_elements.append('<line x1="-1" y1="-0.3" x2="-0.9" y2="-0.3" stroke="white" stroke-width="0.02"/>')
    svg_elements.append('<line x1="-1" y1="0.3" x2="-0.9" y2="0.3" stroke="white" stroke-width="0.02"/>')
    svg_elements.append('<line x1="1" y1="-0.3" x2="0.9" y2="-0.3" stroke="white" stroke-width="0.02"/>')
    svg_elements.append('<line x1="1" y1="0.3" x2="0.9" y2="0.3" stroke="white" stroke-width="0.02"/>')

    # Combine all SVG elements into a single SVG string
    svg_content = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1.1 -0.7 2.2 1.4" style="background-color: green;">' + ''.join(svg_elements) + '</svg>'
    return svg_content

def get_client_data():
    """Fetch the latest client data. Replace this with actual implementation."""
    # Example client data
    client = {
        'ball': [0, 0],
        'robot': {
            'green': {
                1: {'pose': [-0.5, 0, 0]},
                2: {'pose': [-0.5, 0.2, 0]}
            },
            'blue': {
                1: {'pose': [0.5, 0, 0]},
                2: {'pose': [0.5, 0.2, 0]}
            }
        }
    }
    return client

