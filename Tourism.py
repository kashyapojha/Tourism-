"""
Incredible India — State Tourism Guide
Features: Login/Signup, Favourites, Quiz, Dark Mode, Search, TTS
"""

import tkinter as tk

from tkinter import ttk, scrolledtext, messagebox
import json, hashlib, os, random, threading, datetime

try:
    import pyttsx3

    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
DATA_FILE = os.path.join(BASE_DIR, "userdata.json")

# ── Colours ───────────────────────────────────────────────────────────────────
THEMES = {
    "light": {
        "bg": "#f5f4f0",
        "panel": "#ffffff",
        "header": "#1a3d2b",
        "header_fg": "#ffffff",
        "accent": "#1D9E75",
        "accent2": "#0F6E56",
        "text": "#1a1a1a",
        "muted": "#6b7280",
        "border": "#e2e0d8",
        "tag_bg": "#E1F5EE",
        "tag_fg": "#0F6E56",
        "list_sel": "#1D9E75",
        "card": "#f9f8f4",
        "danger": "#c0392b",
    },
    "dark": {
        "bg": "#1c1c1e",
        "panel": "#2c2c2e",
        "header": "#0d1f16",
        "header_fg": "#e0f2eb",
        "accent": "#30d68d",
        "accent2": "#1D9E75",
        "text": "#f2f2f7",
        "muted": "#8e8e93",
        "border": "#3a3a3c",
        "tag_bg": "#1a3d2b",
        "tag_fg": "#30d68d",
        "list_sel": "#1D9E75",
        "card": "#3a3a3c",
        "danger": "#ff453a",
    },
}

# ── State data (25 states, 5 sections each) ───────────────────────────────────
STATES = {
    "Rajasthan": {
        "emoji": "🏯",
        "tag": "Forts & Deserts",
        "Overview": "Rajasthan — the Land of Kings — is India's largest state by area (342,239 sq km). Famed for massive forts, colorful culture, golden deserts and royal palaces, it greets visitors with 'Padhaaro Maare Desh.' Folk dance, music, turbans and camels create a living spectacle unlike anywhere else in India.",
        "Food": "Must-try: Dal Baati Churma · Laal Maas · Ghewar · Ker Sangri · Bajre ki Khichdi · Pyaaz Kachori · Gatte ki Sabzi\n\nRajasthani cuisine is rich, spicy and designed for desert survival. Dal Baati Churma is the state's most iconic dish — baked wheat balls with lentils and sweet churma. Laal Maas is a fiery red mutton curry. Ghewar is a honeycomb-shaped festival dessert.",
        "Places to Visit": "Top spots: Amber Fort · Hawa Mahal · Jaisalmer Fort · Mehrangarh Fort · Udaipur City Palace · Ranthambore National Park · Pushkar Lake · Chokhi Dhani\n\nJaipur — the Pink City — is the crown jewel. Jaisalmer's golden sandstone fort rises from the Thar Desert. Udaipur, the City of Lakes, is among the most romantic cities in India.",
        "Best Time": "October to March — cool and pleasant. Avoid May–June (45°C+). The Pushkar Camel Fair (November) and Jaipur Literature Festival (January) are unmissable events.",
        "Fun Facts": "• India's largest state by area\n• Jaipur was the world's first planned city (1727 AD)\n• The Thar Desert covers 60% of Rajasthan\n• Has more forts and palaces than any other Indian state\n• Home to the only hill fort listed as UNESCO World Heritage — Chittorgarh",
    },
    "Gujarat": {
        "emoji": "🦁",
        "tag": "Desert & Lions",
        "Overview": "Gujarat is the only home of pure Asiatic Lions, houses the world's largest salt desert (Rann of Kutch), and is the birthplace of Mahatma Gandhi and Sardar Vallabhbhai Patel. Its coastline stretches over 1,600 km — the longest of any Indian state.",
        "Food": "Must-try: Dhokla · Thepla · Fafda-Jalebi · Undhiyu · Khandvi · Gujarati Thali · Mohanthal\n\nGujarati cuisine is predominantly vegetarian, subtly sweet and balanced. The Gujarati Thali covers every taste. Undhiyu — mixed vegetables slow-cooked underground — is a winter specialty. Fafda-Jalebi is the beloved Sunday morning breakfast.",
        "Places to Visit": "Top spots: Gir National Park · Rann of Kutch · Dwarka Temple · Somnath Temple · Statue of Unity · Rani ki Vav · Sabarmati Ashram · Marine National Park\n\nThe Rann of Kutch is a dazzling white salt desert in winter. The Statue of Unity at 182m is the world's tallest. Rani ki Vav is a UNESCO-listed stepwell of breathtaking intricacy.",
        "Best Time": "October to March. Rann Utsav (November–February) is a cultural highlight. Navratri Garba dance is a UNESCO Intangible Cultural Heritage.",
        "Fun Facts": "• Longest coastline in India — over 1,600 km\n• Only home of wild Asiatic Lions\n• Statue of Unity is the world's tallest statue\n• Surat processes 90% of the world's diamonds\n• First Indian state to prohibit alcohol (1960)",
    },
    "Kerala": {
        "emoji": "🌴",
        "tag": "Backwaters & Beaches",
        "Overview": "Kerala — 'God's Own Country' — is a 38,863 sq km treasure of backwaters, tea gardens, spice plantations and tropical beaches. Named one of the ten paradises of the world by National Geographic Traveler, it tops India's Human Development Index.",
        "Food": "Must-try: Sadya (banana leaf feast) · Appam with Stew · Fish Molee · Karimeen Pollichathu · Puttu and Kadala Curry · Kerala Prawn Curry · Payasam\n\nKeralan cuisine blends coconut, spices and seafood. The Sadya — a 20+ dish vegetarian feast on banana leaf — is served at Onam. Karimeen Pollichathu (pearl spot fish in banana leaf) is a local delicacy.",
        "Places to Visit": "Top spots: Alleppey Backwaters · Munnar Tea Gardens · Periyar Wildlife Sanctuary · Kovalam Beach · Varkala Cliff · Fort Kochi · Wayanad · Thekkady\n\nAlleppey is the 'Venice of the East' for its houseboat cruises. Munnar's emerald tea gardens are breathtaking. Fort Kochi blends Portuguese, Dutch and British colonial heritage.",
        "Best Time": "September to March (peak). Onam (Aug/Sep): snake boat races and feasts. Monsoon (June–Aug) is ideal for Ayurveda retreats.",
        "Fun Facts": "• 100% literacy rate — highest in India\n• Kalaripayattu (world's oldest martial art) originated here\n• Kerala produces 97% of India's rubber\n• Kathakali is one of India's 8 classical dance forms\n• Named 'God's Own Country' by the tourism board",
    },
    "Uttar Pradesh": {
        "emoji": "🕌",
        "tag": "Taj Mahal & Heritage",
        "Overview": "Uttar Pradesh is home to the Taj Mahal and Varanasi — one of the oldest continuously inhabited cities on earth. It is the origin of both Buddhism and Jainism and India's most populous state.",
        "Food": "Must-try: Lucknowi Dum Biryani · Tunday Kabab · Petha (Agra) · Banarasi Paan · Malai Makhan · Bedai Sabzi · Tehri\n\nLucknow's Dum Biryani and Tunday Kabab are internationally famous. Agra's Petha — a translucent sweet from white pumpkin — is a must-buy souvenir. Banarasi Paan is as much ritual as snack.",
        "Places to Visit": "Top spots: Taj Mahal · Varanasi Ghats · Agra Fort · Fatehpur Sikri · Sarnath · Vrindavan & Mathura · Lucknow Bara Imambara · Dudhwa NP\n\nThe Taj Mahal is a UNESCO World Heritage Site. Varanasi's ghats at sunrise are profoundly spiritual. Fatehpur Sikri is a ghost Mughal city frozen in the 16th century.",
        "Best Time": "October to March. Full moon at the Taj Mahal is a once-in-a-lifetime experience. Kumbh Mela at Prayagraj is the world's largest human gathering.",
        "Fun Facts": "• The Taj Mahal took 22 years and 20,000 workers to build\n• Varanasi is one of the world's oldest cities (3,000+ years)\n• Buddha delivered his first sermon at Sarnath in UP\n• UP produces the most sugarcane in India\n• Lucknow is famous for its chikankari embroidery",
    },
    "Goa": {
        "emoji": "🏖️",
        "tag": "Beaches & Nightlife",
        "Overview": "India's smallest state by area, Goa is a former Portuguese colony that attracts 8+ million tourists annually. Its unique Indo-Portuguese culture, vibrant nightlife, stunning churches and golden beaches make it visibly different from the rest of India.",
        "Food": "Must-try: Fish Curry Rice · Prawn Balchão · Bebinca · Xacuti · Chouriço · Feni · Pork Vindaloo\n\nGoan food marries Indian spices with Portuguese techniques. Fish Curry Rice is the everyday staple. Bebinca is the layered coconut queen of Goan desserts. Feni — distilled from cashew apples — is Goa's beloved local spirit.",
        "Places to Visit": "Top spots: Calangute & Baga · Palolem Beach · Old Goa Churches (UNESCO) · Dudhsagar Falls · Fort Aguada · Anjuna Flea Market · Spice Plantations · Chapora Fort\n\nPalolem is Goa's most picturesque crescent beach. Bom Jesus Basilica is a UNESCO World Heritage Site. Dudhsagar Falls is one of India's tallest waterfalls.",
        "Best Time": "November to February (peak). Goa Carnival (Feb/Mar) is a riot of colour. Monsoon brings lush greenery but beach shacks mostly close.",
        "Fun Facts": "• Highest per capita income among Indian states\n• Two UNESCO World Heritage Sites\n• Feni is the only Indian spirit with a GI tag\n• Under Portuguese rule for 451 years (1510–1961)\n• 30+ beaches — one for every day of the month",
    },
    "Jammu & Kashmir": {
        "emoji": "🏔️",
        "tag": "Paradise Valley",
        "Overview": "Kashmir — 'Paradise on Earth' — is a tapestry of snow-capped peaks, serene lakes, saffron fields and Mughal gardens. The valley sits at ~1,600m elevation, flanked by the Great Himalayas and Pir Panjal range.",
        "Food": "Must-try: Rogan Josh · Wazwan (36-course feast) · Yakhni · Dum Aloo · Kahwa (saffron tea) · Modur Pulao · Seekh Kabab\n\nKashmiri cuisine centres on slow-cooked meats in yoghurt and spice gravies. The Wazwan is a ceremonial 36-course feast — the ultimate expression of Kashmiri hospitality. Kahwa — saffron, cardamom and almond tea — is the valley's warm embrace.",
        "Places to Visit": "Top spots: Dal Lake & Shikara rides · Gulmarg · Pahalgam · Sonamarg Glacier · Leh Palace · Pangong Lake · Vaishno Devi Temple · Mughal Gardens\n\nDal Lake with floating gardens and houseboats is Kashmir's most iconic image. Gulmarg has Asia's highest gondola. Pangong Lake changes colour from blue to green through the day.",
        "Best Time": "Apr–Jun & Sep–Oct for the valley. Dec–Feb for skiing at Gulmarg. Ladakh: June–September.",
        "Fun Facts": "• Kashmir produces 90%+ of India's saffron\n• Dal Lake has 50,000+ people living on houseboats\n• Gulmarg has Asia's highest and longest cable car\n• Pangong Lake sits at 4,350m altitude\n• Pashmina wool is among the world's finest textiles",
    },
    "Karnataka": {
        "emoji": "🏛️",
        "tag": "Silk & Sandalwood",
        "Overview": "Karnataka — the land of sandalwood, silks and spices — blends ancient temple towns, the IT metropolis of Bengaluru, misty hill stations and pristine coastline. It produces 70% of India's coffee and the finest Mulberry silk in the world.",
        "Food": "Must-try: Bisi Bele Bath · Masala Dosa (origin) · Ragi Mudde · Coorg Pandi Curry · Mysore Pak · Neer Dosa · Mangalorean Fish Curry\n\nUdupi gave the world the masala dosa. Mysore Pak was invented in the Mysore royal kitchen. Coorg's Pandi (pork) Curry is a bold tribal specialty. Bisi Bele Bath is a comforting one-pot classic.",
        "Places to Visit": "Top spots: Hampi (UNESCO) · Mysore Palace · Coorg · Jog Falls · Badami Caves · Chikmagalur Coffee Estates · Bandipur NP · Gokarna Beach\n\nHampi — the ruined Vijayanagara capital — is a surreal boulder landscape. Jog Falls is India's second highest waterfall. Gokarna is a spiritual, quieter alternative to Goa.",
        "Best Time": "October to March. Mysore Dasara (October) — 100,000 lit bulbs illuminate the palace. Hampi Utsav (November) revives the glory of the empire.",
        "Fun Facts": "• Karnataka produces 70% of India's coffee\n• Bengaluru is Asia's fastest growing tech city\n• Hampi was the 2nd largest city in the world in the 14th century\n• ISRO headquarters is in Bengaluru\n• Has the highest number of UNESCO sites in South India",
    },
    "Himachal Pradesh": {
        "emoji": "❄️",
        "tag": "Snow & Temples",
        "Overview": "Himachal Pradesh — 'Land of Snow-capped Mountains' — is India's premier hill state. From apple orchards and cedar forests to alpine meadows and glaciated peaks, it is known as 'Dev Bhoomi' (Land of Gods) and India's adventure capital.",
        "Food": "Must-try: Dham (feast) · Siddu (steamed bread) · Chha Gosht · Babru · Aktori (buckwheat pancake) · Madra · Kullu Trout\n\nThe Dham is a traditional feast always cooked by Brahmin cooks. Siddu — steamed bread stuffed with poppy seeds or walnuts with ghee — is deeply comforting in winter. Kullu Trout from Himalayan streams is a delicacy.",
        "Places to Visit": "Top spots: Shimla · Manali & Rohtang Pass · Dharamsala & McLeodGanj · Spiti Valley · Kullu Valley · Kasol · Great Himalayan NP · Khajjiar\n\nShimla was the summer capital of British India. Spiti Valley is a remote high-altitude cold desert. McLeodGanj is the Dalai Lama's residence and a vibrant Tibetan cultural centre.",
        "Best Time": "March–June for hill stations. December–February for skiing at Solang Valley. Spiti is accessible only May–October.",
        "Fun Facts": "• Himachal produces 25% of India's apples\n• Snow leopards inhabit Kugti Wildlife Sanctuary\n• Khajjiar is known as India's Mini Switzerland\n• Shimla was the summer capital of British India\n• The state has over 2,000 temples and monasteries",
    },
    "Punjab": {
        "emoji": "⚔️",
        "tag": "Five Rivers & Sikhs",
        "Overview": "Punjab — the land of five rivers — is India's agricultural powerhouse, producing 40–50% of its wheat and rice. It is the spiritual home of Sikhism. The Golden Temple in Amritsar is reportedly the most visited place in India — surpassing even the Taj Mahal.",
        "Food": "Must-try: Makki di Roti & Sarson da Saag · Amritsari Kulcha · Butter Chicken · Chole Bhature · Lassi · Dal Makhani · Pindi Chhole\n\nButter Chicken and Dal Makhani — now global sensations — were born in Punjab. The winter meal of Makki di Roti and Sarson da Saag with white butter is the soul of rural Punjab.",
        "Places to Visit": "Top spots: Golden Temple · Jallianwala Bagh · Wagah Border · Anandpur Sahib · Qila Mubarak · Maharaja Ranjit Singh Museum · Gobindgarh Fort\n\nThe Golden Temple — covered in 750 kg of gold — feeds 100,000 people daily for free. The Wagah Border sunset ceremony is a spectacular display of nationalism.",
        "Best Time": "October to March. Lohri (January) and Baisakhi (April 13) are celebrated with Bhangra dancing and bonfires.",
        "Fun Facts": "• The Golden Temple feeds 100,000 people free daily — world's largest free kitchen\n• Punjab contributes 40–50% of India's wheat to the national grain pool\n• Butter Chicken was invented in Delhi by a Punjabi migrant\n• Bhangra dance originated here and is now a global phenomenon\n• Punjab has one of the highest tractor densities in the world",
    },
    "West Bengal": {
        "emoji": "🍵",
        "tag": "Darjeeling & Culture",
        "Overview": "West Bengal is India's cultural capital — home of Tagore, Satyajit Ray and Amartya Sen. It stretches from Darjeeling's Himalayan foothills to the Sundarbans mangrove delta. Kolkata's Durga Puja is a UNESCO Intangible Cultural Heritage.",
        "Food": "Must-try: Rosogolla · Macher Jhol · Shorshe Ilish · Luchi & Aloor Dom · Mishti Doi · Kolkata Biryani · Puchka\n\nBengali cuisine is built around fish, mustard oil and milk-based sweets. Ilish (hilsa) is worshipped as a delicacy with its own festival. Kolkata's puchka (pani puri) is considered the best in India.",
        "Places to Visit": "Top spots: Darjeeling (toy train + tea) · Sundarbans NP · Victoria Memorial · Howrah Bridge · Bishnupur Temples · Digha Beach · Hazarduari Palace · Kalimpong\n\nThe Sundarbans is the world's largest mangrove delta. The Darjeeling Himalayan Railway toy train is a UNESCO World Heritage Site.",
        "Best Time": "October to March. Durga Puja (October) transforms Kolkata into an open-air art gallery with spectacular pandals.",
        "Fun Facts": "• Durga Puja is a UNESCO Intangible Cultural Heritage\n• Sundarbans has the world's largest tiger reserve\n• West Bengal produces 25% of India's rice\n• Howrah Bridge has no nuts and bolts — only rivets\n• Darjeeling tea holds a Geographical Indication tag",
    },
    "Andhra Pradesh": {
        "emoji": "🏺",
        "tag": "Temples & Coastline",
        "Overview": "Andhra Pradesh is the land of spices, temples and the world's most visited pilgrimage site — Tirupati's Venkateswara Temple. It has the longest eastern coastline in India and rich Buddhist heritage from the Amaravati civilisation.",
        "Food": "Must-try: Pesarattu · Gongura Mutton · Pulihora · Bobbatlu · Kodi Pulusu · Chegodilu · Hyderabadi Biryani\n\nAndhra cuisine is arguably the spiciest in India. Gongura (sorrel leaf) is unique to AP and used in chutneys, meats and pickles. Pesarattu — a green moong dal crepe — is the classic breakfast.",
        "Places to Visit": "Top spots: Tirupati Temple · Araku Valley · Borra Caves · Visakhapatnam Beach · Amaravati Stupa · Nagarjunasagar Dam · Sri Sailam WS · Lepakshi Temple\n\nTirupati is the world's richest and most visited religious site. Araku Valley is accessible by one of India's most scenic train journeys.",
        "Best Time": "October to March. Ugadi (Telugu New Year, March/April) and Sankranti (January) are the state's biggest festivals.",
        "Fun Facts": "• Tirupati earns over ₹650 crore annually — world's richest temple\n• AP has the longest eastern coastline in India\n• Kuchipudi classical dance originated in AP\n• The state produces the most chillies in India\n• AP was the first state to implement e-governance in India",
    },
    "Arunachal Pradesh": {
        "emoji": "🌿",
        "tag": "Hidden Shangri-La",
        "Overview": "Called 'The Land of the Dawn-Lit Mountains,' Arunachal Pradesh is India's largest north-eastern state and one of the most biodiverse regions on Earth. It is home to 26 major tribes and the first sunrise in India.",
        "Food": "Must-try: Apong (rice beer) · Thukpa · Pika Pila (bamboo shoot) · Smoked Pork with Bamboo · Zan (millet porridge) · Lukter (dried beef) · Marua (millet beer)\n\nArunachali cuisine is flavoured by bamboo shoots, fermented foods and smoked meats. Apong (rice beer) is central to every tribal celebration.",
        "Places to Visit": "Top spots: Tawang Monastery · Ziro Valley · Namdapha NP · Sela Pass · Mechuka Valley · Dirang · Pasighat · Daporijo\n\nTawang Monastery at 10,000 ft is the second largest Buddhist monastery in the world. Ziro Valley is nominated for UNESCO World Heritage.",
        "Best Time": "October to April. Protected Area Permits required for non-Indians. Ziro Music Festival (September) is a cult indie music event.",
        "Fun Facts": "• Receives India's first sunrise\n• Home to 26 major tribes with distinct languages\n• Tawang is the 2nd largest Buddhist monastery in the world\n• Over 500 species of orchids\n• Namdapha NP is one of the world's biodiversity hotspots",
    },
    "Assam": {
        "emoji": "🦏",
        "tag": "Rhinos & Brahmaputra",
        "Overview": "Assam — the Gateway to North-East India — has five National Parks and 18 Wildlife Sanctuaries with the highest concentration of wildlife in India. The Brahmaputra River — considered male in Hindu tradition — is the state's lifeline. Assam produces 55% of India's tea.",
        "Food": "Must-try: Masor Tenga · Duck Meat Curry · Khar · Pitha (rice cake) · Bamboo Shoot Pickle · Jolpan · Assam Laksa\n\nAssamese cuisine is light and minimal in spices. Khar — an alkaline preparation from banana peels — is uniquely Assamese. Pitha rice cakes are made in dozens of varieties, especially at Bihu.",
        "Places to Visit": "Top spots: Kaziranga NP (UNESCO) · Majuli River Island · Kamakhya Temple · Manas NP · Sivasagar · Haflong · Dibru-Saikhowa NP · Pobitora WS\n\nKaziranga has two-thirds of the world's one-horned rhinos. Majuli is the world's largest river island. Kamakhya is one of the 51 Shakti Peethas.",
        "Best Time": "November to April. Bihu (April) is Assam's most joyous festival — the Assamese New Year celebrated with dance, music and feasts.",
        "Fun Facts": "• Produces 55% of India's total tea\n• Kaziranga has 70% of the world's one-horned rhinos\n• Majuli is the world's largest river island\n• The Brahmaputra crosses the Himalayas — one of only three rivers to do so\n• Home to the largest population of wild water buffalo",
    },
    "Bihar": {
        "emoji": "🕉️",
        "tag": "Buddhist Circuit",
        "Overview": "Bihar — from 'Vihara' (monastery) — was the cradle of Buddhism and Jainism, the birthplace of India's first empire (Maurya), and home to Nalanda, the world's first residential university. The Buddha attained enlightenment at Bodh Gaya.",
        "Food": "Must-try: Litti Chokha · Sattu Paratha · Dal Pitha · Makhana Kheer · Tilkut · Chura Dahi · Khaja\n\nLitti Chokha — roasted wheat balls stuffed with sattu served with charred brinjal — is Bihar's most iconic dish. Bihar produces 90% of the world's makhana (fox nuts).",
        "Places to Visit": "Top spots: Bodh Gaya · Nalanda ruins · Rajgir · Vaishali · Vikramshila · Mahabodhi Temple (UNESCO) · Patna Sahib Gurudwara · Valmiki NP\n\nThe Mahabodhi Temple is UNESCO-listed. The Bodhi tree is a direct descendant of the tree under which the Buddha attained enlightenment.",
        "Best Time": "October to March. Chhath Puja (Oct/Nov) — celebrated on riverbanks at sunrise and sunset — is Bihar's most sacred festival.",
        "Fun Facts": "• Nalanda was the world's first residential university\n• Bodh Gaya is one of Buddhism's four holiest sites\n• Bihar produces 90% of the world's makhana (fox nuts)\n• Chandragupta Maurya founded India's first empire here\n• Vaishali is considered the world's first republic (6th century BC)",
    },
    "Chhattisgarh": {
        "emoji": "🌊",
        "tag": "Waterfalls & Tribes",
        "Overview": "Chhattisgarh — India's tribal heartland — has 44% forest cover and 32% tribal population. It is home to the widest waterfall in India (Chitrakote Falls) and the most diverse tribal arts in the country.",
        "Food": "Must-try: Chila · Muthia · Fara · Bafauri · Aamat (tribal curry) · Bore Baasi · Sabudana Khichdi\n\nChhattisgarhi food is rice-based, light on spices and rich in indigenous ingredients. Bore Baasi — overnight-soaked rice with curd and onion — is the tribal breakfast. Aamat is a tangy stew with bamboo shoots unique to Bastar.",
        "Places to Visit": "Top spots: Chitrakote Falls · Bastar · Kanker Palace · Sirpur Buddhist Site · Barnawapara WS · Achanakmar Tiger Reserve · Bhoramdeo Temple · Tirathgarh Falls\n\nChitrakote — India's Niagara — swells to 300m wide in monsoon. Bastar's 75-day Dussehra is the world's longest festival.",
        "Best Time": "October to March. Bastar Dussehra (October) — a 75-day tribal goddess festival — is unique in all of India.",
        "Fun Facts": "• Chitrakote Falls is India's widest waterfall\n• Bastar Dussehra is the world's longest festival (75 days)\n• Over 80% of flora not found elsewhere in India\n• Chhattisgarh produces 15% of India's steel\n• Home to rare Gond and Baiga tribal painting traditions",
    },
    "Haryana": {
        "emoji": "🌾",
        "tag": "Battlefields & Culture",
        "Overview": "Haryana — 'Abode of God' — is both ancient and modern. Kurukshetra, where the Mahabharata war was fought, lies here. Yet Gurugram is one of India's fastest-growing tech and financial hubs. Haryana has produced more Olympic medals per capita than any other Indian state.",
        "Food": "Must-try: Bajra Khichdi · Hara Dhania Cholia · Singri ki Sabzi · Methi Gajar · Kachri ki Chutney · Besan Masala Roti · Alsi ki Pinni\n\nHaryanvi food is simple and nourishing. Bajra (pearl millet) is the staple grain. Alsi ki Pinni — flaxseeds, jaggery and ghee — is a winter energy booster.",
        "Places to Visit": "Top spots: Kurukshetra · Sultanpur NP · Pinjore Gardens · Morni Hills · Panipat Museum · Surajkund Craft Fair · Tilyar Lake · Farrukhnagar Step Well\n\nKurukshetra is one of India's most sacred sites. Surajkund Crafts Mela (February) is one of Asia's largest craft fairs.",
        "Best Time": "October to March. Geeta Jayanti at Kurukshetra (Nov/Dec). Surajkund Crafts Mela (February) is unmissable.",
        "Fun Facts": "• India's top producer of milk\n• Won 8 of India's 12 medals at the 2020 Tokyo Olympics\n• Panipat witnessed three decisive battles that shaped Indian history\n• Gurgaon hosts over 250 Fortune 500 companies\n• Home to India's largest solar power plant",
    },
    "Jharkhand": {
        "emoji": "💧",
        "tag": "Waterfalls & Forests",
        "Overview": "Jharkhand — 'Land of the Forest' — has India's richest mineral reserves yet also some of its most beautiful waterfalls, dense Sal forests and vibrant tribal traditions. Known as the 'Ruhr of India' for its industrial wealth.",
        "Food": "Must-try: Dhuska · Rugra (forest mushroom curry) · Chilka Roti · Litti Chokha · Bamboo Shoot Curry · Handia (rice beer) · Maro (millet porridge)\n\nRugra — a wild mushroom found only in Sal forests — is a seasonal delicacy. Handia rice beer is consumed at every tribal celebration. Dhuska is a crispy fried bread from soaked rice and lentils.",
        "Places to Visit": "Top spots: Hundru Falls · Betla NP · Netarhat · Jonha Falls · Deoghar Baidyanath Dham · Rajmahal Hills · Parasnath Hill · Dasam Falls\n\nHundru Falls drops 98m — one of India's highest. Netarhat is the 'Queen of Chotanagpur' for its sweeping sunrises. Baidyanath Dham is one of the 12 Jyotirlingas.",
        "Best Time": "October to March for waterfalls and wildlife. Sarhul (March/April) and Karma (August/September) are the major tribal festivals.",
        "Fun Facts": "• Richest mineral reserves in India\n• Hundru Falls drops 98m — one of India's highest\n• 28% of India's coal reserves are in Jharkhand\n• Parasnath Hill is the holiest Jain pilgrimage site\n• Jharkhand produces the most lac (shellac) in the world",
    },
    "Madhya Pradesh": {
        "emoji": "🐯",
        "tag": "Tigers & Temples",
        "Overview": "Madhya Pradesh — 'Heart of India' — has more UNESCO World Heritage Sites than any other Indian state and more tiger reserves than any other state. The Narmada River — one of India's seven sacred rivers — flows entirely through MP.",
        "Food": "Must-try: Dal Bafla · Poha Jalebi (Indore) · Bhutte ki Kees · Chakki ki Shaak · Mawa Bati · Sabudana Khichdi · Shikanji\n\nIndore's food scene is legendary — Sarafa Bazaar and Chappan Dukan are famous food streets. Poha-Jalebi is Indore's signature breakfast loved all over India.",
        "Places to Visit": "Top spots: Khajuraho (UNESCO) · Sanchi Stupa (UNESCO) · Bhimbetka (UNESCO) · Kanha Tiger Reserve · Bandhavgarh NP · Pachmarhi · Mandu · Omkareshwar\n\nKhajuraho's 10th-century temples are among the world's finest medieval Indian art. Bandhavgarh has the highest density of tigers in India.",
        "Best Time": "October to March. Tiger sighting is best in April–June. Khajuraho Dance Festival (February) is a classical arts extravaganza.",
        "Fun Facts": "• 3 UNESCO World Heritage Sites — more than any other state\n• Bandhavgarh has the world's highest density of Bengal tigers\n• MP has the most tiger reserves in India (7 reserves)\n• Bhimbetka cave paintings are 30,000 years old\n• The Narmada River flows 1,077 km entirely through MP",
    },
    "Maharashtra": {
        "emoji": "🏰",
        "tag": "Forts & Festivals",
        "Overview": "Maharashtra — India's wealthiest state — blends Maratha glory, Bollywood glamour, Konkan coastline and Mumbai's financial might. Shivaji Maharaj built 300+ forts across the Western Ghats that remain symbols of pride and popular trekking destinations.",
        "Food": "Must-try: Vada Pav · Misal Pav · Puran Poli · Modak · Kolhapuri Chicken · Sol Kadhi · Thali Peeth\n\nVada Pav — deep-fried potato dumpling in a bread roll — is Mumbai's beloved street food. Modak — steamed rice dumpling with coconut and jaggery — is Lord Ganesha's favourite, made by millions at Ganesh Chaturthi.",
        "Places to Visit": "Top spots: Ajanta & Ellora (UNESCO) · Gateway of India · Lonavala & Mahabaleshwar · Shirdi · Kolhapur · Daulatabad Fort · Nashik · Tadoba Tiger Reserve\n\nAjanta and Ellora cave temples span 2nd century BC to 10th century AD. Nashik is India's wine capital and hosts the Kumbh Mela.",
        "Best Time": "October to February. Ganesh Chaturthi (Aug/Sep) — Mumbai celebrates for 11 days with processions and immersion of thousands of Ganesha idols.",
        "Fun Facts": "• Maharashtra is India's wealthiest state by GDP\n• Mumbai produces 1,000+ Bollywood films per year\n• Ajanta cave paintings are 2,000 years old\n• More Shiva temples than any other state\n• Wari pilgrimage to Pandharpur draws 10 million people annually",
    },
    "Manipur": {
        "emoji": "🌺",
        "tag": "Polo & Floating Park",
        "Overview": "Manipur — 'the Jewel of India' — is celebrated for Manipuri dance, unique cuisine, the world's only floating national park (Keibul Lamjao), and the birthplace of Polo. Loktak Lake is the largest freshwater lake in north-east India.",
        "Food": "Must-try: Eromba · Singju · Chamthong · Ngari (fermented fish) · Paknam · Chak-hao Kheer (black rice pudding) · Morok Metpa\n\nNgari (fermented fish) is the backbone of Manipuri cooking. Chak-hao — GI-tagged black rice — is unique to Manipur. Eromba — mashed vegetables with fermented fish — is pungent and addictive.",
        "Places to Visit": "Top spots: Loktak Lake · Keibul Lamjao (floating NP) · Kangla Fort · Ima Keithel (women's market) · Shirui Lily Festival · Dzüko Valley · Moirang · Khonghampat Orchidarium\n\nIma Keithel is the world's only all-women market, 500+ years old. Dzüko Valley is a pristine alpine valley blanketed in wildflowers.",
        "Best Time": "October to February. Shirui Lily Festival (May) celebrates the state flower. Yaosang (Feb/Mar) is Manipur's exuberant 5-day Holi.",
        "Fun Facts": "• Polo originated in Manipur (1st century AD)\n• Keibul Lamjao is the world's only floating national park\n• Ima Keithel is the world's only all-women market (500+ years)\n• Chak-hao black rice has a GI tag\n• Manipuri dance is one of India's 8 classical dance forms",
    },
    "Meghalaya": {
        "emoji": "🌧️",
        "tag": "Wettest Place on Earth",
        "Overview": "Meghalaya — 'Abode of the Clouds' — is India's wettest state. Cherrapunjee and Mawsynram compete for the title of the world's wettest place. The state is home to matrilineal Khasi, Jaintia and Garo tribes and miraculous living root bridges.",
        "Food": "Must-try: Jadoh (rice & pork) · Tungrymbai (fermented soya) · Doh Khleh · Nakham Bitchi · Putharo · Minil Songa · Sakin Gata\n\nMeghalayan food is tribal and forest-based — pork, fermented soya and bamboo shoots dominate. Jadoh is the everyday Khasi staple. Tungrymbai has a deeply pungent, savoury flavour.",
        "Places to Visit": "Top spots: Living Root Bridges · Dawki River · Mawlynnong (Asia's cleanest village) · Elephant Falls · Ward's Lake · Nohkalikai Falls · Umiam Lake · Balpakram NP\n\nLiving root bridges — grown over 500 years — are remarkable bio-engineering. The Dawki River is so clear boats appear to float on air.",
        "Best Time": "October to May. Waterfalls are most dramatic in monsoon. Shillong Autumn Festival (Oct) and Cherry Blossom Festival (Nov) are beautiful.",
        "Fun Facts": "• World's two wettest places — Mawsynram & Cherrapunjee — are both here\n• Living root bridges are grown, not built — over 500 years old\n• One of three Indian states with a matrilineal society\n• Dawki River boats appear to float on air\n• Krem Puri is the world's longest sandstone cave (31 km)",
    },
    "Mizoram": {
        "emoji": "🎋",
        "tag": "Bamboo Forests & Mist",
        "Overview": "Mizoram — 'Land of the Hill People' — has 91%+ literacy, is over 90% Christian, and is deeply musical. Its rolling bamboo-covered hills, clean towns and hospitable Mizo people make it unlike any other Indian state.",
        "Food": "Must-try: Bai · Vawksa Rep (smoked pork) · Mizo Sawhchiar · Bamboo Shoot Fry · Chhum Han · Arsa Buhchiar · Zu (rice wine)\n\nVawksa Rep — smoked pork — is the cornerstone of Mizo cooking. Bai (boiled vegetables with pork and fermented soya) is the everyday staple. Zu rice wine is prepared at home for every festival.",
        "Places to Visit": "Top spots: Phawngpui (Blue Mountain) · Vantawng Falls · Reiek Heritage Village · Champhai Valley · Palak Lake · Murlen NP · Aizawl viewpoints · Tam Dil Lake\n\nPhawngpui — the Blue Mountain at 2,157m — is sacred to the Mizo people. Champhai Valley is the 'Rice Bowl of Mizoram.'",
        "Best Time": "October to March. Chapchar Kut (March) — celebrated with the iconic Cheraw (bamboo dance). Mim Kut (October) marks the maize harvest.",
        "Fun Facts": "• 91%+ literacy — second highest in India\n• Over 90% Christian population\n• Cheraw (bamboo dance) is the iconic cultural art form\n• Mizoram experiences Mautam — bamboo flowering every 48 years causing a rodent plague\n• Phawngpui is the Blue Mountain, sacred to the Mizo people",
    },
    "Nagaland": {
        "emoji": "🦅",
        "tag": "Hornbill Festival",
        "Overview": "Nagaland — 'Land of the Nagas' — has 16 major tribes, each with distinct languages, dress, food and traditions. The annual Hornbill Festival is one of Asia's most spectacular cultural events. The Ghost Pepper (Bhut Jolokia), once the world's hottest chilli, grows here.",
        "Food": "Must-try: Smoked Pork with Bamboo Shoot · Axone (fermented soya) · Galho · Zutho (rice beer) · Akhuni Chutney · Naga Chilli dishes\n\nNaga cuisine is bold, smoky and intensely flavoured. Axone is the pungent foundation of Naga cooking. The Bhut Jolokia (Ghost Pepper) was once the world's hottest chilli. Smoked meat techniques are unique to each tribe.",
        "Places to Visit": "Top spots: Hornbill Festival (Kisama) · Kohima War Cemetery · Dzüko Valley · Pfütsero · Khonoma Green Village · Japfu Peak Trek · Longwa Village · Touphema\n\nKohima War Cemetery honours Allied soldiers from one of WWII's fiercest battles. Longwa Village straddles the India-Myanmar border.",
        "Best Time": "October to March. Hornbill Festival (December 1–10) is the unmissable event. Book accommodation months ahead.",
        "Fun Facts": "• 16 major tribes each with distinct culture\n• Ghost Pepper (Bhut Jolokia) — once world's hottest chilli — is from Nagaland\n• Kohima War Cemetery is one of Asia's most moving WWII memorials\n• Khonoma is India's first green village\n• Longwa Village chief's house straddles the India-Myanmar border",
    },
    "Odisha": {
        "emoji": "🎭",
        "tag": "Temples & Odissi Dance",
        "Overview": "Odisha is home to the sacred Jagannath Temple at Puri, the erotic masterpieces of Konark Sun Temple and the Buddhist stupa at Dhauli. Odisha's Pattachitra paintings, Odissi dance and tribal crafts are internationally recognised art forms. The English word 'Juggernaut' comes from Jagannath.",
        "Food": "Must-try: Dalma · Pakhala Bhaat · Machha Besara · Chhena Poda · Rasgulla · Santula · Mudhi Mansa\n\nOdia cuisine is mild and flavoured by mustard and coconut. Pakhala Bhaat — rice soaked overnight — is one of the world's oldest fermented foods. Chhena Poda is a caramelised cottage cheese dessert — one of India's most unique sweets.",
        "Places to Visit": "Top spots: Puri Jagannath Temple · Konark Sun Temple (UNESCO) · Chilika Lake · Bhubaneswar · Simlipal NP · Dhauli Buddhist Stupa · Bhitarkanika · Rath Yatra\n\nKonark Sun Temple — a 13th-century chariot-shaped temple — is one of the world's greatest architectural achievements. Chilika Lake is Asia's largest brackish water lake.",
        "Best Time": "October to February. Rath Yatra in Puri (June/July) is a once-in-a-lifetime spectacle. Konark Dance Festival (December) is unmissable.",
        "Fun Facts": "• 'Juggernaut' in English comes from Jagannath\n• Konark is called the 'Black Pagoda' by sailors\n• Bhubaneswar has 242 temples alone\n• Odisha Rasagola has a GI tag separate from Bengal's Rosogolla\n• Chilika Lake hosts 160 species of migratory birds in winter",
    },
    "Sikkim": {
        "emoji": "🌸",
        "tag": "Himalayan Wonderland",
        "Overview": "Sikkim — India's smallest state — is arguably its most naturally spectacular. Home to Kangchenjunga (world's 3rd highest mountain at 8,586m), it was an independent Buddhist kingdom until 1975 and became India's first fully organic state in 2016.",
        "Food": "Must-try: Phagshapa · Gundruk · Momo · Thukpa · Chhurpi (hard cheese) · Sel Roti · Tongba (millet beer)\n\nSikkimese cuisine reflects Nepali, Tibetan and Lepcha roots. Momo — steamed dumplings — are everywhere and deeply addictive. Tongba is a fermented millet drink served hot in a bamboo mug — perfect for cold mountain evenings.",
        "Places to Visit": "Top spots: Kangchenjunga · Gurudongmar Lake · Rumtek Monastery · Pelling · Tsomgo Lake · Yumthang Valley · Namchi · Ravangla Buddha Park\n\nGurudongmar Lake at 17,100 ft is one of the world's highest lakes. Yumthang Valley bursts into rhododendron colour in spring.",
        "Best Time": "March–May (rhododendron bloom) and October–December (clear mountain views). Losar — Tibetan New Year (Feb/Mar) — is the biggest festival.",
        "Fun Facts": "• Was an independent Buddhist kingdom until 1975\n• India's first fully organic farming state (2016)\n• Kangchenjunga is the world's 3rd highest mountain at 8,586m\n• Gurudongmar Lake is one of the world's highest lakes at 17,100 ft\n• Over 600 species of orchids — highest density in India",
    },
}

TABS = ["Overview", "Food", "Places to Visit", "Best Time", "Fun Facts"]

QUIZ_QUESTIONS = [
    {
        "q": "Which state is home to the world's only wild Asiatic Lions?",
        "options": ["Rajasthan", "Gujarat", "Maharashtra", "Karnataka"],
        "ans": "Gujarat",
    },
    {
        "q": "Which Indian state receives the country's first sunrise?",
        "options": ["Meghalaya", "Nagaland", "Arunachal Pradesh", "Assam"],
        "ans": "Arunachal Pradesh",
    },
    {
        "q": "The English word 'Juggernaut' comes from which temple?",
        "options": ["Tirupati", "Jagannath (Puri)", "Somnath", "Konark"],
        "ans": "Jagannath (Puri)",
    },
    {
        "q": "Which state produces 55% of India's total tea output?",
        "options": ["West Bengal", "Assam", "Kerala", "Himachal Pradesh"],
        "ans": "Assam",
    },
    {
        "q": "Polo — the sport — originated in which Indian state?",
        "options": ["Rajasthan", "Manipur", "Punjab", "Gujarat"],
        "ans": "Manipur",
    },
    {
        "q": "Which festival lasts 75 days — the world's longest festival?",
        "options": [
            "Pushkar Camel Fair",
            "Hornbill Festival",
            "Bastar Dussehra",
            "Onam",
        ],
        "ans": "Bastar Dussehra",
    },
    {
        "q": "Which state was India's first to become fully organic?",
        "options": ["Kerala", "Sikkim", "Uttarakhand", "Nagaland"],
        "ans": "Sikkim",
    },
    {
        "q": "The Ghost Pepper (Bhut Jolokia) — once world's hottest chilli — grows in which state?",
        "options": ["Andhra Pradesh", "Karnataka", "Nagaland", "Rajasthan"],
        "ans": "Nagaland",
    },
    {
        "q": "Which lake is the world's only floating national park?",
        "options": ["Loktak Lake", "Dal Lake", "Chilika Lake", "Umiam Lake"],
        "ans": "Loktak Lake",
    },
    {
        "q": "Mawsynram and Cherrapunjee are both in which state?",
        "options": ["Assam", "Mizoram", "Nagaland", "Meghalaya"],
        "ans": "Meghalaya",
    },
    {
        "q": "Which state has the world's largest free kitchen?",
        "options": ["Rajasthan", "Gujarat", "Punjab", "Maharashtra"],
        "ans": "Punjab",
    },
    {
        "q": "Namdapha National Park is located in which state?",
        "options": ["Assam", "Arunachal Pradesh", "Meghalaya", "Manipur"],
        "ans": "Arunachal Pradesh",
    },
    {
        "q": "Bhimbetka cave paintings are approximately how old?",
        "options": ["5,000 years", "10,000 years", "30,000 years", "1,000 years"],
        "ans": "30,000 years",
    },
    {
        "q": "Which state is known as 'Dev Bhoomi' (Land of Gods)?",
        "options": ["Uttarakhand", "Himachal Pradesh", "Rajasthan", "Bihar"],
        "ans": "Himachal Pradesh",
    },
    {
        "q": "Kuchipudi classical dance originated in which state?",
        "options": ["Tamil Nadu", "Kerala", "Karnataka", "Andhra Pradesh"],
        "ans": "Andhra Pradesh",
    },
]

# ── Storage helpers ─────────────────────────────────────────────────────────────


def _load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def load_users():
    return _load_json(USERS_FILE, {})


def save_users(users):
    _save_json(USERS_FILE, users)


def load_userdata():
    return _load_json(DATA_FILE, {})


def save_userdata(data):
    _save_json(DATA_FILE, data)


def get_user_record(username):
    ud = load_userdata()
    if username not in ud:
        ud[username] = {"favourites": [], "visited": [], "quiz_scores": []}
        save_userdata(ud)
    return ud[username]


def save_user_record(username, record):
    ud = load_userdata()
    ud[username] = record
    save_userdata(ud)


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH SCREEN
# ══════════════════════════════════════════════════════════════════════════════


class AuthScreen(tk.Frame):
    def __init__(self, master, on_login):
        super().__init__(master, bg="#1a3d2b")
        self.on_login = on_login
        self.mode = "login"  # or "signup"
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = tk.Frame(self, bg="#ffffff", bd=0, relief="flat")
        card.place(relx=0.5, rely=0.5, anchor="center", width=360, height=460)

        tk.Label(card, text="🇮🇳", font=("Helvetica", 40), bg="#ffffff").pack(
            pady=(30, 4)
        )
        tk.Label(
            card,
            text="Incredible India",
            font=("Helvetica", 18, "bold"),
            bg="#ffffff",
            fg="#1a3d2b",
        ).pack()
        tk.Label(
            card,
            text="State Tourism Guide",
            font=("Helvetica", 11),
            bg="#ffffff",
            fg="#6b7280",
        ).pack(pady=(2, 20))

        self.mode_lbl = tk.Label(
            card,
            text="Login to your account",
            font=("Helvetica", 13, "bold"),
            bg="#ffffff",
            fg="#1a1a1a",
        )
        self.mode_lbl.pack()

        form = tk.Frame(card, bg="#ffffff", pady=10, padx=30)
        form.pack(fill="x")

        tk.Label(
            form,
            text="Username",
            bg="#ffffff",
            fg="#6b7280",
            font=("Helvetica", 10),
            anchor="w",
        ).pack(fill="x")
        self.username_var = tk.StringVar()
        tk.Entry(
            form,
            textvariable=self.username_var,
            font=("Helvetica", 12),
            relief="solid",
            bd=1,
        ).pack(fill="x", pady=(2, 10))

        tk.Label(
            form,
            text="Password",
            bg="#ffffff",
            fg="#6b7280",
            font=("Helvetica", 10),
            anchor="w",
        ).pack(fill="x")
        self.password_var = tk.StringVar()
        tk.Entry(
            form,
            textvariable=self.password_var,
            show="●",
            font=("Helvetica", 12),
            relief="solid",
            bd=1,
        ).pack(fill="x", pady=(2, 4))

        # Signup-only field
        self.email_frame = tk.Frame(form, bg="#ffffff")
        tk.Label(
            self.email_frame,
            text="Email (optional)",
            bg="#ffffff",
            fg="#6b7280",
            font=("Helvetica", 10),
            anchor="w",
        ).pack(fill="x")
        self.email_var = tk.StringVar()
        tk.Entry(
            self.email_frame,
            textvariable=self.email_var,
            font=("Helvetica", 12),
            relief="solid",
            bd=1,
        ).pack(fill="x", pady=(2, 4))

        self.err_lbl = tk.Label(
            form,
            text="",
            fg="#c0392b",
            bg="#ffffff",
            font=("Helvetica", 10),
            wraplength=280,
        )
        self.err_lbl.pack()

        self.action_btn = tk.Button(
            form,
            text="Login",
            font=("Helvetica", 12, "bold"),
            bg="#1D9E75",
            fg="white",
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._action,
        )
        self.action_btn.pack(fill="x", pady=8)

        self.toggle_btn = tk.Button(
            card,
            text="Don't have an account? Sign Up",
            font=("Helvetica", 10),
            bg="#ffffff",
            fg="#1D9E75",
            relief="flat",
            cursor="hand2",
            command=self._toggle,
        )
        self.toggle_btn.pack()

        tk.Button(
            card,
            text="Continue as Guest →",
            font=("Helvetica", 10),
            bg="#ffffff",
            fg="#6b7280",
            relief="flat",
            cursor="hand2",
            command=lambda: self.on_login("guest"),
        ).pack(pady=(4, 0))

    def _toggle(self):
        self.mode = "signup" if self.mode == "login" else "login"
        if self.mode == "signup":
            self.mode_lbl.config(text="Create an account")
            self.action_btn.config(text="Sign Up")
            self.toggle_btn.config(text="Already have an account? Login")
            self.email_frame.pack(fill="x")
        else:
            self.mode_lbl.config(text="Login to your account")
            self.action_btn.config(text="Login")
            self.toggle_btn.config(text="Don't have an account? Sign Up")
            self.email_frame.pack_forget()
        self.err_lbl.config(text="")

    def _action(self):
        u = self.username_var.get().strip()
        p = self.password_var.get().strip()
        if not u or not p:
            self.err_lbl.config(text="Username and password are required.")
            return
        users = load_users()
        if self.mode == "login":
            if u not in users or users[u]["pw"] != _hash(p):
                self.err_lbl.config(text="Invalid username or password.")
                return
            self.on_login(u)
        else:
            if len(u) < 3:
                self.err_lbl.config(text="Username must be at least 3 characters.")
                return
            if len(p) < 6:
                self.err_lbl.config(text="Password must be at least 6 characters.")
                return
            if u in users:
                self.err_lbl.config(text="Username already taken.")
                return
            users[u] = {
                "pw": _hash(p),
                "email": self.email_var.get().strip(),
                "joined": datetime.datetime.now().isoformat(),
            }
            save_users(users)
            self.on_login(u)


# ══════════════════════════════════════════════════════════════════════════════
#  QUIZ WINDOW
# ══════════════════════════════════════════════════════════════════════════════


class QuizWindow(tk.Toplevel):
    def __init__(self, master, username, theme, on_done):
        super().__init__(master)
        self.title("India Tourism Quiz")
        self.geometry("520x440")
        self.resizable(False, False)
        self.username = username
        self.T = theme
        self.on_done = on_done
        self.configure(bg=self.T["bg"])

        self.questions = random.sample(QUIZ_QUESTIONS, min(10, len(QUIZ_QUESTIONS)))
        self.idx = 0
        self.score = 0
        self.selected = tk.StringVar()
        self._build()
        self._load_question()

    def _build(self):
        tk.Label(
            self,
            text="🧠  India Tourism Quiz",
            font=("Helvetica", 15, "bold"),
            bg=self.T["header"],
            fg=self.T["header_fg"],
            pady=10,
        ).pack(fill="x")

        self.progress_lbl = tk.Label(
            self, font=("Helvetica", 10), bg=self.T["bg"], fg=self.T["muted"]
        )
        self.progress_lbl.pack(pady=(10, 0))

        self.q_lbl = tk.Label(
            self,
            wraplength=460,
            font=("Helvetica", 13),
            bg=self.T["bg"],
            fg=self.T["text"],
            justify="left",
            padx=20,
        )
        self.q_lbl.pack(pady=14, fill="x")

        self.opt_frame = tk.Frame(self, bg=self.T["bg"])
        self.opt_frame.pack(fill="x", padx=20)
        self.opt_btns = []

        self.feedback_lbl = tk.Label(
            self, text="", font=("Helvetica", 11, "bold"), bg=self.T["bg"]
        )
        self.feedback_lbl.pack(pady=6)

        self.next_btn = tk.Button(
            self,
            text="Next →",
            font=("Helvetica", 11),
            bg=self.T["accent"],
            fg="white",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._next,
            state="disabled",
        )
        self.next_btn.pack(pady=8)

    def _load_question(self):
        for b in self.opt_btns:
            b.destroy()
        self.opt_btns = []
        self.feedback_lbl.config(text="")
        self.next_btn.config(state="disabled")

        q = self.questions[self.idx]
        self.progress_lbl.config(
            text=f"Question {self.idx+1} of {len(self.questions)}  |  Score: {self.score}"
        )
        self.q_lbl.config(text=q["q"])
        opts = q["options"][:]
        random.shuffle(opts)
        for opt in opts:
            b = tk.Button(
                self.opt_frame,
                text=opt,
                font=("Helvetica", 11),
                bg=self.T["card"],
                fg=self.T["text"],
                relief="flat",
                padx=10,
                pady=6,
                cursor="hand2",
                anchor="w",
                bd=1,
                highlightbackground=self.T["border"],
                command=lambda o=opt: self._answer(o),
            )
            b.pack(fill="x", pady=3)
            self.opt_btns.append(b)

    def _answer(self, opt):
        for b in self.opt_btns:
            b.config(state="disabled")
        correct = self.questions[self.idx]["ans"]
        if opt == correct:
            self.score += 1
            self.feedback_lbl.config(text="✓ Correct!", fg="#1D9E75")
        else:
            self.feedback_lbl.config(text=f"✗ Wrong. Answer: {correct}", fg="#c0392b")
        for b in self.opt_btns:
            if b.cget("text") == correct:
                b.config(bg="#d4f0e7")
            elif b.cget("text") == opt and opt != correct:
                b.config(bg="#fde8e8")
        self.next_btn.config(
            state="normal",
            text="Next →" if self.idx < len(self.questions) - 1 else "See Results",
        )

    def _next(self):
        self.idx += 1
        if self.idx < len(self.questions):
            self._load_question()
        else:
            self._show_result()

    def _show_result(self):
        if self.username != "guest":
            rec = get_user_record(self.username)
            rec["quiz_scores"].append(
                {
                    "score": self.score,
                    "total": len(self.questions),
                    "date": datetime.datetime.now().strftime("%d %b %Y"),
                }
            )
            save_user_record(self.username, rec)
        for w in self.winfo_children():
            w.destroy()
        pct = int(self.score / len(self.questions) * 100)
        emoji = "🏆" if pct >= 80 else "👍" if pct >= 50 else "📚"
        tk.Label(self, text=emoji, font=("Helvetica", 50), bg=self.T["bg"]).pack(
            pady=(40, 8)
        )
        tk.Label(
            self,
            text=f"You scored {self.score} / {len(self.questions)}",
            font=("Helvetica", 18, "bold"),
            bg=self.T["bg"],
            fg=self.T["text"],
        ).pack()
        tk.Label(
            self,
            text=f"{pct}% correct",
            font=("Helvetica", 13),
            bg=self.T["bg"],
            fg=self.T["muted"],
        ).pack(pady=4)
        msg = (
            "Outstanding knowledge!"
            if pct >= 80
            else (
                "Good effort! Keep exploring."
                if pct >= 50
                else "Keep visiting states to learn more!"
            )
        )
        tk.Label(
            self, text=msg, font=("Helvetica", 12), bg=self.T["bg"], fg=self.T["accent"]
        ).pack(pady=8)
        tk.Button(
            self,
            text="Close",
            font=("Helvetica", 11),
            bg=self.T["accent"],
            fg="white",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=lambda: [self.destroy(), self.on_done()],
        ).pack(pady=14)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════


class TourismApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Incredible India — State Tourism Guide")
        self.root.geometry("1020x680")
        self.root.resizable(True, True)

        self.username = None
        self.theme_name = "light"
        self.T = THEMES["light"]
        self.current_state = None
        self.current_tab = "Overview"
        self.filtered_names = list(STATES.keys())
        self.tts_engine = None
        self.speaking = False

        self._show_auth()

    # ── Auth ──────────────────────────────────────────────────────────────────

    def _show_auth(self):
        self.root.configure(bg="#1a3d2b")
        for w in self.root.winfo_children():
            w.destroy()
        auth = AuthScreen(self.root, self._on_login)
        auth.pack(fill="both", expand=True)

    def _on_login(self, username):
        self.username = username
        for w in self.root.winfo_children():
            w.destroy()
        self._build_main()

    # ── Build main UI ─────────────────────────────────────────────────────────

    def _build_main(self):
        self.root.configure(bg=self.T["bg"])

        # ── Header ──
        hdr = tk.Frame(self.root, bg=self.T["header"], pady=10)
        hdr.pack(fill="x")
        hdr.columnconfigure(1, weight=1)

        tk.Label(
            hdr,
            text="🇮🇳  Incredible India — State Tourism Guide",
            font=("Helvetica", 16, "bold"),
            bg=self.T["header"],
            fg=self.T["header_fg"],
        ).grid(row=0, column=0, padx=16, sticky="w")

        # right side controls
        ctrl = tk.Frame(hdr, bg=self.T["header"])
        ctrl.grid(row=0, column=2, padx=12, sticky="e")

        user_lbl = "Guest" if self.username == "guest" else f"👤 {self.username}"
        tk.Label(
            ctrl,
            text=user_lbl,
            font=("Helvetica", 10),
            bg=self.T["header"],
            fg=self.T["header_fg"],
        ).pack(side="left", padx=6)

        tk.Button(
            ctrl,
            text="🌙 Dark" if self.theme_name == "light" else "☀️ Light",
            font=("Helvetica", 10),
            bg=self.T["accent2"],
            fg="white",
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            command=self._toggle_theme,
        ).pack(side="left", padx=4)

        tk.Button(
            ctrl,
            text="🧠 Quiz",
            font=("Helvetica", 10),
            bg=self.T["accent"],
            fg="white",
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            command=self._open_quiz,
        ).pack(side="left", padx=4)

        if self.username != "guest":
            tk.Button(
                ctrl,
                text="⭐ Favourites",
                font=("Helvetica", 10),
                bg="#f0a500",
                fg="white",
                relief="flat",
                padx=8,
                pady=3,
                cursor="hand2",
                command=self._show_favourites,
            ).pack(side="left", padx=4)

        tk.Button(
            ctrl,
            text="Logout",
            font=("Helvetica", 10),
            bg=self.T["danger"],
            fg="white",
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            command=self._show_auth,
        ).pack(side="left", padx=4)

        # ── Search bar ──
        sf = tk.Frame(self.root, bg=self.T["bg"], pady=8, padx=16)
        sf.pack(fill="x")
        tk.Label(sf, text="🔍", bg=self.T["bg"], font=("Helvetica", 12)).pack(
            side="left"
        )
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._filter_list())
        tk.Entry(
            sf,
            textvariable=self.search_var,
            font=("Helvetica", 11),
            relief="solid",
            bd=1,
            width=34,
            bg=self.T["panel"],
            fg=self.T["text"],
        ).pack(side="left", padx=8)
        tk.Label(
            sf,
            text="Search states, cuisine, places...",
            bg=self.T["bg"],
            fg=self.T["muted"],
            font=("Helvetica", 9),
        ).pack(side="left")

        # ── Main layout ──
        main = tk.Frame(self.root, bg=self.T["bg"])
        main.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        # Left — state list
        left = tk.Frame(main, bg=self.T["bg"])
        left.pack(side="left", fill="y")
        tk.Label(
            left,
            text=f"States ({len(STATES)})",
            font=("Helvetica", 12, "bold"),
            bg=self.T["bg"],
            fg=self.T["text"],
            anchor="w",
        ).pack(anchor="w", pady=(0, 6))
        lf = tk.Frame(left, bd=1, relief="solid", bg=self.T["panel"])
        lf.pack(fill="y", expand=True)
        sb = tk.Scrollbar(lf, orient="vertical")
        self.listbox = tk.Listbox(
            lf,
            yscrollcommand=sb.set,
            font=("Helvetica", 12),
            width=24,
            activestyle="none",
            selectbackground=self.T["list_sel"],
            selectforeground="white",
            bd=0,
            highlightthickness=0,
            bg=self.T["panel"],
            fg=self.T["text"],
        )
        sb.config(command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self._populate_list(list(STATES.keys()))

        # Right — detail
        right = tk.Frame(main, bg=self.T["bg"], padx=14)
        right.pack(side="left", fill="both", expand=True)

        # State title row
        title_row = tk.Frame(right, bg=self.T["bg"])
        title_row.pack(fill="x", pady=(0, 2))

        self.title_lbl = tk.Label(
            title_row,
            text="← Select a state to begin",
            font=("Helvetica", 16, "bold"),
            bg=self.T["bg"],
            fg=self.T["text"],
            anchor="w",
            wraplength=480,
            justify="left",
        )
        self.title_lbl.pack(side="left")

        self.fav_btn = tk.Button(
            title_row,
            text="☆ Add to Favourites",
            font=("Helvetica", 10),
            bg=self.T["bg"],
            fg=self.T["muted"],
            relief="flat",
            cursor="hand2",
            command=self._toggle_favourite,
        )
        self.fav_btn.pack(side="right", padx=4)

        self.visited_btn = tk.Button(
            title_row,
            text="✓ Mark Visited",
            font=("Helvetica", 10),
            bg=self.T["bg"],
            fg=self.T["muted"],
            relief="flat",
            cursor="hand2",
            command=self._toggle_visited,
        )
        self.visited_btn.pack(side="right", padx=4)

        self.tag_lbl = tk.Label(
            right,
            text="",
            font=("Helvetica", 11, "italic"),
            bg=self.T["bg"],
            fg=self.T["accent"],
            anchor="w",
        )
        self.tag_lbl.pack(anchor="w", pady=(0, 8))

        # Tab bar
        self.tab_frame = tk.Frame(right, bg=self.T["bg"])
        self.tab_frame.pack(fill="x", pady=(0, 6))
        self.tab_btns = {}
        for t in TABS:
            btn = tk.Button(
                self.tab_frame,
                text=t,
                font=("Helvetica", 10),
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
                bg=self.T["card"],
                fg=self.T["muted"],
                cursor="hand2",
                command=lambda tab=t: self._switch_tab(tab),
            )
            btn.pack(side="left", padx=2)
            self.tab_btns[t] = btn

        # Text area
        tf = tk.Frame(right, bd=1, relief="solid")
        tf.pack(fill="both", expand=True)
        self.text_area = scrolledtext.ScrolledText(
            tf,
            wrap="word",
            font=("Helvetica", 12),
            relief="flat",
            bg=self.T["panel"],
            fg=self.T["text"],
            insertbackground=self.T["text"],
            padx=14,
            pady=12,
            state="disabled",
        )
        self.text_area.pack(fill="both", expand=True)

        # Bottom controls
        bf = tk.Frame(right, bg=self.T["bg"], pady=8)
        bf.pack(fill="x")
        self.speak_btn = tk.Button(
            bf,
            text="🔊  Read Aloud",
            font=("Helvetica", 11),
            bg=self.T["accent"],
            fg="white",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._speak,
            state="disabled",
        )
        self.speak_btn.pack(side="left")
        self.stop_btn = tk.Button(
            bf,
            text="⏹  Stop",
            font=("Helvetica", 11),
            bg=self.T["danger"],
            fg="white",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._stop_speaking,
            state="disabled",
        )
        self.stop_btn.pack(side="left", padx=8)

        # Random state button
        tk.Button(
            bf,
            text="🎲 Random State",
            font=("Helvetica", 11),
            bg="#7c3aed",
            fg="white",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._random_state,
        ).pack(side="right", padx=4)

        if not TTS_AVAILABLE:
            tk.Label(
                bf,
                text="Install pyttsx3 for TTS",
                font=("Helvetica", 9),
                bg=self.T["bg"],
                fg=self.T["muted"],
            ).pack(side="left")

        # Status bar
        self.status_var = tk.StringVar(value="Welcome! Select a state to explore.")
        status = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Helvetica", 9),
            bg=self.T["header"],
            fg=self.T["header_fg"],
            anchor="w",
            padx=10,
            pady=3,
        )
        status.pack(fill="x", side="bottom")

    # ── List helpers ──────────────────────────────────────────────────────────

    def _populate_list(self, names):
        self.listbox.delete(0, "end")
        rec = (
            get_user_record(self.username)
            if self.username != "guest"
            else {"favourites": [], "visited": []}
        )
        for name in names:
            s = STATES[name]
            prefix = ""
            if name in rec.get("favourites", []):
                prefix += "⭐"
            if name in rec.get("visited", []):
                prefix += "✓"
            label = f"  {s['emoji']}  {prefix+' ' if prefix else ''}{name}"
            self.listbox.insert("end", label)

    def _filter_list(self):
        q = self.search_var.get().lower()
        self.filtered_names = [
            n
            for n in STATES
            if q in n.lower()
            or q in STATES[n]["tag"].lower()
            or any(q in STATES[n][t].lower() for t in TABS)
        ]
        self._populate_list(self.filtered_names)

    # ── State display ─────────────────────────────────────────────────────────

    def _on_select(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        name = self.filtered_names[sel[0]]
        self._show_state(name)

    def _show_state(self, name):
        self._stop_speaking()
        self.current_state = name
        s = STATES[name]
        self.title_lbl.config(text=f"{s['emoji']}  {name}")
        self.tag_lbl.config(text=s["tag"])
        self.current_tab = "Overview"
        self._highlight_tab("Overview")
        self._render_tab("Overview")
        self._refresh_action_btns()
        self.status_var.set(f"Exploring {name} — {s['tag']}")
        if TTS_AVAILABLE:
            self.speak_btn.config(state="normal")

    def _switch_tab(self, tab):
        self.current_tab = tab
        self._highlight_tab(tab)
        self._render_tab(tab)

    def _highlight_tab(self, active):
        for t, btn in self.tab_btns.items():
            if t == active:
                btn.config(bg=self.T["accent"], fg="white")
            else:
                btn.config(bg=self.T["card"], fg=self.T["muted"])

    def _render_tab(self, tab):
        if not self.current_state:
            return
        content = STATES[self.current_state].get(tab, "")
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", content)
        self.text_area.config(state="disabled")

    # ── Favourites & Visited ──────────────────────────────────────────────────

    def _refresh_action_btns(self):
        if not self.current_state or self.username == "guest":
            self.fav_btn.config(text="☆ Add to Favourites", fg=self.T["muted"])
            self.visited_btn.config(text="✓ Mark Visited", fg=self.T["muted"])
            return
        rec = get_user_record(self.username)
        if self.current_state in rec.get("favourites", []):
            self.fav_btn.config(text="★ Remove Favourite", fg="#f0a500")
        else:
            self.fav_btn.config(text="☆ Add to Favourites", fg=self.T["muted"])
        if self.current_state in rec.get("visited", []):
            self.visited_btn.config(text="✓ Visited!", fg="#1D9E75")
        else:
            self.visited_btn.config(text="○ Mark Visited", fg=self.T["muted"])

    def _toggle_favourite(self):
        if self.username == "guest":
            messagebox.showinfo("Login Required", "Please login to save favourites.")
            return
        if not self.current_state:
            return
        rec = get_user_record(self.username)
        favs = rec.get("favourites", [])
        if self.current_state in favs:
            favs.remove(self.current_state)
            self.status_var.set(f"Removed {self.current_state} from favourites.")
        else:
            favs.append(self.current_state)
            self.status_var.set(f"Added {self.current_state} to favourites! ⭐")
        rec["favourites"] = favs
        save_user_record(self.username, rec)
        self._refresh_action_btns()
        self._populate_list(self.filtered_names)

    def _toggle_visited(self):
        if self.username == "guest":
            messagebox.showinfo(
                "Login Required", "Please login to track visited states."
            )
            return
        if not self.current_state:
            return
        rec = get_user_record(self.username)
        visited = rec.get("visited", [])
        if self.current_state in visited:
            visited.remove(self.current_state)
            self.status_var.set(f"Unmarked {self.current_state} as visited.")
        else:
            visited.append(self.current_state)
            self.status_var.set(f"Marked {self.current_state} as visited! ✓")
        rec["visited"] = visited
        save_user_record(self.username, rec)
        self._refresh_action_btns()
        self._populate_list(self.filtered_names)

    def _show_favourites(self):
        rec = get_user_record(self.username)
        favs = rec.get("favourites", [])
        visited = rec.get("visited", [])
        scores = rec.get("quiz_scores", [])
        win = tk.Toplevel(self.root)
        win.title("My Profile")
        win.geometry("420x460")
        win.configure(bg=self.T["bg"])
        tk.Label(
            win,
            text=f"👤  {self.username}'s Profile",
            font=("Helvetica", 14, "bold"),
            bg=self.T["header"],
            fg=self.T["header_fg"],
            pady=10,
        ).pack(fill="x")

        frm = tk.Frame(win, bg=self.T["bg"], padx=20, pady=14)
        frm.pack(fill="both", expand=True)

        tk.Label(
            frm,
            text=f"⭐ Favourite States ({len(favs)})",
            font=("Helvetica", 11, "bold"),
            bg=self.T["bg"],
            fg=self.T["text"],
        ).pack(anchor="w")
        tk.Label(
            frm,
            text=", ".join(favs) if favs else "None yet",
            font=("Helvetica", 10),
            bg=self.T["bg"],
            fg=self.T["muted"],
            wraplength=360,
            justify="left",
        ).pack(anchor="w", pady=(2, 10))

        tk.Label(
            frm,
            text=f"✓ Visited States ({len(visited)} / {len(STATES)})",
            font=("Helvetica", 11, "bold"),
            bg=self.T["bg"],
            fg=self.T["text"],
        ).pack(anchor="w")
        tk.Label(
            frm,
            text=", ".join(visited) if visited else "None yet",
            font=("Helvetica", 10),
            bg=self.T["bg"],
            fg=self.T["muted"],
            wraplength=360,
            justify="left",
        ).pack(anchor="w", pady=(2, 10))

        tk.Label(
            frm,
            text=f"🧠 Quiz History ({len(scores)} attempts)",
            font=("Helvetica", 11, "bold"),
            bg=self.T["bg"],
            fg=self.T["text"],
        ).pack(anchor="w")
        if scores:
            for s in scores[-5:]:
                tk.Label(
                    frm,
                    text=f"  {s['date']} — {s['score']}/{s['total']} ({int(s['score']/s['total']*100)}%)",
                    font=("Helvetica", 10),
                    bg=self.T["bg"],
                    fg=self.T["muted"],
                ).pack(anchor="w")
        else:
            tk.Label(
                frm,
                text="No quiz attempts yet",
                font=("Helvetica", 10),
                bg=self.T["bg"],
                fg=self.T["muted"],
            ).pack(anchor="w")

        pct = int(len(visited) / len(STATES) * 100)
        tk.Label(
            frm,
            text=f"\n🗺️  You've explored {pct}% of India!",
            font=("Helvetica", 12, "bold"),
            bg=self.T["bg"],
            fg=self.T["accent"],
        ).pack(anchor="w")

    # ── Theme toggle ──────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self.theme_name = "dark" if self.theme_name == "light" else "light"
        self.T = THEMES[self.theme_name]
        for w in self.root.winfo_children():
            w.destroy()
        self._build_main()
        if self.current_state:
            self._show_state(self.current_state)

    # ── Quiz ──────────────────────────────────────────────────────────────────

    def _open_quiz(self):
        QuizWindow(
            self.root,
            self.username,
            self.T,
            on_done=lambda: (
                self._show_favourites() if self.username != "guest" else None
            ),
        )

    # ── Random state ─────────────────────────────────────────────────────────

    def _random_state(self):
        name = random.choice(list(STATES.keys()))
        self._show_state(name)
        # Also select in listbox
        if name in self.filtered_names:
            idx = self.filtered_names.index(name)
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(idx)
            self.listbox.see(idx)

    # ── TTS ───────────────────────────────────────────────────────────────────

    def _speak(self):
        if not self.current_state or self.speaking or not TTS_AVAILABLE:
            return
        self.speaking = True
        self.speak_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        text = STATES[self.current_state].get(self.current_tab, "")
        threading.Thread(target=self._tts_thread, args=(text,), daemon=True).start()

    def _tts_thread(self, text):
        try:
            engine = pyttsx3.init()
            self.tts_engine = engine
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass
        finally:
            self.speaking = False
            self.tts_engine = None
            self.root.after(0, self._reset_speak_btn)

    def _stop_speaking(self):
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except Exception:
                pass
        self.speaking = False
        self._reset_speak_btn()

    def _reset_speak_btn(self):
        if TTS_AVAILABLE and self.current_state:
            self.speak_btn.config(state="normal")
        self.stop_btn.config(state="disabled")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    TourismApp(root)
    root.mainloop()
