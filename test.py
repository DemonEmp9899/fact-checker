"""
Test script to verify the fact-checker components
"""

from utils.claim_extractor import extract_claims
from utils.web_search import search_web
from utils.verifier import verify_claims

def test_claim_extraction():
    """Test claim extraction functionality"""
    sample_text = """
    The global GDP reached $105 trillion in 2023. 
    Apple's stock price hit $500 in December 2024.
    The average temperature increase since pre-industrial times is 1.1°C.
    """
    
    print("Testing claim extraction...")
    print(f"Sample text: {sample_text}")
    print("\nNote: Add your OpenRouter API key to test")
    
def test_web_search():
    """Test web search functionality"""
    query = "What is the current global GDP?"
    
    print("\nTesting web search...")
    print(f"Query: {query}")
    print("\nNote: Add your Tavily API key to test")

def test_verification():
    """Test full verification pipeline"""
    test_claim = "The global GDP reached $105 trillion in 2023"
    
    print("\nTesting verification pipeline...")
    print(f"Claim: {test_claim}")
    print("\nNote: Add both API keys to test")

if __name__ == "__main__":
    print("=" * 50)
    print("Fact-Checker Component Tests")
    print("=" * 50)
    
    test_claim_extraction()
    test_web_search()
    test_verification()
    
    print("\n" + "=" * 50)
    print("To run full tests, add your API keys and run:")
    print("python test.py")
    print("=" * 50)