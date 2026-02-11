# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any

class Home:
    def __init__(
        self,
        home_id: Optional[int] = None,
        product_id: Optional[int] = None,
        house_level: Optional[str] = None,
        house_stability: Optional[str] = None,
        house_fengshui: Optional[str] = None,
        house_type: Optional[str] = None,
        furniture_score: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        self.home_id = home_id
        self.product_id = product_id
        self.house_level = house_level
        self.house_stability = house_stability
        self.house_fengshui = house_fengshui
        self.house_type = house_type
        self.furniture_score = furniture_score
        self.raw_data = raw_data if raw_data is not None else {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "home_id": self.home_id,
            "product_id": self.product_id,
            "house_level": self.house_level,
            "house_stability": self.house_stability,
            "house_fengshui": self.house_fengshui,
            "house_type": self.house_type,
            "furniture_score": self.furniture_score,
            "raw_data": self.raw_data
        }

    def __repr__(self):
        return f"<Home(id={self.home_id}, level='{self.house_level}', fengshui='{self.house_fengshui}')>"
