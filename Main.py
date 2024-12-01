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
default_enemy_speed = 0.5
enemy_speed = default_enemy_speed
wave_number = 1
bullet_state = "ready"
active_enemies = []
player_dx = 0
barriers = []
enemy_bullets = []
menu = None
help_button = None
settings_button = None
menu_background = None
help_pen = None
settings_pen = None
buttons = []
direction_changes = 0
enemy_start_y = 250  
def load_high_score():
    global high_score
    if os.path.exists("high_score.txt"):
        with open("high_score.txt", "r") as file:
            high_score = int(file.read())
    else:
        high_score = 0

def save_high_score():
    with open("high_score.txt", "w") as file:
        file.write(str(high_score))

# Load the high score
load_high_score()

# UI Setup
def setup_ui():
    global score_pen, lives_pen, high_score_pen
    # Score display
    score_pen = turtle.Turtle()
    score_pen.speed(0)
    score_pen.color("white")
    score_pen.penup()
    score_pen.setposition(-380, 260)
    score_pen.hideturtle()

    # Lives display
    lives_pen = turtle.Turtle()
    lives_pen.speed(0)
    lives_pen.color("white")
    lives_pen.penup()
    lives_pen.setposition(300, 260)
    lives_pen.hideturtle()

    # High score display
    high_score_pen = turtle.Turtle()
    high_score_pen.speed(0)
    high_score_pen.color("red")
    high_score_pen.penup()
    high_score_pen.setposition(0, 260)
    high_score_pen.hideturtle()

    update_ui()

def update_ui():
    global score, lives, high_score
    score_pen.clear()
    score_pen.write(f"SCORE: {score}".upper(), False, align="left", font=("Agency FB", 14, "bold"))
    
    lives_pen.clear()
    lives_pen.write(f"LIVES: {lives}".upper(), False, align="right", font=("Agency FB", 14, "bold"))
    
    high_score_pen.clear()
    high_score_pen.write(f"HIGH SCORE: {high_score}".upper(), False, align="center", font=("Agency FB", 14, "bold"))

def show_message(message):
    msg_pen = turtle.Turtle()
    msg_pen.speed(0)
    msg_pen.color("yellow")
    msg_pen.penup()
    msg_pen.hideturtle()
    msg_pen.goto(0, 0)
    msg_pen.write(message, align="center", font=("Arial", 24, "bold"))
    
    # Display the final score and high score
    msg_pen.goto(0, -30)
    msg_pen.write(f"Final Score: {score}", align="center", font=("Arial", 18, "normal"))
    msg_pen.goto(0, -60)
    msg_pen.write(f"High Score: {high_score}", align="center", font=("Arial", 18, "normal"))
    
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

# MotherShip setup
def setup_mothership():
    global mothership
    mothership = turtle.Turtle()
    mothership.color("purple")
    mothership.shape("mothership.gif")
    mothership.penup()
    mothership.speed(0)
    mothership.setposition(-400, 200)
    mothership.setheading(0)
    mothership.dx = 4
    mothership.dy = 0
    mothership.hideturtle()

def spawn_mothership():
    if not mothership.isvisible() and random.random() < 0.001:  # 0.1% chance per frame
        mothership.setposition(-400, 200)
        mothership.showturtle()

def move_mothership():
    if mothership.isvisible():
        x = mothership.xcor() + mothership.dx
        mothership.setx(x)
        if x > 400:
            mothership.hideturtle()
            mothership.setposition(-1000, 1000)  # Move it off-screen

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
    global active_enemies, initial_enemy_count, enemy_speed
    active_enemies.clear()
    enemy_speed = default_enemy_speed  # Reset enemy speed
    start_x = -275  
    start_y = enemy_start_y 
    rows = [
        {"shape": "invader1.gif", "points": 10, "count": 11},  # Row 1
        {"shape": "invader3.gif", "points": 30, "count": 11},  # Row 2
        {"shape": "invader3.gif", "points": 30, "count": 11},  # Row 3
        {"shape": "invader2.gif", "points": 20, "count": 11},  # Row 4
        {"shape": "invader2.gif", "points": 20, "count": 11},  # Row 5
    ]

    row_spacing = 50   
    enemy_spacing = 50   

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
            enemy.is_mothership = False  
            active_enemies.append(enemy)

    initial_enemy_count = len([e for e in active_enemies if not e.is_mothership]) 

def move_enemies():
    global enemy_speed, game_over, enemy_start_y

    # Movement boundaries
    left_boundary = -380
    right_boundary = 380

    boundary_hit = False

    # Move enemies horizontally
    for enemy in active_enemies[:]:
        if enemy.isvisible() and not enemy.is_mothership:
            x = enemy.xcor() + enemy_speed
            enemy.setx(x)
            # Check for boundary collision
            if (enemy_speed > 0 and x >= right_boundary) or (enemy_speed < 0 and x <= left_boundary):
                boundary_hit = True

    # Handle boundary collision after moving all enemies
    if boundary_hit:
        enemy_speed *= -1

     
        speed_increment = 0.4  
        max_enemy_speed = 6.0  
        if abs(enemy_speed) + speed_increment <= max_enemy_speed:
            if enemy_speed > 0:
                enemy_speed += speed_increment
            else:
                enemy_speed -= speed_increment
        else:
            # Cap the enemy speed at maximum limit
            if enemy_speed > 0:
                enemy_speed = max_enemy_speed
            else:
                enemy_speed = -max_enemy_speed

        # Move enemies down by 10 units
        for enemy in active_enemies[:]:
            if enemy.isvisible() and not enemy.is_mothership:
                y = enemy.ycor() - 10  # Move down by 10 units
                enemy.sety(y)
                # Check for game over condition
                if y < -250:
                    game_over = True
                    return

        # Correct enemy positions to stay within boundaries
        for enemy in active_enemies[:]:
            if enemy.isvisible() and not enemy.is_mothership:
                x = enemy.xcor()
                # Adjust positions if they go beyond the boundaries
                if x > right_boundary:
                    enemy.setx(right_boundary)
                elif x < left_boundary:
                    enemy.setx(left_boundary)

    # Move the mothership (if applicable)
    for enemy in active_enemies[:]:
        if enemy.isvisible() and enemy.is_mothership:
            x = enemy.xcor() + enemy.dx
            enemy.setx(x)
            if x > 400:
                enemy.hideturtle()
                enemy.setposition(-1000, 1000)
                active_enemies.remove(enemy)

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
        elif is_collision(player, bullet, distance=15): 
            play_sound("player_hit.wav")
            bullet.hideturtle()
            if bullet in enemy_bullets:
                enemy_bullets.remove(bullet)
            lose_life()

        # Enemy bullets collision with barriers
        for block in barriers[:]:
            if is_collision(bullet, block, distance=10): 
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
    global game_over, score, wave_number, enemy_speed, bullet_state, high_score, enemy_start_y  # Add enemy_start_y to the global declaration
    if not game_over:
        move_player()
        move_bullet()
        move_enemies()
        move_enemy_bullets()
        spawn_mothership()
        move_mothership()

        # Player bullet collision with enemies
        for enemy in active_enemies[:]:
            if is_collision(bullet, enemy):
                play_sound("explosion.wav")
                bullet.hideturtle()
                bullet_state = "ready"
                score += enemy.points
                
                # Update high score if necessary
                if score > high_score:
                    high_score = score
                    save_high_score()  
                update_ui()

                # Explosion effect
                enemy.shape("explosion.gif")
                wn.update()
                time.sleep(0.1) 
                enemy.hideturtle()
                active_enemies.remove(enemy)
                break

        for enemy in active_enemies:
            if is_collision(player, enemy):
                game_over = True
                break

        if is_collision(bullet, mothership):
            play_sound("explosion_bonus.wav")
            bullet.hideturtle()
            bullet_state = "ready"
            update_ui()
            # Explosion effect
            mothership.shape("explosion_bonus.gif")
            wn.update()
            time.sleep(0.1)  
            mothership.hideturtle()
            mothership.shape("mothership.gif")  
            score += 150  

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

        # Check for collision between player's bullet and mothership
        if bullet_state == "fire" and mothership.isvisible():
            if is_collision(bullet, mothership, distance=20):
                # Hide the bullet
                bullet.hideturtle()
                bullet_state = "ready"

                # Hide the mothership and move it off-screen
                mothership.hideturtle()
                mothership.setposition(-1000, 1000) 

                global player_score
                player_score += 100
                update_ui()

        # Move the mothership
        move_mothership()

        if not active_enemies:
            wave_number += 1
            enemy_speed += 0.3
            lives = 3
            enemy_start_y -= 25 
            if enemy_start_y < 50:
                enemy_start_y = 50
            update_ui()
            create_enemies()

        if game_over:
            if score > high_score:
                high_score = score
                save_high_score()
            show_message("Game Over!")
            return

        wn.update()
        wn.ontimer(game_loop, 20)
    else:
        show_message("Game Over!")


def show_help():
    global help_pen
    wn.bgpic("help_background.gif")  
    # Create the pen for help text
    help_pen = turtle.Turtle()
    help_pen.hideturtle()
    help_pen.penup()
    help_pen.color("white")
    help_pen.goto(0, 0)
    wn.onkeypress(start_game, "s")
    wn.onkeypress(show_menu, "q")
    wn.listen()



# Start game function
def start_game(x=None, y=None):
    global game_over, score, lives, enemy_speed, wave_number, bullet_state, direction_changes
    game_over = False
    score = 0
    lives = 3
    wave_number = 1
    bullet_state = "ready"
    enemy_speed = default_enemy_speed
    direction_changes = 0  
    wn.onkeypress(None, "i")
    wn.onkeypress(None, "q")
    wn.onkeypress(None, "s")
    print("Starting the game...")
    wn.bgcolor("black")
    wn.bgpic("space_invaders_background.gif")  
    setup_ui()
    setup_player()
    setup_bullet()
    setup_mothership()
    create_barriers()
    create_enemies()

    wn.onkeypress(move_left, "Left")
    wn.onkeypress(move_right, "Right")
    wn.onkeyrelease(stop_player, "Left")
    wn.onkeyrelease(stop_player, "Right")
    wn.onkey(fire_bullet, "space")
    wn.listen()

    threading.Thread(target=play_background_music, daemon=True).start()

    game_loop()


def show_menu():
    global menu, help_button, settings_button, menu_background, start_button
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
    wn.onkeypress(show_help, "i")
    wn.onkeypress(start_game, "s")
    wn.listen()

# Start background music in a separate thread
threading.Thread(target=play_background_music, daemon=True).start()

if __name__ == "__main__":
    show_menu()
    wn.mainloop()
