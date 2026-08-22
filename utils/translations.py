TRANSLATIONS = {
    "English": {
        "app_title": "Sahaayak",
        "tagline": "Trusted local services. Fair work. Stronger cooperatives.",
        "role_select": "Select Role",
        "customer": "Customer",
        "worker": "Worker",
        "admin": "Admin",
        "emergency": "🚨 Emergency Service",
        "home": "Home",
        "book_service": "Book Service",
        "my_bookings": "My Bookings",
        "logout": "Logout",
        "welcome": "Welcome",
        "search_services": "Search Services",
        "location": "Location",
    },
    "Hindi": {
        "app_title": "सहायक (Sahaayak)",
        "tagline": "भरोसेमंद स्थानीय सेवाएं। उचित काम। मजबूत सहकारी समितियां।",
        "role_select": "भूमिका चुनें",
        "customer": "ग्राहक",
        "worker": "श्रमिक",
        "admin": "व्यवस्थापक",
        "emergency": "🚨 आपातकालीन सेवा",
        "home": "मुख्य पृष्ठ",
        "book_service": "सेवा बुक करें",
        "my_bookings": "मेरी बुकिंग",
        "logout": "लॉग आउट",
        "welcome": "स्वागत है",
        "search_services": "सेवाएं खोजें",
        "location": "स्थान",
    }
}

def t(key, lang="English"):
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"]).get(key, key)
