# mock_data/fake_llm_responses.py

find_file_in_folder_responses = [

    r'''\boxed{```json
    {
      "actions": [
        {
          "type": "find_file_in_folder",
          "directory": "D:/tmp/micro",
          "filename": "nano2.txt"
        }
      ]
    }
    ```}''',

    r'''\boxed{
      "actions": [
        {
          "type": "find_file_in_folder",
          "directory": "D:/tmp/micro",
          "filename": "nano2.txt"
        }
      ]
    }''',

    r'''\boxed{"actions":[{"type":"find_file_in_folder","directory":"D:/tmp/micro","filename":"nano2.txt"}]}'''
]

find_text_in_files_responses = [
    r'''\boxed{```json
    {
      "actions": [
        {
          "type": "find_text_in_files",
          "directory": "d:/tmp/micro",
          "find_text": "hello nano"
        }
      ]
    }
    ```}''',

    r'''\boxed{
      "actions": [
        {
          "type": "find_text_in_files",
          "directory": "d:/tmp/micro",
          "find_text": "hello nano"
        }
      ]
    }''',

    r'''\boxed{"actions":[{"type":"find_text_in_files","directory":"d:/tmp/micro","find_text":"hello nano"}]}'''
]
