import pygame
import math
import sys

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

font = pygame.font.SysFont(None, 24)

# UI tombol
button_panel = [
    {"label": "Bintang", "action": "add_star"},
    {"label": "Oval", "action": "add_oval"},
    {"label": "Rect", "action": "add_rect"},
    {"label": "Kerucut 3D", "action": "add_cone"},
    {"label": "Limas Segitiga 3D", "action": "add_pyramid"},
    {"label": "Isi Warna", "action": "color_fill"},
    {"label": "Border Warna", "action": "color_border"},
    {"label": "Perbesar", "action": "scale_up"},
    {"label": "Perkecil", "action": "scale_down"},
    {"label": "Putar Kiri", "action": "rotate_left"},
    {"label": "Putar Kanan", "action": "rotate_right"},
    {"label": "Geser Kiri", "action": "move_left"},
    {"label": "Geser Kanan", "action": "move_right"},
    {"label": "Geser Atas", "action": "move_up"},
    {"label": "Geser Bawah", "action": "move_down"},
    {"label": "Duplikat", "action": "duplicate"},
    {"label": "Hapus", "action": "delete"}
]

button_rects = [(pygame.Rect(20, 20 + i * 40, 160, 32), b) for i, b in enumerate(button_panel)]
color_rects = [(pygame.Rect(200 + i * 45, 20, 40, 40), color) for i, color in enumerate(colors)]

def draw_buttons():
    for rect, b in button_rects:
        pygame.draw.rect(screen, (100, 200, 255) if b["action"] == last_button_action else GRAY, rect, border_radius=6)
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
        screen.blit(font.render(b["label"], True, BLACK), font.render(b["label"], True, BLACK).get_rect(center=rect.center))

def draw_color_choices():
    screen.blit(font.render("Pilih Warna:", True, BLACK), (200, 70))
    for rect, color in color_rects:
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

def draw_help_panel():
    help_texts = [
        "== Petunjuk Penggunaan:",
        "Tambahkan bentuk dari panel kiri",
        "Gunakan transformasi untuk memodifikasi objek",
        "Klik dan drag objek untuk memindahkan",
    ]
    pygame.draw.rect(screen, (230, 230, 230), (720, 20, 400, 450))
    pygame.draw.rect(screen, BLACK, (720, 20, 400, 450), 2)
    for i, text in enumerate(help_texts):
        screen.blit(font.render(text, True, BLACK), (730, 30 + i * 22))

def rotate_point_3d(x, y, z, angle):
    rad = math.radians(angle)
    cosa, sina = math.cos(rad), math.sin(rad)
    return x * cosa + z * sina, y, -x * sina + z * cosa

def project_point(x, y, z):
    # Proyeksi perspektif sederhana
    return x - z * 0.5, y - z * 0.3

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
    pos, scale, angle = obj["pos"], obj["scale"], obj["angle"]
    base = [rotate_point_3d(scale * math.cos(math.radians(i * 360 / 20)),
                            0,
                            scale * math.sin(math.radians(i * 360 / 20)),
                            angle) for i in range(20)]
    apex = rotate_point_3d(0, scale * 1.5, 0, angle)
    base_2d = [project_point(*pt) for pt in base]
    apex_2d = project_point(*apex)
    base_2d = [(pos[0] + x, pos[1] - y) for x, y in base_2d]
    apex_2d = (pos[0] + apex_2d[0], pos[1] - apex_2d[1])

    # Arsiran sisi-sisi ke apex
    for pt in base_2d[::2]:
        pygame.draw.polygon(screen, obj["color"], [apex_2d, pt, base_2d[(base_2d.index(pt) + 2) % len(base_2d)]])
        pygame.draw.polygon(screen, obj["border_color"], [apex_2d, pt, base_2d[(base_2d.index(pt) + 2) % len(base_2d)]], 1)

    # Dasar lingkaran
    pygame.draw.polygon(screen, obj["color"], base_2d)
    pygame.draw.polygon(screen, obj["border_color"], base_2d, 2)

def draw_pyramid(obj):
    pos, scale, angle = obj["pos"], obj["scale"], obj["angle"]
    verts = [
        (0, scale * 1.5, 0),  # apex
        (-scale, 0, -scale),
        (scale, 0, -scale),
        (scale, 0, scale),
        (-scale, 0, scale)
    ]
    rot = [rotate_point_3d(*v, angle) for v in verts]
    proj = [project_point(*v) for v in rot]
    proj = [(pos[0] + x, pos[1] - y) for x, y in proj]

    # Sisi segitiga (arsiran)
    for i in range(1, 5):
        pygame.draw.polygon(screen, obj["color"], [proj[0], proj[i], proj[i % 4 + 1]])
        pygame.draw.polygon(screen, obj["border_color"], [proj[0], proj[i], proj[i % 4 + 1]], 2)

    # Dasar limas
    pygame.draw.polygon(screen, obj["color"], proj[1:])
    pygame.draw.polygon(screen, obj["border_color"], proj[1:], 2)

def handle_action(action):
    global selected_index, selected_color_type
    if action.startswith("add"):
        if action == "add_star":
            objects.append({"type": "star", "pos": [300, 300], "scale": 40, "angle": 0, "color": YELLOW, "border_color": BLACK})
        elif action == "add_oval":
            objects.append({"type": "oval", "rect": pygame.Rect(300, 300, 80, 50), "angle": 0, "color": CYAN, "border_color": BLACK})
        elif action == "add_rect":
            objects.append({"type": "rect", "rect": pygame.Rect(300, 300, 70, 70), "color": RED, "border_color": BLACK})
        elif action == "add_cone":
            objects.append({"type": "cone", "pos": [300, 300], "scale": 40, "angle": 0, "color": ORANGE, "border_color": BLACK})
        elif action == "add_pyramid":
            objects.append({"type": "pyramid", "pos": [300, 300], "scale": 40, "angle": 0, "color": GREEN, "border_color": BLACK})
        selected_index = len(objects) - 1
    elif selected_index != -1:
        obj = objects[selected_index]
        if action == "color_fill":
            selected_color_type = "fill"
        elif action == "color_border":
            selected_color_type = "border"
        elif action in ["scale_up", "scale_down"]:
            delta = 5 if action == "scale_up" else -5
            if obj["type"] in ("star", "cone", "pyramid"):
                obj["scale"] = max(10, obj["scale"] + delta)
            else:
                obj["rect"].inflate_ip(delta * 2, delta * 2)
        elif action in ["rotate_left", "rotate_right"] and "angle" in obj:
            obj["angle"] += -10 if action == "rotate_left" else 10
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
        elif action == "duplicate":
            new = obj.copy()
            if "rect" in obj:
                new["rect"] = obj["rect"].copy().move(20, 20)
            else:
                new["pos"] = [obj["pos"][0] + 20, obj["pos"][1] + 20]
            objects.append(new)
            selected_index = len(objects) - 1
        elif action == "delete":
            objects.pop(selected_index)
            selected_index = len(objects) - 1 if objects else -1

# Game loop utama
running = True
while running:
    screen.fill(WHITE)
    pygame.draw.rect(screen, (245, 245, 245), (200, 120, 500, 500))
    pygame.draw.rect(screen, BLACK, (200, 120, 500, 500), 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            clicked = False
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
            if not clicked:
                dragging = False
                for rect, b in button_rects:
                    if rect.collidepoint(event.pos):
                        handle_action(b["action"])
                        last_button_action = b["action"]
                for rect, color in color_rects:
                    if rect.collidepoint(event.pos) and selected_index != -1:
                        if selected_color_type == "fill":
                            objects[selected_index]["color"] = color
                        else:
                            objects[selected_index]["border_color"] = color
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging and selected_index != -1:
            obj = objects[selected_index]
            if "pos" in obj:
                obj["pos"] = [event.pos[0] + drag_offset[0], event.pos[1] + drag_offset[1]]
            else:
                obj["rect"].x = event.pos[0] + drag_offset[0]
                obj["rect"].y = event.pos[1] + drag_offset[1]
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DELETE and selected_index != -1:
                objects.pop(selected_index)
                selected_index = len(objects) - 1 if objects else -1

    draw_buttons()
    draw_color_choices()
    draw_help_panel()

    for obj in objects:
        if obj["type"] == "star": draw_star(obj)
        elif obj["type"] == "oval": draw_oval(obj)
        elif obj["type"] == "rect": draw_rect(obj)
        elif obj["type"] == "cone": draw_cone(obj)
        elif obj["type"] == "pyramid": draw_pyramid(obj)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
