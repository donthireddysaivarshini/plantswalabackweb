import os
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from store.models import (
    MainCategory, Category, SpaceTag, SizeOption, ColorOption,
    Brand, HeroSlide, Product, ProductVariant, ProductImage,
    DeliveryEstimate, SiteConfig, Coupon
)
from content.models import AnnouncementBar, SocialProofItem


class Command(BaseCommand):
    help = "Seed store database with complete navigation, categories, sizes, spaces, and products matching Rastlina"

    def handle(self, *args, **options):
        self.stdout.write("Starting store data seeding...")

        with transaction.atomic():
            # 1. Main Categories (Navbar top level)
            main_plants, _ = MainCategory.objects.update_or_create(
                slug='plants',
                defaults={'name': 'Shop plants', 'icon': 'leaf', 'order': 1, 'is_active': True}
            )
            main_types, _ = MainCategory.objects.update_or_create(
                slug='plant-types',
                defaults={'name': 'Plant Types', 'icon': 'flower', 'order': 2, 'is_active': True}
            )
            main_combos, _ = MainCategory.objects.update_or_create(
                slug='plant-combos',
                defaults={'name': 'Plant Combos', 'icon': 'package', 'order': 3, 'is_active': True}
            )
            # Only keep these 3 active in navbar as shown on Rastlina
            MainCategory.objects.exclude(slug__in=['plants', 'plant-types', 'plant-combos']).update(is_active=False)

            # 2. Categories under Main Categories
            # Under Shop plants (Shop by Type in megamenu)
            plants_categories_data = [
                ('Air-Purifying Plants', 'air-purifying-plants', 'categories/air-purifying.jpg', 1),
                ('Best-Selling Plants', 'best-selling-plants', 'categories/best-selling.jpg', 2),
                ('Exotic Plants', 'exotic-plants', 'categories/exotic.jpg', 3),
                ('Fast-Growing Plants', 'fast-growing-plants', 'categories/fast-growing.jpg', 4),
                ('Plants Wala Favourites', 'plants-wala-favourites', 'categories/favourites.jpg', 5),
            ]
            cats_dict = {}
            for name, slug, img, ord_val in plants_categories_data:
                cat, _ = Category.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'name': name,
                        'main_category': main_plants,
                        'image': img,
                        'order': ord_val,
                        'is_featured': True
                    }
                )
                cats_dict[slug] = cat

            # Under Plant Types
            types_categories_data = [
                ('Indoor Plants', 'indoor-plants', 'categories/indoor.jpg', 1),
                ('Outdoor Plants', 'outdoor-plants', 'categories/outdoor.jpg', 2),
                ('Flowering Plants', 'flowering-plants', 'categories/flowering.jpg', 3),
                ('Succulents & Cacti', 'succulents-cacti', '', 4),
                ('Low Maintenance Plants', 'low-maintenance-plants', '', 5),
            ]
            for name, slug, img, ord_val in types_categories_data:
                cat, _ = Category.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'name': name,
                        'main_category': main_types,
                        'image': img if img else None,
                        'order': ord_val,
                        'is_featured': True
                    }
                )
                cats_dict[slug] = cat

            # Under Plant Combos
            combos_categories_data = [
                ('Home Starter Pack', 'home-starter-pack', 'categories/combos.jpg', 1),
                ('Air Purifier Bundle', 'air-purifier-bundle', '', 2),
                ('Desk & Table Combos', 'desk-table-combos', '', 3),
                ('Gift Plant Combos', 'gift-plant-combos', '', 4),
            ]
            for name, slug, img, ord_val in combos_categories_data:
                cat, _ = Category.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'name': name,
                        'main_category': main_combos,
                        'image': img if img else None,
                        'order': ord_val,
                        'is_featured': True
                    }
                )
                cats_dict[slug] = cat

            # 3. Space Tags (Shop by Space in megamenu)
            spaces_data = [
                ('Home', 'home', 'home', 'spaces/category-living.jpg', 1, True),
                ('Living Room', 'living-room', 'sofa', 'spaces/category-living.jpg', 2, True),
                ('Bedroom', 'bedroom', 'bed', 'spaces/category-bedroom.jpg', 3, True),
                ('Office', 'office', 'briefcase', 'spaces/category-office.jpg', 4, True),
                ('Balcony', 'balcony', 'sun', 'spaces/category-balcony.jpg', 5, False),
            ]
            spaces_dict = {}
            for name, slug, icon, img, ord_val, is_feat in spaces_data:
                space, _ = SpaceTag.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'name': name,
                        'icon': icon,
                        'image': img,
                        'order': ord_val,
                        'is_featured': is_feat
                    }
                )
                spaces_dict[slug] = space

            # 4. Size Options (Shop by Size in megamenu)
            # Rastlina navbar specifically highlights 'Small' plants + 'All Plants'
            sizes_data = [
                ('Small', 1, True),
                ('Medium', 2, False),
                ('Large', 3, False),
                ('Extra Large', 4, False),
            ]
            sizes_dict = {}
            for name, ord_val, show_nav in sizes_data:
                sz, _ = SizeOption.objects.update_or_create(
                    name=name,
                    defaults={'order': ord_val, 'show_in_navbar': show_nav}
                )
                sizes_dict[name] = sz

            # 5. Color Options
            colors_data = [
                ('Terracotta', '#C87941', 1),
                ('Sage Green', '#8FAF6E', 2),
                ('Matte Black', '#1A1A1A', 3),
                ('Ivory White', '#F5F5F0', 4),
            ]
            colors_dict = {}
            for name, hex_code, ord_val in colors_data:
                col, _ = ColorOption.objects.update_or_create(
                    name=name,
                    defaults={'hex_code': hex_code, 'order': ord_val}
                )
                colors_dict[name] = col

            # 6. Brand
            brand, _ = Brand.objects.update_or_create(
                slug='plants-wala',
                defaults={'name': 'Plants Wala'}
            )

            # 7. Hero Slide (Banner inside Shop Plants Mega Menu)
            HeroSlide.objects.update_or_create(
                order=1,
                defaults={
                    'title': 'Shop All Plants',
                    'subtitle': 'Naturally',
                    'image': 'hero_slides/hero-living-room.jpg',
                    'link_url': '/shop?main_category=plants',
                    'is_active': True
                }
            )

            # 8. Products with Variants, Space Tags, and Images
            products_data = [
                {
                    'sku': 'PLT-MON-001',
                    'name': 'Monstera Deliciosa (Swiss Cheese Plant)',
                    'slug': 'monstera-deliciosa',
                    'category': cats_dict['air-purifying-plants'],
                    'price': Decimal('699.00'),
                    'original_price': Decimal('899.00'),
                    'care_level': 'easy',
                    'sunlight': 'Bright indirect light',
                    'watering': 'Once a week when top soil is dry',
                    'temperature': '18°C – 30°C',
                    'growth_rate': 'fast',
                    'pet_friendly': False,
                    'air_purifying': True,
                    'is_best_seller': True,
                    'is_trending': True,
                    'is_new_arrival': False,
                    'is_best_deal': False,
                    'image': 'products/monstera.jpg',
                    'spaces': [spaces_dict['living-room'], spaces_dict['home'], spaces_dict['office']],
                    'variants': [
                        (sizes_dict['Small'], colors_dict['Terracotta'], 20, Decimal('0.00')),
                        (sizes_dict['Medium'], colors_dict['Sage Green'], 15, Decimal('200.00')),
                        (sizes_dict['Large'], colors_dict['Matte Black'], 8, Decimal('500.00')),
                    ],
                },
                {
                    'sku': 'PLT-SNK-002',
                    'name': 'Snake Plant (Sansevieria Laurentii)',
                    'slug': 'snake-plant',
                    'category': cats_dict['air-purifying-plants'],
                    'price': Decimal('499.00'),
                    'original_price': Decimal('649.00'),
                    'care_level': 'easy',
                    'sunlight': 'Low to bright indirect light',
                    'watering': 'Every 2-3 weeks',
                    'temperature': '15°C – 32°C',
                    'growth_rate': 'moderate',
                    'pet_friendly': False,
                    'air_purifying': True,
                    'is_best_seller': True,
                    'is_trending': False,
                    'is_new_arrival': True,
                    'is_best_deal': False,
                    'image': 'products/snake-plant.jpg',
                    'spaces': [spaces_dict['bedroom'], spaces_dict['office'], spaces_dict['home']],
                    'variants': [
                        (sizes_dict['Small'], colors_dict['Matte Black'], 25, Decimal('0.00')),
                        (sizes_dict['Medium'], colors_dict['Ivory White'], 15, Decimal('150.00')),
                    ],
                },
                {
                    'sku': 'PLT-ARC-003',
                    'name': 'Areca Palm',
                    'slug': 'areca-palm',
                    'category': cats_dict['best-selling-plants'],
                    'price': Decimal('799.00'),
                    'original_price': Decimal('999.00'),
                    'care_level': 'easy',
                    'sunlight': 'Bright filtered light',
                    'watering': 'Twice a week',
                    'temperature': '18°C – 30°C',
                    'growth_rate': 'moderate',
                    'pet_friendly': True,
                    'air_purifying': True,
                    'is_best_seller': True,
                    'is_trending': True,
                    'is_new_arrival': False,
                    'is_best_deal': False,
                    'image': 'products/areca-palm.jpg',
                    'spaces': [spaces_dict['living-room'], spaces_dict['office'], spaces_dict['balcony']],
                    'variants': [
                        (sizes_dict['Medium'], colors_dict['Terracotta'], 12, Decimal('0.00')),
                        (sizes_dict['Large'], colors_dict['Ivory White'], 10, Decimal('350.00')),
                    ],
                },
                {
                    'sku': 'PLT-ZZP-004',
                    'name': 'ZZ Plant (Zamioculcas Zamiifolia)',
                    'slug': 'zz-plant',
                    'category': cats_dict['fast-growing-plants'],
                    'price': Decimal('549.00'),
                    'original_price': Decimal('699.00'),
                    'care_level': 'easy',
                    'sunlight': 'Low to medium light',
                    'watering': 'Once every 2 weeks',
                    'temperature': '16°C – 32°C',
                    'growth_rate': 'slow',
                    'pet_friendly': False,
                    'air_purifying': True,
                    'is_best_seller': False,
                    'is_trending': False,
                    'is_new_arrival': True,
                    'is_best_deal': True,
                    'image': 'products/zz-plant.jpg',
                    'spaces': [spaces_dict['bedroom'], spaces_dict['living-room'], spaces_dict['office']],
                    'variants': [
                        (sizes_dict['Small'], colors_dict['Matte Black'], 18, Decimal('0.00')),
                        (sizes_dict['Medium'], colors_dict['Sage Green'], 12, Decimal('150.00')),
                    ],
                },
                {
                    'sku': 'PLT-PCL-005',
                    'name': 'Peace Lily (Spathiphyllum)',
                    'slug': 'peace-lily',
                    'category': cats_dict['exotic-plants'],
                    'price': Decimal('599.00'),
                    'original_price': Decimal('749.00'),
                    'care_level': 'moderate',
                    'sunlight': 'Medium indirect light',
                    'watering': 'Once a week when leaves slightly droop',
                    'temperature': '18°C – 28°C',
                    'growth_rate': 'moderate',
                    'pet_friendly': False,
                    'air_purifying': True,
                    'is_best_seller': False,
                    'is_trending': True,
                    'is_new_arrival': False,
                    'is_best_deal': False,
                    'image': 'products/peace-lily.jpg',
                    'spaces': [spaces_dict['bedroom'], spaces_dict['living-room'], spaces_dict['home']],
                    'variants': [
                        (sizes_dict['Small'], colors_dict['Ivory White'], 20, Decimal('0.00')),
                        (sizes_dict['Medium'], colors_dict['Sage Green'], 10, Decimal('150.00')),
                    ],
                },
                {
                    'sku': 'PLT-PTH-006',
                    'name': 'Golden Pothos (Money Plant)',
                    'slug': 'golden-pothos',
                    'category': cats_dict['fast-growing-plants'],
                    'price': Decimal('349.00'),
                    'original_price': Decimal('449.00'),
                    'care_level': 'easy',
                    'sunlight': 'Any light from low to bright',
                    'watering': 'Weekly once',
                    'temperature': '15°C – 30°C',
                    'growth_rate': 'fast',
                    'pet_friendly': False,
                    'air_purifying': True,
                    'is_best_seller': True,
                    'is_trending': False,
                    'is_new_arrival': False,
                    'is_best_deal': True,
                    'image': 'products/pothos.jpg',
                    'spaces': [spaces_dict['home'], spaces_dict['office'], spaces_dict['living-room'], spaces_dict['balcony']],
                    'variants': [
                        (sizes_dict['Small'], colors_dict['Terracotta'], 30, Decimal('0.00')),
                        (sizes_dict['Medium'], colors_dict['Ivory White'], 20, Decimal('100.00')),
                    ],
                },
                {
                    'sku': 'PLT-CAL-007',
                    'name': 'Calathea Ornata (Pinstripe Plant)',
                    'slug': 'calathea-ornata',
                    'category': cats_dict['exotic-plants'],
                    'price': Decimal('649.00'),
                    'original_price': Decimal('799.00'),
                    'care_level': 'expert',
                    'sunlight': 'Medium indirect light',
                    'watering': 'Keep soil consistently moist',
                    'temperature': '18°C – 26°C',
                    'growth_rate': 'moderate',
                    'pet_friendly': True,
                    'air_purifying': True,
                    'is_best_seller': False,
                    'is_trending': True,
                    'is_new_arrival': True,
                    'is_best_deal': False,
                    'image': 'products/calathea-ornata.jpg',
                    'spaces': [spaces_dict['living-room'], spaces_dict['bedroom']],
                    'variants': [
                        (sizes_dict['Small'], colors_dict['Sage Green'], 15, Decimal('0.00')),
                        (sizes_dict['Medium'], colors_dict['Matte Black'], 10, Decimal('150.00')),
                    ],
                },
                {
                    'sku': 'PLT-AGL-008',
                    'name': 'Aglaonema Suksom Jaipong (Red Chinese Evergreen)',
                    'slug': 'aglaonema-suksom-jaipong',
                    'category': cats_dict['plants-wala-favourites'],
                    'price': Decimal('899.00'),
                    'original_price': Decimal('1199.00'),
                    'care_level': 'easy',
                    'sunlight': 'Moderate to bright indirect light',
                    'watering': 'Once a week',
                    'temperature': '18°C – 30°C',
                    'growth_rate': 'slow',
                    'pet_friendly': False,
                    'air_purifying': True,
                    'is_best_seller': False,
                    'is_trending': True,
                    'is_new_arrival': False,
                    'is_best_deal': False,
                    'image': 'products/aglaonema-suksom-jaipong.jpg',
                    'spaces': [spaces_dict['living-room'], spaces_dict['office']],
                    'variants': [
                        (sizes_dict['Small'], colors_dict['Ivory White'], 12, Decimal('0.00')),
                        (sizes_dict['Medium'], colors_dict['Terracotta'], 8, Decimal('200.00')),
                    ],
                },
                {
                    'sku': 'PLT-PHL-009',
                    'name': 'Philodendron Moonshine',
                    'slug': 'philodendron-moonshine',
                    'category': cats_dict['plants-wala-favourites'],
                    'price': Decimal('699.00'),
                    'original_price': Decimal('899.00'),
                    'care_level': 'easy',
                    'sunlight': 'Bright indirect light',
                    'watering': 'Allow top half of soil to dry',
                    'temperature': '18°C – 28°C',
                    'growth_rate': 'moderate',
                    'pet_friendly': False,
                    'air_purifying': True,
                    'is_best_seller': True,
                    'is_trending': False,
                    'is_new_arrival': False,
                    'is_best_deal': False,
                    'image': 'products/philodendron-moonshine.jpg',
                    'spaces': [spaces_dict['office'], spaces_dict['living-room']],
                    'variants': [
                        (sizes_dict['Small'], colors_dict['Matte Black'], 14, Decimal('0.00')),
                        (sizes_dict['Medium'], colors_dict['Sage Green'], 10, Decimal('180.00')),
                    ],
                },
                {
                    'sku': 'PLT-REX-010',
                    'name': 'Rex Begonia (Painted-Leaf Begonia)',
                    'slug': 'rex-begonia',
                    'category': cats_dict['exotic-plants'],
                    'price': Decimal('599.00'),
                    'original_price': Decimal('799.00'),
                    'care_level': 'moderate',
                    'sunlight': 'Bright indirect light, no direct sun',
                    'watering': 'Water when soil feels dry to touch',
                    'temperature': '16°C – 26°C',
                    'growth_rate': 'moderate',
                    'pet_friendly': False,
                    'air_purifying': True,
                    'is_best_seller': False,
                    'is_trending': False,
                    'is_new_arrival': True,
                    'is_best_deal': True,
                    'image': 'products/rex-begonia.jpg',
                    'spaces': [spaces_dict['living-room'], spaces_dict['home']],
                    'variants': [
                        (sizes_dict['Small'], colors_dict['Terracotta'], 16, Decimal('0.00')),
                    ],
                },
            ]

            for pdata in products_data:
                product = Product.objects.filter(slug=pdata['slug']).first() or Product.objects.filter(sku=pdata['sku']).first()
                if product:
                    product.name = pdata['name']
                    product.slug = pdata['slug']
                    product.sku = pdata['sku']
                    product.category = pdata['category']
                    product.brand = brand
                    product.price = pdata['price']
                    product.original_price = pdata['original_price']
                    product.care_level = pdata['care_level']
                    product.sunlight = pdata['sunlight']
                    product.watering = pdata['watering']
                    product.temperature = pdata['temperature']
                    product.growth_rate = pdata['growth_rate']
                    product.pet_friendly = pdata['pet_friendly']
                    product.air_purifying = pdata['air_purifying']
                    product.is_best_seller = pdata['is_best_seller']
                    product.is_trending = pdata['is_trending']
                    product.is_new_arrival = pdata['is_new_arrival']
                    product.is_best_deal = pdata['is_best_deal']
                    product.description = f"Premium quality {pdata['name']} curated specially for your living and working spaces."
                    product.care_instructions = f"• Light: {pdata['sunlight']}\n• Watering: {pdata['watering']}\n• Temperature: {pdata['temperature']}\n• Feed organic fertilizer once a month."
                    product.what_you_get = "• 1 Healthy live potted plant\n• Premium ceramic/nursery pot\n• Detailed plant care card\n• Guaranteed safe eco-packaging"
                    product.is_active = True
                    product.save()
                else:
                    product = Product.objects.create(
                        name=pdata['name'],
                        slug=pdata['slug'],
                        sku=pdata['sku'],
                        category=pdata['category'],
                        brand=brand,
                        price=pdata['price'],
                        original_price=pdata['original_price'],
                        care_level=pdata['care_level'],
                        sunlight=pdata['sunlight'],
                        watering=pdata['watering'],
                        temperature=pdata['temperature'],
                        growth_rate=pdata['growth_rate'],
                        pet_friendly=pdata['pet_friendly'],
                        air_purifying=pdata['air_purifying'],
                        is_best_seller=pdata['is_best_seller'],
                        is_trending=pdata['is_trending'],
                        is_new_arrival=pdata['is_new_arrival'],
                        is_best_deal=pdata['is_best_deal'],
                        description=f"Premium quality {pdata['name']} curated specially for your living and working spaces.",
                        care_instructions=f"• Light: {pdata['sunlight']}\n• Watering: {pdata['watering']}\n• Temperature: {pdata['temperature']}\n• Feed organic fertilizer once a month.",
                        what_you_get="• 1 Healthy live potted plant\n• Premium ceramic/nursery pot\n• Detailed plant care card\n• Guaranteed safe eco-packaging",
                        is_active=True,
                    )

                # Set ManyToMany Space Tags
                product.space_tags.set(pdata['spaces'])

                # Primary Image
                img_obj = ProductImage.objects.filter(product=product, is_primary=True).first()
                if img_obj:
                    img_obj.image = pdata['image']
                    img_obj.alt_text = pdata['name']
                    img_obj.order = 1
                    img_obj.save()
                else:
                    ProductImage.objects.create(
                        product=product,
                        is_primary=True,
                        image=pdata['image'],
                        alt_text=pdata['name'],
                        order=1
                    )

                # Variants (Size + Color + Stock)
                for size_obj, color_obj, stock_count, price_diff in pdata['variants']:
                    ProductVariant.objects.update_or_create(
                        product=product,
                        size=size_obj,
                        color=color_obj,
                        defaults={
                            'stock': stock_count,
                            'price_override': price_diff
                        }
                    )

                # Delivery Estimates
                DeliveryEstimate.objects.update_or_create(
                    product=product,
                    region='Within Telangana',
                    defaults={'estimate': '2-3 business days', 'order': 1}
                )
                DeliveryEstimate.objects.update_or_create(
                    product=product,
                    region='Other States',
                    defaults={'estimate': '4-6 business days', 'order': 2}
                )

            # 9. Site Configuration
            SiteConfig.objects.update_or_create(
                id=1,
                defaults={
                    'shipping_fee': Decimal('99.00'),
                    'free_shipping_threshold': Decimal('1999.00'),
                    'tax_percentage': Decimal('0.00'),
                    'whatsapp_number': '918897021560',
                    'instagram_url': 'https://www.instagram.com/plantswala8?mdxt=MzYyZ3F0aXR0dzNn',
                    'facebook_url': 'https://facebook.com/plantswala',
                    'email': 'plantswala8@gmail.com',
                    'address': '46-16-32, Plants wala store, Opp to spark saloon, Danavaipeta, Rajahmundry - 533103'
                }
            )

            # 10. Coupons
            now = timezone.now()
            Coupon.objects.update_or_create(
                code='GREEN2',
                defaults={
                    'discount_type': 'percentage',
                    'value': Decimal('15.00'),
                    'min_order_value': Decimal('699.00'),
                    'valid_from': now - timedelta(days=1),
                    'valid_to': now + timedelta(days=365),
                    'active': True,
                    'usage_limit': 1000
                }
            )
            Coupon.objects.update_or_create(
                code='WELCOME10',
                defaults={
                    'discount_type': 'percentage',
                    'value': Decimal('10.00'),
                    'min_order_value': Decimal('499.00'),
                    'valid_from': now - timedelta(days=1),
                    'valid_to': now + timedelta(days=365),
                    'active': True,
                    'usage_limit': 1000
                }
            )

            # 11. Content (Announcement Bars & Social Proof)
            announcements = [
                ('🌿 Free Shipping on orders above ₹1999', 1),
                ('✨ Buy 2 Plants @ ₹699 — Use Code: GREEN2', 2),
                ('🏺 Flat 20% OFF on Ceramic Planters', 3),
            ]
            for text, ord_val in announcements:
                AnnouncementBar.objects.update_or_create(
                    text=text,
                    defaults={'order': ord_val, 'is_active': True}
                )

            social_proofs = [
                ('smile', '50,000+', 'Happy Plant Parents', 1),
                ('truck', 'Safe & Fresh', 'Guaranteed Delivery', 2),
                ('star', '4.9/5', '12,000+ Reviews', 3),
            ]
            SocialProofItem.objects.all().delete()
            for icon, title, subtitle, ord_val in social_proofs:
                SocialProofItem.objects.create(
                    icon=icon,
                    title=title,
                    subtitle=subtitle,
                    order=ord_val,
                    is_active=True
                )

        self.stdout.write(self.style.SUCCESS("Store data seeded successfully!"))
