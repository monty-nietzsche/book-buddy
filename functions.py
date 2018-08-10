import urllib
import json
import textwrap
import random
import string


def generateComments():
    '''
    returns a gibberish sentence to simulate a comment in the sample data
    initially filling the database. The sentence consists of 4 words.
    '''
    return ' '.join([''.join([random.choice(string.ascii_letters) for n in
                     xrange(random.randint(4, 10))]) for x in xrange(5)]).\
        capitalize()+"."


def getBookDetails(isbn):
    '''
    takes as input the isbn of a book and queries the Google Books API to
    get the book details such as title, author, image and so on.

    args: isbn (string) representing the unique ISBN of a book

    returns: a dictionary 'Book' containing all available details of the book
    with the ISBN specified in args, if the API request is successful. If not,
    return a dictionary 'Book' containing either a unique key 'error' if the
    request fails, or 'nobook' if the API response contains no book with the
    specific ISBN
    '''

    base_api_link = "https://www.googleapis.com/books/v1/volumes?key=AIzaSyCQpRsaa8lNlskF-gw1Jsdx1kTn_YVn1aw&q=isbn:"

    f = urllib.urlopen(base_api_link + isbn)
    text = f.read()

    decoded_text = text.decode("utf-8")

    # deserializes decoded_text to a Python object
    obj = json.loads(decoded_text)

    # create a dictionary called 'book' and fill it with data from the json
    # received from GoogleBooks or with an error message
    book = {}
    book["isbn"] = isbn

    # Error retrieving the book with the isbn e.g. exceeded quota or wrong isbn
    if 'error' in obj:

        book["error"] = True

    # The book has a correct isbn but does not exist in Google records
    # Create a key in the dictionary Book called 'nobook' and set it to True
    elif (int(obj["totalItems"]) == 0):

        book["nobook"] = True

    # Google Books API sends back a json variable with the book details
    else:

        volume_info = obj["items"][0]
        info = obj["items"][0]["volumeInfo"]
        book = {}
        book["title"] = info["title"]

        # If Google Books does not send back an author, use 'Unknown'
        if 'authors' not in info:
            book["author"] = "Unknown"
        else:
            book["author"] = ",".join(info["authors"])

        # If Google Books does not send back a language, use 'en' (english)
        if 'language' not in info:
            book["language"] = "en"
        else:
            book["language"] = info["language"]

        # If Google Books does not send back a pageCount, use '0'
        if 'pageCount' not in info:
            book["pageCount"] = 0
        else:
            book["pageCount"] = info["pageCount"]

        # If Google Books does not send back an image, use a placeholder
        if 'imageLinks' not in info:
                    book["image"] = "http://ghachem.net/test.jpg"
        else:
            if 'thumbnail' not in info["imageLinks"]:
                book["image"] = "http://ghachem.net/test.jpg"
            else:
                book["image"] = info["imageLinks"]["thumbnail"]

        # If Google Books does not send back description, use 'No description'
        if 'searchInfo' not in volume_info:
                    book["description"] = "No description!"
        else:
            book["description"] = textwrap.fill(
                volume_info["searchInfo"]["textSnippet"],
                width=100)

        # If Google Books does not send back a category, use 'Other'
        if 'categories' not in info:
            book["category"] = "Other"
        else:
            book["category"] = info["categories"][0]

    return book


def getLanguagesList():
    '''
    returns a dictionary of correspondance between standard language
    abbreviations and the name of the lanugage. e.g. 'en' is an
    abbreviation corresponding to 'english'. The response of Google Books
    API returns an abbreviation while the name of the language is displayed
    on the website.
    '''
    LanguageList = {'ab': 'Abkhazian',  'aa': 'Afar', 'af': 'Afrikaans',
                    'ak': 'Akan', 'sq': 'Albanian', 'am': 'Amharic',
                    'ar': 'Arabic', 'an': 'Aragonese', 'hy': 'Armenian',
                    'as': 'Assamese', 'av': 'Avaric', 'ae': 'Avestan',
                    'ay': 'Aymara', 'az': 'Azerbaijani', 'bm': 'Bambara',
                    'ba': 'Bashkir', 'eu': 'Basque', 'be': 'Belarusian',
                    'bn': 'Bengali (Bangla)', 'bh': 'Bihari', 'bi': 'Bislama',
                    'bs': 'Bosnian', 'br': 'Breton', 'bg': 'Bulgarian',
                    'my': 'Burmese', 'ca': 'Catalan', 'ch': 'Chamorro',
                    'ce': 'Chechen', 'ny': 'Chichewa,  Chewa,  Nyanja',
                    'zh': 'Chinese', 'zh-Hans': 'Chinese (Simplified)',
                    'zh-Hant': 'Chinese (Traditional)', 'cv': 'Chuvash',
                    'kw': 'Cornish', 'co': 'Corsican', 'cr': 'Cree',
                    'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish',
                    'dv': 'Divehi,  Dhivehi,  Maldivian', 'nl': 'Dutch',
                    'dz': 'Dzongkha', 'en': 'English', 'eo': 'Esperanto',
                    'et': 'Estonian', 'ee': 'Ewe', 'fo': 'Faroese',
                    'fj': 'Fijian', 'fi': 'Finnish', 'fr': 'French',
                    'ff': 'Fula,  Fulah,  Pulaar,  Pular', 'gl': 'Galician',
                    'gd': 'Gaelic (Scottish)', 'gv': 'Gaelic (Manx)',
                    'ka': 'Georgian', 'de': 'German', 'el': 'Greek',
                    'kl': 'Greenlandic', 'gn': 'Guarani', 'gu': 'Gujarati',
                    'ht': 'Haitian Creole', 'ha': 'Hausa', 'he': 'Hebrew',
                    'hz': 'Herero', 'hi': 'Hindi', 'ho': 'Hiri Motu',
                    'hu': 'Hungarian', 'is': 'Icelandic', 'io': 'Ido',
                    'ig': 'Igbo', 'id,  in': 'Indonesian', 'ia': 'Interlingua',
                    'ie': 'Interlingue', 'iu': 'Inuktitut', 'ik': 'Inupiak',
                    'ga': 'Irish', 'it': 'Italian', 'ja': 'Japanese',
                    'jv': 'Javanese', 'kl': 'Kalaallisut,  Greenlandic',
                    'kn': 'Kannada', 'kr': 'Kanuri', 'ks': 'Kashmiri',
                    'kk': 'Kazakh', 'km': 'Khmer', 'ki': 'Kikuyu',
                    'rw': 'Kinyarwanda (Rwanda)', 'rn': 'Kirundi',
                    'ky': 'Kyrgz', 'kv': 'Komi', 'kg': 'Kongo', 'ko': 'Korean',
                    'ku': 'Kurdish', 'kj': 'Kwanyama', 'lo': 'Lao',
                    'la': 'Latin', 'lv': 'Latvian (Lettish)',
                    'li': 'Limburgish (Limburger)', 'ln': 'Lingala',
                    'lt': 'Lithuanian', 'lu': 'Luga-Katanga',
                    'lg': 'Luganda,  Ganda', 'lb': 'Luxembourgish',
                    'gv': 'Manx', 'mk': 'Macedonian', 'mg': 'Malagasy',
                    'ms': 'Malay', 'ml': 'Malayalam', 'mt': 'Maltese',
                    'mi': 'Maori', 'mr': 'Marathi', 'mh': 'Marshallese',
                    'mo': 'Moldavian', 'mn': 'Mongolian', 'na': 'Nauru',
                    'nv': 'Navajo', 'ng': 'Ndonga', 'nd': 'Northern Ndebele',
                    'ne': 'Nepali', 'no': 'Norwegian',
                    'nb': 'Norwegian bokmaol', 'nn': 'Norwegian nynorsk',
                    'ii': 'Nuosu', 'oc': 'Occitan', 'oj': 'Ojibwe',
                    'cu': 'Old Church Slavonic,  Old Bulgarian', 'or': 'Oriya',
                    'om': 'Oromo(Afaan Oromo)', 'os': 'Ossetian', 'pi': 'Pali',
                    'ps': 'Pashto,  Pushto', 'fa': 'Persian (Farsi)',
                    'pl': 'Polish', 'pt': 'Portuguese',
                    'pa': 'Punjabi (Eastern)', 'qu': 'Quechua',
                    'rm': 'Romansh', 'ro': 'Romanian', 'ru': 'Russian',
                    'se': 'Sami', 'sm': 'Samoan', 'sg': 'Sango',
                    'sa': 'Sanskrit', 'sr': 'Serbian', 'sh': 'Serbo-Croatian',
                    'st': 'Sesotho', 'tn': 'Setswana', 'sn': 'Shona',
                    'ii': 'Sichuan Yi', 'sd': 'Sindhi', 'si': 'Sinhalese',
                    'ss': 'Siswati', 'sk': 'Slovak', 'sl': 'Slovenian',
                    'so': 'Somali', 'nr': 'Southern Ndebele', 'es': 'Spanish',
                    'su': 'Sundanese', 'sw': 'Swahili (Kiswahili)',
                    'ss': 'Swati', 'sv': 'Swedish', 'tl': 'Tagalog',
                    'ty': 'Tahitian', 'tg': 'Tajik', 'ta': 'Tamil',
                    'tt': 'Tatar', 'te': 'Telugu', 'th': 'Thai',
                    'bo': 'Tibetan', 'ti': 'Tigrinya', 'to': 'Tonga',
                    'ts': 'Tsonga', 'tr': 'Turkish', 'tk': 'Turkmen',
                    'tw': 'Twi', 'ug': 'Uyghur', 'uk': 'Ukrainian',
                    'ur': 'Urdu', 'uz': 'Uzbek', 've': 'Venda',
                    'vi': 'Vietnamese', 'vo': 'Volapuek', 'wa': 'Wallon',
                    'cy': 'Welsh', 'wo': 'Wolof', 'fy': 'Western Frisian',
                    'xh': 'Xhosa', 'yi,  ji': 'Yiddish', 'yo': 'Yoruba',
                    'za': 'Zhuang,  Chuang', 'zu': 'Zulu'}

    return LanguageList
