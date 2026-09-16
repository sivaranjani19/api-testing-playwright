import pytest

from tests.factories import build_user_payload


def test_post_lifecycle(api_request_context):
  # --- Setup: need a real user to attach the post to ---
  user_payload = build_user_payload()
  user_response = api_request_context.post("users", data=user_payload)
  assert user_response.status == 201
  user_id = user_response.json()["id"]

  #--Create--
  post_payload = {
      "user_id" : user_id,
      "title" : "MyPost",
      "body" : "All is well"
    }
  create_response = api_request_context.post("posts/", data=post_payload)
  assert create_response.status == 201
  post_id = create_response.json()["id"]

  #-- Read--
  get_response = api_request_context.get(f"posts/{post_id}")
  assert get_response.status == 200
  fetched_response = get_response.json()
  assert fetched_response["title"] == "MyPost"

  #-- Update--
  update_payload = {
    "user_id" : user_id,
    "title" : "MyNewPost",
    "body" : "All is well"
  }
  update_response = api_request_context.put(f"posts/{post_id}", data=update_payload)
  assert update_response.status == 200
  fetched_response = update_response.json()
  assert fetched_response["title"] == "MyNewPost"
  #-- Delete--
  delete_response = api_request_context.delete(f"posts/{post_id}")
  assert delete_response.status == 204
  #Veify Deletion
  verify_response = api_request_context.get(f"posts/{post_id}")
  assert verify_response.status == 404

def test_create_post_comment_for_user(api_request_context):
  create_payload = build_user_payload()
  created_user_response = api_request_context.post("users", data=create_payload)
  assert created_user_response.status == 201
  created_user = created_user_response.json()
  user_id = created_user["id"]
  post_payload = {
        "user_id" : user_id,
        "title" : "MyPost",
        "body" : "All is well"
  }
  posts_response = api_request_context.post("posts/", data=post_payload)
  created_post = posts_response.json()
  post_id = created_post["id"]
  assert posts_response.status == 201
  comment_payload = {
      "post_id" : post_id,
      "name" : "Siva",
      "email" : "siva@gmail.com",
      "body" : "All is well always"
    }
  comment_response = api_request_context.post("comments/", data=comment_payload)
  assert comment_response.status == 201


@pytest.mark.parametrize("field_to_break, bad_value", [("title", ""), ("body", "")])
def test_create_post_with_invalid_payload(api_request_context, field_to_break, bad_value):
  user_payload = build_user_payload()
  user_response = api_request_context.post("users", data=user_payload)
  assert user_response.status == 201
  user_id = user_response.json()["id"]

    #--Create--
  post_payload = {
     "user_id" : user_id,
      "title" : "MyPost",
      "body" : "All is well"
    }
  post_payload[field_to_break] = bad_value
  invalid_value = api_request_context.post("posts/", data=post_payload)
  assert invalid_value.status == 422
  error_response = invalid_value.json()
  assert error_response[0]["field"] == field_to_break

def test_create_post_with_invalid_userId(api_request_context):
  post_payload = {
        "user_id" : 999999999,
        "title" : "MyPost",
        "body" : "All is well"
      }
  invalid_value = api_request_context.post("posts/", data=post_payload)
  assert invalid_value.status == 422
  error_response = invalid_value.json()
  assert error_response[0]["field"] == "user"



