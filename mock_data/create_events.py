import random
from random import randrange
from datetime import timedelta
from datetime import datetime
from random import randint
from events.models import Venue, Event
from regions.models import Region
from accounts.models import User


def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

def random_bands():
    number_of_bands = randint(1,3)
    bands = ["The Beatles", "Elvis Presley", "Michael Jackson", "Madonna", "Elton John", "Led Zeppelin", "Pink Floyd", "Mariah Carey", "Celine Dion", "AC/DC", "Whitney Houston", "Queen", "The Rolling Stones", "ABBA", "Rihanna", "Taylor Swift", "Eminem", "Garth Brooks", "Eagles", "U2", "Billy Joel", "Phil Collins", "Aerosmith", "Frank Sinatra", "Barbra Streisand", "Genesis", "Neil Diamond", "Kanye West", "Bruce Springsteen", "Bee Gees", "Julio Iglesias", "Dire Straits", "Metallica", "Jay-Z", "Bon Jovi", "Britney Spears", "Rod Stewart", "Fleetwood Mac", "George Strait", "Backstreet Boys", "Guns N' Roses", "Prince (musician)", "Paul McCartney", "Kenny Rogers", "Janet Jackson", "Chicago", "The Carpenters", "Bob Dylan", "George Michael", "Bryan Adams", "Def Leppard", "Cher", "Lionel Richie", "Olivia Newton-John", "Stevie Wonder", "Linda Ronstadt", "Tina Turner", "Donna Summer", "The Beach Boys", "The Who", "Barry White", "Katy Perry", "Santana", "Earth, Wind & Fire", "Lady Gaga", "Shania Twain", "R.E.M.", "Bruno Mars", "B'z", "Van Halen", "Red Hot Chili Peppers", "Foreigner", "The Doors", "Reba McEntire", "Meat Loaf", "Barry Manilow", "Tom Petty", "Johnny Hallyday", "The Black Eyed Peas", "Beyoncé", "Journey", "Kenny G", "Enya", "Robbie Williams", "Alabama", "Green Day", "Tupac Shakur", "Nirvana", "The Police", "Bob Marley", "Kiss", "Depeche Mode", "Aretha Franklin"]
    chosen_bands = []
    for i in range(number_of_bands):
        chosen_bands.append(random.choice(bands))
        return ", ".join(chosen_bands)

def random_venue():
    venues = Venue.objects.all()
    return random.choice(venues)

user = User.objects.first()
chicago = Region.objects.first()

for i in range(50):
      event = Event()
      event.start_time = random_date(datetime.now(), datetime.now()+timedelta(weeks=24))
      event.bands = random_bands()
      event.venue = random_venue()
      event.name = "%s @ %s" % (event.bands, event.venue)
      event.region = chicago
      event.user = user
      event.save()
