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
color = 180


def clamp(a, mn, mx):
    if a < mn:
        a = int(mn)
    elif a > mx:
        a = int(mx)
    return int(a)


def writePos(_x, _y, a=True, s=0):
    x, y = clamp(_y, 0, size[0]-1), clamp(_x, 0, size[1]-1)
    img[x, y] = int(s)
    # print("Write in", x, y)
    if a:
        lasts.append((x, y))


def interpolate(width=1):
    if len(lasts) < 2:
        return

    p1 = lasts.pop()
    p2 = lasts.pop()
    lasts.append(p1)
     
    for w in range(0, width):
        m = (p2[0] - p1[0]) / 150, (p2[1] - p1[1]) / 150
        p = [p1[0], p1[1]]

        for i in range(150):
            p[0] += m[0]
            p[1] += m[1]
            writePos(p[1] + w, p[0], False, color)


def sieve(x, y):
    if len(lasts) == 0:
        print("LOX")
        return True

    r = size[0]
    # for p in lasts:
    p = lasts[-1]
    d = math.hypot(x - p[0], y - p[1])
    print(d, x - p[0], y - p[1])
    r = min(r, d)
    # print(r)
    return 0 < r < 300
    # return True


def update():
    cv2.imwrite("output.png", img)


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
        x_tip = int(results.multi_hand_landmarks[0].landmark[tip].x *
                flippedRGB.shape[1])
        y_tip = int(results.multi_hand_landmarks[0].landmark[tip].y *
                flippedRGB.shape[0])
        cv2.circle(flippedRGB,(x_tip, y_tip), 10, (255, 0, 0), -1)

        x2 = int(results.multi_hand_landmarks[0].landmark[0].x *
                    flippedRGB.shape[1])
        y2 = int(results.multi_hand_landmarks[0].landmark[0].y *
                    flippedRGB.shape[0])
        cv2.circle(flippedRGB, (x2, y2), 10, (0, 255, 0), -1)

        if sieve(x_tip, y_tip):
            writePos(x_tip, y_tip, True, point_color)
            interpolate(lines_width)
    # переводим в BGR и показываем результат
    res_image = cv2.cvtColor(flippedRGB, cv2.COLOR_RGB2BGR)
    cv2.imshow("Hands", res_image)
    # cv2.imshow("Hands", flipped)

# освобождаем ресурсы
handsDetector.close()
if revert:
    img = np.fliplr(img)
update()
