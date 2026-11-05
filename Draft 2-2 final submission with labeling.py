
import math
import turtle

# ==========================================
# GLOBAL CONFIGURATION & STATE
# ==========================================
PLAN_SCALE = 0.5
ORIGIN_X = 0
ORIGIN_Y = -45
PLAN_ELEMENTS = []

# State tracker for interactive boundary clicks
LABEL_MODE_ACTIVE = False
LABEL_CORNER_1 = None  # Stores (x1, y1) when waiting for second corner


# ==========================================
# 1. COORDINATE SYSTEM & TRANSFORMATION HELPERS
# ==========================================

def go_to(x, y):
    """Moves turtle to screen coordinate (x, y) without drawing."""
    turtle.penup()
    turtle.goto(x, y)
    turtle.pendown()


def to_screen_x(user_x):
    """Converts user X coordinate to scaled screen X coordinate."""
    return ORIGIN_X + (user_x * PLAN_SCALE)


def to_screen_y(user_y):
    """Converts user Y coordinate to scaled screen Y coordinate."""
    return ORIGIN_Y + (user_y * PLAN_SCALE)


def to_screen_dim(dim):
    """Scales a linear dimension by the active PLAN_SCALE."""
    return dim * PLAN_SCALE


def to_user_x(screen_x):
    """Converts screen X back to unscaled floor plan coordinate."""
    return (screen_x - ORIGIN_X) / PLAN_SCALE


def to_user_y(screen_y):
    """Converts screen Y back to unscaled floor plan coordinate."""
    return (screen_y - ORIGIN_Y) / PLAN_SCALE


# ==========================================
# 2. PERIMETER BOUNDING BOX
# ==========================================

def draw_perimeter_box():
    """Draws the floor plan display bounding box and current scale badge."""
    box_x = -475
    box_y = -350
    box_w = 950
    box_h = 610

    turtle.pensize(2)
    turtle.pencolor("#708090")
    go_to(box_x, box_y)
    turtle.setheading(0)
    for _ in range(2):
        turtle.forward(box_w)
        turtle.left(90)
        turtle.forward(box_h)
        turtle.left(90)

    # Scale badge (placed neatly inside upper-left corner of the perimeter box)
    go_to(box_x + 12, box_y + box_h - 20)
    turtle.pencolor("#404040")
    turtle.write("Scale: " + str(round(PLAN_SCALE, 2)) + "x",
                 align="left", font=("Arial", 9, "bold"))
    turtle.pensize(1)
    turtle.pencolor("black")


def render_canvas_frame():
    """Redraws the outer canvas perimeter box."""
    turtle.tracer(0)
    draw_perimeter_box()
    turtle.tracer(1)


# ==========================================
# 3. DOTTED LINES & ROOM LABEL FUNCTIONS
# ==========================================

def draw_dotted_line(x1, y1, x2, y2, dot_length=5, gap_length=4):
    """Draws a dotted/dashed line segment between two screen points."""
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)
    if dist == 0:
        return

    ux = dx / dist
    uy = dy / dist
    traveled = 0.0
    curr_x = x1
    curr_y = y1

    while traveled < dist:
        segment = min(dot_length, dist - traveled)
        go_to(curr_x, curr_y)
        curr_x += ux * segment
        curr_y += uy * segment
        turtle.goto(curr_x, curr_y)
        traveled += segment

        if traveled < dist:
            gap = min(gap_length, dist - traveled)
            curr_x += ux * gap
            curr_y += uy * gap
            traveled += gap


def draw_dotted_rect(sx, sy, sw, sh):
    """Draws a dotted rectangular boundary on screen."""
    turtle.pensize(1)
    turtle.pencolor("#888888")
    draw_dotted_line(sx, sy, sx + sw, sy)
    draw_dotted_line(sx + sw, sy, sx + sw, sy + sh)
    draw_dotted_line(sx + sw, sy + sh, sx, sy + sh)
    draw_dotted_line(sx, sy + sh, sx, sy)
    turtle.pencolor("black")


def draw_room_label(user_x, user_y, width, height, label_text):
    """Renders an architectural room boundary with dotted lines and centered label."""
    sx = to_screen_x(user_x)
    sy = to_screen_y(user_y)
    sw = to_screen_dim(width)
    sh = to_screen_dim(height)

    draw_dotted_rect(sx, sy, sw, sh)

    cx = sx + (sw / 2)
    cy = sy + (sh / 2) - 5
    turtle.penup()
    turtle.goto(cx, cy)
    turtle.pencolor("#222222")
    turtle.write(label_text, align="center", font=("Arial", 9, "bold"))
    turtle.pencolor("black")


# ==========================================
# 4. WALL DRAWING FUNCTIONS
# ==========================================

def draw_non_structural_wall(x, y, length, orientation='horizontal', thickness=6):
    """Draws a non-structural wall (pair of parallel thin lines)."""
    sx = to_screen_x(x)
    sy = to_screen_y(y)
    s_length = to_screen_dim(length)
    s_thick = max(2, to_screen_dim(thickness))

    if orientation == 'horizontal':
        go_to(sx, sy + s_thick / 2)
        turtle.setheading(0)
        turtle.forward(s_length)
        go_to(sx, sy - s_thick / 2)
        turtle.setheading(0)
        turtle.forward(s_length)
    elif orientation == 'vertical':
        go_to(sx + s_thick / 2, sy)
        turtle.setheading(90)
        turtle.forward(s_length)
        go_to(sx - s_thick / 2, sy)
        turtle.setheading(90)
        turtle.forward(s_length)


def draw_structural_wall(x, y, length, thickness=16, orientation='horizontal'):
    """Draws a structural wall (solid black filled rectangular bar)."""
    sx = to_screen_x(x)
    sy = to_screen_y(y)
    s_length = to_screen_dim(length)
    s_thick = max(4, to_screen_dim(thickness))

    go_to(sx, sy)
    turtle.fillcolor("black")
    turtle.begin_fill()
    if orientation == 'horizontal':
        turtle.setheading(0)
        for _ in range(2):
            turtle.forward(s_length)
            turtle.left(90)
            turtle.forward(s_thick)
            turtle.left(90)
    elif orientation == 'vertical':
        turtle.setheading(90)
        for _ in range(2):
            turtle.forward(s_length)
            turtle.right(90)
            turtle.forward(s_thick)
            turtle.right(90)
    turtle.end_fill()


def draw_gable_end_wall(x, y, length, thickness=20, orientation='horizontal', inset=3):
    """Draws a gable-end wall (nested rectangle)."""
    sx = to_screen_x(x)
    sy = to_screen_y(y)
    s_length = to_screen_dim(length)
    s_thick = max(6, to_screen_dim(thickness))
    s_inset = max(1, to_screen_dim(inset))

    go_to(sx, sy)
    if orientation == 'horizontal':
        w, h = s_length, s_thick
    else:
        w, h = s_thick, s_length

    turtle.setheading(0)
    for _ in range(2):
        turtle.forward(w)
        turtle.left(90)
        turtle.forward(h)
        turtle.left(90)

    go_to(sx + s_inset, sy + s_inset)
    for _ in range(2):
        turtle.forward(w - 2 * s_inset)
        turtle.left(90)
        turtle.forward(h - 2 * s_inset)
        turtle.left(90)


# ==========================================
# 5. DOORS AND WINDOWS FUNCTIONS
# ==========================================

def draw_swing_door(x, y, size=60, orientation="top-right"):
    """Draws an architectural swing door."""
    sx = to_screen_x(x)
    sy = to_screen_y(y)
    s_size = to_screen_dim(size)

    if orientation == "top-right":
        go_to(sx + s_size, sy)
        turtle.setheading(90)
        turtle.circle(s_size, 90)
        go_to(sx, sy)
        turtle.setheading(90)
        turtle.forward(s_size)
    elif orientation == "top-left":
        go_to(sx, sy + s_size)
        turtle.setheading(180)
        turtle.circle(s_size, 90)
        go_to(sx, sy)
        turtle.setheading(90)
        turtle.forward(s_size)
    elif orientation == "bottom-right":
        go_to(sx, sy - s_size)
        turtle.setheading(0)
        turtle.circle(s_size, 90)
        go_to(sx, sy)
        turtle.setheading(270)
        turtle.forward(s_size)
    elif orientation == "bottom-left":
        go_to(sx - s_size, sy)
        turtle.setheading(270)
        turtle.circle(s_size, 90)
        go_to(sx, sy)
        turtle.setheading(270)
        turtle.forward(s_size)
    elif orientation == "right-top":
        go_to(sx, sy + s_size)
        turtle.setheading(270)
        turtle.circle(-s_size, 90)
        go_to(sx, sy)
        turtle.setheading(0)
        turtle.forward(s_size)
    elif orientation == "right-bottom":
        go_to(sx, sy - s_size)
        turtle.setheading(90)
        turtle.circle(s_size, 90)
        go_to(sx, sy)
        turtle.setheading(0)
        turtle.forward(s_size)
    elif orientation == "left-top":
        go_to(sx, sy + s_size)
        turtle.setheading(270)
        turtle.circle(s_size, 90)
        go_to(sx, sy)
        turtle.setheading(180)
        turtle.forward(s_size)
    elif orientation == "left-bottom":
        go_to(sx, sy - s_size)
        turtle.setheading(90)
        turtle.circle(-s_size, 90)
        go_to(sx, sy)
        turtle.setheading(180)
        turtle.forward(s_size)


def draw_sliding_door(x, y, length=100, orientation="horizontal", gap=6):
    """Draws a sliding door with two overlapping sliding panels and jambs."""
    sx = to_screen_x(x)
    sy = to_screen_y(y)
    s_len = to_screen_dim(length)
    s_gap = max(3, to_screen_dim(gap))
    panel_len = s_len * 0.55

    if orientation == "horizontal":
        go_to(sx, sy + s_gap / 2)
        turtle.setheading(0)
        turtle.forward(panel_len)
        go_to(sx + s_len - panel_len, sy - s_gap / 2)
        turtle.setheading(0)
        turtle.forward(panel_len)
        go_to(sx, sy - s_gap)
        turtle.setheading(90)
        turtle.forward(2 * s_gap)
        go_to(sx + s_len, sy - s_gap)
        turtle.setheading(90)
        turtle.forward(2 * s_gap)
    else:
        go_to(sx - s_gap / 2, sy)
        turtle.setheading(90)
        turtle.forward(panel_len)
        go_to(sx + s_gap / 2, sy + s_len - panel_len)
        turtle.setheading(90)
        turtle.forward(panel_len)
        go_to(sx - s_gap, sy)
        turtle.setheading(0)
        turtle.forward(2 * s_gap)
        go_to(sx - s_gap, sy + s_len)
        turtle.setheading(0)
        turtle.forward(2 * s_gap)


def draw_standard_window(x, y, length=120, orientation="horizontal", thickness=14):
    """Draws a standard architectural window."""
    sx = to_screen_x(x)
    sy = to_screen_y(y)
    s_len = to_screen_dim(length)
    s_thick = max(4, to_screen_dim(thickness))

    if orientation == "horizontal":
        go_to(sx, sy + s_thick / 2)
        turtle.setheading(0)
        turtle.forward(s_len)
        go_to(sx, sy - s_thick / 2)
        turtle.setheading(0)
        turtle.forward(s_len)
        go_to(sx, sy)
        turtle.setheading(0)
        turtle.forward(s_len)
        go_to(sx, sy - s_thick / 2)
        turtle.setheading(90)
        turtle.forward(s_thick)
        go_to(sx + s_len, sy - s_thick / 2)
        turtle.setheading(90)
        turtle.forward(s_thick)
    else:
        go_to(sx - s_thick / 2, sy)
        turtle.setheading(90)
        turtle.forward(s_len)
        go_to(sx + s_thick / 2, sy)
        turtle.setheading(90)
        turtle.forward(s_len)
        go_to(sx, sy)
        turtle.setheading(90)
        turtle.forward(s_len)
        go_to(sx - s_thick / 2, sy)
        turtle.setheading(0)
        turtle.forward(s_thick)
        go_to(sx - s_thick / 2, sy + s_len)
        turtle.setheading(0)
        turtle.forward(s_thick)


def draw_sliding_window(x, y, length=120, orientation="horizontal", thickness=14):
    """Draws a sliding window."""
    sx = to_screen_x(x)
    sy = to_screen_y(y)
    s_len = to_screen_dim(length)
    s_thick = max(4, to_screen_dim(thickness))
    panel_len = s_len * 0.55
    offset = max(2, to_screen_dim(3))

    if orientation == "horizontal":
        go_to(sx, sy - s_thick / 2)
        turtle.setheading(0)
        for _ in range(2):
            turtle.forward(s_len)
            turtle.left(90)
            turtle.forward(s_thick)
            turtle.left(90)
        go_to(sx, sy + offset)
        turtle.setheading(0)
        turtle.forward(panel_len)
        go_to(sx + s_len - panel_len, sy - offset)
        turtle.setheading(0)
        turtle.forward(panel_len)
    else:
        go_to(sx - s_thick / 2, sy)
        turtle.setheading(0)
        for _ in range(2):
            turtle.forward(s_thick)
            turtle.left(90)
            turtle.forward(s_len)
            turtle.left(90)
        go_to(sx - offset, sy)
        turtle.setheading(90)
        turtle.forward(panel_len)
        go_to(sx + offset, sy + s_len - panel_len)
        turtle.setheading(90)
        turtle.forward(panel_len)


# ==========================================
# 6. FURNITURE ASSETS (BED & WARDROBE)
# ==========================================

def draw_bed(x, y, bed_type='queen', orientation='vertical'):
    """Draws a scaled bed with proportional pillows and fold line."""
    if bed_type.lower() == 'single':
        bw = 67.5
        bl = 135.0
    else:
        bw = 112.5
        bl = 142.5

    sx = to_screen_x(x)
    sy = to_screen_y(y)
    sbw = to_screen_dim(bw)
    sbl = to_screen_dim(bl)

    if orientation == 'horizontal':
        w, l = sbl, sbw
    else:
        w, l = sbw, sbl

    go_to(sx, sy)
    turtle.fillcolor("#FAFAFA")
    turtle.pencolor("#333333")
    turtle.pensize(2)
    turtle.begin_fill()
    turtle.setheading(0)
    for _ in range(2):
        turtle.forward(w)
        turtle.left(90)
        turtle.forward(l)
        turtle.left(90)
    turtle.end_fill()
    turtle.pensize(1)

    if orientation == 'vertical':
        fold_y = sy + (l * 0.72)
        go_to(sx, fold_y)
        turtle.setheading(0)
        turtle.forward(w)

        if bed_type.lower() == 'single':
            pw = w * 0.65
            ph = l * 0.16
            px = sx + (w - pw) / 2
            py = sy + l - ph - (l * 0.04)
            go_to(px, py)
            for _ in range(2):
                turtle.forward(pw)
                turtle.left(90)
                turtle.forward(ph)
                turtle.left(90)
        else:
            pw = w * 0.40
            ph = l * 0.16
            p_gap = w * 0.08
            py = sy + l - ph - (l * 0.04)
            go_to(sx + p_gap / 2, py)
            for _ in range(2):
                turtle.forward(pw)
                turtle.left(90)
                turtle.forward(ph)
                turtle.left(90)
            go_to(sx + (w / 2) + p_gap / 4, py)
            for _ in range(2):
                turtle.forward(pw)
                turtle.left(90)
                turtle.forward(ph)
                turtle.left(90)
    else:
        fold_x = sx + (w * 0.28)
        go_to(fold_x, sy)
        turtle.setheading(90)
        turtle.forward(l)

        if bed_type.lower() == 'single':
            pw = w * 0.16
            ph = l * 0.65
            px = sx + (w * 0.04)
            py = sy + (l - ph) / 2
            go_to(px, py)
            for _ in range(2):
                turtle.forward(pw)
                turtle.left(90)
                turtle.forward(ph)
                turtle.left(90)
        else:
            pw = w * 0.16
            ph = l * 0.40
            p_gap = l * 0.08
            px = sx + (w * 0.04)
            go_to(px, sy + p_gap / 2)
            for _ in range(2):
                turtle.forward(pw)
                turtle.left(90)
                turtle.forward(ph)
                turtle.left(90)
            go_to(px, sy + (l / 2) + p_gap / 4)
            for _ in range(2):
                turtle.forward(pw)
                turtle.left(90)
                turtle.forward(ph)
                turtle.left(90)

    turtle.pencolor("black")


def draw_wardrobe(x, y, length, depth=60, orientation='horizontal'):
    """Draws a customizable wardrobe unit."""
    sx = to_screen_x(x)
    sy = to_screen_y(y)
    sl = to_screen_dim(length)
    sd = to_screen_dim(depth)

    if orientation == 'horizontal':
        w, h = sl, sd
    else:
        w, h = sd, sl

    go_to(sx, sy)
    turtle.pensize(2)
    turtle.pencolor("#555555")
    turtle.fillcolor("#F2EFE9")
    turtle.begin_fill()
    turtle.setheading(0)
    for _ in range(2):
        turtle.forward(w)
        turtle.left(90)
        turtle.forward(h)
        turtle.left(90)
    turtle.end_fill()
    turtle.pensize(1)

    if orientation == 'horizontal':
        go_to(sx + w / 2, sy)
        turtle.setheading(90)
        turtle.forward(h)
        go_to(sx + (w * 0.1), sy + h / 2)
        turtle.setheading(0)
        turtle.forward(w * 0.8)
    else:
        go_to(sx, sy + h / 2)
        turtle.setheading(0)
        turtle.forward(w)
        go_to(sx + w / 2, sy + (h * 0.1))
        turtle.setheading(90)
        turtle.forward(h * 0.8)

    turtle.pencolor("black")


# ==========================================
# 7. FILE STORAGE & RETRIEVAL (NO JSON)
# ==========================================

def save_plan_to_file(filename):
    """Saves floor plan elements to a plain text file."""
    try:
        f = open(filename, "w")
        f.write("# MA1008 Floor Plan Data File\n")
        f.write("SCALE," + str(PLAN_SCALE) + "\n")
        for item in PLAN_ELEMENTS:
            line_parts = []
            for field in item:
                line_parts.append(str(field))
            f.write(",".join(line_parts) + "\n")
        f.close()
        print("[SUCCESS] Floor plan successfully saved to:", filename)
        return True
    except IOError:
        print("[ERROR] Failed to write file:", filename)
        return False


def load_plan_from_file(filename):
    """Loads and reconstructs a floor plan from a text file."""
    global PLAN_SCALE, PLAN_ELEMENTS
    try:
        f = open(filename, "r")
        lines = f.readlines()
        f.close()
    except FileNotFoundError:
        print("[ERROR] File Not Found: '" + filename + "' does not exist. Please check the file name.")
        return False
    except IOError:
        print("[ERROR] An error occurred while opening:", filename)
        return False

    turtle.clear()
    PLAN_ELEMENTS = []
    render_gui()

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split(",")
        item_type = parts[0].upper().strip()

        try:
            if item_type == "SCALE":
                PLAN_SCALE = float(parts[1])
            elif item_type == "NON_STRUCTURAL_WALL":
                x, y, length = float(parts[1]), float(parts[2]), float(parts[3])
                ori = parts[4].strip()
                draw_non_structural_wall(x, y, length, ori)
                PLAN_ELEMENTS.append(["NON_STRUCTURAL_WALL", x, y, length, ori])
            elif item_type == "STRUCTURAL_WALL":
                x, y, length = float(parts[1]), float(parts[2]), float(parts[3])
                ori = parts[4].strip()
                draw_structural_wall(x, y, length, 16, ori)
                PLAN_ELEMENTS.append(["STRUCTURAL_WALL", x, y, length, ori])
            elif item_type == "GABLE_END_WALL":
                x, y, length = float(parts[1]), float(parts[2]), float(parts[3])
                ori = parts[4].strip()
                draw_gable_end_wall(x, y, length, 20, ori)
                PLAN_ELEMENTS.append(["GABLE_END_WALL", x, y, length, ori])
            elif item_type == "SWING_DOOR":
                x, y, size = float(parts[1]), float(parts[2]), float(parts[3])
                ori = parts[4].strip()
                draw_swing_door(x, y, size, ori)
                PLAN_ELEMENTS.append(["SWING_DOOR", x, y, size, ori])
            elif item_type == "SLIDING_DOOR":
                x, y, length = float(parts[1]), float(parts[2]), float(parts[3])
                ori = parts[4].strip()
                draw_sliding_door(x, y, length, ori)
                PLAN_ELEMENTS.append(["SLIDING_DOOR", x, y, length, ori])
            elif item_type == "STANDARD_WINDOW":
                x, y, length = float(parts[1]), float(parts[2]), float(parts[3])
                ori = parts[4].strip()
                draw_standard_window(x, y, length, ori)
                PLAN_ELEMENTS.append(["STANDARD_WINDOW", x, y, length, ori])
            elif item_type == "SLIDING_WINDOW":
                x, y, length = float(parts[1]), float(parts[2]), float(parts[3])
                ori = parts[4].strip()
                draw_sliding_window(x, y, length, ori)
                PLAN_ELEMENTS.append(["SLIDING_WINDOW", x, y, length, ori])
            elif item_type == "BED":
                x, y = float(parts[1]), float(parts[2])
                b_type = parts[3].strip()
                ori = parts[4].strip()
                draw_bed(x, y, b_type, ori)
                PLAN_ELEMENTS.append(["BED", x, y, b_type, ori])
            elif item_type == "WARDROBE":
                x, y, length, depth = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                ori = parts[5].strip()
                draw_wardrobe(x, y, length, depth, ori)
                PLAN_ELEMENTS.append(["WARDROBE", x, y, length, depth, ori])
            elif item_type in ("ROOM_LABEL", "LABEL"):
                x, y, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                label_text = parts[5].strip()
                draw_room_label(x, y, w, h, label_text)
                PLAN_ELEMENTS.append(["ROOM_LABEL", x, y, w, h, label_text])
        except (ValueError, IndexError):
            print("[WARN] Skipping malformed record:", line)

    render_canvas_frame()
    print("[SUCCESS] Loaded " + str(len(PLAN_ELEMENTS)) + " elements from: " + filename)
    return True


# ==========================================
# 8. GUI BUTTON & TOOLBAR SYSTEM
# ==========================================

def draw_button(x, y, width, height, text, bg_color="#E0E0E0"):
    """Draws an interactive button box with centered text label."""
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
    turtle.goto(x + width / 2, y + (height / 2) - 5)
    turtle.write(text, align="center", font=("Arial", 8, "bold"))
    turtle.pensize(1)


def is_inside_box(click_x, click_y, x, y, width, height):
    """Checks whether a click coordinate falls within a rectangular box."""
    return (x <= click_x <= x + width) and (y <= click_y <= y + height)


def render_gui():
    """Renders the top toolbar panels and buttons cleanly separated from display."""
    turtle.tracer(0)

    # Top Toolbar background header panel (above display perimeter)
    go_to(-490, 280)
    turtle.fillcolor("#F4F4F6")
    turtle.pencolor("#CCCCCC")
    turtle.begin_fill()
    turtle.setheading(0)
    for _ in range(2):
        turtle.forward(980)
        turtle.left(90)
        turtle.forward(85)
        turtle.left(90)
    turtle.end_fill()

    # --- ROW 1: Structural & Openings (y = 328, height = 30) ---
    draw_button(-475, 328, 125, 30, "Non-Structural", "#D1E7DD")
    draw_button(-338, 328, 125, 30, "Structural Wall", "#D1E7DD")
    draw_button(-201, 328, 125, 30, "Gable-End Wall", "#D1E7DD")
    draw_button(-64,  328, 125, 30, "Swing Door",     "#CFF4FC")
    draw_button(73,   328, 125, 30, "Sliding Door",    "#CFF4FC")
    draw_button(210,  328, 125, 30, "Standard Window", "#E2D9F3")
    draw_button(347,  328, 125, 30, "Sliding Window",  "#E2D9F3")

    # --- ROW 2: Assets, Labels & System (y = 290, height = 30) ---
    draw_button(-475, 290, 110, 30, "Place Bed",      "#C8D7DA")
    draw_button(-355, 290, 110, 30, "Place Wardrobe", "#C8D7DA")
    draw_button(-235, 290, 110, 30, "Label Room",     "#FFF0F5")
    draw_button(-115, 290, 110, 30, "Set Scale",      "#FFE5D0")
    draw_button(5,    290, 110, 30, "Save Plan",      "#7fff00")
    draw_button(125,  290, 110, 30, "Load Plan",      "#7fff00")
    draw_button(245,  290, 110, 30, "Clear Canvas",   "#A5D7DA")
    draw_button(365,  290, 110, 30, "Exit",           "#ff2052")

    render_canvas_frame()
    turtle.tracer(1)


# ==========================================
# 9. USER PROMPT & ACTION HANDLERS
# ==========================================

def prompt_opening_inputs(title, default_len=100):
    screen = turtle.Screen()
    x = screen.numinput(title, "Start X:", default=0, minval=-600, maxval=600)
    if x is None:
        return None
    y = screen.numinput(title, "Start Y:", default=0, minval=-500, maxval=500)
    if y is None:
        return None
    length = screen.numinput(title, "Length / Width:", default=default_len, minval=10, maxval=1200)
    if length is None:
        return None
    ori = screen.textinput(title, "Orientation ('h' for horizontal, 'v' for vertical):")
    if ori is None or ori.lower().startswith('h'):
        orientation = 'horizontal'
    else:
        orientation = 'vertical'
    return x, y, length, orientation


def prompt_swing_door_inputs():
    screen = turtle.Screen()
    x = screen.numinput("Swing Door", "Hinge X coordinate:", default=0, minval=-600, maxval=600)
    if x is None:
        return None
    y = screen.numinput("Swing Door", "Hinge Y coordinate:", default=0, minval=-500, maxval=500)
    if y is None:
        return None
    size = screen.numinput("Swing Door", "Door width:", default=45, minval=15, maxval=300)
    if size is None:
        return None

    prompt_text = "Direction:\n1:Top-Right 2:Top-Left 3:Bottom-Right 4:Bottom-Left\n5:Right-Top 6:Right-Bottom 7:Left-Top 8:Left-Bottom"
    c = screen.textinput("Swing Door", prompt_text)
    mapping = {
        '1': 'top-right', '2': 'top-left', '3': 'bottom-right', '4': 'bottom-left',
        '5': 'right-top', '6': 'right-bottom', '7': 'left-top', '8': 'left-bottom'
    }
    orientation = mapping.get(c, 'top-right')
    return x, y, size, orientation


def handle_non_structural():
    data = prompt_opening_inputs("Non-Structural Wall", default_len=150)
    if data:
        x, y, length, ori = data
        draw_non_structural_wall(x, y, length, ori)
        PLAN_ELEMENTS.append(["NON_STRUCTURAL_WALL", x, y, length, ori])


def handle_structural():
    data = prompt_opening_inputs("Structural Wall", default_len=150)
    if data:
        x, y, length, ori = data
        draw_structural_wall(x, y, length, 16, ori)
        PLAN_ELEMENTS.append(["STRUCTURAL_WALL", x, y, length, ori])


def handle_gable():
    data = prompt_opening_inputs("Gable-End Wall", default_len=150)
    if data:
        x, y, length, ori = data
        draw_gable_end_wall(x, y, length, 20, ori)
        PLAN_ELEMENTS.append(["GABLE_END_WALL", x, y, length, ori])


def handle_swing_door():
    data = prompt_swing_door_inputs()
    if data:
        x, y, size, ori = data
        draw_swing_door(x, y, size, ori)
        PLAN_ELEMENTS.append(["SWING_DOOR", x, y, size, ori])


def handle_sliding_door():
    data = prompt_opening_inputs("Sliding Door", default_len=100)
    if data:
        x, y, length, ori = data
        draw_sliding_door(x, y, length, ori)
        PLAN_ELEMENTS.append(["SLIDING_DOOR", x, y, length, ori])


def handle_standard_window():
    data = prompt_opening_inputs("Standard Window", default_len=120)
    if data:
        x, y, length, ori = data
        draw_standard_window(x, y, length, ori)
        PLAN_ELEMENTS.append(["STANDARD_WINDOW", x, y, length, ori])


def handle_sliding_window():
    data = prompt_opening_inputs("Sliding Window", default_len=120)
    if data:
        x, y, length, ori = data
        draw_sliding_window(x, y, length, ori)
        PLAN_ELEMENTS.append(["SLIDING_WINDOW", x, y, length, ori])


def handle_place_bed():
    screen = turtle.Screen()
    b_type = screen.textinput("Place Bed", "Choose bed type:\n'q' for Queen Bed\n's' for Single Bed:")
    if not b_type:
        return
    bed_type = "single" if b_type.lower().startswith('s') else "queen"

    x = screen.numinput("Place Bed", "Bottom-Left X coordinate:", default=0, minval=-600, maxval=600)
    if x is None:
        return
    y = screen.numinput("Place Bed", "Bottom-Left Y coordinate:", default=0, minval=-500, maxval=500)
    if y is None:
        return
    ori_input = screen.textinput("Place Bed", "Orientation ('v' for vertical, 'h' for horizontal):")
    ori = "horizontal" if (ori_input and ori_input.lower().startswith('h')) else "vertical"

    draw_bed(x, y, bed_type, ori)
    PLAN_ELEMENTS.append(["BED", x, y, bed_type, ori])


def handle_place_wardrobe():
    screen = turtle.Screen()
    x = screen.numinput("Place Wardrobe", "Bottom-Left X coordinate:", default=0, minval=-600, maxval=600)
    if x is None:
        return
    y = screen.numinput("Place Wardrobe", "Bottom-Left Y coordinate:", default=0, minval=-500, maxval=500)
    if y is None:
        return
    length = screen.numinput("Place Wardrobe", "Wardrobe Length:", default=120, minval=30, maxval=600)
    if length is None:
        return
    depth = screen.numinput("Place Wardrobe", "Wardrobe Depth:", default=60, minval=20, maxval=200)
    if depth is None:
        return
    ori_input = screen.textinput("Place Wardrobe", "Orientation ('h' for horizontal, 'v' for vertical):")
    ori = "vertical" if (ori_input and ori_input.lower().startswith('v')) else "horizontal"

    draw_wardrobe(x, y, length, depth, ori)
    PLAN_ELEMENTS.append(["WARDROBE", x, y, length, depth, ori])


def start_room_label_mode():
    """Activates interactive boundary selection mode for labeling a room."""
    global LABEL_MODE_ACTIVE, LABEL_CORNER_1
    LABEL_MODE_ACTIVE = True
    LABEL_CORNER_1 = None
    print("\n[INFO] Room Label Mode Activated.")
    print("-> Click on the FIRST corner of the room boundary on canvas.")


def handle_label_click(click_x, click_y):
    """Processes clicks when boundary selection mode is active."""
    global LABEL_MODE_ACTIVE, LABEL_CORNER_1
    ux = to_user_x(click_x)
    uy = to_user_y(click_y)

    if LABEL_CORNER_1 is None:
        LABEL_CORNER_1 = (ux, uy)
        go_to(click_x, click_y)
        turtle.dot(6, "red")
        print("-> Corner 1 set at (" + str(round(ux, 1)) + ", " + str(round(uy, 1)) + ").")
        print("-> Now click on the OPPOSITE corner of the room boundary.")
    else:
        x1, y1 = LABEL_CORNER_1
        x2, y2 = ux, uy

        bx = min(x1, x2)
        by = min(y1, y2)
        bw = abs(x2 - x1)
        bh = abs(y2 - y1)

        LABEL_MODE_ACTIVE = False
        LABEL_CORNER_1 = None

        if bw < 5 or bh < 5:
            print("[WARN] Boundary too small. Room label cancelled.")
            return

        screen = turtle.Screen()
        room_name = screen.textinput("Room Label", "Enter room name (e.g., MASTER BEDROOM, KITCHEN):")
        if not room_name or not room_name.strip():
            print("[WARN] No room name entered. Cancelled.")
            return

        room_name = room_name.strip().upper()
        draw_room_label(bx, by, bw, bh, room_name)
        PLAN_ELEMENTS.append(["ROOM_LABEL", bx, by, bw, bh, room_name])
        print("[SUCCESS] Labeled room: '" + room_name + "' at (" +
              str(round(bx, 1)) + ", " + str(round(by, 1)) + ") size (" +
              str(round(bw, 1)) + " x " + str(round(bh, 1)) + ")")


def handle_set_scale():
    global PLAN_SCALE
    screen = turtle.Screen()
    new_scale = screen.numinput("Set Scale", "Enter scale factor (e.g. 0.5, 0.75, 1.0):",
                                default=PLAN_SCALE, minval=0.1, maxval=3.0)
    if new_scale and new_scale != PLAN_SCALE:
        PLAN_SCALE = new_scale
        turtle.clear()
        render_gui()
        for item in PLAN_ELEMENTS:
            itype = item[0]
            if itype == "NON_STRUCTURAL_WALL":
                draw_non_structural_wall(item[1], item[2], item[3], item[4])
            elif itype == "STRUCTURAL_WALL":
                draw_structural_wall(item[1], item[2], item[3], 16, item[4])
            elif itype == "GABLE_END_WALL":
                draw_gable_end_wall(item[1], item[2], item[3], 20, item[4])
            elif itype == "SWING_DOOR":
                draw_swing_door(item[1], item[2], item[3], item[4])
            elif itype == "SLIDING_DOOR":
                draw_sliding_door(item[1], item[2], item[3], item[4])
            elif itype == "STANDARD_WINDOW":
                draw_standard_window(item[1], item[2], item[3], item[4])
            elif itype == "SLIDING_WINDOW":
                draw_sliding_window(item[1], item[2], item[3], item[4])
            elif itype == "BED":
                draw_bed(item[1], item[2], item[3], item[4])
            elif itype == "WARDROBE":
                draw_wardrobe(item[1], item[2], item[3], item[4], item[5])
            elif itype in ("ROOM_LABEL", "LABEL"):
                draw_room_label(item[1], item[2], item[3], item[4], item[5])
        render_canvas_frame()


def handle_save_plan():
    screen = turtle.Screen()
    filename = screen.textinput("Save Floor Plan", "Enter filename to save (e.g., my_floor_plan.txt):")
    if filename and filename.strip():
        save_plan_to_file(filename.strip())


def handle_load_plan():
    screen = turtle.Screen()
    filename = screen.textinput("Load Floor Plan", "Enter filename to load (e.g., plan_4room_typical.txt):")
    if filename and filename.strip():
        load_plan_from_file(filename.strip())


def handle_clear():
    global PLAN_ELEMENTS, LABEL_MODE_ACTIVE, LABEL_CORNER_1
    turtle.clear()
    PLAN_ELEMENTS = []
    LABEL_MODE_ACTIVE = False
    LABEL_CORNER_1 = None
    render_gui()


def handle_exit():
    turtle.bye()


# ==========================================
# 10. CLICK EVENT DISPATCHER (NO CLASS / NO LAMBDA)
# ==========================================

def on_canvas_click(click_x, click_y):
    """Processes mouse clicks for toolbar buttons or canvas boundary selection."""
    global LABEL_MODE_ACTIVE

    # If currently in Room Label selection mode, route click to label handler
    # strictly within the display canvas area (click_y <= 260)
    if LABEL_MODE_ACTIVE and click_y <= 260:
        handle_label_click(click_x, click_y)
        return

    # Row 1: Structural & Openings (y: 328 to 358)
    if is_inside_box(click_x, click_y, -475, 328, 125, 30):
        handle_non_structural()
    elif is_inside_box(click_x, click_y, -338, 328, 125, 30):
        handle_structural()
    elif is_inside_box(click_x, click_y, -201, 328, 125, 30):
        handle_gable()
    elif is_inside_box(click_x, click_y, -64, 328, 125, 30):
        handle_swing_door()
    elif is_inside_box(click_x, click_y, 73, 328, 125, 30):
        handle_sliding_door()
    elif is_inside_box(click_x, click_y, 210, 328, 125, 30):
        handle_standard_window()
    elif is_inside_box(click_x, click_y, 347, 328, 125, 30):
        handle_sliding_window()

    # Row 2: Assets, Labels & System (y: 290 to 320)
    elif is_inside_box(click_x, click_y, -475, 290, 110, 30):
        handle_place_bed()
    elif is_inside_box(click_x, click_y, -355, 290, 110, 30):
        handle_place_wardrobe()
    elif is_inside_box(click_x, click_y, -235, 290, 110, 30):
        start_room_label_mode()
    elif is_inside_box(click_x, click_y, -115, 290, 110, 30):
        handle_set_scale()
    elif is_inside_box(click_x, click_y, 5, 290, 110, 30):
        handle_save_plan()
    elif is_inside_box(click_x, click_y, 125, 290, 110, 30):
        handle_load_plan()
    elif is_inside_box(click_x, click_y, 245, 290, 110, 30):
        handle_clear()
    elif is_inside_box(click_x, click_y, 365, 290, 110, 30):
        handle_exit()


# ==========================================
# 11. MAIN PROGRAM ENTRY
# ==========================================

def main():
    turtle.setup(1000, 750)
    turtle.title("HDB Floor Plan Designer ")
    turtle.speed(0)
    turtle.hideturtle()

    render_gui()

    screen = turtle.Screen()
    screen.onscreenclick(on_canvas_click)

    turtle.done()


if __name__ == "__main__":
    main()
