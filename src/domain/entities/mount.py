# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any, List

class Mount:
    def __init__(
        self,
        mount_id: Optional[int] = None,
        product_id: Optional[int] = None,
        name: Optional[str] = None,
        mount_type: Optional[str] = None,
        level: Optional[str] = None,
        main_attribute: Optional[str] = None,
        growth: Optional[str] = None,
        skills: Optional[List[Dict[str, Any]]] = None,
        xuanlingzhu: Optional[Dict[str, Any]] = None,
        auspicious_beast_skill: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        self.mount_id = mount_id
        self.product_id = product_id
        self.name = name
        self.mount_type = mount_type
        self.level = level
        self.main_attribute = main_attribute
        self.growth = growth
        self.skills = skills if skills is not None else []
        self.xuanlingzhu = xuanlingzhu if xuanlingzhu is not None else {}
        self.auspicious_beast_skill = auspicious_beast_skill
        self.raw_data = raw_data if raw_data is not None else {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mount_id": self.mount_id,
            "product_id": self.product_id,
            "name": self.name,
            "mount_type": self.mount_type,
            "level": self.level,
            "main_attribute": self.main_attribute,
            "growth": self.growth,
            "skills": self.skills,
            "xuanlingzhu": self.xuanlingzhu,
            "auspicious_beast_skill": self.auspicious_beast_skill,
            "raw_data": self.raw_data
        }

    def __repr__(self):
        return f"<Mount(id={self.mount_id}, name='{self.name}', type='{self.mount_type}')>"
