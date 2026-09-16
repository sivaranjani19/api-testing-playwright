from faker import Faker
fake = Faker()


def build_user_payload():
  create_payload = {
      "name" : "Siva",
      "email" : fake.email(),
      "gender" : "Female",
      "status" : "active"
  }
  return create_payload