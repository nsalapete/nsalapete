import turtle
import os
import platform
import time
import random
import threading

# Platform-specific sound handling
if platform.system() == "Windows":
    try:
        import winsound
    except ImportError:
        print("winsound module not available")

# Screen setup
wn = turtle.Screen()
wn.bgcolor("black")
wn.title("Space Invaders")
wn.setup(width=800, height=600)
wn.tracer(0)

# Register shapes
turtle.register_shape("invader1.gif")  
turtle.register_shape("invader2.gif")
turtle.register_shape("invader3.gif")  
turtle.register_shape("player.gif")
turtle.register_shape("explosion.gif")
turtle.register_shape("barrier.gif")
turtle.register_shape("laser.gif")
turtle.register_shape("invader_laser.gif")
turtle.register_shape("explosion_bonus.gif")
turtle.register_shape("mothership.gif")


# Global variables
score = 0
high_score = 0
lives = 3
game_over = False
player_speed = 5
bullet_speed = 20
enemy_speed = 0.4
wave_number = 1
bullet_state = "ready"
active_enemies = []
player_dx = 0
barriers = []
enemy_bullets = []

# UI Setup
def setup_ui():
    global score_pen, lives_pen
    score_pen = turtle.Turtle()
    score_pen.speed(0)
    score_pen.color("white")
    score_pen.penup()
    score_pen.setposition(-380, 260)
    score_pen.hideturtle()

    lives_pen = turtle.Turtle()
    lives_pen.speed(0)
    lives_pen.color("white")
    lives_pen.penup()
    lives_pen.setposition(300, 260)
    lives_pen.hideturtle()

    update_ui()

def update_ui():
    global score, lives
    score_pen.clear()
    score_pen.write(f"Score: {score}", False, align="left", font=("Arial", 14, "normal"))
    lives_pen.clear()
    lives_pen.write(f"Lives: {lives}", False, align="right", font=("Arial", 14, "normal"))

def show_message(message):
    msg_pen = turtle.Turtle()
    msg_pen.speed(0)
    msg_pen.color("yellow")
    msg_pen.penup()
    msg_pen.hideturtle()
    msg_pen.write(message, align="center", font=("Arial", 24, "bold"))
    wn.update()
    time.sleep(2)
    msg_pen.clear()

# Sound handling
def play_sound(sound_file):
    try:
        if platform.system() == "Windows":
            winsound.PlaySound(sound_file, winsound.SND_ASYNC)
        elif platform.system() == "Linux":
            os.system(f"aplay -q {sound_file} &")
        else:
            os.system(f"afplay {sound_file} &")
    except:
        print("Sound file missing or cannot play.")

def play_background_music():
    winsound.PlaySound('background_music.wav', winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)

# Player setup
def setup_player():
    global player
    player = turtle.Turtle()
    player.color("blue")
    player.shape("player.gif")
    player.penup()
    player.speed(0)
    player.setposition(0, -250)

def move_player():
    global player_dx
    x = player.xcor() + player_dx
    if x < -380:
        x = -380
    if x > 380:
        x = 380
    player.setx(x)

def move_left():
    global player_dx
    player_dx = -player_speed

def move_right():
    global player_dx
    player_dx = player_speed

def stop_player():
    global player_dx
    player_dx = 0

# Bullet setup
def setup_bullet():
    global bullet
    bullet = turtle.Turtle()
    bullet.color("yellow")
    bullet.shape("laser.gif")
    bullet.penup()
    bullet.speed(0)
    bullet.setheading(90)
    bullet.shapesize(0.5, 0.5)
    bullet.hideturtle()

def fire_bullet():
    global bullet_state
    if bullet_state == "ready":
        play_sound("laser.wav")
        bullet_state = "fire"
        x = player.xcor()
        y = player.ycor() + 10
        bullet.setposition(x, y)
        bullet.showturtle()

def move_bullet():
    global bullet_state
    if bullet_state == "fire":
        y = bullet.ycor() + bullet_speed
        bullet.sety(y)
        if y > 290:
            bullet.hideturtle()
            bullet_state = "ready"
#MotherShip setup
def setup_mothership():
    global mothership
    mothership = turtle.Turtle()
    mothership.color("purple")
    mothership.shape("mothership.gif")
    mothership.penup()
    mothership.speed(0)
    mothership.setposition(-400, 200)
    mothership.setheading(0)
    mothership.dx = 0.5
    mothership.dy = 0
    mothership.showturtle()
def spawn_mothership():
    if random.random() < 0.01:  # 1% chance per frame for the mothership to appear
        mothership.showturtle()
        mothership.setx(random.randint(-400, 400))
        mothership.sety(270)

def move_mothership():
    if mothership.isvisible():
        x = mothership.xcor() + mothership.dx
        mothership.setx(x)
        if x > 400:
            mothership.hideturtle()


def mothership_fire(mothership):
    if random.random() < 0.01:  # 1% chance per frame for the mothership to fire
        bullet = turtle.Turtle()
        bullet.color("red")
        bullet.shape("invader_laser.gif")
        bullet.penup()
        bullet.speed(0)
        bullet.setheading(270)
        bullet.shapesize(0.5, 0.5)
        bullet.setposition(mothership.xcor(), mothership.ycor())
        enemy_bullets.append(bullet)
# Enemy setup
def create_enemies():
    global active_enemies, initial_enemy_count
    active_enemies.clear()
    start_x = -275  # Adjusted to fit 11 enemies with spacing
    start_y = 250
    rows = [
        {"shape": "invader1.gif", "points": 10, "count": 11},  # Row 1 (Topmost)
        {"shape": "invader3.gif", "points": 30, "count": 11},  # Row 2
        {"shape": "invader3.gif", "points": 30, "count": 11},  # Row 3
        {"shape": "invader2.gif", "points": 20, "count": 11},  # Row 4
        {"shape": "invader2.gif", "points": 20, "count": 11},  # Row 5
    ]
    
    row_spacing = 50     # Vertical spacing between rows
    enemy_spacing = 50   # Horizontal spacing between enemies

    for row_index, row in enumerate(rows):
        shape = row["shape"]
        points = row["points"]
        count = row["count"]
        y_position = start_y - (row_spacing * row_index)
        
        for i in range(count):
            enemy = turtle.Turtle()
            enemy.shape(shape)
            enemy.penup()
            enemy.speed(0)
            x_position = start_x + (enemy_spacing * i)
            enemy.setposition(x_position, y_position)
            enemy.points = points
            active_enemies.append(enemy)
    
    initial_enemy_count = len(active_enemies)  # Set the initial enemy count

def move_enemies():
    global enemy_speed, game_over
    for enemy in active_enemies:
        x = enemy.xcor() + enemy_speed
        enemy.setx(x)
        if x > 380 or x < -380:
            enemy_speed *= -1
            for e in active_enemies:
                e.sety(e.ycor() - 40)
        if enemy.ycor() < -250:
            game_over = True

def enemy_fire():
    if random.random() < 0.03:  # 3% chance per frame for an enemy to fire
        firing_enemy = random.choice(active_enemies)
        bullet = turtle.Turtle()
        bullet.color("red")
        bullet.shape("invader_laser.gif")
        bullet.penup()
        bullet.speed(0)
        bullet.setheading(270)
        bullet.shapesize(0.5, 0.5)
        bullet.setposition(firing_enemy.xcor(), firing_enemy.ycor())
        enemy_bullets.append(bullet)

def move_enemy_bullets():
    for bullet in enemy_bullets[:]:
        bullet.sety(bullet.ycor() - bullet_speed // 2)
        if bullet.ycor() < -300:
            bullet.hideturtle()
            if bullet in enemy_bullets:
                enemy_bullets.remove(bullet)
        elif is_collision(player, bullet, distance=15):  # Adjusted collision distance
            play_sound("player_hit.wav")
            bullet.hideturtle()
            if bullet in enemy_bullets:
                enemy_bullets.remove(bullet)
            lose_life()

        # Enemy bullets collision with barriers
        for block in barriers[:]:
            if is_collision(bullet, block, distance=10):  # Adjusted collision distance
                bullet.hideturtle()
                if bullet in enemy_bullets:
                    enemy_bullets.remove(bullet)
                block.hideturtle()
                if block in barriers:
                    barriers.remove(block)
                break


# Barrier setup
def create_barriers():
    global barriers
    barriers.clear()
    start_x = -300
    start_y = -200
    barrier_shape = [
        [0,0,1,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1],
    ]
    for i in range(4):  # Create 4 barriers
        barrier_blocks = []
        num_rows = len(barrier_shape)
        for row_index, row in enumerate(barrier_shape):
            for col_index, block_present in enumerate(row):
                if block_present:
                    block = turtle.Turtle()
                    block.shape("square")
                    block.color("green")
                    block.shapesize(stretch_wid=0.5, stretch_len=0.5)
                    block.penup()
                    block.speed(0)
                    x = start_x + (200 * i) + (col_index * 10)
                    # Flip the y-coordinate calculation
                    y = start_y + ((num_rows - 1 - row_index) * 10)
                    block.setposition(x, y)
                    barrier_blocks.append(block)
        barriers.extend(barrier_blocks)

# Player bullet collision with barriers
def handle_bullet_barrier_collision():
    global bullet_state
    for block in barriers[:]:
        if is_collision(bullet, block, distance=10):  # Adjusted collision distance
            bullet.hideturtle()
            bullet_state = "ready"
            block.hideturtle()
            if block in barriers:
                barriers.remove(block)
            break

# Collision detection
def is_collision(t1, t2, distance=20):
    return t1.distance(t2) < distance

def lose_life():
    global lives, game_over
    lives -= 1
    update_ui()
    if lives <= 0:
        game_over = True

# Game loop
def game_loop():
    global game_over, score, wave_number, enemy_speed, bullet_state
    while not game_over:
        wn.update()
        move_player()
        move_bullet()
        move_enemies()
        move_enemy_bullets()
        spawn_mothership()
        mothership_fire(mothership)
        move_mothership()

        # Player bullet collision with enemies
        for enemy in active_enemies[:]:
            if is_collision(bullet, enemy):
                play_sound("explosion.wav")
                bullet.hideturtle()
                bullet_state = "ready"
                score += enemy.points
                update_ui()

                # Explosion effect
                enemy.shape("explosion.gif")
                wn.update()
                time.sleep(0.1)  # Duration of the explosion

                enemy.hideturtle()
                active_enemies.remove(enemy)
                break
        for enemy in active_enemies:
            if is_collision(player, enemy):
                game_over = True
                break
        for enemy in active_enemies:
            if is_collision(bullet, mothership):
                play_sound("explosion_bonus.wav")
                bullet.hideturtle()
                bullet_state = "ready"
                update_ui()
                #Explosion effect
                mothership.shape("explosion_bonus.gif")
                wn.update()
                time.sleep(0.1)  # Duration of the explosion
                mothership.hideturtle()
                mothership.shape("mothership.gif") # Reset the shape back to original
                score = score + 150  
                break
            
        # Player bullet collision with barriers
        for block in barriers[:]:
            if is_collision(bullet, block, distance=5):
                bullet.hideturtle()
                bullet_state = "ready"
                block.hideturtle()
                barriers.remove(block)
                break

        # Enemy bullets collision with barriers
        for e_bullet in enemy_bullets[:]:
            for block in barriers[:]:
                if is_collision(e_bullet, block, distance=5):
                    e_bullet.hideturtle()
                    enemy_bullets.remove(e_bullet)
                    block.hideturtle()
                    barriers.remove(block)
                    break
            else:
                continue
            break

        # Enemy bullets collision with player
        for e_bullet in enemy_bullets[:]:
            if is_collision(player, e_bullet):
                play_sound("player_hit.wav")
                e_bullet.hideturtle()
                enemy_bullets.remove(e_bullet)
                lose_life()
                break

        enemy_fire()
        
        if not active_enemies:
            wave_number += 1
            enemy_speed += 0.2
            create_barriers()  # Reset barriers
            create_enemies()
        
        if game_over:
            show_message("Game Over!")
            break

        time.sleep(0.02)

# Start game function
def start_game():
    # Hide the menu
    menu.clear()
    menu.hideturtle()
    wn.bgpic("space_invaders_background.gif")  # Set the game background

    # Initialize game components
    setup_ui()
    setup_player()
    setup_bullet()
    setup_mothership()
    create_barriers()
    move_mothership()
    create_enemies()
    
    # Keyboard bindings
    wn.onkeypress(move_left, "Left")
    wn.onkeypress(move_right, "Right")
    wn.onkeyrelease(stop_player, "Left")
    wn.onkeyrelease(stop_player, "Right")
    wn.onkey(fire_bullet, "space")
    wn.listen()

    # Start background music
    threading.Thread(target=play_background_music, daemon=True).start()

    # Run the game loop
    game_loop()
  
# Button creation function
def create_button(label, position, onclick_function):
    button = turtle.Turtle()
    button.shape("square")
    button.color("gray")
    button.penup()
    button.goto(position)
    button.shapesize(stretch_wid=2, stretch_len=5)
    button.showturtle()
    text = turtle.Turtle()
    text.hideturtle()
    text.penup()
    text.color("white")
    text.goto(position)
    text.write(label, align="center", font=("Arial", 16, "normal"))
    button.onclick(onclick_function)
    return button

# Show help function
def show_help(x,y):
    print("Help button clicked")
    help_pen = turtle.Turtle()
    help_pen.hideturtle()
    help_pen.penup()
    help_pen.color("white")
    help_pen.goto(0, 0)
    wn.bgpic("help_background.gif")

def hide_help():
    print("Returning to menu from Help")
    help_pen.clear()
    menu_background.showturtle()
    help_button.showturtle()
    settings_button.showturtle()

wn.onkeypress(hide_help, "q")
wn.listen()

settings_pen = None

def show_settings(x, y):
    print("Settings button clicked")
    global settings_pen
    menu.hideturtle()
    menu_background.hideturtle()
    help_button.hideturtle()
    settings_button.hideturtle()

    # Créer le pen pour les paramètres
    settings_pen = turtle.Turtle()
    settings_pen.hideturtle()
    settings_pen.penup()
    settings_pen.color("white")
    settings_pen.goto(0, 0)

    settings_text = """
Parameters:

- Music Volume : ████░░░░░
- Effects Volume : ████░░░░░

Press 'q' to return to the menu.
    """
    settings_pen.write(settings_text, align="center", font=("Arial", 14, "normal"))

    # Assigner la touche 'q' pour revenir au menu
    wn.onkeypress(hide_settings, "q")
    wn.listen()

def hide_settings():
    print("Returning to menu from Settings")
    global settings_pen
    if settings_pen:
        settings_pen.clear()
        settings_pen.hideturtle()
    menu.showturtle()
    menu_background.showturtle()
    help_button.showturtle()
    settings_button.showturtle()

    wn.bgpic("menu_background.gif")

    wn.onkeypress(None, "q")

# Show menu function
def show_menu():
    global menu, help_button, settings_button, menu_background
    wn.bgpic("menu_background.gif")

    menu_background = turtle.Turtle()
    menu_background.hideturtle()
    menu_background.penup()
    menu_background.color("white")
    menu_background.goto(0, 250)

    menu = turtle.Turtle()
    menu.hideturtle()
    menu.penup()
    menu.color("black")
    menu.goto(0, -50)


    help_button = create_button("Help", (-350, 250), show_help)
    settings_button = create_button("Settings", (350, 250), show_settings)


    wn.onkeypress(start_game, "s")
    wn.listen()

# Main execution
show_menu()

# Start background music in a separate thread
threading.Thread(target=play_background_music).start()

wn.mainloop()