import pygame
import random
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

SPEED_DECREMENT = 2

class Train:

    def __init__(self, x, y, agent_name):
        self.position = (x, y)
        self.wagons = []
        self.direction = (1, 0)  # Commence vers la droite
        self.alive = True
        self.agent_name = agent_name
        self.move_timer = 0
        self.speed = 60
        self.last_position = (x, y)
        # Utiliser à la fois le logger serveur et client
        self.server_logger = logging.getLogger('server.train')
        self.client_logger = logging.getLogger('client.train')
        self.server_logger.debug(f"Initializing train at position: {x}, {y}")

    def get_position(self):
        return self.position

    def get_opposite_direction(self, direction):
        """Retourne la direction opposée"""
        return (-direction[0], -direction[1])

    def is_opposite_direction(self, new_direction):
        """Vérifie si la nouvelle direction est opposée à la direction actuelle"""
        opposite = self.get_opposite_direction(self.direction)
        logger.debug(f"Current direction: {self.direction}")
        logger.debug(f"New direction: {new_direction}")
        logger.debug(f"Opposite direction: {opposite}")
        return tuple(new_direction) == opposite

    def has_moved(self):
        """Vérifie si le train a bougé depuis sa dernière position"""
        has_moved = self.position != self.last_position
        logger.debug(f"Has moved: {has_moved} (current: {self.position}, last: {self.last_position})")
        return has_moved

    def change_direction(self, new_direction):
        """Change la direction du train si les conditions sont respectées"""
        logger.debug(f"Attempting to change direction from {self.direction} to {new_direction}")
        
        # Convertir new_direction en tuple pour la comparaison
        new_direction = tuple(new_direction)
        
        if self.is_opposite_direction(new_direction):
            logger.debug("Cannot change to opposite direction")
            return False
            
        if not self.has_moved() and new_direction != self.direction:
            logger.debug("Train hasn't moved since last direction change")
            return False
            
        logger.debug(f"Changing direction to: {new_direction}")
        self.direction = new_direction
        self.last_position = self.position
        return True

    def update(self, passengers, grid_size):
        if not self.alive:
            return
            
        self.move_timer += 1
        # if self.move_timer >= self.move_interval:
        if self.move_timer >= 1000/self.speed:
            self.move_timer = 0
            old_position = self.position
            self.move(grid_size, passengers)
            if self.position != old_position:
                self.last_position = old_position

    def add_wagon(self, position):
        logger.debug(f"Adding wagon at position: {position}")
        self.speed -= SPEED_DECREMENT
        self.wagons.append(position)

    def move(self, grid_size, passengers):
        """Déplacement à intervalle régulier"""
        logger.debug("Moving train")
        
        # Sauvegarder la dernière position du dernier wagon pour un possible nouveau wagon
        last_wagon_position = self.wagons[-1] if self.wagons else self.position
        
        # Déplacer les wagons
        if self.wagons:
            for i in range(len(self.wagons) - 1, 0, -1):
                self.wagons[i] = self.wagons[i - 1]
            self.wagons[0] = self.position
        
        # Déplacer la locomotive
        self.position = (
            self.position[0] + self.direction[0] * grid_size,
            self.position[1] + self.direction[1] * grid_size
        )
        
        # Vérifier collision avec passager
        for passenger in passengers:
            if self.position == passenger.position:
                self.add_wagon(last_wagon_position)
                passenger.respawn()
                break

    def serialize(self):
        """
        Convertit l'état du train en un format sérialisable pour l'envoi au client
        """
        return {
            "position": self.position,
            "wagons": self.wagons,
            "direction": self.direction,
            "alive": self.alive,
            "agent_name": self.agent_name
        }

    def check_collisions(self, all_trains):
        for wagon_pos in self.wagons:
            if self.position == wagon_pos:
                collision_msg = f"Train {self.agent_name} collided with its own wagon at {wagon_pos}"
                self.server_logger.warning(collision_msg)
                self.client_logger.warning(collision_msg)
                return True

        for train in all_trains.values():
            if train.agent_name == self.agent_name:
                continue
            
            # Vérifier la collision avec la tête du train
            if self.position == train.position:
                collision_msg = f"Train {self.agent_name} collided with train {train.agent_name}"
                self.server_logger.warning(collision_msg)
                self.client_logger.warning(collision_msg)
                return True
            
            # Vérifier la collision avec les wagons
            for wagon_pos in train.wagons:
                if self.position == wagon_pos:
                    collision_msg = f"Train {self.agent_name} collided with wagon of train {train.agent_name}"
                    self.server_logger.warning(collision_msg)
                    self.client_logger.warning(collision_msg)
                    return True
        
        return False

    def check_out_of_bounds(self, screen_width, screen_height):
        """Vérifie si le train est sorti de l'écran"""
        x, y = self.position
        if (x < 0 or x >= screen_width or y < 0 or y >= screen_height):
            logger.debug(f"Train {self.agent_name} went out of bounds at {self.position}")
            return True
        return False