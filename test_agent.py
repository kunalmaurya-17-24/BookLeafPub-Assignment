import time
from agent import run_customer_bot

def test_flow():
    print("🧪 Starting End-to-End Tests for BookLeaf AI Agent...\n")


    print("Test 1: WhatsApp Identity & Status Check")
    print("User: 'Hi, what is the status of my book Whimsical Verses?'")
    response1 = run_customer_bot(
        user_input="Hi, what is the status of my book Whimsical Verses?",
        platform="whatsapp",
        sender_id="+91 9876543210"
    )
  
    print(f"Bot: {str(response1)}\n")


    print("Test 2: FAQ Knowledge Base Search")
    print("User: 'How do royalties work for the 21-day challenge?'")
    response2 = run_customer_bot(
        user_input="How do royalties work for the 21-day challenge?",
        platform="web",
        sender_id="user_123"
    )
    print(f"Bot: {str(response2)}\n")


    print("Test 3: Low Confidence / Human Handover")
    print("User: 'I want to sue you for copyright infringement because my dog ate my manuscript.'")
    response3 = run_customer_bot(
        user_input="I want to sue you for copyright infringement because my dog ate my manuscript.",
        platform="email",
        sender_id="grumpy_author@mail.com"
    )
    print(f"Bot: {str(response3)}\n")

if __name__ == "__main__":
    test_flow()
