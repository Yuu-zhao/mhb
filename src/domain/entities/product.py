# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional, Dict, Any, List

class Product:
    def __init__(
        self,
        product_id: Optional[int] = None,
        item_id: str = "", # 对应藏宝阁的编号eid
        product_type: str = "角色", # 角色, 道具, 召唤兽等
        url: str = "",
        price: Optional[float] = None,
        seller_id: Optional[str] = None,
        seller_name: Optional[str] = None,
        listed_status: Optional[str] = None,
        bargainable: Optional[bool] = None,
        time_remaining: Optional[str] = None,
        highlights: Optional[List[str]] = None,
        extracted_data: Optional[Dict[str, Any]] = None, # 存储所有原始提取数据
        created_at: Optional[datetime] = None
    ):
        self.product_id = product_id
        self.item_id = item_id
        self.product_type = product_type
        self.url = url
        self.price = price
        self.seller_id = seller_id
        self.seller_name = seller_name
        self.listed_status = listed_status
        self.bargainable = bargainable
        self.time_remaining = time_remaining
        self.highlights = highlights if highlights is not None else []
        self.extracted_data = extracted_data if extracted_data is not None else {}
        self.created_at = created_at if created_at is not None else datetime.now()
        
        # 关联的领域实体
        self.character = None
        self.items = []
        self.pets = []
        self.mount = None
        self.appearance = None
        self.home = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "item_id": self.item_id,
            "product_type": self.product_type,
            "url": self.url,
            "price": self.price,
            "seller_id": self.seller_id,
            "seller_name": self.seller_name,
            "listed_status": self.listed_status,
            "bargainable": self.bargainable,
            "time_remaining": self.time_remaining,
            "highlights": self.highlights,
            "extracted_data": self.extracted_data,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Product(id={self.product_id}, type='{self.product_type}', item_id='{self.item_id}')>"
