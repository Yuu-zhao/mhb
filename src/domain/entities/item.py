# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any

class Item:
    def __init__(
        self,
        item_id: Optional[int] = None,
        product_id: Optional[int] = None,
        name: Optional[str] = None,
        item_type: Optional[str] = None,
        description: Optional[str] = None,
        icon_url: Optional[str] = None,
        is_equipped: bool = False,
        category: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        self.item_id = item_id
        self.product_id = product_id
        self.name = name
        self.item_type = item_type
        self.description = description
        self.icon_url = icon_url
        self.is_equipped = is_equipped
        self.category = category
        self.raw_data = raw_data if raw_data is not None else {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "product_id": self.product_id,
            "name": self.name,
            "item_type": self.item_type,
            "description": self.description,
            "icon_url": self.icon_url,
            "is_equipped": self.is_equipped,
            "category": self.category,
            "raw_data": self.raw_data
        }

    def __repr__(self):
        return f"<Item(id={self.item_id}, name='{self.name}', type='{self.item_type}')>"
