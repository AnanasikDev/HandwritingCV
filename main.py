import cv2
import mediapipe as mp
import numpy as np
import math

size = 480, 640 # 480, 640
img = np.ones(size) * 255
lasts = []
lines_width = 8
revert = False

point_color = 0
color = 120


def clamp(a, mn, mx):
    if a < mn:
        a = int(mn)
    elif a > mx:
        a = int(mx)
    return int(a)


def writePos(_x, _y, a=True, s=0):
    x, y = clamp(_y, 0, size[0]-1), clamp(_x, 0, size[1]-1)
    img[x, y] = int(s) # clamp(img[x, y] - int(s), 0, 255)
    # print("Write in", x, y)
    if a:
        lasts.append((x, y))


def interpolate(width=1, color=0):
    if len(lasts) < 2:
        return

    p1 = lasts.pop()
    p2 = lasts.pop()
    lasts.append(p1)

    l = abs(p2[0] - p1[0])
    if l == 0:
        return
    for w in range(0, width):
        m = p2[1] - p1[1]
        p = [p1[0], p1[1]]
        x = 1
        if p2[0] < p1[0]:
            x = -1

        for i in range(l):
            p[0] += x
            p[1] += m / l
            
            writePos(p[1] + w, p[0], False, color) #color


def sieve(x, y):
    return True
    if len(lasts) == 0:
        return True

    r = size[0]
    p = lasts[-1]
    d = math.hypot(x - p[0], y - p[1])
    print(d, x - p[0], y - p[1])
    r = min(r, d)
    return 0 < r < 300
    # return True


def update():
    cv2.imwrite("output.png", img)


def pos(results, tip):
    x_tip = int(results.multi_hand_landmarks[0].landmark[tip].x *
                flippedRGB.shape[1])
    y_tip = int(results.multi_hand_landmarks[0].landmark[tip].y *
                flippedRGB.shape[0])
    return x_tip, y_tip


WRITE = 0
ERASE = 1
MOVE = 2


def mode(x_thumb, y_thumb, x_mid, y_mid, x_tip, y_tip):
    mid_thumb = math.hypot(abs(x_thumb - x_mid), abs(y_thumb - y_mid))
    tip_mid = math.hypot(abs(x_tip - x_mid), abs(y_tip - y_mid))

    print(tip_mid)

    if tip_mid < 25:
        return ERASE
    elif mid_thumb >= 60:
        lasts.clear()
        return MOVE
    else:
        return WRITE


update()

# создаем детектор
handsDetector = mp.solutions.hands.Hands()
cap = cv2.VideoCapture(0)
while(cap.isOpened()):
    ret, frame = cap.read()
    if cv2.waitKey(1) & 0xFF == ord('q') or not ret:
       break
    flipped = np.fliplr(frame)
    # переводим его в формат RGB для распознавания
    flippedRGB = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)
    # Распознаем
    results = handsDetector.process(flippedRGB)
    # Рисуем распознанное, если распозналось
    if results.multi_hand_landmarks is not None:
        # нас интересует только подушечка указательного пальца (индекс 8)
        # нужно умножить координаты а размеры картинки
        tip = 8
        x_tip, y_tip = pos(results, tip)
        cv2.circle(flippedRGB,(x_tip, y_tip), 10, (255, 0, 0), -1)

        # wrist_x, wrist_y = pos(results, 0)
        # cv2.circle(flippedRGB, (wrist_x, wrist_y), 10, (0, 255, 0), -1)

        thumb_x, thumb_y = pos(results, 4)
        cv2.circle(flippedRGB, (thumb_x, thumb_y), 10, (0, 255, 255), -1)

        mid_x, mid_y = pos(results, 12)
        cv2.circle(flippedRGB, (mid_x, mid_y), 10, (255, 255, 0), -1)
        if sieve(x_tip, y_tip):
            if mode(thumb_x, thumb_y, mid_x, mid_y, x_tip, y_tip) == WRITE:
                writePos(x_tip, y_tip, True, point_color)
                interpolate(lines_width*2)
            if mode(thumb_x, thumb_y, mid_x, mid_y, x_tip, y_tip) == ERASE:
                writePos(x_tip, y_tip, True, 255)
                interpolate(lines_width*5, 255)

        # update()
        cv2.imshow("output", img)

    # переводим в BGR и показываем результат
    res_image = cv2.cvtColor(flippedRGB, cv2.COLOR_RGB2BGR)
    cv2.imshow("Hands", res_image)
    # update()
#     cv2.imshow("output", img)
    # cv2.imshow("Hands", flipped)

# освобождаем ресурсы
handsDetector.close()
if revert:
    img = np.fliplr(img)
update()
