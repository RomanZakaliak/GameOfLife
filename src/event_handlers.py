import pygame

def on_game_pause(event, pause):
    if event.key == pygame.K_SPACE:
        pause = not pause
    
    return pause
