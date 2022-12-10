import cv2
import mediapipe as mp
import numpy as np

size = 480, 640 # 480, 640
k = 1

img = np.ones(size) * 255

lasts = []


def clamp(a, mn, mx):
    if a < mn:
        a = mn
    elif a > mx:
        a = mx
    return a


def writePos(_x, _y, a=True, s=1):
    x, y = clamp(int(_y * k), 0, size[0]-1), clamp(int(_x * k), 0, size[1]-1)
    img[x, y] = s
    if a:
        lasts.append((x, y))


def interpolate():
    # print(len(lasts))
    if len(lasts) < 2:
        return
    p1 = lasts.pop()
    p2 = lasts.pop()
    lasts.append(p1)
    # print(len(lasts))

    m = (p2[0] - p1[0]) / 100, (p2[1] - p1[1]) / 100

    p = [p1[0], p1[1]]

    for i in range(100):
        p[0] += m[0]
        p[1] += m[1]
        writePos(p[1], p[0], False, 180)

    # print("interpolate,", m[0] * 100, m[1] * 100)


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
        x_tip = int(results.multi_hand_landmarks[0].landmark[8].x *
                flippedRGB.shape[1])
        y_tip = int(results.multi_hand_landmarks[0].landmark[8].y *
                flippedRGB.shape[0])
        cv2.circle(flippedRGB,(x_tip, y_tip), 10, (255, 0, 0), -1)
        pos = results.multi_hand_landmarks[0].landmark[0]
        writePos(pos.x * size[0], pos.y * size[1])
        interpolate()
        print(results.multi_hand_landmarks[0])
    # переводим в BGR и показываем результат
    res_image = cv2.cvtColor(flippedRGB, cv2.COLOR_RGB2BGR)
    cv2.imshow("Hands", res_image)
    update()

# освобождаем ресурсы
handsDetector.close()
update()
