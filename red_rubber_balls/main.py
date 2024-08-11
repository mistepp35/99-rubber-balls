import pygame
import sys
import time
import math
import random
import os

# Change working directory
os.chdir(os.path.dirname(__file__))

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 150  # Increased the ground height to raise the grass level
BALL_RADIUS_MIN = 10
BALL_RADIUS_MAX = 50

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
DARK_BLUE = (0, 0, 139)
FOREST_GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (50, 205, 50)
NIGHT_SKY = (0, 0, 51)
GRASS_BLUE = (0, 100, 200)
GRASS_LIGHT_BLUE = (0, 155, 255)

# Physics constants
GRAVITY = 0.7
FRICTION = 0.99
ELASTICITY = 0.9
COLLISION_TOLERANCE = 0.1
VELOCITY_THRESHOLD = 1  # Velocity threshold for sound playback

# Ball lifetime
BALL_LIFETIME = 10  # seconds

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('99 Rubber Balls')

# Initialize mixer and load background music
pygame.mixer.init()
pygame.mixer.music.load(os.path.join(os.getcwd(), 'music', '8-Bit Misfits - 99 Luftballoons.mp3'))
pygame.mixer.music.play(-1)  # -1 means the music will loop indefinitely

# Load sound effects
bounce_sounds = [
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'bounce1.wav')),
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'bounce2.wav')),
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'bounce3.wav')),
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'bounce4.wav')),
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'bounce5.wav')),
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'bounce6.wav')),
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'bounce7.wav')),
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'bounce8.wav')),
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'bounce9.wav'))
]
pop_sounds = [
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'pop1.wav')),
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'pop2.wav')),
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'pop3.wav')),
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'pop4.wav')),
    pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'pop5.wav')) 
]
sun_pop_sound = pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'pop.wav'))
applause_sound = pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'applause.wav'))
wow_sound = pygame.mixer.Sound(os.path.join(os.getcwd(), 'sounds', 'wow.wav'))

# Load the sun image
sun_image = pygame.image.load('images/sun.png')
sun_image = pygame.transform.scale(sun_image, (150, 150))  # Adjust the size as needed

# Load the face images
sun_faces = [
    pygame.image.load(f'images/face_{i:02}.png') for i in range(1, 11)
]
# Scale the face images
sun_faces = [pygame.transform.scale(face, (100, 60)) for face in sun_faces]
current_face_index = 0

# Load cloud images
cloud_images = [
    pygame.image.load(f'images/cloud_{i}.png') for i in range(1, 6)
]

# Particle class
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-2, 2)
        self.vel_y = random.uniform(-2, 2)
        self.lifetime = random.randint(20, 40)
        self.size = random.randint(2, 5)
        self.color = color

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# Cloud class
class Cloud:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.image = random.choice(cloud_images)  # Randomly select a cloud image

    def update(self):
        self.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, (int(self.x), int(self.y)))

# Star class
class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT // 2)
        self.color = random.choice([RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE])
        self.size = random.randint(2, 5)
        self.vel_y = random.uniform(0.5, 2)

    def update(self):
        self.y += self.vel_y
        if self.y > SCREEN_HEIGHT:
            self.y = random.randint(-50, -10)
            self.x = random.randint(0, SCREEN_WIDTH)
            self.vel_y = random.uniform(0.5, 2)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# Ball class
class Ball:
    def __init__(self, x, y, vel_x, vel_y, radius):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.radius = radius
        self.mass = radius ** 2  # Mass is proportional to the square of the radius
        self.is_falling = True
        self.creation_time = time.time()  # Record the creation time
        self.color = self.color_by_radius()  # Assign a color based on radius

    def color_by_radius(self):
        red_value = int(255 - 127.5 * (self.radius - BALL_RADIUS_MIN) / (BALL_RADIUS_MAX - BALL_RADIUS_MIN))
        return (red_value, 0, 0)

    def update(self):
        if self.is_falling:
            self.vel_y += GRAVITY
            self.x += self.vel_x
            self.y += self.vel_y
            self.vel_x *= FRICTION
            self.vel_y *= FRICTION

            # Collision with the ground
            if self.y + self.radius > SCREEN_HEIGHT - GROUND_HEIGHT + 10:  # Adjusted for new ground height
                self.y = SCREEN_HEIGHT - GROUND_HEIGHT + 10 - self.radius  # Adjusted for new ground height
                self.vel_y *= -ELASTICITY
                if abs(self.vel_y) > VELOCITY_THRESHOLD:
                    self.play_bounce_sound()
                    return True

            # Collision with the sides of the screen
            if self.x - self.radius < 0 or self.x + self.radius > SCREEN_WIDTH:
                self.vel_x *= -ELASTICITY
                if self.x - self.radius < 0:
                    self.x = self.radius
                if self.x + self.radius > SCREEN_WIDTH:
                    self.x = SCREEN_WIDTH - self.radius
                if abs(self.vel_x) > VELOCITY_THRESHOLD:
                    self.play_bounce_sound()
                    return True
        return False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 1)

    def draw_shadow(self, screen):
        shadow_width = self.radius * 1.5
        shadow_height = self.radius / 2
        shadow_rect = pygame.Rect(
            int(self.x - shadow_width / 2), 
            SCREEN_HEIGHT - GROUND_HEIGHT + 10 - int(shadow_height / 2),  # Adjusted for new ground height
            int(shadow_width), 
            int(shadow_height)
        )
        pygame.draw.ellipse(screen, DARK_GREEN, shadow_rect)

    def collide_with(self, other):
        # Distance between the two balls
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.hypot(dx, dy)

        # Check for collision
        if distance < self.radius + other.radius - COLLISION_TOLERANCE:
            angle = math.atan2(dy, dx)
            total_mass = self.mass + other.mass

            # Calculate new velocities
            self_vel_x = self.vel_x * (self.mass - other.mass) / total_mass + (2 * other.mass * other.vel_x) / total_mass
            self_vel_y = self.vel_y * (self.mass - other.mass) / total_mass + (2 * other.mass * self.vel_y) / total_mass
            other_vel_x = other.vel_x * (other.mass - self.mass) / total_mass + (2 * self.mass * self.vel_x) / total_mass
            other_vel_y = other.vel_y * (other.mass - self.mass) / total_mass + (2 * self.mass * self.vel_y) / total_mass

            self.vel_x, self.vel_y = self_vel_x, self_vel_y
            other.vel_x, other.vel_y = other_vel_x, other_vel_y

            # Adjust positions to prevent sticking
            overlap = 0.5 * (self.radius + other.radius - distance + 1)
            self.x += math.cos(angle) * overlap
            self.y += math.sin(angle) * overlap
            other.x -= math.cos(angle) * overlap
            other.y -= math.sin(angle) * overlap

            if abs(self.vel_x) > VELOCITY_THRESHOLD or abs(self.vel_y) > VELOCITY_THRESHOLD:
                self.play_bounce_sound()
                return True
        return False

    def play_bounce_sound(self):
        random.choice(bounce_sounds).play()

    def pop(self):
        random.choice(pop_sounds).play()
        for _ in range(30):
            particles.append(Particle(self.x, self.y, RED))  # Create red particles

# Function to draw the sun with the face and animation
def draw_sun(screen, time_elapsed, pop_effect=False):
    sun_center = (SCREEN_WIDTH - 70, 70)

    if pop_effect:
        for _ in range(30):
            particles.append(Particle(sun_center[0], sun_center[1], YELLOW))
        return

    # Calculate oscillation parameters
    scale_factor = 1 + 0.05 * math.sin(time_elapsed)
    rotation_angle = 5 * math.sin(time_elapsed)

    # Scale and rotate the sun image
    sun_image_scaled = pygame.transform.rotozoom(sun_image, rotation_angle, scale_factor)

    # Blit the animated sun image
    sun_rect = sun_image_scaled.get_rect(center=sun_center)
    screen.blit(sun_image_scaled, sun_rect.topleft)

    # Blit the current sun face image
    face_rect = sun_faces[current_face_index].get_rect(center=sun_center)
    screen.blit(sun_faces[current_face_index], face_rect)

# Function to draw textured grass
def draw_grass(screen, night=False):
    for i in range(SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_HEIGHT):
        if night:
            color = (
                GRASS_BLUE[0] + int((GRASS_LIGHT_BLUE[0] - GRASS_BLUE[0]) * (i - (SCREEN_HEIGHT - GROUND_HEIGHT)) / GROUND_HEIGHT),
                GRASS_BLUE[1] + int((GRASS_LIGHT_BLUE[1] - GRASS_BLUE[1]) * (i - (SCREEN_HEIGHT - GROUND_HEIGHT)) / GROUND_HEIGHT),
                GRASS_BLUE[2] + int((GRASS_LIGHT_BLUE[2] - GRASS_BLUE[2]) * (i - (SCREEN_HEIGHT - GROUND_HEIGHT)) / GROUND_HEIGHT)
            )
        else:
            color = (0, 155 + int(100 * (i - (SCREEN_HEIGHT - GROUND_HEIGHT)) / GROUND_HEIGHT), 0)
        pygame.draw.line(screen, color, (0, i), (SCREEN_WIDTH, i))

# Function to draw textured sky
def draw_sky(screen, night=False):
    if night:
        screen.fill(NIGHT_SKY)
    else:
        for i in range(SCREEN_HEIGHT - GROUND_HEIGHT):
            color = (
                DARK_BLUE[0] + int((SKY_BLUE[0] - DARK_BLUE[0]) * i / (SCREEN_HEIGHT - GROUND_HEIGHT)),
                DARK_BLUE[1] + int((SKY_BLUE[1] - DARK_BLUE[1]) * i / (SCREEN_HEIGHT - GROUND_HEIGHT)),
                DARK_BLUE[2] + int((SKY_BLUE[2] - DARK_BLUE[2]) * i / (SCREEN_HEIGHT - GROUND_HEIGHT))
            )
            pygame.draw.line(screen, color, (0, i), (SCREEN_WIDTH, i))

# Function to update the face index
def update_face_index():
    global current_face_index
    current_face_index = (current_face_index + 1) % len(sun_faces)

def display_text(screen, text, font, color, center):
    rendered_text = font.render(text, True, color)
    rect = rendered_text.get_rect(center=center)
    screen.blit(rendered_text, rect)

def draw_button(screen, text, font, color, center, padding=10):
    rendered_text = font.render(text, True, color)
    rect = rendered_text.get_rect(center=center)
    button_rect = pygame.Rect(rect.left - padding, rect.top - padding, rect.width + 2 * padding, rect.height + 2 * padding)
    pygame.draw.rect(screen, WHITE, button_rect)
    pygame.draw.rect(screen, BLACK, button_rect, 2)
    screen.blit(rendered_text, rect)
    return button_rect

def game_over_screen(screen, score):
    game_over_font = pygame.font.Font(None, 74)
    score_font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    while True:
        draw_sky(screen, night=True)  # Draw the night sky

        # Update and draw stars
        for star in stars:
            star.update()
            star.draw(screen)

        draw_grass(screen, night=True)  # Draw the blue gradient grass

        display_text(screen, "Game Over", game_over_font, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        display_text(screen, f"Final Score: {score}", score_font, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        play_again_button = draw_button(screen, "Play Again", score_font, BLACK, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        quit_button = draw_button(screen, "Quit", score_font, BLACK, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.collidepoint(event.pos):
                    return "play_again"
                elif quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        clock.tick(30)

# Main loop
balls = []
particles = []
clouds = [Cloud(random.randint(0, SCREEN_WIDTH), random.randint(0, 200), random.uniform(0.5, 2)) for _ in range(5)]
stars = [Star() for _ in range(100)]
running = True
mouse_held = False
mouse_positions = []
mouse_down_time = None
start_screen = True
score = 0
ball_count = 0
max_balls = 99
font = pygame.font.Font(None, 36)
game_over_triggered = False
game_over_start_time = None
sun_popped = False
start_time = time.time()
last_ball_creation_time = None
last_click_time = time.time()
keep_going_message = False
wow_message_start_time = None

while running:
    current_time = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                last_click_time = time.time()
                keep_going_message = False
                if start_screen:
                    start_screen = False
                elif ball_count < max_balls:  # Only allow creating balls if under the limit
                    x, y = event.pos
                    mouse_positions = [(x, y)]
                    mouse_held = True
                    mouse_down_time = time.time()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and mouse_held:  # Left mouse button
                mouse_held = False
                mouse_up_time = time.time()
                hold_duration = mouse_up_time - mouse_down_time
                radius = BALL_RADIUS_MIN + int(hold_duration * 100)
                radius = min(radius, BALL_RADIUS_MAX)
                if len(mouse_positions) > 1:
                    # Calculate velocity based on mouse movement
                    dx = mouse_positions[-1][0] - mouse_positions[-2][0]
                    dy = mouse_positions[-1][1] - mouse_positions[-2][1]
                    new_ball = Ball(mouse_positions[-1][0], mouse_positions[-1][1], dx, dy, radius)
                    balls.append(new_ball)
                else:
                    # If there was no significant movement, just drop the ball
                    new_ball = Ball(mouse_positions[-1][0], mouse_positions[-1][1], 0, 0, radius)
                    balls.append(new_ball)

                # Create particles at the position of the new ball
                for _ in range(30):
                    particles.append(Particle(new_ball.x, new_ball.y, YELLOW))  # Yellow particles for creation

                ball_count += 1  # Increment the ball count
                last_ball_creation_time = time.time()  # Record the time of the last ball creation

                # Update face index every 10 balls
                if ball_count % 10 == 0:
                    update_face_index()

                # Check if 99th ball is created
                if ball_count == 99:
                    wow_sound.play()


                    wow_message_start_time = time.time()

    if mouse_held:
        x, y = pygame.mouse.get_pos()
        mouse_positions.append((x, y))
        if len(mouse_positions) > 2:
            mouse_positions.pop(0)  # Keep only the last two positions

    # Display "Keep going!" message if no click for 5 seconds and before 99th ball
    if current_time - last_click_time > 5 and ball_count < max_balls:
        keep_going_message = True

    # Update
    if not start_screen:
        any_collisions = False
        new_balls = []
        for ball in balls:
            if current_time - ball.creation_time < BALL_LIFETIME:
                new_balls.append(ball)
            else:
                ball.pop()  # Pop the ball when its lifetime is over
                if ball_count >= max_balls:
                    game_over_triggered = True
                    game_over_start_time = current_time
        balls = new_balls
        
        for ball in balls:
            if ball.update():
                score += 1
                any_collisions = True

        # Update particles
        particles = [p for p in particles if p.lifetime > 0]
        for particle in particles:
            particle.update()

        # Update clouds
        clouds = [cloud for cloud in clouds if cloud.x < SCREEN_WIDTH + 50]
        for cloud in clouds:
            cloud.update()

        # Add new clouds if there are fewer than 5
        if len(clouds) < 5:
            clouds.append(Cloud(-50, random.randint(0, 200), random.uniform(0.5, 2)))

        # Update stars
        if sun_popped:
            for star in stars:
                star.update()

        # Check for collisions between balls
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                if balls[i].collide_with(balls[j]):
                    score += 1
                    any_collisions = True

        # Check if game over condition is met
        if game_over_triggered:
            if not sun_popped and current_time - last_ball_creation_time > 11:
                sun_pop_sound.play()
                draw_sun(screen, time.time() - start_time, pop_effect=True)
                sun_popped = True
            if current_time - last_ball_creation_time > 15:
                running = False

    # Draw
    draw_sky(screen, night=sun_popped)  # Draw textured sky, night sky if sun popped

    if sun_popped:
        for star in stars:
            star.draw(screen)

    draw_grass(screen, night=sun_popped)  # Draw textured grass, blue gradient if sun popped
    pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT), 1)  # Outline for grass
    if not sun_popped:
        draw_sun(screen, time.time() - start_time, pop_effect=sun_popped)  # Draw the sun with animation and pop effect

    for cloud in clouds:
        cloud.draw(screen)
    for ball in balls:
        ball.draw_shadow(screen)  # Draw ball shadow first
    for ball in balls:
        ball.draw(screen)

    for particle in particles:
        particle.draw(screen)

    # Display "Wow!" message if 99th ball is created
    if wow_message_start_time:
        elapsed_time = time.time() - wow_message_start_time
        if elapsed_time < 1:
            wow_font_size = int(36 + 964 * elapsed_time)  # Grow from 36 to 1000 in one second
            wow_font = pygame.font.Font(None, wow_font_size)
            display_text(screen, "Wow!", wow_font, BLACK, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        else:
            wow_message_start_time = None

    if start_screen:
        font = pygame.font.Font(None, 74)
        text = font.render("Click to start", True, BLACK)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    else:
        ball_count_text = font.render(f"Balls: {ball_count}/{max_balls}", True, BLACK)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(ball_count_text, (10, 10))
        screen.blit(score_text, (10, 50))

        # Draw "Keep going!" message if needed
        if keep_going_message:
            oscillation = 1 + 0.05 * math.sin(2 * math.pi * current_time * 2)
            keep_going_font = pygame.font.Font(None, int(72 * oscillation))  # Larger font size
            keep_going_text = keep_going_font.render("Keep going!", True, BLACK)
            screen.blit(keep_going_text, (SCREEN_WIDTH // 2 - keep_going_text.get_width() // 2, SCREEN_HEIGHT * 1 // 4 - keep_going_text.get_height() // 2))

    pygame.display.flip()
    pygame.time.delay(16)

# Game over screen with play again and quit options
action = game_over_screen(screen, score)
if action == "play_again":
    os.execl(sys.executable, sys.executable, *sys.argv)

pygame.quit()
sys.exit()
