#!/usr/bin/env python3
"""
Simple runner script for the SampleStrategyPipeline demo applications.

This script provides an easy way to run either the mock demo or the real demo.
"""

import sys
import os
import subprocess

def run_mock_demo():
    """Run the mock demo application."""
    print("🎯 Running Mock Demo (No external dependencies required)")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, "mock_demo_app.py"
        ], cwd=os.path.dirname(__file__), check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Mock demo failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running mock demo: {e}")
        return False

def run_real_demo():
    """Run the real demo application (requires OpenWebUI)."""
    print("🎯 Running Real Demo (Requires OpenWebUI running)")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, "demo_app.py"
        ], cwd=os.path.dirname(__file__), check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Real demo failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running real demo: {e}")
        return False

def run_event_timeline_demo():
    """Run the event timeline demo application."""
    print("🎯 Running Event Timeline Demo (Custom schema-based prompts)")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, "event_timeline_demo.py"
        ], cwd=os.path.dirname(__file__), check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Event timeline demo failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running event timeline demo: {e}")
        return False

def run_question_answer_demo():
    """Run the question-answer demo application."""
    print("🎯 Running Question-Answer Demo (Conversational AI with schema)")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, "question_answer_demo.py"
        ], cwd=os.path.dirname(__file__), check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Question-answer demo failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running question-answer demo: {e}")
        return False

def run_question_answer_response_demo():
    """Run the question-answer response demo application."""
    print("🎯 Running Question-Answer Response Demo (Q&A Response Strategy)")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, "question_answer_response_demo.py"
        ], cwd=os.path.dirname(__file__), check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Question-answer response demo failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running question-answer response demo: {e}")
        return False

def run_question_answer_xml_demo():
    """Run the question-answer XML output demo application."""
    print("🎯 Running Question-Answer XML Output Demo (Q&A XML Strategy)")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, "question_answer_xml_output_demo.py"
        ], cwd=os.path.dirname(__file__), check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Question-answer XML demo failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running question-answer XML demo: {e}")
        return False

def run_qa_strategy_pipeline_demo():
    """Run the QA strategy pipeline demo application."""
    print("🎯 Running QA Strategy Pipeline Demo (Complete Q&A Workflow)")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, "qa_strategy_pipeline_demo.py"
        ], cwd=os.path.dirname(__file__), check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ QA strategy pipeline demo failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running QA strategy pipeline demo: {e}")
        return False

def main():
    """Main entry point."""
    print("🚀 SampleStrategyPipeline Demo Runner")
    print("=" * 40)
    print("Choose a demo to run:")
    print("1. Mock Demo (recommended - no external dependencies)")
    print("2. Real Demo (requires OpenWebUI running)")
    print("3. Event Timeline Demo (custom schema-based prompts)")
    print("4. Question-Answer Demo (conversational AI with schema)")
    print("5. Question-Answer Response Demo (Q&A response strategy)")
    print("6. Question-Answer XML Demo (Q&A XML output strategy)")
    print("7. QA Strategy Pipeline Demo (complete Q&A workflow)")
    print("8. All demos")
    print("9. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == "1":
                success = run_mock_demo()
                if success:
                    print("\n✅ Mock demo completed successfully!")
                else:
                    print("\n❌ Mock demo failed!")
                break
                
            elif choice == "2":
                success = run_real_demo()
                if success:
                    print("\n✅ Real demo completed successfully!")
                else:
                    print("\n❌ Real demo failed!")
                break
                
            elif choice == "3":
                success = run_event_timeline_demo()
                if success:
                    print("\n✅ Event timeline demo completed successfully!")
                else:
                    print("\n❌ Event timeline demo failed!")
                break
                
            elif choice == "4":
                success = run_question_answer_demo()
                if success:
                    print("\n✅ Question-answer demo completed successfully!")
                else:
                    print("\n❌ Question-answer demo failed!")
                break
                
            elif choice == "5":
                success = run_question_answer_response_demo()
                if success:
                    print("\n✅ Question-answer response demo completed successfully!")
                else:
                    print("\n❌ Question-answer response demo failed!")
                break
                
            elif choice == "6":
                success = run_question_answer_xml_demo()
                if success:
                    print("\n✅ Question-answer XML demo completed successfully!")
                else:
                    print("\n❌ Question-answer XML demo failed!")
                break
                
            elif choice == "7":
                success = run_qa_strategy_pipeline_demo()
                if success:
                    print("\n✅ QA strategy pipeline demo completed successfully!")
                else:
                    print("\n❌ QA strategy pipeline demo failed!")
                break
                
            elif choice == "8":
                print("\n🔄 Running all demos...")
                print("\n" + "="*60)
                print("MOCK DEMO:")
                print("="*60)
                mock_success = run_mock_demo()
                
                print("\n" + "="*60)
                print("REAL DEMO:")
                print("="*60)
                real_success = run_real_demo()
                
                print("\n" + "="*60)
                print("EVENT TIMELINE DEMO:")
                print("="*60)
                timeline_success = run_event_timeline_demo()
                
                print("\n" + "="*60)
                print("QUESTION-ANSWER DEMO:")
                print("="*60)
                qa_success = run_question_answer_demo()
                
                print("\n" + "="*60)
                print("QUESTION-ANSWER RESPONSE DEMO:")
                print("="*60)
                qa_response_success = run_question_answer_response_demo()
                
                print("\n" + "="*60)
                print("QUESTION-ANSWER XML DEMO:")
                print("="*60)
                qa_xml_success = run_question_answer_xml_demo()
                
                print("\n" + "="*60)
                print("QA STRATEGY PIPELINE DEMO:")
                print("="*60)
                qa_pipeline_success = run_qa_strategy_pipeline_demo()
                
                if mock_success and real_success and timeline_success and qa_success and qa_response_success and qa_xml_success and qa_pipeline_success:
                    print("\n✅ All demos completed successfully!")
                else:
                    print(f"\n⚠️  Mock demo: {'✅ Success' if mock_success else '❌ Failed'}")
                    print(f"Real demo: {'✅ Success' if real_success else '❌ Failed'}")
                    print(f"Event timeline demo: {'✅ Success' if timeline_success else '❌ Failed'}")
                    print(f"Question-answer demo: {'✅ Success' if qa_success else '❌ Failed'}")
                    print(f"Question-answer response demo: {'✅ Success' if qa_response_success else '❌ Failed'}")
                    print(f"Question-answer XML demo: {'✅ Success' if qa_xml_success else '❌ Failed'}")
                    print(f"QA strategy pipeline demo: {'✅ Success' if qa_pipeline_success else '❌ Failed'}")
                break
                
            elif choice == "9":
                print("👋 Goodbye!")
                sys.exit(0)
                
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, 4, 5, 6, 7, 8, or 9.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
