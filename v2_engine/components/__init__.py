"""
Components package for Scribe Engine V2.

Components add modular behaviors to sprites.
"""

from v2_engine.components.component import Component
from v2_engine.components.rigidbody import RigidBody
from v2_engine.components.box_collider import BoxCollider
from v2_engine.components.platformer_controller import PlatformerController
from v2_engine.components.scene_trigger import SceneTrigger

__all__ = ['Component', 'RigidBody', 'BoxCollider', 'PlatformerController', 'SceneTrigger']
