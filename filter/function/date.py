from datetime import datetime

def convertDate(start, end):
    # Convert strings to datetime objects
    start_date = datetime.strptime(start, '%Y-%m-%d').date()
    end_date = datetime.strptime(end, '%Y-%m-%d').date()
    
    return start_date, end_date