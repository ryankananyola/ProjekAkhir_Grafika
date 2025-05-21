import pygame
import math
import sys

pygame.init()
screen = pygame.display.set_mode((1150, 700))
pygame.display.set_caption("Paint 2D Transformasi")
clock = pygame.time.Clock()

# Warna
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

# Variabel untuk drag & drop
dragging = False
drag_offset = [0, 0]

font = pygame.font.SysFont(None, 24)

button_panel = [
    {"label": "Bintang", "action": "add_star"},
    {"label": "Oval", "action": "add_oval"},
    {"label": "Rect", "action": "add_rect"},
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

button_rects = []
for i, b in enumerate(button_panel):
    rect = pygame.Rect(20, 20 + i * 40, 160, 32)
    button_rects.append((rect, b))

color_rects = []
for i, color in enumerate(colors):
    rect = pygame.Rect(200 + i * 45, 20, 40, 40)
    color_rects.append((rect, color))

def draw_buttons():
    for rect, b in button_rects:
        if b["action"] == last_button_action:
            pygame.draw.rect(screen, (100, 200, 255), rect, border_radius=6)
        else:
            pygame.draw.rect(screen, GRAY, rect, border_radius=6)
        pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
        label = font.render(b["label"], True, BLACK)
        screen.blit(label, label.get_rect(center=rect.center))

def draw_color_choices():
    label = font.render("Pilih Warna:", True, BLACK)
    screen.blit(label, (200, 70))
    for rect, color in color_rects:
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

def draw_help_panel():
    help_texts = [
        "== Petunjuk Penggunaan:",
        "",
        "== Tambah Objek:",
        "   - Bintang / Oval / Rect",
        "",
        "== Ubah Warna:",
        "   - Isi Warna: ubah warna dalam objek",
        "   - Border Warna: ubah warna pinggir objek",
        "",
        "== Transformasi:",
        "   - Perbesar / Perkecil objek",
        "   - Putar Kiri / Kanan (bintang & oval)",
        "   - Geser (tombol panah)",
        "",
        "== Lainnya:",
        "   - Duplikat objek terpilih",
        "   - Hapus objek terpilih (atau tekan Delete)",
        "   - Klik warna untuk mengganti sesuai mode",
        "   - Klik objek untuk memilih",
        "   - Drag objek dengan mouse"
    ]

    panel_x = 720
    panel_y = 20
    panel_width = 400
    panel_height = 450

    pygame.draw.rect(screen, (230, 230, 230), (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

    y = panel_y + 10
    for text in help_texts:
        rendered_text = font.render(text, True, BLACK)
        screen.blit(rendered_text, (panel_x + 10, y))
        y += 22

def draw_star(obj):
    x, y = obj["pos"]
    scale = obj["scale"]
    angle = obj["angle"]
    points = []
    for i in range(5):
        theta = math.radians(i * 144 + angle)
        points.append((x + scale * math.cos(theta), y + scale * math.sin(theta)))
    pygame.draw.polygon(screen, obj["color"], points)
    pygame.draw.polygon(screen, obj["border_color"], points, 2)

def draw_oval(obj):
    rect = obj["rect"]
    surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.ellipse(surface, obj["color"], (0, 0, rect.width, rect.height))
    pygame.draw.ellipse(surface, obj["border_color"], (0, 0, rect.width, rect.height), 2)
    rotated_surface = pygame.transform.rotate(surface, obj.get("angle", 0))
    rotated_rect = rotated_surface.get_rect(center=rect.center)
    screen.blit(rotated_surface, rotated_rect.topleft)

def draw_rect(obj):
    pygame.draw.rect(screen, obj["color"], obj["rect"])
    pygame.draw.rect(screen, obj["border_color"], obj["rect"], 2)

def handle_action(action):
    global selected_index, selected_color_type
    if action.startswith("add"):
        if action == "add_star":
            objects.append({"type": "star", "pos": [300, 300], "scale": 40, "angle": 0, "color": YELLOW, "border_color": BLACK})
        elif action == "add_oval":
            objects.append({"type": "oval", "rect": pygame.Rect(300, 300, 80, 50), "angle": 0, "color": CYAN, "border_color": BLACK})
        elif action == "add_rect":
            objects.append({"type": "rect", "rect": pygame.Rect(300, 300, 70, 70), "color": RED, "border_color": BLACK})
        selected_index = len(objects) - 1
    elif selected_index != -1:
        obj = objects[selected_index]
        if action == "color_fill":
            selected_color_type = "fill"
        elif action == "color_border":
            selected_color_type = "border"
        elif action == "scale_up":
            if obj["type"] == "star": obj["scale"] += 5
            else: obj["rect"].inflate_ip(10, 10)
        elif action == "scale_down":
            if obj["type"] == "star": obj["scale"] = max(10, obj["scale"] - 5)
            else: obj["rect"].inflate_ip(-10, -10)
        elif action == "rotate_left" and "angle" in obj:
            obj["angle"] -= 10
        elif action == "rotate_right" and "angle" in obj:
            obj["angle"] += 10
        elif action == "move_left":
            if obj["type"] == "star": obj["pos"][0] -= 10
            else: obj["rect"].x -= 10
        elif action == "move_right":
            if obj["type"] == "star": obj["pos"][0] += 10
            else: obj["rect"].x += 10
        elif action == "move_up":
            if obj["type"] == "star": obj["pos"][1] -= 10
            else: obj["rect"].y -= 10
        elif action == "move_down":
            if obj["type"] == "star": obj["pos"][1] += 10
            else: obj["rect"].y += 10
        elif action == "duplicate":
            copy = obj.copy()
            if copy["type"] == "star":
                copy["pos"] = [copy["pos"][0] + 20, copy["pos"][1] + 20]
            else:
                copy["rect"] = copy["rect"].copy().move(20, 20)
            objects.append(copy)
            selected_index = len(objects) - 1
        elif action == "delete":
            if objects:
                objects.pop(selected_index)
                selected_index = len(objects) - 1

running = True
while running:
    screen.fill(WHITE)
    workspace_rect = pygame.Rect(200, 120, 500, 500)
    pygame.draw.rect(screen, (245, 245, 245), workspace_rect)
    pygame.draw.rect(screen, BLACK, workspace_rect, 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            clicked_on_object = False
            for i in reversed(range(len(objects))):
                obj = objects[i]
                if obj["type"] == "star":
                    x, y = obj["pos"]
                    scale = obj["scale"]
                    angle = obj["angle"]
                    points = []
                    for j in range(5):
                        theta = math.radians(j * 144 + angle)
                        points.append((x + scale * math.cos(theta), y + scale * math.sin(theta)))
                    box = pygame.Rect(x - scale, y - scale, scale * 2, scale * 2)
                    if box.collidepoint(event.pos):
                        selected_index = i
                        clicked_on_object = True
                        break
                else:
                    if obj["rect"].collidepoint(event.pos):
                        selected_index = i
                        clicked_on_object = True
                        break

            if clicked_on_object:
                dragging = True
                obj = objects[selected_index]
                if obj["type"] == "star":
                    drag_offset[0] = obj["pos"][0] - event.pos[0]
                    drag_offset[1] = obj["pos"][1] - event.pos[1]
                else:
                    drag_offset[0] = obj["rect"].x - event.pos[0]
                    drag_offset[1] = obj["rect"].y - event.pos[1]
            else:
                dragging = False

            if not clicked_on_object:
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

        elif event.type == pygame.MOUSEMOTION and dragging and selected_index != -1:
            obj = objects[selected_index]
            new_x = event.pos[0] + drag_offset[0]
            new_y = event.pos[1] + drag_offset[1]
            if obj["type"] == "star":
                obj["pos"][0] = new_x
                obj["pos"][1] = new_y
            else:
                obj["rect"].x = new_x
                obj["rect"].y = new_y

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.KEYDOWN and selected_index != -1:
            obj = objects[selected_index]
            if event.key == pygame.K_LEFT:
                if obj["type"] == "star": obj["pos"][0] -= 10
                else: obj["rect"].x -= 10
            elif event.key == pygame.K_RIGHT:
                if obj["type"] == "star": obj["pos"][0] += 10
                else: obj["rect"].x += 10
            elif event.key == pygame.K_UP:
                if obj["type"] == "star": obj["pos"][1] -= 10
                else: obj["rect"].y -= 10
            elif event.key == pygame.K_DOWN:
                if obj["type"] == "star": obj["pos"][1] += 10
                else: obj["rect"].y += 10
            elif event.key == pygame.K_DELETE:
                objects.pop(selected_index)
                selected_index = len(objects) - 1

    for i, obj in enumerate(objects):
        if obj["type"] == "star":
            draw_star(obj)
        elif obj["type"] == "oval":
            draw_oval(obj)
        elif obj["type"] == "rect":
            draw_rect(obj)

    draw_buttons()
    draw_color_choices()
    draw_help_panel()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
