"""The handlers for exchanging objects with the game process
"""
from . import base

def send_to_game(obj):
    """
    Send an object to the game process

    @param obj The object to be sent
    """
    base.send_to_game(obj)

def recv_from_game():
    """
    Receive an object from the game process

    The method will wait until it receives the object.

    @return The received object.
    """
    return base.recv_from_game()


def ml_ready():
    """
    Inform the game process that the ml process is ready.
    """
    send_to_game("READY")