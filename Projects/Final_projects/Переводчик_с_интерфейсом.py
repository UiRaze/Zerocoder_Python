import pygame
import sys
from deep_translator import GoogleTranslator
from googletrans import LANGUAGES
def translate1(text5, dest_language):
    print("Выполняется перевод...")
    try:
        result = GoogleTranslator(source='auto', target=dest_language).translate(text5)
        print("Результат:", result)
        return result
    except Exception as e:
        print("Ошибка перевода:", e)
        return "Ошибка перевода"

def main():
    pygame.init()

    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Текстовое поле ввода")

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    BLUE = (0, 120, 215)

    font = pygame.font.Font(None, 36)

    input_box = pygame.Rect(200, 250, 400, 50)
    input_box2 = pygame.Rect(200, 375, 400, 50)
    input_box3 = pygame.Rect(200, 500, 400, 50)
    color_inactive = GRAY
    color_active = BLUE
    color = color_inactive
    color2 = color_inactive

    active = False
    active2 = False
    text = ''
    text2 = ''
    translated_text = ''
    current_lang = ''

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                    active2 = False
                elif input_box2.collidepoint(event.pos):
                    active2 = not active2
                    active = False
                else:
                    active = False
                    active2 = False
                color = color_active if active else color_inactive
                color2 = color_active if active2 else color_inactive

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        lang_code = None
                        for code, name in LANGUAGES.items():
                            if name.lower() == text.lower():
                                lang_code = code
                                break
                        current_lang = lang_code
                        print(f"Язык установлен: {text} → {current_lang}")
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif len(text) < 20:
                        text += event.unicode

                elif active2:
                    if event.key == pygame.K_RETURN:
                        if text2.strip() and current_lang:
                            translated_text = translate1(text2, current_lang)
                        else:
                            translated_text = "Введите текст и язык"
                        text2 = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text2 = text2[:-1]
                    elif len(text2) < 20:
                        text2 += event.unicode

        screen.fill(WHITE)
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.draw.rect(screen, color2, input_box2, 2)
        pygame.draw.rect(screen, GRAY, input_box3, 2)

        txt_surface = font.render(text, True, BLACK)
        txt_surface2 = font.render(text2, True, BLACK)
        translated_surface = font.render(str(translated_text), True, BLACK)

        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 10))
        screen.blit(txt_surface2, (input_box2.x + 5, input_box2.y + 10))
        screen.blit(translated_surface, (input_box3.x + 5, input_box3.y + 10))

        screen.blit(font.render('Введите язык для перевода:', True, BLACK), (200, 200))
        screen.blit(font.render('Введите текст для перевода:', True, BLACK), (200, 325))
        screen.blit(font.render('Добро пожаловать в переводчик!!!', True, BLACK), (195, 15))
        screen.blit(font.render('Перевод:', True, BLACK), (200, 450))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()