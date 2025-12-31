#!/usr/bin/env python3
"""
生成示例茶叶数据并插入数据库
"""
from datetime import datetime
from app.db import engine, SessionLocal
from app.models import Tea, Base


def seed_teas():
    """创建数据库表并插入示例数据"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # 检查是否已有数据
    existing = db.query(Tea).count()
    if existing > 0:
        print(f"数据库中已有 {existing} 条茶叶数据，跳过插入")
        db.close()
        return

    # 示例茶叶数据
    teas_data = [
        {
            "name": "老班章古树普洱",
            "category": "pu_er",
            "year": 2020,
            "origin": "云南西双版纳",
            "spec": "357g/饼",
            "price_min": 1200,
            "price_max": 1800,
            "intro": "选用老班章古树茶青，经传统工艺压制，茶汤金黄透亮，香气高扬，回甘持久。",
            "cover_url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800",
            "status": "online",
            "weight": 80
        },
        {
            "name": "白毫银针",
            "category": "white",
            "year": 2023,
            "origin": "福建福鼎",
            "spec": "250g/盒",
            "price_min": 800,
            "price_max": 1200,
            "intro": "白茶中的珍品，满披白毫，如银似雪。清香幽雅，鲜爽甘醇，是白茶中的最高等级。",
            "cover_url": "https://images.unsplash.com/photo-1558160074-4d7d8bdf4256?w=800",
            "status": "online",
            "weight": 75
        },
        {
            "name": "大红袍",
            "category": "yancha",
            "year": 2022,
            "origin": "福建武夷山",
            "spec": "150g/罐",
            "price_min": 600,
            "price_max": 900,
            "intro": "武夷岩茶之王，产于九龙窠悬崖峭壁。香气馥郁，岩韵明显，七泡有余香。",
            "cover_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=800",
            "status": "online",
            "weight": 70
        },
        {
            "name": "金骏眉",
            "category": "black",
            "year": 2023,
            "origin": "福建武夷山",
            "spec": "250g/盒",
            "price_min": 500,
            "price_max": 750,
            "intro": "正山小种的高端品种，全程由制茶师手工制作。汤色金黄，香气花果香明显。",
            "cover_url": "https://images.unsplash.com/photo-1597318181409-cf64d0b5d8a2?w=800",
            "status": "online",
            "weight": 65
        },
        {
            "name": "冰岛古树普洱",
            "category": "pu_er",
            "year": 2019,
            "origin": "云南临沧",
            "spec": "357g/饼",
            "price_min": 2000,
            "price_max": 2800,
            "intro": "冰岛老寨古树茶，甜度突出，生津迅速，喉韵深远，是普洱茶中的极品。",
            "cover_url": "https://images.unsplash.com/photo-1594631252845-29fc4cc8cde9?w=800",
            "status": "online",
            "weight": 85
        },
        {
            "name": "白牡丹",
            "category": "white",
            "year": 2022,
            "origin": "福建福鼎",
            "spec": "300g/盒",
            "price_min": 350,
            "price_max": 500,
            "intro": "采摘一芽一叶或一芽二叶，形似花朵。滋味清淡回甘，花香清雅。",
            "cover_url": "https://images.unsplash.com/photo-1571934811356-5cc061b6821f?w=800",
            "status": "online",
            "weight": 60
        },
        {
            "name": "肉桂",
            "category": "yancha",
            "year": 2021,
            "origin": "福建武夷山",
            "spec": "200g/罐",
            "price_min": 450,
            "price_max": 650,
            "intro": "武夷岩茶当家品种之一，香气辛锐持久，桂皮香气明显，滋味醇厚甘爽。",
            "cover_url": "https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=800",
            "status": "online",
            "weight": 55
        },
        {
            "name": "祁门红茶",
            "category": "black",
            "year": 2023,
            "origin": "安徽祁门",
            "spec": "250g/盒",
            "price_min": 300,
            "price_max": 450,
            "intro": "世界三大高香红茶之一，有独特的祁门香（似花、似果、似蜜），汤色红艳明亮。",
            "cover_url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800",
            "status": "online",
            "weight": 50
        },
        {
            "name": "易武正山",
            "category": "pu_er",
            "year": 2018,
            "origin": "云南西双版纳",
            "spec": "357g/饼",
            "price_min": 800,
            "price_max": 1200,
            "intro": "易武茶区代表，口感柔和细腻，苦涩度低，回甘生津明显，适合陈化。",
            "cover_url": "https://images.unsplash.com/photo-1571934811356-5cc061b6821f?w=800",
            "status": "online",
            "weight": 60
        },
        {
            "name": "水仙",
            "category": "yancha",
            "year": 2020,
            "origin": "福建武夷山",
            "spec": "180g/罐",
            "price_min": 400,
            "price_max": 580,
            "intro": "武夷岩茶传统名丛，茶汤醇厚，兰花香明显，岩韵突出，叶底软亮。",
            "cover_url": "https://images.unsplash.com/photo-1558160074-4d7d8bdf4256?w=800",
            "status": "online",
            "weight": 55
        }
    ]

    # 插入数据
    for tea_data in teas_data:
        tea = Tea(**tea_data)
        db.add(tea)

    db.commit()
    print(f"✓ 成功插入 {len(teas_data)} 条茶叶数据")

    # 验证
    total = db.query(Tea).count()
    print(f"✓ 数据库当前共有 {total} 条茶叶数据")

    db.close()


if __name__ == "__main__":
    seed_teas()
    print("\n数据生成完成！")
