import re
import spacy

nlp = spacy.load("en_core_web_sm")

def segment_query(query):
    segments = []

    # Define regex patterns and keywords for each option
    session_patterns = {
       1: r'\b(SP|SPRING|sp|spring|FALL|FA|fa|fall)[ _-]?(201[4-6]|14|15|16)\b',        # Spring sessions for 2014-2016
       2: r'\b(FA|FALL|fa|fall|sp|spring|SP|SPRING)[ _-]?(201[7-9]|17|18|19|2020)\b',      # Fall sessions for 2017-2020
       3: r'\b(SP|SPRING|FA|FALL|sp|spring|fa|fall)[ _-]?(202[1-3]|21|22|23)\b'  # Sessions for 2021-2023
    }

    demographic_keywords = {
        4: [
            "Gender", "Domicile", "DegreeTitle", "MatricMarks", "MatricMaxMarks", "MetricBoardName",
            "InterDegreeTitle", "InterMarks", "InterMaxMarks", "InterSubjects", "InterBoard",
            "NtsMarks", "Session", "Year", "hum100", "csc101", "mth100", "mth101", "phy121",
            "hum110", "hum114", "csc102", "eee241", "csc110", "mth104", "csc211", "csc103",
            "csc241", "hum102", "mth105", "hum103", "bio231", "hum111", "eee121", "cse291",
            "mth231", "mgt101", "csc322", "mth262", "cse304", "csc339", "cse305", "cse303",
            "csc371", "csc291", "csc336", "csc301", "csc462", "csc141", "bio130", "bio111",
            "bio132", "mth242", "phy120", "csc356", "cse302", "cse494", "cse333", "csc461",
            "cse350", "csc303", "cse356", "csc475", "cse455", "cse498", "csc412", "csc441",
            "eee440", "csc350", "csc321", "csc454", "csc483", "csc498", "csc312", "csc354",
            "csc496", "mgt403", "bio310", "cse354", "cse499", "hum430", "hum220", "cse483",
            "env230", "hum434", "csc402", "csc499", "mgt131", "csc455", "phy100", "phy229",
            "csc471", "csc112", "csc221", "mgt350", "eee231", "csc494", "csc444", "hum320",
            "csc478", "cse299", "csc479", "csc448", "csc271", "mth467", "cse355", "csc456",
            "csc253", "mth375", "bsc208", "csc201", "csc330", "csc445", "csc447", "csc314",
            "csc392", "csc443", "csc332", "csc536", "csc304", "csc581", "csc348", "csc571",
            "hum431", "csc328", "hum432", "csc334", "csc353", "cse330", "csd201", "csd205",
            "csd204", "eee119", "csd203", "csd200", "csd102", "csd100", "csd101", "csd202",
            "gpa_sem_1", "gpa_sem_2", "gpa_sem_3", "gpa_sem_4", "gpa_sem_5", "gpa_sem_6",
            "gpa_sem_7", "gpa_sem_8", "gpa_sem_9", "gpa_sem_10", "gpa_sem_11", "gpa_sem_12",
            "Program", "CGPA", "GPA"
        ]
    }

    additional_keywords = {
        5: [
            "information dissemination", "announcement", "notice", "update", "news",
            "broadcast", "memo", "communication", "share information", "inform",
            "release", "publicize", "alert", "notification", "convey", "send","disseminate"
        ],
        6: [
             "define", "explain", "meaning of", "describe", "purpose of",
            "general information", "information about", "how does", "details on",
            "clarify", "overview of", "summary of", "insight into", "introduction to"
        ]
    }

    # Split the query into sentences
    doc = nlp(query)
    sentences = [sent.text.strip() for sent in doc.sents]

    # Process each sentence for pattern matching
    for sentence in sentences:
        matched = False

        # Attempt to split sentence by "and" if it has multiple query parts
        sub_phrases = sentence.split(" . ")

        for phrase in sub_phrases:
            phrase_matched = False

            # Check session-based options (1, 2, 3)
            for option, pattern in session_patterns.items():
                if re.search(pattern, phrase, re.IGNORECASE):
                    segments.append({"option": option, "query": phrase.strip()})
                    phrase_matched = True
                    matched = True
                    break

            # Check for demographics (option 4)
            if not phrase_matched:
                for option, keywords in demographic_keywords.items():
                    if any(keyword.lower() in phrase.lower() for keyword in keywords):
                        segments.append({"option": option, "query": phrase.strip()})
                        phrase_matched = True
                        matched = True
                        break

            # Check for information dissemination keywords (option 5)
            if not phrase_matched:
                for option, keywords in additional_keywords.items():
                    if option == 5 and any(keyword.lower() in phrase.lower() for keyword in keywords):
                        segments.append({"option": option, "query": phrase.strip()})
                        phrase_matched = True
                        matched = True
                        break

            # Check for general question/definition keywords (option 6)
            if not phrase_matched:
                for option, keywords in additional_keywords.items():
                    if option == 6 and any(keyword.lower() in phrase.lower() for keyword in keywords):
                        segments.append({"option": option, "query": phrase.strip()})
                        phrase_matched = True
                        matched = True
                        break

        # If no match, classify the entire sentence as option 6
        if not matched:
            segments.append({"option": 6, "query": sentence.strip()})

    return segments

# Test with example query
