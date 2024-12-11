import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 850, 627
DEBUG_PANEL_WIDTH = 200

# Colors
WHITE = (255, 255, 255)
GREEN = (106, 163, 41)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (161, 29, 49)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
HOMETEAM = (202, 150, 218)
ENEMYTEAM = (221, 184, 110)

# Circle settings
CIRCLE_RADIUS = 30  # Diameter is 90
NUM_CIRCLES = 4
RAYS_DEFAULT = 24

ROTATION_STEP = math.radians(5)
rotation_angle = 0

TILT_STEP = math.radians(1)
tilt_angle = 0

# Create screen
screen = pygame.display.set_mode((WIDTH + DEBUG_PANEL_WIDTH, HEIGHT))
pygame.display.set_caption("Lidar Sim")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Circle positions and states
circles = [
    {"pos": [150 + i * 200, 150 + i * 100], "dragging": False}
    for i in range(NUM_CIRCLES)
]

goals = [
    [60, 200, 27, 200, BLUE], [763, 200, 27, 200, YELLOW]
]

# Collisions debug data
ray_collisions = {"top": 0, "bottom": 0, "left": 0, "right": 0}

def distance(pos1, pos2):
    """Calculate the distance between two points."""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def is_valid_position(circle_index, new_pos):
    """Check if the circle's new position is valid (within bounds and not colliding)."""
    # Check bounds
    if not (CIRCLE_RADIUS <= new_pos[0] <= WIDTH - 5 - CIRCLE_RADIUS and new_pos[0] > 5 + CIRCLE_RADIUS) or not (CIRCLE_RADIUS <= new_pos[1] <= HEIGHT - 5 - CIRCLE_RADIUS and new_pos[1] >= 5 + CIRCLE_RADIUS):
        return False

    # Check for collisions with other circles
    for i, circle in enumerate(circles):
        if i != circle_index:
            if distance(new_pos, circle["pos"]) < 2 * CIRCLE_RADIUS:
                return False

    return True

def cast_rays(center, num_rays):
    """Cast rays from the edge of the circle and calculate collisions."""
    global ray_collisions
    ray_collisions = {"top": 0, "bottom": 0, "left": 0, "right": 0}

    rays = []
    angle_step = 2 * math.pi / num_rays
    for i in range(num_rays):
        base_angle = i * angle_step + rotation_angle
        tilt = base_angle + tilt_angle
        
        # Start the ray at the edge of the circle based on the base angle
        start_dx = math.cos(base_angle) * CIRCLE_RADIUS
        start_dy = math.sin(base_angle) * CIRCLE_RADIUS
        start_x = center[0] + start_dx
        start_y = center[1] + start_dy
        start_point = (start_x, start_y)
        # Lidar origin point vvv
        # pygame.draw.circle(screen, RED, start_point, 2)
        
        # Ray trajectory determined by the tilt angle
        dx = math.cos(tilt)
        dy = math.sin(tilt)
        
        # Extend ray to the edge of the screen or until blocked
        ray_end = None
        for length in range(1, max(WIDTH, HEIGHT)):
            x = start_x + dx * length * 1.2
            y = start_y + dy * length * 1.2

            # Check for wall collisions
            if x <= 0:
                ray_collisions["left"] += 1
                ray_end = (0, y)
                break
            elif x >= WIDTH:
                ray_collisions["right"] += 1
                ray_end = (WIDTH, y)
                break
            if y <= 0:
                ray_collisions["top"] += 1
                ray_end = (x, 0)
                break
            elif y >= HEIGHT:
                ray_collisions["bottom"] += 1
                ray_end = (x, HEIGHT)
                break

            # Check for collisions with other circles
            for circle in circles[1:]:
                if distance((x, y), circle["pos"]) < CIRCLE_RADIUS:
                    ray_end = (x, y)
                    break

            for goal in goals:
                if x >= goal[0] and x <= goal[0] + goal[2] and y >= goal[1] and y <= goal[1] + goal[3]:
                    ray_end = (x, y)
                    break

            if ray_end:
                break

        if not ray_end:
            ray_end = (x, y)

        rays.append((start_point, ray_end))
    return rays

# Main loop
running = True
num_rays = RAYS_DEFAULT
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                for circle in circles:
                    if distance(event.pos, circle["pos"]) <= CIRCLE_RADIUS:
                        circle["dragging"] = True
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                for circle in circles:
                    circle["dragging"] = False

        elif event.type == pygame.MOUSEMOTION:
            for i, circle in enumerate(circles):
                if circle["dragging"]:
                    new_pos = event.pos
                    if is_valid_position(i, new_pos):
                        circle["pos"] = new_pos
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                rotation_angle -= ROTATION_STEP
            elif event.key == pygame.K_RIGHT:
                rotation_angle += ROTATION_STEP
            if event.key == pygame.K_DOWN:
                tilt_angle -= TILT_STEP
            elif event.key == pygame.K_UP:
                tilt_angle += TILT_STEP

            

    # Clear screen
    screen.fill(GREEN)

    # Draw rectangle border
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT), 5)
    pygame.draw.rect(screen, WHITE, (60, 50, 730, 527), 2)

    for rect in goals:
        pygame.draw.rect(screen, rect[4], (rect[0], rect[1], rect[2], rect[3]), 0)
    # Draw circles
    for circle in circles[:2]:
        pygame.draw.circle(screen, HOMETEAM, (int(circle["pos"][0]), int(circle["pos"][1])), CIRCLE_RADIUS)

    for circle in circles[2:]:
        pygame.draw.circle(screen, ENEMYTEAM, (int(circle["pos"][0]), int(circle["pos"][1])), CIRCLE_RADIUS)

    # Cast rays from the first circle
    rays = cast_rays(circles[0]["pos"], num_rays)
    for ray_start, ray_end in rays:
        pygame.draw.line(screen, ORANGE, ray_start, ray_end, 2)

    # Draw debug panel
    pygame.draw.rect(screen, GRAY, (WIDTH, 0, DEBUG_PANEL_WIDTH, HEIGHT))
    font = pygame.font.SysFont(None, 24)
    y_offset = 20
    for wall, count in ray_collisions.items():
        text = font.render(f"{wall.capitalize()} collisions: {count}", True, BLACK)
        screen.blit(text, (WIDTH + 10, y_offset))
        y_offset += 30
    text = font.render(f"TILT: {round(math.degrees(tilt_angle))}", True, BLACK)
    screen.blit(text, (WIDTH + 10, y_offset))
    text = font.render(f"ROTATION: {round(math.degrees(rotation_angle))}", True, BLACK)
    screen.blit(text, (WIDTH + 10, y_offset + 30))

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
