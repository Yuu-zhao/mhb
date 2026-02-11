# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any, List

class Appearance:
    def __init__(
        self,
        appearance_id: Optional[int] = None,
        product_id: Optional[int] = None,
        dyed_fruit_count: Optional[str] = None,
        saved_dye_schemes: Optional[str] = None,
        total_dyed_fruit_count: Optional[str] = None,
        title_effects: Optional[List[str]] = None,
        spell_attack_effects: Optional[List[str]] = None,
        bubble_frames: Optional[List[str]] = None,
        avatar_frames: Optional[List[str]] = None,
        team_logos: Optional[List[str]] = None,
        xianyu_balance: Optional[str] = None,
        xianyu_points: Optional[str] = None,
        qicai_points: Optional[str] = None,
        total_outfits_count: Optional[str] = None,
        limited_outfits: Optional[List[str]] = None,
        pendants: Optional[List[str]] = None,
        normal_outfits: Optional[List[str]] = None,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        self.appearance_id = appearance_id
        self.product_id = product_id
        self.dyed_fruit_count = dyed_fruit_count
        self.saved_dye_schemes = saved_dye_schemes
        self.total_dyed_fruit_count = total_dyed_fruit_count
        self.title_effects = title_effects if title_effects is not None else []
        self.spell_attack_effects = spell_attack_effects if spell_attack_effects is not None else []
        self.bubble_frames = bubble_frames if bubble_frames is not None else []
        self.avatar_frames = avatar_frames if avatar_frames is not None else []
        self.team_logos = team_logos if team_logos is not None else []
        self.xianyu_balance = xianyu_balance
        self.xianyu_points = xianyu_points
        self.qicai_points = qicai_points
        self.total_outfits_count = total_outfits_count
        self.limited_outfits = limited_outfits if limited_outfits is not None else []
        self.pendants = pendants if pendants is not None else []
        self.normal_outfits = normal_outfits if normal_outfits is not None else []
        self.raw_data = raw_data if raw_data is not None else {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "appearance_id": self.appearance_id,
            "product_id": self.product_id,
            "dyed_fruit_count": self.dyed_fruit_count,
            "saved_dye_schemes": self.saved_dye_schemes,
            "total_dyed_fruit_count": self.total_dyed_fruit_count,
            "title_effects": self.title_effects,
            "spell_attack_effects": self.spell_attack_effects,
            "bubble_frames": self.bubble_frames,
            "avatar_frames": self.avatar_frames,
            "team_logos": self.team_logos,
            "xianyu_balance": self.xianyu_balance,
            "xianyu_points": self.xianyu_points,
            "qicai_points": self.qicai_points,
            "total_outfits_count": self.total_outfits_count,
            "limited_outfits": self.limited_outfits,
            "pendants": self.pendants,
            "normal_outfits": self.normal_outfits,
            "raw_data": self.raw_data
        }

    def __repr__(self):
        return f"<Appearance(id={self.appearance_id}, total_outfits='{self.total_outfits_count}')>"
