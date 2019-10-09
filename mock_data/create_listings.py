from listings.models import Listing
import random
from random import randint
from events.models import Event
from regions.models import Region
from accounts.models import User


def random_bands():
    number_of_bands = randint(1,3)
    bands = ["The Beatles", "Elvis Presley", "Michael Jackson", "Madonna", "Elton John", "Led Zeppelin", "Pink Floyd", "Mariah Carey", "Celine Dion", "AC/DC", "Whitney Houston", "Queen", "The Rolling Stones", "ABBA", "Rihanna", "Taylor Swift", "Eminem", "Garth Brooks", "Eagles", "U2", "Billy Joel", "Phil Collins", "Aerosmith", "Frank Sinatra", "Barbra Streisand", "Genesis", "Neil Diamond", "Kanye West", "Bruce Springsteen", "Bee Gees", "Julio Iglesias", "Dire Straits", "Metallica", "Jay-Z", "Bon Jovi", "Britney Spears", "Rod Stewart", "Fleetwood Mac", "George Strait", "Backstreet Boys", "Guns N' Roses", "Prince (musician)", "Paul McCartney", "Kenny Rogers", "Janet Jackson", "Chicago", "The Carpenters", "Bob Dylan", "George Michael", "Bryan Adams", "Def Leppard", "Cher", "Lionel Richie", "Olivia Newton-John", "Stevie Wonder", "Linda Ronstadt", "Tina Turner", "Donna Summer", "The Beach Boys", "The Who", "Barry White", "Katy Perry", "Santana", "Earth, Wind & Fire", "Lady Gaga", "Shania Twain", "R.E.M.", "Bruno Mars", "B'z", "Van Halen", "Red Hot Chili Peppers", "Foreigner", "The Doors", "Reba McEntire", "Meat Loaf", "Barry Manilow", "Tom Petty", "Johnny Hallyday", "The Black Eyed Peas", "Beyoncé", "Journey", "Kenny G", "Enya", "Robbie Williams", "Alabama", "Green Day", "Tupac Shakur", "Nirvana", "The Police", "Bob Marley", "Kiss", "Depeche Mode", "Aretha Franklin"]
    chosen_bands = []
    for i in range(number_of_bands):
        chosen_bands.append(random.choice(bands))
        return ", ".join(chosen_bands)


def get_random_event():
    if randint(0,1) == 0:
        return None
    events = Event.objects.all()
    return random.choice(events)

def get_random_user():
    users = User.objects.all()
    return random.choice(users)

chicago = Region.objects.first()

for i in range(5000):
    listing = Listing()
    listing.ticket_total = randint(1,10)
    listing.price = randint(1, 500)
    listing.description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    listing.event = get_random_event()
    if listing.event is None:
        listing.bands = random_bands()
        listing.venue = 'Random Venue'
    listing.title = '%s tickets to %s' % (listing.ticket_total, listing.get_band_display())
    listing.region = chicago
    listing.seller = get_random_user()
    listing.save()
