# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any, List

class Pet:
    def __init__(
        self,
        pet_id: Optional[int] = None,
        product_id: Optional[int] = None,
        name: Optional[str] = None,
        pet_type: Optional[str] = None,
        level: Optional[str] = None,
        is_baby: Optional[bool] = None,
        hp: Optional[str] = None,
        mp: Optional[str] = None,
        attack: Optional[str] = None,
        defense: Optional[str] = None,
        speed: Optional[str] = None,
        magic_attack: Optional[str] = None,
        magic_defense: Optional[str] = None,
        growth: Optional[str] = None,
        five_elements: Optional[str] = None,
        aptitude: Optional[Dict[str, str]] = None,
        skills: Optional[List[Dict[str, Any]]] = None,
        inner_elixirs: Optional[List[Dict[str, Any]]] = None,
        equips: Optional[List[Dict[str, Any]]] = None,
        ornaments: Optional[List[Dict[str, Any]]] = None,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        self.pet_id = pet_id
        self.product_id = product_id
        self.name = name
        self.pet_type = pet_type
        self.level = level
        self.is_baby = is_baby
        self.hp = hp
        self.mp = mp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.magic_attack = magic_attack
        self.magic_defense = magic_defense
        self.growth = growth
        self.five_elements = five_elements
        self.aptitude = aptitude if aptitude is not None else {}
        self.skills = skills if skills is not None else []
        self.inner_elixirs = inner_elixirs if inner_elixirs is not None else []
        self.equips = equips if equips is not None else []
        self.ornaments = ornaments if ornaments is not None else []
        self.raw_data = raw_data if raw_data is not None else {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pet_id": self.pet_id,
            "product_id": self.product_id,
            "name": self.name,
            "pet_type": self.pet_type,
            "level": self.level,
            "is_baby": self.is_baby,
            "hp": self.hp,
            "mp": self.mp,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "magic_attack": self.magic_attack,
            "magic_defense": self.magic_defense,
            "growth": self.growth,
            "five_elements": self.five_elements,
            "aptitude": self.aptitude,
            "skills": self.skills,
            "inner_elixirs": self.inner_elixirs,
            "equips": self.equips,
            "ornaments": self.ornaments,
            "raw_data": self.raw_data
        }

    def __repr__(self):
        return f"<Pet(id={self.pet_id}, name='{self.name}', type='{self.pet_type}')>"
