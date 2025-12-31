"""Gap Analysis Service for Chatbot Conversations"""

from typing import List, Dict, Optional
from app.services.chat import ChatService, get_chat_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GapAnalysisService:
    """Service for analyzing gaps in conversations"""
    
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service
    
    async def analyze_conversation(
        self,
        conversation_id: str
    ) -> Dict:
        """
        Analyze a conversation for gaps and missing information
        
        Args:
            conversation_id: ID of the conversation to analyze
        
        Returns:
            Dictionary with gap analysis results
        """
        try:
            # Get conversation history
            history = await self.chat_service.get_conversation_history(conversation_id)
            
            if not history or not history.messages:
                return {
                    "conversation_id": conversation_id,
                    "status": "empty",
                    "gaps": [],
                    "suggestions": ["Start a conversation to analyze gaps"],
                    "completeness_score": 0
                }
            
            # Analyze gaps
            gaps = []
            suggestions = []
            completeness_score = 100
            
            # Check for common gaps
            user_messages = [msg for msg in history.messages if msg.role == "user"]
            ai_messages = [msg for msg in history.messages if msg.role == "assistant"]
            
            # Gap 1: Missing context
            if len(user_messages) < 2:
                gaps.append({
                    "type": "missing_context",
                    "severity": "medium",
                    "description": "Conversation lacks sufficient context",
                    "suggestion": "Provide more background information or ask follow-up questions"
                })
                completeness_score -= 20
            
            # Gap 2: No follow-up questions
            if len(user_messages) == 1 and len(ai_messages) == 1:
                gaps.append({
                    "type": "no_followup",
                    "severity": "low",
                    "description": "Single exchange without follow-up",
                    "suggestion": "Consider asking follow-up questions to deepen the conversation"
                })
                completeness_score -= 10
            
            # Gap 3: Short responses
            short_responses = [
                msg for msg in ai_messages 
                if len(msg.content) < 50
            ]
            if len(short_responses) > len(ai_messages) * 0.5:
                gaps.append({
                    "type": "short_responses",
                    "severity": "low",
                    "description": "Many responses are quite brief",
                    "suggestion": "Ask for more detailed explanations or examples"
                })
                completeness_score -= 15
            
            # Gap 4: Missing specific details
            detail_keywords = ["how", "why", "what", "when", "where", "example", "specific"]
            has_details = any(
                keyword in msg.content.lower() 
                for msg in user_messages 
                for keyword in detail_keywords
            )
            if not has_details and len(user_messages) > 2:
                gaps.append({
                    "type": "missing_details",
                    "severity": "medium",
                    "description": "Conversation may lack specific details",
                    "suggestion": "Ask specific questions using 'how', 'why', 'what', or request examples"
                })
                completeness_score -= 15
            
            # Gap 5: No action items or next steps
            action_keywords = ["next", "step", "action", "do", "should", "recommend"]
            has_actions = any(
                keyword in msg.content.lower() 
                for msg in user_messages 
                for keyword in action_keywords
            )
            if not has_actions and len(user_messages) > 3:
                gaps.append({
                    "type": "no_action_items",
                    "severity": "low",
                    "description": "No clear action items or next steps identified",
                    "suggestion": "Ask about next steps or actionable recommendations"
                })
                completeness_score -= 10
            
            # Gap 6: Unanswered questions
            question_marks = sum(msg.content.count("?") for msg in user_messages)
            if question_marks > len(ai_messages):
                gaps.append({
                    "type": "unanswered_questions",
                    "severity": "high",
                    "description": "More questions asked than answered",
                    "suggestion": "Review responses to ensure all questions are addressed"
                })
                completeness_score -= 25
            
            # Generate suggestions based on gaps
            if not gaps:
                suggestions.append("✅ Conversation appears complete and well-structured")
            else:
                suggestions.extend([gap["suggestion"] for gap in gaps])
            
            # Calculate overall metrics
            metrics = {
                "total_messages": len(history.messages),
                "user_messages": len(user_messages),
                "ai_messages": len(ai_messages),
                "average_message_length": sum(len(msg.content) for msg in history.messages) / len(history.messages) if history.messages else 0,
                "questions_asked": question_marks,
                "completeness_score": max(0, completeness_score)
            }
            
            return {
                "conversation_id": conversation_id,
                "status": "analyzed",
                "gaps": gaps,
                "suggestions": suggestions,
                "completeness_score": metrics["completeness_score"],
                "metrics": metrics,
                "gap_count": len(gaps),
                "severity_breakdown": {
                    "high": len([g for g in gaps if g["severity"] == "high"]),
                    "medium": len([g for g in gaps if g["severity"] == "medium"]),
                    "low": len([g for g in gaps if g["severity"] == "low"])
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing conversation: {e}", exc_info=True)
            return {
                "conversation_id": conversation_id,
                "status": "error",
                "error": str(e),
                "gaps": [],
                "suggestions": [],
                "completeness_score": 0
            }
    
    async def analyze_all_conversations(self) -> Dict:
        """
        Analyze all conversations for overall patterns
        
        Returns:
            Dictionary with overall gap analysis
        """
        try:
            # Get all conversation summaries
            summaries = await self.chat_service.get_conversation_summaries(limit=100)
            
            if not summaries:
                return {
                    "status": "no_conversations",
                    "total_conversations": 0,
                    "overall_insights": []
                }
            
            # Analyze each conversation
            analyses = []
            for summary in summaries:
                analysis = await self.analyze_conversation(summary.conversation_id)
                analyses.append(analysis)
            
            # Aggregate insights
            total_gaps = sum(len(a.get("gaps", [])) for a in analyses)
            avg_completeness = sum(a.get("completeness_score", 0) for a in analyses) / len(analyses) if analyses else 0
            
            # Find common gaps
            gap_types = {}
            for analysis in analyses:
                for gap in analysis.get("gaps", []):
                    gap_type = gap["type"]
                    gap_types[gap_type] = gap_types.get(gap_type, 0) + 1
            
            common_gaps = sorted(gap_types.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "status": "analyzed",
                "total_conversations": len(summaries),
                "analyzed_conversations": len(analyses),
                "total_gaps_found": total_gaps,
                "average_completeness_score": round(avg_completeness, 2),
                "common_gaps": [
                    {"type": gap_type, "frequency": count} 
                    for gap_type, count in common_gaps
                ],
                "conversation_analyses": analyses
            }
            
        except Exception as e:
            logger.error(f"Error analyzing all conversations: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }


async def get_gap_analysis_service() -> GapAnalysisService:
    """Get gap analysis service instance"""
    chat_service = await get_chat_service()
    return GapAnalysisService(chat_service)

