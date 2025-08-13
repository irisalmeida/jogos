import sys
import os
import asyncio
from pathlib import Path
from typing import List, Tuple
import pygame

os.environ.setdefault("SDL_VIDEO_CENTERED", "1")

WIDTH, HEIGHT = 960, 540
FPS = 60
IS_WEB = sys.platform == "emscripten"

BG_COLOR = (18, 24, 26)
CARD_COLOR = (30, 30, 38)
LINE_COLOR = (70, 70, 90)
PRIMARY = (3, 218, 197)
TEXT = (220, 220, 230)
TEXT_MUTED = (180, 184, 190)
ACCENT = (90, 100, 120)

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"


questions = [
    "1. Achei difícil me acalmar",
    "2. Senti minha boca seca",
    "3. Não consegui vivenciar nenhum sentimento positivo",
    "4. Tive dificuldade em respirar (ex: respiração ofegante)",
    "5. Achei difícil ter iniciativa para fazer as coisas",
    "6. Reagi de forma exagerada às situações",
    "7. Senti tremores (ex: nas mãos)",
    "8. Senti que estava sempre nervoso",
    "9. Tive medo de parecer ridículo(a) em público",
    "10. Senti que não tinha nada a desejar",
    "11. Senti-me agitado",
    "12. Achei difícil relaxar",
    "13. Senti-me sem ânimo",
    "14. Fui intolerante com dificuldades",
    "15. Tive sensação de pânico",
    "16. Não consegui me entusiasmar com nada",
    "17. Senti que não tinha valor",
    "18. Estava emotivo(a) demais",
    "19. Coração acelerado mesmo em repouso",
    "20. Senti medo sem motivo",
    "21. A vida parecia sem sentido",
]

options = [
    "Aplicou-se em algum grau, ou por pouco de tempo",
    "Aplicou-se em um grau considerável, ou por boa parte do tempo",
    "Aplicou-se muito, ou na maioria do tempo",
    "Não se aplicou de maneira alguma",
]


STONE_MAP = [
    ("pedra_amarela.png", options[0]),
    ("pedra_vermelha.png", options[1]),
    ("pedra_azul.png", options[2]),
    ("pedra_verde.png", options[3]),
]


def _placeholder(size=(96, 96), label="IMG"):
    pygame.font.init()
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((40, 40, 40, 255))
    pygame.draw.rect(surf, (120, 120, 120, 255), surf.get_rect(), width=2)
    font = pygame.font.Font(None, 20)
    txt = font.render(label, True, TEXT)
    surf.blit(txt, txt.get_rect(center=(size[0] // 2, size[1] // 2)))
    return surf


def load_png(name: str, *, size=None, label=None) -> pygame.Surface:
    path = ASSETS_DIR / name
    if path.exists():
        img = pygame.image.load(str(path)).convert_alpha()
    else:
        img = _placeholder(size=size or (96, 96), label=label or name)
    if size:
        img = pygame.transform.smoothscale(img, size)
    return img


def draw_wrapped_text(surface, text, x, y, font, color=TEXT, max_width=680, line_height=None):
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = f"{current} {w}".strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)

    h = font.get_height() if line_height is None else line_height
    for i, line in enumerate(lines):
        surf = font.render(line, True, color)
        surface.blit(surf, (x, y + i * h))


def draw_button(surface, rect, label, font, *, bg=PRIMARY, fg=(10, 20, 20), hover_bg=None):
    mouse = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mouse)
    color = hover_bg if (is_hover and hover_bg) else (bg if not is_hover else (0, 200, 185))
    pygame.draw.rect(surface, color, rect, border_radius=12)
    txt = font.render(label, True, fg)
    surface.blit(txt, txt.get_rect(center=rect.center))
    return is_hover


def draw_legend(surface, font_small, start_x, start_y, stone_imgs_texts):
    legend_w = 360
    legend_h = 310
    pygame.draw.rect(surface, CARD_COLOR, (start_x, start_y, legend_w, legend_h), border_radius=14)
    pygame.draw.rect(surface, LINE_COLOR, (start_x, start_y, legend_w, legend_h), width=2, border_radius=14)

    title = pygame.font.Font(None, 28).render("Legenda", True, TEXT)
    surface.blit(title, (start_x + 16, start_y + 14))

    y = start_y + 54
    gap = 16
    for img, text in stone_imgs_texts:
        surface.blit(img, (start_x + 18, y))
        draw_wrapped_text(surface, text, start_x + 18 + 48 + 12, y + 6, font_small, color=TEXT, max_width=legend_w - 48 - 36)
        y += max(img.get_height(), 48) + gap


async def game_loop():
    pygame.init()
    pygame.display.set_caption("Teste das Pedras Mágicas")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    title_font = pygame.font.Font(None, 52)
    subtitle_font = pygame.font.Font(None, 28)
    body_font = pygame.font.Font(None, 24)

    bruxo_img = load_png("bruxo.png", size=(140, 140), label="bruxo")

    stone_click_imgs = [load_png(name, size=(86, 86), label=name) for name, _ in STONE_MAP]
    stone_legend_imgs = [load_png(name, size=(42, 42), label=name) for name, _ in STONE_MAP]

    stone_click_rects: List[pygame.Rect] = [img.get_rect() for img in stone_click_imgs]

    state = "intro"
    q_index = 0
    answers: List[int] = [-1] * len(questions)
    legend_pairs = list(zip(stone_legend_imgs, [text for _, text in STONE_MAP]))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == "intro":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    start_btn = pygame.Rect((screen.get_width() - 220) // 2, 500, 220, 45)
                    if start_btn.collidepoint(event.pos):
                        state = "quiz"

            elif state == "quiz":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, rect in enumerate(stone_click_rects):
                        if rect.collidepoint(event.pos):
                            answers[q_index] = i
                            if q_index < len(questions) - 1:
                                q_index += 1
                            else:
                                state = "end"

                    back_btn = pygame.Rect(24, HEIGHT - 60, 120, 36)
                    if back_btn.collidepoint(event.pos) and q_index > 0:
                        q_index -= 1

            elif state == "end":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    restart_btn = pygame.Rect((WIDTH - 220) // 2, HEIGHT - 70, 220, 45)
                    if restart_btn.collidepoint(event.pos):
                        answers = [-1] * len(questions)
                        q_index = 0
                        state = "intro"

        screen.fill(BG_COLOR)

        if state == "intro":
            screen.blit(bruxo_img, ((screen.get_width() - bruxo_img.get_width()) // 2, 40))
            draw_wrapped_text(screen, "Bem-vindo ao Teste das Pedras Mágicas", 80, 200, title_font, max_width=800)

            intro = (
                "Você está prestes a iniciar uma jornada mágica de autoconhecimento. "
                "Cada pergunta revelará uma pedra mágica representando uma parte de você. "
                "Clique na pedra que melhor representa como você se sentiu."
            )
            draw_wrapped_text(screen, intro, 80, 268, subtitle_font, color=TEXT_MUTED, max_width=800)

            start_btn = pygame.Rect((screen.get_width() - 220) // 2, 500, 220, 45)
            draw_button(screen, start_btn, "Iniciar Jornada", subtitle_font)

        elif state == "quiz":
            progress = f"Pergunta {q_index + 1} de {len(questions)}"
            prog_txt = subtitle_font.render(progress, True, TEXT_MUTED)
            screen.blit(prog_txt, (24, 18))

            draw_wrapped_text(screen, questions[q_index], 24, 50, title_font, max_width=560)

            area_w = 560
            area_h = 260
            area_x = 24
            area_y = 130
            pygame.draw.rect(screen, CARD_COLOR, (area_x, area_y, area_w, area_h), border_radius=14)
            pygame.draw.rect(screen, LINE_COLOR, (area_x, area_y, area_w, area_h), width=2, border_radius=14)

            gap = area_w // 5
            base_x = area_x + gap // 2
            y_center = area_y + area_h // 2

            selected = answers[q_index]
            for i, img in enumerate(stone_click_imgs):
                cx = base_x + i * gap + img.get_width() // 2 + 8
                rect = img.get_rect(center=(cx, y_center))
                stone_click_rects[i] = rect
                screen.blit(img, rect)

                if selected == i:
                    pygame.draw.circle(screen, PRIMARY, rect.center, max(rect.width, rect.height) // 2 + 8, width=3)

            instr = "Clique em uma pedra para responder"
            instr_txt = body_font.render(instr, True, TEXT_MUTED)
            screen.blit(instr_txt, (area_x + 16, area_y + area_h - 36))

            back_btn = pygame.Rect(24, HEIGHT - 60, 120, 36)
            draw_button(screen, back_btn, "Voltar", body_font, bg=ACCENT, fg=(235, 235, 240))

            # Legenda à direita
            draw_legend(screen, body_font, start_x=WIDTH - 380, start_y=110, stone_imgs_texts=legend_pairs)

        elif state == "end":
            draw_wrapped_text(screen, "Concluído!", 80, 80, title_font, max_width=800)

            counts = [0, 0, 0, 0]
            for a in answers:
                if 0 <= a < 4:
                    counts[a] += 1

            box = pygame.Rect(80, 140, WIDTH - 160, 280)
            pygame.draw.rect(screen, CARD_COLOR, box, border_radius=14)
            pygame.draw.rect(screen, LINE_COLOR, box, width=2, border_radius=14)

            y = 160
            for i, (name, text_opt) in enumerate(STONE_MAP):
                img = load_png(name, size=(36, 36), label=name)
                screen.blit(img, (100, y))
                left = 100 + 36 + 12
                draw_wrapped_text(screen, f"{text_opt}", left, y + 2, body_font, max_width=box.width - 220)
                qty = subtitle_font.render(f"{counts[i]} resposta(s)", True, TEXT)
                screen.blit(qty, (box.right - qty.get_width() - 24, y + 4))
                y += 56

            restart_btn = pygame.Rect((WIDTH - 220) // 2, HEIGHT - 70, 220, 45)
            draw_button(screen, restart_btn, "Reiniciar", subtitle_font)

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()


def main():
    asyncio.run(game_loop())


if __name__ == "__main__":
    main()
