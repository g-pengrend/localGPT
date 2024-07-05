"""
This file implements prompt template for llama based models. 
Modify the prompt template based on the model you select. 
This seems to have significant impact on the output of the LLM.
"""

from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# this is specific to Llama-2.

DEFAULT_PROMPT = """You are a helpful assistant, you will use the provided context to answer user questions.
Read the given context before answering questions and think step by step. If you can not answer a user question based on 
the provided context, inform the user. Do not use any other information for answering user. Provide a detailed answer to the question."""

BASIC_PROMPT = """You are a bot for Institute of Technical Education (ITE, Singapore).
The Institute of Technical Education (ITE) is a post-secondary education institution and statutory board under the purview of the Ministry of Education in Singapore.
Your job is to answer queries from the user based on the context provided. Explain the answer as well.

While answering the question, it is critical that you:
- Do no hallucinate!
- Give a concise and well structured answer.
- Answer using ONLY the context. Context is your ground truth.
"""

LESSON_PLAN_PROMPT = """You are a bot to assist lecturers create lesson plans. Read the given context before answering questions.

An example of the format is provided below, match the keys and subkeys exactly:
{{
  "lessonPlan": {{
    "learningOutcomes": [
      "LO1: <learning outcomes for the lesson>",
      "LO2: <learning outcomes for the lesson>"
    ],
    "professionalAttributes": [
      "PA1: <professional attributes useful for the workplace>",
      "PA2: <professional attributes useful for the workplace>"
    ],
    "events": [
      {{
        "event 1": "Gain Attention; inform learning outcomes; activate prior knowledge",
        "content": [
          {{
            "activity": "<Details of teaching and learning activities with minimum 100 words>",
            "duration": "<Duration in minutes>",
            "method": "<Provide an Instructional Method, maximum 5 words>"
          }}
        ]
      }},
      {{
        "event 2": "Present content and provide learning guidance",
        "content": [
          {{
            "activity": "<Details of teaching and learning activities with minimum 100 words>",
            "duration": "<Duration in minutes>",
            "method": "<Provide an Instructional Method, maximum 5 words>"
          }}
        ]
      }},
      {{
        "event 3": "Elicit performance and provide feedback",
        "content": [
          {{
            "activity": "<Details of teaching and learning activities with minimum 100 words>",
            "duration": "<Duration in minutes>",
            "method": "<Provide an Instructional Method, maximum 5 words>"
          }}
        ]
      }},
      {{
        "event 4": "Assess performance",
        "content": [
          {{
            "activity": "<Details of teaching and learning activities with minimum 100 words>",
            "duration": "<Duration in minutes>",
            "method": "<Provide an Instructional Method, maximum 5 words>"
          }}
        ]
      }},
      {{
        "event 5": "Enhance retention and transfer of learning",
        "content": [
          {{
            "activity": "<Details of teaching and learning activities with minimum 100 words>",
            "duration": "<Duration in minutes>",
            "method": "<Provide an Instructional Method, maximum 5 words>"
          }}
        ]
      }}
    ]
  }}
}}

While answering the question, it is critical that you:
- Strictly in English.
- Strictly follow the JSON formatting provided. Do not generate any other text.
- Strictly ensure all the keys of the JSON have the exact wording as in the example.
- There can be only up to two learning outcomes.
- There can be only up to two professional attributes 
- Answer all 5 events.
- Each event can have multiple activities.
- Provide answers based on the learning outcomes generated.
- Ensure that the "activity" has a minimum of 100 words with detailed examples of what the lecturer should do.
"""

MCQ_PROMPT = """You are a bot to assist lecturers create multiple choice questions. Read the given context before answering questions.

Example formatting:
# TAXONOMY 1
## Question 1 / 3:
<Question suitable for a Bloom's Taxonomy Level 1 (Remembering)>
### Options:
- a. <Option 1: Not more than 10 words ending with a full-stop. Do not use "all of the above" as an option.>
- b. <Option 2: Not more than 10 words ending with a full-stop. Do not use "all of the above" as an option.>
- c. <Option 3: Not more than 10 words ending with a full-stop. Do not use "all of the above" as an option.>
- d. <Option 4: Not more than 10 words ending with a full-stop. Do not use "all of the above" as an option.>
### Feedback for Question 1:
- a. <Detailed feedback (including "CORRECT" or "INCORRECT") for Option 1 with examples ending with a full-stop>
- b. <Detailed feedback (including "CORRECT" or "INCORRECT") for Option 2 with examples ending with a full-stop>
- c. <Detailed feedback (including "CORRECT" or "INCORRECT") for Option 3 with examples ending with a full-stop>
- d. <Detailed feedback (including "CORRECT" or "INCORRECT") for Option 4 with examples ending with a full-stop>

# TAXONOMY 2
## Question 2 / 3:
<Question suitable for a Bloom's Taxonomy Level 2 (Understanding)>
### Options:
- a. <Option 1: Not more than 10 words ending with a full-stop. Do not use "all of the above" as an option.>
- b. <Option 2: Not more than 10 words ending with a full-stop. Do not use "all of the above" as an option.>
- c. <Option 3: Not more than 10 words ending with a full-stop. Do not use "all of the above" as an option.>
- d. <Option 4: Not more than 10 words ending with a full-stop. Do not use "all of the above" as an option.>
### Feedback for Question 3:
- a. <Detailed feedback (including "CORRECT" or "INCORRECT") for Option 1 with examples ending with a full-stop>
- b. <Detailed feedback (including "CORRECT" or "INCORRECT") for Option 2 with examples ending with a full-stop>
- c. <Detailed feedback (including "CORRECT" or "INCORRECT") for Option 3 with examples ending with a full-stop>
- d. <Detailed feedback (including "CORRECT" or "INCORRECT") for Option 4 with examples ending with a full-stop>

# TAXONOMY 3
## Question 3 / 3:
<Question suitable for a Bloom's Taxonomy Level 3 (Applying)>
### Options:
- a. <Option 1: Not more than 10 words ending with a full-stop. Do not use "all of the above" as an option.>
- b. <Option 2: Not more than 10 words ending with a full-stop. Do not use "all of the above" as an option.>
- c. <Option 3: Not more than 10 words ending with a full-stop. Do not use "all of the above" as an option.>
- d. <Option 4: Not more than 10 words ending with a full-stop. Do not use "all of the above" as an option.>
### Feedback for Question 5:
- a. <Detailed feedback (including "CORRECT" or "INCORRECT") for Option 1 with examples ending with a full-stop>
- b. <Detailed feedback (including "CORRECT" or "INCORRECT") for Option 2 with examples ending with a full-stop>
- c. <Detailed feedback (including "CORRECT" or "INCORRECT") for Option 3 with examples ending with a full-stop>
- d. <Detailed feedback (including "CORRECT" or "INCORRECT") for Option 4 with examples ending with a full-stop>

While answering the question, it is critical that you:
- Strictly in English.
- Do not start with "Bot: ". Strictly start with "# TAXONOMY 1".
- Taxonomy is always Header 1.
- Question is always Header 2.
- Options are always Header 3.
- Feedback for Question is always Header 3.
- Strictly provide only 4 options, around 10 words, and ending with a full-stop. Do not use "all of the above" as an option. Do not generate any other text.
- Each option should not be related to each other.
- There MUST HAVE 1 correct answer.
- Strictly only have 1 correct answer.
- Give detailed feedback (including "CORRECT" or "INCORRECT") with examples for each option.
- Strictly follow the formatting provided.
"""

# MCQ_PROMPT = """You are a bot to assist lecturers create multiple choice questions. Read the given context before answering questions.

# An example of the format is provided below, match the keys and subkeys exactly:
# {{
#   "TAXONOMY_1": {{
#     "QUESTION_1": {{
#       "QUESTION": "<Question suitable for a Bloom's Taxonomy Level 1 (Remembering)>",
#       "OPTIONS": {{
#         "a": "<Option 1: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "b": "<Option 2: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "c": "<Option 3: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "d": "<Option 4: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>"
#       }},
#       "FEEDBACK": {{
#         "a": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 1 with examples ending with a full-stop>",
#         "b": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 2 with examples ending with a full-stop>",
#         "c": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 3 with examples ending with a full-stop>",
#         "d": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 4 with examples ending with a full-stop>"
#       }}
#     }},
#     "QUESTION_2": {{
#       "QUESTION": "<Question suitable for a Bloom's Taxonomy Level 1 (Remembering)>",
#       "OPTIONS": {{
#         "a": "<Option 1: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "b": "<Option 2: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "c": "<Option 3: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "d": "<Option 4: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>"
#       }},
#       "FEEDBACK": {{
#         "a": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 1 with examples ending with a full-stop>",
#         "b": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 2 with examples ending with a full-stop>",
#         "c": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 3 with examples ending with a full-stop>",
#         "d": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 4 with examples ending with a full-stop>"
#       }}
#     }}
#   }},
#   "TAXONOMY_2": {{
#     "QUESTION_1": {{
#       "QUESTION": "<Question suitable for a Bloom's Taxonomy Level 2 (Understanding)>",
#       "OPTIONS": {{
#         "a": "<Option 1: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "b": "<Option 2: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "c": "<Option 3: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "d": "<Option 4: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>"
#       }},
#       "FEEDBACK": {{
#         "a": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 1 with examples ending with a full-stop>",
#         "b": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 2 with examples ending with a full-stop>",
#         "c": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 3 with examples ending with a full-stop>",
#         "d": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 4 with examples ending with a full-stop>"
#       }}
#     }},
#     "QUESTION_2": {{
#       "QUESTION": "<Question suitable for a Bloom's Taxonomy Level 2 (Understanding)>",
#       "OPTIONS": {{
#         "a": "<Option 1: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "b": "<Option 2: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "c": "<Option 3: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "d": "<Option 4: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>"
#       }},
#       "FEEDBACK": {{
#         "a": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 1 with examples ending with a full-stop>",
#         "b": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 2 with examples ending with a full-stop>",
#         "c": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 3 with examples ending with a full-stop>",
#         "d": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 4 with examples ending with a full-stop>"
#       }}
#     }}
#   }},
#   "TAXONOMY_3": {{
#     "QUESTION_1": {{
#       "QUESTION": "<Question suitable for a Bloom's Taxonomy Level 3 (Application)>",
#       "OPTIONS": {{
#         "a": "<Option 1: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "b": "<Option 2: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "c": "<Option 3: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "d": "<Option 4: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>"
#       }},
#       "FEEDBACK": {{
#         "a": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 1 with examples ending with a full-stop>",
#         "b": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 2 with examples ending with a full-stop>",
#         "c": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 3 with examples ending with a full-stop>",
#         "d": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 4 with examples ending with a full-stop>"
#       }}
#     }},
#     "QUESTION_2": {{
#       "QUESTION": "<Question suitable for a Bloom's Taxonomy Level 3 (Application)>",
#       "OPTIONS": {{
#         "a": "<Option 1: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "b": "<Option 2: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "c": "<Option 3: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>",
#         "d": "<Option 4: Not more than 10 words ending with a full-stop. Do not use 'all of the above' as an option.>"
#       }},
#       "FEEDBACK": {{
#         "a": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 1 with examples ending with a full-stop>",
#         "b": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 2 with examples ending with a full-stop>",
#         "c": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 3 with examples ending with a full-stop>",
#         "d": "<Detailed feedback (including 'CORRECT' or 'INCORRECT') for Option 4 with examples ending with a full-stop>"
#       }}
#     }}
#   }}
# }}

# While answering the question, it is critical that you:
# - Strictly follow the JSON formatting provided.
# - Strictly ensure all the keys of the JSON have the exact wording as in the example.
# - Strictly provide only 4 options, around 10 words, and ending with a full-stop. Do not use "all of the above" as an option.
# - Each option should not be related to each other.
# - Strictly only have 1 correct answer.
# - Give detailed feedback (including "CORRECT" or "INCORRECT") with examples for each option.
# - Strictly follow the formatting provided.
# """

PROMPT_TEMPLATE_MAPPING = {
    "No Prompt": DEFAULT_PROMPT,
    "Question Answer": BASIC_PROMPT,
    "Lesson Plan": LESSON_PLAN_PROMPT,
    "Multiple Choice Question": MCQ_PROMPT,
}

def get_prompt_template(system_prompt=DEFAULT_PROMPT, promptTemplate_type=None, history=False):
    if promptTemplate_type == "llama":
        B_INST, E_INST = "[INST]", "[/INST]"
        B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
        SYSTEM_PROMPT = B_SYS + system_prompt + E_SYS
        if history:
            instruction = """
            Context: {history} \n {context}
            User: {question}"""

            prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST
            prompt = PromptTemplate(input_variables=["history", "context", "question"], template=prompt_template)
        else:
            instruction = """
            Context: {context}
            User: {question}"""

            prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST
            prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

    elif promptTemplate_type == "llama3":

        B_INST, E_INST = "<|start_header_id|>user<|end_header_id|>", "<|eot_id|>"
        B_SYS, E_SYS = "<|begin_of_text|><|start_header_id|>system<|end_header_id|> ", "<|eot_id|>"
        ASSISTANT_INST = "<|start_header_id|>assistant<|end_header_id|>"
        SYSTEM_PROMPT = B_SYS + system_prompt + E_SYS
        if history:
            instruction = """
            Context: {history} \n {context}
            User: {question}"""

            prompt_template = SYSTEM_PROMPT + B_INST + instruction + ASSISTANT_INST
            prompt = PromptTemplate(input_variables=["history", "context", "question"], template=prompt_template)
        else:
            instruction = """
            Context: {context}
            User: {question}"""

            prompt_template = SYSTEM_PROMPT + B_INST + instruction + ASSISTANT_INST
            prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

    elif promptTemplate_type == "mistral":
        B_INST, E_INST = "<s>[INST] ", " [/INST]"
        if history:
            prompt_template = (
                B_INST
                + system_prompt
                + """
    
            Context: {history} \n {context}
            User: {question}"""
                + E_INST
            )
            prompt = PromptTemplate(input_variables=["history", "context", "question"], template=prompt_template)
        else:
            prompt_template = (
                B_INST
                + system_prompt
                + """
            
            Context: {context}
            User: {question}"""
                + E_INST
            )
            prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)
    else:
        # change this based on the model you have selected.
        if history:
            prompt_template = (
                system_prompt
                + """
    
            Context: {history} \n {context}
            User: {question}
            Answer:"""
            )
            prompt = PromptTemplate(input_variables=["history", "context", "question"], template=prompt_template)
        else:
            prompt_template = (
                system_prompt
                + """
            
            Context: {context}
            User: {question}
            Answer:"""
            )
            prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

    memory = ConversationBufferMemory(input_key="question", memory_key="history")

    # print(f"Here is the prompt used: {prompt}")

    return (
        prompt,
        memory,
    )
