# core/llm_client/PromptType.py

from enum import Enum


class PromptType(str, Enum):
    FIND_FILE_IN_FOLDER = "find_file_in_folder"
    FIND_TEXT_IN_FILES = "find_text_in_files"
    GENERIC = "generic"




PROMPTS = {
    PromptType.FIND_FILE_IN_FOLDER: (
        "Ты — эксперт по преобразованию команд на естественном языке в JSON-инструкции. "
        "Если получишь команду вида: 'найди на моем компьютере в каталоге d:/tmp файл с именем nano.txt', "
        "верни чистый JSON без пояснений:\n"
        "{\"actions\": [{\"type\": \"find_file_in_folder\", \"directory\": \"D:/tmp\", \"filename\": \"nano.txt\"}]}"
    ),
    PromptType.FIND_TEXT_IN_FILES: (
        "Ты — помощник, который преобразует команды пользователя в чёткие JSON-инструкции. "
        "Если пользователь просит найти строку в текстовых файлах в указанной директории, "
        "то ты должен вернуть строго JSON следующей структуры:\n\n"
        "{\n"
        "  \"actions\": [\n"
        "    {\n"
        "      \"type\": \"find_text_in_files\",\n"
        "      \"directory\": \"<путь к каталогу>\",\n"
        "      \"find_text\": \"<искомый текст>\"\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Твоя задача — распознать путь к каталогу и текст, который нужно найти. "
        "Не добавляй никаких пояснений, комментариев, markdown-разметки или символов оформления. "
        "Верни только чистый JSON строго в описанном формате.\n\n"
        "Примеры команд пользователя:\n"
        "- Найди строку 'hello nano' в каталоге d:/tmp/micro\n"
        "- В каких файлах в d:/data есть строка 'token expired'\n"
        "- Поиск слов 'ошибка подключения' в директории D:/logs\n"
        "- Какие файлы в C:/Users/user/docs содержат текст 'conflict detected'\n"
        "- Найди файлы, в которых есть строка 'hello nano' , в каталоге d:/tmp/micro\n"
    )

    ,
    PromptType.GENERIC: (
        "Ты — агент преобразования естественного языка в JSON. "
        "Возвращай JSON, описывающий действия, которые нужно выполнить."
    )
}
