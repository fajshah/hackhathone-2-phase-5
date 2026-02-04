import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

class PriorityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class EntityExtractor:
    def __init__(self):
        # Patterns for extracting dates
        self.date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',    # YYYY-MM-DD
            r'(today|tomorrow)',                   # Relative dates
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',  # Days of week
            r'(next\s+(week|month|year))',         # Next week/month/year
            r'(in\s+\d+\s+(days?|weeks?|months?|years?))'  # In X days/weeks/months
        ]
        
        # Patterns for extracting priorities
        self.priority_patterns = {
            PriorityLevel.HIGH: [r'\b(high|urgent|important|critical|asap|soonest|top priority)\b'],
            PriorityLevel.MEDIUM: [r'\b(medium|normal|regular|standard|average)\b'],
            PriorityLevel.LOW: [r'\b(low|not urgent|optional|when convenient|whenever)\b']
        }
        
        # Compile patterns for efficiency
        self.compiled_date_patterns = [re.compile(p, re.IGNORECASE) for p in self.date_patterns]
        self.compiled_priority_patterns = {}
        for priority, patterns in self.priority_patterns.items():
            self.compiled_priority_patterns[priority] = [re.compile(p, re.IGNORECASE) for p in patterns]

    def extract_date(self, text: str) -> Optional[datetime]:
        """
        Extract a date from the given text.
        """
        text_lower = text.lower()
        
        # Check for relative dates
        if 'today' in text_lower:
            return datetime.now().replace(hour=23, minute=59, second=0, microsecond=0)
        elif 'tomorrow' in text_lower:
            tomorrow = datetime.now() + timedelta(days=1)
            return tomorrow.replace(hour=23, minute=59, second=0, microsecond=0)
        
        # Check for day of week
        days_of_week = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        for day, day_num in days_of_week.items():
            if day in text_lower:
                today = datetime.now()
                days_ahead = day_num - today.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                target_date = today + timedelta(days_ahead)
                return target_date.replace(hour=23, minute=59, second=0, microsecond=0)
        
        # Check for explicit dates
        for pattern in self.compiled_date_patterns:
            match = pattern.search(text)
            if match:
                date_str = match.group(1)
                try:
                    # Try different date formats
                    for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d-%m-%Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except:
                    continue
        
        return None

    def extract_priority(self, text: str) -> Optional[PriorityLevel]:
        """
        Extract priority level from the given text.
        """
        text_lower = text.lower()
        
        for priority, patterns in self.compiled_priority_patterns.items():
            for pattern in patterns:
                if pattern.search(text_lower):
                    return priority
        
        return None

    def extract_entities(self, text: str) -> Dict[str, any]:
        """
        Extract all entities from the given text.
        """
        entities = {}
        
        # Extract date
        date = self.extract_date(text)
        if date:
            entities['due_date'] = date
        
        # Extract priority
        priority = self.extract_priority(text)
        if priority:
            entities['priority'] = priority.value
        
        # Extract categories (simple approach - look for words after "category:" or "tag:")
        category_match = re.search(r'(category|tag)[:\s]+([^\.\n,]+)', text, re.IGNORECASE)
        if category_match:
            entities['category'] = category_match.group(2).strip()
        
        # Extract task title (basic approach - everything that's not an entity)
        # Remove known entity patterns to isolate the task title
        cleaned_text = text
        for pattern in self.compiled_date_patterns:
            cleaned_text = pattern.sub('', cleaned_text)
        
        for patterns in self.compiled_priority_patterns.values():
            for pattern in patterns:
                cleaned_text = pattern.sub('', cleaned_text)
        
        # Remove category patterns
        cleaned_text = re.sub(r'(category|tag)[:\s]+[^\.\n,]+', '', cleaned_text, flags=re.IGNORECASE)
        
        # Clean up extra spaces and punctuation
        title = re.sub(r'\s+', ' ', cleaned_text.strip())
        if title:
            entities['title'] = title
        
        return entities

# Global instance
entity_extractor = EntityExtractor()

def extract_entities(text: str) -> Dict[str, any]:
    """
    Extract entities from the given text.
    """
    return entity_extractor.extract_entities(text)