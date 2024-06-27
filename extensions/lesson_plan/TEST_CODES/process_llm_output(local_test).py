import subprocess
import os

def main():
  answer = """

  {
    "lessonPlan": {
      "learningOutcomes": [
        "LO1: Students can create data storage correctly according to requirements.",
        "LO2: Students can manipulate data records (e.g., store, update, and delete) correctly according to requirements."
      ],
      "professionalAttributes": [
        "PA1: Students will demonstrate understanding of API connection and usage.",
        "PA2: Students will apply appropriate error handling techniques when working with data access."
      ],
      "events": [
        {
          "event 1": "Gain Attention; inform learning outcomes; activate prior knowledge",
          "content": [
            {
              "activity": "Group discussion to share examples of applications that require data processing and identify the types of data records being manipulated (e.g., contacts, user preferences, etc.).",
              "duration": "10 minutes",
              "method": "Brainstorming"
            }
          ]
        },
        {
          "event 2": "Present content and provide learning guidance",
          "content": [
            {
              "activity": "Lecture on the importance of creating secure and efficient data storage. Demonstrate how to create a database helper class in Android and a data source class in iOS using sample code.",
              "duration": "30 minutes",
              "method": "Lecture with Visual Aids"
            },
            {
              "activity": "Group exercise to compare the differences between creating data storage for Android and iOS. Discuss how to choose the appropriate method based on requirements.",
              "duration": "20 minutes",
              "method": "Collaborative Learning"
            }
          ]
        },
        {
          "event 3": "Elicit performance and provide feedback",
          "content": [
            {
              "activity": "Individual or pair exercise to implement data storage creation for a given application. Students should follow the appropriate method based on the chosen platform (Android or iOS). Provide sample code for reference.",
              "duration": "40 minutes",
              "method": "Coding Exercise"
            },
            {
              "activity": "Peer review and feedback session to evaluate each other's data storage implementation. Emphasize the importance of proper error handling and security considerations.",
              "duration": "20 minutes",
              "method": "Pair Programming"
            }
          ]
        },
        {
          "event 4": "Assess performance",
          "content": [
            {
              "activity": "Individual quiz to test understanding of data storage creation and manipulation. Sample questions include: 'Explain the difference between a database helper class in Android and a data source class in iOS.', 'List at least three methods for securely storing user preferences.'",
              "duration": "15 minutes",
              "method": "Written Quiz"
            },
            {
              "activity": "Group presentation to demonstrate the implementation of data manipulation (e.g., storing, updating, and deleting user information) in the chosen platform. Students should explain their code and discuss any challenges they encountered.",
              "duration": "25 minutes",
              "method": "Oral Presentation"
            }
          ]
        },
        {
          "event 5": "Enhance retention and transfer of learning",
          "content": [
            {
              "activity": "Discussion on best practices for handling data access errors, such as compilation errors, run-time errors, and user input validation. Provide real-life examples to illustrate the importance of appropriate error handling.",
              "duration": "10 minutes",
              "method": "Classroom Discussion"
            },
            {
              "activity": "Individual reflection on how they can apply the learned concepts in their future projects. Students should write down at least one action item to improve their data processing skills.",
              "duration": "10 minutes",
              "method": "Self-Reflection"
            }
          ]
        }
      ]
    }
  }
  """
  os.chdir("C:/Users/Brandon/Desktop/Projects/ELITE_lessonPlans")  # Change to the directory containing run_llm_to_xml.py
  subprocess.run(["python", "./run_llm_to_xml.py", answer])

if __name__ == "__main__":
    main()
