from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data_setup import Category, Base, Item, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# # Create dummy user
User1 = User(name="abc", email="abc@qq.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/' +
             '18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# first category
category1 = Category(name="Elementary School")

session.add(category1)
session.commit()

item1 = Item(name="Aukamm Elementary School", description="Currently, there are 250 elementary\
 students in grades K through 5 attending Aukamm Elementary on the Wiesbaden Air Base. \
 The base was originally an air base for the German Luftwaffe during World War II.", \
 category=category1, user=User1)

session.add(item1)
session.commit()

item2 = Item(name="Mason-Rice Elementary", description="In the 90's, Massachusetts set out to\
 reform public education to bring about a student population that was better educated and \
 performed better on achievement tests. Nowhere is this appreciated more than at Mason-Rice \
 Elementary (MRE) where the third, fourth, and fifth graders outperformed all of the peers in their state.",
  category=category1, user=User1)

session.add(item2)
session.commit()

# second category
category2 = Category(name="Middle School")

session.add(category2)
session.commit()

item1 = Item(name=" Community Day Charter School", description="Community Day Charter was \
    founded in 1995 and was one of the first charter schools in Massachusetts. It began with \
    grades K-3 and added a grade every year thereafter until it had all grades K-8.", 
    category=category2, user=User1)

session.add(item1)
session.commit()

item2 = Item(name="Stowe Middle School", description="Stowe Middle School is a school \
    for grades 6-8. The program at Stowe is rigorous, but the school recognizes the \
    importance of more than just academics. All students are required to perform four \
    hours of community service and many perform more service than is required. \
    Personalized classes are provided so that students can build relationships with \
    other students, as well as staff and faculty.", category=category2, user=User1)

session.add(item2)
session.commit()

# third category
category3 = Category(name="High School")

session.add(category3)
session.commit()

item1 = Item(name="Pine View School", description="The curriculum at Pine View \
    School mixes traditional classroom learning with independent study, mini-courses \
    and ungraded classes. Pine View School places a strong emphasis on parent \
    involvement through volunteering and fundraising opportunities, open houses, \
    newsletters and field trips. Students must maintain a minimum grade point average \
    and complete advanced foreign language courses to graduate. Extracurricular \
    activities at Pine View include the programming and rowing clubs, Model United \
    Nations and National Honor Society.", category=category3, user=User1)

session.add(item1)
session.commit()

item2 = Item(name="Design and Architecture Senior High", description="Academic programs \
    at Design and Architecture Senior High (DASH) include fashion, entertainment, \
    visual communications, fine art, architecture and industrial design. Students \
    at DASH combine courses from their chosen programs with traditional math, \
    science and language arts courses offered with honors and AP options. Admittance \
    to Design and Architecture Senior High requires online and in-person auditions and \
    an optional workshop. Parents can participate in the school's Parent Teacher Student Association.", 
    category=category3, user=User1)

session.add(item2)
session.commit()

print "added category items!"
