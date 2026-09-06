import pytest
from faker import Faker
fake = Faker()
from jsonschema import validate
user_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string"},
        "gender": {"type": "string", "enum": ["male", "female"]},   # what are the valid gender values GoRest accepts?
        "status": {"type": "string", "enum": ["active", "inactive"]},   # same question for status
    },
    "required": ["id", "name", "email", "gender", "status"]   # which keys must be present?
}
def build_user_payload():
  create_payload = {
      "name" : "Siva",
      "email" : fake.email(),
      "gender" : "Female",
      "status" : "active"
  }
  return create_payload
def test_user_lifecycle(api_request_context):
  #--- Create ---
  create_payload = build_user_payload()
  create_response = api_request_context.post("users", data=create_payload)
  assert create_response.status == 201, f"Expected 201, got {create_response.status}"
  created_user = create_response.json()
  user_id = created_user["id"]

  #-- Read--
  get_response = api_request_context.get(f"users/{user_id}")
  assert get_response.status == 200
  fetched_user = get_response.json()
  #print(fetched_user)
  #assert len(fetched_user) > 0
  #first_user = fetched_user[0]
  assert fetched_user.get("id") == created_user["id"]
  assert fetched_user.get("name") == created_user["name"]
  assert fetched_user.get("email") == created_user["email"]
  assert fetched_user.get("gender") == created_user["gender"]
  assert fetched_user.get("status") == created_user["status"]

  validate(instance=fetched_user, schema=user_schema)
  #-- Update--(Put)
  update_payload = {
    "name" : "Skanda"
  }
  update_response = api_request_context.put(f"users/{user_id}", data=update_payload)
  assert update_response.status == 200
  updated_user = update_response.json()
  assert updated_user["name"] == update_payload["name"]

  # -- Delete --
  delete_response = api_request_context.delete(f"users/{user_id}")
  assert delete_response.status == 204

  #Verify Deletion
  verify_response = api_request_context.get(f"users/{user_id}")
  assert verify_response.status == 404

def test_create_user_unauthorized (unauthenticated_request_context):
  create_payload = build_user_payload()
  negative_test = unauthenticated_request_context.post("users", data=create_payload)
  assert negative_test.status == 401

@pytest.mark.parametrize("field_to_break, bad_value", [ ("email", ""),
                                                        ("gender", "notarealgender")
                                                        ])
def test_create_user_invalid_payload(api_request_context, field_to_break, bad_value):
    create_payload = build_user_payload()
    create_payload[field_to_break] = bad_value
    invalid_value = api_request_context.post("users", data=create_payload)
    assert invalid_value.status == 422
    error_body = invalid_value.json()
    assert error_body[0]["field"] == field_to_break




