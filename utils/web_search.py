import requests
import streamlit as st

def search_web(query: str, tavily_key: str) -> str:
    """
    Search web using Tavily API
    
    Args:
        query: Search query
        tavily_key: Tavily API key
        
    Returns:
        str: Compiled search results with sources
    """
    try:
        payload = {
            "api_key": tavily_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": 5,
            "include_answer": True
        }
        
        response = requests.post(
            "https://api.tavily.com/search",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        results = response.json()
        
        # Compile search results
        evidence = ""
        
        # Add the AI-generated answer if available
        if 'answer' in results:
            evidence += f"Summary: {results['answer']}\n\n"
        
        # Add individual search results
        for result in results.get('results', [])[:3]:
            content = result.get('content', '')
            url = result.get('url', '')
            title = result.get('title', '')
            
            if content:
                evidence += f"Source: {title}\n{content}\nURL: {url}\n\n"
        
        return evidence if evidence else "No relevant information found."
        
    except requests.exceptions.RequestException as e:
        st.warning(f"Search API error: {str(e)}")
        return "Search temporarily unavailable."
    except Exception as e:
        st.warning(f"Search error: {str(e)}")
        return "Error performing search."