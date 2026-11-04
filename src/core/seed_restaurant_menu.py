import sqlite3
import json
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "waiter.db")

def seed_menu(conn=None):
    should_close = False
    if conn is None:
        conn = sqlite3.connect(os.path.abspath(DB_FILE))
        should_close = True
    cursor = conn.cursor()

    # Add columns if missing
    cursor.execute("PRAGMA table_info(menu_items)")
    existing_cols = [c[1] for c in cursor.fetchall()]

    new_cols = [
        ("kcal", "INTEGER DEFAULT 0"),
        ("serves", "TEXT DEFAULT ''"),
        ("is_featured", "INTEGER DEFAULT 0"),
        ("is_new", "INTEGER DEFAULT 0"),
        ("image_url", "TEXT DEFAULT ''"),
        ("modifiers_json", "TEXT DEFAULT '{}'"),
        ("price_from", "INTEGER DEFAULT 0")
    ]

    for col_name, col_type in new_cols:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE menu_items ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name}")

    # Standard Modifiers for Chicken Dishes:
    # 1. Baste / Heat levels
    standard_heats = [
        {"id": "vusa", "name": "VUSA XX Hot", "badge": "limited time", "level": 5, "kcal": 33, "color": "#800020", "desc": "Our hottest spice. Fiery, fierce and fuelled by pure chilli."},
        {"id": "extra_hot", "name": "Extra Hot", "badge": "", "level": 4, "kcal": 82, "color": "#B3001B", "desc": "A sizzling hot spice, and then some."},
        {"id": "hot", "name": "Hot", "badge": "", "level": 3, "kcal": 41, "color": "#E65100", "desc": "Tongue-tingling heat, not for the faint hearted."},
        {"id": "medium", "name": "Medium", "badge": "popular", "level": 2, "kcal": 21, "color": "#F57C00", "desc": "Heaps of flavour with just a flicker of fire."},
        {"id": "lemon_herb", "name": "Lemon & Herb", "badge": "", "level": 1, "kcal": 10, "color": "#7CB342", "desc": "Zesty and tangy. A tastebud teaser."},
        {"id": "plain", "name": "Plain...ish", "badge": "", "level": 0, "kcal": 0, "color": "#9E9E9E", "desc": "No added spice. As mild as it gets."},
        {"id": "peri_tamer", "name": "Sweet BBQ", "badge": "", "level": 0, "kcal": 40, "color": "#6A1B9A", "desc": "Deliciously sweet with a hint of smoky BBQ."}
    ]

    # 2. Meal choices
    chicken_half_meals = [
        {"id": "on_its_own", "name": "On its own", "price": 9.25, "kcal": 579, "badge": ""},
        {"id": "two_sides", "name": "+2 regular sides", "price": 15.75, "kcal": 0, "badge": "Best value", "sides_count": 2}
    ]

    chicken_butterfly_meals = [
        {"id": "on_its_own", "name": "On its own", "price": 10.25, "kcal": 332, "badge": ""},
        {"id": "two_sides", "name": "+2 regular sides", "price": 16.75, "kcal": 0, "badge": "Best value", "sides_count": 2}
    ]

    chicken_thighs_meals = [
        {"id": "on_its_own", "name": "On its own", "price": 10.25, "kcal": 706, "badge": ""},
        {"id": "two_sides", "name": "+2 regular sides", "price": 16.75, "kcal": 0, "badge": "Best value", "sides_count": 2}
    ]

    burger_sunset_meals = [
        {"id": "on_its_own", "name": "On its own", "price": 10.25, "kcal": 620, "badge": ""},
        {"id": "two_sides", "name": "+2 regular sides", "price": 16.75, "kcal": 0, "badge": "Best value", "sides_count": 2}
    ]

    # 3. Available sides for combos
    available_sides = [
        {"id": "side-peri-chips", "name": "Salted Chips", "kcal": 498, "surcharge": 0.0, "is_new": 0},
        {"id": "side-plain-chips", "name": "Classic Chips", "kcal": 496, "surcharge": 0.0, "is_new": 0},
        {"id": "side-garlic-bread", "name": "Garlic Bread", "kcal": 372, "surcharge": 0.0, "is_new": 0},
        {"id": "side-spicy-rice", "name": "Spicy Rice", "kcal": 246, "surcharge": 0.0, "is_new": 0},
        {"id": "side-coleslaw", "name": "Coleslaw", "kcal": 233, "surcharge": 0.0, "is_new": 0},
        {"id": "side-creamy-mash", "name": "Creamy Mash", "kcal": 308, "surcharge": 0.0, "is_new": 0},
        {"id": "side-corn", "name": "Corn on the Cob", "kcal": 142, "surcharge": 0.0, "is_new": 0},
        {"id": "side-broccoli", "name": "Tenderstem® Broccoli", "kcal": 32, "surcharge": 0.0, "is_new": 0},
        {"id": "side-macho-peas", "name": "Macho Peas", "kcal": 155, "surcharge": 0.0, "is_new": 0},
        {"id": "side-rainbow-slaw", "name": "Rainbow Slaw", "kcal": 132, "surcharge": 0.0, "is_new": 0},
        {"id": "side-peri-mac", "name": "Loaded Mac & Cheese", "kcal": 621, "surcharge": 2.00, "is_new": 1},
        {"id": "side-mac-cheese", "name": "Classic Mac & Cheese", "kcal": 494, "surcharge": 1.00, "is_new": 0},
        {"id": "side-charred-corn", "name": "Charred Sweetcorn", "kcal": 255, "surcharge": 0.75, "is_new": 0},
        {"id": "side-tomato-salad", "name": "Herb Tomato Salad", "kcal": 136, "surcharge": 0.75, "is_new": 0}
    ]

    standard_extras = [
        {"id": "extra-halloumi", "name": "2 Grilled Halloumi Slices", "price": 2.00, "kcal": 180},
        {"id": "extra-cheddar", "name": "Cheddar Cheese Slice", "price": 1.00, "kcal": 85},
        {"id": "extra-chilli-jam", "name": "Sweet Chilli Jam", "price": 1.25, "kcal": 45},
        {"id": "extra-garlic-perinaise", "name": "Creamy Garlic Dip", "price": 1.25, "kcal": 120}
    ]

    chicken_half_modifiers = {
        "heats": standard_heats,
        "meals": chicken_half_meals,
        "sides": available_sides,
        "extras": standard_extras
    }

    chicken_butterfly_modifiers = {
        "heats": standard_heats,
        "meals": chicken_butterfly_meals,
        "sides": available_sides,
        "extras": standard_extras
    }

    chicken_thighs_modifiers = {
        "heats": standard_heats,
        "meals": chicken_thighs_meals,
        "sides": available_sides,
        "extras": standard_extras
    }

    burger_sunset_modifiers = {
        "heats": standard_heats,
        "meals": burger_sunset_meals,
        "sides": available_sides,
        "extras": standard_extras
    }

    # Complete Restaurant Menu Dataset
    restaurant_items = [
        # STARTERS
        {
            "id": "starter-garlic-pitta",
            "name_en": "Cheesy Garlic Pitta",
            "name_fr": "Pitta à l'Ail et au Fromage",
            "name_ar": "بيتا بالثوم والجبن الذائب",
            "desc_en": "A toasted sourdough pitta oozing with melty cheddar cheese, garlic, spring onions and a hint of spice. Served with our red pepper chutney.",
            "desc_fr": "Pitta au levain toastée débordante de cheddar fondu, ail et oignons nouveaux. Servie avec chutney de poivrons.",
            "desc_ar": "بيتا العجين المخمر المحمصة المحشوة بجبنة الشيدر الذائبة والثوم والبصل الأخضر ولمسة من التوابل. تقدم مع صلصة الفلفل الأحمر.",
            "price": 5.25,
            "category": "Starters",
            "kcal": 597,
            "serves": "Serves 2",
            "is_featured": 1,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1541592106381-b31e9677c0e5?w=700&auto=format&fit=crop&q=80",
            "allergens": ["gluten", "milk"],
            "dietary": ["vegetarian"],
            "upsell_ids": ["starter-halloumi-chilli", "drink-coke"],
            "modifiers": {},
            "price_from": 0
        },
        {
            "id": "starter-chicken-chorizo",
            "name_en": "Chicken Chorizo",
            "name_fr": "Chorizo de Poulet",
            "name_ar": "شوريزو الدجاج المشوي",
            "desc_en": "Chicken chorizo slices spiced with smoked paprika and garlic, then drizzled with honey glaze. No pork. Not a sausage.",
            "desc_fr": "Tranches de chorizo de poulet épicées au paprika fumé et à l'ail, arrosées de miel épicé. Sans porc.",
            "desc_ar": "شرائح شوريزو الدجاج المتبلة بالبابريكا المدخنة والثوم ومغطاة برذاذ العسل الحار. خالية تماماً من لحم الخنزير.",
            "price": 5.25,
            "category": "Starters",
            "kcal": 340,
            "serves": "Serves 2",
            "is_featured": 0,
            "is_new": 1,
            "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=700&auto=format&fit=crop&q=80",
            "allergens": [],
            "dietary": ["halal"],
            "upsell_ids": ["starter-garlic-pitta", "drink-beer"],
            "modifiers": {},
            "price_from": 0
        },
        {
            "id": "starter-halloumi-chilli",
            "name_en": "Halloumi Sticks & Chilli Jam",
            "name_fr": "Bâtonnets d'Halloumi & Confiture de Piment",
            "name_ar": "أصابع الحلومي المشوية مع مربى الفلفل الحار",
            "desc_en": "Five chunky sticks of golden grilled halloumi with sweet chilli jam for dipping.",
            "desc_fr": "Cinq bâtonnets d'halloumi grillé doré avec confiture de piment doux.",
            "desc_ar": "خمس قطع سميكة من جبن الحلوم المشوي الذهبي تقدم مع مربى الفلفل الحلو الحار للغمس.",
            "price": 5.25,
            "category": "Starters",
            "kcal": 458,
            "serves": "Serves 2",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=700&auto=format&fit=crop&q=80",
            "allergens": ["milk"],
            "dietary": ["vegetarian"],
            "upsell_ids": ["starter-garlic-pitta", "drink-coke"],
            "modifiers": {},
            "price_from": 0
        },
        {
            "id": "starter-houmous",
            "name_en": "Houmous with Flame Drizzle",
            "name_fr": "Houmous au Filet d'Huile Épicée",
            "name_ar": "حمص ناعم مع رذاذ الزيت الحار",
            "desc_en": "Velvety houmous drizzled with infused flame chilli oil, served with warm sourdough pitta triangles.",
            "desc_fr": "Houmous onctueux arrosé d'huile infusée au piment, servi avec triangles de pitta chaude.",
            "desc_ar": "حمص كريمي ناعم مغطى برذاذ زيت الفلفل الحار المتبل، يقدم مع مثلثات خبز البيتا الدافئة.",
            "price": 5.25,
            "category": "Starters",
            "kcal": 792,
            "serves": "Serves 2-3",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=700&auto=format&fit=crop&q=80",
            "allergens": ["gluten", "sesame"],
            "dietary": ["vegan", "plant-based"],
            "upsell_ids": ["starter-spicy-olives"],
            "modifiers": {},
            "price_from": 0
        },
        {
            "id": "starter-spicy-olives",
            "name_en": "Spicy Mixed Olives",
            "name_fr": "Olives Mixtes Épicées",
            "name_ar": "زيتون مشكل متبل بالأعشاب والثوم",
            "desc_en": "Juicy pitted olives with garlic, peppers and mushrooms in herb marinade.",
            "desc_fr": "Olives dénoyautées juteuses à l'ail, poivrons et champignons marinés.",
            "desc_ar": "حبات الزيتون المشكلة المنزوعة النوى والمتبلة بالثوم والفلفل والأعشاب العطرية.",
            "price": 4.25,
            "category": "Starters",
            "kcal": 138,
            "serves": "Serves 2",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=700&auto=format&fit=crop&q=80",
            "allergens": [],
            "dietary": ["vegan", "plant-based"],
            "upsell_ids": ["drink-beer"],
            "modifiers": {},
            "price_from": 0
        },

        # FLAME-GRILLED CHICKEN
        {
            "id": "chicken-half",
            "name_en": "1/2 Chicken",
            "name_fr": "1/2 Poulet Grillé",
            "name_ar": "نصف دجاجة مشوية على اللهب",
            "desc_en": "A chicken breast and a leg, served on the bone with crispy flame-grilled skin. Flame-grilled in your favourite spice.",
            "desc_fr": "Un blanc et une cuisse de poulet sur l'os à la peau croustillante grillée à la flamme dans votre épice préférée.",
            "desc_ar": "صدر وفخذ دجاج بالعظم مع جلد مقرمش مشوي على اللهب بتتبيلتك المفضلة من مقياس الحرارة.",
            "price": 9.25,
            "category": "Flame-Grilled Chicken",
            "kcal": 579,
            "serves": "1 Diner",
            "is_featured": 1,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=700&auto=format&fit=crop&q=80",
            "allergens": [],
            "dietary": ["halal"],
            "upsell_ids": ["side-peri-chips", "drink-diet-coke"],
            "modifiers": chicken_half_modifiers,
            "price_from": 1
        },
        {
            "id": "chicken-butterfly",
            "name_en": "Chicken Butterfly",
            "name_fr": "Papillon de Poulet",
            "name_ar": "صدر دجاج فراشة مزدوج مشوي",
            "desc_en": "Two succulent chicken breasts joined by crispy flame-grilled skin, infused with your choice of heat.",
            "desc_fr": "Deux blancs de poulet tendres réunis par une peau croustillante grillée à la flamme.",
            "desc_ar": "صدرا دجاج طريان متصلان بجلد مقرمش مشوي على اللهب ومتبل حسب اختيارك.",
            "price": 10.25,
            "category": "Flame-Grilled Chicken",
            "kcal": 332,
            "serves": "1 Diner",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1532550907401-a500c9a57435?w=700&auto=format&fit=crop&q=80",
            "allergens": [],
            "dietary": ["halal"],
            "upsell_ids": ["side-spicy-rice", "drink-coke"],
            "modifiers": chicken_butterfly_modifiers,
            "price_from": 1
        },
        {
            "id": "chicken-thighs",
            "name_en": "4 Boneless Chicken Thighs",
            "name_fr": "4 Hauts de Cuisse Désossés",
            "name_ar": "٤ أفخاذ دجاج مخلية مشوية",
            "desc_en": "Flame-grilled tender boneless chicken thighs with crispy skin in your choice of spice.",
            "desc_fr": "Quatre hauts de cuisse de poulet désossés très tendres et grillés à la flamme.",
            "desc_ar": "أربعة أفخاذ دجاج طرية مخلية من العظم مشوية على اللهب مع قشرة مقرمشة وتتبيلة لذيذة.",
            "price": 10.25,
            "category": "Flame-Grilled Chicken",
            "kcal": 706,
            "serves": "1 Diner",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=700&auto=format&fit=crop&q=80",
            "allergens": [],
            "dietary": ["halal"],
            "upsell_ids": ["side-peri-chips", "drink-coke-zero"],
            "modifiers": chicken_thighs_modifiers,
            "price_from": 1
        },
        {
            "id": "chicken-whole",
            "name_en": "Whole Chicken",
            "name_fr": "Poulet Entier",
            "name_ar": "دجاجة كاملة مشوية على اللهب",
            "desc_en": "Two breasts and two legs, served on the bone and flame-grilled in your favourite spice. Ideal for sharing.",
            "desc_fr": "Deux blancs et deux cuisses servis sur l'os et grillés à la flamme. Idéal à partager.",
            "desc_ar": "دجاجة كاملة (صدران وفخذان) بالعظم مشوية على اللهب بتتبيلتك المفضلة، مثالية للمشاركة.",
            "price": 17.25,
            "category": "Flame-Grilled Chicken",
            "kcal": 1159,
            "serves": "Serves 2-3",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=700&auto=format&fit=crop&q=80",
            "allergens": [],
            "dietary": ["halal"],
            "upsell_ids": ["side-garlic-bread", "side-spicy-rice"],
            "modifiers": chicken_half_modifiers,
            "price_from": 0
        },
        {
            "id": "chicken-wings-10",
            "name_en": "10 Flame-Grilled Wings",
            "name_fr": "10 Ailes de Poulet Grillées",
            "name_ar": "١٠ أجنحة دجاج مشوية على اللهب",
            "desc_en": "Ten juicy chicken wings, flame-grilled in your favourite spice. Perfect for sharing.",
            "desc_fr": "Dix ailes de poulet juteuses grillées à la flamme selon votre niveau de piquant.",
            "desc_ar": "عشرة أجنحة دجاج طرية وغنية بالنكهة مشوية على اللهب بتتبيلتك المختارة.",
            "price": 13.00,
            "category": "Flame-Grilled Chicken",
            "kcal": 786,
            "serves": "Serves 2",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1567620832903-9fc6debc209f?w=700&auto=format&fit=crop&q=80",
            "allergens": [],
            "dietary": ["halal"],
            "upsell_ids": ["side-peri-chips", "drink-beer"],
            "modifiers": chicken_half_modifiers,
            "price_from": 1
        },

        # BURGERS, PITTAS & WRAPS
        {
            "id": "burger-sunset",
            "name_en": "The Sunset Burger",
            "name_fr": "Le Burger Sunset",
            "name_ar": "برجر صنسيت الذهبي",
            "desc_en": "Two chicken thighs, melting cheddar cheese, smoky red pepper chutney and fresh baby spinach in a soft bolo do caco bun.",
            "desc_fr": "Deux hauts de cuisse de poulet, cheddar fondant, chutney de poivron fumé et pousses d'épinards dans un pain moelleux.",
            "desc_ar": "فخذا دجاج مشويان مع جبنة شيدر ذائبة وصلصة فلفل أحمر مدخنة وأوراق سبانخ طازجة في خبز البولو الناعم.",
            "price": 10.25,
            "category": "Burgers, Pittas, Wraps",
            "kcal": 620,
            "serves": "1 Diner",
            "is_featured": 1,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=700&auto=format&fit=crop&q=80",
            "allergens": ["gluten", "milk"],
            "dietary": ["halal"],
            "upsell_ids": ["side-peri-chips", "drink-diet-coke"],
            "modifiers": burger_sunset_modifiers,
            "price_from": 1
        },
        {
            "id": "burger-chicken",
            "name_en": "Flame-Grilled Chicken Burger",
            "name_fr": "Burger Poulet Grillé Classique",
            "name_ar": "برجر الدجاج المشوي الكلاسيكي",
            "desc_en": "Tender chicken breast, crisp lettuce, tomato and light mayo in a toasted brioche bun.",
            "desc_fr": "Blanc de poulet tendre, salade croquante, tomate et mayonnaise légère dans un pain brioché.",
            "desc_ar": "صدر دجاج طري مع خس مقرمش وطماطم ومايونيز خفيف في خبز بريوش محمص.",
            "price": 8.75,
            "category": "Burgers, Pittas, Wraps",
            "kcal": 412,
            "serves": "1 Diner",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=700&auto=format&fit=crop&q=80",
            "allergens": ["gluten", "eggs"],
            "dietary": ["halal"],
            "upsell_ids": ["side-peri-chips", "drink-coke"],
            "modifiers": burger_sunset_modifiers,
            "price_from": 1
        },
        {
            "id": "pitta-chicken",
            "name_en": "Flame-Grilled Chicken Pitta",
            "name_fr": "Pitta Poulet Grillé",
            "name_ar": "بيتا الدجاج المشوي مع السلطة",
            "desc_en": "Flame-grilled chicken breast tucked into a toasted sourdough pitta with crunchy slaw.",
            "desc_fr": "Blanc de poulet grillé dans une pitta au levain toastée avec salade croquante.",
            "desc_ar": "قطع صدور دجاج مشوية على اللهب محشوة في خبز بيتا محمص مع سلطة كولسلو المقرمشة.",
            "price": 8.75,
            "category": "Burgers, Pittas, Wraps",
            "kcal": 430,
            "serves": "1 Diner",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1529042410759-befb1204b468?w=700&auto=format&fit=crop&q=80",
            "allergens": ["gluten"],
            "dietary": ["halal"],
            "upsell_ids": ["side-peri-chips", "drink-coke-zero"],
            "modifiers": burger_sunset_modifiers,
            "price_from": 1
        },

        # SIDES
        {
            "id": "side-peri-chips",
            "name_en": "Salted Chips",
            "name_fr": "Frites Assaisonnées",
            "name_ar": "بطاطس مقلية متبلة ومملحة",
            "desc_en": "Crispy golden skin-on potato chips tossed in our signature aromatic spice seasoning.",
            "desc_fr": "Frites dorées croustillantes avec la peau, enrobées de notre sel aromatique.",
            "desc_ar": "بطاطس ذهبية مقرمشة بقشرتها ومتبلة بملح الأعشاب الخاص.",
            "price": 3.75,
            "category": "Sides",
            "kcal": 498,
            "serves": "1 Side",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1576107232684-1279f3908594?w=700&auto=format&fit=crop&q=80",
            "allergens": [],
            "dietary": ["vegan", "plant-based"],
            "upsell_ids": ["extra-garlic-perinaise"],
            "modifiers": {},
            "price_from": 0
        },
        {
            "id": "side-spicy-rice",
            "name_en": "Spicy Rice",
            "name_fr": "Riz Épicé",
            "name_ar": "أرز حار متبل بالأعشاب والفلفل",
            "desc_en": "Fluffy long-grain rice infused with red pepper, garlic, onion and herbs with a hint of spice.",
            "desc_fr": "Riz blanc parfumé infusé aux poivrons, oignons, ail et herbes aromatiques.",
            "desc_ar": "أرز حبة طويلة مطبوخ مع الفلفل الأحمر والثوم والأعشاب ونكهة التوابل اللذيذة.",
            "price": 3.75,
            "category": "Sides",
            "kcal": 246,
            "serves": "1 Side",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=700&auto=format&fit=crop&q=80",
            "allergens": [],
            "dietary": ["vegan", "plant-based"],
            "upsell_ids": [],
            "modifiers": {},
            "price_from": 0
        },
        {
            "id": "side-garlic-bread",
            "name_en": "Garlic Bread",
            "name_fr": "Pain à l'Ail Grillé",
            "name_ar": "خبز الثوم المشوي الذهبي",
            "desc_en": "Warm toasted sourdough baguette infused with garlic butter and fresh parsley.",
            "desc_fr": "Baguette au levain croustillante garnie de beurre d'ail et persil frais.",
            "desc_ar": "خبز العجين المخمر المحمص بالزبدة والثوم والبقدونس الطازج.",
            "price": 3.75,
            "category": "Sides",
            "kcal": 372,
            "serves": "1 Side",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1619535860434-ba1d8fa12536?w=700&auto=format&fit=crop&q=80",
            "allergens": ["gluten", "milk"],
            "dietary": ["vegetarian"],
            "upsell_ids": [],
            "modifiers": {},
            "price_from": 0
        },
        {
            "id": "side-macho-peas",
            "name_en": "Macho Peas",
            "name_fr": "Petits Pois Macho",
            "name_ar": "بسلة ماتشو بالنعناع والفلفل",
            "desc_en": "Whole and crushed sweet green peas seasoned with fresh mint, parsley and chilli.",
            "desc_fr": "Petits pois entiers et concassés assaisonnés de menthe, persil et piment doux.",
            "desc_ar": "حبات البازلاء الحلوة المهروسة مع النعناع الطازج والبقدونس ولمسة من الفلفل.",
            "price": 3.75,
            "category": "Sides",
            "kcal": 155,
            "serves": "1 Side",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=700&auto=format&fit=crop&q=80",
            "allergens": [],
            "dietary": ["vegan", "plant-based"],
            "upsell_ids": [],
            "modifiers": {},
            "price_from": 0
        },
        {
            "id": "side-peri-mac",
            "name_en": "Loaded Mac & Cheese",
            "name_fr": "Mac & Cheese Gourmand",
            "name_ar": "معكرونة بالجبنة الغنية المقرمشة",
            "desc_en": "Creamy macaroni pasta baked in a rich cheddar and red leicester cheese sauce, topped with garlic breadcrumbs.",
            "desc_fr": "Macaronis crémeux cuits au four dans une sauce cheddar onctueuse et chapelure à l'ail.",
            "desc_ar": "مكرونة ماك آند تشيز بجبنة الشيدر الذائبة ومغطاة بفتات الخبز المقرمش بالثوم.",
            "price": 5.75,
            "category": "Sides",
            "kcal": 621,
            "serves": "1 Side",
            "is_featured": 0,
            "is_new": 1,
            "image_url": "https://images.unsplash.com/photo-1543339308-43e59d6b73a6?w=700&auto=format&fit=crop&q=80",
            "allergens": ["gluten", "milk"],
            "dietary": ["vegetarian"],
            "upsell_ids": [],
            "modifiers": {},
            "price_from": 0
        },

        # DRINKS
        {
            "id": "drink-diet-coke",
            "name_en": "Bottomless Diet Coke",
            "name_fr": "Diet Coke à Volonté",
            "name_ar": "دايت كوك بإعادة ملء غير محدودة",
            "desc_en": "Free refills all meal long from our digital bottomless soda fountain.",
            "desc_fr": "Recharges gratuites et illimitées à la fontaine à boissons.",
            "desc_ar": "إعادة ملء مجانية غير محدودة طوال وجبتك من نافورة المشروبات المنعشة.",
            "price": 4.25,
            "category": "Drinks",
            "kcal": 1,
            "serves": "Bottomless Refill",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=700&auto=format&fit=crop&q=80",
            "allergens": [],
            "dietary": ["vegan", "plant-based"],
            "upsell_ids": [],
            "modifiers": {},
            "price_from": 0
        },
        {
            "id": "drink-coke",
            "name_en": "Coca-Cola Classic",
            "name_fr": "Coca-Cola Original",
            "name_ar": "كوكاكولا كلاسيك زجاجة باردة",
            "desc_en": "Original classic Coca-Cola glass bottle served ice cold with fresh lemon slice.",
            "desc_fr": "Bouteille de Coca-Cola classique servie bien fraîche avec tranche de citron.",
            "desc_ar": "زجاجة كوكاكولا كلاسيكية مثلجة تقدم مع شريحة ليمون طازجة.",
            "price": 4.25,
            "category": "Drinks",
            "kcal": 126,
            "serves": "330ml Glass Bottle",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=700&auto=format&fit=crop&q=80",
            "allergens": [],
            "dietary": ["vegan", "plant-based"],
            "upsell_ids": [],
            "modifiers": {},
            "price_from": 0
        },
        {
            "id": "drink-beer",
            "name_en": "Craft Golden Lager Pint",
            "name_fr": "Pinte de Blonde Artisanale",
            "name_ar": "بيرة لاجر ذهبية حرفية باردة",
            "desc_en": "Refreshing crisp draught golden lager. Challenge 25 policy applies — ID may be checked on table delivery.",
            "desc_fr": "Bière blonde pression rafraîchissante. Politique Challenge 25 appliquée.",
            "desc_ar": "بيرة لاجر ذهبية منعشة ومبردة. تطبق سياسة Challenge 25 للتحقق من السن القانوني.",
            "price": 6.20,
            "category": "Drinks",
            "kcal": 210,
            "serves": "Pint (568ml)",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1608270586620-248524c67de9?w=700&auto=format&fit=crop&q=80",
            "allergens": ["gluten"],
            "dietary": ["vegan"],
            "upsell_ids": [],
            "modifiers": {},
            "price_from": 0
        },

        # DESSERTS
        {
            "id": "dessert-natas",
            "name_en": "Portuguese Custard Nata",
            "name_fr": "Pastel de Nata Portugais",
            "name_ar": "تارت الكاسترد البرتغالي الشهير",
            "desc_en": "Warm crisp flaky puff pastry filled with creamy rich vanilla custard, lightly dusted with cinnamon.",
            "desc_fr": "Tartelette feuilletée croustillante garnie d'une crème à la vanille dorée et cannelle.",
            "desc_ar": "عجينة البف باستري المقرمشة المحشوة بكريمة الكاسترد الغنية مع رشة قرفة ناعمة.",
            "price": 2.60,
            "category": "Desserts",
            "kcal": 168,
            "serves": "1 Tart",
            "is_featured": 1,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=700&auto=format&fit=crop&q=80",
            "allergens": ["gluten", "milk", "eggs"],
            "dietary": ["vegetarian"],
            "upsell_ids": [],
            "modifiers": {},
            "price_from": 0
        },
        {
            "id": "dessert-choc-cake",
            "name_en": "Gooey Chocolate Cake",
            "name_fr": "Gâteau Fondant au Chocolat",
            "name_ar": "كعكة الشوكولاتة الدافئة الذائبة",
            "desc_en": "Warm molten chocolate cake with a melting heart, served with a scoop of double vanilla ice cream.",
            "desc_fr": "Gâteau moelleux au cœur de chocolat fondant, servi avec une boule de glace vanille.",
            "desc_ar": "كعكة شوكولاتة دافئة بقلب شوكولاتة ذائبة تقدم مع كرة آيس كريم فانيليا غنية.",
            "price": 5.75,
            "category": "Desserts",
            "kcal": 480,
            "serves": "1 Dessert",
            "is_featured": 0,
            "is_new": 0,
            "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=700&auto=format&fit=crop&q=80",
            "allergens": ["gluten", "milk", "eggs"],
            "dietary": ["vegetarian"],
            "upsell_ids": [],
            "modifiers": {},
            "price_from": 0
        }
    ]

    # Delete existing test items and reinsert cleanly
    for item in restaurant_items:
        cursor.execute("""
            INSERT OR REPLACE INTO menu_items (
                id, name_en, name_fr, name_ar,
                desc_en, desc_fr, desc_ar,
                price, category, upsell_ids, stock_qty,
                allergens_json, dietary_json,
                kcal, serves, is_featured, is_new, image_url, modifiers_json, price_from
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["id"],
            item["name_en"], item["name_fr"], item["name_ar"],
            item["desc_en"], item["desc_fr"], item["desc_ar"],
            item["price"], item["category"],
            json.dumps(item["upsell_ids"]), 50,
            json.dumps(item["allergens"]), json.dumps(item["dietary"]),
            item["kcal"], item["serves"], item["is_featured"], item["is_new"],
            item["image_url"], json.dumps(item["modifiers"]), item["price_from"]
        ))

    conn.commit()
    if should_close:
        conn.close()
    print(f"Successfully seeded {len(restaurant_items)} authentic Restaurant items into database!")

if __name__ == "__main__":
    seed_menu()
