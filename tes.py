import pygame
import math
import sys
import colorsys

pygame.init()
screen = pygame.display.set_mode((1150, 700))
pygame.display.set_caption("Paint 2D Transformasi")
clock = pygame.time.Clock()

# Warna dasar
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)

colors = [YELLOW, RED, GREEN, CYAN, BLUE, MAGENTA, ORANGE]
objects = []
selected_index = -1
selected_color_type = "fill"
last_button_action = None
dragging = False
drag_offset = [0, 0]
custom_color = (128, 128, 128)
show_color_picker = False
hue = 0
saturation = 0.5
value = 0.5

font = pygame.font.SysFont(None, 24)
large_font = pygame.font.SysFont(None, 36)

# Canvas area
canvas_rect = pygame.Rect(200, 120, 500, 500)

# UI tombol
button_panel = [
    {"label": "Bintang", "action": "add_star"},
    {"label": "Oval", "action": "add_oval"},
    {"label": "Rect", "action": "add_rect"},
    {"label": "Kerucut 3D", "action": "add_cone"},
    {"label": "Limas 3D", "action": "add_pyramid"},
    {"label": "Isi", "action": "color_fill"},
    {"label": "Border", "action": "color_border"},
    {"label": "Warna Kustom", "action": "custom_color"},
    {"label": "Putar Kiri", "action": "rotate_left"},
    {"label": "Putar Kanan", "action": "rotate_right"},
    {"label": "Rot 3D Atas", "action": "rotate_3d_up"},
    {"label": "Rot 3D Bawah", "action": "rotate_3d_down"},
    {"label": "Rot 3D Kiri", "action": "rotate_3d_left"},
    {"label": "Rot 3D Kanan", "action": "rotate_3d_right"}
]

# Tombol duplikasi dan hapus di bawah canvas
bottom_buttons = [
    {"label": "Duplikat", "action": "duplicate"},
    {"label": "Hapus", "action": "delete"}
]

button_rects = [(pygame.Rect(20, 20 + i * 40, 160, 32), b) for i, b in enumerate(button_panel)]
bottom_button_rects = [(pygame.Rect(200 + i * 160, 640, 150, 40), b) for i, b in enumerate(bottom_buttons)]
# Color palette di atas (tetap)
color_rects = [(pygame.Rect(200 + i * 45, 20, 40, 40), color) for i, color in enumerate(colors)]
custom_color_rect = pygame.Rect(200 + len(colors) * 45 + 10, 20, 70, 40)
# Palet warna HSV untuk warna kustom di kiri bawah
custom_palette_rect = pygame.Rect(20, canvas_rect.bottom + 20, 200, 40)
color_picker_rect = pygame.Rect(720, 480, 250, 180)
hue_slider_rect = pygame.Rect(color_picker_rect.left + 20, color_picker_rect.top + 40, 210, 20)
sv_rect = pygame.Rect(color_picker_rect.left + 20, color_picker_rect.top + 70, 150, 90)
ok_button_rect = pygame.Rect(color_picker_rect.right - 70, color_picker_rect.bottom - 40, 60, 30)

# Tambahkan variabel global untuk animasi
animate_3d = True  # Jika ingin bisa di-toggle, bisa tambahkan tombol nanti
# Hapus tombol Perbesar dan Perkecil dari button_panel
button_panel = [
    {"label": "Bintang", "action": "add_star"},
    {"label": "Oval", "action": "add_oval"},
    {"label": "Rect", "action": "add_rect"},
    {"label": "Kerucut 3D", "action": "add_cone"},
    {"label": "Limas 3D", "action": "add_pyramid"},
    {"label": "Isi", "action": "color_fill"},
    {"label": "Border", "action": "color_border"},
    {"label": "Warna Kustom", "action": "custom_color"},
    {"label": "Putar Kiri", "action": "rotate_left"},
    {"label": "Putar Kanan", "action": "rotate_right"},
    {"label": "Rot 3D Atas", "action": "rotate_3d_up"},
    {"label": "Rot 3D Bawah", "action": "rotate_3d_down"},
    {"label": "Rot 3D Kiri", "action": "rotate_3d_left"},
    {"label": "Rot 3D Kanan", "action": "rotate_3d_right"}
]

# Geser slider ke kanan, di luar canvas
slider_rect = pygame.Rect(750, 500, 260, 18)
slider_knob_radius = 13
slider_dragging = False

# Hapus tombol geser dari button_panel
button_panel = [b for b in button_panel if not b["action"].startswith("move_")]

# Tambahkan area panah di kanan (di bawah slider)
arrow_panel_rect = pygame.Rect(830, 540, 100, 100)
arrow_btn_size = 38
arrow_btn_gap = 8
arrow_btns = {
    "up": pygame.Rect(arrow_panel_rect.centerx - arrow_btn_size//2, arrow_panel_rect.top, arrow_btn_size, arrow_btn_size),
    "down": pygame.Rect(arrow_panel_rect.centerx - arrow_btn_size//2, arrow_panel_rect.bottom - arrow_btn_size, arrow_btn_size, arrow_btn_size),
    "left": pygame.Rect(arrow_panel_rect.left, arrow_panel_rect.centery - arrow_btn_size//2, arrow_btn_size, arrow_btn_size),
    "right": pygame.Rect(arrow_panel_rect.right - arrow_btn_size, arrow_panel_rect.centery - arrow_btn_size//2, arrow_btn_size, arrow_btn_size)
}

def draw_buttons():
    mouse_pos = pygame.mouse.get_pos()
    for rect, b in button_rects:
        is_hover = rect.collidepoint(mouse_pos)
        is_active = b["action"] == last_button_action
        # Gradient background
        grad_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for y in range(rect.height):
            blend = y / rect.height
            if is_active:
                color1 = (60, 160, 255)
                color2 = (120, 210, 255)
            elif is_hover:
                color1 = (120, 210, 255)
                color2 = (180, 240, 255)
            else:
                color1 = (200, 200, 200)
                color2 = (160, 180, 200)
            r = int(color1[0] * (1-blend) + color2[0] * blend)
            g = int(color1[1] * (1-blend) + color2[1] * blend)
            b_ = int(color1[2] * (1-blend) + color2[2] * blend)
            pygame.draw.line(grad_surface, (r, g, b_), (0, y), (rect.width, y))
        # Shadow
        shadow_rect = rect.move(4, 4)
        pygame.draw.rect(screen, (180, 180, 180), shadow_rect, border_radius=14)
        # Button
        screen.blit(grad_surface, rect.topleft)
        pygame.draw.rect(screen, (100, 150, 200) if is_active else (120, 180, 220) if is_hover else (160, 180, 200), rect, 2, border_radius=14)
        # Glow effect
        if is_hover or is_active:
            glow = pygame.Surface((rect.width+8, rect.height+8), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (100,200,255,60), glow.get_rect())
            screen.blit(glow, (rect.x-4, rect.y-4), special_flags=pygame.BLEND_RGBA_ADD)
        # Text
        text_surface = font.render(b["label"], True, (30, 30, 60) if is_active else (30, 60, 90))
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    for rect, b in bottom_button_rects:
        is_hover = rect.collidepoint(mouse_pos)
        is_active = b["action"] == last_button_action
        grad_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for y in range(rect.height):
            blend = y / rect.height
            if is_active:
                color1 = (60, 160, 255)
                color2 = (120, 210, 255)
            elif is_hover:
                color1 = (120, 210, 255)
                color2 = (180, 240, 255)
            else:
                color1 = (200, 200, 200)
                color2 = (160, 180, 200)
            r = int(color1[0] * (1-blend) + color2[0] * blend)
            g = int(color1[1] * (1-blend) + color2[1] * blend)
            b_ = int(color1[2] * (1-blend) + color2[2] * blend)
            pygame.draw.line(grad_surface, (r, g, b_), (0, y), (rect.width, y))
        shadow_rect = rect.move(4, 4)
        pygame.draw.rect(screen, (180, 180, 180), shadow_rect, border_radius=14)
        screen.blit(grad_surface, rect.topleft)
        pygame.draw.rect(screen, (100, 150, 200) if is_active else (120, 180, 220) if is_hover else (160, 180, 200), rect, 2, border_radius=14)
        if is_hover or is_active:
            glow = pygame.Surface((rect.width+8, rect.height+8), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (100,200,255,60), glow.get_rect())
            screen.blit(glow, (rect.x-4, rect.y-4), special_flags=pygame.BLEND_RGBA_ADD)
        text_surface = font.render(b["label"], True, (30, 30, 60) if is_active else (30, 60, 90))
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

def draw_color_choices():
    mouse_pos = pygame.mouse.get_pos()
    # Palet warna utama di atas
    for rect, color in color_rects:
        is_hover = rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
        if selected_index != -1:
            obj = objects[selected_index]
            current_obj_color = obj.get("color") if selected_color_type == "fill" else obj.get("border_color")
            if current_obj_color == color:
                pygame.draw.rect(screen, (80, 180, 255), rect, 4, border_radius=8)
        if is_hover:
            pygame.draw.rect(screen, (80, 180, 255), rect, 3, border_radius=8)

    # Tombol warna kustom di atas
    pygame.draw.rect(screen, custom_color, custom_color_rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, custom_color_rect, 2, border_radius=8)
    screen.blit(font.render("Kustom", True, BLACK), (custom_color_rect.x + 5, custom_color_rect.y + 12))
    rgb_text = f"RGB: {custom_color[0]}, {custom_color[1]}, {custom_color[2]}"
    screen.blit(font.render(rgb_text, True, BLACK), (custom_color_rect.x, custom_color_rect.y + 45))
    color_type_text = f"Warna: {'Isi' if selected_color_type == 'fill' else 'Border'}"
    screen.blit(font.render(color_type_text, True, BLACK), (200, color_rects[0][0].bottom + 10))

def draw_color_picker():
    if not show_color_picker:
        return None, None, None, None

    # Tempatkan color picker di dalam canvas, di bawah objek
    picker_width, picker_height = 250, 180
    picker_x = canvas_rect.left + (canvas_rect.width - picker_width) // 2
    picker_y = canvas_rect.bottom - picker_height - 20
    picker_rect = pygame.Rect(picker_x, picker_y, picker_width, picker_height)

    pygame.draw.rect(screen, WHITE, picker_rect)
    pygame.draw.rect(screen, BLACK, picker_rect, 2)
    screen.blit(large_font.render("Pilih Warna", True, BLACK), (picker_rect.left + 10, picker_rect.top + 10))

    # Preview warna besar
    preview_rect = pygame.Rect(picker_rect.left + 190, picker_rect.top + 20, 50, 50)
    pygame.draw.rect(screen, custom_color, preview_rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, preview_rect, 2, border_radius=8)
    screen.blit(font.render("Preview", True, BLACK), (preview_rect.x, preview_rect.y + 55))

    # Label slider dan SV
    hue_slider_rect_local = pygame.Rect(picker_rect.left + 20, picker_rect.top + 40, 130, 20)
    sv_rect_local = pygame.Rect(picker_rect.left + 20, picker_rect.top + 70, 130, 90)
    ok_button_rect_local = pygame.Rect(picker_rect.right - 70, picker_rect.bottom - 40, 60, 30)
    screen.blit(font.render("Hue", True, BLACK), (hue_slider_rect_local.left, hue_slider_rect_local.top - 22))
    screen.blit(font.render("Saturation/Value", True, BLACK), (sv_rect_local.left, sv_rect_local.top - 22))

    # Hue slider
    pygame.draw.rect(screen, GRAY, hue_slider_rect_local)
    for x in range(hue_slider_rect_local.width):
        h = x / hue_slider_rect_local.width
        r, g, b = colorsys.hsv_to_rgb(h, 1, 1)
        color = (int(r * 255), int(g * 255), int(b * 255))
        pygame.draw.line(screen, color, (hue_slider_rect_local.left + x, hue_slider_rect_local.top), (hue_slider_rect_local.left + x, hue_slider_rect_local.bottom))
    hue_indicator_x = hue_slider_rect_local.left + int(hue * hue_slider_rect_local.width)
    pygame.draw.polygon(screen, BLACK, [(hue_indicator_x - 5, hue_slider_rect_local.top - 5),
                                        (hue_indicator_x + 5, hue_slider_rect_local.top - 5),
                                        (hue_indicator_x, hue_slider_rect_local.top - 10)])
    pygame.draw.polygon(screen, BLACK, [(hue_indicator_x - 5, hue_slider_rect_local.bottom + 5),
                                        (hue_indicator_x + 5, hue_slider_rect_local.bottom + 5),
                                        (hue_indicator_x, hue_slider_rect_local.bottom + 10)])

    # Saturation-Value square
    for y in range(sv_rect_local.height):
        for x in range(sv_rect_local.width):
            s = x / sv_rect_local.width
            v = 1 - y / sv_rect_local.height
            r, g, b = colorsys.hsv_to_rgb(hue, s, v)
            color = (int(r * 255), int(g * 255), int(b * 255))
            screen.set_at((sv_rect_local.left + x, sv_rect_local.top + y), color)
    sv_indicator_x = sv_rect_local.left + int(saturation * sv_rect_local.width)
    sv_indicator_y = sv_rect_local.top + int((1 - value) * sv_rect_local.height)
    pygame.draw.circle(screen, BLACK, (sv_indicator_x, sv_indicator_y), 6, 1)
    pygame.draw.circle(screen, WHITE, (sv_indicator_x, sv_indicator_y), 5)

    # OK button
    pygame.draw.rect(screen, GREEN, ok_button_rect_local)
    pygame.draw.rect(screen, BLACK, ok_button_rect_local, 2)
    ok_text = font.render("OK", True, BLACK)
    screen.blit(ok_text, ok_text.get_rect(center=ok_button_rect_local.center))

    # Update global rect agar event handler tetap berfungsi
    global color_picker_rect, hue_slider_rect, sv_rect, ok_button_rect
    color_picker_rect = picker_rect
    hue_slider_rect = hue_slider_rect_local
    sv_rect = sv_rect_local
    ok_button_rect = ok_button_rect_local

    return ok_button_rect, hue_slider_rect, sv_rect, (sv_indicator_x, sv_indicator_y)

def handle_color_picker_click(pos):
    global custom_color, hue, saturation, value, show_color_picker

    if not show_color_picker:
        return False

    if hue_slider_rect.collidepoint(pos):
        hue = (pos[0] - hue_slider_rect.left) / hue_slider_rect.width
        hue = max(0, min(1, hue))
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        custom_color = (int(r * 255), int(g * 255), int(b * 255))
        return True
    elif sv_rect.collidepoint(pos):
        saturation = (pos[0] - sv_rect.left) / sv_rect.width
        saturation = max(0, min(1, saturation))
        value = 1 - (pos[1] - sv_rect.top) / sv_rect.height
        value = max(0, min(1, value))
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        custom_color = (int(r * 255), int(g * 255), int(b * 255))
        return True
    elif ok_button_rect.collidepoint(pos):
        show_color_picker = False
        if selected_index != -1:
            if selected_color_type == "fill":
                objects[selected_index]["color"] = custom_color
            else:
                objects[selected_index]["border_color"] = custom_color
        return True

    return False

def draw_help_panel():
    help_texts = [
        "=== PETUNJUK PENGGUNAAN ===",
        "",
        "1. TAMBAH BENTUK:",
        "   - Pilih bentuk dari panel kiri",
        "   - Klik warna untuk mengubah warna",
        "   - Klik 'Warna Kustom' untuk memilih warna",
        "",
        "2. TRANSFORMASI (Objek Terpilih):",
        "   - Perbesar / Perkecil: Ubah ukuran",
        "   - Putar: Rotasi 2D",
        "   - Rotasi 3D: Untuk objek 3D",
        "   - Geser: Pindahkan objek",
        "",
        "3. KONTROL:",
        "   - Klik + tahan objek: Pindahkan",
        "   - Tombol panah: Geser halus",
        "   - Delete: Hapus objek terpilih",
        "",
        "4. LAINNYA:",
        "   - Duplikat: Salin objek terpilih",
        "   - Hapus: Hapus objek terpilih"
    ]
    panel_rect = pygame.Rect(720, 20, 400, 450)
    shadow_rect = panel_rect.move(5, 5)
    pygame.draw.rect(screen, (200, 200, 200), shadow_rect, border_radius=16)
    pygame.draw.rect(screen, (240, 240, 255), panel_rect, border_radius=16)
    pygame.draw.rect(screen, BLACK, panel_rect, 2, border_radius=16)
    y_offset = 30
    for text in help_texts:
        if text.startswith("===") or text.startswith("1.") or text.startswith("2.") or text.startswith("3.") or text.startswith("4."):
            screen.blit(font.render(text, True, (30, 30, 120)), (730, y_offset))
            y_offset += 25
        elif text == "":
            y_offset += 10
        else:
            screen.blit(font.render(text, True, (60, 60, 60)), (745, y_offset))
            y_offset += 22

def rotate_point_3d(x, y, z, angle_x, angle_y):
    rad_x = math.radians(angle_x)
    cosa_x, sina_x = math.cos(rad_x), math.sin(rad_x)
    y_rot = y * cosa_x - z * sina_x
    z_rot = y * sina_x + z * cosa_x

    rad_y = math.radians(angle_y)
    cosa_y, sina_y = math.cos(rad_y), math.sin(rad_y)
    x_rot = x * cosa_y + z_rot * sina_y
    z_rot_final = -x * sina_y + z_rot * cosa_y

    return x_rot, y_rot, z_rot_final

def project_point(x, y, z):
    return x - z * 0.5, y - z * 0.3

def constrain_to_canvas(obj):
    if "pos" in obj:
        obj["pos"][0] = max(canvas_rect.left + 20, min(canvas_rect.right - 20, obj["pos"][0]))
        obj["pos"][1] = max(canvas_rect.top + 20, min(canvas_rect.bottom - 20, obj["pos"][1]))
    else:
        if obj["rect"].left < canvas_rect.left:
            obj["rect"].left = canvas_rect.left
        if obj["rect"].right > canvas_rect.right:
            obj["rect"].right = canvas_rect.right
        if obj["rect"].top < canvas_rect.top:
            obj["rect"].top = canvas_rect.top
        if obj["rect"].bottom > canvas_rect.bottom:
            obj["rect"].bottom = canvas_rect.bottom

def draw_star(obj):
    x, y, scale, angle = *obj["pos"], obj["scale"], obj["angle"]
    points = [(x + scale * math.cos(math.radians(i * 144 + angle)),
               y + scale * math.sin(math.radians(i * 144 + angle))) for i in range(5)]
    pygame.draw.polygon(screen, obj["color"], points)
    pygame.draw.polygon(screen, obj["border_color"], points, 2)

def draw_oval(obj):
    rect = obj["rect"]
    surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.ellipse(surface, obj["color"], (0, 0, rect.width, rect.height))
    pygame.draw.ellipse(surface, obj["border_color"], (0, 0, rect.width, rect.height), 2)
    rotated = pygame.transform.rotate(surface, obj["angle"])
    screen.blit(rotated, rotated.get_rect(center=rect.center))

def draw_rect(obj):
    pygame.draw.rect(screen, obj["color"], obj["rect"])
    pygame.draw.rect(screen, obj["border_color"], obj["rect"], 2)

def draw_cone(obj):
    pos, scale, angle_x, angle_y = obj["pos"], obj["scale"], obj.get("angle_x", 0), obj.get("angle_y", 0)
    base = [rotate_point_3d(scale * math.cos(math.radians(i * 360 / 20)),
                            0,
                            scale * math.sin(math.radians(i * 360 / 20)),
                            angle_x, angle_y) for i in range(20)]
    apex = rotate_point_3d(0, scale * 1.5, 0, angle_x, angle_y)
    base_2d = [project_point(*pt) for pt in base]
    apex_2d = project_point(*apex)
    base_2d = [(pos[0] + x, pos[1] - y) for x, y in base_2d]
    apex_2d = (pos[0] + apex_2d[0], pos[1] - apex_2d[1])

    # Draw shadow
    shadow_offset = 10
    shadow_color = (120, 120, 120, 80)
    shadow_points = [(x + shadow_offset, y + shadow_offset) for x, y in base_2d]
    shadow_apex = (apex_2d[0] + shadow_offset, apex_2d[1] + shadow_offset)
    shadow_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    for pt in base_2d[::2]:
        pygame.draw.polygon(shadow_surface, shadow_color, [shadow_apex, (pt[0]+shadow_offset, pt[1]+shadow_offset), (base_2d[(base_2d.index(pt) + 2) % len(base_2d)][0]+shadow_offset, base_2d[(base_2d.index(pt) + 2) % len(base_2d)][1]+shadow_offset)])
    pygame.draw.polygon(shadow_surface, shadow_color, shadow_points)
    screen.blit(shadow_surface, (0, 0))

    # Draw cone faces with gradient
    for i, pt in enumerate(base_2d):
        next_pt = base_2d[(i + 1) % len(base_2d)]
        face_color = tuple(min(255, int(c * (0.8 + 0.2 * (i % 2)))) for c in obj["color"])
        pygame.draw.polygon(screen, face_color, [apex_2d, pt, next_pt])
        pygame.draw.polygon(screen, obj["border_color"], [apex_2d, pt, next_pt], 1)
    pygame.draw.polygon(screen, obj["color"], base_2d)
    pygame.draw.polygon(screen, obj["border_color"], base_2d, 2)

def draw_pyramid(obj):
    pos, scale, angle_x, angle_y = obj["pos"], obj["scale"], obj.get("angle_x", 0), obj.get("angle_y", 0)
    verts = [
        (0, scale * 1.5, 0),  # apex
        (-scale, 0, -scale),
        (scale, 0, -scale),
        (scale, 0, scale),
        (-scale, 0, scale)
    ]
    rot = [rotate_point_3d(*v, angle_x, angle_y) for v in verts]
    proj = [project_point(*v) for v in rot]
    proj = [(pos[0] + x, pos[1] - y) for x, y in proj]

    # Draw shadow
    shadow_offset = 10
    shadow_color = (120, 120, 120, 80)
    shadow_proj = [(x + shadow_offset, y + shadow_offset) for x, y in proj]
    shadow_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    for i in range(1, 5):
        pygame.draw.polygon(shadow_surface, shadow_color, [shadow_proj[0], shadow_proj[i], shadow_proj[i % 4 + 1]])
    pygame.draw.polygon(shadow_surface, shadow_color, shadow_proj[1:])
    screen.blit(shadow_surface, (0, 0))

    # Draw pyramid faces with gradient
    for i in range(1, 5):
        face_color = tuple(min(255, int(c * (0.8 + 0.2 * (i % 2)))) for c in obj["color"])
        pygame.draw.polygon(screen, face_color, [proj[0], proj[i], proj[i % 4 + 1]])
        pygame.draw.polygon(screen, obj["border_color"], [proj[0], proj[i], proj[i % 4 + 1]], 2)
    pygame.draw.polygon(screen, obj["color"], proj[1:])
    pygame.draw.polygon(screen, obj["border_color"], proj[1:], 2)

def handle_action(action):
    global selected_index, selected_color_type, show_color_picker, custom_color

    if action.startswith("add"):
        if action == "add_star":
            objects.append({"type": "star", "pos": [450, 370], "scale": 40, "angle": 0, "color": YELLOW, "border_color": BLACK})
        elif action == "add_oval":
            objects.append({"type": "oval", "rect": pygame.Rect(400, 350, 80, 50), "angle": 0, "color": CYAN, "border_color": BLACK})
        elif action == "add_rect":
            objects.append({"type": "rect", "rect": pygame.Rect(400, 350, 70, 70), "color": RED, "border_color": BLACK})
        elif action == "add_cone":
            objects.append({"type": "cone", "pos": [450, 370], "scale": 40, "angle_x": 0, "angle_y": 0, "color": ORANGE, "border_color": BLACK})
        elif action == "add_pyramid":
            objects.append({"type": "pyramid", "pos": [450, 370], "scale": 40, "angle_x": 0, "angle_y": 0, "color": GREEN, "border_color": BLACK})
        
    elif action == "custom_color":
        show_color_picker = not show_color_picker
    elif selected_index != -1:
        obj = objects[selected_index]
        if action == "color_fill":
            selected_color_type = "fill"
        elif action == "color_border":
            selected_color_type = "border"
        elif action in ["rotate_left", "rotate_right"] and "angle" in obj:
            obj["angle"] += -10 if action == "rotate_left" else 10
        elif action.startswith("rotate_3d_") and obj["type"] in ("cone", "pyramid"):
            if "up" in action:
                obj["angle_x"] = (obj.get("angle_x", 0) - 10) % 360
            elif "down" in action:
                obj["angle_x"] = (obj.get("angle_x", 0) + 10) % 360
            elif "left" in action:
                obj["angle_y"] = (obj.get("angle_y", 0) - 10) % 360
            elif "right" in action:
                obj["angle_y"] = (obj.get("angle_y", 0) + 10) % 360
        elif action.startswith("move_"):
            dx, dy = 0, 0
            if "left" in action: dx = -10
            if "right" in action: dx = 10
            if "up" in action: dy = -10
            if "down" in action: dy = 10
            if "rect" in obj:
                obj["rect"].move_ip(dx, dy)
            else:
                obj["pos"][0] += dx
                obj["pos"][1] += dy
            constrain_to_canvas(obj)
        elif action == "duplicate":
            new = obj.copy()
            if "rect" in obj:
                new["rect"] = obj["rect"].copy().move(20, 20)
            else:
                new["pos"] = [obj["pos"][0] + 20, obj["pos"][1] + 20]
            objects.append(new)
            selected_index = len(objects) - 1
            constrain_to_canvas(new)
        elif action == "delete":
            objects.pop(selected_index)
            selected_index = len(objects) - 1 if objects else -1

def draw_scale_slider():
    if selected_index == -1:
        return
    obj = objects[selected_index]
    # Tentukan nilai skala
    if "scale" in obj:
        scale = obj["scale"]
        min_scale, max_scale = 10, 150
    else:
        # Untuk objek rect/oval, gunakan lebar sebagai skala
        scale = obj["rect"].width
        min_scale, max_scale = 20, 300
    t = (scale - min_scale) / (max_scale - min_scale)
    knob_x = slider_rect.left + int(t * slider_rect.width)
    # Draw bar
    pygame.draw.rect(screen, (200,220,255), slider_rect, border_radius=9)
    pygame.draw.rect(screen, (120,160,220), slider_rect, 2, border_radius=9)
    # Draw fill
    fill_rect = pygame.Rect(slider_rect.left, slider_rect.top, knob_x - slider_rect.left, slider_rect.height)
    pygame.draw.rect(screen, (120,180,255), fill_rect, border_radius=9)
    pygame.draw.circle(screen, (80,140,220), (knob_x, slider_rect.centery), slider_knob_radius)
    pygame.draw.circle(screen, (255,255,255), (knob_x, slider_rect.centery), slider_knob_radius-4)
    pygame.draw.circle(screen, (80,140,220), (knob_x, slider_rect.centery), slider_knob_radius-8)
    # Label dan value di kanan slider
    scale_label = font.render("Skala", True, (30,60,90))
    screen.blit(scale_label, (slider_rect.left, slider_rect.top-24))
    val_label = font.render(str(int(scale)), True, (30,60,90))
    screen.blit(val_label, (slider_rect.right+10, slider_rect.top-2))

def draw_arrow_buttons():
    if selected_index == -1:
        return
    for direction, rect in arrow_btns.items():
        # Button bg
        pygame.draw.rect(screen, (200,220,255), rect, border_radius=12)
        pygame.draw.rect(screen, (120,160,220), rect, 2, border_radius=12)
        # Draw arrow
        cx, cy = rect.center
        if direction == "up":
            pts = [(cx, cy-10), (cx-10, cy+8), (cx+10, cy+8)]
        elif direction == "down":
            pts = [(cx, cy+10), (cx-10, cy-8), (cx+10, cy-8)]
        elif direction == "left":
            pts = [(cx-10, cy), (cx+8, cy-10), (cx+8, cy+10)]
        elif direction == "right":
            pts = [(cx+10, cy), (cx-8, cy-10), (cx-8, cy+10)]
        pygame.draw.polygon(screen, (60,100,180), pts)

# Game loop utama
running = True
while running:
    screen.fill((230, 235, 250))
    canvas_shadow = canvas_rect.move(8, 8)
    pygame.draw.rect(screen, (200, 200, 200), canvas_shadow, border_radius=18)
    pygame.draw.rect(screen, (245, 245, 255), canvas_rect, border_radius=18)
    pygame.draw.rect(screen, BLACK, canvas_rect, 2, border_radius=18)

    # ANIMASI: update sudut rotasi objek 3D
    if animate_3d:
        for obj in objects:
            if obj["type"] == "cone" or obj["type"] == "pyramid":
                obj["angle_y"] = (obj.get("angle_y", 0) + 1) % 360

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            clicked = False

            if show_color_picker:
                handle_color_picker_click(event.pos)
                clicked = True

            # Cek arrow button lebih awal
            if not clicked and selected_index != -1:
                for direction, rect in arrow_btns.items():
                    if rect.collidepoint(event.pos):
                        obj = objects[selected_index]
                        dx, dy = 0, 0
                        if direction == "up": dy = -10
                        elif direction == "down": dy = 10
                        elif direction == "left": dx = -10
                        elif direction == "right": dx = 10
                        if "rect" in obj:
                            obj["rect"].move_ip(dx, dy)
                        else:
                            obj["pos"][0] += dx
                            obj["pos"][1] += dy
                        constrain_to_canvas(obj)
                        clicked = True
                        break

            if not clicked:
                for i in reversed(range(len(objects))):
                    obj = objects[i]
                    box = pygame.Rect(obj["pos"][0]-40, obj["pos"][1]-40, 80, 80) if "pos" in obj else obj["rect"]
                    if box.collidepoint(event.pos):
                        selected_index = i
                        dragging = True
                        if "pos" in obj:
                            drag_offset = [obj["pos"][0] - event.pos[0], obj["pos"][1] - event.pos[1]]
                        else:
                            drag_offset = [obj["rect"].x - event.pos[0], obj["rect"].y - event.pos[1]]
                        clicked = True
                        break

                if not clicked and not show_color_picker:
                    dragging = False
                    for rect, b in button_rects + bottom_button_rects:
                        if rect.collidepoint(event.pos):
                            handle_action(b["action"])
                            last_button_action = b["action"]
                    for rect, color in color_rects:
                        if rect.collidepoint(event.pos) and selected_index != -1:
                            if selected_color_type == "fill":
                                objects[selected_index]["color"] = color
                            else:
                                objects[selected_index]["border_color"] = color
                    if custom_color_rect.collidepoint(event.pos) and selected_index != -1:
                        handle_action("custom_color")
            # Cek slider
            if selected_index != -1 and slider_rect.collidepoint(event.pos):
                slider_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            slider_dragging = False
            # Tambahan: pastikan mouse tidak stuck pada slider
            pygame.event.clear(pygame.MOUSEMOTION)
        elif event.type == pygame.MOUSEMOTION and dragging and selected_index != -1:
            obj = objects[selected_index]
            if "pos" in obj:
                obj["pos"] = [event.pos[0] + drag_offset[0], event.pos[1] + drag_offset[1]]
            else:
                obj["rect"].x = event.pos[0] + drag_offset[0]
                obj["rect"].y = event.pos[1] + drag_offset[1]
            constrain_to_canvas(obj)
        elif event.type == pygame.MOUSEMOTION and slider_dragging and selected_index != -1:
            obj = objects[selected_index]
            min_scale, max_scale = (10, 150) if "scale" in obj else (20, 300)
            rel = (event.pos[0] - slider_rect.left) / slider_rect.width
            rel = max(0, min(1, rel))
            new_scale = int(min_scale + rel * (max_scale - min_scale))
            if "scale" in obj:
                obj["scale"] = new_scale
            else:
                center = obj["rect"].center
                obj["rect"].width = new_scale
                obj["rect"].height = int(new_scale * (obj["rect"].height / obj["rect"].width))
                obj["rect"].center = center
            constrain_to_canvas(obj)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DELETE and selected_index != -1:
                objects.pop(selected_index)
                selected_index = len(objects) - 1 if objects else -1
            elif selected_index != -1:
                obj = objects[selected_index]
                if event.key == pygame.K_LEFT:
                    if "rect" in obj:
                        obj["rect"].move_ip(-10, 0)
                    else:
                        obj["pos"][0] -= 10
                elif event.key == pygame.K_RIGHT:
                    if "rect" in obj:
                        obj["rect"].move_ip(10, 0)
                    else:
                        obj["pos"][0] += 10
                elif event.key == pygame.K_UP:
                    if "rect" in obj:
                        obj["rect"].move_ip(0, -10)
                    else:
                        obj["pos"][1] -= 10
                elif event.key == pygame.K_DOWN:
                    if "rect" in obj:
                        obj["rect"].move_ip(0, 10)
                    else:
                        obj["pos"][1] += 10
                constrain_to_canvas(obj)

    draw_buttons()
    draw_color_choices()
    draw_help_panel()

    for obj in objects:
        if obj["type"] == "star": draw_star(obj)
        elif obj["type"] == "oval": draw_oval(obj)
        elif obj["type"] == "rect": draw_rect(obj)
        elif obj["type"] == "cone": draw_cone(obj)
        elif obj["type"] == "pyramid": draw_pyramid(obj)

    if show_color_picker:
        draw_color_picker()
    draw_scale_slider()
    draw_arrow_buttons()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()