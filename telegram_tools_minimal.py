def get_telegram_tools() -> list:
    """
    Получить список Telegram MCP tools (минимальная версия)
    
    Returns:
        List of tool definitions
    """
    return [
        # === ОСНОВНЫЕ ИНСТРУМЕНТЫ ===
        {
            "name": "telegram_send_message",
            "description": "Отправить текстовое сообщение в чат",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата или username"
                    },
                    "text": {
                        "type": "string",
                        "description": "Текст сообщения"
                    },
                    "parse_mode": {
                        "type": "string",
                        "description": "Режим парсинга (HTML, Markdown)",
                        "default": "HTML"
                    }
                },
                "required": ["chat_id", "text"]
            }
        },
        {
            "name": "telegram_send_photo",
            "description": "Отправить фото в чат",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата или username"
                    },
                    "photo": {
                        "type": "string",
                        "description": "URL фото или file_id"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Подпись к фото"
                    }
                },
                "required": ["chat_id", "photo"]
            }
        },
        {
            "name": "telegram_send_document",
            "description": "Отправить документ в чат",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата или username"
                    },
                    "document": {
                        "type": "string",
                        "description": "URL документа или file_id"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Подпись к документу"
                    }
                },
                "required": ["chat_id", "document"]
            }
        },
        
        # === ИНФОРМАЦИЯ О БОТЕ ===
        {
            "name": "telegram_get_bot_info",
            "description": "Получить информацию о боте",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "telegram_get_updates",
            "description": "Получить обновления бота",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "offset": {
                        "type": "integer",
                        "description": "Смещение для получения обновлений"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Максимальное количество обновлений"
                    }
                }
            }
        },
        
        # === WEBHOOK ===
        {
            "name": "telegram_set_webhook",
            "description": "Установить webhook для бота",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL для webhook"
                    }
                },
                "required": ["url"]
            }
        },
        {
            "name": "telegram_delete_webhook",
            "description": "Удалить webhook бота",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "telegram_get_webhook_info",
            "description": "Получить информацию о webhook",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        
        # === КОМАНДЫ БОТА ===
        {
            "name": "telegram_set_commands",
            "description": "Установить команды бота",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "commands": {
                        "type": "array",
                        "description": "Список команд",
                        "items": {
                            "type": "object",
                            "properties": {
                                "command": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["commands"]
            }
        },
        {
            "name": "telegram_get_commands",
            "description": "Получить список команд бота",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        
        # === УПРАВЛЕНИЕ СООБЩЕНИЯМИ ===
        {
            "name": "telegram_delete_message",
            "description": "Удалить сообщение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "message_id": {
                        "type": "integer",
                        "description": "ID сообщения"
                    }
                },
                "required": ["chat_id", "message_id"]
            }
        },
        {
            "name": "telegram_edit_message",
            "description": "Редактировать сообщение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "message_id": {
                        "type": "integer",
                        "description": "ID сообщения"
                    },
                    "text": {
                        "type": "string",
                        "description": "Новый текст"
                    }
                },
                "required": ["chat_id", "message_id", "text"]
            }
        },
        {
            "name": "telegram_pin_message",
            "description": "Закрепить сообщение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "message_id": {
                        "type": "integer",
                        "description": "ID сообщения"
                    }
                },
                "required": ["chat_id", "message_id"]
            }
        },
        {
            "name": "telegram_unpin_message",
            "description": "Открепить сообщение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    }
                },
                "required": ["chat_id"]
            }
        },
        
        # === CALLBACK QUERIES ===
        {
            "name": "telegram_answer_callback_query",
            "description": "Ответить на callback query",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "callback_query_id": {
                        "type": "string",
                        "description": "ID callback query"
                    },
                    "text": {
                        "type": "string",
                        "description": "Текст ответа"
                    }
                },
                "required": ["callback_query_id"]
            }
        },
        
        # === ОПРОСЫ ===
        {
            "name": "telegram_send_poll",
            "description": "Отправить опрос",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "question": {
                        "type": "string",
                        "description": "Вопрос"
                    },
                    "options": {
                        "type": "array",
                        "description": "Варианты ответов",
                        "items": {"type": "string"}
                    }
                },
                "required": ["chat_id", "question", "options"]
            }
        },
        {
            "name": "telegram_stop_poll",
            "description": "Остановить опрос",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "message_id": {
                        "type": "integer",
                        "description": "ID сообщения с опросом"
                    }
                },
                "required": ["chat_id", "message_id"]
            }
        },
        
        # === ДОПОЛНИТЕЛЬНЫЕ МЕДИА ===
        {
            "name": "telegram_send_dice",
            "description": "Отправить игральную кость",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    }
                },
                "required": ["chat_id"]
            }
        },
        {
            "name": "telegram_send_animation",
            "description": "Отправить анимацию (GIF)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "animation": {
                        "type": "string",
                        "description": "URL анимации или file_id"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Подпись к анимации"
                    }
                },
                "required": ["chat_id", "animation"]
            }
        },
        {
            "name": "telegram_send_video",
            "description": "Отправить видео",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "video": {
                        "type": "string",
                        "description": "URL видео или file_id"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Подпись к видео"
                    }
                },
                "required": ["chat_id", "video"]
            }
        },
        {
            "name": "telegram_send_audio",
            "description": "Отправить аудио",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "audio": {
                        "type": "string",
                        "description": "URL аудио или file_id"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Подпись к аудио"
                    }
                },
                "required": ["chat_id", "audio"]
            }
        },
        {
            "name": "telegram_send_voice",
            "description": "Отправить голосовое сообщение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "voice": {
                        "type": "string",
                        "description": "URL голосового сообщения или file_id"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Подпись к голосовому сообщению"
                    }
                },
                "required": ["chat_id", "voice"]
            }
        },
        {
            "name": "telegram_send_video_note",
            "description": "Отправить видео-заметку",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "video_note": {
                        "type": "string",
                        "description": "URL видео-заметки или file_id"
                    }
                },
                "required": ["chat_id", "video_note"]
            }
        },
        {
            "name": "telegram_send_media_group",
            "description": "Отправить группу медиафайлов",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "media": {
                        "type": "array",
                        "description": "Массив медиафайлов",
                        "items": {"type": "object"}
                    }
                },
                "required": ["chat_id", "media"]
            }
        },
        
        # === INLINE РЕЖИМ ===
        {
            "name": "telegram_answer_inline_query",
            "description": "Ответить на inline query",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "inline_query_id": {
                        "type": "string",
                        "description": "ID inline query"
                    },
                    "results": {
                        "type": "array",
                        "description": "Массив результатов",
                        "items": {"type": "object"}
                    }
                },
                "required": ["inline_query_id", "results"]
            }
        },
        
        # === ДЕЙСТВИЯ ЧАТА ===
        {
            "name": "telegram_send_chat_action",
            "description": "Отправить действие чата (печатает...)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "action": {
                        "type": "string",
                        "description": "Действие (typing, upload_photo, upload_video, etc.)"
                    }
                },
                "required": ["chat_id", "action"]
            }
        },
        
        # === ФАЙЛЫ ===
        {
            "name": "telegram_get_file",
            "description": "Получить файл",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "ID файла"
                    }
                },
                "required": ["file_id"]
            }
        },
        {
            "name": "telegram_get_user_profile_photos",
            "description": "Получить фото профиля пользователя",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID пользователя"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Смещение"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Лимит"
                    }
                },
                "required": ["user_id"]
            }
        },
        
        # === ИГРЫ ===
        {
            "name": "telegram_send_game",
            "description": "Отправить игру",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "game_short_name": {
                        "type": "string",
                        "description": "Короткое имя игры"
                    }
                },
                "required": ["chat_id", "game_short_name"]
            }
        },
        
        # === ПЛАТЕЖИ ===
        {
            "name": "telegram_send_invoice",
            "description": "Отправить счёт для оплаты",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "title": {
                        "type": "string",
                        "description": "Название товара"
                    },
                    "description": {
                        "type": "string",
                        "description": "Описание товара"
                    },
                    "payload": {
                        "type": "string",
                        "description": "Полезная нагрузка"
                    },
                    "provider_token": {
                        "type": "string",
                        "description": "Токен провайдера платежей"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Валюта (USD, EUR, RUB)"
                    },
                    "prices": {
                        "type": "array",
                        "description": "Массив цен",
                        "items": {"type": "object"}
                    }
                },
                "required": ["chat_id", "title", "description", "payload", "provider_token", "currency", "prices"]
            }
        },
    ]

