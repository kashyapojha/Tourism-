"""
Incredible India — Flask Web Application
"""

import os
import json
import hashlib
import random
import datetime
import io
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, flash, send_file
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "data", "users.json")
DATA_FILE  = os.path.join(BASE_DIR, "data", "userdata.json")
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# ── State name constants (resolves SonarCloud duplicate-literal warnings) ─
STATE_HIMACHAL   = "Himachal Pradesh"
STATE_ANDHRA     = "Andhra Pradesh"



# ── Helpers ───────────────────────────────────────────────────────────────────
def _load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default

def _save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def get_user_record(username):
    ud = _load(DATA_FILE, {})
    if username not in ud:
        ud[username] = {"favourites": [], "visited": [], "quiz_scores": []}
        _save(DATA_FILE, ud)
    return ud[username]

def save_user_record(username, record):
    ud = _load(DATA_FILE, {})
    ud[username] = record
    _save(DATA_FILE, ud)

# ── State data ─────────────────────────────────────────────────────────────────
STATES = {
    "Rajasthan": {
        "emoji": "🏯", "tag": "Forts & Deserts", "color": "#c0392b",
        "overview": "Rajasthan — the Land of Kings — is India's largest state (342,239 sq km), famed for massive forts, colorful culture, golden deserts and royal palaces. It greets visitors with 'Padhaaro Maare Desh.' Folk dance, music, turbans and camels create a living spectacle unlike anywhere else.",
        "food": ["Dal Baati Churma", "Laal Maas", "Ghewar", "Ker Sangri", "Bajre ki Khichdi", "Pyaaz Kachori", "Gatte ki Sabzi"],
        "food_note": "Rajasthani cuisine is rich, spicy and designed for desert survival. Dal Baati Churma is the state's most iconic dish. Laal Maas is a fiery red mutton curry. Ghewar is a honeycomb-shaped festival dessert.",
        "places": ["Amber Fort, Jaipur", "Hawa Mahal", "Jaisalmer Fort", "Mehrangarh Fort", "Udaipur City Palace", "Ranthambore NP", "Pushkar Lake"],
        "places_note": "Jaipur — the Pink City — is the crown jewel. Jaisalmer's golden fort rises from the Thar Desert. Udaipur, the City of Lakes, is among India's most romantic cities.",
        "best_time": "October to March — cool and pleasant. Avoid May–June (45°C+). Pushkar Camel Fair (November) and Jaipur Literature Festival (January) are unmissable.",
        "facts": ["India's largest state by area", "Jaipur was the world's first planned city (1727 AD)", "Thar Desert covers 60% of Rajasthan", "More forts and palaces than any other Indian state", "Chittorgarh is the only UNESCO hill fort in India"],
    },
    "Kerala": {
        "emoji": "🌴", "tag": "Backwaters & Beaches", "color": "#27ae60",
        "overview": "Kerala — 'God's Own Country' — is a 38,863 sq km treasure of backwaters, tea gardens, spice plantations and tropical beaches. Named one of the ten paradises of the world by National Geographic Traveler, it tops India's Human Development Index.",
        "food": ["Sadya (banana leaf feast)", "Appam with Stew", "Fish Molee", "Karimeen Pollichathu", "Puttu & Kadala Curry", "Kerala Prawn Curry", "Payasam"],
        "food_note": "Kerala cuisine blends coconut, spices and seafood. The Sadya — a 20+ dish vegetarian feast on banana leaf — is served at Onam. Karimeen Pollichathu is a pearl spot fish wrapped in banana leaf.",
        "places": ["Alleppey Backwaters", "Munnar Tea Gardens", "Periyar WS", "Kovalam Beach", "Varkala Cliff", "Fort Kochi", "Wayanad"],
        "places_note": "Alleppey is the 'Venice of the East' for its houseboat cruises. Munnar's emerald tea gardens are breathtaking. Fort Kochi blends Portuguese, Dutch and British colonial heritage.",
        "best_time": "September to March (peak). Onam (Aug/Sep): snake boat races and feasts. Monsoon (June–Aug) is ideal for Ayurveda retreats.",
        "facts": ["100% literacy rate — highest in India", "Kalaripayattu (world's oldest martial art) originated here", "Produces 97% of India's rubber", "Named 'God's Own Country' by tourism board", "Kathakali is one of India's 8 classical dance forms"],
    },
    "Gujarat": {
        "emoji": "🦁", "tag": "Desert & Lions", "color": "#e67e22",
        "overview": "Gujarat is the only home of pure Asiatic Lions, houses the world's largest salt desert (Rann of Kutch), and is the birthplace of Mahatma Gandhi and Sardar Vallabhbhai Patel. Its coastline stretches over 1,600 km — the longest of any Indian state.",
        "food": ["Dhokla", "Thepla", "Fafda-Jalebi", "Undhiyu", "Khandvi", "Gujarati Thali", "Mohanthal"],
        "food_note": "Gujarati cuisine is predominantly vegetarian, subtly sweet and balanced. The Gujarati Thali covers every taste. Undhiyu — mixed vegetables slow-cooked underground — is a winter specialty.",
        "places": ["Gir National Park", "Rann of Kutch", "Dwarka Temple", "Somnath Temple", "Statue of Unity", "Rani ki Vav", "Sabarmati Ashram"],
        "places_note": "The Rann of Kutch is a dazzling white salt desert in winter. The Statue of Unity at 182m is the world's tallest. Rani ki Vav is a UNESCO-listed stepwell of breathtaking intricacy.",
        "best_time": "October to March. Rann Utsav (November–February) is a cultural highlight. Navratri Garba is a UNESCO Intangible Cultural Heritage.",
        "facts": ["Longest coastline in India — over 1,600 km", "Only home of wild Asiatic Lions", "Statue of Unity is the world's tallest at 182m", "Surat processes 90% of the world's diamonds", "First Indian state to prohibit alcohol (1960)"],
    },
    "Goa": {
        "emoji": "🏖️", "tag": "Beaches & Nightlife", "color": "#3498db",
        "overview": "India's smallest state by area, Goa is a former Portuguese colony that attracts 8+ million tourists annually. Its unique Indo-Portuguese culture, vibrant nightlife, stunning churches and golden beaches make it visibly different from the rest of India.",
        "food": ["Fish Curry Rice", "Prawn Balchão", "Bebinca", "Xacuti", "Chouriço", "Feni", "Pork Vindaloo"],
        "food_note": "Goan food marries Indian spices with Portuguese techniques. Fish Curry Rice is the everyday staple. Bebinca is the layered coconut queen of Goan desserts. Feni — distilled from cashew apples — is Goa's beloved local spirit.",
        "places": ["Calangute & Baga Beach", "Palolem Beach", "Old Goa Churches (UNESCO)", "Dudhsagar Falls", "Fort Aguada", "Anjuna Flea Market", "Chapora Fort"],
        "places_note": "Palolem is Goa's most picturesque crescent beach. Bom Jesus Basilica is a UNESCO World Heritage Site. Dudhsagar Falls is one of India's tallest waterfalls.",
        "best_time": "November to February (peak). Goa Carnival (Feb/Mar) is a riot of colour. Monsoon brings lush greenery but beach shacks mostly close.",
        "facts": ["Highest per capita income among Indian states", "Two UNESCO World Heritage Sites", "Feni is the only Indian spirit with a GI tag", "Under Portuguese rule for 451 years (1510–1961)", "30+ beaches — one for every day of the month"],
    },
    "Jammu & Kashmir": {
        "emoji": "🏔️", "tag": "Paradise Valley", "color": "#8e44ad",
        "overview": "Kashmir — 'Paradise on Earth' — is a tapestry of snow-capped peaks, serene lakes, saffron fields and Mughal gardens. The valley sits at ~1,600m elevation, flanked by the Great Himalayas and Pir Panjal range.",
        "food": ["Rogan Josh", "Wazwan (36-course feast)", "Yakhni", "Dum Aloo", "Kahwa (saffron tea)", "Modur Pulao", "Seekh Kabab"],
        "food_note": "Kashmiri cuisine centres on slow-cooked meats in yoghurt and spice gravies. The Wazwan is a ceremonial 36-course feast — the ultimate expression of Kashmiri hospitality. Kahwa — saffron, cardamom and almond tea — is the valley's warm embrace.",
        "places": ["Dal Lake & Shikara Rides", "Gulmarg (skiing)", "Pahalgam Valley", "Sonamarg Glacier", "Leh Palace", "Pangong Lake", "Vaishno Devi Temple"],
        "places_note": "Dal Lake with floating gardens and houseboats is Kashmir's most iconic image. Gulmarg has Asia's highest gondola. Pangong Lake changes colour from blue to green through the day.",
        "best_time": "Apr–Jun & Sep–Oct for the valley. Dec–Feb for skiing at Gulmarg. Ladakh: June–September.",
        "facts": ["Kashmir produces 90%+ of India's saffron", "Dal Lake has 50,000+ people living on houseboats", "Gulmarg has Asia's highest cable car", "Pangong Lake sits at 4,350m altitude", "Pashmina wool is among the world's finest textiles"],
    },
    "Karnataka": {
        "emoji": "🏛️", "tag": "Silk & Sandalwood", "color": "#d35400",
        "overview": "Karnataka — the land of sandalwood, silks and spices — blends ancient temple towns, the IT metropolis of Bengaluru, misty hill stations and pristine coastline. It produces 70% of India's coffee and the finest Mulberry silk in the world.",
        "food": ["Bisi Bele Bath", "Masala Dosa (origin)", "Ragi Mudde", "Coorg Pandi Curry", "Mysore Pak", "Neer Dosa", "Mangalorean Fish Curry"],
        "food_note": "Udupi gave the world the masala dosa. Mysore Pak was invented in the Mysore royal kitchen. Coorg's Pandi (pork) Curry is a bold tribal specialty. Bisi Bele Bath is a comforting one-pot classic.",
        "places": ["Hampi (UNESCO)", "Mysore Palace", "Coorg (Kodagu)", "Jog Falls", "Badami Caves", "Chikmagalur Coffee Estates", "Gokarna Beach"],
        "places_note": "Hampi — the ruined Vijayanagara capital — is a surreal boulder landscape. Jog Falls is India's second highest waterfall. Gokarna is a spiritual, quieter alternative to Goa.",
        "best_time": "October to March. Mysore Dasara (October) — 100,000 lit bulbs illuminate the palace.",
        "facts": ["Karnataka produces 70% of India's coffee", "Bengaluru is Asia's fastest growing tech city", "Hampi was the 2nd largest city in the world in the 14th century", "ISRO headquarters is in Bengaluru", "Has the most UNESCO sites in South India"],
    },
    "Maharashtra": {
        "emoji": "🏰", "tag": "Forts & Festivals", "color": "#f39c12",
        "overview": "Maharashtra — India's wealthiest state — blends Maratha glory, Bollywood glamour, Konkan coastline and Mumbai's financial might. Shivaji Maharaj built 300+ forts across the Western Ghats that remain popular trekking destinations.",
        "food": ["Vada Pav", "Misal Pav", "Puran Poli", "Modak", "Kolhapuri Chicken", "Sol Kadhi", "Thali Peeth"],
        "food_note": "Vada Pav — deep-fried potato dumpling in a bread roll — is Mumbai's beloved street food. Modak — steamed rice dumpling with coconut and jaggery — is Lord Ganesha's favourite made by millions at Ganesh Chaturthi.",
        "places": ["Ajanta & Ellora (UNESCO)", "Gateway of India", "Lonavala & Mahabaleshwar", "Shirdi", "Daulatabad Fort", "Nashik", "Tadoba Tiger Reserve"],
        "places_note": "Ajanta and Ellora cave temples span 2nd century BC to 10th century AD. Nashik is India's wine capital and hosts the Kumbh Mela.",
        "best_time": "October to February. Ganesh Chaturthi (Aug/Sep) — Mumbai celebrates for 11 days with processions and immersion of thousands of idols.",
        "facts": ["Maharashtra is India's wealthiest state by GDP", "Mumbai produces 1,000+ Bollywood films per year", "Ajanta cave paintings are 2,000 years old", "More Shiva temples than any other state", "Wari pilgrimage to Pandharpur draws 10 million annually"],
    },
    "Punjab": {
        "emoji": "⚔️", "tag": "Five Rivers & Sikhs", "color": "#16a085",
        "overview": "Punjab — the land of five rivers — is India's agricultural powerhouse, producing 40–50% of its wheat and rice. It is the spiritual home of Sikhism. The Golden Temple in Amritsar is reportedly the most visited place in India — surpassing even the Taj Mahal.",
        "food": ["Makki di Roti & Sarson da Saag", "Amritsari Kulcha", "Butter Chicken", "Chole Bhature", "Lassi", "Dal Makhani", "Pindi Chhole"],
        "food_note": "Butter Chicken and Dal Makhani — now global sensations — were born in Punjab. The winter meal of Makki di Roti and Sarson da Saag with white butter is the soul of rural Punjab.",
        "places": ["Golden Temple, Amritsar", "Jallianwala Bagh", "Wagah Border Ceremony", "Anandpur Sahib", "Maharaja Ranjit Singh Museum", "Gobindgarh Fort"],
        "places_note": "The Golden Temple — covered in 750 kg of gold — feeds 100,000 people daily for free. The Wagah Border sunset ceremony is a spectacular display of nationalism.",
        "best_time": "October to March. Lohri (January) and Baisakhi (April 13) are celebrated with Bhangra dancing and bonfires.",
        "facts": ["Golden Temple feeds 100,000 people free daily — world's largest free kitchen", "Punjab contributes 40–50% of India's wheat", "Butter Chicken was invented by a Punjabi migrant", "Bhangra dance is now a global phenomenon", "One of the highest tractor densities in the world"],
    },
    "Himachal Pradesh": {
        "emoji": "❄️", "tag": "Snow & Temples", "color": "#2980b9",
        "overview": "Himachal Pradesh — 'Land of Snow-capped Mountains' — is India's premier hill state. From apple orchards and cedar forests to alpine meadows and glaciated peaks, it is known as 'Dev Bhoomi' (Land of Gods) and India's adventure capital.",
        "food": ["Dham (feast)", "Siddu (steamed bread)", "Chha Gosht", "Babru", "Aktori (buckwheat pancake)", "Madra", "Kullu Trout"],
        "food_note": "The Dham is a traditional feast always cooked by Brahmin cooks. Siddu — steamed bread stuffed with poppy seeds or walnuts with ghee — is deeply comforting in winter. Kullu Trout from Himalayan streams is a delicacy.",
        "places": ["Shimla", "Manali & Rohtang Pass", "Dharamsala & McLeodGanj", "Spiti Valley", "Kullu Valley", "Kasol", "Khajjiar"],
        "places_note": "Shimla was the summer capital of British India. Spiti Valley is a remote high-altitude cold desert. McLeodGanj is the Dalai Lama's residence and a vibrant Tibetan cultural centre.",
        "best_time": "March–June for hill stations. December–February for skiing at Solang Valley. Spiti is accessible only May–October.",
        "facts": ["Himachal produces 25% of India's apples", "Snow leopards inhabit Kugti Wildlife Sanctuary", "Khajjiar is known as India's Mini Switzerland", "Shimla was the summer capital of British India", "Over 2,000 temples and monasteries"],
    },
    "West Bengal": {
        "emoji": "🍵", "tag": "Darjeeling & Culture", "color": "#1abc9c",
        "overview": "West Bengal is India's cultural capital — home of Tagore, Satyajit Ray and Amartya Sen. It stretches from Darjeeling's Himalayan foothills to the Sundarbans mangrove delta. Kolkata's Durga Puja is a UNESCO Intangible Cultural Heritage.",
        "food": ["Rosogolla", "Macher Jhol", "Shorshe Ilish", "Luchi & Aloor Dom", "Mishti Doi", "Kolkata Biryani", "Puchka"],
        "food_note": "Bengali cuisine is built around fish, mustard oil and milk-based sweets. Ilish (hilsa) is worshipped as a delicacy. Kolkata's puchka (pani puri) is considered the best in India.",
        "places": ["Darjeeling (toy train + tea)", "Sundarbans NP", "Victoria Memorial", "Howrah Bridge", "Bishnupur Temples", "Digha Beach", "Hazarduari Palace"],
        "places_note": "The Sundarbans is the world's largest mangrove delta. The Darjeeling Himalayan Railway toy train is a UNESCO World Heritage Site.",
        "best_time": "October to March. Durga Puja (October) transforms Kolkata into an open-air art gallery with spectacular pandals.",
        "facts": ["Durga Puja is a UNESCO Intangible Cultural Heritage", "Sundarbans has the world's largest tiger reserve", "West Bengal produces 25% of India's rice", "Howrah Bridge has no nuts and bolts — only rivets", "Darjeeling tea holds a GI tag"],
    },
    "Uttar Pradesh": {
        "emoji": "🕌", "tag": "Taj Mahal & Heritage", "color": "#e74c3c",
        "overview": "Uttar Pradesh is home to the Taj Mahal and Varanasi — one of the oldest continuously inhabited cities on earth. It is the origin of both Buddhism and Jainism and India's most populous state.",
        "food": ["Lucknowi Dum Biryani", "Tunday Kabab", "Petha (Agra)", "Banarasi Paan", "Malai Makhan", "Bedai Sabzi", "Tehri"],
        "food_note": "Lucknow's Dum Biryani and Tunday Kabab are internationally famous. Agra's Petha — a translucent sweet from white pumpkin — is a must-buy souvenir. Banarasi Paan is as much ritual as snack.",
        "places": ["Taj Mahal, Agra", "Varanasi Ghats", "Agra Fort", "Fatehpur Sikri", "Sarnath", "Vrindavan & Mathura", "Lucknow Bara Imambara"],
        "places_note": "The Taj Mahal is a UNESCO World Heritage Site. Varanasi's ghats at sunrise are profoundly spiritual. Fatehpur Sikri is a ghost Mughal city frozen in the 16th century.",
        "best_time": "October to March. Full moon at the Taj Mahal is a once-in-a-lifetime experience. Kumbh Mela at Prayagraj is the world's largest human gathering.",
        "facts": ["The Taj Mahal took 22 years and 20,000 workers to build", "Varanasi is one of the world's oldest cities (3,000+ years)", "Buddha delivered his first sermon at Sarnath in UP", "UP produces the most sugarcane in India", "Lucknow is famous for chikankari embroidery"],
    },
    "Assam": {
        "emoji": "🦏", "tag": "Rhinos & Brahmaputra", "color": "#27ae60",
        "overview": "Assam — the Gateway to North-East India — has five National Parks and 18 Wildlife Sanctuaries. The Brahmaputra River — considered male in Hindu tradition — is the state's lifeline. Assam produces 55% of India's tea.",
        "food": ["Masor Tenga", "Duck Meat Curry", "Khar", "Pitha (rice cake)", "Bamboo Shoot Pickle", "Jolpan", "Assam Laksa"],
        "food_note": "Assamese cuisine is light and minimal in spices. Khar — an alkaline preparation from banana peels — is uniquely Assamese. Pitha rice cakes are made in dozens of varieties, especially at Bihu.",
        "places": ["Kaziranga NP (UNESCO)", "Majuli River Island", "Kamakhya Temple", "Manas NP", "Sivasagar", "Haflong", "Pobitora WS"],
        "places_note": "Kaziranga has two-thirds of the world's one-horned rhinos. Majuli is the world's largest river island. Kamakhya is one of the 51 Shakti Peethas.",
        "best_time": "November to April. Bihu (April) is Assam's most joyous festival — the Assamese New Year with dance, music and feasts.",
        "facts": ["Produces 55% of India's total tea", "Kaziranga has 70% of the world's one-horned rhinos", "Majuli is the world's largest river island", "The Brahmaputra crosses the Himalayas — one of only three rivers to do so", "Home to the largest population of wild water buffalo"],
    },
    "Bihar": {
        "emoji": "🕉️", "tag": "Buddhist Circuit", "color": "#8e44ad",
        "overview": "Bihar — from 'Vihara' (monastery) — was the cradle of Buddhism and Jainism, the birthplace of India's first empire (Maurya), and home to Nalanda, the world's first residential university. The Buddha attained enlightenment at Bodh Gaya.",
        "food": ["Litti Chokha", "Sattu Paratha", "Dal Pitha", "Makhana Kheer", "Tilkut", "Chura Dahi", "Khaja"],
        "food_note": "Litti Chokha — roasted wheat balls stuffed with sattu served with charred brinjal — is Bihar's most iconic dish. Bihar produces 90% of the world's makhana (fox nuts).",
        "places": ["Bodh Gaya", "Nalanda ruins", "Rajgir", "Vaishali", "Mahabodhi Temple (UNESCO)", "Patna Sahib Gurudwara", "Valmiki NP"],
        "places_note": "The Mahabodhi Temple is UNESCO-listed. The Bodhi tree is a direct descendant of the tree under which the Buddha attained enlightenment.",
        "best_time": "October to March. Chhath Puja (Oct/Nov) — celebrated on riverbanks at sunrise and sunset — is Bihar's most sacred festival.",
        "facts": ["Nalanda was the world's first residential university", "Bodh Gaya is one of Buddhism's four holiest sites", "Bihar produces 90% of the world's makhana", "Chandragupta Maurya founded India's first empire here", "Vaishali is considered the world's first republic (6th century BC)"],
    },
    "Madhya Pradesh": {
        "emoji": "🐯", "tag": "Tigers & Temples", "color": "#e67e22",
        "overview": "Madhya Pradesh — 'Heart of India' — has more UNESCO World Heritage Sites than any other Indian state and more tiger reserves than any other state. The Narmada River flows entirely through MP.",
        "food": ["Dal Bafla", "Poha Jalebi (Indore)", "Bhutte ki Kees", "Chakki ki Shaak", "Mawa Bati", "Sabudana Khichdi", "Shikanji"],
        "food_note": "Indore's food scene is legendary — Sarafa Bazaar and Chappan Dukan are famous food streets. Poha-Jalebi is Indore's signature breakfast loved all over India.",
        "places": ["Khajuraho (UNESCO)", "Sanchi Stupa (UNESCO)", "Bhimbetka (UNESCO)", "Kanha Tiger Reserve", "Bandhavgarh NP", "Pachmarhi", "Omkareshwar"],
        "places_note": "Khajuraho's 10th-century temples are among the world's finest medieval Indian art. Bandhavgarh has the highest density of tigers in India.",
        "best_time": "October to March. Tiger sighting is best in April–June. Khajuraho Dance Festival (February) is a classical arts extravaganza.",
        "facts": ["3 UNESCO World Heritage Sites — more than any other state", "Bandhavgarh has world's highest density of Bengal tigers", "MP has the most tiger reserves in India (7 reserves)", "Bhimbetka cave paintings are 30,000 years old", "The Narmada River flows 1,077 km entirely through MP"],
    },
    "Andhra Pradesh": {
        "emoji": "🏺", "tag": "Temples & Coastline", "color": "#c0392b",
        "overview": "Andhra Pradesh is the land of spices, temples and the world's most visited pilgrimage site — Tirupati's Venkateswara Temple. It has the longest eastern coastline in India and rich Buddhist heritage from the Amaravati civilisation.",
        "food": ["Pesarattu", "Gongura Mutton", "Pulihora", "Bobbatlu", "Kodi Pulusu", "Chegodilu", "Hyderabadi Biryani"],
        "food_note": "Andhra cuisine is arguably the spiciest in India. Gongura (sorrel leaf) is unique to AP. Pesarattu — a green moong dal crepe — is the classic breakfast.",
        "places": ["Tirupati Temple", "Araku Valley", "Borra Caves", "Visakhapatnam Beach", "Amaravati Stupa", "Nagarjunasagar Dam", "Lepakshi Temple"],
        "places_note": "Tirupati is the world's richest and most visited religious site. Araku Valley is accessible by one of India's most scenic train journeys.",
        "best_time": "October to March. Ugadi (Telugu New Year, March/April) and Sankranti (January) are the state's biggest festivals.",
        "facts": ["Tirupati earns over ₹650 crore annually — world's richest temple", "AP has the longest eastern coastline in India", "Kuchipudi classical dance originated in AP", "The state produces the most chillies in India", "AP was the first state to implement e-governance in India"],
    },
    "Nagaland": {
        "emoji": "🦅", "tag": "Hornbill Festival", "color": "#16a085",
        "overview": "Nagaland — 'Land of the Nagas' — has 16 major tribes, each with distinct languages, dress, food and traditions. The annual Hornbill Festival is one of Asia's most spectacular cultural events. The Ghost Pepper (Bhut Jolokia) grows here.",
        "food": ["Smoked Pork with Bamboo Shoot", "Axone (fermented soya)", "Galho", "Zutho (rice beer)", "Akhuni Chutney", "Naga Chilli dishes"],
        "food_note": "Naga cuisine is bold, smoky and intensely flavoured. Axone is the pungent foundation of Naga cooking. The Bhut Jolokia (Ghost Pepper) was once the world's hottest chilli.",
        "places": ["Hornbill Festival, Kisama", "Kohima War Cemetery", "Dzüko Valley", "Khonoma Green Village", "Japfu Peak Trek", "Longwa Village"],
        "places_note": "Kohima War Cemetery honours Allied soldiers from one of WWII's fiercest battles. Longwa Village straddles the India-Myanmar border.",
        "best_time": "October to March. Hornbill Festival (December 1–10) is the unmissable event. Book accommodation months ahead.",
        "facts": ["16 major tribes each with distinct culture", "Ghost Pepper (Bhut Jolokia) — once world's hottest chilli — is from Nagaland", "Kohima War Cemetery is one of Asia's most moving WWII memorials", "Khonoma is India's first green village", "Longwa Village chief's house straddles the India-Myanmar border"],
    },
    "Meghalaya": {
        "emoji": "🌧️", "tag": "Wettest Place on Earth", "color": "#2980b9",
        "overview": "Meghalaya — 'Abode of the Clouds' — is India's wettest state. Cherrapunjee and Mawsynram compete for the title of the world's wettest place. The state is home to matrilineal Khasi, Jaintia and Garo tribes and miraculous living root bridges.",
        "food": ["Jadoh (rice & pork)", "Tungrymbai", "Doh Khleh", "Nakham Bitchi", "Putharo", "Minil Songa", "Sakin Gata"],
        "food_note": "Meghalayan food is tribal and forest-based — pork, fermented soya and bamboo shoots dominate. Jadoh is the everyday Khasi staple. Tungrymbai has a deeply pungent, savoury flavour.",
        "places": ["Living Root Bridges", "Dawki River", "Mawlynnong (Asia's cleanest village)", "Elephant Falls", "Nohkalikai Falls", "Umiam Lake", "Balpakram NP"],
        "places_note": "Living root bridges — grown over 500 years — are remarkable bio-engineering. The Dawki River is so clear boats appear to float on air.",
        "best_time": "October to May. Waterfalls are most dramatic in monsoon. Shillong Autumn Festival (Oct) and Cherry Blossom Festival (Nov) are beautiful.",
        "facts": ["World's two wettest places — Mawsynram & Cherrapunjee — are both here", "Living root bridges are grown, not built — over 500 years old", "One of three Indian states with a matrilineal society", "Dawki River boats appear to float on air", "Krem Puri is the world's longest sandstone cave (31 km)"],
    },
    "Sikkim": {
        "emoji": "🌸", "tag": "Himalayan Wonderland", "color": "#9b59b6",
        "overview": "Sikkim — India's smallest state — is arguably its most naturally spectacular. Home to Kangchenjunga (world's 3rd highest mountain at 8,586m), it was an independent Buddhist kingdom until 1975 and became India's first fully organic state in 2016.",
        "food": ["Phagshapa", "Gundruk", "Momo", "Thukpa", "Chhurpi (hard cheese)", "Sel Roti", "Tongba (millet beer)"],
        "food_note": "Sikkimese cuisine reflects Nepali, Tibetan and Lepcha roots. Momo — steamed dumplings — are everywhere and deeply addictive. Tongba is a fermented millet drink served hot in a bamboo mug.",
        "places": ["Kangchenjunga", "Gurudongmar Lake", "Rumtek Monastery", "Pelling", "Tsomgo Lake", "Yumthang Valley", "Ravangla Buddha Park"],
        "places_note": "Gurudongmar Lake at 17,100 ft is one of the world's highest lakes. Yumthang Valley bursts into rhododendron colour in spring.",
        "best_time": "March–May (rhododendron bloom) and October–December (clear mountain views). Losar — Tibetan New Year (Feb/Mar) — is the biggest festival.",
        "facts": ["Was an independent Buddhist kingdom until 1975", "India's first fully organic farming state (2016)", "Kangchenjunga is the world's 3rd highest mountain at 8,586m", "Gurudongmar Lake is one of the world's highest lakes at 17,100 ft", "Over 600 species of orchids — highest density in India"],
    },
    "Manipur": {"emoji": "🌺", "tag": "Polo & Floating Park", "color": "#e91e63", "overview": "Manipur — 'the Jewel of India' — is celebrated for Manipuri dance, unique cuisine, the world's only floating national park (Keibul Lamjao), and the birthplace of Polo. Loktak Lake is the largest freshwater lake in north-east India.", "food": ["Eromba", "Singju", "Chamthong", "Ngari (fermented fish)", "Paknam", "Chak-hao Kheer", "Morok Metpa"], "food_note": "Ngari (fermented fish) is the backbone of Manipuri cooking. Chak-hao — GI-tagged black rice — is unique to Manipur.", "places": ["Loktak Lake", "Keibul Lamjao (floating NP)", "Kangla Fort", "Ima Keithel (women's market)", "Dzüko Valley", "Khonghampat Orchidarium"], "places_note": "Ima Keithel is the world's only all-women market, 500+ years old. Dzüko Valley is a pristine alpine valley blanketed in wildflowers.", "best_time": "October to February. Shirui Lily Festival (May) celebrates the state flower.", "facts": ["Polo originated in Manipur (1st century AD)", "Keibul Lamjao is the world's only floating national park", "Ima Keithel is the world's only all-women market", "Chak-hao black rice has a GI tag", "Manipuri dance is one of India's 8 classical dance forms"]},
    "Arunachal Pradesh": {"emoji": "🌿", "tag": "Hidden Shangri-La", "color": "#4caf50", "overview": "Called 'The Land of the Dawn-Lit Mountains,' Arunachal Pradesh is India's largest north-eastern state and one of the most biodiverse regions on Earth. It receives the first sunrise in India.", "food": ["Apong (rice beer)", "Thukpa", "Pika Pila", "Smoked Pork with Bamboo", "Zan (millet porridge)", "Lukter (dried beef)"], "food_note": "Arunachali cuisine is flavoured by bamboo shoots, fermented foods and smoked meats. Apong (rice beer) is central to every tribal celebration.", "places": ["Tawang Monastery", "Ziro Valley", "Namdapha NP", "Sela Pass", "Mechuka Valley", "Dirang"], "places_note": "Tawang Monastery at 10,000 ft is the second largest Buddhist monastery in the world. Ziro Valley is nominated for UNESCO World Heritage.", "best_time": "October to April. Ziro Music Festival (September) is a cult indie music event.", "facts": ["Receives India's first sunrise", "Home to 26 major tribes with distinct languages", "Tawang is the 2nd largest Buddhist monastery in the world", "Over 500 species of orchids", "Namdapha NP is one of the world's biodiversity hotspots"]},
    "Mizoram": {"emoji": "🎋", "tag": "Bamboo Forests & Mist", "color": "#00bcd4", "overview": "Mizoram — 'Land of the Hill People' — has 91%+ literacy, is over 90% Christian, and is deeply musical. Its rolling bamboo-covered hills, clean towns and hospitable Mizo people make it unlike any other Indian state.", "food": ["Bai", "Vawksa Rep (smoked pork)", "Mizo Sawhchiar", "Bamboo Shoot Fry", "Chhum Han", "Zu (rice wine)"], "food_note": "Vawksa Rep — smoked pork — is the cornerstone of Mizo cooking. Bai (boiled vegetables with pork) is the everyday staple.", "places": ["Phawngpui (Blue Mountain)", "Vantawng Falls", "Champhai Valley", "Palak Lake", "Murlen NP", "Tam Dil Lake"], "places_note": "Phawngpui — the Blue Mountain at 2,157m — is sacred to the Mizo people. Champhai Valley is the 'Rice Bowl of Mizoram.'", "best_time": "October to March. Chapchar Kut (March) — celebrated with the iconic Cheraw (bamboo dance).", "facts": ["91%+ literacy — second highest in India", "Over 90% Christian population", "Cheraw (bamboo dance) is the iconic cultural art form", "Mizoram experiences Mautam — bamboo flowering every 48 years", "Phawngpui is the Blue Mountain, sacred to the Mizo people"]},
    "Chhattisgarh": {"emoji": "🌊", "tag": "Waterfalls & Tribes", "color": "#ff5722", "overview": "Chhattisgarh — India's tribal heartland — has 44% forest cover and 32% tribal population. It is home to the widest waterfall in India (Chitrakote Falls) and the most diverse tribal arts in the country.", "food": ["Chila", "Muthia", "Fara", "Bafauri", "Aamat (tribal curry)", "Bore Baasi", "Sabudana Khichdi"], "food_note": "Chhattisgarhi food is rice-based and light on spices. Bore Baasi — overnight-soaked rice with curd and onion — is the tribal breakfast.", "places": ["Chitrakote Falls", "Bastar", "Sirpur Buddhist Site", "Achanakmar Tiger Reserve", "Bhoramdeo Temple", "Tirathgarh Falls"], "places_note": "Chitrakote — India's Niagara — swells to 300m wide in monsoon. Bastar's 75-day Dussehra is the world's longest festival.", "best_time": "October to March. Bastar Dussehra (October) — a 75-day tribal goddess festival.", "facts": ["Chitrakote Falls is India's widest waterfall", "Bastar Dussehra is the world's longest festival (75 days)", "Over 80% of flora not found elsewhere in India", "Produces 15% of India's steel", "Home to rare Gond and Baiga tribal painting traditions"]},
    "Haryana": {"emoji": "🌾", "tag": "Battlefields & Culture", "color": "#795548", "overview": "Haryana — 'Abode of God' — is both ancient and modern. Kurukshetra, where the Mahabharata war was fought, lies here. Yet Gurugram is one of India's fastest-growing tech and financial hubs.", "food": ["Bajra Khichdi", "Hara Dhania Cholia", "Singri ki Sabzi", "Methi Gajar", "Kachri ki Chutney", "Besan Masala Roti"], "food_note": "Haryanvi food is simple and nourishing. Bajra (pearl millet) is the staple grain. Alsi ki Pinni — flaxseeds, jaggery and ghee — is a winter energy booster.", "places": ["Kurukshetra", "Sultanpur NP", "Pinjore Gardens", "Morni Hills", "Panipat Museum", "Surajkund Craft Fair"], "places_note": "Kurukshetra is one of India's most sacred sites. Surajkund Crafts Mela (February) is one of Asia's largest craft fairs.", "best_time": "October to March. Geeta Jayanti at Kurukshetra (Nov/Dec). Surajkund Crafts Mela (February) is unmissable.", "facts": ["India's top producer of milk", "Won 8 of India's 12 medals at the 2020 Tokyo Olympics", "Panipat witnessed three decisive battles that shaped Indian history", "Gurgaon hosts over 250 Fortune 500 companies", "Home to India's largest solar power plant"]},
    "Jharkhand": {"emoji": "💧", "tag": "Waterfalls & Forests", "color": "#009688", "overview": "Jharkhand — 'Land of the Forest' — has India's richest mineral reserves yet also some of its most beautiful waterfalls, dense Sal forests and vibrant tribal traditions.", "food": ["Dhuska", "Rugra (forest mushroom curry)", "Chilka Roti", "Litti Chokha", "Bamboo Shoot Curry", "Handia (rice beer)"], "food_note": "Rugra — a wild mushroom found only in Sal forests — is a seasonal delicacy. Handia rice beer is consumed at every tribal celebration.", "places": ["Hundru Falls", "Betla NP", "Netarhat", "Jonha Falls", "Baidyanath Dham", "Parasnath Hill", "Dasam Falls"], "places_note": "Hundru Falls drops 98m — one of India's highest. Netarhat is the 'Queen of Chotanagpur' for its sweeping sunrises.", "best_time": "October to March for waterfalls and wildlife. Sarhul (March/April) and Karma (August/September) are major tribal festivals.", "facts": ["Richest mineral reserves in India", "Hundru Falls drops 98m — one of India's highest", "28% of India's coal reserves are in Jharkhand", "Parasnath Hill is the holiest Jain pilgrimage site", "Produces the most lac (shellac) in the world"]},
    "Odisha": {"emoji": "🎭", "tag": "Temples & Odissi Dance", "color": "#ff9800", "overview": "Odisha is home to the sacred Jagannath Temple at Puri, the erotic masterpieces of Konark Sun Temple and the Buddhist stupa at Dhauli. Odisha's Pattachitra paintings, Odissi dance and tribal crafts are internationally recognised.", "food": ["Dalma", "Pakhala Bhaat", "Machha Besara", "Chhena Poda", "Rasgulla", "Santula", "Mudhi Mansa"], "food_note": "Odia cuisine is mild and flavoured by mustard and coconut. Pakhala Bhaat — rice soaked overnight — is one of the world's oldest fermented foods. Chhena Poda is a caramelised cottage cheese dessert.", "places": ["Puri Jagannath Temple", "Konark Sun Temple (UNESCO)", "Chilika Lake", "Bhubaneswar", "Simlipal NP", "Bhitarkanika", "Rath Yatra"], "places_note": "Konark Sun Temple — a 13th-century chariot-shaped temple — is one of the world's greatest architectural achievements. Chilika Lake is Asia's largest brackish water lake.", "best_time": "October to February. Rath Yatra in Puri (June/July) is a once-in-a-lifetime spectacle.", "facts": ["'Juggernaut' in English comes from Jagannath", "Konark is called the 'Black Pagoda' by sailors", "Bhubaneswar has 242 temples alone", "Odisha Rasagola has a GI tag", "Chilika Lake hosts 160 species of migratory birds in winter"]},
    "Tamil Nadu": {
        "emoji": "🏛️", "tag": "Temples & Classical Arts", "color": "#8B0000",
        "overview": "Tamil Nadu — the Land of Temples — is home to the world's oldest living classical language (Tamil, 2,000+ years) and some of India's most magnificent Dravidian architecture. The state has the largest number of UNESCO-listed temples in the country. With 1,076 km of coastline, ancient port cities, and Bharatanatyam classical dance, it is one of India's most culturally rich states.",
        "food": ["Idli-Sambar","Dosa","Chettinad Chicken Curry","Pongal","Rasam","Filter Coffee","Murukku"],
        "food_note": "Tamil cuisine is one of India's oldest culinary traditions. Chettinad cooking is globally famous for bold spices like kalpasi. Filter coffee in a steel tumbler-davara is a daily ritual. Idli and dosa from Tamil Nadu are considered the originals.",
        "places": ["Meenakshi Temple, Madurai","Brihadeeswarar Temple, Thanjavur","Marina Beach, Chennai","Ooty (Nilgiris)","Mahabalipuram (UNESCO)","Rameswaram","Kodaikanal"],
        "places_note": "The Meenakshi Temple has 14 towering gopurams covered in thousands of sculptures. Mahabalipuram's shore temple is a UNESCO World Heritage Site. Marina Beach is the world's second longest urban beach.",
        "best_time": "November to March. Pongal (January) is Tamil Nadu's most important festival — celebrated with kolam drawings and harvest rituals. Avoid April–June (very hot).",
        "facts": ["Tamil is the world's oldest living classical language","Tamil Nadu has 38,000+ temples — highest in India","Marina Beach is the world's second longest urban beach","The Nilgiri Mountain Railway (Ooty toy train) is UNESCO-listed","Bharatanatyam classical dance originated in Tamil Nadu"],
    },
    "Telangana": {
        "emoji": "🕌", "tag": "Nizams & Pearls", "color": "#FF6600",
        "overview": "Telangana — India's youngest state (formed 2014) — is built on the legacy of the Nizam dynasty, one of history's wealthiest rulers. Hyderabad is a city of iconic biryani, pearls, historic forts and a booming IT industry earning it the nickname 'Cyberabad.' The state has 69 wildlife sanctuaries — the highest number of any Indian state.",
        "food": ["Hyderabadi Dum Biryani","Haleem","Sarva Pindi","Jonna Roti","Gongura Pachadi","Qubani ka Meetha","Osmania Biscuit"],
        "food_note": "Hyderabadi Biryani — cooked in the dum (sealed pot) style — is one of the most celebrated dishes in India. Haleem has a GI tag from Hyderabad and is served especially during Ramadan. Osmania biscuit from the Nizam era is a beloved teatime staple.",
        "places": ["Charminar, Hyderabad","Golconda Fort","Ramoji Film City","Hussain Sagar Lake","Warangal Fort","Nagarjuna Sagar Dam","Laad Bazaar (pearls)"],
        "places_note": "Charminar is Hyderabad's most iconic 16th-century monument. Golconda Fort was once the diamond trading capital — the Kohinoor originated here. Ramoji Film City is the world's largest integrated film studio (Guinness record).",
        "best_time": "October to March. Hyderabad Deccan Festival (February) and Bathukamma flower festival (October) are major cultural highlights.",
        "facts": ["Telangana has 69 wildlife sanctuaries — highest in India","The Kohinoor diamond was mined in Golconda, Hyderabad","Hyderabadi Haleem has a Geographical Indication tag","Ramoji Film City is the world's largest integrated film studio","Hyderabad is India's second largest IT hub — called 'Cyberabad'"],
    },
    "Tripura": {
        "emoji": "🌿", "tag": "Bamboo & Royals", "color": "#2E8B57",
        "overview": "Tripura — a small hilly state surrounded by Bangladesh on three sides — has a remarkably rich royal heritage from the Manikya dynasty. Despite its small size, it is India's third most densely populated state. Tripura is a leading rubber producer and home to a unique blend of Bengali and tribal cultures.",
        "food": ["Mui Borok (tribal cuisine)","Chakhwi","Berma (fermented fish)","Wahan Mosdeng (pork with chilli)","Gudok","Muya Awandru (bamboo shoot curry)"],
        "food_note": "Tripuri tribal cuisine centres on fermented and smoked ingredients. Berma — fermented dried fish — is the backbone of most dishes. Bamboo shoot features in almost every meal. The food is simple, earthy and unmistakably north-eastern.",
        "places": ["Ujjayanta Palace, Agartala","Neermahal Water Palace","Unakoti Rock Carvings","Sepahijala Wildlife Sanctuary","Jampui Hills","Tripura Sundari Temple"],
        "places_note": "Neermahal — a royal water palace built in the middle of a lake — is one of north-east India's most photogenic monuments. Unakoti has thousands of ancient rock carvings from the 7th–9th centuries.",
        "best_time": "October to March. Garia Puja (April) and Kharchi Puja (July) are the state's most important tribal festivals.",
        "facts": ["Tripura is surrounded by Bangladesh on three sides","Neermahal is one of India's two water palaces","Tripura is India's third largest rubber producer","Unakoti has rock carvings of nearly 10 million deities","Tripura produces some of India's finest bamboo crafts"],
    },
    "Uttarakhand": {
        "emoji": "⛰️", "tag": "Dev Bhoomi & Himalayas", "color": "#1565C0",
        "overview": "Uttarakhand — 'Dev Bhoomi' (Land of Gods) — is the source of two of India's holiest rivers: the Ganga (at Gangotri) and the Yamuna (at Yamunotri). It is home to the Char Dham pilgrimage circuit, Jim Corbett National Park (India's oldest), and the UNESCO-listed Valley of Flowers.",
        "food": ["Aloo Ke Gutke","Kafuli (spinach curry)","Bal Mithai (Almora sweet)","Singori","Jhangora ki Kheer","Phaanu (lentil curry)","Chainsoo"],
        "food_note": "Uttarakhand cuisine is simple, wholesome mountain food. Kafuli is a thick spinach and fenugreek curry. Bal Mithai — a dark chocolate-like fudge covered in white sugar balls from Almora — is the state's most beloved sweet.",
        "places": ["Char Dham (Gangotri, Yamunotri, Kedarnath, Badrinath)","Jim Corbett NP","Valley of Flowers (UNESCO)","Rishikesh","Haridwar","Auli (skiing)","Nainital","Mussoorie"],
        "places_note": "Rishikesh is the 'Yoga Capital of the World' and a hub for white-water rafting. The Valley of Flowers is a UNESCO World Heritage Site. Haridwar hosts the Kumbh Mela every 12 years.",
        "best_time": "March–June for treks and pilgrimage. October–November for clear skies. December–February for skiing at Auli. Char Dham opens April–November.",
        "facts": ["Uttarakhand is the source of the Ganga and Yamuna rivers","Jim Corbett is India's oldest national park (established 1936)","Valley of Flowers is a UNESCO World Heritage Site","Rishikesh is the 'Yoga Capital of the World'","Auli is India's premier ski resort at 2,500m altitude"],
    },
    "Delhi": {
        "emoji": "🏙️", "tag": "Capital & History", "color": "#B71C1C",
        "overview": "Delhi — India's National Capital Territory — has 3,000+ years of history and has been the seat of numerous empires including the Mughals and the British. Old Delhi and New Delhi exist side by side — one a Mughal-era labyrinth of lanes, the other a planned colonial capital. It has more UNESCO World Heritage Sites than most Indian cities.",
        "food": ["Chole Bhature","Butter Chicken (invented here)","Stuffed Paranthas (Paranthe Wali Gali)","Daulat ki Chaat","Jalebi","Nihari","Kebabs from Karim's"],
        "food_note": "Delhi's street food scene is legendary. Chandni Chowk's Paranthe Wali Gali serves stuffed parathas in dozens of varieties since 1875. Karim's near Jama Masjid has served Mughlai food since 1913. Daulat ki Chaat is a seasonal foam dessert unique to Delhi.",
        "places": ["Red Fort (UNESCO)","Qutub Minar (UNESCO)","Humayun's Tomb (UNESCO)","India Gate","Lotus Temple","Akshardham Temple","Jama Masjid","Chandni Chowk"],
        "places_note": "Delhi has three UNESCO World Heritage Sites. The Red Fort was the residence of Mughal emperors for 200 years. Qutub Minar at 73m is the world's tallest brick minaret. Akshardham is one of the world's largest Hindu temples.",
        "best_time": "October to March. Republic Day parade (January 26) is a spectacular national event. Avoid May–June (45°C+).",
        "facts": ["Delhi has 3 UNESCO World Heritage Sites","Qutub Minar is the world's tallest brick minaret at 73m","Delhi has been capital of 7 major empires in history","Butter Chicken was invented at Moti Mahal restaurant in Delhi (1950s)","Delhi Metro is one of Asia's largest metro systems"],
    },
    "Ladakh": {
        "emoji": "🏔️", "tag": "High-Altitude Desert", "color": "#5C4033",
        "overview": "Ladakh — 'Land of High Passes' — is a Union Territory at an average altitude of 3,500m, one of the highest inhabited regions on Earth. Flanked by the Himalayas and Karakoram ranges, it is a cold desert of stunning stark beauty, ancient Buddhist monasteries, and some of the world's most dramatic motorcycle and trekking routes.",
        "food": ["Thukpa","Momos","Tsampa (roasted barley flour)","Skyu (pasta with root vegetables)","Butter Tea (Po Cha)","Chang (barley beer)","Chhurpe (hard yak cheese)"],
        "food_note": "Ladakhi cuisine is Tibetan-influenced and built for altitude and cold. Butter Tea (Po Cha) — made with yak butter and salt — is essential for warmth at high altitude. Chang (barley beer) is brewed at home for festivals. Chhurpe (hard yak cheese) is chewed as a snack.",
        "places": ["Pangong Lake","Nubra Valley & Bactrian camels","Khardung La (one of world's highest roads)","Hemis Monastery","Leh Palace","Magnetic Hill","Zanskar Valley","Tso Moriri Lake"],
        "places_note": "Pangong Lake at 4,350m changes colour multiple times through the day and spans India and China. Nubra Valley is a high-altitude desert with Bactrian camels. Khardung La at 5,359m is one of the world's highest motorable roads.",
        "best_time": "June to September (main tourist season — roads open). January–February for the Chadar Trek (frozen Zanskar river). Hemis Festival (June/July) has spectacular masked dance.",
        "facts": ["Ladakh sits at an average altitude of 3,500m — one of Earth's highest inhabited regions","Pangong Lake spans India and China — only 45% is in India","Khardung La at 5,359m is one of the world's highest motorable roads","Highest concentration of Buddhist monasteries in the world","The Chadar Trek on the frozen Zanskar river is one of the world's most extreme treks"],
    },
    "Puducherry": {
        "emoji": "🥖", "tag": "French Riviera of the East", "color": "#1A237E",
        "overview": "Puducherry (Pondicherry) was a French colony for 138 years and retains a unique Franco-Tamil character. The French Quarter (White Town) has bougainvillea-draped colonial villas, French cafes, and yellow-painted police officers. Sri Aurobindo Ashram and the experimental township of Auroville make it a global spiritual destination.",
        "food": ["Bouillabaisse (French fish stew)","Crepes & Croissants","Coconut-based Tamil curries","Prawn dishes","Puducherry Baguette","Café de Flore coffee"],
        "food_note": "Puducherry's cuisine is a delightful fusion of French and Tamil flavours. The French Quarter has authentic patisseries and bistros. Tamil coconut-based seafood curries are equally present. Fresh baguettes with spicy curries is uniquely Pondicherrian.",
        "places": ["French Quarter (White Town)","Promenade Beach","Sri Aurobindo Ashram","Auroville (experimental township)","Basilica of the Sacred Heart","Immaculate Conception Cathedral","Serenity Beach"],
        "places_note": "Auroville is an experimental international township built in 1968 with 3,000 residents from 60 countries. The Matrimandir — a golden geodesic dome — is its meditative heart. The Promenade Beach at dawn is one of the most peaceful walks in India.",
        "best_time": "October to February. Avoid November–December (cyclone season). Bastille Day (July 14) is celebrated here with French flair!",
        "facts": ["Puducherry was a French colony for 138 years — handed over to India in 1954","Auroville has 3,000 residents from 60 countries","The Matrimandir in Auroville has the world's largest optically perfect glass sphere","Highest density of French colonial architecture outside France","French Quarter police wear red-and-black French-style uniforms"],
    },
    "Chandigarh": {
        "emoji": "🌳", "tag": "Planned City & Gardens", "color": "#00695C",
        "overview": "Chandigarh — the first planned city of independent India — was designed by legendary architect Le Corbusier and is a masterpiece of modernist urban planning. It serves as the joint capital of Punjab and Haryana. Known for wide tree-lined roads, the Rock Garden and high quality of life, it consistently ranks among India's cleanest and wealthiest cities.",
        "food": ["Butter Chicken","Chole Bhature","Sarson da Saag with Makki di Roti","Dahi Bhalla","Amritsari Fish","Lassi","Pinni (wheat sweet)"],
        "food_note": "Chandigarh's food scene reflects its Punjabi soul — rich, generous and dairy-forward. Sector 17 and Sector 22 food streets are the city's dining heart. Lassi here is thick, creamy and served in tall clay mugs.",
        "places": ["Rock Garden (made from industrial waste)","Sukhna Lake","Rose Garden","Le Corbusier Centre","Capitol Complex (UNESCO)","Pinjore Gardens","Sector 17 Plaza"],
        "places_note": "The Rock Garden — created by Nek Chand from 5 million pieces of recycled waste — is one of India's most unique art installations. The Capitol Complex is a UNESCO World Heritage Site designed by Le Corbusier.",
        "best_time": "October to March. The Rose Festival (February/March) at the Rose Garden — one of Asia's largest — is spectacular with 50,000+ roses in bloom.",
        "facts": ["Chandigarh was designed by legendary architect Le Corbusier","Capitol Complex is a UNESCO World Heritage Site","Rock Garden uses 5 million pieces of waste material","Chandigarh has the highest per capita income among Indian UTs","The city is divided into numbered sectors — a modernist urban planning experiment"],
    },
    "Andaman & Nicobar Islands": {
        "emoji": "🏝️", "tag": "Tropical Paradise", "color": "#006064",
        "overview": "The Andaman & Nicobar Islands comprise 572 islands in the Bay of Bengal, only 38 inhabited. With crystal-clear turquoise waters, pristine coral reefs, dense rainforests and the historic Cellular Jail (Kala Pani), it is one of India's most remote and breathtaking destinations. The indigenous Sentinelese tribe is one of the world's last uncontacted peoples.",
        "food": ["Coconut Prawn Curry","Fish Tikka","Grilled Lobster","Red Snapper","Coconut Rice","Banana Flower Curry","Fresh seafood platters"],
        "food_note": "Andaman cuisine is dominated by fresh seafood and coconut. Fish, prawn and lobster are incredibly fresh and cooked simply. The influence of Bengali, South Indian and Malay cuisines creates a unique fusion. Coconut features in almost every dish.",
        "places": ["Radhanagar Beach (Havelock Island)","Cellular Jail (Kala Pani), Port Blair","Baratang Island (limestone caves)","Neil Island","Barren Island (active volcano)","Ross Island","Mahatma Gandhi Marine NP (diving)"],
        "places_note": "Radhanagar Beach on Havelock Island has been rated one of Asia's best beaches by Time magazine. Cellular Jail is a deeply moving national memorial. Barren Island is India's only confirmed active volcano.",
        "best_time": "November to April — calm seas and excellent diving visibility. Avoid May–October (monsoon and rough seas). Best diving December–February.",
        "facts": ["572 islands — only 38 inhabited","The Sentinelese tribe is one of the world's last uncontacted peoples","Radhanagar Beach rated Asia's best beach by Time magazine","Barren Island is India's only confirmed active volcano","Cellular Jail (Kala Pani) housed Indian freedom fighters during British rule"],
    },
    "Lakshadweep": {
        "emoji": "🪸", "tag": "Coral Islands", "color": "#0097A7",
        "overview": "Lakshadweep — 'One Hundred Thousand Islands' — is India's smallest Union Territory and only coral island group. Situated in the Arabian Sea, it has 36 islands (11 inhabited) with some of the world's most pristine coral reefs, turquoise lagoons and white sandy beaches. Strict entry permits and limited tourism have kept it one of India's last true paradises.",
        "food": ["Tuna Fish Curry","Octopus fry","Mas Riha (tuna coconut curry)","Kada Curry (coconut chicken)","Fried Breadfruit","Coconut milk rice","Banana chips"],
        "food_note": "Lakshadweep cuisine is almost entirely based on tuna and coconut — the two most abundant local resources. The food is light, mildly spiced and deeply aromatic. Since the population is almost entirely Muslim, there is no beef or pork. Tuna is eaten at virtually every meal.",
        "places": ["Agatti Island (entry point)","Bangaram Island (snorkelling & diving)","Kavaratti (capital, mosques)","Minicoy Island (lighthouse)","Kalpeni Island (coral lagoon)","Kadmat Island (water sports)"],
        "places_note": "Bangaram Island is uninhabited except for a single eco-resort with world-class snorkelling. Minicoy Island has a unique culture distinct from the other islands. The lagoons are so clear you can see the reef from above.",
        "best_time": "October to April — calm seas. Best diving November–March. Entry requires a special permit from the Lakshadweep Administration — plan well ahead.",
        "facts": ["India's smallest Union Territory by area","Has over 90% intact coral cover — among the world's highest","Only 1–2 metres above sea level — extremely vulnerable to climate change","Entry requires a special government permit","Almost entirely Muslim population — unique culture in peninsular India"],
    },
    "Dadra & Nagar Haveli and Daman & Diu": {
        "emoji": "🏖️", "tag": "Portuguese Heritage & Beaches", "color": "#4A148C",
        "overview": "This Union Territory — created in 2020 by merging two former Portuguese colonies — consists of coastal Daman and Diu with Portuguese forts and beaches, and the inland forested Dadra & Nagar Haveli home to Kokna and Varli tribal communities. The entire UT was under Portuguese rule until 1961.",
        "food": ["Seafood (prawn, crab, pomfret)","Vindaloo","Sorpotel","Bebinca","Feni (local spirit)","Coconut curries","Rice and fish"],
        "food_note": "The coastal regions share a food culture with Goa — Portuguese influence is strong. Vindaloo, Sorpotel and Bebinca are common. Fresh seafood — pomfret, prawns and crabs — are cooked simply. Feni (cashew or coconut liquor) is widely available.",
        "places": ["Daman Fort","Moti Daman (Old City)","Naida Caves, Diu","St. Paul's Church, Diu","Devka Beach, Daman","Nagoa Beach, Diu","Vansda National Park"],
        "places_note": "The Diu Fort overlooking the Arabian Sea is one of India's finest Portuguese forts. Naida Caves are an unusual network formed from Portuguese quarried stone. Vansda National Park is home to leopards and 250+ bird species.",
        "best_time": "October to March. Popular weekend getaway from Mumbai and Surat. Diu is one of the few places in Gujarat where alcohol is legally available.",
        "facts": ["Formed in 2020 by merging two separate Union Territories","Daman and Diu were Portuguese colonies until 1961 — 14 years after Independence","Diu is one of the few places in Gujarat where alcohol is legally available","Diu Fort repelled three separate Mughal sieges — never captured in battle","Vansda National Park has one of India's highest densities of leopards"],
    },

}

# Use all states + union territories defined above (28 states + 8 UTs = 36)

STATE_META = {
    # Regions: North, South, East, West, Central, Northeast
    # Climate: Alpine, Temperate, Tropical, Arid, Subtropical, Coastal
    # Themes: beach, heritage, wildlife, hill, desert, spirituality, food, adventure, culture
    "Rajasthan": {"region": "West", "climate": "Arid", "themes": ["heritage", "desert", "culture", "food"], "family_friendly": True},
    "Kerala": {"region": "South", "climate": "Tropical", "themes": ["beach", "culture", "food"], "family_friendly": True},
    "Gujarat": {"region": "West", "climate": "Arid", "themes": ["wildlife", "heritage", "culture"], "family_friendly": True},
    "Goa": {"region": "West", "climate": "Coastal", "themes": ["beach", "food", "culture"], "family_friendly": True},
    "Jammu & Kashmir": {"region": "North", "climate": "Alpine", "themes": ["hill", "adventure", "culture"], "family_friendly": True},
    "Karnataka": {"region": "South", "climate": "Subtropical", "themes": ["heritage", "food", "culture", "wildlife"], "family_friendly": True},
    "Maharashtra": {"region": "West", "climate": "Subtropical", "themes": ["heritage", "culture", "food"], "family_friendly": True},
    "Punjab": {"region": "North", "climate": "Subtropical", "themes": ["culture", "food", "heritage", "spirituality"], "family_friendly": True},
    "Himachal Pradesh": {"region": "North", "climate": "Alpine", "themes": ["hill", "adventure", "spirituality"], "family_friendly": True},
    "West Bengal": {"region": "East", "climate": "Subtropical", "themes": ["culture", "food", "heritage", "wildlife"], "family_friendly": True},
    "Uttar Pradesh": {"region": "North", "climate": "Subtropical", "themes": ["heritage", "spirituality", "culture", "food"], "family_friendly": True},
    "Assam": {"region": "Northeast", "climate": "Subtropical", "themes": ["wildlife", "culture", "adventure"], "family_friendly": True},
    "Bihar": {"region": "East", "climate": "Subtropical", "themes": ["spirituality", "heritage", "culture"], "family_friendly": True},
    "Madhya Pradesh": {"region": "Central", "climate": "Subtropical", "themes": ["wildlife", "heritage", "culture"], "family_friendly": True},
    "Andhra Pradesh": {"region": "South", "climate": "Coastal", "themes": ["spirituality", "heritage", "food"], "family_friendly": True},
    "Nagaland": {"region": "Northeast", "climate": "Temperate", "themes": ["culture", "adventure", "food"], "family_friendly": True},
    "Meghalaya": {"region": "Northeast", "climate": "Temperate", "themes": ["adventure", "culture", "wildlife"], "family_friendly": True},
    "Sikkim": {"region": "Northeast", "climate": "Alpine", "themes": ["hill", "adventure", "culture", "spirituality"], "family_friendly": True},
    "Manipur": {"region": "Northeast", "climate": "Temperate", "themes": ["culture", "wildlife", "adventure"], "family_friendly": True},
    "Arunachal Pradesh": {"region": "Northeast", "climate": "Alpine", "themes": ["adventure", "culture", "hill"], "family_friendly": True},
    "Mizoram": {"region": "Northeast", "climate": "Temperate", "themes": ["culture", "hill", "adventure"], "family_friendly": True},
    "Chhattisgarh": {"region": "Central", "climate": "Subtropical", "themes": ["wildlife", "culture", "adventure"], "family_friendly": True},
    "Haryana": {"region": "North", "climate": "Subtropical", "themes": ["heritage", "culture", "food"], "family_friendly": True},
    "Jharkhand": {"region": "East", "climate": "Subtropical", "themes": ["wildlife", "adventure", "culture"], "family_friendly": True},
    "Odisha": {"region": "East", "climate": "Coastal", "themes": ["heritage", "spirituality", "culture", "beach"], "family_friendly": True},
    "Tamil Nadu": {"region": "South", "climate": "Coastal", "themes": ["heritage", "spirituality", "culture", "food"], "family_friendly": True},
    "Telangana": {"region": "South", "climate": "Subtropical", "themes": ["heritage", "culture", "food"], "family_friendly": True},
    "Tripura": {"region": "Northeast", "climate": "Subtropical", "themes": ["culture", "heritage", "adventure"], "family_friendly": True},
    "Uttarakhand": {"region": "North", "climate": "Alpine", "themes": ["spirituality", "adventure", "hill", "wildlife"], "family_friendly": True},
    "Delhi": {"region": "North", "climate": "Subtropical", "themes": ["heritage", "culture", "food"], "family_friendly": True},
    "Ladakh": {"region": "North", "climate": "Alpine", "themes": ["adventure", "hill", "culture"], "family_friendly": True},
    "Puducherry": {"region": "South", "climate": "Coastal", "themes": ["beach", "culture", "heritage", "food"], "family_friendly": True},
    "Chandigarh": {"region": "North", "climate": "Subtropical", "themes": ["culture", "heritage", "food"], "family_friendly": True},
    "Andaman & Nicobar Islands": {"region": "East", "climate": "Coastal", "themes": ["beach", "wildlife", "adventure"], "family_friendly": True},
    "Lakshadweep": {"region": "West", "climate": "Coastal", "themes": ["beach", "adventure", "wildlife"], "family_friendly": True},
    "Dadra & Nagar Haveli and Daman & Diu": {"region": "West", "climate": "Coastal", "themes": ["beach", "heritage", "culture"], "family_friendly": True},
}

def get_meta(name):
    return STATE_META.get(name, {"region": "Unknown", "climate": "Unknown", "themes": [], "family_friendly": True})

def _ensure_all_states_have_meta():
    for k in STATES.keys():
        if k not in STATE_META:
            STATE_META[k] = {"region": "Unknown", "climate": "Unknown", "themes": [], "family_friendly": True}

_ensure_all_states_have_meta()

QUIZ_QUESTIONS = [
    {"q": "Which state is home to the world's only wild Asiatic Lions?", "options": ["Rajasthan", "Gujarat", "Maharashtra", "Karnataka"], "ans": "Gujarat"},
    {"q": "Which Indian state receives the country's first sunrise?", "options": ["Meghalaya", "Nagaland", "Arunachal Pradesh", "Assam"], "ans": "Arunachal Pradesh"},
    {"q": "The English word 'Juggernaut' comes from which temple?", "options": ["Tirupati", "Jagannath (Puri)", "Somnath", "Konark"], "ans": "Jagannath (Puri)"},
    {"q": "Which state produces 55% of India's total tea output?", "options": ["West Bengal", "Assam", "Kerala", STATE_HIMACHAL], "ans": "Assam"},
    {"q": "Polo — the sport — originated in which Indian state?", "options": ["Rajasthan", "Manipur", "Punjab", "Gujarat"], "ans": "Manipur"},
    {"q": "Which festival lasts 75 days — the world's longest festival?", "options": ["Pushkar Camel Fair", "Hornbill Festival", "Bastar Dussehra", "Onam"], "ans": "Bastar Dussehra"},
    {"q": "Which state was India's first to become fully organic?", "options": ["Kerala", "Sikkim", "Uttarakhand", "Nagaland"], "ans": "Sikkim"},
    {"q": "Ghost Pepper (Bhut Jolokia) grows in which state?", "options": [STATE_ANDHRA, "Karnataka", "Nagaland", "Rajasthan"], "ans": "Nagaland"},
    {"q": "Which lake is the world's only floating national park?", "options": ["Loktak Lake", "Dal Lake", "Chilika Lake", "Umiam Lake"], "ans": "Loktak Lake"},
    {"q": "Mawsynram and Cherrapunjee are both in which state?", "options": ["Assam", "Mizoram", "Nagaland", "Meghalaya"], "ans": "Meghalaya"},
    {"q": "Which state has the world's largest free kitchen?", "options": ["Rajasthan", "Gujarat", "Punjab", "Maharashtra"], "ans": "Punjab"},
    {"q": "Bhimbetka cave paintings are approximately how old?", "options": ["5,000 years", "10,000 years", "30,000 years", "1,000 years"], "ans": "30,000 years"},
    {"q": "Kuchipudi classical dance originated in which state?", "options": ["Tamil Nadu", "Kerala", "Karnataka", STATE_ANDHRA], "ans": STATE_ANDHRA},
    {"q": "Which state is known as 'Dev Bhoomi' (Land of Gods)?", "options": ["Uttarakhand", STATE_HIMACHAL, "Rajasthan", "Bihar"], "ans": STATE_HIMACHAL},
    {"q": "Nalanda — the world's first university — was in which state?", "options": ["UP", "Maharashtra", "Bihar", "Rajasthan"], "ans": "Bihar"},
]

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        users = _load(USERS_FILE, {})
        if username in users and users[username]["pw"] == _hash(password):
            session["username"] = username
            return redirect(url_for("home"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        email    = request.form.get("email", "").strip()
        users = _load(USERS_FILE, {})
        if len(username) < 3:
            flash("Username must be at least 3 characters.", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
        elif username in users:
            flash("Username already taken.", "error")
        else:
            users[username] = {
                "pw": _hash(password), "email": email,
                "joined": datetime.datetime.now().isoformat()
            }
            _save(USERS_FILE, users)
            session["username"] = username
            return redirect(url_for("home"))
    return render_template("signup.html")

@app.route("/guest", methods=["GET"])
def guest():
    session["username"] = "guest"
    return redirect(url_for("home"))

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/home", methods=["GET"])
@login_required
def home():
    username = session["username"]
    rec = get_user_record(username) if username != "guest" else {"favourites": [], "visited": [], "quiz_scores": []}
    states_list = [{"key": k, **{f: v for f, v in v.items()}, "meta": get_meta(k)} for k, v in STATES.items()]
    return render_template("home.html",
        username=username,
        states=states_list,
        favourites=rec.get("favourites", []),
        visited=rec.get("visited", []),
        total=len(STATES)
    )

@app.route("/state/<name>", methods=["GET"])
@login_required
def state_detail(name):
    if name not in STATES:
        return redirect(url_for("home"))
    username = session["username"]
    rec = get_user_record(username) if username != "guest" else {"favourites": [], "visited": [], "quiz_scores": []}
    return render_template("state.html",
        username=username,
        state_key=name,
        state=STATES[name],
        is_fav=name in rec.get("favourites", []),
        is_visited=name in rec.get("visited", [])
    )

@app.route("/api/favourite", methods=["POST"])
@login_required
def toggle_favourite():
    username = session["username"]
    if username == "guest":
        return jsonify({"error": "Login required"}), 403
    name = request.json.get("name")
    if name not in STATES:
        return jsonify({"error": "Not found"}), 404
    rec = get_user_record(username)
    favs = rec.get("favourites", [])
    if name in favs:
        favs.remove(name)
        added = False
    else:
        favs.append(name)
        added = True
    rec["favourites"] = favs
    save_user_record(username, rec)
    return jsonify({"added": added, "count": len(favs)})

@app.route("/api/visited", methods=["POST"])
@login_required
def toggle_visited():
    username = session["username"]
    if username == "guest":
        return jsonify({"error": "Login required"}), 403
    name = request.json.get("name")
    if name not in STATES:
        return jsonify({"error": "Not found"}), 404
    rec = get_user_record(username)
    visited = rec.get("visited", [])
    if name in visited:
        visited.remove(name)
        added = False
    else:
        visited.append(name)
        added = True
    rec["visited"] = visited
    save_user_record(username, rec)
    return jsonify({"added": added, "count": len(visited), "total": len(STATES)})

@app.route("/quiz", methods=["GET"])
@login_required
def quiz():
    questions = random.sample(QUIZ_QUESTIONS, min(10, len(QUIZ_QUESTIONS)))
    for q in questions:
        opts = q["options"][:]
        random.shuffle(opts)
        q["shuffled"] = opts
    session["quiz"] = questions
    session["quiz_score"] = 0
    session["quiz_idx"] = 0
    return render_template("quiz.html", username=session["username"],
                           question=questions[0], idx=0, total=len(questions))

@app.route("/quiz/answer", methods=["POST"])
@login_required
def quiz_answer():
    questions = session.get("quiz", [])
    idx = session.get("quiz_idx", 0)
    score = session.get("quiz_score", 0)
    answer = request.form.get("answer", "")
    correct = questions[idx]["ans"]
    is_correct = answer == correct
    if is_correct:
        score += 1
        session["quiz_score"] = score
    idx += 1
    session["quiz_idx"] = idx
    if idx >= len(questions):
        username = session["username"]
        if username != "guest":
            rec = get_user_record(username)
            rec["quiz_scores"].append({
                "score": score, "total": len(questions),
                "date": datetime.datetime.now().strftime("%d %b %Y")
            })
            save_user_record(username, rec)
        return render_template("quiz_result.html", username=username,
                               score=score, total=len(questions))
    return render_template("quiz.html", username=session["username"],
                           question=questions[idx], idx=idx, total=len(questions),
                           last_correct=is_correct, last_answer=answer, last_correct_ans=correct)

@app.route("/profile", methods=["GET"])
@login_required
def profile():
    username = session["username"]
    if username == "guest":
        return redirect(url_for("home"))
    rec = get_user_record(username)
    users = _load(USERS_FILE, {})
    user_info = users.get(username, {})
    return render_template("profile.html",
        username=username,
        email=user_info.get("email", ""),
        joined=user_info.get("joined", "")[:10],
        favourites=rec.get("favourites", []),
        visited=rec.get("visited", []),
        quiz_scores=rec.get("quiz_scores", [])[-5:],
        total=len(STATES),
        states=STATES
    )

@app.route("/public/<username>", methods=["GET"])
def public_profile(username):
    users = _load(USERS_FILE, {})
    if username not in users:
        return redirect(url_for("login"))
    rec = get_user_record(username)
    return render_template(
        "public_profile.html",
        username=username,
        email=users.get(username, {}).get("email", ""),
        joined=users.get(username, {}).get("joined", "")[:10],
        favourites=rec.get("favourites", []),
        visited=rec.get("visited", []),
        quiz_scores=rec.get("quiz_scores", [])[-10:],
        total=len(STATES),
        states=STATES,
    )

def _render_profile_pdf(username):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    users = _load(USERS_FILE, {})
    rec = get_user_record(username)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    y = h - 60
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Incredible India — Profile")
    y -= 28
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"User: {username}")
    y -= 18
    email = users.get(username, {}).get("email", "")
    if email:
        c.drawString(50, y, f"Email: {email}")
        y -= 18
    joined = users.get(username, {}).get("joined", "")[:10]
    if joined:
        c.drawString(50, y, f"Joined: {joined}")
        y -= 22

    favs = rec.get("favourites", [])
    visited = rec.get("visited", [])
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Favourites ({len(favs)}):")
    y -= 16
    c.setFont("Helvetica", 11)
    c.drawString(60, y, ", ".join(favs) if favs else "None")
    y -= 22

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Visited ({len(visited)} / {len(STATES)}):")
    y -= 16
    c.setFont("Helvetica", 11)
    c.drawString(60, y, ", ".join(visited) if visited else "None")
    y -= 22

    scores = rec.get("quiz_scores", [])[-10:]
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Quiz History ({len(scores)} latest):")
    y -= 16
    c.setFont("Helvetica", 11)
    if scores:
        for s in reversed(scores):
            c.drawString(60, y, f"{s.get('date','')} — {s.get('score',0)}/{s.get('total',0)}")
            y -= 14
            if y < 60:
                c.showPage()
                y = h - 60
                c.setFont("Helvetica", 11)
    else:
        c.drawString(60, y, "No attempts yet.")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf

@app.route("/profile/pdf", methods=["GET"])
@login_required
def profile_pdf():
    username = session["username"]
    if username == "guest":
        return redirect(url_for("home"))
    buf = _render_profile_pdf(username)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name=f"{username}_profile.pdf")

@app.route("/public/<username>/pdf", methods=["GET"])
def public_profile_pdf(username):
    users = _load(USERS_FILE, {})
    if username not in users:
        return redirect(url_for("login"))
    buf = _render_profile_pdf(username)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name=f"{username}_profile.pdf")

@app.route("/compare", methods=["GET"])
@login_required
def compare():
    a = request.args.get("a")
    b = request.args.get("b")
    state_a = STATES.get(a) if a in STATES else None
    state_b = STATES.get(b) if b in STATES else None
    return render_template("compare.html", username=session["username"], states=STATES, a=a, b=b, state_a=state_a, state_b=state_b)

@app.route("/itinerary", methods=["GET", "POST"])
@login_required
def itinerary():
    plan = None
    if request.method == "POST":
        try:
            days = int(request.form.get("days", "5"))
        except Exception:
            days = 5
        themes = request.form.getlist("themes")
        region = request.form.get("region") or "Any"
        pace = request.form.get("pace") or "balanced"

        candidates = list(STATES.keys())
        if region != "Any":
            candidates = [s for s in candidates if get_meta(s)["region"] == region]
        if themes:
            candidates = [s for s in candidates if any(t in get_meta(s)["themes"] for t in themes)]

        random.shuffle(candidates)
        if not candidates:
            candidates = list(STATES.keys())
            random.shuffle(candidates)

        # Simple generator: 1 state per day, reuse if days > candidates
        chosen = [candidates[i % len(candidates)] for i in range(max(1, days))]
        plan = [{"day": i + 1, "state": s, "tag": STATES[s]["tag"], "emoji": STATES[s]["emoji"], "theme": ", ".join(get_meta(s)["themes"][:3])} for i, s in enumerate(chosen)]

    regions = sorted({m["region"] for m in STATE_META.values() if m.get("region")})
    theme_set = sorted({t for m in STATE_META.values() for t in m.get("themes", [])})
    return render_template("itinerary.html", username=session["username"], plan=plan, regions=regions, themes=theme_set)

@app.route("/api/random", methods=["GET"])
@login_required
def random_state():
    name = random.choice(list(STATES.keys()))
    return jsonify({"name": name})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "app": "incredible-india-tourism"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")