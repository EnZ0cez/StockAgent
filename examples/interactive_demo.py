import asyncio
import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.conversation_manager import ConversationManager
from config import settings, validate_settings

async def interactive_mode():
    """Interactive mode for real-time conversation"""
    print("🤖 Stock Analysis AI Agent - Interactive Mode")
    print("=" * 60)
    print("Type 'quit' to exit, 'reset' to clear conversation")
    print("-" * 60)
    
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
    
    print("\n👋 Hello! I'm your Stock Analysis AI Agent.")
    print("I can help you analyze stocks, compare investments, and answer questions about the market.")
    print("\nTry asking me things like:")
    print("• 'Analyze AAPL stock'")
    print("• 'What are the risk factors for Tesla?'")
    print("• 'Compare Apple and Microsoft'")
    print("• 'Explain P/E ratios'")
    print("\nWhat would you like to know?")
    print("-" * 60)
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Have a great day!")
                break
            
            # Check for reset command
            if user_input.lower() == 'reset':
                response = conversation_manager.reset_conversation()
                print(f"🤖 Agent: {response['message']}")
                continue
            
            # Skip empty input
            if not user_input:
                continue
            
            # Process the message
            print("🤖 Agent: Thinking...")
            response = await conversation_manager.process_message(user_input)
            
            # Display response
            print(f"🤖 Agent: {response['message']}")
            
            # Show additional data if available
            if response.get('data'):
                data = response['data']
                if data.get('type') == 'new_analysis' and data.get('analysis_result'):
                    analysis = data['analysis_result']
                    print(f"\n📊 Analysis Summary:")
                    print(f"   Recommendation: {analysis.get('recommendation', 'N/A')}")
                    print(f"   Confidence: {analysis.get('confidence_score', 0):.2f}")
                    print(f"   Risk Level: {analysis.get('risk_level', 'N/A')}")
                    
                    # Show report paths if available
                    reports = analysis.get('reports', {})
                    if reports.get('pdf_path'):
                        print(f"   PDF Report: {reports['pdf_path']}")
                    if reports.get('json_path'):
                        print(f"   JSON Report: {reports['json_path']}")
                
                elif data.get('type') == 'comparison' and data.get('comparison_data'):
                    print(f"\n📈 Comparison Data Available")
                    
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Have a great day!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")

async def batch_analysis():
    """Batch analysis example for multiple stocks"""
    print("📊 Batch Analysis Example")
    print("=" * 50)
    
    # Stocks to analyze
    stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    conversation_manager = ConversationManager()
    
    print(f"Analyzing {len(stocks)} stocks...")
    
    for stock in stocks:
        print(f"\n📈 Analyzing {stock}...")
        
        query = f"Analyze {stock} stock"
        response = await conversation_manager.process_message(query)
        
        if response['success']:
            analysis_result = response.get('data', {}).get('analysis_result', {})
            print(f"   Recommendation: {analysis_result.get('recommendation', 'N/A')}")
            print(f"   Confidence: {analysis_result.get('confidence_score', 0):.2f}")
            
            # Show report paths
            reports = analysis_result.get('reports', {})
            if reports.get('pdf_path'):
                print(f"   PDF: {reports['pdf_path']}")
            if reports.get('json_path'):
                print(f"   JSON: {reports['json_path']}")
        else:
            print(f"   ❌ Analysis failed: {response.get('message', 'Unknown error')}")
        
        # Reset conversation for next stock
        conversation_manager.reset_conversation()
        
        # Small delay between analyses
        await asyncio.sleep(2)
    
    print(f"\n✅ Batch analysis completed!")

async def main():
    """Main function to choose mode"""
    print("🚀 Stock Analysis AI Agent")
    print("=" * 50)
    print("Choose a mode:")
    print("1. Interactive Mode")
    print("2. Batch Analysis Demo")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nSelect mode (1-3): ").strip()
            
            if choice == '1':
                await interactive_mode()
                break
            elif choice == '2':
                await batch_analysis()
                break
            elif choice == '3':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())