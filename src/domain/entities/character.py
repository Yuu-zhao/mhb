# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any, List

class Character:
    def __init__(
        self,
        character_id: Optional[int] = None,
        product_id: Optional[int] = None,
        level: Optional[str] = None,
        role_name: Optional[str] = None,
        sect: Optional[str] = None,
        new_qianyuan_dan_count: Optional[str] = None,
        mooncake_zongzi_chance: Optional[str] = None,
        ascension_tribulation_sainthood: Optional[str] = None,
        achievement_points: Optional[str] = None,
        used_potential_fruit_count: Optional[str] = None,
        total_experience: Optional[str] = None,
        attack_cultivation: Optional[str] = None,
        defense_cultivation: Optional[str] = None,
        magic_cultivation: Optional[str] = None,
        magic_resistance_cultivation: Optional[str] = None,
        hunting_skill_cultivation: Optional[str] = None,
        beast_rearing_skill: Optional[str] = None,
        attack_control: Optional[str] = None,
        defense_control: Optional[str] = None,
        magic_control: Optional[str] = None,
        magic_resistance_control: Optional[str] = None,
        school_skills: Optional[List[Dict[str, Any]]] = None,
        life_skills: Optional[List[Dict[str, Any]]] = None,
        story_skills: Optional[List[Dict[str, Any]]] = None,
        story_skill_remaining_points: Optional[str] = None,
        proficiency: Optional[Dict[str, str]] = None,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        self.character_id = character_id
        self.product_id = product_id
        self.level = level
        self.role_name = role_name
        self.sect = sect
        self.new_qianyuan_dan_count = new_qianyuan_dan_count
        self.mooncake_zongzi_chance = mooncake_zongzi_chance
        self.ascension_tribulation_sainthood = ascension_tribulation_sainthood
        self.achievement_points = achievement_points
        self.used_potential_fruit_count = used_potential_fruit_count
        self.total_experience = total_experience
        self.attack_cultivation = attack_cultivation
        self.defense_cultivation = defense_cultivation
        self.magic_cultivation = magic_cultivation
        self.magic_resistance_cultivation = magic_resistance_cultivation
        self.hunting_skill_cultivation = hunting_skill_cultivation
        self.beast_rearing_skill = beast_rearing_skill
        self.attack_control = attack_control
        self.defense_control = defense_control
        self.magic_control = magic_control
        self.magic_resistance_control = magic_resistance_control
        self.school_skills = school_skills if school_skills is not None else []
        self.life_skills = life_skills if life_skills is not None else []
        self.story_skills = story_skills if story_skills is not None else []
        self.story_skill_remaining_points = story_skill_remaining_points
        self.proficiency = proficiency if proficiency is not None else {}
        self.raw_data = raw_data if raw_data is not None else {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "product_id": self.product_id,
            "level": self.level,
            "role_name": self.role_name,
            "sect": self.sect,
            "new_qianyuan_dan_count": self.new_qianyuan_dan_count,
            "mooncake_zongzi_chance": self.mooncake_zongzi_chance,
            "ascension_tribulation_sainthood": self.ascension_tribulation_sainthood,
            "achievement_points": self.achievement_points,
            "used_potential_fruit_count": self.used_potential_fruit_count,
            "total_experience": self.total_experience,
            "attack_cultivation": self.attack_cultivation,
            "defense_cultivation": self.defense_cultivation,
            "magic_cultivation": self.magic_cultivation,
            "magic_resistance_cultivation": self.magic_resistance_cultivation,
            "hunting_skill_cultivation": self.hunting_skill_cultivation,
            "beast_rearing_skill": self.beast_rearing_skill,
            "attack_control": self.attack_control,
            "defense_control": self.defense_control,
            "magic_control": self.magic_control,
            "magic_resistance_control": self.magic_resistance_control,
            "school_skills": self.school_skills,
            "life_skills": self.life_skills,
            "story_skills": self.story_skills,
            "story_skill_remaining_points": self.story_skill_remaining_points,
            "proficiency": self.proficiency,
            "raw_data": self.raw_data
        }

    def __repr__(self):
        return f"<Character(id={self.character_id}, level='{self.level}', role='{self.role_name}')>"
