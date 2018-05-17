
from src.app import create_app
from src.db import *
import src.config as config


def create_roles():
    role1 = Role(name=Name("admin"))
    role1.save()

    role2 = Role(name=Name("OC"))
    role2.save()

    role3 = Role(name=Name("NC"))
    role3.save()

    role4 = Role(name=Name("dummyrole"))
    role4.save()

    user1 = User(name=Name("admin"), email=Email("outreach-admin@vlabs.ac.in"), role = role1)
    user1.save()

    user2 = User(name=Name("dummyuseroc"), email=Email("dummyuseroc@vlabs.ac.in"), role = role2 )
    user2.save()

    user3 = User(name=Name("dummyusernc"), email=Email("dummyusernc@vlabs.ac.in"), role = role3 )
    user3.save()

    centre = NodalCentre(name="dummycentre", location="dummylocation",
                                   created_by=user1)

    centre.save()

def create_status():
    status1 = Status(name=Name("Upcoming"))
    status1.save()

    status2 = Status(name=Name("Pending for Approval"))
    status2.save()

    status3 = Status(name=Name("Approved"))
    status3.save()

    status4 = Status(name=Name("Rejected"))
    status4.save()

    status5 = Status(name=Name("Pending for Upload"))
    status5.save()

    status6 = Status(name=Name("Cancel"))
    status6.save()


if __name__ == "__main__":
    db.create_all(app=create_app(config))
    create_roles()
    create_status()
