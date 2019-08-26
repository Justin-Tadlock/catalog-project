from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Sub_Category, Item

engine = create_engine('sqlite:///item_catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create Dummy User
new_user = User(name="Tommy Sanders", 
                email="t.sanders@gmail.com",
                picture="https://i.imgur.com/krcUjZf.jpg")
session.add(new_user)
session.commit()

# Adding Basic Categories
new_category = Category(name="Outdoors", user_id=1)
session.add(new_category)
session.commit()

new_category = Category(name="Video Games", user_id=1)
session.add(new_category)
session.commit()

new_category = Category(name="Technology", user_id=1)
session.add(new_category)
session.commit()

# Adding Basic Sub Categories
# Outdoors
new_sub_category = Sub_Category(name="Boots", cat_id=1, user_id=1)
session.add(new_sub_category)
session.commit()

new_sub_category = Sub_Category(name="Tents", cat_id=1, user_id=1)
session.add(new_sub_category)
session.commit()

new_sub_category = Sub_Category(name="Backpacks", cat_id=1, user_id=1)
session.add(new_sub_category)
session.commit()

# Video Games
new_sub_category = Sub_Category(name="Consoles", cat_id=2, user_id=1)
session.add(new_sub_category)
session.commit()

new_sub_category = Sub_Category(name="Games", cat_id=2, user_id=1)
session.add(new_sub_category)
session.commit()

new_sub_category = Sub_Category(name="Accessories", cat_id=2, user_id=1)
session.add(new_sub_category)
session.commit()

# Technology
new_sub_category = Sub_Category(name="Desktops", cat_id=3, user_id=1)
session.add(new_sub_category)
session.commit()

new_sub_category = Sub_Category(name="Laptops", cat_id=3, user_id=1)
session.add(new_sub_category)
session.commit()

# Creating basic items
# Outdoors
new_item = Item(name="KEEN Men's Targhee II Mid Waterproof Hiking Boot",
                price="$135.00",
                category="Outdoors",
                sub_category="Boots",
                picture = "https://images-na.ssl-images-amazon.com/images/I/714NRVdSqRL._UX695_.jpg",
                link = "https://www.amazon.com/KEEN-Targhee-Waterproof-Shitake-Brindle/dp/B008J5F9Y0/ref=sxin_3_osp67-3fc2ce6f_cov?ascsubtag=3fc2ce6f-87af-4af2-960a-c14586b9381c&creativeASIN=B008J5F9F4&cv_ct_id=amzn1.osp.3fc2ce6f-87af-4af2-960a-c14586b9381c&cv_ct_pg=search&cv_ct_wn=osp-search&keywords=waterproof%2Bhiking%2Bboots&linkCode=oas&pd_rd_i=B008J5F9F4&pd_rd_r=4dc0695f-fe3c-4f62-b7c0-45733a671bf0&pd_rd_w=kTcF4&pd_rd_wg=KjwSQ&pf_rd_p=ecf33437-71b9-4523-8c89-d04c930d3865&pf_rd_r=9VAA1XD78FWNQNXAEPH6&qid=1566542411&s=gateway&tag=fnonsite-20&th=1&psc=1",
                description="Water-proof boots. Great for hiking in creaks!",
                cat_id=1,
                sub_cat_id=1,
                user_id=1)
session.add(new_item)
session.commit()

new_item = Item(name="Columbia Women's Newton Ridge Plus Waterproof Hiking Boot",
                price="$59.99",
                category="Outdoors",
                sub_category="Boots",
                picture = "https://images-na.ssl-images-amazon.com/images/I/61X2TJj%2Bi-L._UY695_.jpg",
                link = "https://www.amazon.com/Columbia-Womens-Newton-Hiking-Regular/dp/B006A1EWIO/ref=sr_1_7?keywords=waterproof%2Bhiking%2Bboots&qid=1566542304&s=gateway&sr=8-7&th=1&psc=1",
                description="Water-proof boots. Great for hiking in creaks!",
                cat_id=1,
                sub_cat_id=1,
                user_id=1)
session.add(new_item)
session.commit()

new_item = Item(name="Doggy Tent",
                price="$29.99",
                category="Outdoors",
                sub_category="Tents",
                picture = "https://images-na.ssl-images-amazon.com/images/I/81l1PyX-edL._SL1500_.jpg",
                link = "https://www.amazon.com/little-dove-Pet-Teepee-Puppy/dp/B01H19RFYG/ref=sxin_1_osp105-14966aa1_cov?ascsubtag=14966aa1-75d7-45cd-b1f7-29ab402d84af&creativeASIN=B01H19RFYG&cv_ct_id=amzn1.osp.14966aa1-75d7-45cd-b1f7-29ab402d84af&cv_ct_pg=search&cv_ct_wn=osp-search&keywords=dog+tent&linkCode=oas&pd_rd_i=B01H19RFYG&pd_rd_r=e97d5e84-91f3-4f08-a97e-848158ebf6da&pd_rd_w=Kpoi6&pd_rd_wg=oPX5N&pf_rd_p=ecf33437-71b9-4523-8c89-d04c930d3865&pf_rd_r=S4Q2VGF7DYFD9G1BQFXX&qid=1566541877&s=gateway&tag=5042nst800sr-20",
                description="A small tent specifically for your pup!",
                cat_id=1,
                sub_cat_id=2,
                user_id=1)
session.add(new_item)
session.commit()

new_item = Item(name="TETON Sports Scout 3400 Internal Frame Backpack",
                price="$59.99",
                category="Outdoors",
                sub_category="Backpacks",
                picture="https://images-na.ssl-images-amazon.com/images/I/81JGjSMU6WL._SL1500_.jpg",
                link="https://www.amazon.com/TETON-Sports-Internal-High-Performance-Backpacking/dp/B000F34ZKS/ref=sxin_3_ac_d_pm?ac_md=3-2-QWJvdmUgJDUw-ac_d_pm&keywords=hiking+backpack&pd_rd_i=B000F34ZKS&pd_rd_r=ff46a27f-0858-436e-867d-990b26d96559&pd_rd_w=SpvJu&pd_rd_wg=nx0Tn&pf_rd_p=aed08533-d0f3-456a-bfcd-3ec60fc417c9&pf_rd_r=H4889PKT9DCN2QPPHYN6&psc=1&qid=1566542521&s=gateway",
                description="Performance Backpack for Backpacking, Hiking, Camping",
                cat_id=1,
                sub_cat_id=3,
                user_id=1)
session.add(new_item)
session.commit()

# Video Games
new_item = Item(name="Microsoft Xbox One X 1TB Console with Wireless Controller",
                price="$385.00",
                category="Video Games",
                sub_category="Consoles",
                picture="https://images-na.ssl-images-amazon.com/images/I/61LVSqb4BHL._AC_.jpg",
                link="https://www.amazon.com/Microsoft-Xbox-One-Console-Wireless-Controller/dp/B07NBVPZ6L/ref=sr_1_18?keywords=xbox+one+x&qid=1566542840&s=gateway&sr=8-18",
                description="Microsoft Xbox One X 1TB Console with Wireless Controller: Xbox One X Enhanced, HDR, Native 4K, Ultra HD",
                cat_id=2,
                sub_cat_id=4,
                user_id=1)
session.add(new_item)
session.commit()

new_item = Item(name="Halo: Master Chief Collection - Xbox One Digital Code",
                price="$29.99",
                category="Video Games",
                sub_category="Games",
                picture="https://images-na.ssl-images-amazon.com/images/I/71ripjSsxiL._AC_SX215_.jpg",
                link="https://www.amazon.com/Halo-Master-Chief-Collection-Digital/dp/B00ZQ17PL0/ref=sr_1_2?crid=35CKO99RVGFN4&keywords=halo+master+chief+collection+xbox+one&qid=1566543256&s=gateway&sprefix=Halo+master%2Caps%2C271&sr=8-2",
                description="The Complete Master Chief Story – Honoring the iconic hero and his epic journey, The Master Chief’s entire story is brought together as The Master Chief Collection.",
                cat_id=2,
                sub_cat_id=5,
                user_id=1)
session.add(new_item)
session.commit()

new_item = Item(name="Destiny 2: Forsaken - Legendary Collection",
                price="$32.99",
                category="Video Games",
                sub_category="Games",
                picture="https://images-na.ssl-images-amazon.com/images/I/71iC185t43L._AC_SX215_.jpg",
                link="https://www.amazon.com/Destiny-Forsaken-Legendary-Collection-Xbox-One/dp/B07F8R7CFG/ref=sr_1_2?keywords=Destiny%2Bxbox&qid=1566543419&s=gateway&sr=8-2&th=1",
                description="Four story experiences. Eight worlds to explore. Thousands of rewards to discover. One Legendary Collection.",
                cat_id=2,
                sub_cat_id=5,
                user_id=1)
session.add(new_item)
session.commit()

new_item = Item(name="Dual Charging Station for Xbox One",
                price="$24.49",
                category="Video Games",
                sub_category="Accessories",
                picture="https://images-na.ssl-images-amazon.com/images/I/81vvwFaLweL._SL1500_.jpg",
                link="https://www.amazon.com/AmazonBasics-Dual-Charging-Station-Xbox-One/dp/B01N1P0KFI/ref=sxin_1_pb?keywords=xbox+one+accessories&pd_rd_i=B01N1P0KFI&pd_rd_r=bd082d99-fd8f-4e41-a796-5887252751b8&pd_rd_w=t7iWK&pd_rd_wg=KqBNK&pf_rd_p=9ef0c97a-254b-445c-822b-c948e2d94ddd&pf_rd_r=QMYWY0XQV0YY8GDX70Z2&qid=1566619433&s=gateway",
                description="Charge one controller or two controllers at the same time with the AmazonBasics Xbox One Dual Charging Station.",
                cat_id=2,
                sub_cat_id=6,
                user_id=1)
session.add(new_item)
session.commit()

# Technology
new_item = Item(name="Meerkat",
                price="$32.99",
                category="Technology",
                sub_category="Desktops",
                picture="https://d1vhcvzji58n1j.cloudfront.net/assets/products/meer4/forward-4f71009d14_2560.png",
                link="https://system76.com/desktops/meerkat",
                description="Meerkat is so easy to set up and use that you’ll be on the Internet in less than 10 minutes. Simply plug in your keyboard, mouse, and monitor.",
                cat_id=3,
                sub_cat_id=7,
                user_id=1)
session.add(new_item)
session.commit()

new_item = Item(name="Adder",
                price="$2,099.00",
                category="Technology",
                sub_category="Laptops",
                picture="https://d1vhcvzji58n1j.cloudfront.net/assets/products/addw1/feature-f21036bc9f_2560.webp",
                link="https://system76.com/laptops/adder",
                description="A wonderfully powerful balance of power and battery life with the ability to toggle between NVIDIA graphics and intel graphics.",
                cat_id=3,
                sub_cat_id=8,
                user_id=1)
session.add(new_item)
session.commit()

new_item = Item(name="Thelio R1",
                price="$899.00",
                category="Technology",
                sub_category="Desktops",
                picture="https://d1vhcvzji58n1j.cloudfront.net/assets/thelio/page/thumbnail-thelio-regular-cd1af656fb_2560.webp",
                link="https://system76.com/cart/configure/thelio-r1",
                description="A space-saving desktop, Thelio is designed to maximize the performance of every high-end component while remaining incredibly compact.",
                cat_id=3,
                sub_cat_id=7,
                user_id=1)
session.add(new_item)
session.commit()


print("Finished adding initial items!")
