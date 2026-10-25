import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from django.utils.text import slugify

from store.models import (
    MainCategory, Category, SpaceTag, SizeOption, ColorOption,
    HeroSlide, Product, ProductVariant, ProductImage, DeliveryEstimate, FAQ
)
from content.models import AnnouncementBar, SocialProofItem


class Command(BaseCommand):
    help = "Seed initial store navigation, space tags, sizes, categories, and products."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting comprehensive store data seeding..."))

        base_dir = Path(settings.BASE_DIR)
        workspace_dir = base_dir.parent
        assets_dir = workspace_dir / "plantsfrontweb" / "src" / "assets"
        products_asset_dir = assets_dir / "products"
        watch_shop_dir = base_dir / "store" / "initial_watch_shop"

        media_root = Path(settings.MEDIA_ROOT)
        media_root.mkdir(parents=True, exist_ok=True)
        (media_root / "products").mkdir(parents=True, exist_ok=True)
        (media_root / "categories").mkdir(parents=True, exist_ok=True)
        (media_root / "spaces").mkdir(parents=True, exist_ok=True)
        (media_root / "hero_slides").mkdir(parents=True, exist_ok=True)

        # ─── 1. MAIN CATEGORIES ──────────────────────────────────────────────
        main_cats_data = [
            {"name": "Shop plants", "slug": "plants", "icon": "leaf", "order": 1},
            {"name": "Plant Types", "slug": "plant-types", "icon": "flower", "order": 2},
            {"name": "Plant Combos", "slug": "plant-combos", "icon": "package", "order": 3},
            {"name": "Planters", "slug": "planters", "icon": "box", "order": 4},
        ]
        main_categories = {}
        for m in main_cats_data:
            obj, _ = MainCategory.objects.update_or_create(
                slug=m["slug"],
                defaults={
                    "name": m["name"],
                    "icon": m["icon"],
                    "order": m["order"],
                    "is_active": True,
                }
            )
            main_categories[m["slug"]] = obj
            self.stdout.write(f"  [OK] MainCategory: {obj.name} ({obj.slug})")

        # ─── 2. CATEGORIES ───────────────────────────────────────────────────
        # Sub-categories under 'plants' (Shop by Type in screenshot)
        plants_types = [
            ("Air-Purifying Plants", "air-purifying-plants", 1),
            ("Best-Selling Plants", "best-selling-plants", 2),
            ("Exotic Plants", "exotic-plants", 3),
            ("Fast-Growing Plants", "fast-growing-plants", 4),
            ("Plants Favourites", "plants-favourites", 5),
        ]
        categories_dict = {}
        for name, slug, order in plants_types:
            cat, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "main_category": main_categories["plants"],
                    "name": name,
                    "order": order,
                    "is_featured": True,
                    "description": f"Explore our premium selection of {name.lower()}."
                }
            )
            categories_dict[slug] = cat

        # Sub-categories under 'plant-types'
        plant_types_data = [
            ("Indoor Plants", "indoor-plants", 1),
            ("Outdoor Plants", "outdoor-plants", 2),
            ("Flowering Plants", "flowering-plants", 3),
            ("Low Maintenance Plants", "low-maintenance-plants", 4),
            ("Succulents & Cacti", "succulents-cacti", 5),
        ]
        for name, slug, order in plant_types_data:
            cat, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "main_category": main_categories["plant-types"],
                    "name": name,
                    "order": order,
                    "is_featured": True,
                }
            )
            categories_dict[slug] = cat

        # Sub-categories under 'plant-combos'
        plant_combos_data = [
            ("Living Room Combo", "living-room-combo", 1),
            ("Work Desk Duo", "work-desk-duo", 2),
            ("Air Purifier Pack", "air-purifier-pack", 3),
            ("Beginner Friendly Set", "beginner-friendly-set", 4),
        ]
        for name, slug, order in plant_combos_data:
            cat, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "main_category": main_categories["plant-combos"],
                    "name": name,
                    "order": order,
                    "is_featured": True,
                }
            )
            categories_dict[slug] = cat

        # ─── 3. SPACE TAGS ───────────────────────────────────────────────────
        spaces_data = [
            ("Home", "home", "home", 1, "category-living.jpg"),
            ("Living Room", "living-room", "sofa", 2, "category-living.jpg"),
            ("Bedroom", "bedroom", "bed", 3, "category-bedroom.jpg"),
            ("Office", "office", "briefcase", 4, "category-office.jpg"),
            ("Balcony", "balcony", "sun", 5, "category-balcony.jpg"),
        ]
        space_tags_dict = {}
        for name, slug, icon, order, img_file in spaces_data:
            space, _ = SpaceTag.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "icon": icon,
                    "order": order,
                    "is_featured": True,
                }
            )
            img_path = assets_dir / img_file
            if img_path.is_file() and not space.image:
                dest_path = media_root / "spaces" / img_file
                shutil.copy2(img_path, dest_path)
                space.image = f"spaces/{img_file}"
                space.save()
            space_tags_dict[slug] = space
            self.stdout.write(f"  [OK] SpaceTag: {space.name}")

        # ─── 4. SIZE & COLOR OPTIONS ─────────────────────────────────────────
        sizes_data = [
            ("Small", 1, True),
            ("Medium", 2, True),
            ("Large", 3, True),
            ("Extra Large", 4, False),
        ]
        size_options = {}
        for name, order, show_nav in sizes_data:
            size_obj, _ = SizeOption.objects.update_or_create(
                name=name,
                defaults={"order": order, "show_in_navbar": show_nav}
            )
            size_options[name] = size_obj

        colors_data = [
            ("Classic Terracotta", "#C87941", 1),
            ("Matte White", "#FFFFFF", 2),
            ("Matte Black", "#1A1A1A", 3),
            ("Sage Green", "#8FAF6E", 4),
        ]
        color_options = {}
        for name, hex_code, order in colors_data:
            color_obj, _ = ColorOption.objects.update_or_create(
                name=name,
                defaults={"hex_code": hex_code, "order": order}
            )
            color_options[name] = color_obj

        # ─── 5. HERO SLIDE (NAVBAR BANNER) ───────────────────────────────────
        hero_img_src = assets_dir / "hero-living-room.jpg"
        slide, _ = HeroSlide.objects.update_or_create(
            title="Shop All Plants",
            defaults={
                "subtitle": "NATURALLY",
                "link_url": "/shop?main_category=plants",
                "order": 1,
                "is_active": True,
            }
        )
        if hero_img_src.is_file() and not slide.image:
            dest_hero = media_root / "hero_slides" / "hero-living-room.jpg"
            shutil.copy2(hero_img_src, dest_hero)
            slide.image = "hero_slides/hero-living-room.jpg"
            slide.save()
        self.stdout.write("  [OK] HeroSlide seeded")

        # ─── 6. PRODUCTS, VARIANTS & IMAGES ──────────────────────────────────
        products_catalog = [
            {
                "name": "Monstera Deliciosa",
                "slug": "monstera-deliciosa",
                "sku": "PLT-MON-001",
                "category_slug": "air-purifying-plants",
                "price": 699.00,
                "original_price": 999.00,
                "care_level": "easy",
                "sunlight": "Bright indirect light",
                "watering": "Once a week",
                "temperature": "18°C – 30°C",
                "growth_rate": "fast",
                "pet_friendly": False,
                "air_purifying": True,
                "is_best_seller": True,
                "is_trending": True,
                "is_new_arrival": False,
                "is_best_deal": True,
                "description": "The Swiss Cheese plant is a dramatic, fast-growing tropical plant famous for its iconic perforated leaves.",
                "care_instructions": "Place in bright, filtered light.\nWater when the top 2 inches of soil feel dry.\nWipe the leaves periodically with a damp cloth.\nAvoid cold drafts.",
                "what_you_get": "1 Healthy Monstera Deliciosa Plant\n1 Self-watering Nursery Pot\nDetailed Plant Care Guide",
                "image_filename": "monstera.jpg",
                "image_source": products_asset_dir / "monstera.jpg",
                "spaces": ["living-room", "office", "home"],
            },
            {
                "name": "Snake Plant (Sansevieria)",
                "slug": "snake-plant",
                "sku": "PLT-SNK-002",
                "category_slug": "best-selling-plants",
                "price": 399.00,
                "original_price": 549.00,
                "care_level": "easy",
                "sunlight": "Low to bright indirect light",
                "watering": "Every 2-3 weeks",
                "temperature": "15°C – 32°C",
                "growth_rate": "slow",
                "pet_friendly": False,
                "air_purifying": True,
                "is_best_seller": True,
                "is_trending": True,
                "is_new_arrival": False,
                "is_best_deal": True,
                "description": "Indestructible and architectural, the Snake Plant releases oxygen at night and thrives on neglect.",
                "care_instructions": "Tolerates low light but enjoys medium indirect sun.\nAllow soil to dry out completely between waterings.\nDo not overwater in winter.\nPrefers standard indoor temperatures.",
                "what_you_get": "1 Hardy Snake Plant\n1 Eco-friendly Recyclable Pot\nPlant Care Card",
                "image_filename": "snake-plant.jpg",
                "image_source": products_asset_dir / "snake-plant.jpg",
                "spaces": ["bedroom", "office", "home"],
            },
            {
                "name": "ZZ Plant (Zamioculcas)",
                "slug": "zz-plant",
                "sku": "PLT-ZZ-003",
                "category_slug": "best-selling-plants",
                "price": 449.00,
                "original_price": 649.00,
                "care_level": "easy",
                "sunlight": "Low to medium indirect light",
                "watering": "Every 2-3 weeks",
                "temperature": "18°C – 28°C",
                "growth_rate": "slow",
                "pet_friendly": False,
                "air_purifying": True,
                "is_best_seller": True,
                "is_trending": False,
                "is_new_arrival": False,
                "is_best_deal": False,
                "description": "With glossy, emerald-green wand-like leaves, the ZZ Plant is practically immortal and handles dim corners with ease.",
                "care_instructions": "Handles low light effortlessly.\nWater sparingly once the soil is bone dry.\nKeep away from prolonged direct harsh sunlight.\nWipe leaves to maintain natural high shine.",
                "what_you_get": "1 Robust ZZ Plant\n1 Premium Minimalist Planter\nCare Instructions",
                "image_filename": "zz-plant.jpg",
                "image_source": products_asset_dir / "zz-plant.jpg",
                "spaces": ["office", "bedroom", "living-room"],
            },
            {
                "name": "Golden Pothos (Money Plant)",
                "slug": "golden-pothos",
                "sku": "PLT-PTH-004",
                "category_slug": "fast-growing-plants",
                "price": 249.00,
                "original_price": 349.00,
                "care_level": "easy",
                "sunlight": "Any light condition except deep shade",
                "watering": "Once a week",
                "temperature": "15°C – 32°C",
                "growth_rate": "fast",
                "pet_friendly": False,
                "air_purifying": True,
                "is_best_seller": True,
                "is_trending": True,
                "is_new_arrival": False,
                "is_best_deal": True,
                "description": "A lush, cascading vine adorned with heart-shaped, variegated gold and green foliage that brings positivity and vitality.",
                "care_instructions": "Thrives in moderate indirect light.\nWater when the top inch of soil feels dry.\nTrim vines to encourage fuller, bushier growth.\nCan be grown trailing or climbing a moss stick.",
                "what_you_get": "1 Trailing Golden Pothos\n1 Self-Watering Hanging/Table Pot\nGrowth Guide",
                "image_filename": "pothos.jpg",
                "image_source": products_asset_dir / "pothos.jpg",
                "spaces": ["home", "office", "living-room", "balcony"],
            },
            {
                "name": "Peace Lily (Spathiphyllum)",
                "slug": "peace-lily",
                "sku": "PLT-PCE-005",
                "category_slug": "air-purifying-plants",
                "price": 499.00,
                "original_price": 699.00,
                "care_level": "easy",
                "sunlight": "Medium to low indirect light",
                "watering": "When leaves begin to droop slightly",
                "temperature": "18°C – 28°C",
                "growth_rate": "moderate",
                "pet_friendly": False,
                "air_purifying": True,
                "is_best_seller": False,
                "is_trending": True,
                "is_new_arrival": True,
                "is_best_deal": False,
                "description": "Elegant white blooms emerge above rich, deep green foliage. One of NASA's top air-filtering botanical wonders.",
                "care_instructions": "Avoid direct afternoon sun.\nKeep soil consistently moist but never waterlogged.\nMist leaves during dry summer months.\nRemove spent blooms at the base.",
                "what_you_get": "1 Flowering Peace Lily Plant\n1 Designer White Ceramic Finish Pot\nCare Guide",
                "image_filename": "peace-lily.jpg",
                "image_source": products_asset_dir / "peace-lily.jpg",
                "spaces": ["living-room", "bedroom", "office"],
            },
            {
                "name": "Areca Palm",
                "slug": "areca-palm",
                "sku": "PLT-ARC-006",
                "category_slug": "plants-favourites",
                "price": 899.00,
                "original_price": 1299.00,
                "care_level": "moderate",
                "sunlight": "Bright filtered sunlight",
                "watering": "Twice a week in summer, once a week in winter",
                "temperature": "18°C – 32°C",
                "growth_rate": "moderate",
                "pet_friendly": True,
                "air_purifying": True,
                "is_best_seller": True,
                "is_trending": True,
                "is_new_arrival": False,
                "is_best_deal": False,
                "description": "Feathery, arching palm fronds instantly transform any indoor room or living area into a tropical retreat.",
                "care_instructions": "Place near a bright window with sheer curtains.\nEnsure good drainage to prevent root rot.\nPet safe and completely non-toxic.\nFeed with mild fertilizer once a month.",
                "what_you_get": "1 Large Multi-Cane Areca Palm (2.5 - 3 ft)\n1 Heavy Duty Planter\nCare Booklet",
                "image_filename": "areca-palm.jpg",
                "image_source": products_asset_dir / "areca-palm.jpg",
                "spaces": ["living-room", "home", "balcony"],
            },
            {
                "name": "Aglaonema Suksom Jaipong",
                "slug": "aglaonema-suksom-jaipong",
                "sku": "PLT-AGL-007",
                "category_slug": "exotic-plants",
                "price": 799.00,
                "original_price": 1199.00,
                "care_level": "easy",
                "sunlight": "Bright indirect light",
                "watering": "Once every 7 to 10 days",
                "temperature": "20°C – 30°C",
                "growth_rate": "moderate",
                "pet_friendly": False,
                "air_purifying": True,
                "is_best_seller": False,
                "is_trending": True,
                "is_new_arrival": True,
                "is_best_deal": True,
                "description": "Stunning neon-red foliage edged in emerald green makes this rare collector plant an absolute showstopper.",
                "care_instructions": "Bright indirect light preserves the vibrant crimson color.\nAllow top half of soil to dry before watering.\nPrefers warm indoor temperatures.\nProtect from direct harsh rays.",
                "what_you_get": "1 Exotic Red Suksom Jaipong Plant\n1 Sleek Planter\nCollector's Certificate & Guide",
                "image_filename": "aglaonema-suksom-jaipong.jpg",
                "image_source": watch_shop_dir / "aglaonema-suksom-jaipong.jpg",
                "spaces": ["living-room", "home", "office"],
            },
            {
                "name": "Calathea Ornata",
                "slug": "calathea-ornata",
                "sku": "PLT-CAL-008",
                "category_slug": "exotic-plants",
                "price": 599.00,
                "original_price": 849.00,
                "care_level": "moderate",
                "sunlight": "Medium indirect light",
                "watering": "Keep evenly moist with distilled or RO water",
                "temperature": "18°C – 26°C",
                "growth_rate": "moderate",
                "pet_friendly": True,
                "air_purifying": True,
                "is_best_seller": False,
                "is_trending": True,
                "is_new_arrival": True,
                "is_best_deal": False,
                "description": "Also known as the Pinstripe Prayer Plant, its dark burgundy-purple backed leaves feature intricate hand-painted pink stripes.",
                "care_instructions": "Enjoys high humidity and warm corners.\nSensitive to tap water salts — use filtered or rainwater.\nLeaves fold upward at night in prayer.\nSafe for dogs and cats.",
                "what_you_get": "1 Calathea Ornata Pinstripe Plant\n1 Decorative Matte Planter\nCare Instructions",
                "image_filename": "calathea-ornata.jpg",
                "image_source": watch_shop_dir / "calathea-ornata.jpg",
                "spaces": ["bedroom", "living-room", "home"],
            },
            {
                "name": "Philodendron Moonshine",
                "slug": "philodendron-moonshine",
                "sku": "PLT-PHL-009",
                "category_slug": "plants-favourites",
                "price": 549.00,
                "original_price": 799.00,
                "care_level": "easy",
                "sunlight": "Medium to bright indirect light",
                "watering": "Once a week",
                "temperature": "18°C – 28°C",
                "growth_rate": "fast",
                "pet_friendly": False,
                "air_purifying": True,
                "is_best_seller": True,
                "is_trending": True,
                "is_new_arrival": False,
                "is_best_deal": False,
                "description": "Luminous silvery lime-green leaves that glow in the sunlight and bring a fresh botanical aesthetic to any interior.",
                "care_instructions": "Thrives in medium to bright indirect light.\nAllow top 2 inches of soil to dry between waterings.\nClean broad leaves with a damp cloth.\nFeed with diluted balanced fertilizer in spring.",
                "what_you_get": "1 Philodendron Moonshine Plant\n1 Modern Nordic Pot\nCare Guide",
                "image_filename": "philodendron-moonshine.jpg",
                "image_source": watch_shop_dir / "philodendron-moonshine.jpg",
                "spaces": ["living-room", "office", "home"],
            },
            {
                "name": "Rex Begonia",
                "slug": "rex-begonia",
                "sku": "PLT-REX-010",
                "category_slug": "exotic-plants",
                "price": 499.00,
                "original_price": 699.00,
                "care_level": "moderate",
                "sunlight": "Gentle morning sun or bright indirect light",
                "watering": "Once every 5 to 7 days",
                "temperature": "18°C – 26°C",
                "growth_rate": "moderate",
                "pet_friendly": False,
                "air_purifying": True,
                "is_best_seller": False,
                "is_trending": True,
                "is_new_arrival": True,
                "is_best_deal": True,
                "description": "Prized for its iridescent spiral leaves displaying metallic pink, silver, and deep wine-colored swirls.",
                "care_instructions": "Water at the base of the plant avoiding water on leaves.\nProvide gentle morning or dappled light.\nHigh ambient humidity prevents leaf-edge browning.\nLight, well-draining peat mix.",
                "what_you_get": "1 King Rex Begonia\n1 Terracotta Finish Planter\nCare Guide",
                "image_filename": "rex-begonia.jpg",
                "image_source": watch_shop_dir / "rex-begonia.jpg",
                "spaces": ["living-room", "bedroom", "home"],
            },
        ]

        for p_data in products_catalog:
            cat = categories_dict.get(p_data["category_slug"]) or categories_dict["air-purifying-plants"]
            prod, created = Product.objects.update_or_create(
                slug=p_data["slug"],
                defaults={
                    "name": p_data["name"],
                    "sku": p_data["sku"],
                    "category": cat,
                    "price": p_data["price"],
                    "original_price": p_data["original_price"],
                    "care_level": p_data["care_level"],
                    "sunlight": p_data["sunlight"],
                    "watering": p_data["watering"],
                    "temperature": p_data["temperature"],
                    "growth_rate": p_data["growth_rate"],
                    "pet_friendly": p_data["pet_friendly"],
                    "air_purifying": p_data["air_purifying"],
                    "is_best_seller": p_data["is_best_seller"],
                    "is_trending": p_data["is_trending"],
                    "is_new_arrival": p_data["is_new_arrival"],
                    "is_best_deal": p_data["is_best_deal"],
                    "is_active": True,
                    "description": p_data["description"],
                    "care_instructions": p_data["care_instructions"],
                    "what_you_get": p_data["what_you_get"],
                }
            )

            # Link Space Tags
            for sp_slug in p_data["spaces"]:
                if sp_slug in space_tags_dict:
                    prod.space_tags.add(space_tags_dict[sp_slug])

            # Copy Image and create ProductImage
            src_img = p_data["image_source"]
            if src_img.is_file():
                dest_img_rel = f"products/{p_data['image_filename']}"
                dest_img_abs = media_root / "products" / p_data["image_filename"]
                shutil.copy2(src_img, dest_img_abs)
                ProductImage.objects.get_or_create(
                    product=prod,
                    image=dest_img_rel,
                    defaults={
                        "is_primary": True,
                        "alt_text": prod.name,
                        "order": 1,
                    }
                )

            # Create Size and Color Variants
            # Small variant
            ProductVariant.objects.update_or_create(
                product=prod,
                size=size_options["Small"],
                color=color_options["Classic Terracotta"],
                defaults={"stock": 50, "price_override": 0.00}
            )
            # Medium variant (+150 INR)
            ProductVariant.objects.update_or_create(
                product=prod,
                size=size_options["Medium"],
                color=color_options["Matte White"],
                defaults={"stock": 40, "price_override": 150.00}
            )
            # Large variant (+350 INR)
            ProductVariant.objects.update_or_create(
                product=prod,
                size=size_options["Large"],
                color=color_options["Matte Black"],
                defaults={"stock": 25, "price_override": 350.00}
            )

            # Add Delivery Estimates
            DeliveryEstimate.objects.get_or_create(
                product=prod,
                region="Within Telangana",
                defaults={"estimate": "2-3 business days", "order": 1}
            )
            DeliveryEstimate.objects.get_or_create(
                product=prod,
                region="All Other States",
                defaults={"estimate": "4-6 business days", "order": 2}
            )

            self.stdout.write(f"  [OK] Product & Variants: {prod.name} ({prod.sku})")

        # ─── 7. CONTENT ANNOUNCEMENTS & SOCIAL PROOF ─────────────────────────
        announcements = [
            ("🌿 Free Express Shipping on orders above ₹1999", 1),
            ("✨ Buy 2 Plants @ ₹699 — Use Code: GREEN2", 2),
            ("🪴 100% Plant Replacement Guarantee on Transit Damage", 3),
        ]
        for text, order in announcements:
            AnnouncementBar.objects.get_or_create(text=text, defaults={"order": order, "is_active": True})

        social_proofs = [
            ("smile", "25,000+ Happy Plant Parents", "Delivering healthy plants across 200+ Indian cities", 1),
            ("truck", "Safe & Secure Eco-Packaging", "Custom breathable boxes keep plants fresh for up to 7 days", 2),
            ("star", "4.9★ Average Plant Rating", "Rated highest in quality and customer service across India", 3),
        ]
        for icon, title, subtitle, order in social_proofs:
            SocialProofItem.objects.get_or_create(title=title, defaults={
                "icon": icon,
                "subtitle": subtitle,
                "order": order,
                "is_active": True
            })

        # ─── 8. FAQs ─────────────────────────────────────────────────────────
        faqs = [
            (
                "How do you pack live plants for transit?",
                "We use custom-engineered, breathable eco-friendly packaging that locks the pot in place and protects delicate foliage from tipping or shifting during transit.",
                1
            ),
            (
                "What if my plant arrives wilted or damaged?",
                "We provide a 100% Transit Guarantee! If your plant suffers transit shock or arrives damaged, just message us on WhatsApp with a photo within 48 hours for a free replacement.",
                2
            ),
            (
                "Do these plants come potted with soil?",
                "Yes! All our plants arrive fully potted in nutrient-rich organic potting mix and ready to brighten up your home or office.",
                3
            ),
            (
                "How do I care for my plant once it arrives?",
                "Give your plant a gentle drink of water and place it in medium, indirect light for the first 2-3 days to let it acclimate to your home's humidity and light.",
                4
            ),
        ]
        for question, answer, order in faqs:
            FAQ.objects.get_or_create(question=question, defaults={"answer": answer, "order": order, "is_active": True})

        self.stdout.write(self.style.SUCCESS("[OK] All store categories, space tags, size tags, products, variants, and content seeded successfully!"))
