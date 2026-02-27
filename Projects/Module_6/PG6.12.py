import pygame
import threading
import queue
import asyncio
from googletrans import Translator, LANGUAGES

# Инициализация Pygame
pygame.init()
WIDTH, HEIGHT = 850, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Переводчик с Pygame")
font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 18)
clock = pygame.time.Clock()

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (70, 130, 180)
GREEN = (100, 200, 100)
RED = (220, 60, 60)
LIGHT_BLUE = (230, 240, 255)

# Элементы интерфейса
input_box = pygame.Rect(50, 70, 750, 40)
lang_box = pygame.Rect(50, 150, 200, 40)
translate_btn = pygame.Rect(300, 150, 200, 40)
lang_list_btn = pygame.Rect(550, 150, 250, 40)
result_box = pygame.Rect(50, 230, 750, 350)

# Переменные состояния
input_text = ''
lang_code = 'en'
result_text = ''
active_input = None  # 'text' или 'lang'
translating = False
error_message = ''
show_lang_list = False
result_queue = queue.Queue()
last_click_time = 0  # Для защиты от двойного клика

# Создание переводчика (один экземпляр для всех переводов)
translator = Translator()


def run_async_translation(text, dest_lang):
    """Запускает асинхронный перевод в отдельном потоке"""

    async def async_translate():
        try:
            translation = await translator.translate(text, dest=dest_lang)
            return translation.text
        except Exception as e:
            return f"Ошибка перевода: {str(e)}"

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_translate())
    loop.close()
    return result


def translation_worker():
    """Поток для выполнения перевода"""
    global translating
    try:
        translated = run_async_translation(input_text, lang_code)
        result_queue.put(translated)
    except Exception as e:
        result_queue.put(f"Критическая ошибка: {str(e)}")
    finally:
        translating = False


def draw_multiline_text(surface, text, rect, font, color=BLACK):
    """Отрисовка многострочного текста в прямоугольнике"""
    words = text.split()
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] < rect.width - 20:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    lines.append(current_line)

    y_offset = rect.top + 10
    max_height = rect.bottom - 20
    for line in lines:
        if y_offset + font.get_height() > max_height:
            break
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (rect.left + 10, y_offset))
        y_offset += font.get_height() + 2


# Основной цикл
running = True
while running:
    current_time = pygame.time.get_ticks()
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Защита от двойного клика
            if current_time - last_click_time < 300:
                continue
            last_click_time = current_time

            # Обработка открытия/закрытия списка языков
            if lang_list_btn.collidepoint(event.pos):
                show_lang_list = not show_lang_list

            # Закрытие списка языков при клике вне его области
            elif show_lang_list:
                if not (50 <= event.pos[0] <= WIDTH - 50 and 100 <= event.pos[1] <= HEIGHT - 50):
                    show_lang_list = False

            # Активация полей ввода
            if input_box.collidepoint(event.pos):
                active_input = 'text'
                show_lang_list = False
            elif lang_box.collidepoint(event.pos):
                active_input = 'lang'
                show_lang_list = False
            else:
                active_input = None

            # Обработка нажатия кнопки перевода
            if translate_btn.collidepoint(event.pos) and not translating and input_text.strip():
                if lang_code not in LANGUAGES:
                    error_message = f"Ошибка: язык '{lang_code}' не поддерживается"
                    result_text = ''
                else:
                    translating = True
                    error_message = ''
                    thread = threading.Thread(target=translation_worker)
                    thread.daemon = True
                    thread.start()

        if event.type == pygame.KEYDOWN:
            if show_lang_list:
                # Закрытие списка языков по нажатию Esc
                if event.key == pygame.K_ESCAPE:
                    show_lang_list = False
                continue

            if active_input == 'text':
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    # Автоматический перевод при нажатии Enter
                    if lang_code in LANGUAGES and input_text.strip():
                        translating = True
                        error_message = ''
                        thread = threading.Thread(target=translation_worker)
                        thread.daemon = True
                        thread.start()
                elif event.unicode.isprintable() and len(input_text) < 500:
                    input_text += event.unicode

            if active_input == 'lang':
                if event.key == pygame.K_BACKSPACE:
                    lang_code = lang_code[:-1]
                elif event.unicode.isalpha() and len(lang_code) < 6:
                    lang_code += event.unicode.lower()

    # Проверка результатов из очереди
    while not result_queue.empty():
        result = result_queue.get()
        if result.startswith("Ошибка перевода") or result.startswith("Критическая ошибка"):
            error_message = result
            result_text = ''
        else:
            result_text = result
            error_message = ''

    # Очистка экрана
    screen.fill(WHITE)

    # Отрисовка элементов интерфейса
    # Заголовок
    title = font.render("PyGame Переводчик", True, BLUE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    # Поле ввода текста
    pygame.draw.rect(screen, BLUE if active_input == 'text' else GRAY, input_box, 2)
    display_text = input_text if len(input_text) <= 60 else input_text[:57] + "..."
    text_surface = font.render(display_text, True, BLACK)
    screen.blit(text_surface, (input_box.x + 10, input_box.y + 5))
    label = small_font.render("Введите текст для перевода:", True, BLACK)
    screen.blit(label, (50, 45))

    # Поле выбора языка
    pygame.draw.rect(screen, BLUE if active_input == 'lang' else GRAY, lang_box, 2)
    # Отображаем название языка, если код существует
    lang_display = LANGUAGES.get(lang_code, lang_code).capitalize() if lang_code else "Выберите язык"
    lang_surface = font.render(lang_display, True, BLACK)
    screen.blit(lang_surface, (lang_box.x + 10, lang_box.y + 5))
    lang_label = small_font.render("Язык перевода:", True, BLACK)
    screen.blit(lang_label, (50, 125))

    # Кнопка перевода
    btn_color = GREEN if not translating and input_text.strip() and lang_code in LANGUAGES else GRAY
    pygame.draw.rect(screen, btn_color, translate_btn)
    btn_text = font.render("Перевести" if not translating else "Перевод...", True, WHITE)
    screen.blit(btn_text, (translate_btn.x + (80 if not translating else 40), translate_btn.y + 5))

    # Кнопка списка языков
    pygame.draw.rect(screen, BLUE, lang_list_btn)
    lang_btn_text = font.render("Выбрать язык", True, WHITE)
    screen.blit(lang_btn_text, (lang_list_btn.x + 50, lang_list_btn.y + 5))

    # Блок результата
    pygame.draw.rect(screen, GRAY, result_box, 2)
    if translating:
        loading_text = font.render("Переводим...", True, BLUE)
        screen.blit(loading_text, (result_box.x + 10, result_box.y + 10))
    elif error_message:
        # Разбиваем длинные сообщения об ошибках
        error_lines = []
        if len(error_message) > 60:
            parts = error_message.split(":")
            error_lines.append(parts[0] + ":")
            error_lines.append(" ".join(parts[1:]))
        else:
            error_lines = [error_message]

        for i, line in enumerate(error_lines):
            error_surf = small_font.render(line, True, RED)
            screen.blit(error_surf, (result_box.x + 10, result_box.y + 10 + i * 25))
    elif result_text:
        draw_multiline_text(screen, result_text, result_box, font)
    else:
        placeholder = font.render("Результат перевода появится здесь...", True, (150, 150, 150))
        screen.blit(placeholder, (result_box.x + 10, result_box.y + 10))

    # Отображение списка языков
    if show_lang_list:
        # Полупрозрачный фон
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(WHITE)
        screen.blit(overlay, (0, 0))

        # Окно списка языков
        lang_window = pygame.Rect(50, 100, WIDTH - 100, HEIGHT - 200)
        pygame.draw.rect(screen, LIGHT_BLUE, lang_window)
        pygame.draw.rect(screen, BLUE, lang_window, 2)

        # Заголовок окна
        title = font.render("Доступные языки", True, BLACK)
        screen.blit(title, (lang_window.x + 10, lang_window.y + 10))

        # Список языков (в несколько колонок)
        lang_items = [(code, name) for code, name in LSANGUAGE.items()]
        #lang_items.sort(key=lambda x: x[1])  # Сортировка по названию

        col_width = (lang_window.width - 40) // 2
        max_items_per_col = 25

        # Разделение на две колонки
        mid_point = len(lang_items) // 2
        col1_items = lang_items[:mid_point]
        col2_items = lang_items[mid_point:]

        # Первая колонка
        for i, (code, name) in enumerate(col1_items[:max_items_per_col]):
            y_pos = lang_window.y + 60 + i * 25
            x_pos = lang_window.x + 20

            item_rect = pygame.Rect(x_pos, y_pos - 2, col_width - 20, 24)
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = item_rect.collidepoint(mouse_pos)

            # Отображение элемента
            item_color = BLUE if is_hovered else BLACK
            lang_str = f"{name.capitalize()} ({code})"
            lang_surf = small_font.render(lang_str, True, item_color)
            screen.blit(lang_surf, (x_pos, y_pos))

            # Обработка клика
            if is_hovered and pygame.mouse.get_pressed()[0] and current_time - last_click_time > 300:
                lang_code = code
                show_lang_list = False
                last_click_time = current_time

        # Вторая колонка
        for i, (code, name) in enumerate(col2_items[:max_items_per_col]):
            y_pos = lang_window.y + 60 + i * 25
            x_pos = lang_window.x + 20 + col_width

            item_rect = pygame.Rect(x_pos, y_pos - 2, col_width - 20, 24)
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = item_rect.collidepoint(mouse_pos)

            # Отображение элемента
            item_color = BLUE if is_hovered else BLACK
            lang_str = f"{name.capitalize()} ({code})"
            lang_surf = small_font.render(lang_str, True, item_color)
            screen.blit(lang_surf, (x_pos, y_pos))

            # Обработка клика
            if is_hovered and pygame.mouse.get_pressed()[0] and current_time - last_click_time > 300:
                lang_code = code
                show_lang_list = False
                last_click_time = current_time

        # Подсказка о количестве языков
        total_langs = len(lang_items)
        hint = small_font.render(f"Всего языков: {total_langs}. Нажмите на язык для выбора.", True, GRAY)
        screen.blit(hint, (lang_window.x + 10, lang_window.bottom - 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()