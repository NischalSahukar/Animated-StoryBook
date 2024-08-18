import pygame
import sys
import os
import cv2
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animated Storybook")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CREAM = (255, 253, 208)

# Fonts
try:
    title_font = pygame.font.SysFont("Algerian", 64)
    heading_font = pygame.font.SysFont("Algerian", 48)
    text_font = pygame.font.SysFont("Times New Roman", 28)
except pygame.error:
    print("Custom fonts not found. Using default fonts.")
    title_font = pygame.font.Font(None, 64)
    heading_font = pygame.font.Font(None, 48)
    text_font = pygame.font.Font(None, 28)

# Set the directory where your images are located
image_dir = os.path.dirname(__file__)  # This will use the same directory as the script

# Try to load images, use solid color if images are not found
backgrounds = []
for i in range(1, 23):  # Load 23 images (1 for menu/end, 22 for story)
    try:
        img_path = os.path.join(image_dir, f"background{i}.png")
        backgrounds.append(pygame.image.load(img_path))
    except pygame.error:
        # If image is not found, use a solid color background
        bg = pygame.Surface((WIDTH, HEIGHT))
        bg.fill((200, 220, 255))  # Light blue color
        backgrounds.append(bg)

# Load sounds
try:
    pygame.mixer.music.load("background_music.mp3")
    page_turn_sound = pygame.mixer.Sound("page_turn.wav")
except pygame.error:
    print("Warning: Sound files not found. Continuing without sound.")

# Story heading
story_heading = "The Lion King"

# Story pages
pages = [
    "The story opens with the birth of Simba, son of King Mufasa and Queen Sarabi.",
    "All the animals of the Pride Lands gather to witness the presentation of the future king.",
    "Rafiki, a wise mandrill shaman, presents the newborn cub to the assembled animals.",
    "As Simba grows, Mufasa teaches him about the responsibilities of being a king and the delicate balance of nature, which he calls the 'Circle of Life'.",
    "Meanwhile, Mufasa's younger brother, Scar, grows increasingly jealous and resentful of Simba, as the cub's birth has displaced him as heir to the throne.",
    "One day, Scar tricks Simba and his best friend Nala into visiting a forbidden elephant graveyard.",
    "There, they're attacked by three hyenas - Shenzi, Banzai, and Ed - who are in league with Scar.",
    "Mufasa rescues the cubs, disappointing Scar's attempt to have Simba killed.",
    "Undeterred, Scar devises a new plan. He lures Simba into a gorge and signals the hyenas to start a wildebeest stampede.",
    "Mufasa arrives to save Simba but is betrayed by Scar, who throws him off a cliff into the stampede. Simba witnesses his father's death but doesn't see Scar's role in it.",
    "Scar convinces the traumatized Simba that the king's death was Simba's fault and tells him to run away and never return.",
    "As Simba flees, Scar orders the hyenas to kill him, but Simba escapes. Scar then returns to Pride Rock and claims the throne, allowing the hyenas to enter the Pride Lands.",
    "Simba collapses in the desert but is rescued by Timon (a meerkat) and Pumbaa (a warthog).",
    "They take him in, teaching him their carefree philosophy of 'Hakuna Matata' (No Worries). Simba grows into adulthood living a carefree life with his new friends.",
    "Years later, Simba encounters Nala, who has left the Pride Lands searching for help. She informs Simba of Scar's tyrannical rule and the suffering of their pride. Simba, still guilty about his father's death, refuses to return.",
    "Rafiki discovers that Simba is alive and finds him, showing him that Mufasa's spirit lives on.",
    "Mufasa's ghost appears to Simba, urging him to take his rightful place as king. Inspired, Simba decides to return to the Pride Lands.",
    "Simba, with help from Nala, Timon, and Pumbaa, returns home and confronts Scar. Scar tries to blame the hyenas for Mufasa's death, but Simba forces him to admit the truth to the pride.",
    "A battle ensues, ending with Simba defeating Scar, who is then killed by the hyenas he betrayed.",
    "With Scar's defeat, Simba takes his place as the rightful king.",
    "The story ends as it began, with Rafiki presenting Simba and Nala's newborn cub to the assembled animals of the Pride Lands, continuing the Circle of Life.",
]

# Game states
MENU = 0
STORY = 1
END = 2
game_state = MENU

# Story variables
current_page = 0
text_position = HEIGHT
fade_alpha = 0
page_turn_progress = 0
turning_page = False
VIDEO = 3

# Text wrapping function
def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    return lines

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = text_font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Create buttons
start_button = Button(300, 350, 200, 50, "Start Story", (0, 255, 0), BLACK)
quit_button = Button(300, 450, 200, 50, "Quit", (255, 0, 0), BLACK)

# Page turning effect
def draw_page_turn(surface, progress):
    curve = lambda x: 1 - (1 - x) ** 3  # Smoother curve
    shadow_color = (100, 100, 100)
    for x in range(WIDTH):
        h = int(HEIGHT * curve(x / WIDTH))
        progress_height = int(h * progress)
        pygame.draw.line(surface, (200, 200, 200), (x, HEIGHT), (x, HEIGHT - progress_height))
        pygame.draw.line(surface, shadow_color, (x, HEIGHT - progress_height), (x, HEIGHT - progress_height - 5))
# Main game loop
clock = pygame.time.Clock()
running = True

def fade_transition(surface, next_state):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(BLACK)
    for alpha in range(0, 300, 5):
        fade.set_alpha(alpha)
        surface.blit(fade, (0, 0))
        pygame.display.flip()
    return next_state

def play_image_sequence(image_folder, duration_per_image=2):
    images = []
    for filename in sorted(os.listdir(image_folder)):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, filename)
            try:
                image = pygame.image.load(image_path)
                images.append(image)
            except pygame.error:
                print(f"Couldn't load image: {image_path}")

    if not images:
        print("No images found in the specified folder.")
        return

    clock = pygame.time.Clock()
    current_image = 0
    start_time = pygame.time.get_ticks()

    running = True
    while running and current_image < len(images):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        current_time = pygame.time.get_ticks()
        if current_time - start_time > duration_per_image * 1000:
            current_image += 1
            start_time = current_time
            if current_image >= len(images):
                break

        if current_image < len(images):
            # Scale image to fit screen
            scaled_image = pygame.transform.scale(images[current_image], (WIDTH, HEIGHT))
            screen.blit(scaled_image, (0, 0))
            pygame.display.flip()

        clock.tick(30)

    # pygame.mixer.music.stop()
    pygame.time.wait(1000)  # Wait for 1 second after the last image
       
# Start background music
try:
    pygame.mixer.music.play(-1)
except pygame.error:
    pass

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == MENU:
                if start_button.is_clicked(event.pos):
                    game_state = STORY
                elif quit_button.is_clicked(event.pos):
                    running = False
            elif game_state == STORY:
                if not turning_page and current_page < len(pages) - 1:
                    turning_page = True
                    page_turn_progress = 0
                    try:
                        page_turn_sound.play()
                    except NameError:
                        pass
                else:
                    game_state = END
            elif game_state == END:
                running = False

    screen.fill(WHITE)

    if game_state == MENU:
        # Draw menu background
        screen.blit(backgrounds[0], (0, 0))
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 128))  # White with 50% opacity
        screen.blit(overlay, (0, 0))
        
        # Draw title
        title_text = title_font.render("Animated Storybook", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Draw story heading
        heading_text = heading_font.render(story_heading, True, BLACK)
        screen.blit(heading_text, (WIDTH // 2 - heading_text.get_width() // 2, 200))
        
        start_button.draw(screen)
        quit_button.draw(screen)
        
    elif game_state == STORY:
        bg_index = min(current_page + 1, len(backgrounds) - 1)
        screen.blit(backgrounds[bg_index], (0, 0))

        if turning_page:
            page_turn_progress += 0.04
            if page_turn_progress >= 1:
                turning_page = False
                current_page += 1
                text_position = HEIGHT
                fade_alpha = 0
                page_turn_progress = 0
            draw_page_turn(screen, page_turn_progress)
        else:
            if text_position > HEIGHT // 4:
                text_position -= 5
            if fade_alpha < 255:
                fade_alpha += 5

            wrapped_text = wrap_text(pages[current_page], text_font, WIDTH - 100)
            text_surface = pygame.Surface((WIDTH - 80, len(wrapped_text) * 35 + 20), pygame.SRCALPHA)
            text_surface.fill((CREAM[0], CREAM[1], CREAM[2], 200))
            for i, line in enumerate(wrapped_text):
                line_surface = text_font.render(line, True, BLACK)
                text_surface.blit(line_surface, (10, i * 35 + 10))
            
            text_surface.set_alpha(fade_alpha)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, text_position))
            screen.blit(text_surface, text_rect)

        if current_page == len(pages) - 1 and not turning_page:
            end_button = Button(WIDTH - 150, HEIGHT - 70, 100, 50, "The End", (0, 0, 255), WHITE)
            end_button.draw(screen)
            if end_button.is_clicked(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                game_state = END

    # In your main game loop, add this condition:
    elif game_state == VIDEO:
        play_image_sequence("C:/Users/nisch/Documents/cg/slideshow", 2)
        game_state = END  # Or wherever you want to go after the video
 
    elif game_state == END:
        # Draw end background
        screen.blit(backgrounds[0], (0, 0))
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 128))  # White with 50% opacity
        screen.blit(overlay, (0, 0))
        
        end_text = title_font.render("The End", True, BLACK)
        screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - end_text.get_height() // 2))

        # Add a button to play the video
        video_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, "Play Video", (0, 255, 0), BLACK)
        video_button.draw(screen)
    
        if video_button.is_clicked(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            game_state = VIDEO
    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(120)

# Quit the game
pygame.quit()
sys.exit()