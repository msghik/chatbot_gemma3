import requests
import json
import sys

# --- CONFIGURATION ---
BASE_URL = "http://127.0.0.1:8000"
ADMIN_USER = {"username": "admin", "password": "admin"}
FOO_USER = {"username": "foo", "password": "foo"}

def run_tests():
    """Main function to orchestrate the API tests."""
    print("🚀 Starting Chatbot API Test Suite...")
    
    # 1. Authenticate both users and get their tokens
    print("\nStep 1: Authenticating users...")
    admin_token = get_jwt_token(ADMIN_USER)
    foo_token = get_jwt_token(FOO_USER)

    if not admin_token or not foo_token:
        print("\n❌ Test failed: Could not authenticate one or more users.")
        print("👉 Please ensure you have created both users with the correct passwords.")
        return

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    foo_headers = {"Authorization": f"Bearer {foo_token}"}
    print("✅ Users authenticated successfully.")

    # 2. Admin creates a session and has a conversation
    print("\nStep 2: Testing Admin's conversation...")
    admin_session_id = create_chat_session(admin_headers)
    ask_question(
        headers=admin_headers,
        session_id=admin_session_id,
        question="My name is Admin, and my favorite color is blue.",
        should_contain=None # This is the first message, no context to check yet
    )
    ask_question(
        headers=admin_headers,
        session_id=admin_session_id,
        question="What is my name?",
        should_contain="Admin"
    )
    ask_question(
        headers=admin_headers,
        session_id=admin_session_id,
        question="What is my favorite color?",
        should_contain="blue"
    )
    print("✅ Admin's conversation test passed.")

    # 3. Foo checks for sessions (should have none) and starts their own
    print("\nStep 3: Testing Foo's conversation and data isolation...")
    sessions = list_chat_sessions(foo_headers)
    if sessions:
        print(f"❌ Test failed: User 'foo' should have 0 sessions but found {len(sessions)}.")
        return
    print("  - Verified 'foo' has no access to 'admin' sessions.")

    foo_session_id = create_chat_session(foo_headers)
    ask_question(
        headers=foo_headers,
        session_id=foo_session_id,
        question="My name is Foo, and I like the color green.",
        should_contain=None
    )
    ask_question(
        headers=foo_headers,
        session_id=foo_session_id,
        question="What is my favorite color?",
        should_contain="green" # Should know 'green'
    )
    ask_question(
        headers=foo_headers,
        session_id=foo_session_id,
        question="Do you know my name?",
        should_contain="Foo" # Should know 'Foo'
    )
    print("✅ Foo's conversation test passed.")


    # 4. Re-check Admin's session to ensure it wasn't affected by Foo's chat
    print("\nStep 4: Re-testing Admin's session to ensure history is isolated...")
    ask_question(
        headers=admin_headers,
        session_id=admin_session_id,
        question="Just to be sure, what is my favorite color?",
        should_contain="blue" # Must still be 'blue', not 'green'
    )
    print("✅ Admin's conversation history remains isolated and correct.")
    
    # 5. Admin deletes their session, and we verify it's gone
    print("\nStep 5: Testing session deletion...")
    delete_chat_session(admin_headers, admin_session_id)
    sessions = list_chat_sessions(admin_headers)
    if sessions:
        print(f"❌ Test failed: 'admin' user should have 0 sessions after deletion but found {len(sessions)}.")
        return
    print("  - Verified 'admin' session was deleted.")
    
    # 6. Check that Foo's session still exists
    sessions = list_chat_sessions(foo_headers)
    if not sessions or sessions[0]['id'] != foo_session_id:
        print(f"❌ Test failed: 'foo' user's session was deleted incorrectly.")
        return
    print("  - Verified 'foo' session was not affected by admin's deletion.")
    
    print("\n🎉 All tests passed successfully! 🎉")
    print("\n👉 You can now check your Redis database. You should only see keys related to 'foo's session.")
    print("   Example redis-cli command: SCAN 0 MATCH \"chat:*\"")


# --- HELPER FUNCTIONS ---

def get_jwt_token(user_credentials):
    """Logs in a user and returns the access token."""
    try:
        response = requests.post(f"{BASE_URL}/api/token/", data=user_credentials)
        response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
        return response.json().get("access")
    except requests.exceptions.RequestException as e:
        print(f"  - Error getting token for {user_credentials['username']}: {e}")
        return None

def list_chat_sessions(headers):
    """Fetches all chat sessions for the authenticated user."""
    try:
        response = requests.get(f"{BASE_URL}/api/chats/", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  - Error listing chat sessions: {e}")
        sys.exit(1) # Exit if we can't perform a basic operation

def create_chat_session(headers):
    """Creates a new chat session and returns its ID."""
    try:
        print("  - Creating a new chat session...")
        response = requests.post(f"{BASE_URL}/api/chats/", headers=headers)
        response.raise_for_status()
        session_id = response.json().get("id")
        print(f"  - Session created with ID: {session_id}")
        return session_id
    except requests.exceptions.RequestException as e:
        print(f"  - Error creating chat session: {e}")
        sys.exit(1)

def ask_question(headers, session_id, question, should_contain):
    """Sends a question to a session and validates the response."""
    try:
        print(f'  - Asking: "{question}"')
        response = requests.post(f"{BASE_URL}/api/chats/{session_id}/", headers=headers, json={"message": question})
        response.raise_for_status()
        answer = response.json().get("answer", "")
        print(f'  - Bot replied: "{answer}"')

        if should_contain and should_contain.lower() not in answer.lower():
            print(f"❌ Test failed: Bot's answer did not contain '{should_contain}'.")
            sys.exit(1) # Stop the test script on failure
        
    except requests.exceptions.RequestException as e:
        print(f"  - Error asking question: {e}")
        sys.exit(1)

def delete_chat_session(headers, session_id):
    """Deletes a specific chat session."""
    try:
        print(f"  - Deleting session ID: {session_id}...")
        response = requests.delete(f"{BASE_URL}/api/chats/{session_id}/", headers=headers)
        response.raise_for_status()
        print(f"  - Session {session_id} deleted.")
    except requests.exceptions.RequestException as e:
        print(f"  - Error deleting chat session: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
