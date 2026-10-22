import turtle

# ==========================================
# GLOBAL CONFIGURATION & SCALE STATE
# (Strictly procedural: no classes or lambdas)
# ==========================================

# Drawing area perimeter box coordinates
BOX_X = -470
BOX_Y = -330
BOX_W = 940
BOX_H = 560

# Origin location inside the drawing area (center of the box)
ORIGIN_X = 0
ORIGIN_Y = -50

# Active drawing scale factor (1.0 = standard 1:1 pixel scale)
PLAN_SCALE = 1.0


# ==========================================
# 1. Coordinate Transform & Turtle Helpers
# ==========================================

def to_screen_x(x):
    """Converts user X coordinate to turtle screen coordinate using active scale."""
    return ORIGIN_X + (x * PLAN_SCALE)


def to_screen_y(y):
    """Converts user Y coordinate to turtle screen coordinate using active scale."""
    return ORIGIN_Y + (y * PLAN_SCALE)


def to_screen_dim(val):
    """Scales a dimension (length, radius, thickness) using active scale."""
    return val * PLAN_SCALE


def go_to(x, y):
    """Moves turtle to absolute screen (x, y) without drawing."""
    turtle.penup()
    turtle.goto(x, y)
    turtle.pendown()


# ==========================================
# 2. Perimeter Box & Origin Marker
# ==========================================

def draw_perimeter_box():
    """Draws the rectangular boundary enclosing the floor plan drawing area."""
    go_to(BOX_X, BOX_Y)
    turtle.pencolor("#2C3E50")
    turtle.pensize(2)
    turtle.setheading(0)
    for _ in range(2):
        turtle.forward(BOX_W)
        turtle.left(90)
        turtle.forward(BOX_H)
        turtle.left(90)

    # Perimeter label & scale badge at top-left of the box
    go_to(BOX_X + 15, BOX_Y + BOX_H - 22)
    turtle.pencolor("#555555")
    turtle.write(
        "DRAWING AREA  |  Scale: " + str(round(PLAN_SCALE, 2)) + "x",
        align="left",
        font=("Arial", 10, "bold")
    )
    turtle.pensize(1)
    turtle.pencolor("black")


def draw_origin_marker():
    """Draws an origin crosshair and axes marker at (0, 0) inside the box."""
    # Red crosshairs
    turtle.pencolor("#D9534F")
    turtle.pensize(2)

    # X-axis line & positive pointer
    go_to(ORIGIN_X - 25, ORIGIN_Y)
    turtle.setheading(0)
    turtle.forward(55)
    turtle.write(" +X", align="left", font=("Arial", 8, "bold"))

    # Y-axis line & positive pointer
    go_to(ORIGIN_X, ORIGIN_Y - 25)
    turtle.setheading(90)
    turtle.forward(55)
    turtle.write(" +Y", align="left", font=("Arial", 8, "bold"))

    # Origin center circle
    go_to(ORIGIN_X, ORIGIN_Y - 4)
    turtle.fillcolor("#D9534F")
    turtle.begin_fill()
    turtle.circle(4)
    turtle.end_fill()

    # Origin text label
    go_to(ORIGIN_X + 8, ORIGIN_Y - 18)
    turtle.write("(0, 0)", align="left", font=("Arial", 9, "bold"))

    turtle.pensize(1)
    turtle.pencolor("black")


# ==========================================
# 3. Draw Walls Functions (Scaled)
# ==========================================

def draw_non_structural_wall(user_x, user_y, length, orientation='horizontal', thickness=6):
    """Draws a non-structural wall (pair of parallel thin lines)."""
    sx = to_screen_x(user_x)
    sy = to_screen_y(user_y)
    slen = to_screen_dim(length)
    sthick = to_screen_dim(thickness)

    if orientation == 'horizontal':
        go_to(sx, sy + sthick / 2)
        turtle.setheading(0)
        turtle.forward(slen)
        go_to(sx, sy - sthick / 2)
        turtle.setheading(0)
        turtle.forward(slen)
    elif orientation == 'vertical':
        go_to(sx + sthick / 2, sy)
        turtle.setheading(90)
        turtle.forward(slen)
        go_to(sx - sthick / 2, sy)
        turtle.setheading(90)
        turtle.forward(slen)


def draw_structural_wall(user_x, user_y, length, thickness=16, orientation='horizontal'):
    """Draws a structural wall (solid black filled rectangular bar)."""
    sx = to_screen_x(user_x)
    sy = to_screen_y(user_y)
    slen = to_screen_dim(length)
    sthick = to_screen_dim(thickness)

    go_to(sx, sy)
    turtle.fillcolor("black")
    turtle.begin_fill()
    if orientation == 'horizontal':
        turtle.setheading(0)
        for _ in range(2):
            turtle.forward(slen)
            turtle.left(90)
            turtle.forward(sthick)
            turtle.left(90)
    elif orientation == 'vertical':
        turtle.setheading(90)
        for _ in range(2):
            turtle.forward(slen)
            turtle.right(90)
            turtle.forward(sthick)
            turtle.right(90)
    turtle.end_fill()


def draw_gable_end_wall(user_x, user_y, length, thickness=20, orientation='horizontal', inset=3):
    """Draws a gable-end wall (nested rectangle)."""
    sx = to_screen_x(user_x)
    sy = to_screen_y(user_y)
    slen = to_screen_dim(length)
    sthick = to_screen_dim(thickness)
    sinset = to_screen_dim(inset)

    if orientation == 'horizontal':
        w, h = slen, sthick
    else:
        w, h = sthick, slen

    go_to(sx, sy)
    turtle.setheading(0)
    for _ in range(2):
        turtle.forward(w)
        turtle.left(90)
        turtle.forward(h)
        turtle.left(90)

    go_to(sx + sinset, sy + sinset)
    for _ in range(2):
        turtle.forward(w - 2 * sinset)
        turtle.left(90)
        turtle.forward(h - 2 * sinset)
        turtle.left(90)


# ==========================================
# 4. Doors and Windows Functions (Scaled)
# ==========================================

def draw_swing_door(user_x, user_y, size=60, orientation="top-right"):
    """Draws an architectural swing door."""
    sx = to_screen_x(user_x)
    sy = to_screen_y(user_y)
    ssize = to_screen_dim(size)

    if orientation == "top-right":
        go_to(sx + ssize, sy)
        turtle.setheading(90)
        turtle.circle(ssize, 90)
        go_to(sx, sy)
        turtle.setheading(90)
        turtle.forward(ssize)

    elif orientation == "top-left":
        go_to(sx, sy + ssize)
        turtle.setheading(180)
        turtle.circle(ssize, 90)
        go_to(sx, sy)
        turtle.setheading(90)
        turtle.forward(ssize)

    elif orientation == "bottom-right":
        go_to(sx, sy - ssize)
        turtle.setheading(0)
        turtle.circle(ssize, 90)
        go_to(sx, sy)
        turtle.setheading(270)
        turtle.forward(ssize)

    else:  # bottom-left
        go_to(sx - ssize, sy)
        turtle.setheading(270)
        turtle.circle(ssize, 90)
        go_to(sx, sy)
        turtle.setheading(270)
        turtle.forward(ssize)


def draw_sliding_door(user_x, user_y, length=100, orientation="horizontal", gap=6):
    """Draws a sliding door with two overlapping sliding panels and jambs."""
    sx = to_screen_x(user_x)
    sy = to_screen_y(user_y)
    slen = to_screen_dim(length)
    sgap = to_screen_dim(gap)
    panel_len = slen * 0.55

    if orientation == "horizontal":
        go_to(sx, sy + sgap / 2)
        turtle.setheading(0)
        turtle.forward(panel_len)
        go_to(sx + slen - panel_len, sy - sgap / 2)
        turtle.setheading(0)
        turtle.forward(panel_len)
        go_to(sx, sy - sgap)
        turtle.setheading(90)
        turtle.forward(2 * sgap)
        go_to(sx + slen, sy - sgap)
        turtle.setheading(90)
        turtle.forward(2 * sgap)
    else:
        go_to(sx - sgap / 2, sy)
        turtle.setheading(90)
        turtle.forward(panel_len)
        go_to(sx + sgap / 2, sy + slen - panel_len)
        turtle.setheading(90)
        turtle.forward(panel_len)
        go_to(sx - sgap, sy)
        turtle.setheading(0)
        turtle.forward(2 * sgap)
        go_to(sx - sgap, sy + slen)
        turtle.setheading(0)
        turtle.forward(2 * sgap)


def draw_standard_window(user_x, user_y, length=120, orientation="horizontal", thickness=14):
    """Draws a standard architectural window."""
    sx = to_screen_x(user_x)
    sy = to_screen_y(user_y)
    slen = to_screen_dim(length)
    sthick = to_screen_dim(thickness)

    if orientation == "horizontal":
        go_to(sx, sy + sthick / 2)
        turtle.setheading(0)
        turtle.forward(slen)
        go_to(sx, sy - sthick / 2)
        turtle.setheading(0)
        turtle.forward(slen)
        go_to(sx, sy)
        turtle.setheading(0)
        turtle.forward(slen)
        go_to(sx, sy - sthick / 2)
        turtle.setheading(90)
        turtle.forward(sthick)
        go_to(sx + slen, sy - sthick / 2)
        turtle.setheading(90)
        turtle.forward(sthick)
    else:
        go_to(sx - sthick / 2, sy)
        turtle.setheading(90)
        turtle.forward(slen)
        go_to(sx + sthick / 2, sy)
        turtle.setheading(90)
        turtle.forward(slen)
        go_to(sx, sy)
        turtle.setheading(90)
        turtle.forward(slen)
        go_to(sx - sthick / 2, sy)
        turtle.setheading(0)
        turtle.forward(sthick)
        go_to(sx - sthick / 2, sy + slen)
        turtle.setheading(0)
        turtle.forward(sthick)


def draw_sliding_window(user_x, user_y, length=120, orientation="horizontal", thickness=14):
    """Draws a sliding window with offset sliding sashes."""
    sx = to_screen_x(user_x)
    sy = to_screen_y(user_y)
    slen = to_screen_dim(length)
    sthick = to_screen_dim(thickness)
    panel_len = slen * 0.55
    offset = to_screen_dim(3)

    if orientation == "horizontal":
        go_to(sx, sy - sthick / 2)
        turtle.setheading(0)
        for _ in range(2):
            turtle.forward(slen)
            turtle.left(90)
            turtle.forward(sthick)
            turtle.left(90)
        go_to(sx, sy + offset)
        turtle.setheading(0)
        turtle.forward(panel_len)
        go_to(sx + slen - panel_len, sy - offset)
        turtle.setheading(0)
        turtle.forward(panel_len)
    else:
        go_to(sx - sthick / 2, sy)
        turtle.setheading(0)
        for _ in range(2):
            turtle.forward(sthick)
            turtle.left(90)
            turtle.forward(slen)
            turtle.left(90)
        go_to(sx - offset, sy)
        turtle.setheading(90)
        turtle.forward(panel_len)
        go_to(sx + offset, sy + slen - panel_len)
        turtle.setheading(90)
        turtle.forward(panel_len)


# ==========================================
# 5. GUI BUTTON & TOOLBAR SYSTEM
# ==========================================

def draw_button(x, y, width, height, text, bg_color="#E0E0E0"):
    """Draws a button box with centered text label."""
    go_to(x, y)
    turtle.fillcolor(bg_color)
    turtle.pencolor("black")
    turtle.pensize(2)
    turtle.setheading(0)

    turtle.begin_fill()
    for _ in range(2):
        turtle.forward(width)
        turtle.left(90)
        turtle.forward(height)
        turtle.left(90)
    turtle.end_fill()

    turtle.penup()
    turtle.goto(x + width / 2, y + (height / 2) - 7)
    turtle.write(text, align="center", font=("Arial", 9, "bold"))
    turtle.pensize(1)


def is_inside_box(click_x, click_y, x, y, width, height):
    """Checks whether a click coordinate falls within a rectangular box."""
    return (x <= click_x <= x + width) and (y <= click_y <= y + height)


def render_gui():
    """Renders the 2-tier toolbar, the perimeter box, and the origin marker."""
    turtle.tracer(0)

    # Toolbar background panel
    go_to(-490, 255)
    turtle.fillcolor("#F5F5F5")
    turtle.pencolor("#CCCCCC")
    turtle.begin_fill()
    turtle.setheading(0)
    for _ in range(2):
        turtle.forward(980)
        turtle.left(90)
        turtle.forward(105)
        turtle.left(90)
    turtle.end_fill()

    # --- ROW 1: Walls & Actions (y = 315, height = 38) ---
    draw_button(-470, 315, 140, 38, "Non-Structural", "#D1E7DD")
    draw_button(-315, 315, 140, 38, "Structural Wall", "#D1E7DD")
    draw_button(-160, 315, 140, 38, "Gable-End Wall", "#D1E7DD")
    draw_button(70, 315, 115, 38, "Set Scale", "#FFE5D0")
    draw_button(200, 315, 120, 38, "Clear Canvas", "#FFF3CD")
    draw_button(335, 315, 120, 38, "Exit", "#F8D7DA")

    # --- ROW 2: Openings (y = 265, height = 38) ---
    draw_button(-470, 265, 140, 38, "Swing Door", "#CFF4FC")
    draw_button(-315, 265, 140, 38, "Sliding Door", "#CFF4FC")
    draw_button(-160, 265, 140, 38, "Standard Window", "#E2D9F3")
    draw_button(-5, 265, 140, 38, "Sliding Window", "#E2D9F3")

    # Render Perimeter Box & Origin Marker
    draw_perimeter_box()
    draw_origin_marker()

    turtle.pencolor("black")
    turtle.tracer(1)


# ==========================================
# 6. INPUT DIALOGS & ACTION HANDLERS
# ==========================================

def prompt_opening_inputs(title, default_len=100):
    """Prompts for coordinates (relative to origin), length, and orientation."""
    screen = turtle.Screen()
    x = screen.numinput(title, "X offset from Origin (0,0):", default=0, minval=-500, maxval=500)
    if x is None:
        return None
    y = screen.numinput(title, "Y offset from Origin (0,0):", default=0, minval=-300, maxval=300)
    if y is None:
        return None
    length = screen.numinput(title, "Length / Width (units):", default=default_len, minval=10, maxval=800)
    if length is None:
        return None
    ori = screen.textinput(title, "Orientation ('h' for horizontal, 'v' for vertical):")
    if ori is None or ori.lower().startswith('h'):
        orientation = 'horizontal'
    else:
        orientation = 'vertical'
    return x, y, length, orientation


def prompt_swing_door_inputs():
    """Prompts for swing door hinge position (relative to origin), size, and swing direction."""
    screen = turtle.Screen()
    x = screen.numinput("Swing Door", "Hinge X (from Origin 0,0):", default=0, minval=-500, maxval=500)
    if x is None:
        return None
    y = screen.numinput("Swing Door", "Hinge Y (from Origin 0,0):", default=0, minval=-300, maxval=300)
    if y is None:
        return None
    size = screen.numinput("Swing Door", "Door width / radius (units):", default=60, minval=15, maxval=250)
    if size is None:
        return None

    prompt_text = "Swing direction:\n1: Top-Right\n2: Top-Left\n3: Bottom-Right\n4: Bottom-Left"
    choice = screen.textinput("Swing Door", prompt_text)
    if choice == '2':
        orientation = "top-left"
    elif choice == '3':
        orientation = "bottom-right"
    elif choice == '4':
        orientation = "bottom-left"
    else:
        orientation = "top-right"
    return x, y, size, orientation


def handle_set_scale():
    """Updates the global scale factor and redraws the perimeter and origin."""
    global PLAN_SCALE
    screen = turtle.Screen()
    new_scale = screen.numinput(
        "Set Scale",
        "Enter new scale factor (e.g., 0.5 to 2.5):",
        default=PLAN_SCALE,
        minval=0.1,
        maxval=5.0
    )
    if new_scale is not None and new_scale > 0:
        PLAN_SCALE = new_scale
        # Redraw bounding box header with updated scale badge
        turtle.tracer(0)
        draw_perimeter_box()
        draw_origin_marker()
        turtle.tracer(1)


def handle_non_structural():
    data = prompt_opening_inputs("Non-Structural Wall", default_len=150)
    if data:
        x, y, length, orientation = data
        draw_non_structural_wall(x, y, length, orientation)


def handle_structural():
    data = prompt_opening_inputs("Structural Wall", default_len=150)
    if data:
        x, y, length, orientation = data
        draw_structural_wall(x, y, length, 16, orientation)


def handle_gable():
    data = prompt_opening_inputs("Gable-End Wall", default_len=150)
    if data:
        x, y, length, orientation = data
        draw_gable_end_wall(x, y, length, 20, orientation)


def handle_swing_door():
    data = prompt_swing_door_inputs()
    if data:
        x, y, size, orientation = data
        draw_swing_door(x, y, size, orientation)


def handle_sliding_door():
    data = prompt_opening_inputs("Sliding Door", default_len=100)
    if data:
        x, y, length, orientation = data
        draw_sliding_door(x, y, length, orientation)


def handle_standard_window():
    data = prompt_opening_inputs("Standard Window", default_len=120)
    if data:
        x, y, length, orientation = data
        draw_standard_window(x, y, length, orientation)


def handle_sliding_window():
    data = prompt_opening_inputs("Sliding Window", default_len=120)
    if data:
        x, y, length, orientation = data
        draw_sliding_window(x, y, length, orientation)


def handle_clear():
    turtle.clear()
    render_gui()


def handle_exit():
    turtle.bye()


# ==========================================
# 7. CLICK EVENT DISPATCHER
# ==========================================

def on_canvas_click(click_x, click_y):
    """Dispatches mouse click coordinates to individual button actions."""
    # Row 1: Walls & Actions (y: 315 to 353)
    if is_inside_box(click_x, click_y, -470, 315, 140, 38):
        handle_non_structural()
    elif is_inside_box(click_x, click_y, -315, 315, 140, 38):
        handle_structural()
    elif is_inside_box(click_x, click_y, -160, 315, 140, 38):
        handle_gable()
    elif is_inside_box(click_x, click_y, 70, 315, 115, 38):
        handle_set_scale()
    elif is_inside_box(click_x, click_y, 200, 315, 120, 38):
        handle_clear()
    elif is_inside_box(click_x, click_y, 335, 315, 120, 38):
        handle_exit()

    # Row 2: Doors & Windows (y: 265 to 303)
    elif is_inside_box(click_x, click_y, -470, 265, 140, 38):
        handle_swing_door()
    elif is_inside_box(click_x, click_y, -315, 265, 140, 38):
        handle_sliding_door()
    elif is_inside_box(click_x, click_y, -160, 265, 140, 38):
        handle_standard_window()
    elif is_inside_box(click_x, click_y, -5, 265, 140, 38):
        handle_sliding_window()


# ==========================================
# 8. MAIN FUNCTION
# ==========================================

def main():
    turtle.setup(1000, 750)
    turtle.title("HDB Floor Plan Designer")
    turtle.speed(0)
    turtle.hideturtle()

    render_gui()

    screen = turtle.Screen()
    screen.onscreenclick(on_canvas_click)

    turtle.done()


if __name__ == "__main__":
    main()