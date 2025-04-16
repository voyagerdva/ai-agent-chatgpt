# core/llm_client/prompts.py

from enum import Enum

class PromptType(str, Enum):
    FIND_FILE_IN_FOLDER = "find_file_in_folder"
    FIND_TEXT = "find_text"
    GENERIC = "generic"

PROMPTS = {
    PromptType.FIND_FILE_IN_FOLDER: (
        "Ты — эксперт по преобразованию команд на естественном языке в JSON-инструкции. "
        "Если получишь команду вида: 'найди на моем компьютере в каталоге d:/tmp файл с именем nano.txt', "
        "верни чистый JSON без пояснений:\n"
        "{\"actions\": [{\"type\": \"find_file_in_folder\", \"directory\": \"D:/tmp\", \"filename\": \"nano.txt\"}]}"
    ),
    PromptType.FIND_TEXT: (
        "Ты — эксперт по анализу естественного языка. Если получишь команду вида: "
        "'найди строку \"hello\" в файлах каталога D:/tmp', верни JSON:\n"
        "{\"actions\": [{\"type\": \"find_text\", \"directory\": \"D:/tmp\", \"text\": \"hello\"}]}"
    ),
    PromptType.GENERIC: (
        "Ты — агент преобразования естественного языка в JSON. "
        "Возвращай JSON, описывающий действия, которые нужно выполнить."
    )
}
