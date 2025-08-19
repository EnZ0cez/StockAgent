import asyncio
import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.conversation_manager import ConversationManager
from config import settings, validate_settings

async def main():
    """Main example demonstrating the stock analysis agent"""
    print("🚀 Stock Analysis AI Agent Demo")
    print("=" * 50)
    
    # Validate configuration
    try:
        validate_settings()
        print("✅ Configuration validated successfully")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your .env file and ensure all required API keys are set.")
        return
    
    # Initialize conversation manager
    conversation_manager = ConversationManager()
    
    # Example conversations
    example_queries = [
        "Analyze AAPL stock for the past year",
        "What are the main risk factors for this investment?",
        "How might this stock perform if interest rates rise?",
        "Compare AAPL with MSFT and GOOGL",
        "What's the difference between growth and value investing?"
    ]
    
    print("\n📊 Starting conversation examples...")
    print("-" * 50)
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n--- Example {i}: {query} ---")
        
        # Process the query
        response = await conversation_manager.process_message(query)
        
        print(f"Response: {response['message']}")
        
        if response.get('data'):
            data = response['data']
            print(f"Data Type: {data.get('type', 'unknown')}")
            
            if data.get('type') == 'new_analysis' and data.get('analysis_result'):
                analysis = data['analysis_result']
                print(f"Recommendation: {analysis.get('recommendation', 'N/A')}")
                print(f"Confidence: {analysis.get('confidence_score', 0):.2f}")
        
        # Add a small delay between examples
        await asyncio.sleep(1)
    
    # Show conversation summary
    summary = conversation_manager.get_conversation_summary()
    print(f"\n📈 Conversation Summary:")
    print(f"Total messages: {summary['total_messages']}")
    print(f"Current symbol: {summary['current_symbol']}")
    print(f"Analysis complete: {summary['analysis_complete']}")
    
    print("\n✅ Demo completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())