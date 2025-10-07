import cv2
import mediapipe as mp
import pyautogui
import time

print("тут чет происходит")

# Инициализация MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Настройки
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

screen_w, screen_h = pyautogui.size()
print(f"📺 Разрешение экрана: {screen_w}x{screen_h}")

# Открываем камеру
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("все хрень вася")
    exit()

print("📹 камера работать")
print("🎮 РУКОВОДСТВО ПО ЖЕСТАМ:")
print("   ЛЕВАЯ РУКА:")
print("   👆 Указательный палец - ДВИЖЕНИЕ КУРСОРА")
print("   🤘 Указательный+мизинец - ПРАВАЯ КНОПКА")
print("   👆👆 Указательный+средний - ЛЕВЫЙ КЛИК (без перемещения)")
print("   ПРАВАЯ РУКА:")
print("   ✊ Кулак - СУПЕР БЫСТРАЯ ПРОКРУТКА")
print("   🚪 Нажмите 'Q' для выхода")

# Переменные для управления
last_click_time = 0
last_right_click_time = 0
last_scroll_time = 0
scroll_mode = False
last_scroll_y = None


def is_left_hand(hand_landmarks):
    """Определение левой руки"""
    wrist = hand_landmarks.landmark[0]
    pinky_mcp = hand_landmarks.landmark[17]
    return pinky_mcp.x > wrist.x


def is_right_hand(hand_landmarks):
    """Определение правой руки"""
    return not is_left_hand(hand_landmarks)


def is_fist(landmarks):
    """Определение жеста кулака"""
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    fingers_bent = 0
    for tip, pip in zip(tips, pips):
        if landmarks[tip].y > landmarks[pip].y:
            fingers_bent += 1

    return fingers_bent >= 3


def is_two_fingers(landmarks):
    """Жест двух пальцев """
    index_extended = landmarks[8].y < landmarks[6].y
    middle_extended = landmarks[12].y < landmarks[10].y
    ring_bent = landmarks[16].y > landmarks[14].y
    pinky_bent = landmarks[20].y > landmarks[18].y
    return index_extended and middle_extended and ring_bent and pinky_bent


def is_right_click_gesture(landmarks):
    """Жест для правой кнопки """
    index_extended = landmarks[8].y < landmarks[6].y
    pinky_extended = landmarks[20].y < landmarks[18].y
    middle_bent = landmarks[12].y > landmarks[10].y
    ring_bent = landmarks[16].y > landmarks[14].y
    return index_extended and pinky_extended and middle_bent and ring_bent


def is_pointing_gesture(landmarks):
    """Жест указательного пальца"""
    index_extended = landmarks[8].y < landmarks[6].y
    middle_bent = landmarks[12].y > landmarks[10].y
    ring_bent = landmarks[16].y > landmarks[14].y
    pinky_bent = landmarks[20].y > landmarks[18].y
    return index_extended and middle_bent and ring_bent and pinky_bent


def handle_scroll(current_y):
    """Крутись шайтан"""
    global last_scroll_y, last_scroll_time

    current_time = time.time()


    if last_scroll_y is None:
        last_scroll_y = current_y
        return


    delta_y = last_scroll_y - current_y


    if abs(delta_y) > 0.001:

        scroll_amount = int(delta_y * 800)


        if current_time - last_scroll_time > 0.03:
            pyautogui.scroll(scroll_amount)
            print(f"🚀 ПРОКРУТКА: {scroll_amount}")
            last_scroll_time = current_time


    last_scroll_y = current_y


try:
    while True:
        success, img = cap.read()
        if not success:
            break


        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        current_time = time.time()
        left_hand_detected = False
        right_hand_detected = False

        # Сбрасываем жесты
        left_gesture = "Нет"
        right_gesture = "Нет"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark


                if is_left_hand(hand_landmarks):
                    left_hand_detected = True
                    mp_drawing.draw_landmarks(
                        img, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                    )


                    index_tip = landmarks[8]
                    cursor_x = int(index_tip.x * screen_w)
                    cursor_y = int(index_tip.y * screen_h)


                    if is_right_click_gesture(landmarks):
                        left_gesture = "Правая кнопка"
                        if current_time - last_right_click_time > 0.5:
                            # Перемещаем курсор и делаем правый клик
                            pyautogui.moveTo(cursor_x, cursor_y)
                            pyautogui.rightClick()
                            print("право")
                            last_right_click_time = current_time

                    elif is_two_fingers(landmarks):
                        left_gesture = "Левый клик"
                        if current_time - last_click_time > 0.5:
                            # ТОЛЬКО КЛИК БЕЗ ПЕРЕМЕЩЕНИЯ КУРСОРА
                            pyautogui.click()
                            print("👆👆 Левый клик (без перемещения)")
                            last_click_time = current_time

                    elif is_pointing_gesture(landmarks):
                        left_gesture = "Движение"

                        pyautogui.moveTo(cursor_x, cursor_y)

                elif is_right_hand(hand_landmarks):
                    right_hand_detected = True
                    mp_drawing.draw_landmarks(
                        img, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                    )


                    middle_tip_y = landmarks[12].y


                    if is_fist(landmarks):
                        right_gesture = "🚀 Бистро"
                        scroll_mode = True
                        handle_scroll(middle_tip_y)
                    else:
                        right_gesture = "Нет"
                        scroll_mode = False
                        last_scroll_y = None


        if not right_hand_detected:
            scroll_mode = False
            last_scroll_y = None


        cv2.putText(img, f"ЛЕВАЯ: {left_gesture}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(img, f"ПРАВАЯ: {right_gesture}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


        scroll_status = "🚀 АКТИВНА" if scroll_mode else "ВЫКЛ"
        scroll_color = (0, 255, 255) if scroll_mode else (0, 0, 255)
        cv2.putText(img, f"ПРОКРУТКА: {scroll_status}", (10, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, scroll_color, 2)


        if scroll_mode:
            cv2.putText(img, "Двигайте рукой ВВЕРХ/ВНИЗ для прокрутки", (10, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow('Gesture Control - СУПЕР БЫСТРАЯ ПРОКРУТКА', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback

    traceback.print_exc()

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("пятница")