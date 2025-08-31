from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Category, Product, UserInteraction
from recommendations.models import UserProfile
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate the database with Indian e-commerce dummy data'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        parser.add_argument('--products', type=int, default=50, help='Number of products to create')

    def handle(self, *args, **options):
        self.stdout.write('Creating Indian e-commerce dummy data...')
        
        # Create categories relevant to Indian market
        categories_data = [
            {'name': 'Electronics & Gadgets', 'slug': 'electronics', 'description': 'Smartphones, laptops, and electronic accessories'},
            {'name': 'Fashion & Clothing', 'slug': 'fashion', 'description': 'Traditional and western wear for men and women'},
            {'name': 'Books & Education', 'slug': 'books', 'description': 'Academic books, novels, and educational materials'},
            {'name': 'Home & Kitchen', 'slug': 'home-kitchen', 'description': 'Home appliances, kitchenware, and furniture'},
            {'name': 'Sports & Fitness', 'slug': 'sports', 'description': 'Sports equipment, fitness gear, and outdoor accessories'},
            {'name': 'Beauty & Personal Care', 'slug': 'beauty', 'description': 'Cosmetics, skincare, and personal hygiene products'},
            {'name': 'Toys & Games', 'slug': 'toys', 'description': 'Children toys, board games, and educational toys'},
            {'name': 'Grocery & Food', 'slug': 'grocery', 'description': 'Indian spices, snacks, and packaged foods'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description']
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Indian-focused product data with INR pricing
        products_data = {
            'Electronics & Gadgets': [
                ('OnePlus Nord CE 3', 'Latest 5G smartphone with 108MP camera and fast charging', 24999, 'smartphone,mobile,5g,oneplus,android'),
                ('Mi True Wireless Earbuds', 'Premium sound quality with active noise cancellation', 4999, 'audio,wireless,xiaomi,earbuds,bluetooth'),
                ('HP Pavilion Gaming Laptop', 'Intel i5 processor with NVIDIA graphics for gaming', 65999, 'laptop,gaming,hp,intel,nvidia'),
                ('boAt Smartwatch Xtend', 'Fitness tracking with heart rate monitor and GPS', 7999, 'smartwatch,fitness,boat,health,gps'),
                ('iPad Air 10.9 inch', '10.9-inch Liquid Retina display with A14 Bionic chip', 54900, 'tablet,ipad,apple,productivity'),
                ('JBL Flip 6 Speaker', 'Portable Bluetooth speaker with powerful bass', 9999, 'speaker,jbl,bluetooth,portable,bass'),
            ],
            'Fashion & Clothing': [
                ('Levi\'s 511 Slim Jeans', 'Classic slim fit denim jeans for everyday wear', 3499, 'jeans,levis,denim,casual,mens'),
                ('Allen Solly Cotton Shirt', 'Formal cotton shirt perfect for office wear', 1299, 'shirt,formal,cotton,allen-solly,office'),
                ('Woodland Leather Jacket', 'Genuine leather jacket for winter fashion', 8999, 'jacket,leather,woodland,winter,fashion'),
                ('Nike Air Max Shoes', 'Comfortable running shoes with air cushioning', 7999, 'shoes,nike,running,sports,air-max'),
                ('Peter England Suit', 'Two-piece formal suit for special occasions', 6999, 'suit,formal,peter-england,wedding,office'),
                ('Fabindia Kurti', 'Traditional cotton kurti with ethnic prints', 1899, 'kurti,traditional,fabindia,ethnic,cotton'),
            ],
            'Books & Education': [
                ('NCERT Physics Class 12', 'Official NCERT textbook for Class 12 Physics', 299, 'textbook,ncert,physics,education,cbse'),
                ('The Mahabharata by R.K. Narayan', 'Classic retelling of the Indian epic', 399, 'novel,classic,indian,literature,epic'),
                ('Objective Mathematics by R.D. Sharma', 'Comprehensive guide for competitive exams', 899, 'mathematics,competitive,jee,neet,sharma'),
                ('Rich Dad Poor Dad Hindi', 'Hindi translation of the bestselling finance book', 199, 'finance,self-help,hindi,money,investing'),
                ('Indian History by Bipan Chandra', 'Complete guide to modern Indian history', 599, 'history,india,independence,bipan-chandra'),
                ('Gitanjali by Rabindranath Tagore', 'Nobel Prize winning collection of poems', 250, 'poetry,tagore,literature,nobel,bengali'),
            ],
            'Home & Kitchen': [
                ('Prestige Pressure Cooker 5L', 'Stainless steel pressure cooker for Indian cooking', 2499, 'pressure-cooker,prestige,kitchen,cooking,steel'),
                ('Bajaj Majesty Mixer Grinder', '750W mixer grinder with 3 jars for grinding spices', 3999, 'mixer-grinder,bajaj,kitchen,spices,grinding'),
                ('Godrej Eon Refrigerator', '185L single door refrigerator with inverter technology', 16999, 'refrigerator,godrej,appliance,cooling,inverter'),
                ('Cello Plastic Chairs Set', 'Set of 4 durable plastic chairs for home', 2999, 'chairs,plastic,cello,furniture,dining'),
                ('Milton Thermosteel Flask', '1 litre stainless steel flask keeps drinks hot/cold', 899, 'flask,milton,thermosteel,hot,cold'),
                ('Pigeon Induction Cooktop', '1800W induction cooktop for modern cooking', 2299, 'induction,pigeon,cooktop,cooking,electric'),
            ],
            'Sports & Fitness': [
                ('Cosco Volleyball', 'Professional quality volleyball for matches', 799, 'volleyball,cosco,sports,outdoor,team'),
                ('Nivia Basketball', 'Official size basketball with excellent grip', 1299, 'basketball,nivia,sports,outdoor,team'),
                ('Strauss Gym Equipment Set', 'Complete home gym set with dumbbells and resistance bands', 4999, 'gym,fitness,dumbbells,home-workout,strauss'),
                ('Yonex Badminton Racket', 'Professional badminton racket for tournaments', 3499, 'badminton,yonex,racket,sports,professional'),
                ('Domyos Yoga Mat', '6mm thick yoga mat for comfortable exercise', 1299, 'yoga,mat,fitness,exercise,domyos'),
                ('Nivia Running Shoes', 'Lightweight running shoes for daily jogging', 2499, 'running,shoes,nivia,jogging,fitness'),
            ],
            'Beauty & Personal Care': [
                ('Lakme Absolute Foundation', 'Full coverage foundation for flawless skin', 899, 'foundation,lakme,makeup,coverage,beauty'),
                ('Himalaya Face Wash', 'Neem and turmeric face wash for clear skin', 149, 'facewash,himalaya,neem,turmeric,skincare'),
                ('Mama Earth Sunscreen', 'Natural sunscreen with SPF 50+ protection', 399, 'sunscreen,mamaearth,natural,spf,protection'),
                ('Forest Essentials Perfume', 'Luxury Ayurvedic perfume with rose and sandalwood', 2999, 'perfume,forest-essentials,ayurvedic,luxury,natural'),
                ('The Body Shop Moisturizer', 'Vitamin E body moisturizer for soft skin', 1299, 'moisturizer,body-shop,vitamin-e,skincare'),
                ('Biotique Hair Oil', 'Coconut oil with bhringraj for healthy hair', 299, 'hair-oil,biotique,coconut,bhringraj,natural'),
            ],
            'Toys & Games': [
                ('Lego Classic Building Set', 'Creative building blocks for children aged 4-99', 2999, 'lego,building,blocks,creative,children'),
                ('Funskool Monopoly India', 'Indian edition of the classic property game', 1299, 'monopoly,funskool,board-game,family,strategy'),
                ('Hot Wheels Car Set', 'Pack of 10 die-cast cars for kids', 1999, 'hot-wheels,cars,diecast,kids,collection'),
                ('Rubik\'s Cube 3x3', 'Original 3x3 speed cube for puzzle lovers', 699, 'rubiks-cube,puzzle,brain,speed,solving'),
                ('Barbie Doll House', 'Three-story dollhouse with furniture and accessories', 4999, 'barbie,dollhouse,girls,imaginative,play'),
                ('Chess Board Wooden', 'Handcrafted wooden chess board with pieces', 1499, 'chess,wooden,strategy,board-game,classic'),
            ],
            'Grocery & Food': [
                ('Tata Tea Premium', '1kg pack of premium Assam tea blend', 299, 'tea,tata,assam,premium,beverage'),
                ('Amul Pure Ghee', '1 litre tin of pure cow ghee for cooking', 599, 'ghee,amul,pure,cow,cooking'),
                ('MDH Garam Masala', '100g pack of authentic garam masala spice mix', 89, 'spices,mdh,garam-masala,authentic,cooking'),
                ('Britannia Good Day Cookies', 'Butter cookies pack for tea time snacking', 45, 'cookies,britannia,butter,snack,teatime'),
                ('Maggi 2-Minute Noodles', 'Pack of 12 masala noodles for quick meals', 144, 'noodles,maggi,instant,masala,quick'),
                ('Haldiram\'s Bhujia', '400g pack of spicy sev bhujia snack', 120, 'bhujia,haldirams,spicy,snack,namkeen'),
            ],
        }

        # Create products with Indian pricing in rupees
        created_products = 0
        for category in categories:
            if category.name in products_data:
                for product_info in products_data[category.name]:
                    name, description, price, tags = product_info
                    slug = name.lower().replace(' ', '-').replace("'", '').replace('\\', '')
                    
                    product, created = Product.objects.get_or_create(
                        slug=slug,
                        defaults={
                            'name': name,
                            'category': category,
                            'description': description,
                            'price': Decimal(str(price)),  # INR pricing
                            'stock': random.randint(10, 100),
                            'rating': round(random.uniform(3.5, 5.0), 1),
                            'popularity_score': round(random.uniform(0.1, 1.0), 2),
                            'tags': tags,
                        }
                    )
                    if created:
                        created_products += 1
                        
        self.stdout.write(f'Created {created_products} Indian products')

        # Create test users with Indian names
        indian_names = [
            ('Rahul', 'Sharma'), ('Priya', 'Patel'), ('Amit', 'Singh'), ('Sneha', 'Gupta'),
            ('Vikram', 'Kumar'), ('Anita', 'Reddy'), ('Suresh', 'Joshi'), ('Kavya', 'Nair'),
            ('Arjun', 'Agarwal'), ('Meera', 'Iyer'), ('Rohit', 'Verma'), ('Pooja', 'Yadav')
        ]
        
        created_users = 0
        for i in range(min(options['users'], len(indian_names))):
            first_name, last_name = indian_names[i]
            username = f'{first_name.lower()}{last_name.lower()}'
            email = f'{username}@example.com'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )
            
            if created:
                user.set_password('indian123')
                user.save()
                
                # Create user profile with Indian preferences
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'preferences': {
                            'preferred_categories': random.sample([cat.slug for cat in categories], 3),
                            'price_range': random.choice(['budget', 'mid-range', 'premium']),
                            'brand_preference': random.choice(['local', 'international', 'premium'])
                        }
                    }
                )
                created_users += 1

        self.stdout.write(f'Created {created_users} Indian test users')

        # Create random interactions
        users = User.objects.all()
        products = Product.objects.all()
        interaction_types = ['view', 'like', 'dislike', 'add_to_cart']
        
        created_interactions = 0
        for user in users:
            # Each user interacts with 10-30 random products
            num_interactions = random.randint(10, 30)
            user_products = random.sample(list(products), min(num_interactions, len(products)))
            
            for product in user_products:
                interaction_type = random.choice(interaction_types)
                
                # Create multiple interactions for some products
                num_same_interactions = random.randint(1, 3)
                for _ in range(num_same_interactions):
                    UserInteraction.objects.create(
                        user=user,
                        product=product,
                        interaction_type=interaction_type,
                        session_key=f'session_{user.id}_{random.randint(1000, 9999)}'
                    )
                    created_interactions += 1

        self.stdout.write(f'Created {created_interactions} user interactions')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated Indian e-commerce database with:\n'
                f'- {len(categories)} categories\n'
                f'- {created_products} products (INR pricing)\n'
                f'- {created_users} users\n'
                f'- {created_interactions} interactions'
            )
        )
