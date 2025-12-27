import numpy as np
import cv2
import kociemba

CUBE_SEPARATION = 100
CELL_SIZE = 50
def draw_cells(frame, start_x, start_y):
    for row in range(3):
        for col in range(3):
            x1, y1 = start_x + row * CELL_SIZE, start_y + col * CELL_SIZE
            w, h = x1 + CELL_SIZE, y1 + CELL_SIZE
            frame = cv2.rectangle(frame, (x1, y1), (w, h), (0, 0, 0), 2)

def draw_test_cells(frame, colors, start_x, start_y):
    for i in range(len(colors)):
        row = i // 3
        col = i % 3

        x1, y1 = start_x + col * CELL_SIZE, start_y + row * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE

        color = colors[i]
        color_rect = colors_bgr.get(color, (0, 0, 0))

        frame = cv2.rectangle(frame, (x1, y1), (x2, y2), color_rect, -1)

def detect_color(hsv, masks_dict, start_x, start_y):
    colors_scores = {}
    detected_colors = []

    for row in range(3):
        for col in range(3):
            x1 = start_x + col * CELL_SIZE
            y1 = start_y + row * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            for color, mask in masks_dict.items():
                region = mask[y1:y2, x1:x2]
                score = np.sum(region > 0)
                colors_scores[color] = score

            color = max(colors_scores, key=colors_scores.get)
            detected_colors.append(color)

    return detected_colors

def get_kociemba_str(face_colors):
    order = "URFDLB"
    res = []
    for face in order:
        res.append("".join(face_colors[face]))

    return "".join(res)

def format_text(solved_str, num_per_row):
    res = []

    for i in range(1, len(solved_str) + 1):
        res.append(solved_str[i - 1])
        if i % num_per_row == 0:
            res.append("\n")

    return res

def add_spacing(text_list, ch_ignore):
    res = []
    
    for item in text_list:
        if item != ch_ignore:
            res.append(item.ljust(2, " "))

        else:
            res.append(ch_ignore)
            
    return res

def draw_text_solved_str(frame, text_list):
    text_list = add_spacing(text_list, "\n")
    current = []
    res = []

    for item in text_list:
        if item == "\n":
            res.append(current)
            current = []

        else:
            current.append(item)

    (text_width, text_height), baseline = cv2.getTextSize(" ".join(res[0]), font, font_scale, thickness)
    num_rows = len(res)
    starting_x = (WIDTH - text_width) // 2
    starting_y = (HEIGHT - text_height * (num_rows - 1)) // 2

    for i in range(len(res)):
        row_text = " ".join(res[i])
        cv2.putText(frame, row_text, (starting_x, starting_y + text_height * i + 20 * i), font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)



face_text = ["Upper face", "Right face", "Front face", "Down face", "Left face", "Back face"]
face_colors = {}
face_counter = 0
faces = "URFDLB"

colors_bgr = {
    "R": (0, 0, 255),
    "L": (0, 165, 255),
    "D": (0, 255, 255),
    "F": (47, 255, 173),
    "B": (255, 191, 0),
    "U": (255, 255, 255)
}

text = face_text[0]
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
thickness = 2

solved = False

video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    WIDTH = int(video.get(3))
    HEIGHT = int(video.get(4))

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    kernal = np.ones((5, 5), "uint8")
    
    red_lower = np.array([136, 87, 20], np.uint8)
    red_upper = np.array([180, 255, 255], np.uint8)
    red_mask = cv2.inRange(hsv, red_lower, red_upper)
    red_mask = cv2.dilate(red_mask, kernal)

    green_lower = np.array([40, 50, 20])
    green_upper = np.array([75, 255, 255])
    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    green_mask = cv2.dilate(green_mask, kernal)
    
    blue_lower = np.array([80, 80, 20], np.uint8)
    blue_upper = np.array([135, 255, 255], np.uint8)
    blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
    blue_mask = cv2.dilate(blue_mask, kernal)

    yellow_lower = np.array([15, 150, 20], np.uint8)
    yellow_upper = np.array([35, 255, 255], np.uint8)
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    yellow_mask = cv2.dilate(yellow_mask, kernal)

    orange_lower = np.array([0, 150, 20], np.uint8)
    orange_upper = np.array([14, 255, 255], np.uint8)
    orange_mask = cv2.inRange(hsv, orange_lower, orange_upper)
    orange_mask = cv2.dilate(orange_mask, kernal)

    white_lower = np.array([0, 0, 130], np.uint8)
    white_upper = np.array([180, 50, 255], np.uint8)
    white_mask = cv2.inRange(hsv, white_lower, white_upper)
    white_mask = cv2.dilate(white_mask, kernal)

    masks_dict = {
        "R": red_mask,
        "L": orange_mask,
        "B": blue_mask,
        "F": green_mask,
        "D": yellow_mask,
        "U": white_mask
    }
    
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    start_capture_grid_x, start_capture_grid_y = (WIDTH - CELL_SIZE * 6 - CUBE_SEPARATION) // 2, (HEIGHT - CELL_SIZE * 3) // 2
    start_test_cube_x, start_test_cube_y = start_capture_grid_x + CELL_SIZE * 3 + CUBE_SEPARATION, start_capture_grid_y

    res = detect_color(hsv, masks_dict, start_capture_grid_x, start_capture_grid_y)

    if not solved:
        draw_cells(frame, start_capture_grid_x, start_capture_grid_y)
        draw_test_cells(frame, res, start_test_cube_x, start_test_cube_y)
        draw_cells(frame, start_test_cube_x, start_test_cube_y)

        center_x = start_capture_grid_x + (CELL_SIZE * 6 + CUBE_SEPARATION) // 2
        center_y = start_capture_grid_y
    else:
        center_x = WIDTH // 2
        center_y = HEIGHT // 2

    text_x = center_x - text_width // 2
    text_y = center_y - 10
    
    if not solved:
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)
    else:
        draw_text_solved_str(frame, format_text(solved_text, 5))

    cv2.imshow("frame", frame)
    
    key = cv2.waitKey(1)
    if key == ord(" "):
        face_colors[faces[face_counter]] = res
        face_counter += 1

        if face_counter >= len(faces):
            print("All faces scanned!")
            cube_str = get_kociemba_str(face_colors)

            try:
                solved_pattern = kociemba.solve(cube_str)
                solved = True
                solved_text = solved_pattern.split(" ")
                
            except ValueError:
                print("Invalid cube")
                face_counter = 0
                text = face_text[0]

        else:
            text = face_text[face_counter]

    elif key == ord("r"):
        solved = False
        face_counter = 0
        text = face_text[face_counter]

    elif key == ord("q"):
        break

video.release()
cv2.destroyAllWindows()